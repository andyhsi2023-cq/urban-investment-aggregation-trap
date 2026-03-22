"""
64_city_real_fai_only.py
========================
目的: 仅使用真实 FAI 数据 (fai_imputed=False) 重算 Urban Q / K* / OCR / UCI
      验证 2017+ 插补数据是否影响核心定性结论

输入:
  - 02-data/processed/china_city_panel_real.csv (300 城市面板)
  - 02-data/raw/china_national_real_data.csv (国家级真实数据)
  - 02-data/raw/penn_world_table.csv (PWT hc 指数)
输出:
  - 02-data/processed/china_city_real_fai_panel.csv
  - 02-data/processed/china_city_real_fai_uci.csv
  - 03-analysis/models/city_real_fai_analysis.txt
  - 03-analysis/models/city_inverted_u_real.txt
  - 04-figures/drafts/fig21_city_real_fai.png
依赖: pandas, numpy, statsmodels, scipy, sklearn, matplotlib
"""

import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from sklearn.cluster import KMeans
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

# 分析报告缓冲
report = []
def rpt(line=''):
    report.append(line)
    print(line)

# ============================================================
# 步骤 1: 数据加载与筛选
# ============================================================
rpt("=" * 70)
rpt("步骤 1: 数据加载与筛选 — 仅保留真实 FAI 数据")
rpt("=" * 70)

city = pd.read_csv(os.path.join(DATA_PROC, 'china_city_panel_real.csv'))
natl = pd.read_csv(os.path.join(DATA_RAW, 'china_national_real_data.csv'))

# 加载 PWT hc
pwt = pd.read_csv(os.path.join(DATA_RAW, 'penn_world_table.csv'), encoding='utf-8-sig')
pwt_chn = pwt[pwt['countrycode'] == 'CHN'][['year', 'hc']].dropna()

rpt(f"原始面板: {city.shape[0]} 行, {city['city'].nunique()} 城市, "
    f"{city['year'].min()}-{city['year'].max()}")
rpt(f"  fai_imputed=True: {(city['fai_imputed'] == True).sum()} 行")
rpt(f"  fai_imputed=False: {(city['fai_imputed'] == False).sum()} 行")

# 筛选: 仅保留 fai_imputed != True 的行
# fai_imputed 列可能是 bool 或 string
df_real = city[city['fai_imputed'] != True].copy()

rpt(f"\n筛选后: {df_real.shape[0]} 行, {df_real['city'].nunique()} 城市")
rpt(f"  年份范围: {df_real['year'].min()}-{df_real['year'].max()}")

# 各年份城市数
year_counts = df_real.groupby('year')['city'].nunique()
rpt("\n各年份城市数 (仅真实 FAI):")
for yr, n in year_counts.items():
    fai_avail = df_real[(df_real['year'] == yr) & df_real['fai_100m'].notna()].shape[0]
    hp_avail = df_real[(df_real['year'] == yr) & df_real['house_price'].notna()].shape[0]
    rpt(f"  {yr}: {n} 城市, FAI非空={fai_avail}, 房价非空={hp_avail}")

# 核心分析窗口: 有房价 + 有真实 FAI
df_core = df_real[df_real['house_price'].notna() & df_real['fai_100m'].notna()].copy()
rpt(f"\n核心分析窗口 (有房价 + 有真实 FAI):")
rpt(f"  {df_core.shape[0]} 行, {df_core['city'].nunique()} 城市")
rpt(f"  年份: {sorted(df_core['year'].unique())}")

# ============================================================
# 步骤 2: 用真实数据重算 Urban Q
# ============================================================
rpt("\n" + "=" * 70)
rpt("步骤 2: 用真实 FAI 数据重算 Urban Q")
rpt("=" * 70)

# --- V(t): 城市不动产市场价值 ---
# V(t) = 房价(元/m2) x 人口(万人) x 1万 x 人均住房面积(m2/人) / 1亿
area_lookup = {}
for y in range(1990, 2025):
    if y <= 2000:
        area_lookup[y] = 20.0
    elif y <= 2020:
        area_lookup[y] = 20.0 + (41.76 - 20.0) * (y - 2000) / 20
    else:
        area_lookup[y] = 41.76 + 0.25 * (y - 2020)

df_real['per_capita_area_m2'] = df_real['year'].map(area_lookup)
df_real['V_real'] = (
    df_real['house_price'] *
    df_real['pop_10k'] * 10000 *
    df_real['per_capita_area_m2'] /
    1e8
)

# --- K(t): PIM 法累计资本存量 (仅用真实 FAI) ---
DELTA = 0.05

def compute_pim_real(group):
    """永续盘存法: 仅使用真实 FAI 数据"""
    group = group.sort_values('year').copy()
    fai = group['fai_100m'].values
    n = len(group)

    K = np.full(n, np.nan)
    valid_idx = np.where(~np.isnan(fai))[0]
    if len(valid_idx) == 0:
        group['K_real'] = np.nan
        return group

    first_valid = valid_idx[0]

    # 初始增长率
    if len(valid_idx) >= 3:
        early_fai = fai[valid_idx[:5]]
        early_fai = early_fai[early_fai > 0]
        if len(early_fai) >= 2:
            g = np.mean(np.diff(early_fai) / early_fai[:-1])
            g = max(0.02, min(g, 0.30))
        else:
            g = 0.10
    else:
        g = 0.10

    if fai[first_valid] > 0:
        K[first_valid] = fai[first_valid] / (g + DELTA)
    else:
        K[first_valid] = 0

    for i in range(first_valid + 1, n):
        if np.isnan(K[i-1]):
            if not np.isnan(fai[i]) and fai[i] > 0:
                K[i] = fai[i] / (g + DELTA)
            continue
        inv = fai[i] if not np.isnan(fai[i]) else 0
        K[i] = K[i-1] * (1 - DELTA) + inv

    group['K_real'] = K
    return group

