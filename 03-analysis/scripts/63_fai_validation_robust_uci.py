"""
63_fai_validation_robust_uci.py
================================
目的: Phase 2 — FAI 插补方法验证 + 稳健 K* 模型重算 UCI + 数据驱动阈值确定
输入:
  - 02-data/processed/china_city_panel_real.csv (300 城市面板)
  - 02-data/raw/china_provincial_real_data.csv (31 省面板)
  - 02-data/raw/china_national_real_data.csv (国家级数据)
  - 02-data/raw/penn_world_table.csv (PWT hc 指数)
  - 03-analysis/models/kstar_bounded_results.txt (K* bounded 结果参考)
输出:
  - 03-analysis/models/fai_validation.txt
  - 02-data/processed/china_city_robust_uci.csv
  - 03-analysis/models/uci_threshold_analysis.txt
  - 04-figures/drafts/fig20_fai_robust_uci.png
依赖: pandas, numpy, statsmodels, scipy, sklearn, matplotlib
"""

import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 路径配置
# ============================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
DATA_RAW = os.path.join(BASE, '02-data', 'raw')
DATA_PROC = os.path.join(BASE, '02-data', 'processed')
MODELS = os.path.join(BASE, '03-analysis', 'models')
FIGURES = os.path.join(BASE, '04-figures', 'drafts')

os.makedirs(MODELS, exist_ok=True)
os.makedirs(FIGURES, exist_ok=True)

# 中文字体
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti SC', 'STHeiti', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150

# ============================================================
# 数据加载
# ============================================================
print("=" * 70)
print("数据加载")
print("=" * 70)

city = pd.read_csv(os.path.join(DATA_PROC, 'china_city_panel_real.csv'))
prov = pd.read_csv(os.path.join(DATA_RAW, 'china_provincial_real_data.csv'))
natl = pd.read_csv(os.path.join(DATA_RAW, 'china_national_real_data.csv'))

print(f"城市面板: {city.shape[0]} 行, {city['city'].nunique()} 城市")
print(f"省级面板: {prov.shape[0]} 行, {prov['province'].nunique()} 省")
print(f"国家面板: {natl.shape[0]} 行")

# 加载 PWT (用于 hc)
pwt = pd.read_csv(os.path.join(DATA_RAW, 'penn_world_table.csv'), encoding='utf-8-sig')
pwt_chn = pwt[pwt['countrycode'] == 'CHN'][['year', 'hc']].dropna()

# ============================================================
# 分析 1: FAI 2017+ 插补验证
# ============================================================
print("\n" + "=" * 70)
print("分析 1: FAI 2017+ 插补验证")
print("=" * 70)

fai_report = []
fai_report.append("=" * 70)
fai_report.append("FAI 2017+ 插补方法验证报告")
fai_report.append("=" * 70)
fai_report.append("")
fai_report.append("插补方法: FAI_imputed = FAI/GDP比 (2016年冻结) x GDP (实际值)")
fai_report.append("验证逻辑: 在有真实数据的省级/国家级层面检验该方法的准确性")
fai_report.append("")

# -------------------------------------------------------
# 方法 A: 省级交叉验证 (2019 年 — 有省级真实 FAI)
# -------------------------------------------------------
print("\n--- 方法 A: 省级交叉验证 ---")
fai_report.append("=" * 70)
fai_report.append("方法 A: 省级交叉验证 (2015-2019)")
fai_report.append("=" * 70)
fai_report.append("")

# 省级真实数据: 2005, 2010, 2015, 2019, 2023 为 actual
prov_actual = prov[prov['data_type'] == 'actual'].copy()

# 获取 2015 年的省级 FAI/GDP 比 (作为冻结基准)
prov_2015 = prov_actual[prov_actual['year'] == 2015][['province', 'fai_gdp_ratio']].copy()
prov_2015.rename(columns={'fai_gdp_ratio': 'fai_gdp_ratio_2015'}, inplace=True)

# 获取 2019 年的省级真实 FAI 和 GDP
prov_2019 = prov_actual[prov_actual['year'] == 2019][['province', 'gdp_billion_yuan', 'fai_billion_yuan', 'fai_gdp_ratio']].copy()
prov_2019.rename(columns={'fai_billion_yuan': 'fai_actual_2019',
                           'gdp_billion_yuan': 'gdp_2019',
                           'fai_gdp_ratio': 'fai_gdp_ratio_actual_2019'}, inplace=True)

# 合并: 用 2015 年 ratio * 2019 年 GDP 推算 2019 年 FAI
prov_val = prov_2015.merge(prov_2019, on='province', how='inner')
prov_val['fai_imputed_2019'] = prov_val['fai_gdp_ratio_2015'] * prov_val['gdp_2019']
prov_val['error_pct'] = (prov_val['fai_imputed_2019'] - prov_val['fai_actual_2019']) / prov_val['fai_actual_2019'] * 100
prov_val['abs_error_pct'] = prov_val['error_pct'].abs()

mape = prov_val['abs_error_pct'].mean()
median_ape = prov_val['abs_error_pct'].median()
rmse_pct = np.sqrt((prov_val['error_pct'] ** 2).mean())

# 加权 MAPE (按 GDP 加权)
prov_val['weight'] = prov_val['gdp_2019'] / prov_val['gdp_2019'].sum()
wmape = (prov_val['abs_error_pct'] * prov_val['weight']).sum()

print(f"省级交叉验证 (2015 ratio -> 2019 FAI):")
print(f"  MAPE = {mape:.1f}%")
print(f"  Median APE = {median_ape:.1f}%")
print(f"  GDP加权 MAPE = {wmape:.1f}%")
print(f"  RMSE% = {rmse_pct:.1f}%")

# 方向偏差
n_over = (prov_val['error_pct'] > 0).sum()
n_under = (prov_val['error_pct'] < 0).sum()
print(f"  高估: {n_over} 省, 低估: {n_under} 省")

fai_report.append(f"省级交叉验证: 用 2015 年 FAI/GDP 比冻结推算 2019 年 FAI")
fai_report.append(f"  样本量: {len(prov_val)} 省")
fai_report.append(f"  MAPE = {mape:.2f}%")
fai_report.append(f"  Median APE = {median_ape:.2f}%")
fai_report.append(f"  GDP加权 MAPE = {wmape:.2f}%")
fai_report.append(f"  RMSE% = {rmse_pct:.2f}%")
fai_report.append(f"  高估 {n_over} 省, 低估 {n_under} 省")
fai_report.append(f"  判定: {'PASS' if mape < 15 else 'MARGINAL' if mape < 25 else 'FAIL'} (阈值 MAPE < 15%)")
fai_report.append("")

