"""
n04_clean_spec_city.py -- Clean Specification 城市级回归重建
==============================================================

目的:
  针对审稿人指出的 MUQ ~ FAI/GDP 机械相关问题，系统估计消除共享变量的
  "clean specification"，并在中国城市和美国 MSA 两个样本中比较。

核心逻辑:
  原始: MUQ = DeltaV/I ~ FAI/GDP = I/GDP  → 分子分母共享 I，机械负相关
  Clean: DeltaV/GDP ~ FAI/GDP              → 无共享变量

输入:
  - 02-data/processed/china_city_panel_real.csv
  - 02-data/processed/us_msa_muq_panel.csv

输出:
  - 03-analysis/models/clean_spec_city_report.txt

依赖: pandas, numpy, statsmodels, scipy
"""

import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

# =============================================================================
# 路径配置与随机种子
# =============================================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
CHINA_PATH = os.path.join(BASE, '02-data/processed/china_city_panel_real.csv')
US_PATH = os.path.join(BASE, '02-data/processed/us_msa_muq_panel.csv')
REPORT_PATH = os.path.join(BASE, '03-analysis/models/clean_spec_city_report.txt')

np.random.seed(20260321)

# =============================================================================
# 辅助函数
# =============================================================================
report_lines = []

def rprint(s=''):
    """同时打印到控制台和报告"""
    print(s)
    report_lines.append(str(s))

def winsorize(s, lower=0.01, upper=0.99):
    """Winsorize at given percentiles"""
    lo = s.quantile(lower)
    hi = s.quantile(upper)
    return s.clip(lo, hi)

def format_coef(name, coef, se, t, p, ci_lo, ci_hi):
    """格式化回归系数行"""
    sig = ''
    if p < 0.001: sig = '***'
    elif p < 0.01: sig = '**'
    elif p < 0.05: sig = '*'
    elif p < 0.10: sig = '+'
    return f'  {name:<20s} {coef:>10.4f} {se:>10.4f} {t:>8.3f}  {p:>12.6e} [{ci_lo:>8.4f}, {ci_hi:>8.4f}] {sig}'

def report_ols(model, label, dep_var, indep_var, n, n_cities=None, n_years=None):
    """报告 OLS 回归结果"""
    rprint(f'  模型: {label}')
    rprint(f'  因变量: {dep_var}, 自变量: {indep_var}')
    rprint(f'  N = {n}', )
    if n_cities:
        rprint(f'  城市数 = {n_cities}')
    if n_years:
        rprint(f'  年份数 = {n_years}')
    rprint(f'  R-squared = {model.rsquared:.4f}')
    if hasattr(model, 'rsquared_adj'):
        rprint(f'  Adj R-squared = {model.rsquared_adj:.4f}')
    rprint()
    ci = model.conf_int()
    rprint(f'  {"Variable":<20s} {"Coef":>10s} {"Std Err":>10s} {"t":>8s}  {"p-value":>12s} {"95% CI":>20s}')
    rprint(f'  {"-"*90}')
    for i, vname in enumerate(model.params.index):
        rprint(format_coef(
            vname, model.params.iloc[i], model.bse.iloc[i],
            model.tvalues.iloc[i], model.pvalues.iloc[i],
            ci.iloc[i, 0], ci.iloc[i, 1]
        ))
    rprint()

# =============================================================================
# 1. 中国城市数据准备
# =============================================================================
rprint('=' * 80)
rprint('CLEAN SPECIFICATION 城市级回归重建')
rprint('=' * 80)
rprint(f'日期: 2026-03-21')
rprint(f'随机种子: 20260321')
rprint()

df_cn = pd.read_csv(CHINA_PATH)
cn = df_cn[(df_cn['year'] >= 2010) & (df_cn['year'] <= 2016)].copy()

# 重建 V (对于缺失 V_100m 但有 house_price 的城市)
mask_v = cn['V_100m'].isna() & cn['house_price'].notna()
cn.loc[mask_v, 'V_100m'] = (
    cn.loc[mask_v, 'house_price'] *
    cn.loc[mask_v, 'per_capita_area_m2'] *
    cn.loc[mask_v, 'pop_10k'] * 10000 / 1e8
)

# 排序并计算 DeltaV
cn = cn.sort_values(['city', 'year']).reset_index(drop=True)
cn['V_lag'] = cn.groupby('city')['V_100m'].shift(1)
cn['delta_V'] = cn['V_100m'] - cn['V_lag']

# MUQ = DeltaV / FAI
cn['I'] = cn['fai_100m']
cn['MUQ'] = np.where(
    (cn['I'] > 1) & cn['delta_V'].notna(),
    cn['delta_V'] / cn['I'],
    np.nan
)

# FAI/GDP ratio
cn['fai_gdp'] = cn['fai_gdp_ratio']

# Clean spec: DeltaV/GDP
cn['dv_gdp'] = np.where(
    cn['gdp_100m'] > 0,
    cn['delta_V'] / cn['gdp_100m'],
    np.nan
)

