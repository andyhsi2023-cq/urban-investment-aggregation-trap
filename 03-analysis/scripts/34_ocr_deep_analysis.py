#!/usr/bin/env python3
"""
34_ocr_deep_analysis.py
=======================
目的：深入分析 OCR（过度资本化率）的决定因素、预测力与跨国分布
输入：global_ocr_uci_normalized.csv, global_urban_q_panel.csv, world_bank_usable_panel.csv, penn_world_table.csv
输出：
  - 03-analysis/models/ocr_determinants.txt        — OCR 决定因素回归
  - 03-analysis/models/ocr_global_ranking.txt       — 全球 OCR 排名
  - 03-analysis/models/ocr_predictive_power.txt     — OCR 预测力分析
  - 04-figures/drafts/fig16_ocr_deep.png            — 三子图可视化
依赖：pandas, numpy, statsmodels, scipy, matplotlib
"""

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import statsmodels.api as sm
# PanelOLS not available in this env; using manual demeaning instead
import statsmodels.formula.api as smf
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os

# ============================================================
# 路径配置
# ============================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
DATA_PROC = os.path.join(BASE, '02-data/processed')
DATA_RAW = os.path.join(BASE, '02-data/raw')
MODELS = os.path.join(BASE, '03-analysis/models')
FIGURES = os.path.join(BASE, '04-figures/drafts')

os.makedirs(MODELS, exist_ok=True)
os.makedirs(FIGURES, exist_ok=True)

# ============================================================
# 数据加载与合并
# ============================================================
print("=" * 60)
print("加载数据...")
print("=" * 60)

# 主 OCR 数据
ocr_df = pd.read_csv(os.path.join(DATA_PROC, 'global_ocr_uci_normalized.csv'))

# Q 面板（含 services_pct_gdp, gfcf_pct_gdp, gdp_constant_2015 等）
q_df = pd.read_csv(os.path.join(DATA_PROC, 'global_urban_q_panel.csv'))

# World Bank（补充缺失的 services 数据）
wb_df = pd.read_csv(os.path.join(DATA_PROC, 'world_bank_usable_panel.csv'))
wb_df = wb_df.rename(columns={'country_iso3': 'country_code'})

# PWT（人口增长率、投资率等）
pwt_df = pd.read_csv(os.path.join(DATA_RAW, 'penn_world_table.csv'))
pwt_df = pwt_df.rename(columns={'countrycode': 'country_code'})

# --- 合并 ---
# 从 Q 面板取 services_pct_gdp, industry_pct_gdp, gdp_constant_2015, gfcf_pct_gdp, total_pop
q_cols = ['country_code', 'year', 'services_pct_gdp', 'industry_pct_gdp',
          'gdp_constant_2015', 'gfcf_pct_gdp', 'total_pop', 'urban_q']
q_sub = q_df[q_cols].copy()

df = ocr_df.merge(q_sub, on=['country_code', 'year'], how='left')

# 从 PWT 取 pop（用于计算人口增长率）和 csh_i（投资份额）
pwt_cols = ['country_code', 'year', 'pop', 'csh_i', 'rgdpna']
pwt_sub = pwt_df[pwt_cols].copy()
df = df.merge(pwt_sub, on=['country_code', 'year'], how='left')

# 计算人口增长率（年度）
df = df.sort_values(['country_code', 'year'])
df['pop_growth'] = df.groupby('country_code')['pop'].pct_change() * 100  # 百分比

# 计算 GDP 增长率（用 constant 2015 USD）
df['gdp_growth'] = df.groupby('country_code')['gdp_constant_2015'].pct_change() * 100

# 计算 ln 变量
df['ln_OCR'] = np.log(df['OCR'].clip(lower=1e-10))
df['ln_hc'] = np.log(df['hc'].clip(lower=0.01))
df['urbanization'] = df['urban_rate']
df['I_GDP'] = df['gfcf_pct_gdp']  # 投资/GDP 比率
df['services_pct'] = df['services_pct_gdp']

print(f"合并后数据: {df.shape[0]} 行, {df['country_code'].nunique()} 个国家")
print(f"OCR 非空: {df['OCR'].notna().sum()}")
print(f"services_pct 非空: {df['services_pct'].notna().sum()}")
print(f"I_GDP 非空: {df['I_GDP'].notna().sum()}")
print(f"hc 非空: {df['hc'].notna().sum()}")

# ============================================================
# 分析 1：OCR 决定因素回归
# ============================================================
print("\n" + "=" * 60)
print("分析 1：OCR 决定因素回归")
print("=" * 60)

# 准备回归数据
reg_vars = ['ln_OCR', 'urbanization', 'I_GDP', 'pop_growth', 'ln_hc', 'services_pct',
            'country_code', 'year']
reg_df = df.dropna(subset=reg_vars).copy()

# 城镇化率二次项（检验非线性）
reg_df['urbanization_sq'] = reg_df['urbanization'] ** 2

