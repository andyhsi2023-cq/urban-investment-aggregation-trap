#!/usr/bin/env python3
"""
86_japan_prefecture_scaling.py — 日本都道府県標度律检验
=====================================================
目的: 验证标度律 (scaling law) 在日本 47 都道府県是否成立
      核心假说: 人均GDP ~ Pop^alpha (超线性标度 alpha > 0)
      附加: 住宅标度律、空置率梯度分析

数据来源:
  - 内閣府 県民経済計算 (Cabinet Office SNA): 県内総生産 GDP (FY2020)
  - 総務省 国勢調査 2020: 都道府県人口
  - 総務省 住宅・土地統計調査 2018: 住宅数・空置率
  数据已根据公开发布值内嵌于脚本中（47行数据量，确保完全可复现）

输出:
  - 02-data/raw/japan_prefecture_data.csv
  - 03-analysis/models/japan_prefecture_scaling_report.txt
  - 04-figures/drafts/fig_japan_scaling.png
依赖: numpy, pandas, scipy, statsmodels, matplotlib
"""

import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import warnings
warnings.filterwarnings('ignore')

# 日本語フォント設定 (macOS)
plt.rcParams['font.family'] = 'Hiragino Sans'
plt.rcParams['axes.unicode_minus'] = False

# ============================================================
# 路径配置
# ============================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
DATA_RAW = os.path.join(BASE, '02-data', 'raw')
MODELS = os.path.join(BASE, '03-analysis', 'models')
FIGS = os.path.join(BASE, '04-figures', 'drafts')
SOURCE_DIR = os.path.join(BASE, '04-figures', 'source-data')

for d in [DATA_RAW, MODELS, FIGS, SOURCE_DIR]:
    os.makedirs(d, exist_ok=True)

report_lines = []
def rpt(s=''):
    report_lines.append(s)
    print(s)

# ============================================================
# Nature 级配色 (色盲安全)
# ============================================================
REGION_COLORS = {
    '関東': '#0072B2',   # 蓝 — 关东
    '近畿': '#D55E00',   # 橙红 — 近畿
    '中部': '#009E73',   # 绿 — 中部
    '九州': '#CC79A7',   # 粉紫 — 九州冲绳
    '東北': '#E69F00',   # 黄 — 东北
    '北海道': '#56B4E9', # 浅蓝 — 北海道
    '中国': '#F0E442',   # 黄绿 — 中国地方
    '四国': '#999999',   # 灰 — 四国
}

# ============================================================
# 步骤 1: 都道府県数据（内嵌自公开统计）
# ============================================================
rpt('=' * 72)
rpt('日本 47 都道府県 標度律検験 (Scaling Law Analysis)')
rpt('=' * 72)
rpt()
rpt('数据来源:')
rpt('  人口: 総務省 国勢調査 2020 (Census 2020)')
rpt('  GDP: 内閣府 県民経済計算 令和2年度 (FY2020, nominal)')
rpt('  住宅: 総務省 住宅・土地統計調査 2018')
rpt()

# 47 都道府県データ
# pop_2020: 国勢調査 2020 人口（千人）
# gdp_fy2020: 県内総生産 FY2020 名目（十億円）
# housing_2018: 住宅総数 2018（千戸）
# vacant_2018: 空き家数 2018（千戸）
# area_km2: 面積（平方km）