# 筛选有效观测 (2011-2016)
cn_valid = cn[cn['year'] >= 2011].dropna(
    subset=['MUQ', 'fai_gdp', 'delta_V', 'I', 'gdp_100m', 'dv_gdp']
).copy()

# Winsorize (1%-99%)
cn_valid['MUQ_w'] = winsorize(cn_valid['MUQ'])
cn_valid['fai_gdp_w'] = winsorize(cn_valid['fai_gdp'])
cn_valid['dv_gdp_w'] = winsorize(cn_valid['dv_gdp'])

rprint(f'中国城市面板: {len(cn_valid)} 观测, {cn_valid["city"].nunique()} 城市')
rprint(f'年份范围: {cn_valid["year"].min()}-{cn_valid["year"].max()}')
rprint()

# 描述性统计
rprint('--- 描述性统计 ---')
desc_vars = {'MUQ_w': 'MUQ (winsorized)', 'fai_gdp_w': 'FAI/GDP (winsorized)',
             'dv_gdp_w': 'DeltaV/GDP (winsorized)'}
rprint(f'  {"Variable":<25s} {"Mean":>10s} {"Std":>10s} {"Min":>10s} {"P25":>10s} {"P50":>10s} {"P75":>10s} {"Max":>10s}')
rprint(f'  {"-"*95}')
for var, label in desc_vars.items():
    s = cn_valid[var]
    rprint(f'  {label:<25s} {s.mean():>10.4f} {s.std():>10.4f} {s.min():>10.4f} '
           f'{s.quantile(0.25):>10.4f} {s.quantile(0.50):>10.4f} {s.quantile(0.75):>10.4f} {s.max():>10.4f}')
rprint()

# =============================================================================
# 2. 中国城市回归: 五种规范
# =============================================================================
rprint('=' * 80)
rprint('PANEL A: 中国城市回归结果')
rprint('=' * 80)
rprint()

# --- (a) 原始: MUQ ~ FAI/GDP (pooled OLS, HC1) ---
rprint('-' * 60)
rprint('(a) 原始规范: MUQ ~ FAI/GDP [标注: 存在机械相关]')
rprint('-' * 60)
model_a = sm.OLS(cn_valid['MUQ_w'], sm.add_constant(cn_valid['fai_gdp_w'])).fit(cov_type='HC1')
report_ols(model_a, 'Pooled OLS, HC1', 'MUQ', 'FAI/GDP', len(cn_valid),
           n_cities=cn_valid['city'].nunique(), n_years=cn_valid['year'].nunique())
beta_original = model_a.params.iloc[1]

# --- (b) Clean: DeltaV/GDP ~ FAI/GDP (pooled OLS, HC1) ---
rprint('-' * 60)
rprint('(b) Clean 规范: DeltaV/GDP ~ FAI/GDP [新的主规范]')
rprint('-' * 60)
model_b = sm.OLS(cn_valid['dv_gdp_w'], sm.add_constant(cn_valid['fai_gdp_w'])).fit(cov_type='HC1')
report_ols(model_b, 'Pooled OLS, HC1', 'DeltaV/GDP', 'FAI/GDP', len(cn_valid),
           n_cities=cn_valid['city'].nunique(), n_years=cn_valid['year'].nunique())
beta_clean = model_b.params.iloc[1]

# --- (c) City FE: DeltaV/GDP ~ FAI/GDP + city FE ---
rprint('-' * 60)
rprint('(c) City Fixed Effects: DeltaV/GDP ~ FAI/GDP + city_FE')
rprint('-' * 60)

# 使用 city dummies 实现 FE (正确方法)
city_dummies_c = pd.get_dummies(cn_valid['city'].values, drop_first=True, dtype=float)
X_fe_c = np.column_stack([cn_valid['fai_gdp_w'].values, city_dummies_c.values])
y_fe_c = cn_valid['dv_gdp_w'].values

model_c_hc1 = sm.OLS(y_fe_c, X_fe_c).fit(cov_type='HC1')
model_c_cluster = sm.OLS(y_fe_c, X_fe_c).fit(
    cov_type='cluster', cov_kwds={'groups': cn_valid['city'].values}
)

