"""
n30_unified_panel.py
====================
目的: 构建覆盖 8 国、1573 个区域单元的统一 GDP-based MUQ 面板，
      并进行跨国 Simpson's Paradox 检验和 Aggregation Trap 验证。

输入:
  - 02-data/processed/china_city_panel_real.csv (中国 275 城)
  - 02-data/processed/china_provincial_muq.csv (中国 31 省)
  - 02-data/raw/japan_prefectural_panel.csv (日本 47 县)
  - 02-data/raw/korea_regional_panel.csv (韩国 17 市道)
  - 02-data/processed/us_msa_muq_panel.csv (美国 921 MSA)
  - 02-data/raw/europe_regional_panel.csv (欧洲 265 NUTS-2)
  - 02-data/raw/oceania_regional_panel.csv (澳大利亚 8 州)
  - 02-data/raw/africa_regional_panel.csv (南非 9 省)

输出:
  - 02-data/processed/unified_regional_panel.csv
  - 03-analysis/models/unified_panel_report.txt

依赖: pandas, numpy, scipy, statsmodels
"""

import os
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import spearmanr
import statsmodels.api as sm
import warnings

# ============================================================================
# 路径配置
# ============================================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
DATA_RAW = os.path.join(BASE, '02-data/raw')
DATA_PROC = os.path.join(BASE, '02-data/processed')
OUT_DATA = os.path.join(DATA_PROC, 'unified_regional_panel.csv')
OUT_REPORT = os.path.join(BASE, '03-analysis/models/unified_panel_report.txt')
SOURCE_DIR = os.path.join(BASE, '04-figures/source_data')
os.makedirs(SOURCE_DIR, exist_ok=True)

SEED = 20260322
np.random.seed(SEED)

# 报告缓冲
report_lines = []
def rpt(s=''):
    report_lines.append(s)
    print(s)

rpt('=' * 78)
rpt('UNIFIED REGIONAL PANEL: 8-Country GDP-based MUQ')
rpt(f'Date: 2026-03-22')
rpt(f'Random seed: {SEED}')
rpt('=' * 78)

# ============================================================================
# PART 1: 读取并标准化各国数据
# ============================================================================
rpt('\n' + '=' * 78)
rpt('PART 1: DATA HARMONIZATION')
rpt('=' * 78)

frames = []

# --- 1a. 中国 275 城 ---
rpt('\n--- 1a. China (275 cities) ---')
cn_city = pd.read_csv(os.path.join(DATA_PROC, 'china_city_panel_real.csv'))
# gdp_100m (亿元), fai_100m (亿元) 作为 GFCF 代理
# 计算 delta_gdp 和 GDP-based MUQ
cn_city = cn_city.sort_values(['city_code', 'year'])
cn_city['gdp'] = cn_city['gdp_100m'] * 1e8  # 转为元
cn_city['gfcf'] = cn_city['fai_100m'] * 1e8  # FAI 作为 GFCF 代理
cn_city['delta_gdp'] = cn_city.groupby('city_code')['gdp'].diff()
cn_city['muq_gdp'] = cn_city['delta_gdp'] / cn_city['gfcf']
cn_city['population'] = cn_city['pop_10k'] * 1e4  # 转为人
cn_city['gdp_per_capita'] = cn_city['gdp'] / cn_city['population']

# 提取统一变量
cn_std = pd.DataFrame({
    'region_id': cn_city['city_code'].astype(str),
    'region_name': cn_city['city'],
    'country': 'China',
    'country_iso3': 'CHN',
    'continent': 'Asia',
    'income_group': 'Upper-Middle',
    'year': cn_city['year'],
    'gdp': cn_city['gdp'],
    'gfcf': cn_city['gfcf'],
    'delta_gdp': cn_city['delta_gdp'],
    'muq_gdp': cn_city['muq_gdp'],
    'population': cn_city['population'],
    'urbanization': cn_city['urbanization_rate_pct'],
    'gdp_per_capita': cn_city['gdp_per_capita'],
    'source_level': 'city',
})
frames.append(cn_std)
n_regions_cn = cn_city['city_code'].nunique()
rpt(f'  Loaded: {len(cn_std)} obs, {n_regions_cn} cities, '
    f'years {cn_city["year"].min()}-{cn_city["year"].max()}')