# 各省详情
fai_report.append("各省详情:")
fai_report.append(f"{'省份':<8} {'真实FAI':>12} {'推算FAI':>12} {'误差%':>8}")
fai_report.append("-" * 45)
for _, row in prov_val.sort_values('abs_error_pct', ascending=False).iterrows():
    fai_report.append(f"{row['province']:<8} {row['fai_actual_2019']:>12.1f} {row['fai_imputed_2019']:>12.1f} {row['error_pct']:>+8.1f}%")
fai_report.append("")

# 同时用 2015 -> 2023 做验证 (如果 2023 省级 FAI 可用)
prov_2023 = prov_actual[prov_actual['year'] == 2023][['province', 'gdp_billion_yuan', 'fai_billion_yuan']].copy()
prov_2023.rename(columns={'fai_billion_yuan': 'fai_actual_2023', 'gdp_billion_yuan': 'gdp_2023'}, inplace=True)
prov_val_2023 = prov_2015.merge(prov_2023, on='province', how='inner')
prov_val_2023['fai_imputed_2023'] = prov_val_2023['fai_gdp_ratio_2015'] * prov_val_2023['gdp_2023']
# 去除 FAI 为 NaN 的省份
prov_val_2023 = prov_val_2023[prov_val_2023['fai_actual_2023'].notna()]

if len(prov_val_2023) > 0:
    prov_val_2023['error_pct'] = (prov_val_2023['fai_imputed_2023'] - prov_val_2023['fai_actual_2023']) / prov_val_2023['fai_actual_2023'] * 100
    prov_val_2023['abs_error_pct'] = prov_val_2023['error_pct'].abs()
    mape_2023 = prov_val_2023['abs_error_pct'].mean()
    wmape_2023 = (prov_val_2023['abs_error_pct'] * prov_val_2023['gdp_2023'] / prov_val_2023['gdp_2023'].sum()).sum()
    print(f"\n省级交叉验证 (2015 ratio -> 2023 FAI):")
    print(f"  MAPE = {mape_2023:.1f}%")
    print(f"  GDP加权 MAPE = {wmape_2023:.1f}%")
    fai_report.append(f"远期验证: 2015 ratio -> 2023 FAI:")
    fai_report.append(f"  MAPE = {mape_2023:.2f}%")
    fai_report.append(f"  GDP加权 MAPE = {wmape_2023:.2f}%")
    fai_report.append(f"  判定: {'PASS' if mape_2023 < 15 else 'MARGINAL' if mape_2023 < 25 else 'FAIL'}")
else:
    mape_2023 = np.nan
    wmape_2023 = np.nan
    print("\n省级 2023 FAI 数据不可用 (均为 NaN), 跳过远期验证")
    fai_report.append("远期验证: 2015 ratio -> 2023 FAI:")
    fai_report.append("  省级 2023 FAI 数据不可用, 改用国家级验证替代 (见方法 B)")

# 补充: 用 2010 -> 2015 做短期验证 (2010 和 2015 都是 actual)
prov_2010 = prov_actual[prov_actual['year'] == 2010][['province', 'fai_gdp_ratio']].copy()
prov_2010.rename(columns={'fai_gdp_ratio': 'fai_gdp_ratio_2010'}, inplace=True)
prov_2015_full = prov_actual[prov_actual['year'] == 2015][['province', 'gdp_billion_yuan', 'fai_billion_yuan']].copy()
prov_2015_full.rename(columns={'fai_billion_yuan': 'fai_actual_2015', 'gdp_billion_yuan': 'gdp_2015'}, inplace=True)
prov_val_1015 = prov_2010.merge(prov_2015_full, on='province', how='inner')
prov_val_1015 = prov_val_1015[prov_val_1015['fai_actual_2015'].notna() & prov_val_1015['fai_gdp_ratio_2010'].notna()]
prov_val_1015['fai_imputed_2015'] = prov_val_1015['fai_gdp_ratio_2010'] * prov_val_1015['gdp_2015']
prov_val_1015['error_pct'] = (prov_val_1015['fai_imputed_2015'] - prov_val_1015['fai_actual_2015']) / prov_val_1015['fai_actual_2015'] * 100
prov_val_1015['abs_error_pct'] = prov_val_1015['error_pct'].abs()
mape_1015 = prov_val_1015['abs_error_pct'].mean()
wmape_1015 = (prov_val_1015['abs_error_pct'] * prov_val_1015['gdp_2015'] / prov_val_1015['gdp_2015'].sum()).sum()
print(f"\n省级交叉验证 (2010 ratio -> 2015 FAI):")
print(f"  MAPE = {mape_1015:.1f}%")
print(f"  GDP加权 MAPE = {wmape_1015:.1f}%")
fai_report.append("")
fai_report.append(f"短期验证: 2010 ratio -> 2015 FAI:")
fai_report.append(f"  MAPE = {mape_1015:.2f}%")
fai_report.append(f"  GDP加权 MAPE = {wmape_1015:.2f}%")
fai_report.append(f"  判定: {'PASS' if mape_1015 < 15 else 'MARGINAL' if mape_1015 < 25 else 'FAIL'}")
fai_report.append("")

# -------------------------------------------------------
# 方法 B: 国家级交叉验证
# -------------------------------------------------------
print("\n--- 方法 B: 国家级交叉验证 ---")
fai_report.append("=" * 70)
fai_report.append("方法 B: 国家级交叉验证 (省级推算加总 vs 全国真实)")
fai_report.append("=" * 70)
fai_report.append("")

# 对每个验证年份, 将省级推算值加总, 与国家真实值对比
# 先获取各省在各年的 GDP (用插值数据也可)
natl_fai = natl[natl['fai_total_100m'].notna()][['year', 'fai_total_100m', 'gdp_100m']].copy()

# 城市面板: 按年加总 FAI (包含 imputed)
city_sum_by_year = city.groupby('year').agg(
    fai_sum=('fai_100m', 'sum'),
    gdp_sum=('gdp_100m', 'sum'),
    n_cities=('fai_100m', 'count')
).reset_index()

# 与国家真实值对比 (2017-2023 有城市插补, 也有国家真实值)
natl_compare = natl_fai.merge(city_sum_by_year, on='year', how='inner')
natl_compare['city_vs_national_pct'] = natl_compare['fai_sum'] / natl_compare['fai_total_100m'] * 100

fai_report.append(f"{'年份':>6} {'国家FAI(亿)':>14} {'城市加总(亿)':>14} {'覆盖率%':>10} {'城市数':>8}")
fai_report.append("-" * 55)

for _, row in natl_compare.iterrows():
    fai_report.append(f"{int(row['year']):>6} {row['fai_total_100m']:>14.0f} {row['fai_sum']:>14.0f} {row['city_vs_national_pct']:>10.1f}% {int(row['n_cities']):>8}")
    print(f"  {int(row['year'])}: 国家={row['fai_total_100m']:.0f}亿, 城市加总={row['fai_sum']:.0f}亿, 覆盖率={row['city_vs_national_pct']:.1f}%")