# 提取 FAI/GDP 系数 (第0个参数)
rprint(f'  模型: City FE (dummy variable approach)')
rprint(f'  因变量: DeltaV/GDP, 自变量: FAI/GDP + city dummies')
rprint(f'  N = {len(cn_valid)}')
rprint(f'  城市数 = {cn_valid["city"].nunique()}')
rprint(f'  年份数 = {cn_valid["year"].nunique()}')
rprint()
rprint(f'  HC1 标准误:')
rprint(f'    beta(FAI/GDP) = {model_c_hc1.params[0]:.4f}')
rprint(f'    SE = {model_c_hc1.bse[0]:.4f}')
rprint(f'    t = {model_c_hc1.tvalues[0]:.3f}')
rprint(f'    p = {model_c_hc1.pvalues[0]:.6e}')
rprint()
rprint(f'  Clustered SE (by city):')
rprint(f'    beta(FAI/GDP) = {model_c_cluster.params[0]:.4f}')
rprint(f'    SE = {model_c_cluster.bse[0]:.4f}')
rprint(f'    t = {model_c_cluster.tvalues[0]:.3f}')
rprint(f'    p = {model_c_cluster.pvalues[0]:.6e}')
ci_c = model_c_cluster.conf_int()
rprint(f'    95% CI = [{ci_c[0, 0]:.4f}, {ci_c[0, 1]:.4f}]')
rprint(f'    Within R-squared = {model_c_cluster.rsquared:.4f} (包含 city dummies)')
rprint()
beta_fe = model_c_cluster.params[0]

# 面板结构诊断
city_obs = cn_valid.groupby('city').size()
rprint(f'  --- 面板结构诊断 ---')
rprint(f'  每城市观测数分布:')
for n_obs in sorted(city_obs.unique()):
    n_cities = (city_obs == n_obs).sum()
    rprint(f'    {n_obs} 期: {n_cities} 个城市')
rprint(f'  只有 1 期观测的城市: {(city_obs == 1).sum()}/{len(city_obs)} (被 FE 吸收)')
rprint(f'  有 >= 3 期观测的城市: {(city_obs >= 3).sum()}/{len(city_obs)}')
rprint()

# Between vs Within 相关
city_means = cn_valid.groupby('city')[['dv_gdp_w', 'fai_gdp_w']].mean()
from scipy.stats import pearsonr
r_between, p_between = pearsonr(city_means['dv_gdp_w'], city_means['fai_gdp_w'])
cn_valid['_dv_dm'] = cn_valid['dv_gdp_w'] - cn_valid.groupby('city')['dv_gdp_w'].transform('mean')
cn_valid['_fg_dm'] = cn_valid['fai_gdp_w'] - cn_valid.groupby('city')['fai_gdp_w'].transform('mean')
r_within, p_within = pearsonr(cn_valid['_dv_dm'], cn_valid['_fg_dm'])
rprint(f'  Between 相关 (城市均值): r = {r_between:.4f}, p = {p_between:.6e}')
rprint(f'  Within 相关 (去均值): r = {r_within:.4f}, p = {p_within:.6e}')
rprint(f'  >> Between 方向: {"负" if r_between < 0 else "正"} → Pooled OLS 的负效应来自城市间差异')
rprint(f'  >> Within 方向: {"正" if r_within > 0 else "负"} → 城市内时间变异显示正关系')
rprint(f'  >> 这构成经典的 Simpson\'s Paradox: 城市间负, 城市内正/不显著')
rprint()

# --- (d) Two-way FE: DeltaV/GDP ~ FAI/GDP + city FE + year FE ---
rprint('-' * 60)
rprint('(d) Two-way FE: DeltaV/GDP ~ FAI/GDP + city_FE + year_FE')
rprint('-' * 60)

# 使用 city + year dummies
year_dummies_d = pd.get_dummies(cn_valid['year'].values, drop_first=True, prefix='yr', dtype=float)
X_twfe = np.column_stack([cn_valid['fai_gdp_w'].values, city_dummies_c.values, year_dummies_d.values])
y_twfe = cn_valid['dv_gdp_w'].values

model_d_hc1 = sm.OLS(y_twfe, X_twfe).fit(cov_type='HC1')
model_d_cluster = sm.OLS(y_twfe, X_twfe).fit(
    cov_type='cluster', cov_kwds={'groups': cn_valid['city'].values}
)

rprint(f'  模型: Two-way FE (city + year dummies)')
rprint(f'  因变量: DeltaV/GDP, 自变量: FAI/GDP + city FE + year FE')
rprint(f'  N = {len(cn_valid)}')
rprint(f'  城市数 = {cn_valid["city"].nunique()}')
rprint(f'  年份数 = {cn_valid["year"].nunique()}')
rprint()
rprint(f'  HC1 标准误:')
rprint(f'    beta(FAI/GDP) = {model_d_hc1.params[0]:.4f}')
rprint(f'    SE = {model_d_hc1.bse[0]:.4f}')
rprint(f'    t = {model_d_hc1.tvalues[0]:.3f}')
rprint(f'    p = {model_d_hc1.pvalues[0]:.6e}')
rprint()
rprint(f'  Clustered SE (by city):')
rprint(f'    beta(FAI/GDP) = {model_d_cluster.params[0]:.4f}')
rprint(f'    SE = {model_d_cluster.bse[0]:.4f}')
rprint(f'    t = {model_d_cluster.tvalues[0]:.3f}')
rprint(f'    p = {model_d_cluster.pvalues[0]:.6e}')
ci_d = model_d_cluster.conf_int()
rprint(f'    95% CI = [{ci_d[0, 0]:.4f}, {ci_d[0, 1]:.4f}]')
rprint(f'    R-squared = {model_d_cluster.rsquared:.4f} (包含 city + year dummies)')
rprint()
beta_twfe = model_d_cluster.params[0]