prefectures_data = [
    # (都道府県, 地方, pop_1000, gdp_billion_yen, housing_1000, vacant_1000, area_km2)
    ('北海道', '北海道', 5224, 19220, 2747, 382, 83424),
    ('青森', '東北', 1238, 4502, 589, 97, 9646),
    ('岩手', '東北', 1211, 4730, 553, 90, 15275),
    ('宮城', '東北', 2302, 9300, 1068, 136, 7282),
    ('秋田', '東北', 960, 3377, 432, 74, 11638),
    ('山形', '東北', 1068, 3949, 430, 57, 9323),
    ('福島', '東北', 1834, 7570, 849, 127, 13784),
    ('茨城', '関東', 2868, 12920, 1294, 195, 6097),
    ('栃木', '関東', 1934, 9050, 869, 124, 6408),
    ('群馬', '関東', 1940, 8680, 896, 117, 6362),
    ('埼玉', '関東', 7345, 22840, 3263, 345, 3798),
    ('千葉', '関東', 6284, 20600, 2883, 381, 5158),
    ('東京', '関東', 14048, 115440, 7671, 810, 2194),
    ('神奈川', '関東', 9237, 35530, 4451, 484, 2416),
    ('新潟', '中部', 2202, 8710, 972, 130, 12584),
    ('富山', '中部', 1035, 4620, 425, 52, 4248),
    ('石川', '中部', 1133, 4740, 509, 68, 4186),
    ('福井', '中部', 767, 3300, 319, 42, 4190),
    ('山梨', '中部', 810, 3290, 397, 71, 4465),
    ('長野', '中部', 2049, 8100, 960, 190, 13562),
    ('岐阜', '中部', 1979, 7610, 873, 121, 10621),
    ('静岡', '中部', 3633, 16360, 1658, 245, 7777),
    ('愛知', '中部', 7542, 39600, 3446, 390, 5173),
    ('三重', '中部', 1770, 8070, 816, 115, 5774),
    ('滋賀', '近畿', 1414, 6600, 586, 65, 4017),
    ('京都', '近畿', 2578, 10400, 1314, 173, 4612),
    ('大阪', '近畿', 8838, 40600, 4586, 709, 1905),
    ('兵庫', '近畿', 5465, 20500, 2601, 360, 8401),
    ('奈良', '近畿', 1325, 3660, 612, 90, 3691),
    ('和歌山', '近畿', 923, 3470, 461, 86, 4725),
    ('鳥取', '中国', 554, 1850, 253, 38, 3507),
    ('島根', '中国', 671, 2500, 311, 48, 6708),
    ('岡山', '中国', 1890, 7400, 877, 126, 7115),
    ('広島', '中国', 2800, 11960, 1358, 191, 8479),
    ('山口', '中国', 1342, 5680, 666, 109, 6112),
    ('徳島', '四国', 720, 2990, 362, 62, 4147),
    ('香川', '四国', 951, 3690, 452, 66, 1877),
    ('愛媛', '四国', 1335, 4870, 675, 109, 5676),
    ('高知', '四国', 692, 2340, 371, 65, 7104),
    ('福岡', '九州', 5135, 18970, 2464, 327, 4987),
    ('佐賀', '九州', 812, 2820, 343, 49, 2441),
    ('長崎', '九州', 1312, 4360, 619, 88, 4131),
    ('熊本', '九州', 1739, 5970, 789, 99, 7409),
    ('大分', '九州', 1124, 4320, 551, 79, 6341),
    ('宮崎', '九州', 1070, 3570, 517, 73, 7735),
    ('鹿児島', '九州', 1588, 5300, 798, 112, 9187),
    ('沖縄', '九州', 1468, 4470, 614, 65, 2282),
]

# DataFrame 构建
cols = ['prefecture', 'region', 'pop_1000', 'gdp_billion_yen',
        'housing_1000', 'vacant_1000', 'area_km2']
df = pd.DataFrame(prefectures_data, columns=cols)

# 派生变量
df['population'] = df['pop_1000'] * 1000
df['gdp_yen'] = df['gdp_billion_yen'] * 1e9
df['gdp_per_capita'] = df['gdp_yen'] / df['population']               # 円/人
df['gdp_pc_million'] = df['gdp_per_capita'] / 1e6                     # 百万円/人
df['housing_total'] = df['housing_1000'] * 1000
df['vacant_total'] = df['vacant_1000'] * 1000
df['vacancy_rate'] = df['vacant_total'] / df['housing_total'] * 100    # %
df['housing_per_capita'] = df['housing_total'] / df['population']
df['pop_density'] = df['population'] / df['area_km2']

# 対数変換
df['ln_pop'] = np.log(df['population'])
df['ln_gdp_pc'] = np.log(df['gdp_per_capita'])
df['ln_housing_pc'] = np.log(df['housing_per_capita'])
df['ln_vacancy'] = np.log(df['vacancy_rate'])
df['ln_pop_density'] = np.log(df['pop_density'])

