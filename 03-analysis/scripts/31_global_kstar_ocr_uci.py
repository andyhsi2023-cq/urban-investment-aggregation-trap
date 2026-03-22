#!/usr/bin/env python3
"""
31_global_kstar_ocr_uci.py
==========================
目的：基于全球面板数据估计 K*（理论最优资产存量），计算 OCR 和 UCI
输入：
  - 02-data/processed/global_urban_q_panel.csv （158 国 Urban Q 面板）
  - 02-data/raw/penn_world_table.csv （PWT 人力资本等）
输出：
  - 02-data/processed/global_kstar_ocr_uci.csv （K*/OCR/UCI 面板）
  - 03-analysis/models/kstar_regression.txt （K* 回归结果）
  - 03-analysis/models/global_inverted_u_regression.txt （倒 U 型回归）
  - 04-figures/drafts/fig11_kstar_ocr_uci.png （3 张子图）
依赖：pandas, numpy, statsmodels, matplotlib, scipy
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

warnings.filterwarnings('ignore')

# ============================================================
# 路径设置
# ============================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
DATA_PROC = os.path.join(BASE, '02-data', 'processed')
DATA_RAW = os.path.join(BASE, '02-data', 'raw')
MODELS = os.path.join(BASE, '03-analysis', 'models')
FIGS = os.path.join(BASE, '04-figures', 'drafts')

for d in [DATA_PROC, MODELS, FIGS]:
    os.makedirs(d, exist_ok=True)

# ============================================================
# 步骤 1：加载与合并数据
# ============================================================
print("=" * 60)
print("步骤 1：构建分析面板")
print("=" * 60)

# 加载 Urban Q 面板
uq = pd.read_csv(os.path.join(DATA_PROC, 'global_urban_q_panel.csv'))
print(f"Urban Q 面板: {uq.shape[0]} 行, {uq['country_code'].nunique()} 国")

# 加载 PWT
pwt = pd.read_csv(os.path.join(DATA_RAW, 'penn_world_table.csv'), encoding='utf-8-sig')
print(f"PWT: {pwt.shape[0]} 行, {pwt['countrycode'].nunique()} 国")

# 从 PWT 中提取补充列
pwt_sub = pwt[['countrycode', 'year', 'hc', 'rnna', 'rgdpna', 'pop', 'emp', 'csh_i', 'delta']].copy()
pwt_sub.rename(columns={'countrycode': 'country_code',
                         'hc': 'hc_pwt',
                         'rnna': 'rnna_pwt',
                         'rgdpna': 'rgdpna_pwt'}, inplace=True)

# 合并
df = uq.merge(pwt_sub, on=['country_code', 'year'], how='left')
print(f"合并后: {df.shape[0]} 行")

# 统一关键变量
df['K'] = df['K_best'].fillna(df['rnna_pwt'])
df['V'] = df['V3']
df['Q'] = df['urban_q']
df['GDP'] = df['gdp_constant_2015']
df['Pu'] = df['urban_pop']
df['H'] = df['hc'].fillna(df['hc_pwt'])
df['urban_rate'] = df['urban_pct']
df['services_share'] = df['services_pct_gdp']
df['working_age_pct'] = df['pop_15_64_pct']
df['inv_gdp_ratio'] = df['gfcf_pct_gdp']
df['dV_V'] = df['delta_V_ratio']

# 收入分组（基于最新可用年份的人均 GDP）
latest_gdp = df.dropna(subset=['GDP', 'total_pop']).copy()
latest_gdp['gdp_pc'] = latest_gdp['GDP'] / latest_gdp['total_pop']
latest = latest_gdp.sort_values('year').groupby('country_code')['gdp_pc'].last().reset_index()
latest.columns = ['country_code', 'gdp_pc_latest']

def income_group(gdp_pc):
    if pd.isna(gdp_pc):
        return np.nan
    elif gdp_pc < 1200:
        return 'Low'
    elif gdp_pc < 4500:
        return 'Lower-middle'
    elif gdp_pc < 14000:
        return 'Upper-middle'
    else:
        return 'High'

latest['income_group'] = latest['gdp_pc_latest'].apply(income_group)
df = df.merge(latest[['country_code', 'income_group']], on='country_code', how='left')

print(f"\n收入分组分布:")
print(df.groupby('income_group')['country_code'].nunique())

# ============================================================
# 步骤 2：K* 面板回归
# ============================================================
print("\n" + "=" * 60)
print("步骤 2：K* 面板回归")
print("=" * 60)

# 准备回归样本
reg_df = df[['country_code', 'region', 'year', 'K', 'Pu', 'H', 'GDP']].dropna().copy()
# 确保正值
reg_df = reg_df[(reg_df['K'] > 0) & (reg_df['Pu'] > 0) & (reg_df['H'] > 0) & (reg_df['GDP'] > 0)]
print(f"回归样本: {reg_df.shape[0]} 观测, {reg_df['country_code'].nunique()} 国")

# 取对数
for col in ['K', 'Pu', 'H', 'GDP']:
    reg_df[f'ln_{col}'] = np.log(reg_df[col])

# -------------------------------------------------------
# 模型 1（主模型）：Correlated Random Effects / Mundlak
# 用国家均值 + 组内偏差分离 between 和 within 效应
# 这样 between 系数（从截面变异）给出结构性弹性用于 K* 预测
# within 系数（从时间变异）反映调整动态
# -------------------------------------------------------
# 计算国家均值
for col in ['ln_Pu', 'ln_H', 'ln_GDP']:
    means = reg_df.groupby('country_code')[col].transform('mean')
    reg_df[f'{col}_bar'] = means  # Mundlak 项

# 构建 X 矩阵：原始变量 + Mundlak 均值项 + 年份 FE
year_dummies = pd.get_dummies(reg_df['year'], prefix='fy', drop_first=True, dtype=float)

X_mundlak = reg_df[['ln_Pu', 'ln_H', 'ln_GDP',
                      'ln_Pu_bar', 'ln_H_bar', 'ln_GDP_bar']].copy()
X_mundlak = pd.concat([X_mundlak, year_dummies], axis=1)
X_mundlak = sm.add_constant(X_mundlak)
y_mundlak = reg_df['ln_K']

model_mundlak = sm.OLS(y_mundlak, X_mundlak).fit(cov_type='cluster',
                                                    cov_kwds={'groups': reg_df['country_code']})

print("\n--- 模型 1: Mundlak (Correlated RE) ---")
for v in ['ln_Pu', 'ln_H', 'ln_GDP', 'ln_Pu_bar', 'ln_H_bar', 'ln_GDP_bar']:
    print(f"  {v:<15} = {model_mundlak.params[v]:>8.4f} (SE={model_mundlak.bse[v]:.4f}, p={model_mundlak.pvalues[v]:.4e})")
print(f"  R-squared: {model_mundlak.rsquared:.4f}")

# Between 效应 = within + bar 系数之和（即截面关系）
alpha_P_between = model_mundlak.params['ln_Pu'] + model_mundlak.params['ln_Pu_bar']
alpha_H_between = model_mundlak.params['ln_H'] + model_mundlak.params['ln_H_bar']
alpha_G_between = model_mundlak.params['ln_GDP'] + model_mundlak.params['ln_GDP_bar']

print(f"\n  Between 效应 (截面弹性，用于 K* 结构):")
print(f"    alpha_P (between) = {alpha_P_between:.4f}")
print(f"    alpha_H (between) = {alpha_H_between:.4f}")
print(f"    alpha_G (between) = {alpha_G_between:.4f}")

# -------------------------------------------------------
# 模型 2（备选 / 结构性）：Between Estimator
# 使用国家时间平均值的截面回归，直接获取结构弹性
# -------------------------------------------------------
country_means = reg_df.groupby('country_code')[['ln_K', 'ln_Pu', 'ln_H', 'ln_GDP']].mean().reset_index()
# 合并 region
country_means = country_means.merge(
    reg_df[['country_code', 'region']].drop_duplicates(),
    on='country_code', how='left'
)
region_dummies = pd.get_dummies(country_means['region'], prefix='reg', drop_first=True, dtype=float)

X_between = country_means[['ln_Pu', 'ln_H', 'ln_GDP']].copy()
X_between = pd.concat([X_between, region_dummies], axis=1)
X_between = sm.add_constant(X_between)
y_between = country_means['ln_K']

model_between = sm.OLS(y_between, X_between).fit(cov_type='HC1')

print(f"\n--- 模型 2: Between Estimator (截面回归) ---")
for v in ['ln_Pu', 'ln_H', 'ln_GDP']:
    print(f"  {v:<10} = {model_between.params[v]:>8.4f} (SE={model_between.bse[v]:.4f}, p={model_between.pvalues[v]:.4e})")
print(f"  R-squared: {model_between.rsquared:.4f}")
print(f"  N countries: {len(country_means)}")

alpha_P = model_between.params['ln_Pu']
alpha_H = model_between.params['ln_H']
alpha_G = model_between.params['ln_GDP']
se_P = model_between.bse['ln_Pu']
se_H = model_between.bse['ln_H']
se_G = model_between.bse['ln_GDP']
p_P = model_between.pvalues['ln_Pu']
p_H = model_between.pvalues['ln_H']
p_G = model_between.pvalues['ln_GDP']

# -------------------------------------------------------
# 模型 3：TWFE (Country + Year FE) — 作为稳健性检验
# -------------------------------------------------------
country_dummies = pd.get_dummies(reg_df['country_code'], prefix='fc', drop_first=True, dtype=float)
X_twfe = reg_df[['ln_Pu', 'ln_H', 'ln_GDP']].copy()
X_twfe = pd.concat([X_twfe, country_dummies, year_dummies], axis=1)
X_twfe = sm.add_constant(X_twfe)
y_twfe = reg_df['ln_K']

model_twfe = sm.OLS(y_twfe, X_twfe).fit(cov_type='HC1')

print(f"\n--- 模型 3: TWFE (稳健性) ---")
for v in ['ln_Pu', 'ln_H', 'ln_GDP']:
    print(f"  {v:<10} = {model_twfe.params[v]:>8.4f} (SE={model_twfe.bse[v]:.4f}, p={model_twfe.pvalues[v]:.4e})")
print(f"  R-squared: {model_twfe.rsquared:.4f}")
print(f"  N: {model_twfe.nobs:.0f}")

# -------------------------------------------------------
# 选择 K* 预测模型
# -------------------------------------------------------
# 使用 Between Estimator 的系数进行 K* 预测
# 因为 K* 是"结构最优"，反映的是截面上 Pu, H, GDP 决定 K 的长期均衡
# TWFE 的 within 估计反映短期调整，不适合作为 K* 的结构弹性
print(f"\n==> 使用 Between Estimator 的系数用于 K* 预测")
print(f"    alpha_P = {alpha_P:.4f}")
print(f"    alpha_H = {alpha_H:.4f}")
print(f"    alpha_G = {alpha_G:.4f}")

# 计算 K*：使用 between 模型的系数 + 区域固定效应
# K*(i,t) = exp(a0 + aP*ln(Pu_it) + aH*ln(H_it) + aG*ln(GDP_it) + region_FE)
# 需要为每个观测获取区域 FE
# 从主面板获取 region 映射
country_region_map = df[['country_code', 'region']].drop_duplicates().set_index('country_code')['region']
if 'region' not in reg_df.columns:
    reg_df['region'] = reg_df['country_code'].map(country_region_map)

# 为 reg_df 中的每个观测计算预测值
X_pred = reg_df[['ln_Pu', 'ln_H', 'ln_GDP']].copy()
# 添加区域虚拟变量
reg_regions = pd.get_dummies(reg_df['region'], prefix='reg', drop_first=True, dtype=float)
X_pred = pd.concat([X_pred, reg_regions], axis=1)
X_pred = sm.add_constant(X_pred)

# 确保列对齐
for col in X_between.columns:
    if col not in X_pred.columns:
        X_pred[col] = 0
X_pred = X_pred[X_between.columns]

reg_df['ln_K_hat'] = model_between.predict(X_pred)
reg_df['K_star'] = np.exp(reg_df['ln_K_hat'])

print(f"\nK* 预测完成: {reg_df['K_star'].notna().sum()} 观测")

# 保存回归结果到文件
kstar_report = []
kstar_report.append("=" * 70)
kstar_report.append("K* Panel Regression Results")
kstar_report.append("=" * 70)
kstar_report.append("")
kstar_report.append("PREFERRED MODEL: Between Estimator (cross-sectional structural elasticities)")
kstar_report.append("Model: ln(K_bar) = a0 + aP*ln(Pu_bar) + aH*ln(H_bar) + aG*ln(GDP_bar) + Region FE")
kstar_report.append("Estimation: OLS on country-level time averages, HC1 Robust SE")
kstar_report.append("")
kstar_report.append(f"N countries:    {len(country_means)}")
kstar_report.append(f"R-squared:      {model_between.rsquared:.6f}")
kstar_report.append(f"Adj R-squared:  {model_between.rsquared_adj:.6f}")
kstar_report.append(f"F-statistic:    {model_between.fvalue:.2f}")
kstar_report.append("")
kstar_report.append("-" * 70)
kstar_report.append(f"{'Variable':<20} {'Coef':>10} {'Std Err':>10} {'t':>10} {'P>|t|':>12} {'[0.025':>10} {'0.975]':>10}")
kstar_report.append("-" * 70)

for var in ['const', 'ln_Pu', 'ln_H', 'ln_GDP']:
    ci = model_between.conf_int().loc[var]
    kstar_report.append(
        f"{var:<20} {model_between.params[var]:>10.4f} {model_between.bse[var]:>10.4f} "
        f"{model_between.tvalues[var]:>10.4f} {model_between.pvalues[var]:>12.4e} "
        f"{ci[0]:>10.4f} {ci[1]:>10.4f}"
    )

# Region FE
for var in [c for c in X_between.columns if c.startswith('reg_')]:
    ci = model_between.conf_int().loc[var]
    region_name = var.replace('reg_', '')
    kstar_report.append(
        f"{region_name:<20} {model_between.params[var]:>10.4f} {model_between.bse[var]:>10.4f} "
        f"{model_between.tvalues[var]:>10.4f} {model_between.pvalues[var]:>12.4e} "
        f"{ci[0]:>10.4f} {ci[1]:>10.4f}"
    )
kstar_report.append("-" * 70)
kstar_report.append("")
kstar_report.append("Interpretation:")
kstar_report.append(f"  alpha_P = {alpha_P:.4f}: 城镇人口每增加1%, K* 增加约 {alpha_P:.2f}%")
kstar_report.append(f"  alpha_H = {alpha_H:.4f}: 人力资本指数每增加1%, K* 增加约 {alpha_H:.2f}%")
kstar_report.append(f"  alpha_G = {alpha_G:.4f}: GDP每增加1%, K* 增加约 {alpha_G:.2f}%")
kstar_report.append("")

# Mundlak 结果
kstar_report.append("")
kstar_report.append("=" * 70)
kstar_report.append("ROBUSTNESS 1: Mundlak (Correlated Random Effects)")
kstar_report.append("Model: ln(K) = aP*ln(Pu) + aH*ln(H) + aG*ln(GDP) + bar(X) + Year FE")
kstar_report.append("=" * 70)
kstar_report.append("")
kstar_report.append(f"N observations: {model_mundlak.nobs:.0f}")
kstar_report.append(f"R-squared:      {model_mundlak.rsquared:.6f}")
kstar_report.append("")
kstar_report.append(f"{'Variable':<20} {'Coef':>10} {'Std Err':>10} {'P>|t|':>12}")
kstar_report.append("-" * 55)
for v in ['ln_Pu', 'ln_H', 'ln_GDP', 'ln_Pu_bar', 'ln_H_bar', 'ln_GDP_bar']:
    kstar_report.append(
        f"{v:<20} {model_mundlak.params[v]:>10.4f} {model_mundlak.bse[v]:>10.4f} {model_mundlak.pvalues[v]:>12.4e}"
    )
kstar_report.append("")
kstar_report.append(f"Between effects (within + bar):")
kstar_report.append(f"  alpha_P_between = {alpha_P_between:.4f}")
kstar_report.append(f"  alpha_H_between = {alpha_H_between:.4f}")
kstar_report.append(f"  alpha_G_between = {alpha_G_between:.4f}")

# TWFE 结果
kstar_report.append("")
kstar_report.append("=" * 70)
kstar_report.append("ROBUSTNESS 2: Two-Way Fixed Effects (Country + Year FE)")
kstar_report.append("=" * 70)
kstar_report.append("")
kstar_report.append(f"N observations: {model_twfe.nobs:.0f}")
kstar_report.append(f"R-squared:      {model_twfe.rsquared:.6f}")
kstar_report.append("")
kstar_report.append(f"{'Variable':<20} {'Coef':>10} {'Std Err':>10} {'P>|t|':>12}")
kstar_report.append("-" * 55)
for v in ['ln_Pu', 'ln_H', 'ln_GDP']:
    kstar_report.append(
        f"{v:<20} {model_twfe.params[v]:>10.4f} {model_twfe.bse[v]:>10.4f} {model_twfe.pvalues[v]:>12.4e}"
    )
kstar_report.append("")
kstar_report.append("Note: TWFE within-estimator captures short-run adjustment dynamics.")
kstar_report.append("Negative within-coefficients for H and GDP are expected due to")
kstar_report.append("multicollinearity between K (PIM-based) and GDP within countries.")
kstar_report.append("The between estimator better captures structural long-run elasticities.")

kstar_path = os.path.join(MODELS, 'kstar_regression.txt')
with open(kstar_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(kstar_report))
print(f"\nK* 回归结果已保存: {kstar_path}")

# ============================================================
# 步骤 3：计算 OCR 和 UCI
# ============================================================
print("\n" + "=" * 60)
print("步骤 3：计算 OCR 和 UCI")
print("=" * 60)

# 将 K_star 合并回主面板
kstar_cols = reg_df[['country_code', 'year', 'K_star', 'ln_K_hat']].copy()
df = df.merge(kstar_cols, on=['country_code', 'year'], how='left')

# OCR = K / K*
df['OCR'] = df['K'] / df['K_star']

# UCI = Q / OCR = V * K* / K^2
df['UCI'] = df['Q'] / df['OCR']

# 描述性统计
for name, series in [('OCR', df['OCR']), ('UCI', df['UCI']), ('Q', df['Q'])]:
    valid = series.dropna()
    # 去极端值
    q01, q99 = valid.quantile(0.01), valid.quantile(0.99)
    trimmed = valid[(valid >= q01) & (valid <= q99)]
    print(f"\n{name} 描述性统计 (N={len(valid)}, trimmed N={len(trimmed)}):")
    print(f"  Mean:   {trimmed.mean():.4f}")
    print(f"  Median: {trimmed.median():.4f}")
    print(f"  Std:    {trimmed.std():.4f}")
    print(f"  P25:    {trimmed.quantile(0.25):.4f}")
    print(f"  P75:    {trimmed.quantile(0.75):.4f}")

ocr_valid = df['OCR'].dropna()
print(f"\n过度建设 (OCR > 1): {(ocr_valid > 1).sum()} / {len(ocr_valid)} ({100*(ocr_valid > 1).mean():.1f}%)")
print(f"建设不足 (OCR < 1): {(ocr_valid < 1).sum()} / {len(ocr_valid)} ({100*(ocr_valid < 1).mean():.1f}%)")

# 按收入组统计
print(f"\nOCR 按收入组 (中位数):")
ocr_by_inc = df.dropna(subset=['OCR', 'income_group']).groupby('income_group')['OCR'].agg(['count', 'mean', 'median', 'std'])
print(ocr_by_inc.to_string())

print(f"\nUCI 按收入组 (中位数):")
uci_by_inc = df.dropna(subset=['UCI', 'income_group']).groupby('income_group')['UCI'].agg(['count', 'mean', 'median', 'std'])
print(uci_by_inc.to_string())

# ============================================================
# 步骤 4：倒 U 型跨国回归
# ============================================================
print("\n" + "=" * 60)
print("步骤 4：倒 U 型跨国回归")
print("=" * 60)

# dV/V = a + b*(I/GDP) - c*(I/GDP)^2 + X*gamma + mu_i + lambda_t
inv_df = df[['country_code', 'year', 'dV_V', 'inv_gdp_ratio',
             'urban_rate', 'services_share', 'H', 'total_pop']].dropna().copy()

# 人口增长率
inv_df = inv_df.sort_values(['country_code', 'year'])
inv_df['pop_growth'] = inv_df.groupby('country_code')['total_pop'].pct_change() * 100
inv_df = inv_df.dropna(subset=['pop_growth'])

# 投资/GDP 比率
inv_df['I_GDP'] = inv_df['inv_gdp_ratio']
inv_df['I_GDP_sq'] = inv_df['I_GDP'] ** 2

# 排除极端值
inv_df = inv_df[(inv_df['dV_V'] > inv_df['dV_V'].quantile(0.01)) &
                (inv_df['dV_V'] < inv_df['dV_V'].quantile(0.99))].copy()

print(f"倒 U 型回归样本: {inv_df.shape[0]} 观测, {inv_df['country_code'].nunique()} 国")

# 控制变量
inv_df['ln_H'] = np.log(inv_df['H'].clip(lower=0.1))

# 固定效应
c_dummies = pd.get_dummies(inv_df['country_code'], prefix='fc', drop_first=True, dtype=float)
y_dummies = pd.get_dummies(inv_df['year'], prefix='fy', drop_first=True, dtype=float)

X_inv = inv_df[['I_GDP', 'I_GDP_sq', 'urban_rate', 'services_share', 'ln_H', 'pop_growth']].copy()
X_inv_full = pd.concat([X_inv, c_dummies, y_dummies], axis=1)
X_inv_full = sm.add_constant(X_inv_full)
y_inv = inv_df['dV_V']

model_inv_u = sm.OLS(y_inv, X_inv_full).fit(cov_type='HC1')

b_coef = model_inv_u.params['I_GDP']
c_coef = model_inv_u.params['I_GDP_sq']
b_se = model_inv_u.bse['I_GDP']
c_se = model_inv_u.bse['I_GDP_sq']

# 最优投资率和破坏阈值
if c_coef < 0:
    I_opt = -b_coef / (2 * c_coef)
    I_destroy = -b_coef / c_coef
else:
    I_opt = np.nan
    I_destroy = np.nan

print(f"\n倒 U 型回归核心结果:")
print(f"  b (I/GDP):     {b_coef:.6f} (SE={b_se:.6f}, p={model_inv_u.pvalues['I_GDP']:.4e})")
print(f"  c (I/GDP)^2:   {c_coef:.6f} (SE={c_se:.6f}, p={model_inv_u.pvalues['I_GDP_sq']:.4e})")
print(f"  I*_opt:        {I_opt:.2f}% of GDP")
print(f"  I_destroy:     {I_destroy:.2f}% of GDP")
print(f"  R-squared:     {model_inv_u.rsquared:.4f}")
print(f"  N:             {model_inv_u.nobs:.0f}")

# 控制变量
print(f"\n控制变量:")
for var in ['urban_rate', 'services_share', 'ln_H', 'pop_growth']:
    print(f"  {var:<20} {model_inv_u.params[var]:>10.6f} (SE={model_inv_u.bse[var]:.6f}, p={model_inv_u.pvalues[var]:.4e})")

# 保存倒 U 型结果
inv_u_report = []
inv_u_report.append("=" * 70)
inv_u_report.append("Global Inverted-U Regression Results")
inv_u_report.append("Model: dV/V = a + b*(I/GDP) + c*(I/GDP)^2 + X*gamma + mu_i + lambda_t")
inv_u_report.append("Estimation: OLS + Country FE + Year FE, HC1 Robust SE")
inv_u_report.append("=" * 70)
inv_u_report.append("")
inv_u_report.append(f"N observations: {model_inv_u.nobs:.0f}")
inv_u_report.append(f"N countries:    {inv_df['country_code'].nunique()}")
inv_u_report.append(f"Year range:     {inv_df['year'].min()} - {inv_df['year'].max()}")
inv_u_report.append(f"R-squared:      {model_inv_u.rsquared:.6f}")
inv_u_report.append(f"Adj R-squared:  {model_inv_u.rsquared_adj:.6f}")
inv_u_report.append(f"AIC:            {model_inv_u.aic:.2f}")
inv_u_report.append(f"BIC:            {model_inv_u.bic:.2f}")
inv_u_report.append("")
inv_u_report.append("-" * 70)
inv_u_report.append(f"{'Variable':<20} {'Coef':>12} {'Std Err':>10} {'t':>10} {'P>|t|':>12} {'[0.025':>10} {'0.975]':>10}")
inv_u_report.append("-" * 70)

key_vars = ['I_GDP', 'I_GDP_sq', 'urban_rate', 'services_share', 'ln_H', 'pop_growth']
for var in key_vars:
    ci = model_inv_u.conf_int().loc[var]
    inv_u_report.append(
        f"{var:<20} {model_inv_u.params[var]:>12.6f} {model_inv_u.bse[var]:>10.6f} "
        f"{model_inv_u.tvalues[var]:>10.4f} {model_inv_u.pvalues[var]:>12.4e} "
        f"{ci[0]:>10.6f} {ci[1]:>10.6f}"
    )
inv_u_report.append("-" * 70)
inv_u_report.append("")
inv_u_report.append("Derived Parameters:")
inv_u_report.append(f"  I*_opt  = -b/(2c) = {I_opt:.2f}% of GDP  (value-maximizing investment rate)")
inv_u_report.append(f"  I_dest  = -b/c    = {I_destroy:.2f}% of GDP  (value-destroying threshold)")
inv_u_report.append("")
inv_u_report.append("Note: Country and year fixed effects included but not shown.")
inv_u_report.append("Standard errors are heteroskedasticity-robust (HC1).")
inv_u_report.append("Dependent variable: annual change rate of asset value proxy (dV/V).")
inv_u_report.append("Sample trimmed at 1st/99th percentile of dV/V to reduce outlier influence.")

inv_u_path = os.path.join(MODELS, 'global_inverted_u_regression.txt')
with open(inv_u_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(inv_u_report))
print(f"\n倒 U 型回归结果已保存: {inv_u_path}")

# ============================================================
# 步骤 5：可视化
# ============================================================
print("\n" + "=" * 60)
print("步骤 5：可视化")
print("=" * 60)

fig = plt.figure(figsize=(18, 6))
gs = gridspec.GridSpec(1, 3, wspace=0.32)

# --- 图 A：K* 回归拟合优度 ---
ax1 = fig.add_subplot(gs[0])
plot_df = reg_df.dropna(subset=['ln_K', 'ln_K_hat']).copy()
if len(plot_df) > 3000:
    plot_sample = plot_df.sample(3000, random_state=42)
else:
    plot_sample = plot_df

ax1.scatter(plot_sample['ln_K_hat'], plot_sample['ln_K'],
            alpha=0.15, s=8, color='#2166AC', edgecolors='none')
lims = [min(plot_sample['ln_K_hat'].min(), plot_sample['ln_K'].min()),
        max(plot_sample['ln_K_hat'].max(), plot_sample['ln_K'].max())]
ax1.plot(lims, lims, 'k--', linewidth=1, alpha=0.7, label='45-degree line')
ax1.set_xlabel('Predicted ln(K)', fontsize=11)
ax1.set_ylabel('Actual ln(K)', fontsize=11)
ax1.set_title(f'A. K* Regression Fit (Between Estimator)\n($R^2$ = {model_between.rsquared:.4f}, N = {len(country_means)} countries)',
              fontsize=11, fontweight='bold')
ax1.legend(fontsize=9)

# 标注核心弹性
textstr = (f'$\\alpha_P$ = {alpha_P:.3f}\n'
           f'$\\alpha_H$ = {alpha_H:.3f}\n'
           f'$\\alpha_G$ = {alpha_G:.3f}')
ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=9,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 计算面板层面 R2（实际 vs 预测的相关系数）
corr_panel = np.corrcoef(plot_df['ln_K'], plot_df['ln_K_hat'])[0, 1]
ax1.text(0.05, 0.72, f'Panel $r$ = {corr_panel:.3f}', transform=ax1.transAxes, fontsize=9,
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# --- 图 B：OCR 按收入组的箱线图 ---
ax2 = fig.add_subplot(gs[1])
ocr_plot = df.dropna(subset=['OCR', 'income_group']).copy()
ocr_plot = ocr_plot[ocr_plot['OCR'].between(0.1, 5.0)]
income_order = ['Low', 'Lower-middle', 'Upper-middle', 'High']
ocr_groups = [ocr_plot[ocr_plot['income_group'] == g]['OCR'].values for g in income_order]

# 过滤空组
valid_groups = [(g, data) for g, data in zip(income_order, ocr_groups) if len(data) > 0]
labels = [g for g, _ in valid_groups]
data = [d for _, d in valid_groups]

bp = ax2.boxplot(data, labels=labels, patch_artist=True,
                 showfliers=False, widths=0.6)
colors_box = ['#D73027', '#FC8D59', '#91BFDB', '#4575B4'][:len(labels)]
for patch, color in zip(bp['boxes'], colors_box):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=1, alpha=0.7, label='OCR = 1 (balanced)')
ax2.set_ylabel('OCR (K / K*)', fontsize=11)
ax2.set_xlabel('Income Group', fontsize=11)
ax2.set_title('B. Overcapacity Ratio by Income Group', fontsize=11, fontweight='bold')
ax2.legend(fontsize=8)

for i, (g, d) in enumerate(valid_groups):
    med = np.median(d)
    ax2.text(i + 1, med + 0.08, f'{med:.2f}\n(n={len(d)})', ha='center', fontsize=7.5)

# --- 图 C：UCI vs Urban Q ---
ax3 = fig.add_subplot(gs[2])
uci_plot = df.dropna(subset=['UCI', 'Q', 'income_group']).copy()
uci_plot = uci_plot[(uci_plot['UCI'].between(0, 8)) & (uci_plot['Q'].between(0, 8))]

color_map = {'Low': '#D73027', 'Lower-middle': '#FC8D59',
             'Upper-middle': '#91BFDB', 'High': '#4575B4'}
for group in income_order:
    sub = uci_plot[uci_plot['income_group'] == group]
    if len(sub) > 0:
        ax3.scatter(sub['Q'], sub['UCI'], alpha=0.12, s=6,
                    color=color_map[group], label=group, edgecolors='none')

# 标注关键国家
highlight_countries = ['CHN', 'USA', 'JPN', 'DEU', 'BRA', 'IND', 'GBR', 'NGA', 'SAU']
latest_year_data = uci_plot.sort_values('year').groupby('country_code').last().reset_index()
for cc in highlight_countries:
    row = latest_year_data[latest_year_data['country_code'] == cc]
    if len(row) > 0 and not pd.isna(row.iloc[0]['UCI']):
        x, y_val = row.iloc[0]['Q'], row.iloc[0]['UCI']
        if 0 < x < 8 and 0 < y_val < 8:
            ax3.annotate(cc, (x, y_val), fontsize=7, fontweight='bold',
                         xytext=(5, 5), textcoords='offset points',
                         bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow', alpha=0.6))

ax3.axhline(y=1.0, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)
ax3.axvline(x=1.0, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)
ax3.set_xlabel('Urban Q (V / K)', fontsize=11)
ax3.set_ylabel('UCI (Q / OCR)', fontsize=11)
ax3.set_title('C. UCI vs Urban Q', fontsize=11, fontweight='bold')
ax3.legend(fontsize=8, loc='upper right', markerscale=3)

plt.suptitle('Figure 11: K* Estimation, Overcapacity Ratio & Urban Coordination Index',
             fontsize=13, fontweight='bold', y=1.02)
fig_path = os.path.join(FIGS, 'fig11_kstar_ocr_uci.png')
plt.savefig(fig_path, dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
print(f"图表已保存: {fig_path}")

# ============================================================
# 步骤 6：输出面板
# ============================================================
print("\n" + "=" * 60)
print("步骤 6：输出 K*/OCR/UCI 面板")
print("=" * 60)

out_cols = ['country_code', 'country_name', 'region', 'income_group', 'year',
            'K', 'V', 'Q', 'GDP', 'Pu', 'H', 'urban_rate', 'services_share',
            'working_age_pct', 'inv_gdp_ratio', 'dV_V',
            'K_star', 'OCR', 'UCI']
out_df = df[out_cols].copy()
out_df = out_df.sort_values(['country_code', 'year']).reset_index(drop=True)

csv_path = os.path.join(DATA_PROC, 'global_kstar_ocr_uci.csv')
out_df.to_csv(csv_path, index=False)
print(f"面板数据已保存: {csv_path}")
print(f"  总行数: {out_df.shape[0]}")
print(f"  含 K* 的行数: {out_df['K_star'].notna().sum()}")
print(f"  含 OCR 的行数: {out_df['OCR'].notna().sum()}")
print(f"  含 UCI 的行数: {out_df['UCI'].notna().sum()}")

# 代表性国家最新数据
print("\n代表性国家最新年份 K*/OCR/UCI:")
showcase = ['CHN', 'USA', 'JPN', 'DEU', 'GBR', 'BRA', 'IND', 'NGA', 'SAU']
latest_showcase = out_df.dropna(subset=['UCI']).sort_values('year').groupby('country_code').last()
for cc in showcase:
    if cc in latest_showcase.index:
        r = latest_showcase.loc[cc]
        print(f"  {cc} ({int(r['year'])}): Q={r['Q']:.3f}, OCR={r['OCR']:.3f}, UCI={r['UCI']:.3f}")

print("\n" + "=" * 60)
print("全部完成!")
print("=" * 60)