print(f"回归样本: {reg_df.shape[0]} 行, {reg_df['country_code'].nunique()} 个国家")
print(f"年份范围: {reg_df['year'].min()} - {reg_df['year'].max()}")

# --- 模型 1：Pooled OLS ---
formula_1 = 'ln_OCR ~ urbanization + I_GDP + pop_growth + ln_hc + services_pct'
m1 = smf.ols(formula_1, data=reg_df).fit(cov_type='cluster', cov_kwds={'groups': reg_df['country_code']})

# --- 模型 2：含城镇化率二次项 ---
formula_2 = 'ln_OCR ~ urbanization + urbanization_sq + I_GDP + pop_growth + ln_hc + services_pct'
m2 = smf.ols(formula_2, data=reg_df).fit(cov_type='cluster', cov_kwds={'groups': reg_df['country_code']})

# --- 模型 3：国家固定效应（手动 demean） ---
# 使用 entity demeaned 的方式
for col in ['ln_OCR', 'urbanization', 'urbanization_sq', 'I_GDP', 'pop_growth', 'ln_hc', 'services_pct']:
    grp_mean = reg_df.groupby('country_code')[col].transform('mean')
    reg_df[f'{col}_dm'] = reg_df[col] - grp_mean

formula_3_dm = 'ln_OCR_dm ~ urbanization_dm + urbanization_sq_dm + I_GDP_dm + pop_growth_dm + ln_hc_dm + services_pct_dm - 1'
m3 = smf.ols(formula_3_dm, data=reg_df).fit(cov_type='cluster', cov_kwds={'groups': reg_df['country_code']})

# --- 模型 4：双向固定效应（entity + time demean） ---
# 先去除国家均值，再去除年份均值
for col in ['ln_OCR', 'urbanization', 'urbanization_sq', 'I_GDP', 'pop_growth', 'ln_hc', 'services_pct']:
    grp_mean_c = reg_df.groupby('country_code')[col].transform('mean')
    temp = reg_df[col] - grp_mean_c
    grp_mean_t = reg_df.groupby('year')[col].transform('mean')
    grand_mean = reg_df[col].mean()
    # 双向 demean: x_it - x_i. - x_.t + x_..
    reg_df[f'{col}_tw'] = reg_df[col] - grp_mean_c - grp_mean_t + grand_mean

formula_4_tw = 'ln_OCR_tw ~ urbanization_tw + urbanization_sq_tw + I_GDP_tw + pop_growth_tw + ln_hc_tw + services_pct_tw - 1'
m4 = smf.ols(formula_4_tw, data=reg_df).fit(cov_type='cluster', cov_kwds={'groups': reg_df['country_code']})

# 输出结果
det_report = []
det_report.append("=" * 80)
det_report.append("OCR 决定因素回归分析")
det_report.append("被解释变量: ln(OCR)")
det_report.append("=" * 80)
det_report.append(f"\n样本: {reg_df.shape[0]} 国家-年度观测, {reg_df['country_code'].nunique()} 个国家")
det_report.append(f"时间跨度: {reg_df['year'].min()} - {reg_df['year'].max()}")

det_report.append("\n" + "-" * 80)
det_report.append(f"{'变量':<25} {'(1) Pooled':>12} {'(2) +Urb²':>12} {'(3) FE':>12} {'(4) TWFE':>12}")
det_report.append("-" * 80)

# 变量映射
var_map_pooled = {
    'Intercept': 'Intercept',
    'urbanization': 'urbanization',
    'I_GDP': 'I_GDP (投资/GDP)',
    'pop_growth': 'pop_growth (人口增长)',
    'ln_hc': 'ln(hc) (人力资本)',
    'services_pct': 'services_pct (三产占比)',
    'urbanization_sq': 'urbanization² (城镇化²)',
}
var_map_dm = {
    'urbanization_dm': 'urbanization',
    'urbanization_sq_dm': 'urbanization² (城镇化²)',
    'I_GDP_dm': 'I_GDP (投资/GDP)',
    'pop_growth_dm': 'pop_growth (人口增长)',
    'ln_hc_dm': 'ln(hc) (人力资本)',
    'services_pct_dm': 'services_pct (三产占比)',
}
var_map_tw = {
    'urbanization_tw': 'urbanization',
    'urbanization_sq_tw': 'urbanization² (城镇化²)',
    'I_GDP_tw': 'I_GDP (投资/GDP)',
    'pop_growth_tw': 'pop_growth (人口增长)',
    'ln_hc_tw': 'ln(hc) (人力资本)',
    'services_pct_tw': 'services_pct (三产占比)',
}

display_vars = ['Intercept', 'urbanization', 'urbanization² (城镇化²)',
                'I_GDP (投资/GDP)', 'pop_growth (人口增长)',
                'ln(hc) (人力资本)', 'services_pct (三产占比)']