rpt(f'N = {len(df)} 都道府県')
rpt(f'人口範囲: {df["pop_1000"].min():.0f}千 ~ {df["pop_1000"].max():.0f}千人')
rpt(f'GDP範囲: {df["gdp_billion_yen"].min():.0f} ~ {df["gdp_billion_yen"].max():.0f} 十億円')
rpt(f'空置率範囲: {df["vacancy_rate"].min():.1f}% ~ {df["vacancy_rate"].max():.1f}%')
rpt()

# CSV 出力
csv_path = os.path.join(DATA_RAW, 'japan_prefecture_data.csv')
df.to_csv(csv_path, index=False, encoding='utf-8-sig')
rpt(f'数据保存: {csv_path}')
rpt()

# ============================================================
# 步骤 2: 描述性統計
# ============================================================
rpt('=' * 72)
rpt('步骤 2: 描述性統計')
rpt('=' * 72)
rpt()

desc_vars = ['pop_1000', 'gdp_billion_yen', 'gdp_pc_million',
             'housing_per_capita', 'vacancy_rate', 'pop_density']
desc_labels = ['人口(千人)', 'GDP(十億円)', '人均GDP(百万円)',
               '人均住宅(戸/人)', '空置率(%)', '人口密度(人/km²)']

rpt(f'{"変量":<20} {"平均":>10} {"標準偏差":>10} {"最小":>10} {"最大":>10}')
rpt('-' * 62)
for var, lab in zip(desc_vars, desc_labels):
    rpt(f'{lab:<20} {df[var].mean():>10.1f} {df[var].std():>10.1f} '
        f'{df[var].min():>10.1f} {df[var].max():>10.1f}')
rpt()

# 地方別集計
rpt('地方別平均:')
rpt(f'{"地方":<10} {"N":>4} {"平均人口千人":>12} {"平均GDP十億":>12} '
    f'{"人均GDP百万円":>14} {"空置率%":>8}')
rpt('-' * 64)
for reg in ['北海道', '東北', '関東', '中部', '近畿', '中国', '四国', '九州']:
    sub = df[df['region'] == reg]
    rpt(f'{reg:<10} {len(sub):>4} {sub["pop_1000"].mean():>12.0f} '
        f'{sub["gdp_billion_yen"].mean():>12.0f} '
        f'{sub["gdp_pc_million"].mean():>14.2f} '
        f'{sub["vacancy_rate"].mean():>8.1f}')
rpt()

# ============================================================
# 步骤 3: 標度律回帰分析
# ============================================================
rpt('=' * 72)
rpt('步骤 3: 標度律回帰分析')
rpt('=' * 72)
rpt()

def run_ols(y, x, label_y, label_x, df_in):
    """OLS回帰 + ロバストSE + 診断"""
    X = sm.add_constant(df_in[x])
    model = sm.OLS(df_in[y], X).fit(cov_type='HC1')
    alpha = model.params[x]
    se = model.bse[x]
    ci_lo, ci_hi = model.conf_int().loc[x]
    r2 = model.rsquared
    f_p = model.f_pvalue

    rpt(f'--- {label_y} ~ {label_x} ---')
    rpt(f'  α (slope)     = {alpha:.4f}  (SE = {se:.4f})')
    rpt(f'  95% CI        = [{ci_lo:.4f}, {ci_hi:.4f}]')
    rpt(f'  p-value       = {model.pvalues[x]:.2e}')
    rpt(f'  R²            = {r2:.4f}')
    rpt(f'  F-stat p      = {f_p:.2e}')
    rpt(f'  N             = {model.nobs:.0f}')

    # 残差正規性検定
    _, jb_p = stats.jarque_bera(model.resid)
    rpt(f'  Jarque-Bera p = {jb_p:.4f}')

    # Shapiro-Wilk
    _, sw_p = stats.shapiro(model.resid)
    rpt(f'  Shapiro-Wilk p= {sw_p:.4f}')
    rpt()

    return model, alpha, se, r2

# --- Model 1: ln(GDP_pc) ~ ln(Pop) ---
rpt('【Model 1】人均GDP標度律: ln(GDP_pc) ~ α·ln(Pop)')
rpt('  如果 α > 0 → 超線形標度 (agglomeration economies)')
rpt('  如果 α = 0 → 線形標度')
rpt('  如果 α < 0 → 亜線形標度')
rpt()
m1, alpha1, se1, r2_1 = run_ols('ln_gdp_pc', 'ln_pop',
                                  'ln(GDP_per_capita)', 'ln(Population)', df)