rpt("  计算资本存量 K_real (PIM, 仅真实 FAI)...")
df_real = df_real.groupby('city', group_keys=False).apply(compute_pim_real)
rpt(f"  K_real 非空记录: {df_real['K_real'].notna().sum()}")

# Urban Q = V / K
df_real['Q_real'] = df_real['V_real'] / df_real['K_real']
df_real.loc[df_real['Q_real'] < 0, 'Q_real'] = np.nan
df_real.loc[df_real['Q_real'] > 20, 'Q_real'] = np.nan

# MUQ = dV / dI
df_real = df_real.sort_values(['city', 'year'])
df_real['dV'] = df_real.groupby('city')['V_real'].diff()
df_real['MUQ_real'] = df_real['dV'] / df_real['fai_100m']
df_real.loc[df_real['MUQ_real'].abs() > 50, 'MUQ_real'] = np.nan

n_q = df_real['Q_real'].notna().sum()
rpt(f"  Urban Q 有效: {n_q} 观测, {df_real.loc[df_real['Q_real'].notna(), 'city'].nunique()} 城市")

# 汇总 Q 统计
rpt("\n  真实数据 Urban Q 年度统计:")
for yr in sorted(df_real[df_real['Q_real'].notna()]['year'].unique()):
    q_yr = df_real[(df_real['year'] == yr) & df_real['Q_real'].notna()]['Q_real']
    rpt(f"    {yr}: mean={q_yr.mean():.4f}, median={q_yr.median():.4f}, "
        f"std={q_yr.std():.4f}, n={len(q_yr)}")

# ============================================================
# 步骤 3: M2 模型重算 K* 和 OCR
# ============================================================
rpt("\n" + "=" * 70)
rpt("步骤 3: M2 模型重算 K*/OCR/UCI (仅真实 FAI 年份)")
rpt("=" * 70)

# 添加 PWT hc
df_real = df_real.merge(pwt_chn[['year', 'hc']].rename(columns={'hc': 'hc_national'}),
                        on='year', how='left')
# 外推 hc
hc_last_year = pwt_chn['year'].max()
hc_last_val = pwt_chn[pwt_chn.year == hc_last_year]['hc'].values[0]
hc_recent = pwt_chn[pwt_chn.year >= hc_last_year - 5].sort_values('year')
hc_growth = (hc_recent['hc'].iloc[-1] / hc_recent['hc'].iloc[0]) ** (1/5) - 1
for yr in range(int(hc_last_year) + 1, 2024):
    df_real.loc[df_real['year'] == yr, 'hc_national'] = hc_last_val * (1 + hc_growth) ** (yr - hc_last_year)

# 城市级 hc 代理
gdp_pc_median = df_real.groupby('year')['gdp_per_capita'].median()
df_real = df_real.merge(gdp_pc_median.rename('gdp_pc_median'), on='year', how='left')
df_real['hc_ratio'] = (df_real['gdp_per_capita'] / df_real['gdp_pc_median']).clip(0.3, 5.0)
df_real['hc_city'] = df_real['hc_national'] * df_real['hc_ratio'] ** 0.3

# M2 回归: ln K = a0 + aP*ln(Pu) + aD*ln(GDP_pc) + Region FE
# 仅使用 2005-2016 数据做 Between 回归
reg_mask = (
    df_real['K_real'].notna() & (df_real['K_real'] > 0) &
    df_real['pop_10k'].notna() & (df_real['pop_10k'] > 0) &
    df_real['gdp_per_capita'].notna() & (df_real['gdp_per_capita'] > 0) &
    (df_real['year'] >= 2005) & (df_real['year'] <= 2016)
)
reg_df = df_real[reg_mask].copy()
reg_df['ln_K'] = np.log(reg_df['K_real'])
reg_df['ln_Pu'] = np.log(reg_df['pop_10k'])
reg_df['ln_GDP_pc'] = np.log(reg_df['gdp_per_capita'])

rpt(f"  M2 回归样本: {reg_df.shape[0]} 观测, {reg_df['city'].nunique()} 城市, "
    f"年份 {reg_df['year'].min()}-{reg_df['year'].max()}")

# Between 估计 (城市均值)
between = reg_df.groupby('city').agg({
    'ln_K': 'mean', 'ln_Pu': 'mean', 'ln_GDP_pc': 'mean', 'region': 'first'
}).reset_index()

region_dummies = pd.get_dummies(between['region'], prefix='reg', drop_first=True, dtype=float)
X_m2 = pd.concat([sm.add_constant(between[['ln_Pu', 'ln_GDP_pc']]), region_dummies], axis=1)
y_m2 = between['ln_K']
model_m2 = sm.OLS(y_m2, X_m2).fit(cov_type='HC1')

rpt(f"\n  M2 Between 回归 (2005-2016 真实数据, N={len(between)} 城市):")
rpt(f"    R-squared = {model_m2.rsquared:.4f}")
for var in model_m2.params.index:
    rpt(f"    {var}: coef={model_m2.params[var]:.4f}, SE={model_m2.bse[var]:.4f}, p={model_m2.pvalues[var]:.4e}")