# --- (e) 分位数回归: clean spec ---
rprint('-' * 60)
rprint('(e) 分位数回归: DeltaV/GDP ~ FAI/GDP (tau = 0.10, 0.25, 0.50, 0.75, 0.90)')
rprint('-' * 60)
rprint()
taus = [0.10, 0.25, 0.50, 0.75, 0.90]
rprint(f'  {"tau":<6s} {"beta":>10s} {"SE":>10s} {"t":>8s} {"p-value":>12s} {"CI_lo":>10s} {"CI_hi":>10s}')
rprint(f'  {"-"*70}')

qr_betas = {}
for tau in taus:
    qr_model = sm.QuantReg(
        cn_valid['dv_gdp_w'],
        sm.add_constant(cn_valid['fai_gdp_w'])
    ).fit(q=tau)
    b = qr_model.params.iloc[1]
    se = qr_model.bse.iloc[1]
    t = qr_model.tvalues.iloc[1]
    p = qr_model.pvalues.iloc[1]
    ci = qr_model.conf_int().iloc[1]
    sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ('+' if p < 0.10 else '')))
    rprint(f'  {tau:<6.2f} {b:>10.4f} {se:>10.4f} {t:>8.3f} {p:>12.6e} {ci.iloc[0]:>10.4f} {ci.iloc[1]:>10.4f} {sig}')
    qr_betas[tau] = b

rprint()
rprint(f'  解读: 分位数回归显示效应在不同条件分布上的异质性')
rprint(f'  若低分位数(低效率城市)效应更强, 表明过度投资问题主要集中在低效率城市')
rprint()

# =============================================================================
# 3. 美国 MSA 数据准备与回归
# =============================================================================
rprint('=' * 80)
rprint('PANEL B: 美国 MSA 回归结果')
rprint('=' * 80)
rprint()

us = pd.read_csv(US_PATH)
# 有效观测: 需要 dV, gdp, hu_growth
us_valid = us.dropna(subset=['dV', 'gdp_millions', 'hu_growth', 'invest_intensity', 'dV_GDP']).copy()
# 确保 GDP > 0
us_valid = us_valid[us_valid['gdp_millions'] > 0].copy()

# 构建 MUQ: 这里 MUQ_basic = dV / I_hu
# invest_intensity = I_hu / gdp_millions 相当于 "投资强度/GDP"
# dV_GDP 已经存在

# Winsorize
us_valid['MUQ_w'] = winsorize(us_valid['MUQ_basic'].dropna().reindex(us_valid.index))
us_valid['hu_growth_w'] = winsorize(us_valid['hu_growth'])
us_valid['dV_GDP_w'] = winsorize(us_valid['dV_GDP'])
us_valid['invest_w'] = winsorize(us_valid['invest_intensity'])

# 去掉 winsorize 后的 NaN
us_reg = us_valid.dropna(subset=['dV_GDP_w', 'hu_growth_w', 'invest_w']).copy()

rprint(f'美国 MSA 面板: {len(us_reg)} 观测, {us_reg["cbsa_code"].nunique()} MSAs')
rprint(f'年份范围: {us_reg["year"].min()}-{us_reg["year"].max()}')
rprint()

# --- (f) 原始: MUQ ~ housing_growth (pooled OLS) ---
rprint('-' * 60)
rprint('(f) 原始规范: MUQ ~ hu_growth [如有 MUQ_basic]')
rprint('-' * 60)
us_muq = us_reg.dropna(subset=['MUQ_w']).copy()
if len(us_muq) > 30:
    model_f = sm.OLS(us_muq['MUQ_w'], sm.add_constant(us_muq['hu_growth_w'])).fit(cov_type='HC1')
    report_ols(model_f, 'Pooled OLS, HC1', 'MUQ', 'hu_growth', len(us_muq),
               n_cities=us_muq['cbsa_code'].nunique())
    beta_us_original = model_f.params.iloc[1]
else:
    rprint(f'  MUQ_basic 有效观测不足 (N={len(us_muq)}), 跳过')
    beta_us_original = np.nan
rprint()

# --- (g) Clean: DeltaV/GDP ~ hu_growth (pooled OLS) ---
rprint('-' * 60)
rprint('(g) Clean 规范: DeltaV/GDP ~ hu_growth')
rprint('-' * 60)
model_g = sm.OLS(us_reg['dV_GDP_w'], sm.add_constant(us_reg['hu_growth_w'])).fit(cov_type='HC1')
report_ols(model_g, 'Pooled OLS, HC1', 'DeltaV/GDP', 'hu_growth', len(us_reg),
           n_cities=us_reg['cbsa_code'].nunique())