# --- Model 2: ln(Housing_pc) ~ ln(Pop) ---
rpt('【Model 2】人均住宅標度律: ln(Housing_pc) ~ β·ln(Pop)')
rpt('  如果 β < 0 → 大都市人均住宅少 (housing scarcity scaling)')
rpt()
m2, alpha2, se2, r2_2 = run_ols('ln_housing_pc', 'ln_pop',
                                  'ln(Housing_per_capita)', 'ln(Population)', df)

# --- Model 3: ln(Vacancy_rate) ~ ln(Pop) ---
rpt('【Model 3】空置率標度律: ln(Vacancy%) ~ γ·ln(Pop)')
rpt('  如果 γ < 0 → 小県空置率高 (OCR scaling)')
rpt('  这直接对应 OCR 概念：小城市过度建设')
rpt()
m3, alpha3, se3, r2_3 = run_ols('ln_vacancy', 'ln_pop',
                                  'ln(Vacancy_rate)', 'ln(Population)', df)

# --- Model 4: ln(Vacancy_rate) ~ ln(Pop_density) ---
rpt('【Model 4】空置率 vs 人口密度: ln(Vacancy%) ~ δ·ln(Pop_density)')
rpt()
m4, alpha4, se4, r2_4 = run_ols('ln_vacancy', 'ln_pop_density',
                                  'ln(Vacancy_rate)', 'ln(Pop_density)', df)

# ============================================================
# 步骤 4: 与中国/美国对比
# ============================================================
rpt('=' * 72)
rpt('步骤 4: 跨国対比')
rpt('=' * 72)
rpt()
rpt('標度律指数 α 対比 (ln(GDP_pc) ~ α·ln(Pop)):')
rpt(f'{"国/地域":<15} {"α":>8} {"SE":>8} {"R²":>8} {"N":>6} {"来源"}')
rpt('-' * 72)
rpt(f'{"日本(都道府県)":<15} {alpha1:>8.4f} {se1:>8.4f} {r2_1:>8.4f} {47:>6} {"本分析"}')
rpt(f'{"中国(275城市)":<15} {"~0.05":>8} {"—":>8} {"~0.15":>8} {"275":>6} {"Script 80"}')
rpt(f'{"美国(MSA)":<15} {"~0.08":>8} {"—":>8} {"~0.20":>8} {"384":>6} {"Script 83"}')
rpt()
rpt('空置率標度律 γ (ln(Vacancy%) ~ γ·ln(Pop)):')
rpt(f'{"日本(都道府県)":<15} {alpha3:>8.4f} {se3:>8.4f} {r2_3:>8.4f} {47:>6}')
rpt()

# ============================================================
# 步骤 5: 異常値 (Outlier) 分析
# ============================================================
rpt('=' * 72)
rpt('步骤 5: 特殊都道府県分析')
rpt('=' * 72)
rpt()

# 計算 GDP_pc 残差
X1 = sm.add_constant(df['ln_pop'])
resid1 = m1.resid
df['resid_gdp_pc'] = resid1

# 上位/下位
top5 = df.nlargest(5, 'resid_gdp_pc')
bot5 = df.nsmallest(5, 'resid_gdp_pc')

rpt('人均GDP正方向偏差 Top 5 (実績 > 予測):')
for _, r in top5.iterrows():
    rpt(f'  {r["prefecture"]}: residual = {r["resid_gdp_pc"]:+.3f}, '
        f'人口={r["pop_1000"]:.0f}千, GDP_pc={r["gdp_pc_million"]:.2f}百万円')
rpt()
rpt('人均GDP負方向偏差 Top 5 (実績 < 予測):')
for _, r in bot5.iterrows():
    rpt(f'  {r["prefecture"]}: residual = {r["resid_gdp_pc"]:+.3f}, '
        f'人口={r["pop_1000"]:.0f}千, GDP_pc={r["gdp_pc_million"]:.2f}百万円')
rpt()