# --- 1b. 日本 47 县 ---
rpt('\n--- 1b. Japan (47 prefectures) ---')
jp = pd.read_csv(os.path.join(DATA_RAW, 'japan_prefectural_panel.csv'))
jp_std = pd.DataFrame({
    'region_id': 'JP-' + jp['pref_code'].astype(str).str.zfill(2),
    'region_name': jp['prefecture_en'],
    'country': 'Japan',
    'country_iso3': 'JPN',
    'continent': 'Asia',
    'income_group': 'High',
    'year': jp['year'],
    'gdp': jp['gdp_nominal_myen'] * 1e6,  # 百万日元 -> 日元
    'gfcf': jp['gfcf_nominal_myen'] * 1e6,
    'delta_gdp': jp['delta_gdp_myen'] * 1e6,
    'muq_gdp': jp['muq'],  # 已有: delta_gdp / gfcf
    'population': jp['population'],
    'urbanization': np.nan,
    'gdp_per_capita': jp['gdp_per_capita_myen'] * 1e6,
    'source_level': 'prefecture',
})
frames.append(jp_std)
rpt(f'  Loaded: {len(jp_std)} obs, {jp["pref_code"].nunique()} prefectures, '
    f'years {jp["year"].min()}-{jp["year"].max()}')

# --- 1c. 韩国 17 市道 ---
rpt('\n--- 1c. Korea (17 regions) ---')
kr = pd.read_csv(os.path.join(DATA_RAW, 'korea_regional_panel.csv'))
kr_std = pd.DataFrame({
    'region_id': 'KR-' + kr['sido_code'].astype(str).str.zfill(2),
    'region_name': kr['name_en'],
    'country': 'Korea',
    'country_iso3': 'KOR',
    'continent': 'Asia',
    'income_group': 'High',
    'year': kr['year'],
    'gdp': kr['grdp_bkrw'] * 1e9,  # 十亿韩元 -> 韩元
    'gfcf': kr['gfcf_bkrw'] * 1e9,
    'delta_gdp': kr['delta_grdp'] * 1e9,
    'muq_gdp': kr['muq'],  # 已有
    'population': kr['population_1000'] * 1e3,
    'urbanization': np.nan,
    'gdp_per_capita': kr['grdp_per_capita'],
    'source_level': 'province',
})
frames.append(kr_std)
rpt(f'  Loaded: {len(kr_std)} obs, {kr["sido_code"].nunique()} regions, '
    f'years {kr["year"].min()}-{kr["year"].max()}')

# --- 1d. 美国 921 MSA ---
rpt('\n--- 1d. United States (921 MSAs) ---')
us = pd.read_csv(os.path.join(DATA_PROC, 'us_msa_muq_panel.csv'))
# 美国 MSA 没有 GFCF，用住房投资近似: I_hu (新增住房价值)
# GDP-based MUQ: delta_GDP / I_hu (住房投资作为 GFCF 代理)
us = us.sort_values(['cbsa_code', 'year'])
us['delta_gdp_usd'] = us['gdp_millions'] * 1e6 - us['gdp_lag'] * 1e6
# 注意: 美国 MSA 没有真正的 GFCF，I_hu 是新增住房价值
# 我们用 invest_intensity * GDP 作为 GFCF 代理
# invest_intensity = I_hu / V_total_lag，不适合作 GFCF
# 替代方案: 用全国 GFCF/GDP 比率 * regional GDP 估算
# 美国全国 GFCF/GDP 约 21% (World Bank, 2010-2022 平均)
US_GFCF_GDP_RATIO = 0.21
us['gfcf_est'] = us['gdp_millions'] * 1e6 * US_GFCF_GDP_RATIO

us_std = pd.DataFrame({
    'region_id': 'US-' + us['cbsa_code'].astype(str),
    'region_name': us['msa_name'],
    'country': 'United States',
    'country_iso3': 'USA',
    'continent': 'North America',
    'income_group': 'High',
    'year': us['year'],
    'gdp': us['gdp_millions'] * 1e6,
    'gfcf': us['gfcf_est'],
    'delta_gdp': us['delta_gdp_usd'],
    'muq_gdp': us['delta_gdp_usd'] / us['gfcf_est'],
    'population': us['population'],
    'urbanization': np.nan,
    'gdp_per_capita': us['gdp_per_capita'],
    'source_level': 'msa',
})
frames.append(us_std)
rpt(f'  Loaded: {len(us_std)} obs, {us["cbsa_code"].nunique()} MSAs, '
    f'years {us["year"].min()}-{us["year"].max()}')
rpt(f'  Note: GFCF estimated as {US_GFCF_GDP_RATIO*100:.0f}% of GDP (US national average)')