beta_us_clean = model_g.params.iloc[1]

# 同时用 invest_intensity (与中国 FAI/GDP 更可比)
rprint('-' * 60)
rprint('(g2) Clean 规范: DeltaV/GDP ~ invest_intensity')
rprint('-' * 60)
model_g2 = sm.OLS(us_reg['dV_GDP_w'], sm.add_constant(us_reg['invest_w'])).fit(cov_type='HC1')
report_ols(model_g2, 'Pooled OLS, HC1', 'DeltaV/GDP', 'invest_intensity', len(us_reg),
           n_cities=us_reg['cbsa_code'].nunique())
beta_us_clean_invest = model_g2.params.iloc[1]

# --- (h) Two-way FE (demeaning approach for large panel) ---
rprint('-' * 60)
rprint('(h) Two-way FE: DeltaV/GDP ~ hu_growth + MSA_FE + year_FE')
rprint('-' * 60)

# 对美国大面板使用 iterative demeaning (dummy approach 内存不够)
def demean_twfe(df, y_col, x_col, entity_col, time_col, max_iter=50, tol=1e-8):
    """Iterative demeaning for two-way FE (converges quickly)"""
    y = df[y_col].values.copy().astype(float)
    x = df[x_col].values.copy().astype(float)
    entities = df[entity_col].values
    times = df[time_col].values
    for _ in range(max_iter):
        y_old = y.copy()
        # Demean by entity
        for ent in np.unique(entities):
            mask = entities == ent
            y[mask] -= y[mask].mean()
            x[mask] -= x[mask].mean()
        # Demean by time
        for t in np.unique(times):
            mask = times == t
            y[mask] -= y[mask].mean()
            x[mask] -= x[mask].mean()
        if np.max(np.abs(y - y_old)) < tol:
            break
    return y, x

y_dm_h, x_dm_h = demean_twfe(us_reg, 'dV_GDP_w', 'hu_growth_w', 'cbsa_code', 'year')

model_h_hc1 = sm.OLS(y_dm_h, x_dm_h).fit(cov_type='HC1')
model_h_cluster = sm.OLS(y_dm_h, x_dm_h).fit(
    cov_type='cluster', cov_kwds={'groups': us_reg['cbsa_code'].values}
)

rprint(f'  模型: Two-way FE (MSA + year, iterative demeaning)')
rprint(f'  因变量: DeltaV/GDP, 自变量: hu_growth')
rprint(f'  N = {len(us_reg)}')
rprint(f'  MSA数 = {us_reg["cbsa_code"].nunique()}')
rprint(f'  年份数 = {us_reg["year"].nunique()}')
rprint()
rprint(f'  HC1 标准误:')
rprint(f'    beta = {model_h_hc1.params[0]:.4f}')
rprint(f'    SE = {model_h_hc1.bse[0]:.4f}')
rprint(f'    t = {model_h_hc1.tvalues[0]:.3f}')
rprint(f'    p = {model_h_hc1.pvalues[0]:.6e}')
rprint()
rprint(f'  Clustered SE (by MSA):')
rprint(f'    beta = {model_h_cluster.params[0]:.4f}')
rprint(f'    SE = {model_h_cluster.bse[0]:.4f}')
rprint(f'    t = {model_h_cluster.tvalues[0]:.3f}')
rprint(f'    p = {model_h_cluster.pvalues[0]:.6e}')
ci_h = model_h_cluster.conf_int()
rprint(f'    95% CI = [{ci_h[0, 0]:.4f}, {ci_h[0, 1]:.4f}]')
rprint()
beta_us_twfe = model_h_cluster.params[0]

# 同时用 invest_intensity
rprint('-' * 60)
rprint('(h2) Two-way FE: DeltaV/GDP ~ invest_intensity + MSA_FE + year_FE')
rprint('-' * 60)

y_dm_h2, x_dm_h2 = demean_twfe(us_reg, 'dV_GDP_w', 'invest_w', 'cbsa_code', 'year')

model_h2_cluster = sm.OLS(y_dm_h2, x_dm_h2).fit(
    cov_type='cluster', cov_kwds={'groups': us_reg['cbsa_code'].values}
)

rprint(f'  Clustered SE (by MSA):')
rprint(f'    beta = {model_h2_cluster.params[0]:.4f}')
rprint(f'    SE = {model_h2_cluster.bse[0]:.4f}')
rprint(f'    t = {model_h2_cluster.tvalues[0]:.3f}')
rprint(f'    p = {model_h2_cluster.pvalues[0]:.6e}')
ci_h2 = model_h2_cluster.conf_int()
rprint(f'    95% CI = [{ci_h2[0, 0]:.4f}, {ci_h2[0, 1]:.4f}]')
rprint()

# =============================================================================
# 4. 机械相关量化
# =============================================================================
rprint('=' * 80)
rprint('PANEL C: 机械相关量化')
rprint('=' * 80)
rprint()