def fmt_coef(model, param_name, map_dict=None):
    """格式化系数为 coef (se) [stars]"""
    if map_dict:
        # reverse map
        actual_name = None
        for k, v in map_dict.items():
            if v == param_name:
                actual_name = k
                break
        if actual_name is None:
            return ''
        param_name = actual_name
    if param_name not in model.params.index:
        return ''
    coef = model.params[param_name]
    se = model.bse[param_name]
    pval = model.pvalues[param_name]
    stars = '***' if pval < 0.001 else '**' if pval < 0.01 else '*' if pval < 0.05 else ''
    return f"{coef:.4f}{stars}"

def fmt_se(model, param_name, map_dict=None):
    if map_dict:
        actual_name = None
        for k, v in map_dict.items():
            if v == param_name:
                actual_name = k
                break
        if actual_name is None:
            return ''
        param_name = actual_name
    if param_name not in model.params.index:
        return ''
    se = model.bse[param_name]
    return f"({se:.4f})"

for var_display in display_vars:
    c1 = fmt_coef(m1, var_display, var_map_pooled)
    c2 = fmt_coef(m2, var_display, var_map_pooled)
    c3 = fmt_coef(m3, var_display, var_map_dm)
    c4 = fmt_coef(m4, var_display, var_map_tw)
    det_report.append(f"{var_display:<25} {c1:>12} {c2:>12} {c3:>12} {c4:>12}")

    s1 = fmt_se(m1, var_display, var_map_pooled)
    s2 = fmt_se(m2, var_display, var_map_pooled)
    s3 = fmt_se(m3, var_display, var_map_dm)
    s4 = fmt_se(m4, var_display, var_map_tw)
    det_report.append(f"{'':25} {s1:>12} {s2:>12} {s3:>12} {s4:>12}")

det_report.append("-" * 80)
det_report.append(f"{'N':25} {m1.nobs:>12.0f} {m2.nobs:>12.0f} {m3.nobs:>12.0f} {m4.nobs:>12.0f}")
det_report.append(f"{'R²':25} {m1.rsquared:>12.4f} {m2.rsquared:>12.4f} {m3.rsquared:>12.4f} {m4.rsquared:>12.4f}")
det_report.append(f"{'固定效应':25} {'无':>12} {'无':>12} {'国家':>12} {'国家+年份':>12}")
det_report.append(f"{'聚类标准误':25} {'国家':>12} {'国家':>12} {'国家':>12} {'国家':>12}")
det_report.append("-" * 80)
det_report.append("注: *** p<0.001, ** p<0.01, * p<0.05。标准误聚类到国家层面。")

# 详细解读
det_report.append("\n" + "=" * 80)
det_report.append("关键发现解读")
det_report.append("=" * 80)

# 从 TWFE 模型提取解读
tw_params = m4.params
tw_pvals = m4.pvalues
for orig, display in var_map_tw.items():
    if orig in tw_params.index:
        coef = tw_params[orig]
        pv = tw_pvals[orig]
        sig = "显著" if pv < 0.05 else "不显著"
        direction = "正" if coef > 0 else "负"
        det_report.append(f"- {display}: 系数={coef:.4f}, p={pv:.4f} ({sig}, {direction}向)")

det_report_text = '\n'.join(det_report)
print(det_report_text)

with open(os.path.join(MODELS, 'ocr_determinants.txt'), 'w', encoding='utf-8') as f:
    f.write(det_report_text)

# ============================================================
# 分析 2：OCR 与后续经济绩效
# ============================================================
print("\n" + "=" * 60)
print("分析 2：OCR 预测未来 GDP 增长")
print("=" * 60)

# 计算 5 年滚动 GDP 增长率
df_pred = df[['country_code', 'year', 'OCR', 'OCR_norm', 'gdp_constant_2015',
              'urbanization', 'ln_hc', 'I_GDP', 'region', 'income_group']].copy()

# 5 年后的 GDP
df_pred = df_pred.sort_values(['country_code', 'year'])
df_pred['gdp_future5'] = df_pred.groupby('country_code')['gdp_constant_2015'].shift(-5)
df_pred['gdp_growth_5yr'] = ((df_pred['gdp_future5'] / df_pred['gdp_constant_2015']) - 1) * 100

# ln(OCR) 和 OCR² 用于非线性检验
df_pred['ln_OCR'] = np.log(df_pred['OCR'].clip(lower=1e-10))
df_pred['OCR_sq'] = df_pred['OCR_norm'] ** 2

pred_vars = ['OCR_norm', 'OCR_sq', 'gdp_growth_5yr', 'urbanization', 'ln_hc', 'I_GDP', 'country_code', 'year']
pred_df = df_pred.dropna(subset=['OCR_norm', 'gdp_growth_5yr', 'country_code', 'year']).copy()

# 去除极端值（GDP增长率超过 ±100%）
pred_df = pred_df[(pred_df['gdp_growth_5yr'] > -50) & (pred_df['gdp_growth_5yr'] < 150)]