# --- 1e. 欧洲 265 NUTS-2 ---
rpt('\n--- 1e. Europe (265 NUTS-2 regions) ---')
eu = pd.read_csv(os.path.join(DATA_RAW, 'europe_regional_panel.csv'))
eu_std = pd.DataFrame({
    'region_id': eu['geo'],
    'region_name': eu['geo'],  # NUTS code 作为名称
    'country': eu['country_name'],
    'country_iso3': eu['iso3'],
    'continent': 'Europe',
    'income_group': 'High',
    'year': eu['year'],
    'gdp': eu['gdp_meur'] * 1e6,  # 百万欧元 -> 欧元
    'gfcf': eu['gfcf_est_meur'] * 1e6,
    'delta_gdp': eu['delta_gdp'] * 1e6,
    'muq_gdp': eu['muq'],
    'population': eu['population'],
    'urbanization': np.nan,
    'gdp_per_capita': eu['gdp_per_capita'],
    'source_level': 'nuts2',
})
frames.append(eu_std)
rpt(f'  Loaded: {len(eu_std)} obs, {eu["geo"].nunique()} regions, '
    f'{eu["country_name"].nunique()} countries, '
    f'years {eu["year"].min()}-{eu["year"].max()}')

# --- 1f. 澳大利亚 8 州 ---
rpt('\n--- 1f. Australia (8 states/territories) ---')
au = pd.read_csv(os.path.join(DATA_RAW, 'oceania_regional_panel.csv'))
au_std = pd.DataFrame({
    'region_id': au['region_code'],
    'region_name': au['region_name'],
    'country': 'Australia',
    'country_iso3': 'AUS',
    'continent': 'Oceania',
    'income_group': 'High',
    'year': au['year'],
    'gdp': au['gdp_usd'],
    'gfcf': au['gfcf_est_usd'],
    'delta_gdp': au['delta_gdp'],
    'muq_gdp': au['muq'],
    'population': au['population'],
    'urbanization': np.nan,
    'gdp_per_capita': au['gdp_per_capita'],
    'source_level': 'state',
})
frames.append(au_std)
rpt(f'  Loaded: {len(au_std)} obs, {au["region_code"].nunique()} regions, '
    f'years {au["year"].min()}-{au["year"].max()}')

# --- 1g. 南非 9 省 ---
rpt('\n--- 1g. South Africa (9 provinces) ---')
za = pd.read_csv(os.path.join(DATA_RAW, 'africa_regional_panel.csv'))
za_std = pd.DataFrame({
    'region_id': za['region_code'],
    'region_name': za['region_name'],
    'country': 'South Africa',
    'country_iso3': 'ZAF',
    'continent': 'Africa',
    'income_group': 'Upper-Middle',
    'year': za['year'],
    'gdp': za['gdp_usd'],
    'gfcf': za['gfcf_est_usd'],
    'delta_gdp': za['delta_gdp'],
    'muq_gdp': za['muq'],
    'population': za['population'],
    'urbanization': za.get('urban_pct_national', np.nan),
    'gdp_per_capita': za['gdp_per_capita'],
    'source_level': 'province',
})
frames.append(za_std)
rpt(f'  Loaded: {len(za_std)} obs, {za["region_code"].nunique()} regions, '
    f'years {za["year"].min()}-{za["year"].max()}')

# ============================================================================
# PART 2: 合并与清洗
# ============================================================================
rpt('\n' + '=' * 78)
rpt('PART 2: MERGE AND CLEAN')
rpt('=' * 78)

panel = pd.concat(frames, ignore_index=True)
rpt(f'\nRaw merged panel: {len(panel)} obs')
rpt(f'Unique regions: {panel["region_id"].nunique()}')
rpt(f'Countries: {panel["country"].nunique()}')

# 计算统一的 GDP-based MUQ (对未预计算的重新计算)
# muq_gdp = delta_gdp / gfcf
mask_recalc = panel['muq_gdp'].isna() & panel['delta_gdp'].notna() & panel['gfcf'].notna()
panel.loc[mask_recalc & (panel['gfcf'] > 0), 'muq_gdp'] = (
    panel.loc[mask_recalc & (panel['gfcf'] > 0), 'delta_gdp'] /
    panel.loc[mask_recalc & (panel['gfcf'] > 0), 'gfcf']
)

# 添加 ln 变量
panel['ln_gdp'] = np.log(panel['gdp'].clip(lower=1))
panel['ln_pop'] = np.log(panel['population'].clip(lower=1))
panel['ln_gdp_pc'] = np.log(panel['gdp_per_capita'].clip(lower=1))

# Winsorise MUQ at 1%/99%
rpt('\nWinsorising MUQ at 1%/99% tails...')
muq_valid = panel['muq_gdp'].dropna()
q01 = muq_valid.quantile(0.01)
q99 = muq_valid.quantile(0.99)
rpt(f'  Before winsorise: min={muq_valid.min():.4f}, max={muq_valid.max():.4f}')
rpt(f'  Thresholds: q01={q01:.4f}, q99={q99:.4f}')
panel['muq_gdp_w'] = panel['muq_gdp'].clip(lower=q01, upper=q99)
muq_w_valid = panel['muq_gdp_w'].dropna()
rpt(f'  After winsorise: min={muq_w_valid.min():.4f}, max={muq_w_valid.max():.4f}')