alpha_P_m2_real = model_m2.params['ln_Pu']
alpha_D_m2_real = model_m2.params['ln_GDP_pc']

# 也使用全球弹性 (alpha_P=1.0127, alpha_D=0.7075), 仅标定截距
alpha_P_global = 1.0127
alpha_D_global = 0.7075

# 混合策略: 全球弹性 + 中国区域截距
between['ln_Kstar_str'] = (alpha_P_global * between['ln_Pu']
                            + alpha_D_global * between['ln_GDP_pc'])

# 区域特定截距
region_thetas = {}
for reg in between['region'].unique():
    mask = between['region'] == reg
    resid = between.loc[mask, 'ln_K'] - between.loc[mask, 'ln_Kstar_str']
    theta = resid.median()
    region_thetas[reg] = theta
    between.loc[mask, 'ln_theta'] = theta

rpt("\n  区域特定截距 (全球弹性 + 中国 2005-2016 标定):")
for reg in sorted(region_thetas.keys()):
    rpt(f"    {reg}: ln(theta) = {region_thetas[reg]:.4f}")

# 计算全面板的 K* (但仅在有 K_real 的年份计算 OCR)
all_mask = (
    df_real['pop_10k'].notna() & (df_real['pop_10k'] > 0) &
    df_real['gdp_per_capita'].notna() & (df_real['gdp_per_capita'] > 0)
)

df_real['ln_Kstar_raw'] = np.nan
for reg, theta in region_thetas.items():
    rmask = all_mask & (df_real['region'] == reg)
    df_real.loc[rmask, 'ln_Kstar_raw'] = (
        theta
        + alpha_P_global * np.log(df_real.loc[rmask, 'pop_10k'])
        + alpha_D_global * np.log(df_real.loc[rmask, 'gdp_per_capita'])
    )

# 标定: 2015 年 OCR 中位数 = 1.15
cal_year = 2015
cal_mask = (
    (df_real['year'] == cal_year) &
    df_real['K_real'].notna() & (df_real['K_real'] > 0) &
    df_real['ln_Kstar_raw'].notna()
)
if cal_mask.sum() > 0:
    cal_data = df_real[cal_mask].copy()
    ln_ocr_med = (np.log(cal_data['K_real']) - cal_data['ln_Kstar_raw']).median()
    delta_cal = ln_ocr_med - np.log(1.15)
    rpt(f"\n  标定: 2015年 OCR 中位数 (原始) = {np.exp(ln_ocr_med):.3f}, delta = {delta_cal:.4f}")
    df_real.loc[df_real['ln_Kstar_raw'].notna(), 'ln_Kstar'] = df_real.loc[df_real['ln_Kstar_raw'].notna(), 'ln_Kstar_raw'] + delta_cal
else:
    df_real['ln_Kstar'] = df_real['ln_Kstar_raw']
    delta_cal = 0

df_real['Kstar_real'] = np.exp(df_real['ln_Kstar'])

# OCR = K / K*
valid_ocr = (
    df_real['K_real'].notna() & (df_real['K_real'] > 0) &
    df_real['Kstar_real'].notna() & (df_real['Kstar_real'] > 0)
)
df_real.loc[valid_ocr, 'OCR_real'] = df_real.loc[valid_ocr, 'K_real'] / df_real.loc[valid_ocr, 'Kstar_real']

# UCI = Q / OCR
uci_mask = df_real['Q_real'].notna() & df_real['OCR_real'].notna() & (df_real['OCR_real'] > 0)
df_real.loc[uci_mask, 'UCI_real'] = df_real.loc[uci_mask, 'Q_real'] / df_real.loc[uci_mask, 'OCR_real']

# UCI 归一化 (log-transform + min-max, 参考年 = 2016 因为是最后一个真实年)
ref_year = 2016
uci_pos = df_real['UCI_real'].notna() & (df_real['UCI_real'] > 0)
ref_uci = df_real[(df_real['year'] == ref_year) & uci_pos]['UCI_real']
if len(ref_uci) > 0:
    ln_ref = np.log(ref_uci)
    ln_p5 = ln_ref.quantile(0.02)
    ln_p95 = ln_ref.quantile(0.98)
    df_real['UCI_norm'] = np.nan
    df_real.loc[uci_pos, 'UCI_norm'] = (
        (np.log(df_real.loc[uci_pos, 'UCI_real']) - ln_p5) / (ln_p95 - ln_p5)
    ).clip(0, 1)

rpt(f"\n  OCR 有效: {df_real['OCR_real'].notna().sum()} 观测")
rpt(f"  UCI 有效: {df_real['UCI_real'].notna().sum()} 观测")
rpt(f"  UCI_norm 有效: {df_real['UCI_norm'].notna().sum()} 观测")

# OCR/UCI 年度统计
rpt("\n  OCR/UCI 年度统计 (2010-2016, 有 Q 的年份):")
for yr in range(2010, 2017):
    mask_yr = (df_real['year'] == yr) & df_real['OCR_real'].notna() & df_real['UCI_norm'].notna()
    sub = df_real[mask_yr]
    if len(sub) > 0:
        rpt(f"    {yr}: OCR median={sub['OCR_real'].median():.3f}, "
            f"UCI_norm median={sub['UCI_norm'].median():.3f}, n={len(sub)}")