print(f"预测样本: {pred_df.shape[0]} 观测, {pred_df['country_code'].nunique()} 个国家")

pred_report = []
pred_report.append("=" * 80)
pred_report.append("OCR 对未来 GDP 增长的预测力分析")
pred_report.append("被解释变量: 5 年累积 GDP 增长率 (%)")
pred_report.append("=" * 80)
pred_report.append(f"\n样本: {pred_df.shape[0]} 观测, {pred_df['country_code'].nunique()} 个国家")

# 模型 A: 线性
fm_a = 'gdp_growth_5yr ~ OCR_norm'
ma = smf.ols(fm_a, data=pred_df).fit(cov_type='cluster', cov_kwds={'groups': pred_df['country_code']})

# 模型 B: 二次项
fm_b = 'gdp_growth_5yr ~ OCR_norm + OCR_sq'
mb = smf.ols(fm_b, data=pred_df).fit(cov_type='cluster', cov_kwds={'groups': pred_df['country_code']})

# 模型 C: 含控制变量
pred_df_c = pred_df.dropna(subset=['urbanization', 'I_GDP']).copy()
pred_df_c['OCR_sq'] = pred_df_c['OCR_norm'] ** 2
fm_c = 'gdp_growth_5yr ~ OCR_norm + OCR_sq + urbanization + I_GDP'
mc = smf.ols(fm_c, data=pred_df_c).fit(cov_type='cluster', cov_kwds={'groups': pred_df_c['country_code']})

# 模型 D: 国家固定效应
for col in ['gdp_growth_5yr', 'OCR_norm', 'OCR_sq', 'urbanization', 'I_GDP']:
    if col in pred_df_c.columns:
        pred_df_c[f'{col}_dm'] = pred_df_c[col] - pred_df_c.groupby('country_code')[col].transform('mean')

fm_d = 'gdp_growth_5yr_dm ~ OCR_norm_dm + OCR_sq_dm + urbanization_dm + I_GDP_dm - 1'
md = smf.ols(fm_d, data=pred_df_c).fit(cov_type='cluster', cov_kwds={'groups': pred_df_c['country_code']})

pred_report.append("\n" + "-" * 80)
pred_report.append(f"{'变量':<25} {'(A) 线性':>12} {'(B) 二次':>12} {'(C) +控制':>12} {'(D) FE':>12}")
pred_report.append("-" * 80)

for var in ['Intercept', 'OCR_norm', 'OCR_sq', 'urbanization', 'I_GDP']:
    vals = []
    for model in [ma, mb, mc]:
        if var in model.params.index:
            coef = model.params[var]
            pval = model.pvalues[var]
            stars = '***' if pval < 0.001 else '**' if pval < 0.01 else '*' if pval < 0.05 else ''
            vals.append(f"{coef:.4f}{stars}")
        else:
            vals.append('')
    # model D uses demeaned
    dm_var = f'{var}_dm' if var != 'Intercept' else var
    if dm_var in md.params.index:
        coef = md.params[dm_var]
        pval = md.pvalues[dm_var]
        stars = '***' if pval < 0.001 else '**' if pval < 0.01 else '*' if pval < 0.05 else ''
        vals.append(f"{coef:.4f}{stars}")
    else:
        vals.append('')

    pred_report.append(f"{var:<25} {vals[0]:>12} {vals[1]:>12} {vals[2]:>12} {vals[3]:>12}")

    # SEs
    se_vals = []
    for model in [ma, mb, mc]:
        if var in model.bse.index:
            se_vals.append(f"({model.bse[var]:.4f})")
        else:
            se_vals.append('')
    dm_var = f'{var}_dm' if var != 'Intercept' else var
    if dm_var in md.bse.index:
        se_vals.append(f"({md.bse[dm_var]:.4f})")
    else:
        se_vals.append('')
    pred_report.append(f"{'':25} {se_vals[0]:>12} {se_vals[1]:>12} {se_vals[2]:>12} {se_vals[3]:>12}")

pred_report.append("-" * 80)
pred_report.append(f"{'N':25} {ma.nobs:>12.0f} {mb.nobs:>12.0f} {mc.nobs:>12.0f} {md.nobs:>12.0f}")
pred_report.append(f"{'R²':25} {ma.rsquared:>12.4f} {mb.rsquared:>12.4f} {mc.rsquared:>12.4f} {md.rsquared:>12.4f}")
pred_report.append("-" * 80)

# 计算 OCR_norm 的转折点（二次项模型）
if 'OCR_norm' in mb.params.index and 'OCR_sq' in mb.params.index:
    b1 = mb.params['OCR_norm']
    b2 = mb.params['OCR_sq']
    if b2 != 0:
        turning_point = -b1 / (2 * b2)
        pred_report.append(f"\n二次项模型转折点: OCR_norm = {turning_point:.4f}")
        pred_report.append(f"  - 当 OCR_norm < {turning_point:.4f} 时, OCR 增加与 GDP 增长{('正' if b1 > 0 else '负')}相关")
        pred_report.append(f"  - 当 OCR_norm > {turning_point:.4f} 时, OCR 增加与 GDP 增长{('负' if b2 < 0 else '正')}相关")