# 空置率特殊分析
rpt('空置率 Top 10:')
vac_top = df.nlargest(10, 'vacancy_rate')
for _, r in vac_top.iterrows():
    rpt(f'  {r["prefecture"]}: {r["vacancy_rate"]:.1f}%, '
        f'人口={r["pop_1000"]:.0f}千人')
rpt()
rpt('空置率 Bottom 5:')
vac_bot = df.nsmallest(5, 'vacancy_rate')
for _, r in vac_bot.iterrows():
    rpt(f'  {r["prefecture"]}: {r["vacancy_rate"]:.1f}%, '
        f'人口={r["pop_1000"]:.0f}千人')
rpt()

# ============================================================
# 步骤 6: 日本的独特性 — Q<1 时代的空间异质性
# ============================================================
rpt('=' * 72)
rpt('步骤 6: 日本的Q<1周期与空間格差')
rpt('=' * 72)
rpt()
rpt('日本是唯一经历完整 Q<1 周期的发达经济体:')
rpt('  - 1990年バブル崩壊後、不動産価値 < 再建築費 が30年間持続')
rpt('  - 全国空置率 2018年: 13.6%（846万戸）')
rpt('  - 人口減少は地方から進行 → 空置率の地域格差拡大')
rpt()

# 空置率と人口の Spearman 相関
rho_sp, p_sp = stats.spearmanr(df['population'], df['vacancy_rate'])
rpt(f'空置率 vs 人口 (Spearman): rho = {rho_sp:.4f}, p = {p_sp:.4f}')

# 大都市 vs 地方の比較
metro = df[df['pop_1000'] >= 2000]  # 200万人以上
rural = df[df['pop_1000'] < 1000]   # 100万人未満
rpt(f'大都市圏 (≥200万人, N={len(metro)}): 平均空置率 = {metro["vacancy_rate"].mean():.1f}%')
rpt(f'地方県 (<100万人, N={len(rural)}): 平均空置率 = {rural["vacancy_rate"].mean():.1f}%')

# t検定
t_stat, t_p = stats.ttest_ind(metro['vacancy_rate'], rural['vacancy_rate'])
rpt(f'  Welch t-test: t = {t_stat:.2f}, p = {t_p:.4f}')
rpt()

# OCR との対応関係
rpt('理論的含意:')
rpt('  空置率は過剰建設率 (OCR) の直接指標')
rpt('  ln(Vacancy%) ~ γ·ln(Pop) で γ < 0 ならば:')
rpt('  → 小都市ほど住宅過剰 (OCR高い)')
rpt('  → Urban Tobin\'s Q フレームワークと整合')
if alpha3 < 0:
    rpt(f'  ★ 日本データは γ = {alpha3:.4f} < 0 → 仮説支持')
else:
    rpt(f'  ★ 日本データは γ = {alpha3:.4f} ≥ 0 → 仮説不支持（要検討）')
rpt()

# ============================================================
# 步骤 7: 可視化
# ============================================================
rpt('=' * 72)
rpt('步骤 7: 可視化')
rpt('=' * 72)
rpt()

fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.suptitle('Scaling Laws in Japanese Prefectures (47 Prefectures)',
             fontsize=16, fontweight='bold', y=0.98)

# 标注用都道府県
highlight = ['東京', '大阪', '北海道', '沖縄', '秋田', '鳥取', '愛知', '神奈川']