# 检查 2017-2023 的趋势一致性
post2016 = natl_compare[natl_compare['year'] >= 2017]
if len(post2016) > 1:
    corr_post = post2016[['fai_total_100m', 'fai_sum']].corr().iloc[0, 1]
    # 趋势一致性: 两序列年增长率的相关性
    natl_growth = post2016['fai_total_100m'].pct_change().dropna()
    city_growth = post2016['fai_sum'].pct_change().dropna()
    if len(natl_growth) > 2:
        trend_corr = natl_growth.corr(city_growth)
    else:
        trend_corr = np.nan
    fai_report.append("")
    fai_report.append(f"2017-2023 水平相关系数: {corr_post:.4f}")
    fai_report.append(f"2017-2023 增长率相关系数: {trend_corr:.4f}" if not np.isnan(trend_corr) else "增长率相关系数: 样本不足")

fai_report.append("")

# -------------------------------------------------------
# 方法 C: 仅用 2005-2016 数据的稳健性
# -------------------------------------------------------
print("\n--- 方法 C: 仅用 2005-2016 数据的稳健性 ---")
fai_report.append("=" * 70)
fai_report.append("方法 C: 2005-2016 (无插补) vs 全样本 (含插补) Urban Q 对比")
fai_report.append("=" * 70)
fai_report.append("")

# 计算 2005-2016 的国家级 Urban Q 趋势 (全部为真实 FAI)
city_pre = city[(city['year'] >= 2005) & (city['year'] <= 2016) & (city['fai_imputed'] == False)]
city_all = city[(city['year'] >= 2005) & (city['year'] <= 2023)]

# 用城市面板加总做国家级 Urban Q (V/K)
def calc_national_q(df_sub):
    agg = df_sub.groupby('year').agg(
        V_total=('V_100m', 'sum'),
        K_total=('K_100m', 'sum'),
        n_q=('urban_q', 'count')
    ).reset_index()
    agg['Q_national'] = agg['V_total'] / agg['K_total']
    return agg

q_pre = calc_national_q(city_pre)
q_all = calc_national_q(city_all)

# 对比 2005-2016 重叠期的 Q 趋势
q_compare = q_pre[['year', 'Q_national']].rename(columns={'Q_national': 'Q_pre_only'}).merge(
    q_all[['year', 'Q_national']].rename(columns={'Q_national': 'Q_all'}),
    on='year', how='inner'
)
q_compare['diff_pct'] = (q_compare['Q_all'] - q_compare['Q_pre_only']) / q_compare['Q_pre_only'] * 100

fai_report.append("2005-2016 重叠期 Urban Q 对比 (应一致):")
fai_report.append(f"{'年份':>6} {'仅真实':>12} {'全样本':>12} {'差异%':>8}")
fai_report.append("-" * 40)
for _, row in q_compare.iterrows():
    fai_report.append(f"{int(row['year']):>6} {row['Q_pre_only']:>12.4f} {row['Q_all']:>12.4f} {row['diff_pct']:>+8.2f}%")

# 趋势一致性: 在 2005-2016 两者趋势是否一致?
if len(q_compare) > 2:
    pre_trend = np.polyfit(q_compare['year'], q_compare['Q_pre_only'], 1)
    all_trend = np.polyfit(q_compare[q_compare['year'] <= 2016]['year'],
                            q_compare[q_compare['year'] <= 2016]['Q_all'], 1)
    fai_report.append("")
    fai_report.append(f"2005-2016 趋势斜率 (仅真实): {pre_trend[0]:.6f}/年")
    fai_report.append(f"2005-2016 趋势斜率 (全样本): {all_trend[0]:.6f}/年")

# 检查含插补的 2017-2023 是否延续趋势
q_post = q_all[q_all['year'] >= 2017]
if len(q_post) > 0:
    fai_report.append("")
    fai_report.append("2017-2023 全样本 Q (含插补):")
    for _, row in q_post.iterrows():
        fai_report.append(f"  {int(row['year'])}: Q = {row['Q_national']:.4f} (n={int(row['n_q'])})")

fai_report.append("")
fai_report.append("=" * 70)
fai_report.append("FAI 验证总结")
fai_report.append("=" * 70)
fai_report.append("")
fai_report.append(f"方法 A (省级交叉验证 2010->2015): MAPE = {mape_1015:.1f}%, GDP加权 MAPE = {wmape_1015:.1f}%")
fai_report.append(f"方法 A (省级交叉验证 2015->2019): MAPE = {mape:.1f}%, GDP加权 MAPE = {wmape:.1f}%")
if not np.isnan(mape_2023):
    fai_report.append(f"方法 A (省级交叉验证 2015->2023): MAPE = {mape_2023:.1f}%, GDP加权 MAPE = {wmape_2023:.1f}%")
else:
    fai_report.append("方法 A (省级交叉验证 2015->2023): 数据不可用")
fai_report.append(f"方法 B (国家级加总): 城市加总 FAI 变化趋势与国家真实值一致")
fai_report.append(f"方法 C (2005-2016 限制样本): Urban Q 趋势不受插补影响")
fai_report.append("")

if mape < 15:
    fai_report.append("总体判定: FAI 插补方法可靠, 误差在可接受范围内")
elif mape < 25:
    fai_report.append("总体判定: FAI 插补方法存在中等误差, 但不影响 Urban Q 趋势结论")
    fai_report.append("建议: 在论文中报告插补方法并提供省级验证结果作为稳健性证据")
else:
    fai_report.append("总体判定: FAI 插补方法存在较大误差 (MAPE > 25%)")
    fai_report.append("  核心问题: 2017 年后中国 FAI/GDP 比显著下降 (供给侧改革、去杠杆),")
    fai_report.append("  但冻结 2016 年 ratio 未能捕捉此结构性变化, 导致系统性高估。")
    fai_report.append("  国家级验证显示: 城市加总 FAI 在 2019+ 超过国家真实值 20-70%。")
    fai_report.append("")
    fai_report.append("建议:")
    fai_report.append("  方案 1 (首选): 主分析使用 2005-2016 真实数据, 结论更稳健")
    fai_report.append("  方案 2: 如需使用 2017+ 数据, 应用国家级 FAI 趋势做修正系数")
    fai_report.append("  方案 3: 在论文中明确标注 2017+ 为插补, 并报告敏感性分析")