pred_report_text = '\n'.join(pred_report)
print(pred_report_text)

with open(os.path.join(MODELS, 'ocr_predictive_power.txt'), 'w', encoding='utf-8') as f:
    f.write(pred_report_text)

# ============================================================
# 分析 3：OCR 国际排名
# ============================================================
print("\n" + "=" * 60)
print("分析 3：OCR 全球排名（2015-2019 均值）")
print("=" * 60)

# 2015-2019 均值
rank_df = df[(df['year'] >= 2015) & (df['year'] <= 2019) & df['OCR_norm'].notna()].copy()
rank_agg = rank_df.groupby(['country_code', 'country_name', 'region', 'income_group']).agg(
    OCR_norm_mean=('OCR_norm', 'mean'),
    OCR_mean=('OCR', 'mean'),
    n_years=('OCR_norm', 'count')
).reset_index()

# 至少 3 年数据
rank_agg = rank_agg[rank_agg['n_years'] >= 3].sort_values('OCR_norm_mean', ascending=False).reset_index(drop=True)
rank_agg['rank'] = range(1, len(rank_agg) + 1)

rank_report = []
rank_report.append("=" * 80)
rank_report.append("全球 OCR 排名（2015-2019 均值）")
rank_report.append("=" * 80)
rank_report.append(f"纳入国家数: {len(rank_agg)}（要求至少 3 年数据）")

# Top 20 过度建设
rank_report.append("\n" + "-" * 80)
rank_report.append("【过度建设 Top 20】—— OCR_norm 最高")
rank_report.append("-" * 80)
rank_report.append(f"{'排名':>4} {'国家代码':<6} {'国家':<25} {'地区':<25} {'OCR_norm':>10} {'OCR':>12}")
rank_report.append("-" * 80)
top20 = rank_agg.head(20)
for _, row in top20.iterrows():
    rank_report.append(
        f"{row['rank']:>4} {row['country_code']:<6} {row['country_name']:<25} "
        f"{str(row['region']):<25} {row['OCR_norm_mean']:>10.6f} {row['OCR_mean']:>12.6f}"
    )

# Bottom 20 建设不足
rank_report.append("\n" + "-" * 80)
rank_report.append("【建设不足 Top 20】—— OCR_norm 最低")
rank_report.append("-" * 80)
rank_report.append(f"{'排名':>4} {'国家代码':<6} {'国家':<25} {'地区':<25} {'OCR_norm':>10} {'OCR':>12}")
rank_report.append("-" * 80)
bottom20 = rank_agg.tail(20).iloc[::-1]
for _, row in bottom20.iterrows():
    rank_report.append(
        f"{row['rank']:>4} {row['country_code']:<6} {row['country_name']:<25} "
        f"{str(row['region']):<25} {row['OCR_norm_mean']:>10.6f} {row['OCR_mean']:>12.6f}"
    )

# 按区域统计
rank_report.append("\n" + "-" * 80)
rank_report.append("按区域 OCR 分布")
rank_report.append("-" * 80)
region_stats = rank_agg.groupby('region').agg(
    n=('OCR_norm_mean', 'count'),
    mean=('OCR_norm_mean', 'mean'),
    median=('OCR_norm_mean', 'median'),
    std=('OCR_norm_mean', 'std'),
    min=('OCR_norm_mean', 'min'),
    max=('OCR_norm_mean', 'max')
).sort_values('mean', ascending=False)

rank_report.append(f"{'区域':<30} {'N':>4} {'均值':>10} {'中位数':>10} {'标准差':>10} {'最小值':>10} {'最大值':>10}")
rank_report.append("-" * 80)
for region, row in region_stats.iterrows():
    rank_report.append(
        f"{str(region):<30} {row['n']:>4.0f} {row['mean']:>10.6f} {row['median']:>10.6f} "
        f"{row['std']:>10.6f} {row['min']:>10.6f} {row['max']:>10.6f}"
    )

# 按收入组统计
rank_report.append("\n" + "-" * 80)
rank_report.append("按收入组 OCR 分布")
rank_report.append("-" * 80)
income_stats = rank_agg.groupby('income_group').agg(
    n=('OCR_norm_mean', 'count'),
    mean=('OCR_norm_mean', 'mean'),
    median=('OCR_norm_mean', 'median'),
    std=('OCR_norm_mean', 'std')
).sort_values('mean', ascending=False)

rank_report.append(f"{'收入组':<25} {'N':>4} {'均值':>10} {'中位数':>10} {'标准差':>10}")
for ig, row in income_stats.iterrows():
    rank_report.append(
        f"{str(ig):<25} {row['n']:>4.0f} {row['mean']:>10.6f} {row['median']:>10.6f} {row['std']:>10.6f}"
    )

