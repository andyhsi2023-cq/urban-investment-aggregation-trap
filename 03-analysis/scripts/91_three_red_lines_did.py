"""
三道红线政策的双重差分准自然实验
=================================
目的: 利用2020年8月三道红线政策作为准自然实验，
      检验"过度投资导致 Q 下降"的因果方向。
输入: 02-data/processed/china_city_panel_real.csv
输出:
  - 03-analysis/models/three_red_lines_did_report.txt
  - 04-figures/drafts/fig_three_red_lines_did.png
  - 03-analysis/sensitivity/three_red_lines_source_data.csv
依赖: pandas, numpy, statsmodels, scipy, matplotlib
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from scipy.stats import norm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as mticker

# ============================================================
# 0. 路径与随机种子
# ============================================================
PROJECT = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
DATA_PATH = os.path.join(PROJECT, '02-data/processed/china_city_panel_real.csv')
REPORT_PATH = os.path.join(PROJECT, '03-analysis/models/three_red_lines_did_report.txt')
FIGURE_PATH = os.path.join(PROJECT, '04-figures/drafts/fig_three_red_lines_did.png')
SOURCE_DATA_PATH = os.path.join(PROJECT, '03-analysis/sensitivity/three_red_lines_source_data.csv')

np.random.seed(42)

# 报告缓冲区
report_lines = []
def rprint(s=''):
    """同时打印和记录到报告"""
    print(s)
    report_lines.append(str(s))

# ============================================================
# 1. 数据加载与预处理
# ============================================================
rprint('=' * 70)
rprint('三道红线政策 DID 准自然实验')
rprint('Three Red Lines Policy — Difference-in-Differences')
rprint('=' * 70)
rprint()

df = pd.read_csv(DATA_PATH)
rprint(f'原始数据: {len(df)} 行, {df["city"].nunique()} 城市, '
       f'年份 {df["year"].min()}-{df["year"].max()}')

# 聚焦 2017-2023
panel = df[df['year'].between(2017, 2023)].copy()
rprint(f'分析样本 (2017-2023): {len(panel)} 行, {panel["city"].nunique()} 城市')

# ============================================================
# 1a. 构建处理强度变量: 政策前房地产依赖度
# ============================================================
pre_period = panel[panel['year'].between(2017, 2019)].copy()

# RE_dependence = mean(re_invest / gdp) for 2017-2019
pre_period['re_dep'] = pre_period['re_invest_100m'] / pre_period['gdp_100m']
city_re_dep = pre_period.groupby('city')['re_dep'].mean().reset_index()
city_re_dep.columns = ['city', 'RE_dep']

# 对于缺失 re_invest 但有 re_gdp_ratio 的城市，用 re_gdp_ratio 补充
pre_ratio = pre_period.groupby('city')['re_gdp_ratio'].mean().reset_index()
pre_ratio.columns = ['city', 're_gdp_ratio_mean']
city_re_dep = city_re_dep.merge(pre_ratio, on='city', how='outer')
city_re_dep['RE_dep'] = city_re_dep['RE_dep'].fillna(city_re_dep['re_gdp_ratio_mean'])
city_re_dep = city_re_dep.drop(columns=['re_gdp_ratio_mean'])

n_valid = city_re_dep['RE_dep'].notna().sum()
rprint(f'有效 RE_dep 城市数: {n_valid}')
rprint(f'RE_dep 描述统计:')
desc = city_re_dep['RE_dep'].describe()
for k, v in desc.items():
    rprint(f'  {k}: {v:.4f}')
rprint()

# Winsorize RE_dep at 1%/99%
lo, hi = city_re_dep['RE_dep'].quantile([0.01, 0.99])
city_re_dep['RE_dep'] = city_re_dep['RE_dep'].clip(lo, hi)

# 标准化 (z-score)
re_mean = city_re_dep['RE_dep'].mean()
re_std = city_re_dep['RE_dep'].std()
city_re_dep['RE_dep_z'] = (city_re_dep['RE_dep'] - re_mean) / re_std

# 二元分组: 中位数切分
median_re = city_re_dep['RE_dep'].median()
city_re_dep['high_dep'] = (city_re_dep['RE_dep'] >= median_re).astype(int)
rprint(f'RE_dep 中位数: {median_re:.4f}')
rprint(f'高依赖组: {city_re_dep["high_dep"].sum()} 城市, '
       f'低依赖组: {(1 - city_re_dep["high_dep"]).sum()} 城市')

# 四分位分组 (仅对非缺失)
valid_mask = city_re_dep['RE_dep'].notna()
city_re_dep.loc[valid_mask, 'RE_dep_q4'] = pd.qcut(
    city_re_dep.loc[valid_mask, 'RE_dep'].rank(method='first'),
    4, labels=[1, 2, 3, 4]).astype(int)
city_re_dep['RE_dep_q4'] = city_re_dep['RE_dep_q4'].astype('Int64')
rprint(f'四分位分组: {city_re_dep["RE_dep_q4"].value_counts().sort_index().to_dict()}')
rprint()

# ============================================================
# 1b. 合并处理变量，构建分析面板
# ============================================================
panel = panel.merge(city_re_dep[['city', 'RE_dep', 'RE_dep_z', 'high_dep', 'RE_dep_q4']],
                    on='city', how='left')

# 排除 RE_dep 缺失的城市
panel = panel[panel['RE_dep'].notna()].copy()
rprint(f'合并后有效样本: {len(panel)} 行, {panel["city"].nunique()} 城市')

# ============================================================
# 1c. 构建分析变量
# ============================================================
# 时间变量
panel['post'] = (panel['year'] >= 2021).astype(int)
panel['transition'] = (panel['year'] == 2020).astype(int)

# 因变量: ln(house_price), urban_q
panel['ln_hp'] = np.log(panel['house_price'])

# 相对于2019年的变化
hp_2019 = panel[panel['year'] == 2019][['city', 'house_price', 'urban_q', 'ln_hp']].copy()
hp_2019.columns = ['city', 'hp_2019', 'q_2019', 'ln_hp_2019']
panel = panel.merge(hp_2019, on='city', how='left')
panel['delta_ln_hp'] = panel['ln_hp'] - panel['ln_hp_2019']
panel['delta_q'] = panel['urban_q'] - panel['q_2019']

# 控制变量
panel['gdp_growth'] = panel.groupby('city')['gdp_100m'].pct_change()
panel['fiscal_self'] = panel['fiscal_revenue_100m'] / panel['fiscal_expenditure_100m']
panel['pop_growth'] = panel.groupby('city')['pop_10k'].pct_change()
panel['debt_gdp'] = panel['total_bond_balance'] / panel['gdp_100m']

# Winsorize 所有连续变量 at 1%/99%
winsor_vars = ['ln_hp', 'urban_q', 'delta_ln_hp', 'delta_q',
               'gdp_growth', 'fiscal_self', 'pop_growth', 'debt_gdp']
for var in winsor_vars:
    if var in panel.columns:
        lo_v, hi_v = panel[var].quantile([0.01, 0.99])
        panel[var] = panel[var].clip(lo_v, hi_v)

# DID 交互项
panel['post_x_RE_dep_z'] = panel['post'] * panel['RE_dep_z']
panel['post_x_high_dep'] = panel['post'] * panel['high_dep']

# 省份编码
panel['province_code'] = pd.Categorical(panel['province']).codes

# 城市数值编码 (用于固定效应)
panel['city_id'] = pd.Categorical(panel['city']).codes

rprint(f'最终分析面板: {len(panel)} 行, {panel["city"].nunique()} 城市, '
       f'{panel["year"].nunique()} 年')
rprint()

# ============================================================
# 2. 描述性统计
# ============================================================
rprint('=' * 70)
rprint('2. 描述性统计: 高/低依赖组比较')
rprint('=' * 70)
rprint()

for period_name, mask in [('政策前 (2017-2019)', panel['year'].between(2017, 2019)),
                           ('政策后 (2021-2023)', panel['year'].between(2021, 2023))]:
    rprint(f'--- {period_name} ---')
    sub = panel[mask]
    for dep_name, dep_mask in [('高依赖', sub['high_dep'] == 1),
                                ('低依赖', sub['high_dep'] == 0)]:
        s = sub[dep_mask]
        rprint(f'  {dep_name} (N={s["city"].nunique()} 城市):')
        rprint(f'    房价均值: {s["house_price"].mean():.0f} 元/m2')
        rprint(f'    Q 均值:   {s["urban_q"].mean():.4f}')
        rprint(f'    GDP均值:  {s["gdp_100m"].mean():.1f} 亿元')
        rprint(f'    RE_dep:   {s["RE_dep"].mean():.4f}')
    rprint()

# ============================================================
# 辅助函数: OLS with clustered SE
# ============================================================
def run_ols_cluster(y, X, cluster_var, panel_df):
    """
    OLS回归，城市级聚类标准误。
    返回 (model_result, summary_string)
    """
    mask = y.notna() & X.notna().all(axis=1) & cluster_var.notna()
    y_c, X_c, cl_c = y[mask], X[mask], cluster_var[mask]

    model = sm.OLS(y_c, sm.add_constant(X_c))
    # 使用 HC1 聚类标准误
    result = model.fit(cov_type='cluster', cov_kwds={'groups': cl_c})
    return result


def format_result_table(result, var_names=None):
    """格式化回归结果为文本表格"""
    lines = []
    params = result.params
    bse = result.bse
    tvals = result.tvalues
    pvals = result.pvalues
    ci = result.conf_int()

    lines.append(f'{"Variable":<25} {"Coef":>10} {"SE":>10} {"t":>8} {"p":>10} {"95% CI":>24}')
    lines.append('-' * 90)
    for i, name in enumerate(params.index):
        display_name = var_names[i] if var_names and i < len(var_names) else name
        ci_str = f'[{ci.iloc[i, 0]:.4f}, {ci.iloc[i, 1]:.4f}]'
        lines.append(f'{display_name:<25} {params.iloc[i]:>10.4f} {bse.iloc[i]:>10.4f} '
                     f'{tvals.iloc[i]:>8.3f} {pvals.iloc[i]:>10.6f} {ci_str:>24}')
    lines.append('-' * 90)
    lines.append(f'N = {int(result.nobs)}, R2 = {result.rsquared:.4f}, '
                 f'Adj-R2 = {result.rsquared_adj:.4f}')
    return '\n'.join(lines)


# ============================================================
# 3. Design 1: 连续 DID (主分析)
# ============================================================
rprint('=' * 70)
rprint('3. Design 1: 连续 DID (Continuous Treatment Intensity)')
rprint('=' * 70)
rprint()

# 排除2020年 (过渡年)
did_panel = panel[panel['year'] != 2020].copy()

# --- 3a. 因变量 = ln(house_price) ---
rprint('--- 3a. 因变量: ln(房价) ---')

# 省份固定效应哑变量
province_dummies = pd.get_dummies(did_panel['province'], prefix='prov', drop_first=True).astype(float)

# 年份哑变量
year_dummies = pd.get_dummies(did_panel['year'], prefix='yr', drop_first=True).astype(float)

# 基础模型: 无控制变量, 无年份FE (仅 post 吸收时间趋势)
X_base = did_panel[['post', 'RE_dep_z', 'post_x_RE_dep_z']].copy()

res_hp_base = run_ols_cluster(
    did_panel['ln_hp'], X_base, did_panel['city_id'], did_panel)

rprint('模型 1: 基础模型 (无控制变量, 无FE)')
rprint(format_result_table(res_hp_base))
rprint()

# 含控制变量模型 (年份FE 吸收 post, 故不单独放 post)
controls = ['gdp_growth', 'fiscal_self', 'pop_growth', 'debt_gdp']
X_ctrl = did_panel[['RE_dep_z', 'post_x_RE_dep_z'] + controls].copy()
X_ctrl = pd.concat([X_ctrl, province_dummies, year_dummies], axis=1)

res_hp_ctrl = run_ols_cluster(
    did_panel['ln_hp'], X_ctrl, did_panel['city_id'], did_panel)

rprint('模型 2: 含控制变量 + 省份固定效应')
# 只显示核心变量
rprint(format_result_table(res_hp_ctrl))
rprint()

# --- 3b. 因变量 = urban_q ---
rprint('--- 3b. 因变量: Urban Q ---')

X_q = did_panel[['RE_dep_z', 'post_x_RE_dep_z'] + controls].copy()
X_q = pd.concat([X_q, province_dummies, year_dummies], axis=1)

res_q_ctrl = run_ols_cluster(
    did_panel['urban_q'], X_q, did_panel['city_id'], did_panel)

rprint('模型 3: 因变量 Urban Q, 含控制变量 + 省份FE')
rprint(format_result_table(res_q_ctrl))
rprint()

# --- 3c. 城市固定效应模型 (更严格) ---
rprint('--- 3c. 城市固定效应模型 (Two-Way FE) ---')

# 使用去均值法 (within estimator) 代替大量哑变量
# 对城市做组内去均值
def demean_by_group(df, vars_list, group_col):
    """组内去均值 (within transformation)"""
    result = df[vars_list].copy()
    groups = df[group_col]
    for var in vars_list:
        group_means = df.groupby(group_col)[var].transform('mean')
        result[var] = df[var] - group_means
    return result

fe_vars = ['ln_hp', 'urban_q', 'post', 'RE_dep_z', 'post_x_RE_dep_z'] + controls
fe_panel = did_panel[['city_id', 'year'] + fe_vars].dropna().copy()

# 城市去均值
demeaned = demean_by_group(fe_panel, fe_vars, 'city_id')

# 年份去均值 (two-way)
for var in fe_vars:
    yr_mean = fe_panel.groupby('year')[var].transform('mean')
    city_mean = fe_panel.groupby('city_id')[var].transform('mean')
    grand_mean = fe_panel[var].mean()
    demeaned[var] = fe_panel[var] - city_mean - yr_mean + grand_mean

# TWFE: 因变量 ln_hp
X_twfe = demeaned[['post_x_RE_dep_z'] + controls]
res_hp_twfe = sm.OLS(demeaned['ln_hp'], sm.add_constant(X_twfe)).fit(
    cov_type='cluster', cov_kwds={'groups': fe_panel['city_id']})

rprint('模型 4: TWFE ln(房价) ~ Post x RE_dep_z')
rprint(format_result_table(res_hp_twfe))
rprint()

# TWFE: 因变量 urban_q
res_q_twfe = sm.OLS(demeaned['urban_q'], sm.add_constant(X_twfe)).fit(
    cov_type='cluster', cov_kwds={'groups': fe_panel['city_id']})

rprint('模型 5: TWFE Urban Q ~ Post x RE_dep_z')
rprint(format_result_table(res_q_twfe))
rprint()

# ============================================================
# 3d. 核心结果汇总
# ============================================================
rprint('--- 核心结果汇总 ---')
for name, res, dv in [
    ('Model 1 (Base, ln_hp)', res_hp_base, 'ln(HP)'),
    ('Model 2 (Ctrl+ProvFE, ln_hp)', res_hp_ctrl, 'ln(HP)'),
    ('Model 3 (Ctrl+ProvFE, Q)', res_q_ctrl, 'Q'),
    ('Model 4 (TWFE, ln_hp)', res_hp_twfe, 'ln(HP)'),
    ('Model 5 (TWFE, Q)', res_q_twfe, 'Q'),
]:
    # 找到 post_x_RE_dep_z 系数
    if 'post_x_RE_dep_z' in res.params.index:
        coef = res.params['post_x_RE_dep_z']
        se = res.bse['post_x_RE_dep_z']
        p = res.pvalues['post_x_RE_dep_z']
        ci = res.conf_int().loc['post_x_RE_dep_z']
        rprint(f'  {name}: beta_DID = {coef:.4f} (SE={se:.4f}), '
               f'p = {p:.6f}, 95%CI [{ci[0]:.4f}, {ci[1]:.4f}]')
rprint()

# ============================================================
# 4. Design 2: 二元 DID
# ============================================================
rprint('=' * 70)
rprint('4. Design 2: 二元 DID (Binary Treatment)')
rprint('=' * 70)
rprint()

X_bin = did_panel[['high_dep', 'post_x_high_dep'] + controls].copy()
X_bin = pd.concat([X_bin, province_dummies, year_dummies], axis=1)

# ln(HP)
res_bin_hp = run_ols_cluster(did_panel['ln_hp'], X_bin, did_panel['city_id'], did_panel)
rprint('模型 6: 二元 DID, ln(房价)')
coef = res_bin_hp.params['post_x_high_dep']
se = res_bin_hp.bse['post_x_high_dep']
p = res_bin_hp.pvalues['post_x_high_dep']
ci = res_bin_hp.conf_int().loc['post_x_high_dep']
rprint(f'  DID 系数: {coef:.4f} (SE={se:.4f}), p = {p:.6f}, '
       f'95%CI [{ci[0]:.4f}, {ci[1]:.4f}]')
rprint(f'  N = {int(res_bin_hp.nobs)}, R2 = {res_bin_hp.rsquared:.4f}')
rprint()

# Urban Q
res_bin_q = run_ols_cluster(did_panel['urban_q'], X_bin, did_panel['city_id'], did_panel)
rprint('模型 7: 二元 DID, Urban Q')
coef = res_bin_q.params['post_x_high_dep']
se = res_bin_q.bse['post_x_high_dep']
p = res_bin_q.pvalues['post_x_high_dep']
ci = res_bin_q.conf_int().loc['post_x_high_dep']
rprint(f'  DID 系数: {coef:.4f} (SE={se:.4f}), p = {p:.6f}, '
       f'95%CI [{ci[0]:.4f}, {ci[1]:.4f}]')
rprint(f'  N = {int(res_bin_q.nobs)}, R2 = {res_bin_q.rsquared:.4f}')
rprint()

# ============================================================
# 5. Design 3: 事件研究法 (Event Study)
# ============================================================
rprint('=' * 70)
rprint('5. Design 3: 事件研究法 (Event Study)')
rprint('=' * 70)
rprint()

# 以 2019 为参照年，估计每年的交互系数
es_panel = panel.copy()  # 包含2020
ref_year = 2019
years_all = sorted(es_panel['year'].unique())

# 构建交互项: RE_dep_z * Year_t (除参照年)
for yr in years_all:
    if yr != ref_year:
        es_panel[f'RE_dep_x_{yr}'] = es_panel['RE_dep_z'] * (es_panel['year'] == yr).astype(int)

interact_vars = [f'RE_dep_x_{yr}' for yr in years_all if yr != ref_year]

# 省份 + 年份固定效应
prov_dum = pd.get_dummies(es_panel['province'], prefix='prov', drop_first=True).astype(float)
yr_dum = pd.get_dummies(es_panel['year'], prefix='yr', drop_first=True).astype(float)

# 事件研究: ln(HP)
X_es = es_panel[interact_vars + controls].copy()
X_es = pd.concat([X_es, prov_dum, yr_dum], axis=1)

res_es_hp = run_ols_cluster(es_panel['ln_hp'], X_es, es_panel['city_id'], es_panel)

rprint('事件研究: ln(房价)')
es_results_hp = []
for yr in years_all:
    if yr == ref_year:
        es_results_hp.append({'year': yr, 'coef': 0, 'se': 0, 'ci_lo': 0, 'ci_hi': 0, 'p': np.nan})
    else:
        var = f'RE_dep_x_{yr}'
        coef = res_es_hp.params[var]
        se = res_es_hp.bse[var]
        p = res_es_hp.pvalues[var]
        ci = res_es_hp.conf_int().loc[var]
        es_results_hp.append({'year': yr, 'coef': coef, 'se': se,
                              'ci_lo': ci[0], 'ci_hi': ci[1], 'p': p})
        rprint(f'  {yr}: beta = {coef:.4f} (SE={se:.4f}), p = {p:.6f}, '
               f'95%CI [{ci[0]:.4f}, {ci[1]:.4f}]')

es_df_hp = pd.DataFrame(es_results_hp)

# 事件研究: Urban Q
X_es_q = es_panel[interact_vars + controls].copy()
X_es_q = pd.concat([X_es_q, prov_dum, yr_dum], axis=1)

res_es_q = run_ols_cluster(es_panel['urban_q'], X_es_q, es_panel['city_id'], es_panel)

rprint()
rprint('事件研究: Urban Q')
es_results_q = []
for yr in years_all:
    if yr == ref_year:
        es_results_q.append({'year': yr, 'coef': 0, 'se': 0, 'ci_lo': 0, 'ci_hi': 0, 'p': np.nan})
    else:
        var = f'RE_dep_x_{yr}'
        coef = res_es_q.params[var]
        se = res_es_q.bse[var]
        p = res_es_q.pvalues[var]
        ci = res_es_q.conf_int().loc[var]
        es_results_q.append({'year': yr, 'coef': coef, 'se': se,
                              'ci_lo': ci[0], 'ci_hi': ci[1], 'p': p})
        rprint(f'  {yr}: beta = {coef:.4f} (SE={se:.4f}), p = {p:.6f}, '
               f'95%CI [{ci[0]:.4f}, {ci[1]:.4f}]')

es_df_q = pd.DataFrame(es_results_q)
rprint()

# 平行趋势检验: 联合检验政策前系数是否为零
rprint('--- 平行趋势检验 ---')
rprint('注: 以2019为参照年, 检验2017和2018的交互系数是否联合为零')
pre_vars_test = [f'RE_dep_x_{yr}' for yr in [2017, 2018]]

for name, res in [('ln(HP)', res_es_hp), ('Q', res_es_q)]:
    # 逐个检验
    for yr in [2017, 2018]:
        var = f'RE_dep_x_{yr}'
        if var in res.params.index:
            c = res.params[var]
            p = res.pvalues[var]
            rprint(f'  {name} {yr}: coef = {c:.4f}, p = {p:.4f}')

    # Joint F-test
    try:
        r_matrix = np.zeros((len(pre_vars_test), len(res.params)))
        for j, var in enumerate(pre_vars_test):
            idx = list(res.params.index).index(var)
            r_matrix[j, idx] = 1
        wald = res.wald_test(r_matrix)
        f_stat = float(np.array(wald.statistic).flat[0])
        f_p = float(np.array(wald.pvalue).flat[0])
        rprint(f'  {name} Joint F-test: F = {f_stat:.3f}, p = {f_p:.6f}')
        if f_p > 0.10:
            rprint(f'    -> 不能拒绝平行趋势假设 (p > 0.10)')
        elif f_p > 0.05:
            rprint(f'    -> 边际显著 (0.05 < p < 0.10), 平行趋势假设不完全满足')
        else:
            rprint(f'    -> 警告: 平行趋势假设不满足 (p < 0.05)')
    except Exception as e:
        rprint(f'  {name} Joint F-test 未能完成: {e}')
rprint()

# ============================================================
# 6. 机制检验: 政策后投资是否下降更多?
# ============================================================
rprint('=' * 70)
rprint('6. 机制检验: 三道红线是否导致高依赖城市投资降幅更大?')
rprint('=' * 70)
rprint()
rprint('注意: FAI 在2017+为估算值 (fai_imputed=True), re_invest 在2020+缺失')
rprint('因此机制检验的可靠性受限。此处仅作参考。')
rprint()

# 使用 FAI/GDP 作为投资指标 (re_invest 政策后不可用)
panel['fai_gdp'] = panel['fai_100m'] / panel['gdp_100m']
# Winsorize
lo_fg, hi_fg = panel['fai_gdp'].quantile([0.01, 0.99])
panel['fai_gdp'] = panel['fai_gdp'].clip(lo_fg, hi_fg)

mech_panel = panel[panel['year'] != 2020].copy()
prov_dum_m = pd.get_dummies(mech_panel['province'], prefix='prov', drop_first=True).astype(float)
yr_dum_m = pd.get_dummies(mech_panel['year'], prefix='yr', drop_first=True).astype(float)

X_mech = mech_panel[['post', 'RE_dep_z', 'post_x_RE_dep_z']].copy()
X_mech = pd.concat([X_mech, prov_dum_m, yr_dum_m], axis=1)

res_mech = run_ols_cluster(mech_panel['fai_gdp'], X_mech, mech_panel['city_id'], mech_panel)

rprint('因变量: FAI/GDP')
coef_m = res_mech.params['post_x_RE_dep_z']
se_m = res_mech.bse['post_x_RE_dep_z']
p_m = res_mech.pvalues['post_x_RE_dep_z']
ci_m = res_mech.conf_int().loc['post_x_RE_dep_z']
rprint(f'  DID 系数: {coef_m:.4f} (SE={se_m:.4f}), p = {p_m:.6f}, '
       f'95%CI [{ci_m[0]:.4f}, {ci_m[1]:.4f}]')
rprint(f'  N = {int(res_mech.nobs)}, R2 = {res_mech.rsquared:.4f}')
if coef_m < 0:
    rprint('  -> 高依赖城市政策后 FAI/GDP 降幅更大 (机制成立)')
else:
    rprint('  -> 高依赖城市政策后 FAI/GDP 未降更多 (机制不成立)')
rprint()

# 描述性: 高/低组 FAI/GDP 均值变化
rprint('描述性: 高/低依赖组 FAI/GDP 均值')
for period, mask in [('2017-2019', mech_panel['year'].between(2017, 2019)),
                      ('2021-2023', mech_panel['year'].between(2021, 2023))]:
    sub = mech_panel[mask]
    h = sub[sub['high_dep'] == 1]['fai_gdp'].mean()
    l = sub[sub['high_dep'] == 0]['fai_gdp'].mean()
    rprint(f'  {period}: 高依赖={h:.4f}, 低依赖={l:.4f}, 差异={h-l:.4f}')
rprint()

# ============================================================
# 7. 剂量-反应分析 (Dose-Response)
# ============================================================
rprint('=' * 70)
rprint('7. 剂量-反应分析 (四分位)')
rprint('=' * 70)
rprint()

dr_panel = panel[panel['year'] != 2020].copy()
# 以 Q1 (最低依赖) 为参照组
for q in [2, 3, 4]:
    dr_panel[f'q{q}'] = (dr_panel['RE_dep_q4'] == q).astype(int)
    dr_panel[f'post_x_q{q}'] = dr_panel['post'] * dr_panel[f'q{q}']

q_vars = [f'q{q}' for q in [2, 3, 4]] + [f'post_x_q{q}' for q in [2, 3, 4]]
prov_dum_dr = pd.get_dummies(dr_panel['province'], prefix='prov', drop_first=True).astype(float)
yr_dum_dr = pd.get_dummies(dr_panel['year'], prefix='yr', drop_first=True).astype(float)

X_dr = dr_panel[['post'] + q_vars + controls].copy()
X_dr = pd.concat([X_dr, prov_dum_dr, yr_dum_dr], axis=1)

# ln(HP)
res_dr_hp = run_ols_cluster(dr_panel['ln_hp'], X_dr, dr_panel['city_id'], dr_panel)

rprint('剂量-反应: ln(房价), 参照组 = Q1 (最低依赖)')
dr_results_hp = [{'quartile': 'Q1', 'coef': 0, 'se': 0, 'ci_lo': 0, 'ci_hi': 0, 'p': np.nan}]
for q in [2, 3, 4]:
    var = f'post_x_q{q}'
    coef = res_dr_hp.params[var]
    se = res_dr_hp.bse[var]
    p = res_dr_hp.pvalues[var]
    ci = res_dr_hp.conf_int().loc[var]
    dr_results_hp.append({'quartile': f'Q{q}', 'coef': coef, 'se': se,
                           'ci_lo': ci[0], 'ci_hi': ci[1], 'p': p})
    rprint(f'  Q{q} x Post: {coef:.4f} (SE={se:.4f}), p = {p:.6f}, '
           f'95%CI [{ci[0]:.4f}, {ci[1]:.4f}]')

dr_df_hp = pd.DataFrame(dr_results_hp)
rprint()

# Urban Q
res_dr_q = run_ols_cluster(dr_panel['urban_q'], X_dr, dr_panel['city_id'], dr_panel)

rprint('剂量-反应: Urban Q, 参照组 = Q1 (最低依赖)')
dr_results_q = [{'quartile': 'Q1', 'coef': 0, 'se': 0, 'ci_lo': 0, 'ci_hi': 0, 'p': np.nan}]
for q in [2, 3, 4]:
    var = f'post_x_q{q}'
    coef = res_dr_q.params[var]
    se = res_dr_q.bse[var]
    p = res_dr_q.pvalues[var]
    ci = res_dr_q.conf_int().loc[var]
    dr_results_q.append({'quartile': f'Q{q}', 'coef': coef, 'se': se,
                          'ci_lo': ci[0], 'ci_hi': ci[1], 'p': p})
    rprint(f'  Q{q} x Post: {coef:.4f} (SE={se:.4f}), p = {p:.6f}, '
           f'95%CI [{ci[0]:.4f}, {ci[1]:.4f}]')

dr_df_q = pd.DataFrame(dr_results_q)

# 检验趋势性: Q2 < Q3 < Q4? (线性递增)
rprint()
rprint('剂量-反应线性趋势检验:')
for name, res in [('ln(HP)', res_dr_hp), ('Q', res_dr_q)]:
    # 线性对比: -1*Q2 + 0*Q3 + 1*Q4
    r_matrix = np.zeros((1, len(res.params)))
    idx_q2 = list(res.params.index).index('post_x_q2')
    idx_q4 = list(res.params.index).index('post_x_q4')
    r_matrix[0, idx_q2] = -1
    r_matrix[0, idx_q4] = 1
    wald = res.wald_test(r_matrix)
    f_stat = wald.statistic[0][0] if hasattr(wald.statistic, '__getitem__') else wald.statistic
    f_p = float(wald.pvalue) if np.isscalar(wald.pvalue) else float(np.array(wald.pvalue).flat[0])
    rprint(f'  {name}: Q4-Q2 对比 F = {f_stat:.3f}, p = {f_p:.6f}')
rprint()

# ============================================================
# 8. Placebo 检验
# ============================================================
rprint('=' * 70)
rprint('8. Placebo 检验 (假政策时点 = 2017)')
rprint('=' * 70)
rprint()

# Placebo 设计: 2014-2015 vs 2017-2018, 假政策在2016年底
# (完全在真实政策2020之前, 不受真实政策污染)
# RE_dep 使用 2014-2015 的数据
placebo_full = df[df['year'].between(2014, 2018)].copy()
placebo_full['ln_hp'] = np.log(placebo_full['house_price'])

# 计算 2014-2015 的 RE_dep
pre_placebo = placebo_full[placebo_full['year'].between(2014, 2015)].copy()
pre_placebo['re_dep_p'] = pre_placebo['re_invest_100m'] / pre_placebo['gdp_100m']
city_re_dep_p = pre_placebo.groupby('city')['re_dep_p'].mean().reset_index()
city_re_dep_p.columns = ['city', 'RE_dep_placebo']

# Winsorize + standardize
valid_p = city_re_dep_p['RE_dep_placebo'].notna()
lo_p, hi_p = city_re_dep_p.loc[valid_p, 'RE_dep_placebo'].quantile([0.01, 0.99])
city_re_dep_p['RE_dep_placebo'] = city_re_dep_p['RE_dep_placebo'].clip(lo_p, hi_p)
pm = city_re_dep_p['RE_dep_placebo'].mean()
ps = city_re_dep_p['RE_dep_placebo'].std()
city_re_dep_p['RE_dep_p_z'] = (city_re_dep_p['RE_dep_placebo'] - pm) / ps

placebo_full = placebo_full.merge(city_re_dep_p[['city', 'RE_dep_p_z']], on='city', how='left')
placebo_full = placebo_full[placebo_full['RE_dep_p_z'].notna()]

# 排除2016 (假的过渡年)
placebo_did = placebo_full[placebo_full['year'] != 2016].copy()
placebo_did['post_p'] = (placebo_did['year'] >= 2017).astype(int)
placebo_did['post_x_RE_dep_p'] = placebo_did['post_p'] * placebo_did['RE_dep_p_z']
placebo_did['city_id_p'] = pd.Categorical(placebo_did['city']).codes

rprint(f'Placebo 样本: {len(placebo_did)} 行, {placebo_did["city"].nunique()} 城市')
rprint(f'  年份: {sorted(placebo_did["year"].unique())}')

# 省份 FE (年份FE 吸收 post_p)
prov_dum_p = pd.get_dummies(placebo_did['province'], prefix='prov', drop_first=True).astype(float)
yr_dum_p = pd.get_dummies(placebo_did['year'], prefix='yr', drop_first=True).astype(float)

X_placebo = placebo_did[['RE_dep_p_z', 'post_x_RE_dep_p']].copy()
X_placebo = pd.concat([X_placebo, prov_dum_p, yr_dum_p], axis=1)

# ln(HP)
res_placebo_hp = run_ols_cluster(
    placebo_did['ln_hp'], X_placebo, placebo_did['city_id_p'], placebo_did)

coef_plac = res_placebo_hp.params['post_x_RE_dep_p']
se_plac = res_placebo_hp.bse['post_x_RE_dep_p']
p_plac = res_placebo_hp.pvalues['post_x_RE_dep_p']
ci_plac = res_placebo_hp.conf_int().loc['post_x_RE_dep_p']

rprint(f'Placebo DID (2014-2015 vs 2017-2018, 假政策2016):')
rprint(f'  ln(HP): beta = {coef_plac:.4f} (SE={se_plac:.4f}), p = {p_plac:.6f}, '
       f'95%CI [{ci_plac[0]:.4f}, {ci_plac[1]:.4f}]')
if p_plac > 0.10:
    rprint(f'  -> Placebo 不显著 (p > 0.10), 支持真实效应的有效性')
else:
    rprint(f'  -> 警告: Placebo 显著 (p < 0.10), 需要谨慎解读主分析结果')
rprint()

# ============================================================
# 9. 异质性分析: 按城市等级
# ============================================================
rprint('=' * 70)
rprint('9. 异质性分析: 按城市规模分组')
rprint('=' * 70)
rprint()

# 使用2019年GDP划分城市等级 (替代行政层级)
gdp_2019 = df[df['year'] == 2019][['city', 'gdp_100m']].copy()
gdp_2019.columns = ['city', 'gdp_2019']

# 分为三组: 大城市 (top 25%), 中等 (25-75%), 小城市 (bottom 25%)
q25 = gdp_2019['gdp_2019'].quantile(0.25)
q75 = gdp_2019['gdp_2019'].quantile(0.75)
gdp_2019['city_size'] = pd.cut(gdp_2019['gdp_2019'],
                                 bins=[-np.inf, q25, q75, np.inf],
                                 labels=['小城市', '中等城市', '大城市'])

het_panel = did_panel.merge(gdp_2019[['city', 'city_size']], on='city', how='left')
het_panel = het_panel[het_panel['city_size'].notna()]

for size in ['小城市', '中等城市', '大城市']:
    sub = het_panel[het_panel['city_size'] == size]
    if len(sub) < 50:
        rprint(f'  {size}: 样本过少 ({len(sub)}), 跳过')
        continue

    prov_dum_h = pd.get_dummies(sub['province'], prefix='prov', drop_first=True).astype(float)
    yr_dum_h = pd.get_dummies(sub['year'], prefix='yr', drop_first=True).astype(float)
    X_h = sub[['post', 'RE_dep_z', 'post_x_RE_dep_z']].copy()
    X_h = pd.concat([X_h, prov_dum_h, yr_dum_h], axis=1)

    # ln(HP)
    res_h = run_ols_cluster(sub['ln_hp'], X_h, sub['city_id'], sub)
    if 'post_x_RE_dep_z' in res_h.params.index:
        coef_h = res_h.params['post_x_RE_dep_z']
        se_h = res_h.bse['post_x_RE_dep_z']
        p_h = res_h.pvalues['post_x_RE_dep_z']
        ci_h = res_h.conf_int().loc['post_x_RE_dep_z']
        rprint(f'  {size} ({sub["city"].nunique()} 城市): '
               f'beta_DID = {coef_h:.4f} (SE={se_h:.4f}), p = {p_h:.6f}, '
               f'95%CI [{ci_h[0]:.4f}, {ci_h[1]:.4f}]')
rprint()

# ============================================================
# 10. 结果解读
# ============================================================
rprint('=' * 70)
rprint('10. 结果解读')
rprint('=' * 70)
rprint()

# 主效应方向
main_coef = res_hp_ctrl.params.get('post_x_RE_dep_z', np.nan)
main_p = res_hp_ctrl.pvalues.get('post_x_RE_dep_z', np.nan)
main_q_coef = res_q_ctrl.params.get('post_x_RE_dep_z', np.nan)
main_q_p = res_q_ctrl.pvalues.get('post_x_RE_dep_z', np.nan)

rprint(f'主效应 ln(HP): beta = {main_coef:.4f}, p = {main_p:.6f}')
rprint(f'主效应 Q:      beta = {main_q_coef:.4f}, p = {main_q_p:.6f}')
rprint()

rprint('--- 因果假说检验 ---')
rprint()
rprint('假说 A ("过度投资有害"): 限制投资后，高依赖城市 Q 应止跌/回升')
rprint('  预测: beta_DID(Q) > 0')
rprint()
rprint('假说 B ("经济冲击"): 政策冲击直接打压高依赖城市房价')
rprint('  预测: beta_DID(Q) < 0, beta_DID(HP) < 0')
rprint()

if main_coef > 0 and main_p < 0.05:
    rprint('结论 [ln(HP)]: DID 交互项显著为正 (p < 0.05)')
    rprint('  高依赖城市政策后房价表现相对更好 — 支持假说A')
elif main_coef < 0 and main_p < 0.05:
    rprint('结论 [ln(HP)]: DID 交互项显著为负 (p < 0.05)')
    rprint('  高依赖城市政策后房价跌幅更大 — 支持假说B')
else:
    rprint(f'结论 [ln(HP)]: DID 交互项不显著 (p = {main_p:.4f})')
    rprint(f'  点估计方向: {"正" if main_coef > 0 else "负"}, 但统计上不能区分两个假说')
rprint()

if main_q_coef > 0 and main_q_p < 0.05:
    rprint('结论 [Q]: DID 交互项显著为正 (p < 0.05)')
    rprint('  高依赖城市政策后 Q 相对回升 — 强力支持假说A')
elif main_q_coef < 0 and main_q_p < 0.05:
    rprint('结论 [Q]: DID 交互项显著为负 (p < 0.05)')
    rprint('  高依赖城市政策后 Q 跌幅更大 — 支持假说B')
    rprint('  然而, 这并不排除假说A。两种机制可能同时存在:')
    rprint('  短期内政策冲击打压需求(V下降)和投资(K不变) -> Q下降')
    rprint('  长期效应需要更长的观察窗口才能显现')
else:
    rprint(f'结论 [Q]: DID 交互项不显著 (p = {main_q_p:.4f})')

rprint()
rprint('--- 附加诊断 ---')
rprint(f'TWFE 模型 [ln(HP)]: beta = {res_hp_twfe.params.get("post_x_RE_dep_z", np.nan):.4f}, '
       f'p = {res_hp_twfe.pvalues.get("post_x_RE_dep_z", np.nan):.6f}')
rprint(f'TWFE 模型 [Q]:      beta = {res_q_twfe.params.get("post_x_RE_dep_z", np.nan):.4f}, '
       f'p = {res_q_twfe.pvalues.get("post_x_RE_dep_z", np.nan):.6f}')
rprint(f'二元 DID [Q]:       beta = {res_bin_q.params.get("post_x_high_dep", np.nan):.4f}, '
       f'p = {res_bin_q.pvalues.get("post_x_high_dep", np.nan):.6f}')
rprint()
rprint('方向一致性: 所有规格下 Q 的 DID 系数方向是否一致?')
q_signs = [
    res_q_ctrl.params.get('post_x_RE_dep_z', np.nan),
    res_q_twfe.params.get('post_x_RE_dep_z', np.nan),
    res_bin_q.params.get('post_x_high_dep', np.nan),
]
if all(c < 0 for c in q_signs if not np.isnan(c)):
    rprint('  所有规格方向一致 (负): 方向性结论稳健')
elif all(c > 0 for c in q_signs if not np.isnan(c)):
    rprint('  所有规格方向一致 (正): 方向性结论稳健')
else:
    rprint('  规格间方向不一致: 需谨慎解读')
rprint()

# ============================================================
# 11. 图表
# ============================================================
rprint('=' * 70)
rprint('11. 生成图表')
rprint('=' * 70)

# 中文字体设置
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Heiti SC', 'SimHei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

fig = plt.figure(figsize=(16, 14))
gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.3)

# 颜色方案
c_main = '#2166AC'
c_ci = '#92C5DE'
c_high = '#D6604D'
c_low = '#4393C3'
c_ref = '#999999'

# ---- Panel (a): 事件研究图 ----
ax1 = fig.add_subplot(gs[0, 0])
years_plot = es_df_hp['year'].values
coefs_hp = es_df_hp['coef'].values
ci_lo_hp = es_df_hp['ci_lo'].values
ci_hi_hp = es_df_hp['ci_hi'].values

ax1.fill_between(years_plot, ci_lo_hp, ci_hi_hp, alpha=0.25, color=c_ci)
ax1.plot(years_plot, coefs_hp, 'o-', color=c_main, markersize=7, linewidth=2)
ax1.axhline(0, color=c_ref, linestyle='--', linewidth=0.8)
ax1.axvline(2020, color='red', linestyle=':', linewidth=1.2, alpha=0.7)
ax1.set_xlabel('Year')
ax1.set_ylabel('Coefficient (RE_dep x Year)')
ax1.set_title('(a) Event Study: ln(House Price)', fontsize=12, fontweight='bold')
ax1.set_xticks(years_plot)
ax1.annotate('Three Red Lines\n(Aug 2020)', xy=(2020, ax1.get_ylim()[1] * 0.85),
             fontsize=8, ha='center', color='red', alpha=0.8)

# ---- Panel (b): 高/低依赖组平行趋势 ----
ax2 = fig.add_subplot(gs[0, 1])

# 计算高/低组的年均 ln(HP) 和 Q
trends = panel.groupby(['year', 'high_dep']).agg(
    mean_ln_hp=('ln_hp', 'mean'),
    mean_q=('urban_q', 'mean'),
    mean_hp=('house_price', 'mean')
).reset_index()

for dep_val, label, color, marker in [(1, 'High RE Dependence', c_high, 's'),
                                       (0, 'Low RE Dependence', c_low, 'o')]:
    sub = trends[trends['high_dep'] == dep_val]
    ax2.plot(sub['year'], sub['mean_q'], f'{marker}-', color=color,
             label=label, markersize=6, linewidth=2)

ax2.axvline(2020, color='red', linestyle=':', linewidth=1.2, alpha=0.7)
ax2.set_xlabel('Year')
ax2.set_ylabel('Mean Urban Q')
ax2.set_title('(b) Parallel Trends: Urban Q', fontsize=12, fontweight='bold')
ax2.legend(fontsize=9, loc='best')
ax2.set_xticks(sorted(panel['year'].unique()))

# ---- Panel (c): 剂量-反应图 ----
ax3 = fig.add_subplot(gs[1, 0])

quartiles = [1, 2, 3, 4]
dr_coefs_hp = dr_df_hp['coef'].values
dr_ci_lo_hp = dr_df_hp['ci_lo'].values
dr_ci_hi_hp = dr_df_hp['ci_hi'].values

ax3.bar(quartiles, dr_coefs_hp, color=[c_low, '#78B7C5', '#E1AF00', c_high],
        edgecolor='white', width=0.6, alpha=0.85)
ax3.errorbar(quartiles, dr_coefs_hp,
             yerr=[dr_coefs_hp - dr_ci_lo_hp, dr_ci_hi_hp - dr_coefs_hp],
             fmt='none', color='black', capsize=4, linewidth=1.5)
ax3.axhline(0, color=c_ref, linestyle='--', linewidth=0.8)
ax3.set_xlabel('RE Dependence Quartile')
ax3.set_ylabel('DID Coefficient (Post x Quartile)')
ax3.set_title('(c) Dose-Response: ln(House Price)', fontsize=12, fontweight='bold')
ax3.set_xticks(quartiles)
ax3.set_xticklabels(['Q1\n(Lowest)', 'Q2', 'Q3', 'Q4\n(Highest)'])

# ---- Panel (d): 机制检验 - FAI/GDP 变化 ----
ax4 = fig.add_subplot(gs[1, 1])

# 高/低组 FAI/GDP 趋势
fai_trends = panel.groupby(['year', 'high_dep'])['fai_gdp'].mean().reset_index()

for dep_val, label, color, marker in [(1, 'High RE Dependence', c_high, 's'),
                                       (0, 'Low RE Dependence', c_low, 'o')]:
    sub = fai_trends[fai_trends['high_dep'] == dep_val]
    ax4.plot(sub['year'], sub['fai_gdp'], f'{marker}-', color=color,
             label=label, markersize=6, linewidth=2)

ax4.axvline(2020, color='red', linestyle=':', linewidth=1.2, alpha=0.7)
ax4.set_xlabel('Year')
ax4.set_ylabel('FAI / GDP')
ax4.set_title('(d) Mechanism: Investment Intensity', fontsize=12, fontweight='bold')
ax4.legend(fontsize=9, loc='best')
ax4.set_xticks(sorted(panel['year'].unique()))

# 整体标题
fig.suptitle('Three Red Lines Policy: Difference-in-Differences Analysis',
             fontsize=14, fontweight='bold', y=0.98)

plt.savefig(FIGURE_PATH, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
rprint(f'图表已保存: {FIGURE_PATH}')

# ============================================================
# 12. 保存报告和源数据
# ============================================================

# 保存报告
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
print(f'\n报告已保存: {REPORT_PATH}')

# 保存源数据 (Source Data for figure)
source_data = {
    'event_study_hp': es_df_hp,
    'event_study_q': es_df_q,
    'dose_response_hp': dr_df_hp,
    'dose_response_q': dr_df_q,
    'trends_by_group': trends,
    'fai_trends': fai_trends,
}

# 合并为一个 CSV (多表)
with open(SOURCE_DATA_PATH, 'w') as f:
    for name, sdf in source_data.items():
        f.write(f'## {name}\n')
        sdf.to_csv(f, index=False)
        f.write('\n')
print(f'源数据已保存: {SOURCE_DATA_PATH}')

print('\n分析完成。')