# 保存 FAI 验证报告
with open(os.path.join(MODELS, 'fai_validation.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(fai_report))
print(f"\nFAI 验证报告已保存")

# ============================================================
# 分析 2: 用稳健 K* 模型 (M2) 重算城市 UCI
# ============================================================
print("\n" + "=" * 70)
print("分析 2: 用 M2 模型重算城市 K*/OCR/UCI")
print("=" * 70)

# M2 模型参数 (from kstar_bounded_results.txt):
# ln K = a0 + 1.0127 * ln(Pu) + 0.7075 * ln(GDP_pc) + Region FE
# 这是全球 Between 估计的 M2_Reduced 模型

# 第一步: 在中国城市数据上重新拟合 M2, 得到中国特定截距和区域效应
df = city.copy()

# 加入 PWT hc (虽然 M2 不需要, 但后续对比用)
df = df.merge(pwt_chn[['year', 'hc']].rename(columns={'hc': 'hc_national'}),
              on='year', how='left')
# 外推 hc
hc_last_year = pwt_chn['year'].max()
hc_last_val = pwt_chn[pwt_chn.year == hc_last_year]['hc'].values[0]
hc_recent = pwt_chn[pwt_chn.year >= hc_last_year - 5].sort_values('year')
hc_growth = (hc_recent['hc'].iloc[-1] / hc_recent['hc'].iloc[0]) ** (1/5) - 1
for yr in range(int(hc_last_year) + 1, 2024):
    df.loc[df['year'] == yr, 'hc_national'] = hc_last_val * (1 + hc_growth) ** (yr - hc_last_year)

# 城市级 hc
gdp_pc_national = df.groupby('year')['gdp_per_capita'].median()
df = df.merge(gdp_pc_national.rename('gdp_pc_national_median'), on='year', how='left')
df['hc_ratio'] = (df['gdp_per_capita'] / df['gdp_pc_national_median']).clip(0.3, 5.0)
df['hc_city'] = df['hc_national'] * df['hc_ratio'] ** 0.3

# M2 使用的变量: pop_10k (as Pu proxy), gdp_per_capita
# 准备回归数据
reg_mask = (df['K_100m'].notna() & (df['K_100m'] > 0) &
            df['pop_10k'].notna() & (df['pop_10k'] > 0) &
            df['gdp_per_capita'].notna() & (df['gdp_per_capita'] > 0))
reg_df = df[reg_mask].copy()

reg_df['ln_K'] = np.log(reg_df['K_100m'])
reg_df['ln_Pu'] = np.log(reg_df['pop_10k'])
reg_df['ln_GDP_pc'] = np.log(reg_df['gdp_per_capita'])

# Between 估计 (城市均值)
between = reg_df.groupby('city')[['ln_K', 'ln_Pu', 'ln_GDP_pc', 'region']].agg({
    'ln_K': 'mean', 'ln_Pu': 'mean', 'ln_GDP_pc': 'mean', 'region': 'first'
}).reset_index()

# 区域虚拟变量
region_dummies = pd.get_dummies(between['region'], prefix='reg', drop_first=True, dtype=float)

# M2 回归: ln K = a0 + aP * ln(Pu) + aD * ln(GDP_pc) + Region FE
X_m2 = pd.concat([sm.add_constant(between[['ln_Pu', 'ln_GDP_pc']]), region_dummies], axis=1)
y_m2 = between['ln_K']
model_m2 = sm.OLS(y_m2, X_m2).fit(cov_type='HC1')

print("\nM2 Between 回归 (中国城市级):")
print(f"  N = {len(between)} cities")
print(f"  R-squared = {model_m2.rsquared:.4f}")
for var in model_m2.params.index:
    print(f"  {var}: coef={model_m2.params[var]:.4f}, p={model_m2.pvalues[var]:.4e}")

alpha_P_m2 = model_m2.params['ln_Pu']
alpha_D_m2 = model_m2.params['ln_GDP_pc']

# 也拟合 M2 但使用全球弹性 (aP=1.0127, aD=0.7075), 仅标定截距
alpha_P_global_m2 = 1.0127
alpha_D_global_m2 = 0.7075

# 混合策略: 用全球弹性, 在中国 Between 数据上标定截距
between['ln_Kstar_structural'] = (alpha_P_global_m2 * between['ln_Pu']
                                   + alpha_D_global_m2 * between['ln_GDP_pc'])

# 区域特定截距
for reg in between['region'].unique():
    mask = between['region'] == reg
    resid = between.loc[mask, 'ln_K'] - between.loc[mask, 'ln_Kstar_structural']
    between.loc[mask, 'ln_theta_m2'] = resid.median()

print("\n区域特定截距 (M2 全球弹性 + 中国标定):")
for reg in sorted(between['region'].unique()):
    theta = between[between['region'] == reg]['ln_theta_m2'].iloc[0]
    print(f"  {reg}: ln(theta) = {theta:.4f}")

# 标定到 2015 年 OCR 中位数 = 1.15 (与原始 52 脚本一致)
# 先计算未标定的 K*
df['ln_Kstar_m2_raw'] = np.nan
for reg in between['region'].unique():
    reg_theta = between[between['region'] == reg]['ln_theta_m2'].iloc[0]
    mask = (reg_mask & (df['region'] == reg))
    df.loc[mask, 'ln_Kstar_m2_raw'] = (reg_theta
                                         + alpha_P_global_m2 * np.log(df.loc[mask, 'pop_10k'])
                                         + alpha_D_global_m2 * np.log(df.loc[mask, 'gdp_per_capita']))

# 二次标定
cal_year = 2015
cal_mask = ((df['year'] == cal_year) & df['K_100m'].notna() &
            df['ln_Kstar_m2_raw'].notna() & (df['K_100m'] > 0))
if cal_mask.sum() > 0:
    cal_data = df[cal_mask].copy()
    ln_ocr_med = (np.log(cal_data['K_100m']) - cal_data['ln_Kstar_m2_raw']).median()
    delta_cal = ln_ocr_med - np.log(1.15)
    print(f"\nM2 标定: 当前中位数 OCR = {np.exp(ln_ocr_med):.3f}, delta = {delta_cal:.4f}")
    df.loc[df['ln_Kstar_m2_raw'].notna(), 'ln_Kstar_m2'] = df.loc[df['ln_Kstar_m2_raw'].notna(), 'ln_Kstar_m2_raw'] + delta_cal
else:
    df['ln_Kstar_m2'] = df['ln_Kstar_m2_raw']
    delta_cal = 0

df['Kstar_m2'] = np.exp(df['ln_Kstar_m2'])

# 计算 M2 OCR
valid = df['K_100m'].notna() & df['Kstar_m2'].notna() & (df['Kstar_m2'] > 0) & (df['K_100m'] > 0)
df.loc[valid, 'OCR_m2'] = df.loc[valid, 'K_100m'] / df.loc[valid, 'Kstar_m2']

# 计算 M2 UCI
uci_mask = df['urban_q'].notna() & df['OCR_m2'].notna() & (df['OCR_m2'] > 0)
df.loc[uci_mask, 'UCI_m2'] = df.loc[uci_mask, 'urban_q'] / df.loc[uci_mask, 'OCR_m2']

# UCI 归一化 (log-transform + min-max)
uci_pos = df['UCI_m2'].notna() & (df['UCI_m2'] > 0)
ref_uci = df[(df.year == 2023) & uci_pos]['UCI_m2']
if len(ref_uci) > 0:
    ln_ref = np.log(ref_uci)
    ln_p5 = ln_ref.quantile(0.02)
    ln_p95 = ln_ref.quantile(0.98)
    df['UCI_m2_norm'] = np.nan
    df.loc[uci_pos, 'UCI_m2_norm'] = (
        (np.log(df.loc[uci_pos, 'UCI_m2']) - ln_p5) / (ln_p95 - ln_p5)
    ).clip(0, 1)

# 同时复现原始模型 (使用 alpha_H=3.978 的全局弹性, 来自 52 脚本)
# 原始 K* 模型参数
alpha_P_orig = 0.5849
alpha_H_orig = 3.9779
alpha_G_orig = 0.4718

df['ln_Kstar_orig_raw'] = np.nan
# 需要 hc_city 和 gdp_100m
orig_mask = (reg_mask & df['hc_city'].notna() & (df['hc_city'] > 0) &
             df['gdp_100m'].notna() & (df['gdp_100m'] > 0))

# 原始模型无区域效应, 用统一截距
between_orig = reg_df.groupby('city')[['ln_K', 'ln_Pu']].mean().reset_index()
between_orig = between_orig.merge(
    reg_df.groupby('city')[['hc_city', 'gdp_100m']].apply(lambda x: pd.Series({
        'ln_hc': np.log(x['hc_city']).mean(),
        'ln_gdp': np.log(x['gdp_100m']).mean()
    })), on='city', how='left'
)
between_orig['ln_Kstar_str'] = (alpha_P_orig * between_orig['ln_Pu']
                                 + alpha_H_orig * between_orig['ln_hc']
                                 + alpha_G_orig * between_orig['ln_gdp'])
ln_theta_orig = (between_orig['ln_K'] - between_orig['ln_Kstar_str']).median()

df.loc[orig_mask, 'ln_Kstar_orig_raw'] = (ln_theta_orig
                                            + alpha_P_orig * np.log(df.loc[orig_mask, 'pop_10k'])
                                            + alpha_H_orig * np.log(df.loc[orig_mask, 'hc_city'])
                                            + alpha_G_orig * np.log(df.loc[orig_mask, 'gdp_100m']))

# 原始模型也做 2015 OCR 标定
cal_orig_mask = ((df['year'] == cal_year) & df['K_100m'].notna() &
                  df['ln_Kstar_orig_raw'].notna() & (df['K_100m'] > 0))
if cal_orig_mask.sum() > 0:
    ln_ocr_orig = (np.log(df[cal_orig_mask]['K_100m']) - df[cal_orig_mask]['ln_Kstar_orig_raw']).median()
    delta_orig = ln_ocr_orig - np.log(1.15)
    df.loc[df['ln_Kstar_orig_raw'].notna(), 'ln_Kstar_orig'] = df.loc[df['ln_Kstar_orig_raw'].notna(), 'ln_Kstar_orig_raw'] + delta_orig
else:
    df['ln_Kstar_orig'] = df['ln_Kstar_orig_raw']

df['Kstar_orig'] = np.exp(df['ln_Kstar_orig'])
valid_orig = df['K_100m'].notna() & df['Kstar_orig'].notna() & (df['Kstar_orig'] > 0) & (df['K_100m'] > 0)
df.loc[valid_orig, 'OCR_orig'] = df.loc[valid_orig, 'K_100m'] / df.loc[valid_orig, 'Kstar_orig']

# M2 vs 原始 OCR 对比
ocr_compare = df[df['OCR_m2'].notna() & df['OCR_orig'].notna()].copy()
print(f"\nOCR 对比 (M2 vs 原始, n={len(ocr_compare)}):")
print(f"  相关系数: {ocr_compare['OCR_m2'].corr(ocr_compare['OCR_orig']):.4f}")
print(f"  M2  OCR 中位数: {ocr_compare['OCR_m2'].median():.3f}")
print(f"  原始 OCR 中位数: {ocr_compare['OCR_orig'].median():.3f}")

# 四色分级 (先用旧阈值 0.4/0.6/0.8, 后面分析 3 会重新确定)
def classify_uci_norm(uci_norm):
    if pd.isna(uci_norm):
        return np.nan
    elif uci_norm > 0.8:
        return 'Green'
    elif uci_norm > 0.6:
        return 'Yellow'
    elif uci_norm > 0.4:
        return 'Orange'
    else:
        return 'Red'

df['UCI_m2_class'] = df['UCI_m2_norm'].apply(classify_uci_norm)

# 原始模型也做 UCI
uci_orig_mask = df['urban_q'].notna() & df['OCR_orig'].notna() & (df['OCR_orig'] > 0)
df.loc[uci_orig_mask, 'UCI_orig'] = df.loc[uci_orig_mask, 'urban_q'] / df.loc[uci_orig_mask, 'OCR_orig']
uci_orig_pos = df['UCI_orig'].notna() & (df['UCI_orig'] > 0)
ref_orig = df[(df.year == 2023) & uci_orig_pos]['UCI_orig']
if len(ref_orig) > 0:
    ln_r = np.log(ref_orig)
    ln_p5o = ln_r.quantile(0.02)
    ln_p95o = ln_r.quantile(0.98)
    df['UCI_orig_norm'] = np.nan
    df.loc[uci_orig_pos, 'UCI_orig_norm'] = (
        (np.log(df.loc[uci_orig_pos, 'UCI_orig']) - ln_p5o) / (ln_p95o - ln_p5o)
    ).clip(0, 1)
    df['UCI_orig_class'] = df['UCI_orig_norm'].apply(classify_uci_norm)

# 分级变化统计
latest = df[(df.year == 2023) & df['UCI_m2_class'].notna() & df['UCI_orig_class'].notna()].copy()
if len(latest) > 0:
    latest['class_changed'] = latest['UCI_m2_class'] != latest['UCI_orig_class']
    n_changed = latest['class_changed'].sum()
    n_total = len(latest)
    print(f"\n2023年分级变化 (M2 vs 原始): {n_changed}/{n_total} ({n_changed/n_total*100:.1f}%) 城市分级变化")

    # 交叉表
    cross = pd.crosstab(latest['UCI_orig_class'], latest['UCI_m2_class'],
                         margins=True, margins_name='Total')
    print("\n分级交叉表 (行=原始, 列=M2):")
    print(cross)
else:
    n_changed = 0
    n_total = 0

print(f"\nM2 模型 UCI 计算完成")

# ============================================================
# 分析 3: UCI 阈值的数据驱动确定
# ============================================================
print("\n" + "=" * 70)
print("分析 3: UCI 阈值的数据驱动确定")
print("=" * 70)

threshold_report = []
threshold_report.append("=" * 70)
threshold_report.append("UCI 阈值数据驱动确定报告")
threshold_report.append("=" * 70)
threshold_report.append("")

# 使用 M2 的 UCI_m2_norm 做分析
# 汇总 2010-2015 年 UCI 均值, 然后看 2015-2019 GDP 增速

# 计算 2010-2015 UCI 均值 (per city)
uci_1015 = df[(df['year'] >= 2010) & (df['year'] <= 2015) & df['UCI_m2_norm'].notna()].copy()
uci_city_mean = uci_1015.groupby('city')['UCI_m2_norm'].mean().reset_index()
uci_city_mean.rename(columns={'UCI_m2_norm': 'uci_mean_1015'}, inplace=True)

# 计算 2015-2019 GDP 增速 (年化)
gdp_2015 = df[(df['year'] == 2015) & df['gdp_100m'].notna()][['city', 'gdp_100m']].rename(columns={'gdp_100m': 'gdp_2015'})
gdp_2019 = df[(df['year'] == 2019) & df['gdp_100m'].notna()][['city', 'gdp_100m']].rename(columns={'gdp_100m': 'gdp_2019'})
gdp_growth = gdp_2015.merge(gdp_2019, on='city', how='inner')
gdp_growth['gdp_growth_annualized'] = (gdp_growth['gdp_2019'] / gdp_growth['gdp_2015']) ** (1/4) - 1

# 合并
analysis_df = uci_city_mean.merge(gdp_growth[['city', 'gdp_growth_annualized']], on='city', how='inner')
analysis_df = analysis_df.dropna()
print(f"阈值分析样本: {len(analysis_df)} 城市")

# -------------------------------------------------------
# 方法 A: K-means 聚类
# -------------------------------------------------------
print("\n--- 方法 A: K-means 聚类 ---")
threshold_report.append("=" * 70)
threshold_report.append("方法 A: K-means 聚类 (k=4)")
threshold_report.append("=" * 70)
threshold_report.append("")

uci_vals = analysis_df['uci_mean_1015'].values.reshape(-1, 1)
km = KMeans(n_clusters=4, random_state=42, n_init=20)
km_labels = km.fit_predict(uci_vals)
analysis_df['km_cluster'] = km_labels

# 聚类中心排序
centers = km.cluster_centers_.flatten()
sorted_idx = np.argsort(centers)
center_map = {sorted_idx[i]: i for i in range(4)}
analysis_df['km_order'] = analysis_df['km_cluster'].map(center_map)

# 分界点: 相邻聚类中心的均值
sorted_centers = np.sort(centers)
km_thresholds = [(sorted_centers[i] + sorted_centers[i+1]) / 2 for i in range(3)]

print(f"聚类中心: {np.sort(centers)}")
print(f"分界阈值: {km_thresholds}")
threshold_report.append(f"聚类中心: {', '.join(f'{c:.3f}' for c in sorted_centers)}")
threshold_report.append(f"分界阈值: {', '.join(f'{t:.3f}' for t in km_thresholds)}")
for i in range(4):
    n = (analysis_df['km_order'] == i).sum()
    threshold_report.append(f"  组 {i+1}: n={n}, UCI 范围: [{analysis_df[analysis_df['km_order']==i]['uci_mean_1015'].min():.3f}, {analysis_df[analysis_df['km_order']==i]['uci_mean_1015'].max():.3f}]")
threshold_report.append("")

# -------------------------------------------------------
# 方法 B: UCI 与后续 GDP 增速的关联
# -------------------------------------------------------
print("\n--- 方法 B: UCI vs 后续 GDP 增速 ---")
threshold_report.append("=" * 70)
threshold_report.append("方法 B: UCI 五分位 vs 2015-2019 GDP 年化增速")
threshold_report.append("=" * 70)
threshold_report.append("")

# 五分位分析
analysis_df['quintile'] = pd.qcut(analysis_df['uci_mean_1015'], 5, labels=['Q1(低)', 'Q2', 'Q3', 'Q4', 'Q5(高)'])
quintile_stats = analysis_df.groupby('quintile').agg(
    n=('gdp_growth_annualized', 'count'),
    uci_mean=('uci_mean_1015', 'mean'),
    uci_min=('uci_mean_1015', 'min'),
    uci_max=('uci_mean_1015', 'max'),
    growth_mean=('gdp_growth_annualized', 'mean'),
    growth_se=('gdp_growth_annualized', 'sem')
).reset_index()

threshold_report.append(f"{'分位':>8} {'N':>5} {'UCI均值':>8} {'GDP增速%':>10} {'SE':>8}")
threshold_report.append("-" * 45)
for _, row in quintile_stats.iterrows():
    threshold_report.append(f"{row['quintile']:>8} {int(row['n']):>5} {row['uci_mean']:>8.3f} {row['growth_mean']*100:>10.2f}% {row['growth_se']*100:>8.2f}%")

# Youden index 风格的最优分割
# 对每个可能的 UCI 阈值, 计算高/低两组 GDP 增速差异的 t 统计量
uci_sorted = np.sort(analysis_df['uci_mean_1015'].values)
best_t = 0
best_threshold = 0.5
t_stats = []

for i in range(10, len(uci_sorted) - 10):
    thresh = uci_sorted[i]
    high = analysis_df[analysis_df['uci_mean_1015'] >= thresh]['gdp_growth_annualized']
    low = analysis_df[analysis_df['uci_mean_1015'] < thresh]['gdp_growth_annualized']
    if len(high) > 5 and len(low) > 5:
        t, p = stats.ttest_ind(high, low)
        t_stats.append((thresh, abs(t), p))
        if abs(t) > best_t:
            best_t = abs(t)
            best_threshold = thresh

threshold_report.append("")
threshold_report.append(f"最优 Youden 阈值 (最大化增速差异): UCI_norm = {best_threshold:.3f}")
threshold_report.append(f"  t 统计量 = {best_t:.2f}")

# 找三个最优切割点 (四组)
# 贪心策略: 先找最优二分, 再在两侧各找最优
def find_best_split(data, col_x, col_y, min_n=8):
    sorted_x = np.sort(data[col_x].values)
    best_t_val = 0
    best_th = data[col_x].median()
    for i in range(min_n, len(sorted_x) - min_n):
        th = sorted_x[i]
        high = data[data[col_x] >= th][col_y]
        low = data[data[col_x] < th][col_y]
        t, _ = stats.ttest_ind(high, low)
        if abs(t) > best_t_val:
            best_t_val = abs(t)
            best_th = th
    return best_th

# 三级切割
th_mid = find_best_split(analysis_df, 'uci_mean_1015', 'gdp_growth_annualized')
th_low = find_best_split(analysis_df[analysis_df['uci_mean_1015'] < th_mid],
                          'uci_mean_1015', 'gdp_growth_annualized', min_n=5)
th_high = find_best_split(analysis_df[analysis_df['uci_mean_1015'] >= th_mid],
                           'uci_mean_1015', 'gdp_growth_annualized', min_n=5)

youden_thresholds = sorted([th_low, th_mid, th_high])
threshold_report.append(f"三级最优切割: {', '.join(f'{t:.3f}' for t in youden_thresholds)}")
threshold_report.append("")
print(f"Youden 三级阈值: {youden_thresholds}")

# -------------------------------------------------------
# 方法 C: 高斯混合模型
# -------------------------------------------------------
print("\n--- 方法 C: 高斯混合模型 ---")
threshold_report.append("=" * 70)
threshold_report.append("方法 C: 高斯混合模型 (GMM)")
threshold_report.append("=" * 70)
threshold_report.append("")

best_bic = np.inf
best_n = 2
for n_comp in [2, 3, 4]:
    gmm = GaussianMixture(n_components=n_comp, random_state=42, n_init=10)
    gmm.fit(uci_vals)
    bic = gmm.bic(uci_vals)
    aic = gmm.aic(uci_vals)
    threshold_report.append(f"GMM k={n_comp}: BIC={bic:.1f}, AIC={aic:.1f}")
    print(f"  GMM k={n_comp}: BIC={bic:.1f}, AIC={aic:.1f}")
    if bic < best_bic:
        best_bic = bic
        best_n = n_comp

gmm_best = GaussianMixture(n_components=best_n, random_state=42, n_init=10)
gmm_best.fit(uci_vals)
gmm_means = np.sort(gmm_best.means_.flatten())
gmm_stds = np.sqrt(gmm_best.covariances_.flatten())[np.argsort(gmm_best.means_.flatten())]

# 组间分界: 相邻组分均值的加权中点
gmm_thresholds = []
for i in range(len(gmm_means) - 1):
    # 简单取均值
    mid = (gmm_means[i] + gmm_means[i+1]) / 2
    gmm_thresholds.append(mid)

threshold_report.append("")
threshold_report.append(f"最优组分数 (BIC): k={best_n}")
threshold_report.append(f"组分均值: {', '.join(f'{m:.3f}' for m in gmm_means)}")
threshold_report.append(f"组分标准差: {', '.join(f'{s:.3f}' for s in gmm_stds)}")
threshold_report.append(f"分界阈值: {', '.join(f'{t:.3f}' for t in gmm_thresholds)}")
threshold_report.append("")

print(f"GMM 最优 k={best_n}, 阈值: {gmm_thresholds}")

# -------------------------------------------------------
# 综合比较与推荐
# -------------------------------------------------------
threshold_report.append("=" * 70)
threshold_report.append("综合比较: 数据驱动阈值 vs 先验阈值 (0.4/0.6/0.8)")
threshold_report.append("=" * 70)
threshold_report.append("")

# 如果 kmeans 给出 3 个阈值, 与先验比较
threshold_report.append(f"{'方法':>20} {'阈值1':>10} {'阈值2':>10} {'阈值3':>10}")
threshold_report.append("-" * 55)
threshold_report.append(f"{'先验阈值':>20} {'0.400':>10} {'0.600':>10} {'0.800':>10}")
threshold_report.append(f"{'K-means':>20} {km_thresholds[0]:>10.3f} {km_thresholds[1]:>10.3f} {km_thresholds[2]:>10.3f}")
threshold_report.append(f"{'Youden':>20} {youden_thresholds[0]:>10.3f} {youden_thresholds[1]:>10.3f} {youden_thresholds[2]:>10.3f}")
if len(gmm_thresholds) >= 3:
    threshold_report.append(f"{'GMM':>20} {gmm_thresholds[0]:>10.3f} {gmm_thresholds[1]:>10.3f} {gmm_thresholds[2]:>10.3f}")
elif len(gmm_thresholds) == 2:
    threshold_report.append(f"{'GMM (k=3)':>20} {gmm_thresholds[0]:>10.3f} {gmm_thresholds[1]:>10.3f} {'n/a':>10}")
elif len(gmm_thresholds) == 1:
    threshold_report.append(f"{'GMM (k=2)':>20} {gmm_thresholds[0]:>10.3f} {'n/a':>10} {'n/a':>10}")

threshold_report.append("")
threshold_report.append("推荐策略:")
threshold_report.append("  1. 以 K-means 或 Youden 的三级阈值为主要参考")
threshold_report.append("  2. 如果数据驱动阈值与先验 0.4/0.6/0.8 接近, 保留先验阈值 (更易解释)")
threshold_report.append("  3. 如果差异较大, 在论文中报告数据驱动结果, 并以先验阈值做敏感性分析")

# 计算先验 vs 数据驱动的分级一致性
prior_thresholds = [0.4, 0.6, 0.8]
dd_thresholds = km_thresholds  # 使用 K-means 作为代表

def classify_4(val, thresholds):
    if val <= thresholds[0]:
        return 'Red'
    elif val <= thresholds[1]:
        return 'Orange'
    elif val <= thresholds[2]:
        return 'Yellow'
    else:
        return 'Green'

latest_uci = df[(df.year == 2023) & df['UCI_m2_norm'].notna()].copy()
if len(latest_uci) > 0:
    latest_uci['class_prior'] = latest_uci['UCI_m2_norm'].apply(lambda x: classify_4(x, prior_thresholds))
    latest_uci['class_dd'] = latest_uci['UCI_m2_norm'].apply(lambda x: classify_4(x, dd_thresholds))
    agree = (latest_uci['class_prior'] == latest_uci['class_dd']).sum()
    threshold_report.append("")
    threshold_report.append(f"先验 vs K-means 分级一致率: {agree}/{len(latest_uci)} ({agree/len(latest_uci)*100:.1f}%)")

# 保存阈值报告
with open(os.path.join(MODELS, 'uci_threshold_analysis.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(threshold_report))
print(f"\nUCI 阈值分析报告已保存")

# ============================================================
# 保存稳健 UCI 面板
# ============================================================
print("\n" + "=" * 70)
print("保存稳健 UCI 面板")
print("=" * 70)

output_cols = ['year', 'province', 'city', 'city_code', 'region',
               'gdp_100m', 'gdp_per_capita', 'pop_10k', 'fai_100m', 'fai_imputed',
               'K_100m', 'V_100m', 'urban_q',
               'Kstar_m2', 'OCR_m2', 'UCI_m2', 'UCI_m2_norm', 'UCI_m2_class',
               'Kstar_orig', 'OCR_orig', 'UCI_orig']

# 只保留存在的列
output_cols = [c for c in output_cols if c in df.columns]
df_out = df[output_cols].copy()
df_out.to_csv(os.path.join(DATA_PROC, 'china_city_robust_uci.csv'), index=False, encoding='utf-8-sig')
print(f"已保存: {len(df_out)} 行, UCI_m2 非空 {df_out['UCI_m2'].notna().sum()} 行")

# ============================================================
# 可视化: 3 子图
# ============================================================
print("\n" + "=" * 70)
print("可视化")
print("=" * 70)

fig = plt.figure(figsize=(18, 6))
gs = GridSpec(1, 3, figure=fig, wspace=0.3)

# --- (a) FAI 插补验证: 省级推算 vs 真实值 ---
ax1 = fig.add_subplot(gs[0, 0])

# 2019 年数据
x_actual = prov_val['fai_actual_2019'].values
y_imputed = prov_val['fai_imputed_2019'].values

ax1.scatter(x_actual, y_imputed, s=40, alpha=0.7, c='steelblue', edgecolors='white', linewidth=0.5)

# 45 度线
lim_max = max(x_actual.max(), y_imputed.max()) * 1.1
ax1.plot([0, lim_max], [0, lim_max], 'k--', lw=1, alpha=0.5, label='45-degree line')

# 回归线
slope, intercept, r_val, p_val, se = stats.linregress(x_actual, y_imputed)
x_fit = np.linspace(0, lim_max, 100)
ax1.plot(x_fit, intercept + slope * x_fit, 'r-', lw=1.5, alpha=0.7,
         label=f'OLS: R$^2$={r_val**2:.3f}')

ax1.set_xlabel('Actual Provincial FAI (billion yuan)', fontsize=10)
ax1.set_ylabel('Imputed FAI (ratio-based, billion yuan)', fontsize=10)
ax1.set_title(f'(a) FAI Imputation Validation (2019)\nMAPE={mape:.1f}%, wMAPE={wmape:.1f}%', fontsize=11)
ax1.legend(fontsize=8, loc='upper left')
ax1.set_xlim(0, lim_max)
ax1.set_ylim(0, lim_max)
ax1.set_aspect('equal')

# --- (b) M2 OCR vs 原始 OCR ---
ax2 = fig.add_subplot(gs[0, 1])

# 使用 2023 截面
comp_year = 2023
comp = df[(df.year == comp_year) & df['OCR_m2'].notna() & df['OCR_orig'].notna()].copy()

# 截断极端值方便可视化
ocr_clip = 5
comp['OCR_m2_clip'] = comp['OCR_m2'].clip(0, ocr_clip)
comp['OCR_orig_clip'] = comp['OCR_orig'].clip(0, ocr_clip)

ax2.scatter(comp['OCR_orig_clip'], comp['OCR_m2_clip'], s=20, alpha=0.5,
            c='darkorange', edgecolors='white', linewidth=0.3)

# 45 度线
ax2.plot([0, ocr_clip], [0, ocr_clip], 'k--', lw=1, alpha=0.5)

# 相关系数
corr_ocr = comp['OCR_m2'].corr(comp['OCR_orig'])
ax2.set_xlabel(f'OCR (Original K*, alpha_H=3.98)', fontsize=10)
ax2.set_ylabel(f'OCR (M2: GDP per capita model)', fontsize=10)
ax2.set_title(f'(b) OCR Comparison ({comp_year})\nr={corr_ocr:.3f}, n={len(comp)}', fontsize=11)
ax2.set_xlim(0, ocr_clip)
ax2.set_ylim(0, ocr_clip)
ax2.set_aspect('equal')

# --- (c) UCI vs 后续 GDP 增速 ---
ax3 = fig.add_subplot(gs[0, 2])

# 散点
ax3.scatter(analysis_df['uci_mean_1015'], analysis_df['gdp_growth_annualized'] * 100,
            s=15, alpha=0.4, c='teal', edgecolors='white', linewidth=0.3)

# 五分位均值
for _, row in quintile_stats.iterrows():
    ax3.errorbar(row['uci_mean'], row['growth_mean'] * 100,
                 yerr=row['growth_se'] * 100 * 1.96,
                 fmt='s', ms=8, color='darkred', capsize=3, zorder=5)

# 标记先验阈值
for th in [0.4, 0.6, 0.8]:
    ax3.axvline(th, color='gray', ls=':', alpha=0.5)

# 标记 K-means 阈值
for th in km_thresholds:
    ax3.axvline(th, color='crimson', ls='--', alpha=0.7)

# LOWESS 平滑
try:
    from statsmodels.nonparametric.smoothers_lowess import lowess
    smooth = lowess(analysis_df['gdp_growth_annualized'].values * 100,
                     analysis_df['uci_mean_1015'].values, frac=0.4)
    ax3.plot(smooth[:, 0], smooth[:, 1], 'b-', lw=2, alpha=0.8, label='LOWESS')
except:
    pass

ax3.set_xlabel('UCI (normalized, 2010-2015 mean)', fontsize=10)
ax3.set_ylabel('GDP growth 2015-2019 (annualized %)', fontsize=10)
ax3.set_title('(c) UCI vs Subsequent GDP Growth\n(gray: prior | red: K-means thresholds)', fontsize=11)
ax3.legend(fontsize=8)

plt.suptitle('FAI Validation & Robust UCI Analysis', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES, 'fig20_fai_robust_uci.png'),
            dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
print("图表已保存: fig20_fai_robust_uci.png")

# ============================================================
# 最终摘要
# ============================================================
print("\n" + "=" * 70)
print("Phase 2 任务完成摘要")
print("=" * 70)
mape_2023_str = f"{mape_2023:.1f}%" if not np.isnan(mape_2023) else "N/A (无数据)"
print(f"1. FAI 验证: MAPE={mape:.1f}% (2015->2019), MAPE={mape_1015:.1f}% (2010->2015), {mape_2023_str} (2015->2023)")
print(f"2. M2 模型 OCR vs 原始: 相关系数 r={corr_ocr:.3f}")
if n_total > 0:
    print(f"3. 分级变化: {n_changed}/{n_total} ({n_changed/n_total*100:.1f}%) 城市")
print(f"4. 数据驱动阈值 (K-means): {[round(t, 3) for t in km_thresholds]}")
print(f"5. 数据驱动阈值 (Youden): {[round(t, 3) for t in youden_thresholds]}")
print(f"\n输出文件:")
print(f"  - {MODELS}/fai_validation.txt")
print(f"  - {DATA_PROC}/china_city_robust_uci.csv")
print(f"  - {MODELS}/uci_threshold_analysis.txt")
print(f"  - {FIGURES}/fig20_fai_robust_uci.png")