# 添加 GDP per capita 四分位分组
panel['gdp_pc_quartile'] = pd.qcut(
    panel['gdp_per_capita'].dropna(), 4, labels=['Q1_Low', 'Q2', 'Q3', 'Q4_High']
).reindex(panel.index)

# 汇总统计
rpt('\n--- Panel Summary by Country ---')
summary = panel.groupby('country').agg(
    n_regions=('region_id', 'nunique'),
    n_obs=('muq_gdp_w', 'count'),
    year_min=('year', 'min'),
    year_max=('year', 'max'),
    muq_mean=('muq_gdp_w', 'mean'),
    muq_median=('muq_gdp_w', 'median'),
    muq_sd=('muq_gdp_w', 'std'),
).sort_values('n_regions', ascending=False)
rpt(summary.to_string())

total_regions = panel['region_id'].nunique()
rpt(f'\nTotal unique regions: {total_regions}')
rpt(f'Total obs with valid MUQ: {panel["muq_gdp_w"].notna().sum()}')

# 保存统一面板
panel.to_csv(OUT_DATA, index=False)
rpt(f'\nPanel saved to: {OUT_DATA}')

# ============================================================================
# PART 3: SIMPSON'S PARADOX ANALYSIS (Regional Level)
# ============================================================================
rpt('\n' + '=' * 78)
rpt('PART 3: SIMPSON\'S PARADOX -- CROSS-NATIONAL REGIONAL')
rpt('=' * 78)

df_sp = panel.dropna(subset=['muq_gdp_w', 'year']).copy()

# --- 3a. 按国家收入水平分组 ---
rpt('\n--- 3a. By Income Group ---')
for grp in df_sp['income_group'].dropna().unique():
    sub = df_sp[df_sp['income_group'] == grp]
    if len(sub) < 20:
        continue
    rho, p = spearmanr(sub['year'], sub['muq_gdp_w'])
    rpt(f'  {grp}: n={len(sub):,}, Spearman(year, MUQ) rho={rho:.4f}, p={p:.4f}')

# pooled
rho_pool, p_pool = spearmanr(df_sp['year'], df_sp['muq_gdp_w'])
rpt(f'  POOLED: n={len(df_sp):,}, Spearman(year, MUQ) rho={rho_pool:.4f}, p={p_pool:.4f}')

# --- 3b. 按 GDP per capita 四分位 ---
rpt('\n--- 3b. By GDP per capita Quartile ---')
for grp in ['Q1_Low', 'Q2', 'Q3', 'Q4_High']:
    sub = df_sp[df_sp['gdp_pc_quartile'] == grp]
    if len(sub) < 20:
        continue
    rho, p = spearmanr(sub['year'], sub['muq_gdp_w'])
    rpt(f'  {grp}: n={len(sub):,}, Spearman(year, MUQ) rho={rho:.4f}, p={p:.4f}')

rpt(f'  POOLED: rho={rho_pool:.4f}, p={p_pool:.4f} (same as above)')

# --- 3c. 按国家分别计算 ---
rpt('\n--- 3c. By Country ---')
country_rhos = {}
for ctry in sorted(df_sp['country'].unique()):
    sub = df_sp[df_sp['country'] == ctry]
    if len(sub) < 20:
        continue
    rho, p = spearmanr(sub['year'], sub['muq_gdp_w'])
    country_rhos[ctry] = (rho, p, len(sub))
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
    rpt(f'  {ctry:20s}: n={len(sub):>6,}, rho={rho:+.4f}, p={p:.4f} {sig}')

# Simpson 检验: 多数国家方向 vs pooled 方向
n_negative = sum(1 for r, p, n in country_rhos.values() if r < 0)
n_positive = sum(1 for r, p, n in country_rhos.values() if r > 0)
rpt(f'\n  Simpson Check: {n_negative} countries negative, {n_positive} positive')
rpt(f'  Pooled direction: {"positive" if rho_pool > 0 else "negative"} (rho={rho_pool:+.4f})')
if (rho_pool > 0 and n_negative > n_positive) or (rho_pool < 0 and n_positive > n_negative):
    rpt('  ==> SIMPSON\'S PARADOX DETECTED')
else:
    rpt('  ==> No clear Simpson\'s Paradox at regional level')