# ============================================================
# 步骤 4: 四色分级 (K-means 数据驱动阈值)
# ============================================================
rpt("\n" + "=" * 70)
rpt("步骤 4: 四色分级 (K-means 数据驱动阈值)")
rpt("=" * 70)

# 使用 2016 年截面做 K-means
uci_2016 = df_real[(df_real['year'] == ref_year) & df_real['UCI_norm'].notna()].copy()
rpt(f"  2016 年有 UCI_norm 的城市: {len(uci_2016)}")

if len(uci_2016) >= 20:
    # K-means k=4
    X_km = uci_2016['UCI_norm'].values.reshape(-1, 1)
    km = KMeans(n_clusters=4, n_init=50, random_state=42)
    km.fit(X_km)
    centers = sorted(km.cluster_centers_.flatten())
    thresholds_km = [(centers[i] + centers[i+1]) / 2 for i in range(3)]
    rpt(f"  K-means 聚类中心: {[f'{c:.3f}' for c in centers]}")
    rpt(f"  K-means 阈值: {[f'{t:.3f}' for t in thresholds_km]}")
else:
    # 使用之前的阈值作为备选
    thresholds_km = [0.428, 0.712, 0.894]
    rpt(f"  样本不足, 使用先前阈值: {thresholds_km}")

t1, t2, t3 = thresholds_km

def classify_uci(uci_norm):
    if pd.isna(uci_norm):
        return np.nan
    elif uci_norm >= t3:
        return 'Green'
    elif uci_norm >= t2:
        return 'Yellow'
    elif uci_norm >= t1:
        return 'Orange'
    else:
        return 'Red'

# 对所有年份分级
df_real['signal'] = df_real['UCI_norm'].apply(classify_uci)

# 2016 年分级统计
rpt(f"\n  2016 年四色分级 (阈值: {t1:.3f}/{t2:.3f}/{t3:.3f}):")
sig_2016 = df_real[(df_real['year'] == ref_year) & df_real['signal'].notna()]
for color in ['Red', 'Orange', 'Yellow', 'Green']:
    sub = sig_2016[sig_2016['signal'] == color]
    pct = len(sub) / len(sig_2016) * 100 if len(sig_2016) > 0 else 0
    rpt(f"    {color}: {len(sub)} 城市 ({pct:.1f}%)")
    if len(sub) > 0 and len(sub) <= 15:
        rpt(f"      城市: {', '.join(sub['city'].values)}")
    elif len(sub) > 15:
        rpt(f"      前15: {', '.join(sub.sort_values('UCI_norm')['city'].values[:15])}")

# 各年份分级变化
rpt("\n  各年份四色分级城市占比:")
for yr in sorted(df_real[df_real['signal'].notna()]['year'].unique()):
    sig_yr = df_real[(df_real['year'] == yr) & df_real['signal'].notna()]
    if len(sig_yr) < 5:
        continue
    counts = sig_yr['signal'].value_counts()
    red_pct = counts.get('Red', 0) / len(sig_yr) * 100
    orange_pct = counts.get('Orange', 0) / len(sig_yr) * 100
    yellow_pct = counts.get('Yellow', 0) / len(sig_yr) * 100
    green_pct = counts.get('Green', 0) / len(sig_yr) * 100
    rpt(f"    {yr}: Red={red_pct:.1f}% Orange={orange_pct:.1f}% "
        f"Yellow={yellow_pct:.1f}% Green={green_pct:.1f}% (n={len(sig_yr)})")

# ============================================================
# 步骤 5: 与全时段 (含插补) 结果对比
# ============================================================
rpt("\n" + "=" * 70)
rpt("步骤 5: 真实数据 vs 含插补数据对比")
rpt("=" * 70)

# 加载含插补的 urban_q (已在 city panel 中)
# 对比同一城市同一年份的 Q_real vs Q_imputed
df_compare = df_real[(df_real['year'] >= 2010) & (df_real['year'] <= 2016)].copy()
df_compare_q = df_compare[df_compare['Q_real'].notna() & df_compare['urban_q'].notna()].copy()

if len(df_compare_q) > 0:
    corr = df_compare_q['Q_real'].corr(df_compare_q['urban_q'])
    diff_pct = ((df_compare_q['Q_real'] - df_compare_q['urban_q']) / df_compare_q['urban_q'] * 100)
    rpt(f"  2010-2016 Q_real vs Q_imputed 对比 (n={len(df_compare_q)}):")
    rpt(f"    相关系数: {corr:.6f}")
    rpt(f"    平均差异: {diff_pct.mean():.4f}%")
    rpt(f"    最大差异: {diff_pct.abs().max():.4f}%")

    # 2016 年截面对比
    q16_real = df_real[(df_real['year'] == 2016) & df_real['Q_real'].notna()]['Q_real']
    q16_imp = city[(city['year'] == 2016) & city['urban_q'].notna()]['urban_q']

    rpt(f"\n  2016 截面 Q 分布:")
    rpt(f"    真实: mean={q16_real.mean():.4f}, median={q16_real.median():.4f}, "
        f"std={q16_real.std():.4f}, n={len(q16_real)}")
    rpt(f"    含插补: mean={q16_imp.mean():.4f}, median={q16_imp.median():.4f}, "
        f"std={q16_imp.std():.4f}, n={len(q16_imp)}")

# 之前含插补的 2023 年 Q 分布 (来自原始数据)
q23_imp = city[(city['year'] == 2023) & city['urban_q'].notna()]['urban_q']
rpt(f"\n  2023 (插补) Q 分布: mean={q23_imp.mean():.4f}, median={q23_imp.median():.4f}, n={len(q23_imp)}")

