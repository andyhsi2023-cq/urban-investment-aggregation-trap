"""
n20_provincial_muq.py -- 省级 MUQ 全面分析
==============================================================

目的:
  基于中国31省2005-2023面板数据，构建省级 Marginal Urban Q (MUQ)，
  并进行 Simpson's Paradox 检验、Clean Specification 回归、
  时序分析、标度律估计等全方位分析，与城市级结果形成互补验证。

核心优势:
  - 时间跨度19年（2005-2023），覆盖完整周期
  - FAI 为省级统计局真实数据（2005-2019），非估算
  - 覆盖2020-2024房地产危机期（通过V_billion变化捕捉）

输入:
  - 02-data/processed/china_provincial_panel_real.csv

输出:
  - 03-analysis/models/provincial_muq_report.txt
  - 02-data/processed/china_provincial_muq.csv

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
DATA_PATH = os.path.join(BASE, '02-data/processed/china_provincial_panel_real.csv')
REPORT_PATH = os.path.join(BASE, '03-analysis/models/provincial_muq_report.txt')
MUQ_CSV_PATH = os.path.join(BASE, '02-data/processed/china_provincial_muq.csv')

np.random.seed(20260322)

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
    return f'  {name:<20s} {coef:>10.4f} {se:>10.4f} {t:>8.3f}  p={p:.4e} [{ci_lo:>8.4f}, {ci_hi:>8.4f}] {sig}'

def report_ols(model, label, dep_var, indep_var, n, n_prov=None, n_years=None):
    """报告 OLS 回归结果"""
    rprint(f'  模型: {label}')
    rprint(f'  因变量: {dep_var}, 自变量: {indep_var}')
    rprint(f'  N = {n}')
    if n_prov:
        rprint(f'  省份数 = {n_prov}')
    if n_years:
        rprint(f'  年份数 = {n_years}')
    rprint(f'  R-squared = {model.rsquared:.4f}')
    if hasattr(model, 'rsquared_adj'):
        rprint(f'  Adj R-squared = {model.rsquared_adj:.4f}')
    rprint()
    ci = model.conf_int()
    rprint(f'  {"Variable":<20s} {"Coef":>10s} {"SE":>10s} {"t":>8s}  {"p-value":>14s} {"95% CI":>20s}')
    rprint(f'  {"-"*90}')
    for vname in model.params.index:
        if vname.startswith('C(') or vname.startswith('fe_'):
            continue  # 跳过固定效应虚拟变量
        c = model.params[vname]
        s = model.bse[vname]
        t_val = model.tvalues[vname]
        p_val = model.pvalues[vname]
        rprint(format_coef(vname, c, s, t_val, p_val, ci.loc[vname, 0], ci.loc[vname, 1]))
    rprint()

# =============================================================================
# 1. 读取数据与预处理
# =============================================================================
rprint('=' * 80)
rprint('省级 MUQ (Marginal Urban Q) 全面分析')
rprint('=' * 80)
rprint(f'分析日期: 2026-03-22')
rprint(f'数据来源: {DATA_PATH}')
rprint()

df = pd.read_csv(DATA_PATH)
rprint(f'原始数据: {len(df)} 观测, {df["province_en"].nunique()} 省, '
       f'{df["year"].min()}-{df["year"].max()}')

# 区域分组 (东/中/西 三大地带)
east = ['Beijing', 'Tianjin', 'Hebei', 'Liaoning', 'Shanghai', 'Jiangsu',
        'Zhejiang', 'Fujian', 'Shandong', 'Guangdong', 'Hainan']
central = ['Shanxi', 'Jilin', 'Heilongjiang', 'Anhui', 'Jiangxi', 'Henan',
           'Hubei', 'Hunan']
west = ['Inner Mongolia', 'Guangxi', 'Chongqing', 'Sichuan', 'Guizhou',
        'Yunnan', 'Tibet', 'Shaanxi', 'Gansu', 'Qinghai', 'Ningxia', 'Xinjiang']

def assign_region(prov):
    if prov in east: return 'East'
    elif prov in central: return 'Central'
    elif prov in west: return 'West'
    return 'Unknown'

df['region'] = df['province_en'].apply(assign_region)
rprint(f'区域分组: 东部 {len(east)} 省, 中部 {len(central)} 省, 西部 {len(west)} 省')
rprint()

# =============================================================================
# 2. 构建 MUQ
# =============================================================================
rprint('=' * 80)
rprint('第一部分: 构建省级 MUQ')
rprint('=' * 80)
rprint()

# 排序确保差分正确
df = df.sort_values(['province_en', 'year']).reset_index(drop=True)

# Delta V: 住房价值年度变化
df['delta_V'] = df.groupby('province_en')['V_billion'].diff()

# Delta GDP
df['delta_GDP'] = df.groupby('province_en')['gdp_billion_yuan'].diff()

# Housing-based MUQ = Delta(V) / FAI
# 注意: V_billion 从2010开始有值，FAI到2019截止
# 因此 Housing MUQ 的有效区间为 2011-2019 (diff后)
df['muq_housing'] = df['delta_V'] / df['fai_billion_yuan']

# GDP-based MUQ = Delta(GDP) / FAI
df['muq_gdp'] = df['delta_GDP'] / df['fai_billion_yuan']

# 人均 GDP (元/人)
df['pc_gdp'] = df['gdp_billion_yuan'] / df['total_pop_10k'] * 10000

# DeltaV/GDP 和 FAI/GDP (用于 clean specification)
df['deltaV_gdp'] = df['delta_V'] / df['gdp_billion_yuan']
df['fai_gdp'] = df['fai_billion_yuan'] / df['gdp_billion_yuan']

# 描述有效MUQ样本
muq_h_valid = df['muq_housing'].notna()
muq_g_valid = df['muq_gdp'].notna()

rprint('Housing-based MUQ (DeltaV / FAI):')
rprint(f'  有效观测: {muq_h_valid.sum()}')
if muq_h_valid.sum() > 0:
    rprint(f'  年份范围: {df.loc[muq_h_valid, "year"].min()}-{df.loc[muq_h_valid, "year"].max()}')
    rprint(f'  原始统计: mean={df.loc[muq_h_valid, "muq_housing"].mean():.4f}, '
           f'median={df.loc[muq_h_valid, "muq_housing"].median():.4f}, '
           f'std={df.loc[muq_h_valid, "muq_housing"].std():.4f}')
    rprint(f'  原始范围: [{df.loc[muq_h_valid, "muq_housing"].min():.4f}, '
           f'{df.loc[muq_h_valid, "muq_housing"].max():.4f}]')
rprint()

rprint('GDP-based MUQ (DeltaGDP / FAI):')
rprint(f'  有效观测: {muq_g_valid.sum()}')
if muq_g_valid.sum() > 0:
    rprint(f'  年份范围: {df.loc[muq_g_valid, "year"].min()}-{df.loc[muq_g_valid, "year"].max()}')
    rprint(f'  原始统计: mean={df.loc[muq_g_valid, "muq_gdp"].mean():.4f}, '
           f'median={df.loc[muq_g_valid, "muq_gdp"].median():.4f}, '
           f'std={df.loc[muq_g_valid, "muq_gdp"].std():.4f}')
rprint()

# Winsorize 1%/99%
for col in ['muq_housing', 'muq_gdp', 'deltaV_gdp', 'fai_gdp']:
    valid = df[col].notna()
    if valid.sum() > 10:
        df.loc[valid, col] = winsorize(df.loc[valid, col])

rprint('Winsorize 1%/99% 后:')
muq_h_valid = df['muq_housing'].notna()
muq_g_valid = df['muq_gdp'].notna()
if muq_h_valid.sum() > 0:
    rprint(f'  Housing MUQ: mean={df.loc[muq_h_valid, "muq_housing"].mean():.4f}, '
           f'median={df.loc[muq_h_valid, "muq_housing"].median():.4f}, '
           f'std={df.loc[muq_h_valid, "muq_housing"].std():.4f}')
if muq_g_valid.sum() > 0:
    rprint(f'  GDP MUQ: mean={df.loc[muq_g_valid, "muq_gdp"].mean():.4f}, '
           f'median={df.loc[muq_g_valid, "muq_gdp"].median():.4f}, '
           f'std={df.loc[muq_g_valid, "muq_gdp"].std():.4f}')
rprint()

# =============================================================================
# 3. Simpson's Paradox 检验
# =============================================================================
rprint('=' * 80)
rprint('第二部分: Simpson\'s Paradox 检验')
rprint('=' * 80)
rprint()
rprint('检验: MUQ 与 城镇化率 的相关性在组内与全样本是否方向相反')
rprint()

# 使用 GDP-based MUQ（样本更大，2006-2019）
muq_col = 'muq_gdp'
muq_label = 'GDP-based MUQ'

# --- 3a. 按区域分组 (东/中/西) ---
rprint('--- 3a. 按区域分组 (东/中/西) ---')
rprint()

sim_data = df[['province_en', 'year', 'region', muq_col, 'urbanization_rate_pct']].dropna()
rprint(f'有效样本: N = {len(sim_data)}')
rprint()

# 全样本 Spearman
r_pool, p_pool = stats.spearmanr(sim_data['urbanization_rate_pct'], sim_data[muq_col])
rprint(f'全样本 (Pooled):')
rprint(f'  Spearman rho = {r_pool:.4f}, p = {p_pool:.4e}, N = {len(sim_data)}')
rprint()

rprint('组内 (Within-region):')
simpson_flag_region = False
for reg in ['East', 'Central', 'West']:
    sub = sim_data[sim_data['region'] == reg]
    if len(sub) < 10:
        rprint(f'  {reg}: N = {len(sub)} (样本不足)')
        continue
    r_sub, p_sub = stats.spearmanr(sub['urbanization_rate_pct'], sub[muq_col])
    rprint(f'  {reg:<10s}: Spearman rho = {r_sub:.4f}, p = {p_sub:.4e}, N = {len(sub)}')
    if r_sub * r_pool < 0:
        simpson_flag_region = True

rprint()
if simpson_flag_region:
    rprint('  ** Simpson\'s Paradox 存在: 组内与全样本相关方向相反 **')
else:
    rprint('  Simpson\'s Paradox 未检出 (按区域分组)')
rprint()

# --- 3b. 按人均GDP三分位数分组 ---
rprint('--- 3b. 按人均GDP三分位数分组 ---')
rprint()

# 用 2015 年人均 GDP 作为时不变分组标准
pc_gdp_2015 = df[df['year'] == 2015][['province_en', 'pc_gdp']].dropna()
q33 = pc_gdp_2015['pc_gdp'].quantile(0.333)
q67 = pc_gdp_2015['pc_gdp'].quantile(0.667)
rprint(f'分组依据: 2015年人均GDP (元/人)')
rprint(f'  低收入 < {q33:.0f} < 中收入 < {q67:.0f} < 高收入')

def income_group(prov):
    val = pc_gdp_2015[pc_gdp_2015['province_en'] == prov]['pc_gdp']
    if len(val) == 0:
        return 'Unknown'
    v = val.values[0]
    if v < q33: return 'Low'
    elif v < q67: return 'Mid'
    else: return 'High'

sim_data['income_group'] = sim_data['province_en'].apply(income_group)

rprint()
simpson_flag_income = False
for grp in ['Low', 'Mid', 'High']:
    sub = sim_data[sim_data['income_group'] == grp]
    if len(sub) < 10:
        rprint(f'  {grp}: N = {len(sub)} (样本不足)')
        continue
    r_sub, p_sub = stats.spearmanr(sub['urbanization_rate_pct'], sub[muq_col])
    rprint(f'  {grp:<10s}: Spearman rho = {r_sub:.4f}, p = {p_sub:.4e}, N = {len(sub)}')
    if r_sub * r_pool < 0:
        simpson_flag_income = True

rprint()
if simpson_flag_income:
    rprint('  ** Simpson\'s Paradox 存在: 组内与全样本相关方向相反 (按收入分组) **')
else:
    rprint('  Simpson\'s Paradox 未检出 (按收入分组)')
rprint()

# --- 3c. Housing-based MUQ 同样检验 ---
rprint('--- 3c. Housing-based MUQ 重复检验 ---')
rprint()
sim_h = df[['province_en', 'year', 'region', 'muq_housing', 'urbanization_rate_pct']].dropna()
if len(sim_h) > 20:
    r_pool_h, p_pool_h = stats.spearmanr(sim_h['urbanization_rate_pct'], sim_h['muq_housing'])
    rprint(f'全样本: Spearman rho = {r_pool_h:.4f}, p = {p_pool_h:.4e}, N = {len(sim_h)}')
    for reg in ['East', 'Central', 'West']:
        sub = sim_h[sim_h['region'] == reg]
        if len(sub) >= 10:
            r_s, p_s = stats.spearmanr(sub['urbanization_rate_pct'], sub['muq_housing'])
            rprint(f'  {reg:<10s}: rho = {r_s:.4f}, p = {p_s:.4e}, N = {len(sub)}')
rprint()

# =============================================================================
# 4. Clean Specification 回归
# =============================================================================
rprint('=' * 80)
rprint('第三部分: Clean Specification 回归')
rprint('=' * 80)
rprint()
rprint('Clean Specification: DeltaV/GDP ~ FAI/GDP')
rprint('消除 MUQ=DeltaV/FAI ~ FAI/GDP 中分母共享 FAI 的机械相关')
rprint()

# 准备回归数据
reg_data = df[['province_en', 'year', 'region', 'deltaV_gdp', 'fai_gdp',
               'urbanization_rate_pct']].dropna().copy()
rprint(f'回归样本: N = {len(reg_data)}, '
       f'{reg_data["province_en"].nunique()} 省, '
       f'{reg_data["year"].nunique()} 年 ({reg_data["year"].min()}-{reg_data["year"].max()})')
rprint()

# --- 4a. Pooled OLS with HC1 ---
rprint('--- 4a. Pooled OLS (HC1 robust SE) ---')
rprint()
X_pool = sm.add_constant(reg_data['fai_gdp'])
y_pool = reg_data['deltaV_gdp']
m_pool = sm.OLS(y_pool, X_pool).fit(cov_type='HC1')
report_ols(m_pool, 'Pooled OLS (HC1)', 'DeltaV/GDP', 'FAI/GDP',
           len(reg_data), reg_data['province_en'].nunique(), reg_data['year'].nunique())

# --- 4b. Province Fixed Effects ---
rprint('--- 4b. Province Fixed Effects ---')
rprint()
# 使用 statsmodels 的 from_formula 来处理固定效应
# 为避免打印大量虚拟变量，手动 demean
def within_transform(data, group_col, value_cols):
    """组内去均值 (within transformation)"""
    result = data.copy()
    for col in value_cols:
        group_means = data.groupby(group_col)[col].transform('mean')
        result[col + '_w'] = data[col] - group_means
    return result

reg_data = within_transform(reg_data, 'province_en', ['deltaV_gdp', 'fai_gdp'])

X_fe = sm.add_constant(reg_data['fai_gdp_w'])
y_fe = reg_data['deltaV_gdp_w']
m_fe = sm.OLS(y_fe, X_fe).fit(cov_type='HC1')

n_prov = reg_data['province_en'].nunique()
n_yr = reg_data['year'].nunique()
n_obs = len(reg_data)
# 调整自由度: k = n_prov - 1 个虚拟变量已被吸收
rprint(f'  模型: Province FE (within transformation)')
rprint(f'  因变量: DeltaV/GDP (demeaned), 自变量: FAI/GDP (demeaned)')
rprint(f'  N = {n_obs}, 省份数 = {n_prov}, 年份数 = {n_yr}')
rprint(f'  Within R-squared = {m_fe.rsquared:.4f}')
rprint()
ci_fe = m_fe.conf_int()
for vname in m_fe.params.index:
    c = m_fe.params[vname]
    s = m_fe.bse[vname]
    t_val = m_fe.tvalues[vname]
    p_val = m_fe.pvalues[vname]
    rprint(format_coef(vname, c, s, t_val, p_val, ci_fe.loc[vname, 0], ci_fe.loc[vname, 1]))
rprint()

# --- 4c. Two-way FE (Province + Year) ---
rprint('--- 4c. Two-way FE (Province + Year) ---')
rprint()
reg_data2 = within_transform(reg_data, 'year', ['deltaV_gdp_w', 'fai_gdp_w'])
# 双重去均值: 先去省均值，再去年均值
X_twfe = sm.add_constant(reg_data2['fai_gdp_w_w'])
y_twfe = reg_data2['deltaV_gdp_w_w']
m_twfe = sm.OLS(y_twfe, X_twfe).fit(cov_type='HC1')

rprint(f'  模型: Two-way FE (Province + Year, within transformation)')
rprint(f'  因变量: DeltaV/GDP (double-demeaned), 自变量: FAI/GDP (double-demeaned)')
rprint(f'  N = {n_obs}, 省份数 = {n_prov}, 年份数 = {n_yr}')
rprint(f'  Within R-squared = {m_twfe.rsquared:.4f}')
rprint()
ci_twfe = m_twfe.conf_int()
for vname in m_twfe.params.index:
    c = m_twfe.params[vname]
    s = m_twfe.bse[vname]
    t_val = m_twfe.tvalues[vname]
    p_val = m_twfe.pvalues[vname]
    rprint(format_coef(vname, c, s, t_val, p_val, ci_twfe.loc[vname, 0], ci_twfe.loc[vname, 1]))
rprint()

# --- 4d. GDP-based Clean Spec: DeltaGDP/GDP ~ FAI/GDP ---
rprint('--- 4d. GDP-based Clean Specification: DeltaGDP/GDP ~ FAI/GDP ---')
rprint()
df['deltaGDP_gdp'] = df['delta_GDP'] / df['gdp_billion_yuan']
reg_gdp = df[['province_en', 'year', 'deltaGDP_gdp', 'fai_gdp']].dropna().copy()
# winsorize
for col in ['deltaGDP_gdp']:
    reg_gdp[col] = winsorize(reg_gdp[col])

X_gdp = sm.add_constant(reg_gdp['fai_gdp'])
y_gdp = reg_gdp['deltaGDP_gdp']
m_gdp = sm.OLS(y_gdp, X_gdp).fit(cov_type='HC1')
report_ols(m_gdp, 'Pooled OLS (HC1)', 'DeltaGDP/GDP', 'FAI/GDP',
           len(reg_gdp), reg_gdp['province_en'].nunique())

# 汇总 clean spec 结果
rprint('--- Clean Specification 汇总 ---')
rprint()
rprint(f'  {"Specification":<35s} {"beta(FAI/GDP)":>12s} {"SE":>10s} {"p-value":>14s} {"N":>6s}')
rprint(f'  {"-"*80}')

specs = [
    ('Pooled OLS (DeltaV/GDP)', m_pool, 'fai_gdp'),
    ('Province FE (DeltaV/GDP)', m_fe, 'fai_gdp_w'),
    ('Two-way FE (DeltaV/GDP)', m_twfe, 'fai_gdp_w_w'),
    ('Pooled OLS (DeltaGDP/GDP)', m_gdp, 'fai_gdp'),
]
for label, m, var in specs:
    if var in m.params.index:
        b = m.params[var]
        s = m.bse[var]
        p = m.pvalues[var]
        rprint(f'  {label:<35s} {b:>12.4f} {s:>10.4f} p={p:.4e} {int(m.nobs):>6d}')
rprint()

# =============================================================================
# 5. 省级 MUQ 时序分析
# =============================================================================
rprint('=' * 80)
rprint('第四部分: 省级 MUQ 时序分析')
rprint('=' * 80)
rprint()

# --- 5a. 全国加权平均 MUQ (GDP权重) ---
rprint('--- 5a. 全国GDP加权平均 MUQ 时序 ---')
rprint()

# Housing-based MUQ (需要 V 和 FAI 都有值: 2011-2019)
ts_h = df[df['muq_housing'].notna()].copy()
# GDP加权
ts_h['weight'] = ts_h.groupby('year')['gdp_billion_yuan'].transform(lambda x: x / x.sum())
ts_h['weighted_muq'] = ts_h['muq_housing'] * ts_h['weight']
national_h = ts_h.groupby('year').agg(
    muq_weighted=('weighted_muq', 'sum'),
    muq_median=('muq_housing', 'median'),
    muq_mean=('muq_housing', 'mean'),
    n_prov=('province_en', 'nunique')
).reset_index()

rprint('Housing-based MUQ (DeltaV/FAI), GDP-weighted national average:')
rprint(f'  {"Year":>6s} {"Weighted":>10s} {"Mean":>10s} {"Median":>10s} {"N_prov":>8s}')
for _, r in national_h.iterrows():
    rprint(f'  {int(r["year"]):>6d} {r["muq_weighted"]:>10.4f} {r["muq_mean"]:>10.4f} '
           f'{r["muq_median"]:>10.4f} {int(r["n_prov"]):>8d}')
rprint()

# GDP-based MUQ (2006-2019)
ts_g = df[df['muq_gdp'].notna()].copy()
ts_g['weight'] = ts_g.groupby('year')['gdp_billion_yuan'].transform(lambda x: x / x.sum())
ts_g['weighted_muq'] = ts_g['muq_gdp'] * ts_g['weight']
national_g = ts_g.groupby('year').agg(
    muq_weighted=('weighted_muq', 'sum'),
    muq_median=('muq_gdp', 'median'),
    muq_mean=('muq_gdp', 'mean'),
    n_prov=('province_en', 'nunique')
).reset_index()

rprint('GDP-based MUQ (DeltaGDP/FAI), GDP-weighted national average:')
rprint(f'  {"Year":>6s} {"Weighted":>10s} {"Mean":>10s} {"Median":>10s} {"N_prov":>8s}')
for _, r in national_g.iterrows():
    rprint(f'  {int(r["year"]):>6d} {r["muq_weighted"]:>10.4f} {r["muq_mean"]:>10.4f} '
           f'{r["muq_median"]:>10.4f} {int(r["n_prov"]):>8d}')
rprint()

# Q=1 交叉年份
rprint('Q=1 交叉检测 (Housing MUQ):')
for i in range(1, len(national_h)):
    prev = national_h.iloc[i-1]['muq_weighted']
    curr = national_h.iloc[i]['muq_weighted']
    if (prev - 1) * (curr - 1) < 0:
        yr_prev = int(national_h.iloc[i-1]['year'])
        yr_curr = int(national_h.iloc[i]['year'])
        # 线性插值
        cross_yr = yr_prev + (1 - prev) / (curr - prev)
        rprint(f'  交叉于 {cross_yr:.1f} ({yr_prev}: {prev:.4f} -> {yr_curr}: {curr:.4f})')
if all(national_h['muq_weighted'] < 1):
    rprint(f'  全部年份 MUQ < 1 (最大值: {national_h["muq_weighted"].max():.4f})')
elif all(national_h['muq_weighted'] > 1):
    rprint(f'  全部年份 MUQ > 1 (最小值: {national_h["muq_weighted"].min():.4f})')
rprint()

# --- 5b. 分区域 MUQ 时序 ---
rprint('--- 5b. 分区域 MUQ 时序 (GDP-based, GDP-weighted) ---')
rprint()

for reg in ['East', 'Central', 'West']:
    ts_r = ts_g[ts_g['region'] == reg].copy()
    if len(ts_r) == 0:
        continue
    ts_r['weight'] = ts_r.groupby('year')['gdp_billion_yuan'].transform(lambda x: x / x.sum())
    ts_r['weighted_muq'] = ts_r['muq_gdp'] * ts_r['weight']
    reg_ts = ts_r.groupby('year')['weighted_muq'].sum().reset_index()
    rprint(f'{reg}:')
    vals = []
    for _, r in reg_ts.iterrows():
        vals.append(f'{int(r["year"])}:{r["weighted_muq"]:.3f}')
    # 每行5个年份
    for i in range(0, len(vals), 5):
        rprint(f'  {", ".join(vals[i:i+5])}')
    rprint()

# --- 5c. 分区域 Housing MUQ 时序 ---
rprint('--- 5c. 分区域 Housing MUQ 时序 (GDP-weighted) ---')
rprint()

for reg in ['East', 'Central', 'West']:
    ts_r = ts_h[ts_h['region'] == reg].copy()
    if len(ts_r) == 0:
        continue
    ts_r['weight'] = ts_r.groupby('year')['gdp_billion_yuan'].transform(lambda x: x / x.sum())
    ts_r['weighted_muq'] = ts_r['muq_housing'] * ts_r['weight']
    reg_ts = ts_r.groupby('year')['weighted_muq'].sum().reset_index()
    rprint(f'{reg}:')
    vals = []
    for _, r in reg_ts.iterrows():
        vals.append(f'{int(r["year"])}:{r["weighted_muq"]:.3f}')
    for i in range(0, len(vals), 5):
        rprint(f'  {", ".join(vals[i:i+5])}')
    rprint()

# =============================================================================
# 6. 扩展 MUQ 到 2020-2023 (仅使用 DeltaV, 无 FAI)
# =============================================================================
rprint('=' * 80)
rprint('第五部分: 2020-2023 Urban Q 时序 (FAI 缺失期)')
rprint('=' * 80)
rprint()
rprint('注: 2020-2023 FAI 缺失，无法计算 MUQ，但可使用 urban_q = V/K 观察趋势')
rprint()

q_ts = df[df['urban_q'].notna()].copy()
q_ts['weight'] = q_ts.groupby('year')['gdp_billion_yuan'].transform(lambda x: x / x.sum())
q_ts['weighted_q'] = q_ts['urban_q'] * q_ts['weight']
national_q = q_ts.groupby('year').agg(
    q_weighted=('weighted_q', 'sum'),
    q_median=('urban_q', 'median'),
    q_mean=('urban_q', 'mean'),
    n_prov=('province_en', 'nunique')
).reset_index()

rprint('Urban Q (V/K), GDP-weighted national average:')
rprint(f'  {"Year":>6s} {"Weighted":>10s} {"Mean":>10s} {"Median":>10s} {"N_prov":>8s}')
for _, r in national_q.iterrows():
    rprint(f'  {int(r["year"]):>6d} {r["q_weighted"]:>10.4f} {r["q_mean"]:>10.4f} '
           f'{r["q_median"]:>10.4f} {int(r["n_prov"]):>8d}')
rprint()

# Q=1 交叉
rprint('Q=1 交叉检测 (Average Q = V/K):')
for i in range(1, len(national_q)):
    prev = national_q.iloc[i-1]['q_weighted']
    curr = national_q.iloc[i]['q_weighted']
    if (prev - 1) * (curr - 1) < 0:
        yr_prev = int(national_q.iloc[i-1]['year'])
        yr_curr = int(national_q.iloc[i]['year'])
        cross_yr = yr_prev + (1 - prev) / (curr - prev)
        rprint(f'  交叉于 {cross_yr:.1f} ({yr_prev}: {prev:.4f} -> {yr_curr}: {curr:.4f})')
rprint()

# 分区域 Q 时序
rprint('分区域 Urban Q (V/K) 时序:')
for reg in ['East', 'Central', 'West']:
    ts_r = q_ts[q_ts['region'] == reg].copy()
    ts_r['weight'] = ts_r.groupby('year')['gdp_billion_yuan'].transform(lambda x: x / x.sum())
    ts_r['weighted_q'] = ts_r['urban_q'] * ts_r['weight']
    reg_ts = ts_r.groupby('year')['weighted_q'].sum().reset_index()
    rprint(f'  {reg}:')
    vals = []
    for _, r in reg_ts.iterrows():
        vals.append(f'{int(r["year"])}:{r["weighted_q"]:.3f}')
    for i in range(0, len(vals), 5):
        rprint(f'    {", ".join(vals[i:i+5])}')
rprint()

# =============================================================================
# 7. 标度律分析
# =============================================================================
rprint('=' * 80)
rprint('第六部分: 省级标度律分析')
rprint('=' * 80)
rprint()
rprint('截面标度律: ln(Y) ~ alpha + beta * ln(Pop)')
rprint('每年分别估计，报告 beta 的中位数和范围')
rprint()

# 需要 V, GDP, K, Pop 都有值
scale_data = df[df['V_billion'].notna() & (df['total_pop_10k'] > 0) &
                (df['gdp_billion_yuan'] > 0) & (df['K_billion'] > 0)].copy()
scale_data['ln_pop'] = np.log(scale_data['total_pop_10k'])
scale_data['ln_V'] = np.log(scale_data['V_billion'])
scale_data['ln_GDP'] = np.log(scale_data['gdp_billion_yuan'])
scale_data['ln_K'] = np.log(scale_data['K_billion'])

# 面积数据
scale_data['ln_area'] = np.log(scale_data['per_capita_area_m2'])

rprint(f'标度律样本: {len(scale_data)} 观测, '
       f'{scale_data["year"].min()}-{scale_data["year"].max()}')
rprint()

# 逐年截面回归
scaling_results = {}
for dep, dep_label in [('ln_V', 'ln(V)'), ('ln_GDP', 'ln(GDP)'), ('ln_K', 'ln(K)')]:
    betas = []
    for yr in sorted(scale_data['year'].unique()):
        sub = scale_data[scale_data['year'] == yr]
        if len(sub) < 10:
            continue
        X = sm.add_constant(sub['ln_pop'])
        y = sub[dep]
        m = sm.OLS(y, X).fit()
        betas.append({
            'year': yr,
            'beta': m.params['ln_pop'],
            'se': m.bse['ln_pop'],
            'pval': m.pvalues['ln_pop'],
            'r2': m.rsquared,
            'n': len(sub)
        })
    if betas:
        bdf = pd.DataFrame(betas)
        scaling_results[dep] = bdf
        med_beta = bdf['beta'].median()
        mean_beta = bdf['beta'].mean()
        min_beta = bdf['beta'].min()
        max_beta = bdf['beta'].max()
        rprint(f'{dep_label} ~ ln(Pop):')
        rprint(f'  beta 中位数 = {med_beta:.4f}, 均值 = {mean_beta:.4f}')
        rprint(f'  beta 范围 = [{min_beta:.4f}, {max_beta:.4f}]')
        rprint(f'  逐年结果:')
        for _, r in bdf.iterrows():
            sig = '***' if r['pval'] < 0.001 else ('**' if r['pval'] < 0.01 else ('*' if r['pval'] < 0.05 else ''))
            rprint(f'    {int(r["year"])}: beta={r["beta"]:.4f} (SE={r["se"]:.4f}), R2={r["r2"]:.3f}, N={int(r["n"])} {sig}')
        rprint()

# Pooled 标度律 (with year FE)
rprint('--- Pooled 标度律 (year FE) ---')
rprint()
for dep, dep_label in [('ln_V', 'ln(V)'), ('ln_GDP', 'ln(GDP)'), ('ln_K', 'ln(K)')]:
    year_dummies = pd.get_dummies(scale_data['year'], prefix='yr', drop_first=True, dtype=float)
    X = pd.concat([sm.add_constant(scale_data[['ln_pop']].reset_index(drop=True)),
                    year_dummies.reset_index(drop=True)], axis=1)
    y = scale_data[dep].reset_index(drop=True)
    m = sm.OLS(y.astype(float), X.astype(float)).fit(cov_type='HC1')
    b = m.params['ln_pop']
    s = m.bse['ln_pop']
    ci = m.conf_int().loc['ln_pop']
    rprint(f'{dep_label}: beta = {b:.4f} (SE={s:.4f}), 95% CI [{ci[0]:.4f}, {ci[1]:.4f}], '
           f'p={m.pvalues["ln_pop"]:.4e}, N={int(m.nobs)}')

rprint()

# beta_V 分解: beta_V = 1 + beta_A + beta_P
# V = Urban_Pop * per_capita_area * avg_house_price
rprint('--- beta_V 分解 ---')
rprint()
rprint('V = Urban_Pop * per_capita_area * avg_house_price')
rprint('ln(V) ~ beta_V * ln(Pop)')
rprint('分解: beta_V = 1 + beta_A + beta_P')
rprint('  其中 beta_A = d(ln(per_capita_area))/d(ln(Pop))')
rprint('  beta_P = d(ln(avg_house_price))/d(ln(Pop))')
rprint()

decomp_data = scale_data[scale_data['avg_house_price'].notna() &
                          (scale_data['avg_house_price'] > 0)].copy().reset_index(drop=True)
decomp_data['ln_price'] = np.log(decomp_data['avg_house_price'])

# Pooled with year FE
for dep, dep_label in [('ln_area', 'ln(per_capita_area)'), ('ln_price', 'ln(house_price)')]:
    year_dummies = pd.get_dummies(decomp_data['year'], prefix='yr', drop_first=True, dtype=float)
    X = pd.concat([sm.add_constant(decomp_data[['ln_pop']]), year_dummies], axis=1)
    y = decomp_data[dep]
    m = sm.OLS(y.astype(float), X.astype(float)).fit(cov_type='HC1')
    b = m.params['ln_pop']
    s = m.bse['ln_pop']
    ci = m.conf_int().loc['ln_pop']
    rprint(f'{dep_label}: beta = {b:.4f} (SE={s:.4f}), 95% CI [{ci[0]:.4f}, {ci[1]:.4f}], '
           f'p={m.pvalues["ln_pop"]:.4e}')

# 从 V 的 pooled 结果获取 beta_V
year_dummies_v = pd.get_dummies(decomp_data['year'], prefix='yr', drop_first=True, dtype=float)
X_v = pd.concat([sm.add_constant(decomp_data[['ln_pop']]), year_dummies_v], axis=1)
y_v = np.log(decomp_data['V_billion'])
m_v = sm.OLS(y_v.astype(float), X_v.astype(float)).fit(cov_type='HC1')
beta_V = m_v.params['ln_pop']
rprint(f'\nbeta_V (from V regression) = {beta_V:.4f}')
rprint(f'隐含分解: beta_V = 1 + beta_A + beta_P')

# 获取 beta_A 和 beta_P
X_a = pd.concat([sm.add_constant(decomp_data[['ln_pop']]), year_dummies_v], axis=1)
m_a = sm.OLS(decomp_data['ln_area'].astype(float), X_a.astype(float)).fit(cov_type='HC1')
m_p = sm.OLS(decomp_data['ln_price'].astype(float), X_a.astype(float)).fit(cov_type='HC1')
beta_A = m_a.params['ln_pop']
beta_P = m_p.params['ln_pop']
rprint(f'  1 + beta_A + beta_P = 1 + {beta_A:.4f} + {beta_P:.4f} = {1 + beta_A + beta_P:.4f}')
rprint(f'  (直接估计 beta_V = {beta_V:.4f}, 差异 = {beta_V - (1 + beta_A + beta_P):.4f})')
rprint()
rprint('  注意: per_capita_area_m2 是全国均值，各省同一年份无截面差异，')
rprint('  因此 beta_A 趋近 0。分解主要由 beta_P (房价弹性) 驱动。')
rprint('  V 的截面差异主要来自 人口规模 和 房价 两个维度。')
rprint()

# beta_V > 1 的解读
if beta_V > 1:
    rprint(f'beta_V = {beta_V:.4f} > 1: 住房价值对人口的弹性大于1 (超线性)')
    rprint('含义: 大省的住房价值增长比人口增长更快 → 集聚溢价')
else:
    rprint(f'beta_V = {beta_V:.4f} <= 1: 住房价值对人口的弹性不超过1 (次线性或线性)')
    rprint('含义: 省级数据中住房价值与人口近似线性，集聚溢价不如城市级明显')
    rprint('  (城市级 beta_V 通常 > 1，因为城市间房价差异远大于省份间)')
rprint()

# =============================================================================
# 8. 省级面板优势总结
# =============================================================================
rprint('=' * 80)
rprint('第七部分: 省级面板的关键优势')
rprint('=' * 80)
rprint()

# FAI 覆盖检查
fai_valid = df[df['fai_billion_yuan'].notna()]
v_valid = df[df['V_billion'].notna()]
q_valid = df[df['urban_q'].notna()]

rprint(f'数据覆盖:')
rprint(f'  总观测: {len(df)} (31省 x 19年)')
rprint(f'  FAI 有效: {len(fai_valid)} 观测 ({fai_valid["year"].min()}-{fai_valid["year"].max()})')
rprint(f'  V_billion 有效: {len(v_valid)} 观测 ({v_valid["year"].min()}-{v_valid["year"].max()})')
rprint(f'  Urban Q 有效: {len(q_valid)} 观测 ({q_valid["year"].min()}-{q_valid["year"].max()})')
rprint()

# 插值与真实数据比例
actual = df[df['data_type'] == 'actual']
interp = df[df['data_type'] == 'interpolated']
rprint(f'数据类型:')
rprint(f'  实际数据: {len(actual)} ({len(actual)/len(df)*100:.1f}%)')
rprint(f'  插值数据: {len(interp)} ({len(interp)/len(df)*100:.1f}%)')
rprint()

# 面板平衡性
obs_per_prov = df.groupby('province_en')['year'].count()
rprint(f'面板平衡性:')
rprint(f'  每省观测数: min={obs_per_prov.min()}, max={obs_per_prov.max()}, '
       f'mean={obs_per_prov.mean():.1f}')
rprint(f'  完全平衡: {"是" if obs_per_prov.min() == obs_per_prov.max() else "否"}')
rprint()

# FAI 为真实统计数据（非估算）
rprint('FAI 数据质量:')
rprint('  省级 FAI 来自国家统计局固定资产投资统计，为真实报告数据')
rprint('  城市级 FAI 常需从省级按比例估算，存在测量误差')
rprint('  省级面板消除了这一估算偏差来源')
rprint()

# 2020-2023 房地产危机覆盖
crisis_q = df[(df['year'] >= 2020) & (df['urban_q'].notna())]
rprint(f'2020-2023 房地产危机期覆盖:')
rprint(f'  有效 Urban Q 观测: {len(crisis_q)} ({crisis_q["province_en"].nunique()} 省)')
if len(crisis_q) > 0:
    crisis_mean = crisis_q.groupby('year')['urban_q'].mean()
    for yr, val in crisis_mean.items():
        rprint(f'    {yr}: mean Q = {val:.4f}')
rprint()

# =============================================================================
# 9. 保存输出
# =============================================================================

# 保存 MUQ 数据
out_cols = ['province', 'province_en', 'year', 'region', 'data_type',
            'gdp_billion_yuan', 'urbanization_rate_pct', 'fai_billion_yuan',
            'avg_house_price', 'total_pop_10k', 'per_capita_area_m2',
            'V_billion', 'K_billion', 'urban_q',
            'delta_V', 'delta_GDP', 'muq_housing', 'muq_gdp',
            'pc_gdp', 'deltaV_gdp', 'fai_gdp']
out_df = df[[c for c in out_cols if c in df.columns]]
out_df.to_csv(MUQ_CSV_PATH, index=False)
rprint(f'MUQ 数据已保存: {MUQ_CSV_PATH}')
rprint(f'  列: {list(out_df.columns)}')
rprint(f'  行数: {len(out_df)}')
rprint()

# 保存报告
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

print(f'\n报告已保存: {REPORT_PATH}')
print('分析完成.')