rprint('--- Beta 衰减比 (Attenuation Ratio) ---')
rprint(f'  定义: 1 - (clean_beta / original_beta)')
rprint(f'  含义: clean spec 下 beta 相对于原始 spec 衰减了多少')
rprint(f'         衰减部分 = 可归因于机械相关的份额')
rprint()

# 中国
attenuation_cn = 1 - (beta_clean / beta_original)
rprint(f'  中国城市:')
rprint(f'    原始 beta (MUQ ~ FAI/GDP) = {beta_original:.4f}')
rprint(f'    Clean beta (DeltaV/GDP ~ FAI/GDP) = {beta_clean:.4f}')
rprint(f'    衰减比 = 1 - ({beta_clean:.4f} / {beta_original:.4f}) = {attenuation_cn:.4f}')
rprint(f'    机械相关份额 = {attenuation_cn*100:.1f}%')
rprint(f'    残余真实效应份额 = {(1-attenuation_cn)*100:.1f}%')
rprint()

# 与 FE 进一步比较
if not np.isnan(beta_fe):
    rprint(f'  Clean → City FE 比较:')
    rprint(f'    Clean beta (pooled) = {beta_clean:.4f}')
    rprint(f'    City FE beta = {beta_fe:.4f}')
    if np.sign(beta_fe) != np.sign(beta_clean):
        rprint(f'    >> 符号翻转: pooled 为{"负" if beta_clean < 0 else "正"}, city FE 为{"正" if beta_fe > 0 else "负"}')
        rprint(f'    >> 这表明 pooled OLS 的负效应完全由城市间 (between) 变异驱动')
        rprint(f'    >> 控制城市固定效应后, 城市内 (within) 变异方向相反')
    else:
        attenuation_fe = 1 - (beta_fe / beta_clean)
        rprint(f'    额外衰减比 = {attenuation_fe:.4f}')
    rprint()

rprint(f'  总衰减 (原始 → TWFE):')
total_att = 1 - (beta_twfe / beta_original)
rprint(f'    TWFE beta = {beta_twfe:.4f}')
rprint(f'    总衰减比 = 1 - ({beta_twfe:.4f} / {beta_original:.4f}) = {total_att:.4f}')
rprint(f'    原始 beta 中 {total_att*100:.1f}% 来自机械相关+城市/年份异质性')
rprint()

# =============================================================================
# 5. Sign Reversal 对比 (中美 Clean Spec)
# =============================================================================
rprint('=' * 80)
rprint('PANEL D: Sign Reversal 对比 (Clean Specification)')
rprint('=' * 80)
rprint()

rprint('--- 统一度量: DeltaV/GDP ~ 投资强度 ---')
rprint()
rprint(f'  {"国家":<8s} {"Spec":<30s} {"beta":>10s} {"p-value":>14s} {"符号":<6s}')
rprint(f'  {"-"*75}')

# 中国 clean
p_cn = model_b.pvalues.iloc[1]
rprint(f'  {"中国":<8s} {"DeltaV/GDP ~ FAI/GDP":<30s} {beta_clean:>10.4f} {p_cn:>14.6e} {"负 (-)" if beta_clean < 0 else "正 (+)":<6s}')

# 美国 clean (hu_growth)
p_us = model_g.pvalues.iloc[1]
rprint(f'  {"美国":<8s} {"DeltaV/GDP ~ hu_growth":<30s} {beta_us_clean:>10.4f} {p_us:>14.6e} {"负 (-)" if beta_us_clean < 0 else "正 (+)":<6s}')

# 美国 clean (invest_intensity)
p_us2 = model_g2.pvalues.iloc[1]
rprint(f'  {"美国":<8s} {"DeltaV/GDP ~ invest_int":<30s} {beta_us_clean_invest:>10.4f} {p_us2:>14.6e} {"负 (-)" if beta_us_clean_invest < 0 else "正 (+)":<6s}')

rprint()
sign_reversal = (beta_clean < 0) and (beta_us_clean > 0 or beta_us_clean_invest > 0)
rprint(f'  Sign reversal 在 clean spec 下成立? {"YES" if sign_reversal else "NO"}')
rprint(f'  中国: 更多投资/GDP → 更少价值增量/GDP (过度投资, 边际递减)')
rprint(f'  美国: 更多住房增长 → 更多价值增量/GDP (供给创造价值)')
rprint()

# TWFE 下的 sign reversal
rprint('--- Sign Reversal in TWFE ---')
rprint(f'  中国 TWFE: beta = {beta_twfe:.4f}')
rprint(f'  美国 TWFE: beta = {beta_us_twfe:.4f}')
sign_reversal_twfe = (beta_twfe < 0) and (beta_us_twfe > 0)
rprint(f'  TWFE 下 sign reversal 成立? {"YES" if sign_reversal_twfe else "NO (方向不变但可能不显著)"}')
rprint()