# 中国的位置
china_rank = rank_agg[rank_agg['country_code'] == 'CHN']
if not china_rank.empty:
    rank_report.append(f"\n中国排名: 第 {china_rank['rank'].values[0]} / {len(rank_agg)} 名")
    rank_report.append(f"  OCR_norm = {china_rank['OCR_norm_mean'].values[0]:.6f}")

rank_report_text = '\n'.join(rank_report)
print(rank_report_text)

with open(os.path.join(MODELS, 'ocr_global_ranking.txt'), 'w', encoding='utf-8') as f:
    f.write(rank_report_text)

# ============================================================
# 分析 4：OCR-Q 联动
# ============================================================
print("\n" + "=" * 60)
print("分析 4：OCR-Q 联动机制")
print("=" * 60)

# 准备 OCR 和 Q 的联动数据
oq_df = df[['country_code', 'year', 'OCR_norm', 'urban_q']].dropna().copy()
oq_df = oq_df.sort_values(['country_code', 'year'])

# 创建滞后变量
for lag in [1, 2, 3, 5]:
    oq_df[f'OCR_lag{lag}'] = oq_df.groupby('country_code')['OCR_norm'].shift(lag)
    oq_df[f'Q_lag{lag}'] = oq_df.groupby('country_code')['urban_q'].shift(lag)

print(f"OCR-Q 联动样本: {oq_df.shape[0]} 观测")

# 当期 OCR 对未来 Q 的预测
oq_pred = oq_df.dropna(subset=['OCR_lag1', 'OCR_lag2', 'OCR_lag3']).copy()

if len(oq_pred) > 50:
    # 分布滞后模型: Q_t = a + b1*OCR_{t-1} + b2*OCR_{t-2} + b3*OCR_{t-3}
    fm_oq = 'urban_q ~ OCR_lag1 + OCR_lag2 + OCR_lag3'
    m_oq = smf.ols(fm_oq, data=oq_pred).fit(cov_type='cluster', cov_kwds={'groups': oq_pred['country_code']})

    pred_report_lines = pred_report  # append to same report

    oq_report = []
    oq_report.append("\n\n" + "=" * 80)
    oq_report.append("OCR-Q 联动分析")
    oq_report.append("=" * 80)
    oq_report.append(f"样本: {m_oq.nobs:.0f} 观测")
    oq_report.append("\n分布滞后模型: Q_t = a + b1*OCR_{t-1} + b2*OCR_{t-2} + b3*OCR_{t-3}")
    oq_report.append(m_oq.summary().as_text())

    # 简单 Granger 因果（F 检验）
    # 受限模型: Q_t ~ Q_{t-1} + Q_{t-2}
    oq_g = oq_df.dropna(subset=['Q_lag1', 'Q_lag2', 'OCR_lag1', 'OCR_lag2']).copy()
    if len(oq_g) > 50:
        m_restricted = smf.ols('urban_q ~ Q_lag1 + Q_lag2', data=oq_g).fit()
        m_unrestricted = smf.ols('urban_q ~ Q_lag1 + Q_lag2 + OCR_lag1 + OCR_lag2', data=oq_g).fit()

        # F 检验
        n = m_unrestricted.nobs
        k_r = m_restricted.df_model
        k_u = m_unrestricted.df_model
        q_restrictions = k_u - k_r
        ssr_r = m_restricted.ssr
        ssr_u = m_unrestricted.ssr
        f_stat = ((ssr_r - ssr_u) / q_restrictions) / (ssr_u / (n - k_u - 1))
        f_pval = 1 - stats.f.cdf(f_stat, q_restrictions, n - k_u - 1)

        oq_report.append(f"\nGranger 因果检验 (OCR → Q):")
        oq_report.append(f"  F统计量 = {f_stat:.4f}, p值 = {f_pval:.6f}")
        oq_report.append(f"  结论: {'OCR Granger-causes Q (显著)' if f_pval < 0.05 else 'OCR 不能 Granger-cause Q'}")

        # 反向: Q → OCR
        oq_g2 = oq_df.dropna(subset=['Q_lag1', 'Q_lag2', 'OCR_lag1', 'OCR_lag2']).copy()
        oq_g2['OCR_lag1_oc'] = oq_g2.groupby('country_code')['OCR_norm'].shift(1)
        oq_g2['OCR_lag2_oc'] = oq_g2.groupby('country_code')['OCR_norm'].shift(2)
        m_r2 = smf.ols('OCR_norm ~ OCR_lag1 + OCR_lag2', data=oq_g2.dropna(subset=['OCR_lag1','OCR_lag2'])).fit()
        m_u2 = smf.ols('OCR_norm ~ OCR_lag1 + OCR_lag2 + Q_lag1 + Q_lag2', data=oq_g2.dropna(subset=['OCR_lag1','OCR_lag2','Q_lag1','Q_lag2'])).fit()

        n2 = m_u2.nobs
        f_stat2 = ((m_r2.ssr - m_u2.ssr) / 2) / (m_u2.ssr / (n2 - m_u2.df_model - 1))
        f_pval2 = 1 - stats.f.cdf(f_stat2, 2, n2 - m_u2.df_model - 1)

        oq_report.append(f"\nGranger 因果检验 (Q → OCR):")
        oq_report.append(f"  F统计量 = {f_stat2:.4f}, p值 = {f_pval2:.6f}")
        oq_report.append(f"  结论: {'Q Granger-causes OCR (显著)' if f_pval2 < 0.05 else 'Q 不能 Granger-cause OCR'}")

    oq_report_text = '\n'.join(oq_report)
    print(oq_report_text)

    # 追加到 predictive_power 文件
    with open(os.path.join(MODELS, 'ocr_predictive_power.txt'), 'a', encoding='utf-8') as f:
        f.write(oq_report_text)