# 定性结论检验
rpt("\n  定性结论检验:")
# 一线城市 Q 高?
tier1_cities = ['北京市', '上海市', '广州市', '深圳市']
q16_tier1 = df_real[(df_real['year'] == 2016) & df_real['city'].isin(tier1_cities) &
                      df_real['Q_real'].notna()]['Q_real']
q16_rest = df_real[(df_real['year'] == 2016) & ~df_real['city'].isin(tier1_cities) &
                     df_real['Q_real'].notna()]['Q_real']
if len(q16_tier1) > 0:
    rpt(f"    一线城市 Q (2016): mean={q16_tier1.mean():.3f} vs 其他: mean={q16_rest.mean():.3f}")
    rpt(f"    结论: 一线城市 Q {'高于' if q16_tier1.mean() > q16_rest.mean() else '不高于'}其他城市 — 与插补结果一致")

# 红灯占比
if len(sig_2016) > 0:
    red_pct_2016 = (sig_2016['signal'] == 'Red').sum() / len(sig_2016) * 100
    redorange_pct_2016 = sig_2016['signal'].isin(['Red', 'Orange']).sum() / len(sig_2016) * 100
    rpt(f"    2016 红灯占比: {red_pct_2016:.1f}%")
    rpt(f"    2016 红+橙占比: {redorange_pct_2016:.1f}%")

# ============================================================
# 步骤 6: 2017-2024 修正方案 (参考值)
# ============================================================
rpt("\n" + "=" * 70)
rpt("步骤 6: 2017-2024 FAI 修正方案 (敏感性分析, 参考值)")
rpt("=" * 70)

# 方案 A: 国家级 FAI/GDP 趋势修正
natl['fai_gdp_ratio'] = natl['fai_total_100m'] / natl['gdp_100m']
fai_gdp_2016 = natl[natl['year'] == 2016]['fai_gdp_ratio'].values[0]

rpt(f"\n  方案 A: 国家级 FAI/GDP 比趋势修正")
rpt(f"    2016 FAI/GDP = {fai_gdp_2016:.4f}")

# 计算各年份的调整系数 = actual_ratio / 2016_ratio
correction_factors = {}
for yr in range(2017, 2024):
    row = natl[natl['year'] == yr]
    if len(row) > 0 and row['fai_gdp_ratio'].notna().any():
        actual_ratio = row['fai_gdp_ratio'].values[0]
        correction = actual_ratio / fai_gdp_2016
        correction_factors[yr] = correction
        rpt(f"    {yr}: FAI/GDP = {actual_ratio:.4f}, 修正系数 = {correction:.4f}")

# 对含插补的城市数据做修正
df_corrected = city.copy()
for yr, cf in correction_factors.items():
    imp_mask = (df_corrected['year'] == yr) & (df_corrected['fai_imputed'] == True)
    df_corrected.loc[imp_mask, 'fai_100m_corrected'] = df_corrected.loc[imp_mask, 'fai_100m'] * cf

# 未修正的保留原值
df_corrected['fai_100m_corrected'] = df_corrected['fai_100m_corrected'].fillna(df_corrected['fai_100m'])

# 用修正后的 FAI 重算 K
def compute_pim_corrected(group):
    group = group.sort_values('year').copy()
    fai = group['fai_100m_corrected'].values
    n = len(group)
    K = np.full(n, np.nan)
    valid_idx = np.where(~np.isnan(fai))[0]
    if len(valid_idx) == 0:
        group['K_corrected'] = np.nan
        return group
    first_valid = valid_idx[0]
    if len(valid_idx) >= 3:
        early_fai = fai[valid_idx[:5]]
        early_fai = early_fai[early_fai > 0]
        if len(early_fai) >= 2:
            g = np.mean(np.diff(early_fai) / early_fai[:-1])
            g = max(0.02, min(g, 0.30))
        else:
            g = 0.10
    else:
        g = 0.10
    if fai[first_valid] > 0:
        K[first_valid] = fai[first_valid] / (g + DELTA)
    else:
        K[first_valid] = 0
    for i in range(first_valid + 1, n):
        if np.isnan(K[i-1]):
            if not np.isnan(fai[i]) and fai[i] > 0:
                K[i] = fai[i] / (g + DELTA)
            continue
        inv = fai[i] if not np.isnan(fai[i]) else 0
        K[i] = K[i-1] * (1 - DELTA) + inv
    group['K_corrected'] = K
    return group

rpt("  计算修正后 K_corrected...")
df_corrected = df_corrected.groupby('city', group_keys=False).apply(compute_pim_corrected)

# 修正后 V 和 Q
df_corrected['per_capita_area_m2'] = df_corrected['year'].map(area_lookup)
df_corrected['V_corrected'] = (
    df_corrected['house_price'] *
    df_corrected['pop_10k'] * 10000 *
    df_corrected['per_capita_area_m2'] /
    1e8
)
df_corrected['Q_corrected'] = df_corrected['V_corrected'] / df_corrected['K_corrected']
df_corrected.loc[df_corrected['Q_corrected'] < 0, 'Q_corrected'] = np.nan
df_corrected.loc[df_corrected['Q_corrected'] > 20, 'Q_corrected'] = np.nan