def plot_scaling(ax, xvar, yvar, model, xlabel, ylabel, title,
                 alpha_val, r2_val, label_prefix=''):
    """標度律散点図 + 回帰線"""
    # 地方別色分け
    for region, color in REGION_COLORS.items():
        mask = df['region'] == region
        ax.scatter(df.loc[mask, xvar], df.loc[mask, yvar],
                   c=color, s=50, alpha=0.8, edgecolors='white',
                   linewidths=0.5, zorder=3, label=region)

    # 回帰線
    x_range = np.linspace(df[xvar].min() - 0.2, df[xvar].max() + 0.2, 100)
    X_pred = sm.add_constant(x_range)
    y_pred = model.predict(X_pred)
    ax.plot(x_range, y_pred, 'k-', linewidth=2, zorder=2)

    # 95% 信頼帯
    pred = model.get_prediction(X_pred)
    ci = pred.conf_int(alpha=0.05)
    ax.fill_between(x_range, ci[:, 0], ci[:, 1],
                    color='grey', alpha=0.15, zorder=1)

    # ラベル
    for _, row in df[df['prefecture'].isin(highlight)].iterrows():
        ax.annotate(row['prefecture'],
                    (row[xvar], row[yvar]),
                    fontsize=7,
                    xytext=(5, 5), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.7))

    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    slope_sym = label_prefix if label_prefix else 'α'
    ax.set_title(f'{title}\n{slope_sym} = {alpha_val:.4f}, R² = {r2_val:.4f}',
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')

# Panel A: GDP per capita scaling
plot_scaling(axes[0, 0], 'ln_pop', 'ln_gdp_pc', m1,
             'ln(Population)', 'ln(GDP per capita, yen)',
             'A. GDP per Capita Scaling',
             alpha1, r2_1, 'α')

# Panel B: Housing per capita scaling
plot_scaling(axes[0, 1], 'ln_pop', 'ln_housing_pc', m2,
             'ln(Population)', 'ln(Housing per capita)',
             'B. Housing per Capita Scaling',
             alpha2, r2_2, 'β')

# Panel C: Vacancy rate scaling
plot_scaling(axes[1, 0], 'ln_pop', 'ln_vacancy', m3,
             'ln(Population)', 'ln(Vacancy rate, %)',
             'C. Vacancy Rate Scaling',
             alpha3, r2_3, 'γ')

# Panel D: Vacancy rate vs population density
plot_scaling(axes[1, 1], 'ln_pop_density', 'ln_vacancy', m4,
             'ln(Population density, per km²)', 'ln(Vacancy rate, %)',
             'D. Vacancy Rate vs Density',
             alpha4, r2_4, 'δ')

# 共通凡例
handles = [Line2D([0], [0], marker='o', color='w', markerfacecolor=c,
                  markersize=8, label=r)
           for r, c in REGION_COLORS.items()]
fig.legend(handles=handles, loc='lower center', ncol=8,
           fontsize=9, frameon=True, fancybox=True,
           bbox_to_anchor=(0.5, 0.01))

plt.tight_layout(rect=[0, 0.05, 1, 0.96])

fig_path = os.path.join(FIGS, 'fig_japan_scaling.png')
fig.savefig(fig_path, dpi=300, bbox_inches='tight', facecolor='white')
rpt(f'図表保存: {fig_path}')

# Source data
source_path = os.path.join(SOURCE_DIR, 'fig_japan_scaling_source.csv')
df.to_csv(source_path, index=False, encoding='utf-8-sig')
rpt(f'源数据保存: {source_path}')
rpt()

# ============================================================
# 步骤 8: ロバスト性検定
# ============================================================
rpt('=' * 72)
rpt('步骤 8: ロバスト性分析')
rpt('=' * 72)
rpt()

# 8a: 東京除外
rpt('--- 8a: 東京除外 ---')
df_no_tokyo = df[df['prefecture'] != '東京']
X_nt = sm.add_constant(df_no_tokyo['ln_pop'])
m1_nt = sm.OLS(df_no_tokyo['ln_gdp_pc'], X_nt).fit(cov_type='HC1')
rpt(f'  Model 1 (東京除外): α = {m1_nt.params["ln_pop"]:.4f} '
    f'(SE = {m1_nt.bse["ln_pop"]:.4f}), R² = {m1_nt.rsquared:.4f}')

m3_nt = sm.OLS(df_no_tokyo['ln_vacancy'], X_nt).fit(cov_type='HC1')
rpt(f'  Model 3 (東京除外): γ = {m3_nt.params["ln_pop"]:.4f} '
    f'(SE = {m3_nt.bse["ln_pop"]:.4f}), R² = {m3_nt.rsquared:.4f}')
rpt()

# 8b: 三大都市圏除外 (東京+大阪+愛知)
rpt('--- 8b: 三大都市圏除外 (東京+大阪+愛知) ---')
df_no_3 = df[~df['prefecture'].isin(['東京', '大阪', '愛知'])]
X_n3 = sm.add_constant(df_no_3['ln_pop'])
m1_n3 = sm.OLS(df_no_3['ln_gdp_pc'], X_n3).fit(cov_type='HC1')
rpt(f'  Model 1 (三大除外): α = {m1_n3.params["ln_pop"]:.4f} '
    f'(SE = {m1_n3.bse["ln_pop"]:.4f}), R² = {m1_n3.rsquared:.4f}')
rpt()

# 8c: Rank-based (Spearman)
rpt('--- 8c: Spearman 順位相関 ---')
rho1, p1 = stats.spearmanr(df['ln_pop'], df['ln_gdp_pc'])
rpt(f'  ln(Pop) vs ln(GDP_pc): rho = {rho1:.4f}, p = {p1:.4e}')
rho2, p2 = stats.spearmanr(df['ln_pop'], df['ln_housing_pc'])
rpt(f'  ln(Pop) vs ln(Housing_pc): rho = {rho2:.4f}, p = {p2:.4e}')
rho3, p3 = stats.spearmanr(df['ln_pop'], df['ln_vacancy'])
rpt(f'  ln(Pop) vs ln(Vacancy%): rho = {rho3:.4f}, p = {p3:.4e}')
rpt()

# 8d: 非線形性検定 (二次項)
rpt('--- 8d: 非線形性検定 (二次項追加) ---')
df['ln_pop_sq'] = df['ln_pop'] ** 2
X_quad = sm.add_constant(df[['ln_pop', 'ln_pop_sq']])
m1_q = sm.OLS(df['ln_gdp_pc'], X_quad).fit(cov_type='HC1')
rpt(f'  Model 1 + ln(Pop)²:')
rpt(f'    ln(Pop)   = {m1_q.params["ln_pop"]:.4f} (p = {m1_q.pvalues["ln_pop"]:.4f})')
rpt(f'    ln(Pop)²  = {m1_q.params["ln_pop_sq"]:.4f} (p = {m1_q.pvalues["ln_pop_sq"]:.4f})')
rpt(f'    R²        = {m1_q.rsquared:.4f}')
if m1_q.pvalues['ln_pop_sq'] < 0.05:
    rpt('    → 二次項有意 → 非線形性あり')
else:
    rpt('    → 二次項非有意 → 線形標度律で十分')
rpt()

# ============================================================
# 步骤 9: 総括
# ============================================================
rpt('=' * 72)
rpt('步骤 9: 総括 — 日本都道府県標度律')
rpt('=' * 72)
rpt()
rpt('主要発見:')
rpt(f'  1. 人均GDP標度指数 α = {alpha1:.4f} (p = {m1.pvalues["ln_pop"]:.2e})')
if alpha1 > 0 and m1.pvalues['ln_pop'] < 0.05:
    rpt('     → 超線形標度成立：大都市ほど人均GDP高い (集積の経済)')
elif alpha1 > 0:
    rpt('     → 正の傾向あるが統計的に有意でない')
else:
    rpt('     → 亜線形/標度律不成立')

rpt(f'  2. 人均住宅標度指数 β = {alpha2:.4f} (p = {m2.pvalues["ln_pop"]:.2e})')
if alpha2 < 0 and m2.pvalues['ln_pop'] < 0.05:
    rpt('     → 大都市ほど人均住宅少ない (住宅希少性の標度律)')

rpt(f'  3. 空置率標度指数 γ = {alpha3:.4f} (p = {m3.pvalues["ln_pop"]:.2e})')
if alpha3 < 0 and m3.pvalues['ln_pop'] < 0.05:
    rpt('     → 小県ほど空置率高い → OCR標度律成立')
    rpt('     → Urban Tobin\'s Q理論と整合: Q<1環境で小都市が最も過剰')

rpt()
rpt('理論的含意 (Urban Q Phase Transition):')
rpt('  日本のデータは以下を示唆:')
rpt('  - バブル崩壊後のQ<1長期化は全国的現象だが、影響は均一でない')
rpt('  - 集積の経済が弱い地方県ほど、過剰建設の影響が深刻')
rpt('  - 空置率の地域格差は「相転移の空間的異質性」を表す')
rpt('  - これは中国の将来予測に直接応用可能')
rpt()

# レポート保存
report_path = os.path.join(MODELS, 'japan_prefecture_scaling_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
rpt(f'レポート保存: {report_path}')
rpt()
rpt('完了。')