# ============================================================
# 可视化：三子图
# ============================================================
print("\n" + "=" * 60)
print("绘制可视化（3 子图）")
print("=" * 60)

fig = plt.figure(figsize=(18, 6.5))
gs = GridSpec(1, 3, figure=fig, wspace=0.35)

# --- (a) OCR 决定因素回归系数图（TWFE 模型） ---
ax1 = fig.add_subplot(gs[0, 0])

# 使用模型 4 (TWFE) 的系数
coef_names_tw = ['urbanization_tw', 'urbanization_sq_tw', 'I_GDP_tw',
                  'pop_growth_tw', 'ln_hc_tw', 'services_pct_tw']
display_names = ['Urbanization', 'Urbanization$^2$', 'Investment/GDP',
                 'Pop. growth', 'ln(Human capital)', 'Services (% GDP)']

coefs = [m4.params[v] for v in coef_names_tw]
ci_low = [m4.conf_int().loc[v, 0] for v in coef_names_tw]
ci_high = [m4.conf_int().loc[v, 1] for v in coef_names_tw]
pvals_tw = [m4.pvalues[v] for v in coef_names_tw]

# 标准化系数以便可比（用 z-score 缩放）
# 使用原始变量标准差来缩放
std_map = {
    'urbanization_tw': reg_df['urbanization'].std(),
    'urbanization_sq_tw': reg_df['urbanization_sq'].std(),
    'I_GDP_tw': reg_df['I_GDP'].std(),
    'pop_growth_tw': reg_df['pop_growth'].std(),
    'ln_hc_tw': reg_df['ln_hc'].std(),
    'services_pct_tw': reg_df['services_pct'].std(),
}
sd_y = reg_df['ln_OCR'].std()

std_coefs = [m4.params[v] * std_map[v] / sd_y for v in coef_names_tw]
std_ci_low = [m4.conf_int().loc[v, 0] * std_map[v] / sd_y for v in coef_names_tw]
std_ci_high = [m4.conf_int().loc[v, 1] * std_map[v] / sd_y for v in coef_names_tw]

y_pos = np.arange(len(display_names))[::-1]
colors = ['#c0392b' if c > 0 else '#2980b9' for c in std_coefs]
face_colors = []
for i, pv in enumerate(pvals_tw):
    if pv < 0.05:
        face_colors.append(colors[i])
    else:
        face_colors.append('white')

ax1.barh(y_pos, std_coefs, height=0.5, color=face_colors, edgecolor=colors, linewidth=1.5)
ax1.errorbar(std_coefs, y_pos, xerr=[np.array(std_coefs) - np.array(std_ci_low),
             np.array(std_ci_high) - np.array(std_coefs)],
             fmt='none', ecolor='black', capsize=3, linewidth=1)
ax1.axvline(0, color='black', linewidth=0.8, linestyle='--')
ax1.set_yticks(y_pos)
ax1.set_yticklabels(display_names, fontsize=9)
ax1.set_xlabel('Standardized coefficient (TWFE)', fontsize=9)
ax1.set_title('(a) Determinants of OCR', fontsize=11, fontweight='bold')

# 添加显著性标记
for i, (c, pv) in enumerate(zip(std_coefs, pvals_tw)):
    star = '***' if pv < 0.001 else '**' if pv < 0.01 else '*' if pv < 0.05 else ''
    offset = 0.02 if c >= 0 else -0.02
    ha = 'left' if c >= 0 else 'right'
    ax1.text(c + offset, y_pos[i], star, ha=ha, va='center', fontsize=9, fontweight='bold')

# --- (b) OCR vs 未来 GDP 增速散点图 ---
ax2 = fig.add_subplot(gs[0, 1])

# 使用 pred_df 数据
plot_df = pred_df.dropna(subset=['OCR_norm', 'gdp_growth_5yr']).copy()
# 去除极端值
q1, q99 = plot_df['OCR_norm'].quantile(0.01), plot_df['OCR_norm'].quantile(0.99)
plot_df = plot_df[(plot_df['OCR_norm'] >= q1) & (plot_df['OCR_norm'] <= q99)]