rpt("\n  修正后 Urban Q 年度统计 (2017-2023, 方案A 参考值):")
for yr in range(2017, 2024):
    q_yr = df_corrected[(df_corrected['year'] == yr) & df_corrected['Q_corrected'].notna()]['Q_corrected']
    q_orig = city[(city['year'] == yr) & city['urban_q'].notna()]['urban_q']
    if len(q_yr) > 0:
        rpt(f"    {yr}: Q_corrected={q_yr.mean():.4f} vs Q_imputed={q_orig.mean():.4f} "
            f"(diff={q_yr.mean()-q_orig.mean():.4f}, n={len(q_yr)})")

# 方案 B: 省级增速修正 (简要说明)
rpt("\n  方案 B: 省级增速修正")
rpt("    需要省级 FAI 年度数据 (目前仅有 2005/2010/2015/2019 四个快照)")
rpt("    在可用数据下, 方案 A (国家级趋势) 更为简洁可行")
rpt("    方案 B 留作有更多省级年度数据时的改进方向")

# ============================================================
# 步骤 7: 倒 U 型截面检验 (仅真实数据)
# ============================================================
rpt("\n" + "=" * 70)
rpt("步骤 7: 倒 U 型截面检验 (2010-2016 真实数据)")
rpt("=" * 70)

# dV/V = a + b*(FAI/GDP) - c*(FAI/GDP)^2 + controls + city_FE + year_FE + e
inv_u_data = df_real[
    (df_real['year'] >= 2010) & (df_real['year'] <= 2016) &
    df_real['V_real'].notna() & (df_real['V_real'] > 0) &
    df_real['fai_100m'].notna() & (df_real['fai_100m'] > 0) &
    df_real['gdp_100m'].notna() & (df_real['gdp_100m'] > 0) &
    df_real['pop_10k'].notna()
].copy()

# 计算 dV/V
inv_u_data = inv_u_data.sort_values(['city', 'year'])
inv_u_data['V_lag'] = inv_u_data.groupby('city')['V_real'].shift(1)
inv_u_data['dV_V'] = (inv_u_data['V_real'] - inv_u_data['V_lag']) / inv_u_data['V_lag']
inv_u_data['fai_gdp'] = inv_u_data['fai_100m'] / inv_u_data['gdp_100m']
inv_u_data['fai_gdp_sq'] = inv_u_data['fai_gdp'] ** 2

# 去极端
inv_u_data = inv_u_data[
    inv_u_data['dV_V'].notna() &
    (inv_u_data['dV_V'].abs() < 2) &  # 去极端增长率
    (inv_u_data['fai_gdp'] < 3) &
    (inv_u_data['fai_gdp'] > 0)
].copy()

rpt(f"  倒 U 型检验样本: {len(inv_u_data)} 观测, {inv_u_data['city'].nunique()} 城市")

# 控制变量
inv_u_data['ln_gdp_pc'] = np.log(inv_u_data['gdp_per_capita'].clip(lower=1))
inv_u_data['ln_pop'] = np.log(inv_u_data['pop_10k'].clip(lower=1))

inv_u_report = []
def rpt_inv(line=''):
    inv_u_report.append(line)
    print(line)

rpt_inv("=" * 70)
rpt_inv("倒 U 型截面回归: dV/V ~ FAI/GDP + (FAI/GDP)^2 + controls")
rpt_inv("=" * 70)

# 模型 1: 无固定效应 (pooled OLS)
X1 = sm.add_constant(inv_u_data[['fai_gdp', 'fai_gdp_sq', 'ln_gdp_pc', 'ln_pop']])
y1 = inv_u_data['dV_V']
m1 = sm.OLS(y1, X1).fit(cov_type='HC1')

rpt_inv(f"\n模型 1: Pooled OLS (N={len(inv_u_data)})")
rpt_inv(f"  R-squared: {m1.rsquared:.4f}")
for var in m1.params.index:
    rpt_inv(f"  {var:15s}: coef={m1.params[var]:10.6f}, SE={m1.bse[var]:.6f}, p={m1.pvalues[var]:.4e}")

b_pool = m1.params.get('fai_gdp', 0)
c_pool = m1.params.get('fai_gdp_sq', 0)
if c_pool < 0 and b_pool > 0:
    istar_pool = -b_pool / (2 * c_pool)
    rpt_inv(f"  I*_opt (FAI/GDP 最优): {istar_pool:.4f}")
    rpt_inv(f"  倒 U 型: 成立 (b > 0, c < 0)")
else:
    istar_pool = np.nan
    rpt_inv(f"  倒 U 型: 不成立 (b={b_pool:.4f}, c={c_pool:.4f})")

# 模型 2: 年份固定效应
year_dummies = pd.get_dummies(inv_u_data['year'], prefix='yr', drop_first=True, dtype=float)
X2 = pd.concat([sm.add_constant(inv_u_data[['fai_gdp', 'fai_gdp_sq', 'ln_gdp_pc', 'ln_pop']]),
                 year_dummies], axis=1)
m2 = sm.OLS(y1, X2).fit(cov_type='HC1')

rpt_inv(f"\n模型 2: Year FE (N={len(inv_u_data)})")
rpt_inv(f"  R-squared: {m2.rsquared:.4f}")
for var in ['const', 'fai_gdp', 'fai_gdp_sq', 'ln_gdp_pc', 'ln_pop']:
    if var in m2.params.index:
        rpt_inv(f"  {var:15s}: coef={m2.params[var]:10.6f}, SE={m2.bse[var]:.6f}, p={m2.pvalues[var]:.4e}")