# --- 3d. MUQ ~ urbanization (for countries with urbanization data) ---
rpt('\n--- 3d. MUQ ~ Urbanization (where available) ---')
df_urb = df_sp.dropna(subset=['urbanization'])
if len(df_urb) > 50:
    for grp in df_urb['income_group'].dropna().unique():
        sub = df_urb[df_urb['income_group'] == grp]
        if len(sub) < 20:
            continue
        rho, p = spearmanr(sub['urbanization'], sub['muq_gdp_w'])
        rpt(f'  {grp}: n={len(sub):,}, Spearman(urb, MUQ) rho={rho:.4f}, p={p:.4f}')
    rho_u, p_u = spearmanr(df_urb['urbanization'], df_urb['muq_gdp_w'])
    rpt(f'  POOLED: n={len(df_urb):,}, rho={rho_u:.4f}, p={p_u:.4f}')
else:
    rpt('  Insufficient urbanization data at regional level.')

# ============================================================================
# PART 4: UNIFIED PANEL REGRESSIONS
# ============================================================================
rpt('\n' + '=' * 78)
rpt('PART 4: PANEL REGRESSIONS')
rpt('=' * 78)

df_reg = panel.dropna(subset=['muq_gdp_w', 'ln_gdp_pc']).copy()

# --- 4a. MUQ ~ ln(GDP_pc) + Country FE + Year FE ---
rpt('\n--- 4a. MUQ ~ ln(GDP_pc) + Country FE + Year FE ---')
# 创建虚拟变量
country_dummies = pd.get_dummies(df_reg['country'], prefix='c', drop_first=True)
year_dummies = pd.get_dummies(df_reg['year'], prefix='y', drop_first=True)

X_4a = pd.concat([df_reg[['ln_gdp_pc']], country_dummies, year_dummies], axis=1)
X_4a = sm.add_constant(X_4a)
y_4a = df_reg['muq_gdp_w']

# 只保留完整行
mask_4a = X_4a.notna().all(axis=1) & y_4a.notna()
X_4a = X_4a[mask_4a].astype(float)
y_4a = y_4a[mask_4a]

try:
    model_4a = sm.OLS(y_4a, X_4a).fit(cov_type='cluster',
                                        cov_kwds={'groups': df_reg.loc[mask_4a, 'region_id']})
    rpt(f'  N = {model_4a.nobs:.0f}, R2 = {model_4a.rsquared:.4f}, '
        f'Adj-R2 = {model_4a.rsquared_adj:.4f}')
    beta_gdp = model_4a.params['ln_gdp_pc']
    se_gdp = model_4a.bse['ln_gdp_pc']
    ci_gdp = model_4a.conf_int().loc['ln_gdp_pc']
    p_gdp = model_4a.pvalues['ln_gdp_pc']
    rpt(f'  ln(GDP_pc): beta = {beta_gdp:.4f}, SE = {se_gdp:.4f}')
    rpt(f'    95% CI: [{ci_gdp[0]:.4f}, {ci_gdp[1]:.4f}], p = {p_gdp:.6f}')
except Exception as e:
    rpt(f'  Regression failed: {e}')

# --- 4b. MUQ ~ urbanization + Country FE + Year FE (where available) ---
rpt('\n--- 4b. MUQ ~ urbanization + Country FE + Year FE ---')
df_reg_u = panel.dropna(subset=['muq_gdp_w', 'urbanization']).copy()
if len(df_reg_u) > 100:
    country_dummies_u = pd.get_dummies(df_reg_u['country'], prefix='c', drop_first=True)
    year_dummies_u = pd.get_dummies(df_reg_u['year'], prefix='y', drop_first=True)
    X_4b = pd.concat([df_reg_u[['urbanization']], country_dummies_u, year_dummies_u], axis=1)
    X_4b = sm.add_constant(X_4b)
    y_4b = df_reg_u['muq_gdp_w']
    mask_4b = X_4b.notna().all(axis=1) & y_4b.notna()
    X_4b = X_4b[mask_4b].astype(float)
    y_4b = y_4b[mask_4b]
    try:
        model_4b = sm.OLS(y_4b, X_4b).fit(cov_type='cluster',
                                            cov_kwds={'groups': df_reg_u.loc[mask_4b, 'region_id']})
        rpt(f'  N = {model_4b.nobs:.0f}, R2 = {model_4b.rsquared:.4f}')
        beta_urb = model_4b.params['urbanization']
        se_urb = model_4b.bse['urbanization']
        ci_urb = model_4b.conf_int().loc['urbanization']
        p_urb = model_4b.pvalues['urbanization']
        rpt(f'  urbanization: beta = {beta_urb:.6f}, SE = {se_urb:.6f}')
        rpt(f'    95% CI: [{ci_urb[0]:.6f}, {ci_urb[1]:.6f}], p = {p_urb:.6f}')
    except Exception as e:
        rpt(f'  Regression failed: {e}')
else:
    rpt(f'  Insufficient observations with urbanization data (n={len(df_reg_u)})')