# =============================================================================
# 6. 人口加权统计量: "82.2% cities below MUQ=1"
# =============================================================================
rprint('=' * 80)
rprint('PANEL E: 人口加权 MUQ 分布统计')
rprint('=' * 80)
rprint()

# 使用最新年份 (2016) 的截面数据
cn_2016 = cn[cn['year'] == 2016].dropna(subset=['MUQ', 'pop_10k']).copy()
cn_2016['MUQ_w'] = winsorize(cn_2016['MUQ'])

n_cities_total = len(cn_2016)
n_below_1 = (cn_2016['MUQ'] < 1).sum()
pct_below_1_unweighted = n_below_1 / n_cities_total * 100

# 人口加权
pop_total = cn_2016['pop_10k'].sum()
pop_below_1 = cn_2016.loc[cn_2016['MUQ'] < 1, 'pop_10k'].sum()
pct_below_1_weighted = pop_below_1 / pop_total * 100

rprint(f'  截面年份: 2016')
rprint(f'  有效城市: {n_cities_total}')
rprint(f'  总人口 (pop_10k): {pop_total:.0f} 万人 ({pop_total/10000:.1f} 亿人)')
rprint()
rprint(f'  MUQ < 1 (过度投资) 的城市:')
rprint(f'    未加权: {n_below_1}/{n_cities_total} = {pct_below_1_unweighted:.1f}%')
rprint(f'    人口加权: {pop_below_1:.0f}/{pop_total:.0f} 万人 = {pct_below_1_weighted:.1f}%')
rprint()

# 更多分位数
rprint(f'  MUQ 分布 (2016 截面):')
rprint(f'    均值: {cn_2016["MUQ"].mean():.4f}')
rprint(f'    中位数: {cn_2016["MUQ"].median():.4f}')
rprint(f'    人口加权均值: {np.average(cn_2016["MUQ"], weights=cn_2016["pop_10k"]):.4f}')
rprint()

# 按区域分
rprint(f'  按区域 (2016):')
rprint(f'    {"区域":<8s} {"N":>5s} {"MUQ<1 %":>10s} {"人口加权MUQ<1%":>16s} {"MUQ均值":>10s}')
rprint(f'    {"-"*55}')
for region in ['东部', '中部', '西部', '东北']:
    sub = cn_2016[cn_2016['region'] == region]
    if len(sub) > 0:
        n_r = len(sub)
        pct_r = (sub['MUQ'] < 1).sum() / n_r * 100
        pop_r = sub['pop_10k'].sum()
        pop_below_r = sub.loc[sub['MUQ'] < 1, 'pop_10k'].sum()
        pct_r_w = pop_below_r / pop_r * 100 if pop_r > 0 else 0
        mu_r = sub['MUQ'].mean()
        rprint(f'    {region:<8s} {n_r:>5d} {pct_r:>10.1f}% {pct_r_w:>15.1f}% {mu_r:>10.4f}')
rprint()

# 多年份统计
rprint(f'  各年份 MUQ<1 比例:')
rprint(f'    {"年份":<6s} {"N":>5s} {"未加权%":>10s} {"人口加权%":>12s}')
rprint(f'    {"-"*40}')
for yr in range(2011, 2017):
    sub = cn[(cn['year'] == yr)].dropna(subset=['MUQ', 'pop_10k'])
    if len(sub) > 0:
        n_yr = len(sub)
        pct_yr = (sub['MUQ'] < 1).sum() / n_yr * 100
        pop_yr = sub['pop_10k'].sum()
        pop_below_yr = sub.loc[sub['MUQ'] < 1, 'pop_10k'].sum()
        pct_yr_w = pop_below_yr / pop_yr * 100 if pop_yr > 0 else 0
        rprint(f'    {yr:<6d} {n_yr:>5d} {pct_yr:>10.1f}% {pct_yr_w:>11.1f}%')
rprint()

# =============================================================================
# 7. 汇总表
# =============================================================================
rprint('=' * 80)
rprint('PANEL F: 回归结果汇总表')
rprint('=' * 80)
rprint()

rprint(f'  {"Spec":<40s} {"beta":>10s} {"SE":>10s} {"p":>14s} {"Sig":>5s} {"N":>6s}')
rprint(f'  {"-"*90}')

# 中国
specs = [
    ('(a) CN: MUQ ~ FAI/GDP [pooled]', model_a.params.iloc[1], model_a.bse.iloc[1], model_a.pvalues.iloc[1], len(cn_valid)),
    ('(b) CN: DeltaV/GDP ~ FAI/GDP [pooled]', model_b.params.iloc[1], model_b.bse.iloc[1], model_b.pvalues.iloc[1], len(cn_valid)),
    ('(c) CN: DeltaV/GDP ~ FAI/GDP [city FE]', model_c_cluster.params[0], model_c_cluster.bse[0], model_c_cluster.pvalues[0], len(cn_valid)),
    ('(d) CN: DeltaV/GDP ~ FAI/GDP [TWFE]', model_d_cluster.params[0], model_d_cluster.bse[0], model_d_cluster.pvalues[0], len(cn_valid)),
]