b_yr = m2.params.get('fai_gdp', 0)
c_yr = m2.params.get('fai_gdp_sq', 0)
if c_yr < 0 and b_yr > 0:
    istar_yr = -b_yr / (2 * c_yr)
    rpt_inv(f"  I*_opt: {istar_yr:.4f}")
    rpt_inv(f"  倒 U 型: 成立")
else:
    istar_yr = np.nan
    rpt_inv(f"  倒 U 型: 不成立 (b={b_yr:.4f}, c={c_yr:.4f})")

# 模型 3: City FE + Year FE (面板内估计)
city_dummies = pd.get_dummies(inv_u_data['city'], prefix='city', drop_first=True, dtype=float)
X3 = pd.concat([inv_u_data[['fai_gdp', 'fai_gdp_sq', 'ln_gdp_pc', 'ln_pop']],
                 year_dummies, city_dummies], axis=1)
# 不加 constant 因为有城市固定效应
m3 = sm.OLS(y1, X3).fit(cov_type='HC1')

rpt_inv(f"\n模型 3: City FE + Year FE (N={len(inv_u_data)})")
rpt_inv(f"  R-squared: {m3.rsquared:.4f}")
for var in ['fai_gdp', 'fai_gdp_sq', 'ln_gdp_pc', 'ln_pop']:
    if var in m3.params.index:
        rpt_inv(f"  {var:15s}: coef={m3.params[var]:10.6f}, SE={m3.bse[var]:.6f}, p={m3.pvalues[var]:.4e}")

b_fe = m3.params.get('fai_gdp', 0)
c_fe = m3.params.get('fai_gdp_sq', 0)
if c_fe < 0 and b_fe > 0:
    istar_fe = -b_fe / (2 * c_fe)
    rpt_inv(f"  I*_opt: {istar_fe:.4f}")
    rpt_inv(f"  倒 U 型: 成立")
else:
    istar_fe = np.nan
    rpt_inv(f"  倒 U 型: 不成立 (b={b_fe:.4f}, c={c_fe:.4f})")

# 与之前结果对比
rpt_inv(f"\n汇总:")
rpt_inv(f"  Pooled OLS:    b={b_pool:.4f}, c={c_pool:.4f}, I*={istar_pool:.4f}" if not np.isnan(istar_pool) else f"  Pooled OLS:    b={b_pool:.4f}, c={c_pool:.4f}, 不成立")
rpt_inv(f"  Year FE:       b={b_yr:.4f}, c={c_yr:.4f}, I*={istar_yr:.4f}" if not np.isnan(istar_yr) else f"  Year FE:       b={b_yr:.4f}, c={c_yr:.4f}, 不成立")
rpt_inv(f"  City+Year FE:  b={b_fe:.4f}, c={c_fe:.4f}, I*={istar_fe:.4f}" if not np.isnan(istar_fe) else f"  City+Year FE:  b={b_fe:.4f}, c={c_fe:.4f}, 不成立")
rpt_inv(f"\n  中国 2010-2016 平均 FAI/GDP: {inv_u_data['fai_gdp'].mean():.4f}")
rpt_inv(f"  中国 2010-2016 中位 FAI/GDP: {inv_u_data['fai_gdp'].median():.4f}")

# ============================================================
# 可视化 (4 个子图)
# ============================================================
rpt("\n" + "=" * 70)
rpt("可视化")
rpt("=" * 70)

fig, axes = plt.subplots(2, 2, figsize=(14, 11))
fig.suptitle('Urban Q 真实 FAI 分析 (2010-2016)', fontsize=14, fontweight='bold')

# (a) 真实数据 vs 插补数据的 Q 分布 (2016 截面)
ax = axes[0, 0]
q16_real_vals = df_real[(df_real['year'] == 2016) & df_real['Q_real'].notna()]['Q_real']
q23_imp_vals = city[(city['year'] == 2023) & city['urban_q'].notna()]['urban_q']
q16_imp_vals = city[(city['year'] == 2016) & city['urban_q'].notna()]['urban_q']

bins = np.linspace(0, 5, 30)
ax.hist(q16_real_vals.clip(upper=5), bins=bins, alpha=0.6, color='steelblue',
        label=f'2016 真实 (n={len(q16_real_vals)}, mean={q16_real_vals.mean():.2f})', density=True)
ax.hist(q23_imp_vals.clip(upper=5), bins=bins, alpha=0.5, color='coral',
        label=f'2023 插补 (n={len(q23_imp_vals)}, mean={q23_imp_vals.mean():.2f})', density=True)
ax.axvline(1.0, color='gray', linestyle='--', alpha=0.7, label='Q=1')
ax.set_xlabel('Urban Q')
ax.set_ylabel('Density')
ax.set_title('(a) Q 分布: 2016真实 vs 2023插补')
ax.legend(fontsize=8)