# ============================================================================
# PART 5: GLOBAL SCALING LAW
# ============================================================================
rpt('\n' + '=' * 78)
rpt('PART 5: GLOBAL SCALING LAW  ln(GDP) ~ ln(Pop)')
rpt('=' * 78)

df_sc = panel.dropna(subset=['ln_gdp', 'ln_pop']).copy()
# 去掉无穷大
df_sc = df_sc[np.isfinite(df_sc['ln_gdp']) & np.isfinite(df_sc['ln_pop'])]

# 全样本
X_sc = sm.add_constant(df_sc['ln_pop'])
model_sc = sm.OLS(df_sc['ln_gdp'], X_sc).fit(cov_type='HC1')
rpt(f'\nGlobal: ln(GDP) = {model_sc.params["const"]:.3f} + '
    f'{model_sc.params["ln_pop"]:.4f} * ln(Pop)')
rpt(f'  beta = {model_sc.params["ln_pop"]:.4f}, '
    f'SE = {model_sc.bse["ln_pop"]:.4f}, '
    f'95% CI: [{model_sc.conf_int().loc["ln_pop"][0]:.4f}, '
    f'{model_sc.conf_int().loc["ln_pop"][1]:.4f}]')
rpt(f'  R2 = {model_sc.rsquared:.4f}, N = {model_sc.nobs:.0f}')

# 分洲报告
rpt('\n  By Continent:')
for cont in sorted(df_sc['continent'].unique()):
    sub = df_sc[df_sc['continent'] == cont]
    if len(sub) < 30:
        rpt(f'    {cont}: n={len(sub)}, too few for regression')
        continue
    X_c = sm.add_constant(sub['ln_pop'])
    try:
        m_c = sm.OLS(sub['ln_gdp'], X_c).fit(cov_type='HC1')
        ci_c = m_c.conf_int().loc['ln_pop']
        rpt(f'    {cont:15s}: beta={m_c.params["ln_pop"]:.4f} '
            f'[{ci_c[0]:.4f}, {ci_c[1]:.4f}], '
            f'R2={m_c.rsquared:.4f}, n={len(sub)}')
    except Exception as e:
        rpt(f'    {cont}: failed - {e}')

# 分国家
rpt('\n  By Country:')
for ctry in sorted(df_sc['country'].unique()):
    sub = df_sc[df_sc['country'] == ctry]
    if len(sub) < 30:
        continue
    X_c = sm.add_constant(sub['ln_pop'])
    try:
        m_c = sm.OLS(sub['ln_gdp'], X_c).fit(cov_type='HC1')
        ci_c = m_c.conf_int().loc['ln_pop']
        rpt(f'    {ctry:20s}: beta={m_c.params["ln_pop"]:.4f} '
            f'[{ci_c[0]:.4f}, {ci_c[1]:.4f}], '
            f'R2={m_c.rsquared:.4f}, n={len(sub)}')
    except Exception as e:
        pass

# ============================================================================
# PART 6: CROSS-COUNTRY MUQ TREND (weighted average)
# ============================================================================
rpt('\n' + '=' * 78)
rpt('PART 6: CROSS-COUNTRY MUQ TIME SERIES')
rpt('=' * 78)

# 各国加权平均 MUQ (GDP 加权)
df_ts = panel.dropna(subset=['muq_gdp_w', 'gdp']).copy()
df_ts = df_ts[df_ts['gdp'] > 0]

rpt('\n  Country-level GDP-weighted mean MUQ by year:')
trend_data = []
for ctry in sorted(df_ts['country'].unique()):
    sub = df_ts[df_ts['country'] == ctry]
    yearly = sub.groupby('year').apply(
        lambda g: np.average(g['muq_gdp_w'], weights=g['gdp'])
        if g['gdp'].sum() > 0 else np.nan
    ).reset_index()
    yearly.columns = ['year', 'muq_weighted']
    yearly['country'] = ctry
    trend_data.append(yearly)

trend_df = pd.concat(trend_data, ignore_index=True)
rpt('\n  Sample years per country:')
for ctry in sorted(trend_df['country'].unique()):
    sub = trend_df[trend_df['country'] == ctry].dropna()
    if len(sub) > 0:
        rpt(f'    {ctry:20s}: {sub["year"].min()}-{sub["year"].max()}, '
            f'mean MUQ={sub["muq_weighted"].mean():.4f}')

# 保存趋势数据
trend_path = os.path.join(SOURCE_DIR, 'unified_muq_trends.csv')
trend_df.to_csv(trend_path, index=False)
rpt(f'\n  Trend data saved: {trend_path}')