# 散点
ax2.scatter(plot_df['OCR_norm'], plot_df['gdp_growth_5yr'],
            alpha=0.15, s=8, color='#7f8c8d', edgecolors='none', rasterized=True)

# 拟合线（二次多项式）
x_fit = np.linspace(plot_df['OCR_norm'].quantile(0.02), plot_df['OCR_norm'].quantile(0.98), 200)
# 用模型 B 的系数
if 'OCR_norm' in mb.params.index and 'OCR_sq' in mb.params.index:
    y_fit = mb.params['Intercept'] + mb.params['OCR_norm'] * x_fit + mb.params['OCR_sq'] * x_fit**2
    ax2.plot(x_fit, y_fit, color='#e74c3c', linewidth=2.5, label='Quadratic fit')

    # 线性拟合对比
    y_fit_lin = ma.params['Intercept'] + ma.params['OCR_norm'] * x_fit
    ax2.plot(x_fit, y_fit_lin, color='#3498db', linewidth=2, linestyle='--', label='Linear fit')

# 标注转折点
if 'OCR_norm' in mb.params.index and 'OCR_sq' in mb.params.index:
    b1 = mb.params['OCR_norm']
    b2 = mb.params['OCR_sq']
    if b2 != 0:
        tp = -b1 / (2 * b2)
        tp_y = mb.params['Intercept'] + b1 * tp + b2 * tp**2
        if plot_df['OCR_norm'].min() < tp < plot_df['OCR_norm'].max():
            ax2.axvline(tp, color='gray', linewidth=1, linestyle=':', alpha=0.7)
            ax2.annotate(f'Turning point\nOCR={tp:.3f}', xy=(tp, tp_y),
                        xytext=(tp + 0.01, tp_y + 10), fontsize=8,
                        arrowprops=dict(arrowstyle='->', color='gray'))

ax2.set_xlabel('OCR$_{norm}$ (lagged 5 years)', fontsize=9)
ax2.set_ylabel('5-year cumulative GDP growth (%)', fontsize=9)
ax2.set_title('(b) OCR vs. Future GDP Growth', fontsize=11, fontweight='bold')
ax2.legend(fontsize=8, loc='upper right')

# --- (c) 全球 OCR 排名条形图 ---
ax3 = fig.add_subplot(gs[0, 2])

# Top 20 + Bottom 20
n_show = 15  # 每侧 15 个更紧凑
top_n = rank_agg.head(n_show).copy()
bottom_n = rank_agg.tail(n_show).iloc[::-1].copy()

# 拼接
bar_data = pd.concat([top_n, bottom_n], ignore_index=True)
bar_data['label'] = bar_data['country_code'] + ' ' + bar_data['country_name'].str[:12]

y_pos_bar = np.arange(len(bar_data))
colors_bar = ['#c0392b'] * n_show + ['#2980b9'] * n_show

ax3.barh(y_pos_bar, bar_data['OCR_norm_mean'], color=colors_bar, height=0.7, alpha=0.85)
ax3.set_yticks(y_pos_bar)
ax3.set_yticklabels(bar_data['label'], fontsize=6.5)
ax3.invert_yaxis()
ax3.set_xlabel('OCR$_{norm}$ (2015-2019 mean)', fontsize=9)
ax3.set_title('(c) Global OCR Ranking', fontsize=11, fontweight='bold')

# 分隔线
ax3.axhline(n_show - 0.5, color='black', linewidth=1, linestyle='-')
ax3.text(bar_data['OCR_norm_mean'].max() * 0.5, n_show * 0.45,
         'Over-capitalized', ha='center', fontsize=8, color='#c0392b', fontstyle='italic')
ax3.text(bar_data['OCR_norm_mean'].max() * 0.5, n_show + n_show * 0.45,
         'Under-capitalized', ha='center', fontsize=8, color='#2980b9', fontstyle='italic')

# 标记中国
china_in_bar = bar_data[bar_data['country_code'] == 'CHN']
if not china_in_bar.empty:
    idx = china_in_bar.index[0]
    ax3.get_yticklabels()[idx].set_color('#c0392b')
    ax3.get_yticklabels()[idx].set_fontweight('bold')

plt.suptitle('Finding 4: Deep Analysis of Overcapitalization Ratio (OCR)',
             fontsize=13, fontweight='bold', y=1.02)

plt.savefig(os.path.join(FIGURES, 'fig16_ocr_deep.png'), dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()

print(f"\n图表已保存: {os.path.join(FIGURES, 'fig16_ocr_deep.png')}")
print(f"回归结果已保存: {os.path.join(MODELS, 'ocr_determinants.txt')}")
print(f"排名结果已保存: {os.path.join(MODELS, 'ocr_global_ranking.txt')}")
print(f"预测力分析已保存: {os.path.join(MODELS, 'ocr_predictive_power.txt')}")
print("\n完成！")