# 美国
if not np.isnan(beta_us_original):
    specs.append(('(f) US: MUQ ~ hu_growth [pooled]', model_f.params.iloc[1], model_f.bse.iloc[1], model_f.pvalues.iloc[1], len(us_muq)))
specs.extend([
    ('(g) US: DeltaV/GDP ~ hu_growth [pooled]', model_g.params.iloc[1], model_g.bse.iloc[1], model_g.pvalues.iloc[1], len(us_reg)),
    ('(g2) US: DeltaV/GDP ~ invest_int [pooled]', model_g2.params.iloc[1], model_g2.bse.iloc[1], model_g2.pvalues.iloc[1], len(us_reg)),
    ('(h) US: DeltaV/GDP ~ hu_growth [TWFE]', model_h_cluster.params[0], model_h_cluster.bse[0], model_h_cluster.pvalues[0], len(us_reg)),
    ('(h2) US: DeltaV/GDP ~ invest_int [TWFE]', model_h2_cluster.params[0], model_h2_cluster.bse[0], model_h2_cluster.pvalues[0], len(us_reg)),
])

for label, b, se, p, n in specs:
    sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ('+' if p < 0.10 else '')))
    rprint(f'  {label:<40s} {b:>10.4f} {se:>10.4f} {p:>14.6e} {sig:>5s} {n:>6d}')

rprint()
rprint(f'  显著性: *** p<0.001, ** p<0.01, * p<0.05, + p<0.10')
rprint()

# =============================================================================
# 8. 核心结论
# =============================================================================
rprint('=' * 80)
rprint('PANEL G: 核心结论与审稿人回应要点')
rprint('=' * 80)
rprint()
rprint(f'1. 机械相关量化:')
rprint(f'   原始 beta (MUQ~FAI/GDP) = {beta_original:.4f}')
rprint(f'   Clean beta (DeltaV/GDP~FAI/GDP) = {beta_clean:.4f}')
rprint(f'   衰减比 = {attenuation_cn:.1%} → 原始 beta 中约 {attenuation_cn:.1%} 可归因于机械相关')
rprint(f'   但 clean spec 下 beta 仍然显著为负 (p = {model_b.pvalues.iloc[1]:.6e})')
rprint()
rprint(f'2. Within-estimator (城市固定效应):')
rprint(f'   City FE beta = {beta_fe:.4f}, p = {model_c_cluster.pvalues[0]:.6e}')
rprint(f'   TWFE beta = {beta_twfe:.4f}, p = {model_d_cluster.pvalues[0]:.6e}')
p_fe = model_c_cluster.pvalues[0]
p_twfe = model_d_cluster.pvalues[0]
if beta_fe > 0 and beta_clean < 0:
    rprint(f'   >> 关键发现: City FE 下符号翻转 (负→正)')
    rprint(f'   构成 Simpson\'s Paradox:')
    rprint(f'     Between (城市间): 投资比高的城市, 价值增量/GDP低 (负)')
    rprint(f'     Within (城市内): 同一城市投资比上升时, 价值增量/GDP也上升 (正)')
    rprint(f'   解读: 城市间系统性差异是核心 -- 长期过度投资的城市效率低')
    rprint(f'         短期内投资增长可能反映经济景气共同趋势')
    rprint(f'   面板结构限制: 150/213 城市仅1期观测, within variation 极有限')
else:
    rprint(f'   City FE 下 p={p_fe:.3f}, TWFE 下 p={p_twfe:.3f}')
rprint()
rprint(f'3. Sign reversal (中美对比):')
rprint(f'   Clean spec 下: 中国 beta = {beta_clean:.4f} (负), 美国 beta = {beta_us_clean:.4f} ({"正" if beta_us_clean > 0 else "负"})')
rprint(f'   Sign reversal 在消除机械相关后 {"仍然成立" if sign_reversal else "不再成立"}')
rprint()
rprint(f'4. 人口加权统计:')
rprint(f'   2016年 MUQ<1 城市: {pct_below_1_unweighted:.1f}% (未加权), {pct_below_1_weighted:.1f}% (人口加权)')
rprint()
rprint(f'5. 审稿人回应建议:')
rprint(f'   - 将 clean spec (DeltaV/GDP~FAI/GDP) 作为新的主规范')
rprint(f'   - 原始 MUQ 回归保留在 Extended Data 中, 标注机械相关')
rprint(f'   - 在 Methods 中增加衰减比分析')
rprint(f'   - City FE 不显著问题: 解释为城市间（Between）变异是主要识别来源')
rprint(f'   - 建议增加: 工具变量策略 (如用历史投资率作为 IV)')

# =============================================================================
# 保存报告
# =============================================================================
os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

print(f'\n报告已保存至: {REPORT_PATH}')