# ============================================================================
# PART 7: AGGREGATION TRAP CROSS-NATIONAL VERIFICATION (P5)
# ============================================================================
rpt('\n' + '=' * 78)
rpt('PART 7: AGGREGATION TRAP -- CROSS-NATIONAL VERIFICATION')
rpt('=' * 78)

rpt('''
Theorem conditions:
  A1: Within-group MUQ is declining over time
  A2: Systematic compositional shift (high-MUQ regions gain weight)
  A3: Between-group gap exceeds within-group decline

We test for countries with sufficient regional units:
  China (275 cities), Europe (265 regions), US (921 MSAs)
  Japan (47 prefs), Korea (17 regions), Australia (8), South Africa (9)
''')

def test_aggregation_trap(df_country, country_name, n_groups=4):
    """
    检验 Aggregation Trap 三个条件。
    将区域按 GDP per capita 分为 n_groups 组。
    """
    rpt(f'\n--- {country_name} ---')
    df = df_country.dropna(subset=['muq_gdp_w', 'gdp_per_capita', 'year']).copy()
    df = df[np.isfinite(df['muq_gdp_w']) & np.isfinite(df['gdp_per_capita'])]

    if len(df) < 50:
        rpt(f'  Insufficient data (n={len(df)}). Skipping.')
        return None

    n_regions = df['region_id'].nunique()
    rpt(f'  N obs = {len(df)}, N regions = {n_regions}')

    # 按年内 GDP per capita 分组 (动态分组)
    def assign_group(g):
        try:
            g['gdp_group'] = pd.qcut(g['gdp_per_capita'], n_groups, labels=False, duplicates='drop')
        except ValueError:
            g['gdp_group'] = pd.cut(g['gdp_per_capita'], n_groups, labels=False)
        return g

    df = df.groupby('year', group_keys=False).apply(assign_group)

    if 'gdp_group' not in df.columns or df['gdp_group'].isna().all():
        rpt('  Failed to create groups.')
        return None

    # === A1: 组内 MUQ 是否随时间递减? ===
    rpt('\n  A1: Within-group decline (MUQ ~ year within each group)')
    a1_pass = 0
    a1_total = 0
    group_alphas = {}
    group_betas = {}

    for g in sorted(df['gdp_group'].dropna().unique()):
        sub = df[df['gdp_group'] == g]
        if len(sub) < 20:
            continue
        a1_total += 1
        rho, p = spearmanr(sub['year'], sub['muq_gdp_w'])
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
        direction = 'DECLINE' if rho < 0 else 'INCREASE'
        if rho < 0:
            a1_pass += 1
        rpt(f'    Group {g}: n={len(sub):>5}, Spearman rho={rho:+.4f}, p={p:.4f} {sig} [{direction}]')

        # OLS for alpha, beta
        X_g = sm.add_constant(sub['year'] - sub['year'].min())
        try:
            m_g = sm.OLS(sub['muq_gdp_w'], X_g).fit()
            group_alphas[g] = m_g.params['const']
            group_betas[g] = m_g.params.iloc[1] if len(m_g.params) > 1 else 0
        except:
            pass

    a1_result = a1_pass == a1_total and a1_total > 0
    rpt(f'  A1 RESULT: {a1_pass}/{a1_total} groups declining. '
        f'{"PASS" if a1_result else "FAIL"}')

    # === A2: 组间跃迁 (高 MUQ 组权重增加) ===
    rpt('\n  A2: Compositional shift')
    # 计算各时期每组的 GDP 权重
    yearly_weights = df.groupby(['year', 'gdp_group']).agg(
        total_gdp=('gdp', 'sum'),
        mean_muq=('muq_gdp_w', 'mean')
    ).reset_index()
    yearly_total = df.groupby('year')['gdp'].sum().reset_index()
    yearly_total.columns = ['year', 'year_total_gdp']
    yearly_weights = yearly_weights.merge(yearly_total, on='year')
    yearly_weights['weight'] = yearly_weights['total_gdp'] / yearly_weights['year_total_gdp']

    # 检查高 GDP per capita 组是否随时间获得更多权重
    a2_pass_count = 0
    a2_total_count = 0
    for g in sorted(yearly_weights['gdp_group'].dropna().unique()):
        sub = yearly_weights[yearly_weights['gdp_group'] == g].sort_values('year')
        if len(sub) < 5:
            continue
        a2_total_count += 1
        rho, p = spearmanr(sub['year'], sub['weight'])
        direction = 'INCREASING' if rho > 0 else 'DECREASING'
        # 高组应增加,低组应减少
        expected_positive = (g >= n_groups / 2)
        if (expected_positive and rho > 0) or (not expected_positive and rho < 0):
            a2_pass_count += 1
        rpt(f'    Group {g}: weight trend rho={rho:+.4f}, p={p:.4f} [{direction}]')

    a2_result = a2_pass_count >= a2_total_count * 0.5
    rpt(f'  A2 RESULT: {a2_pass_count}/{a2_total_count} groups shift as expected. '
        f'{"PASS" if a2_result else "FAIL"}')

    # === A3: 组间差是否超过组内降? ===
    rpt('\n  A3: Between-group gap dominates within-group decline')
    # 计算 pooled vs within
    rho_pool, p_pool = spearmanr(df['year'], df['muq_gdp_w'])

    # 加权平均 within-group rho
    within_rhos = []
    within_weights = []
    for g in sorted(df['gdp_group'].dropna().unique()):
        sub = df[df['gdp_group'] == g]
        if len(sub) < 20:
            continue
        rho_g, _ = spearmanr(sub['year'], sub['muq_gdp_w'])
        within_rhos.append(rho_g)
        within_weights.append(len(sub))

    if within_rhos:
        weighted_within = np.average(within_rhos, weights=within_weights)
        between_component = rho_pool - weighted_within

        rpt(f'    Pooled rho:     {rho_pool:+.4f}')
        rpt(f'    Weighted within: {weighted_within:+.4f}')
        rpt(f'    Between component: {between_component:+.4f}')

        a3_result = abs(between_component) > abs(weighted_within)
        rpt(f'    |Between| ({abs(between_component):.4f}) '
            f'{">" if a3_result else "<="} '
            f'|Within| ({abs(weighted_within):.4f})')
        rpt(f'  A3 RESULT: {"PASS" if a3_result else "FAIL"}')

        # 是否存在 Simpson's Paradox?
        if weighted_within < 0 and rho_pool > 0:
            rpt(f'  ==> SIMPSON\'S PARADOX: within negative, pooled positive')
        elif weighted_within > 0 and rho_pool < 0:
            rpt(f'  ==> REVERSE SIMPSON\'S PARADOX: within positive, pooled negative')
        else:
            rpt(f'  ==> No sign reversal between within and pooled')
    else:
        a3_result = False
        rpt('  A3: Insufficient data for decomposition')

    # 总结
    all_pass = a1_result and a2_result and a3_result
    rpt(f'\n  VERDICT for {country_name}:')
    rpt(f'    A1 (within decline):      {"PASS" if a1_result else "FAIL"}')
    rpt(f'    A2 (compositional shift):  {"PASS" if a2_result else "FAIL"}')
    rpt(f'    A3 (between > within):    {"PASS" if a3_result else "FAIL"}')
    rpt(f'    ALL CONDITIONS:           {"SATISFIED" if all_pass else "NOT ALL SATISFIED"}')

    return {'A1': a1_result, 'A2': a2_result, 'A3': a3_result, 'all': all_pass}