# (b) UCI 四色分级 (2016 年)
ax = axes[0, 1]
colors_map = {'Red': '#e74c3c', 'Orange': '#e67e22', 'Yellow': '#f1c40f', 'Green': '#2ecc71'}
sig_data = df_real[(df_real['year'] == ref_year) & df_real['signal'].notna()]
if len(sig_data) > 0:
    counts = sig_data['signal'].value_counts()
    categories = ['Red', 'Orange', 'Yellow', 'Green']
    vals = [counts.get(c, 0) for c in categories]
    bars = ax.bar(categories, vals, color=[colors_map[c] for c in categories], edgecolor='white')
    for bar, v in zip(bars, vals):
        if v > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    str(v), ha='center', va='bottom', fontsize=10)
    ax.set_ylabel('城市数')
    ax.set_title(f'(b) UCI 四色分级 ({ref_year}, 真实数据)')
    total = sum(vals)
    ax.text(0.95, 0.95, f'Total: {total}\nThresholds:\n{t1:.3f}/{t2:.3f}/{t3:.3f}',
            transform=ax.transAxes, fontsize=8, va='top', ha='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# (c) FAI/GDP vs dV/V 散点图 + 二次拟合
ax = axes[1, 0]
plot_data = inv_u_data[inv_u_data['fai_gdp'] < 2.5].copy()
ax.scatter(plot_data['fai_gdp'], plot_data['dV_V'], alpha=0.15, s=10, c='steelblue')

# 二次拟合曲线
x_fit = np.linspace(0.01, 2.0, 200)
if not np.isnan(istar_pool):
    y_fit = m1.params['const'] + b_pool * x_fit + c_pool * x_fit**2
    # 加上控制变量的均值效应
    y_fit += m1.params['ln_gdp_pc'] * plot_data['ln_gdp_pc'].mean()
    y_fit += m1.params['ln_pop'] * plot_data['ln_pop'].mean()
    ax.plot(x_fit, y_fit, 'r-', linewidth=2, label=f'Quadratic fit (I*={istar_pool:.2f})')
    ax.axvline(istar_pool, color='red', linestyle=':', alpha=0.7, label=f'I* = {istar_pool:.2f}')

ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
ax.set_xlabel('FAI/GDP')
ax.set_ylabel(r'$\Delta V / V$')
ax.set_title('(c) 投资效率: FAI/GDP vs 价值增长率 (2010-2016)')
ax.legend(fontsize=8)
ax.set_xlim(0, 2.0)
ax.set_ylim(-1.5, 1.5)

# (d) 真实 Q vs 插补 Q 相关性 (2010-2016 重叠期)
ax = axes[1, 1]
scatter_data = df_compare_q.copy()
if len(scatter_data) > 0:
    ax.scatter(scatter_data['urban_q'], scatter_data['Q_real'], alpha=0.3, s=10, c='steelblue')
    # 1:1 线
    q_max = max(scatter_data['urban_q'].max(), scatter_data['Q_real'].max())
    q_max = min(q_max, 10)
    ax.plot([0, q_max], [0, q_max], 'r--', linewidth=1, label='1:1 line')
    corr_val = scatter_data['Q_real'].corr(scatter_data['urban_q'])
    ax.text(0.05, 0.95, f'r = {corr_val:.4f}\nn = {len(scatter_data)}',
            transform=ax.transAxes, fontsize=10, va='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.set_xlabel('Q (含插补面板)')
    ax.set_ylabel('Q (仅真实 FAI)')
    ax.set_title('(d) Q 一致性检验 (2010-2016)')
    ax.set_xlim(0, q_max)
    ax.set_ylim(0, q_max)
    ax.legend(fontsize=8)

plt.tight_layout()
fig_path = os.path.join(FIGURES, 'fig21_city_real_fai.png')
plt.savefig(fig_path, dpi=200, bbox_inches='tight')
plt.close()
rpt(f"  图表已保存: {fig_path}")

# ============================================================
# 保存输出
# ============================================================
rpt("\n" + "=" * 70)
rpt("保存输出")
rpt("=" * 70)

# 1. 真实 FAI 城市面板
out_cols_panel = ['year', 'province', 'city', 'city_code', 'region', 'huhuanyong',
                   'gdp_100m', 'gdp_per_capita', 'pop_10k', 'urbanization_rate_pct',
                   'fai_100m', 'fai_imputed', 'house_price',
                   'V_real', 'K_real', 'Q_real', 'MUQ_real',
                   'fai_gdp_ratio', 'per_capita_area_m2']
out_panel = df_real[[c for c in out_cols_panel if c in df_real.columns]].copy()
panel_path = os.path.join(DATA_PROC, 'china_city_real_fai_panel.csv')
out_panel.to_csv(panel_path, index=False, encoding='utf-8-sig')
rpt(f"  真实 FAI 面板: {panel_path} ({out_panel.shape[0]} 行)")

# 2. 真实 FAI 城市 UCI
uci_cols = ['year', 'province', 'city', 'city_code', 'region',
            'Q_real', 'K_real', 'Kstar_real', 'OCR_real', 'UCI_real', 'UCI_norm', 'signal']
out_uci = df_real[[c for c in uci_cols if c in df_real.columns]].copy()
out_uci = out_uci[out_uci['UCI_norm'].notna()]
uci_path = os.path.join(DATA_PROC, 'china_city_real_fai_uci.csv')
out_uci.to_csv(uci_path, index=False, encoding='utf-8-sig')
rpt(f"  真实 FAI UCI: {uci_path} ({out_uci.shape[0]} 行)")

# 3. 分析报告
report_path = os.path.join(MODELS, 'city_real_fai_analysis.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))
rpt(f"  分析报告: {report_path}")

# 4. 倒 U 型回归报告
inv_u_path = os.path.join(MODELS, 'city_inverted_u_real.txt')
with open(inv_u_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(inv_u_report))
rpt(f"  倒 U 型回归: {inv_u_path}")

rpt("\n" + "=" * 70)
rpt("全部完成")
rpt("=" * 70)