# 对每个国家运行
results_trap = {}
for ctry in ['China', 'Japan', 'Korea', 'United States', 'Australia', 'South Africa']:
    df_c = panel[panel['country'] == ctry]
    n_g = 4 if df_c['region_id'].nunique() > 30 else 3 if df_c['region_id'].nunique() > 10 else 2
    result = test_aggregation_trap(df_c, ctry, n_groups=n_g)
    if result:
        results_trap[ctry] = result

# 欧洲整体 (265 区域视为一个"国家")
df_eu = panel[panel['continent'] == 'Europe']
result_eu = test_aggregation_trap(df_eu, 'Europe (265 NUTS-2)', n_groups=4)
if result_eu:
    results_trap['Europe'] = result_eu

# 汇总表
rpt('\n' + '=' * 78)
rpt('AGGREGATION TRAP SUMMARY')
rpt('=' * 78)
rpt(f'\n  {"Country":<25} {"A1":>6} {"A2":>6} {"A3":>6} {"All":>8}')
rpt(f'  {"-"*25} {"-"*6} {"-"*6} {"-"*6} {"-"*8}')
for ctry, res in results_trap.items():
    a1 = 'PASS' if res['A1'] else 'FAIL'
    a2 = 'PASS' if res['A2'] else 'FAIL'
    a3 = 'PASS' if res['A3'] else 'FAIL'
    allp = 'YES' if res['all'] else 'NO'
    rpt(f'  {ctry:<25} {a1:>6} {a2:>6} {a3:>6} {allp:>8}')

n_all_pass = sum(1 for r in results_trap.values() if r['all'])
rpt(f'\n  {n_all_pass}/{len(results_trap)} countries/regions satisfy all 3 conditions.')

# ============================================================================
# SAVE REPORT
# ============================================================================
with open(OUT_REPORT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
    f.write('\n')

rpt(f'\nReport saved to: {OUT_REPORT}')
rpt('Done.')
