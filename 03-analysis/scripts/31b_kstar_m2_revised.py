#!/usr/bin/env python3
"""
31b_kstar_m2_revised.py
========================
目的：用降维模型 M2 重新估计 K*，重算全球 158 国的 OCR 和 UCI
      M2 用 GDP per capita 替代分别纳入的 GDP 和 hc，避免共线性

动机：M1 中 alpha_H 在 Between (+3.978) 和 TWFE (-3.965) 之间符号反转，
      说明 Cobb-Douglas 函数形式存在多重共线性问题。
      M2 降维模型: ln(K) = a0 + aP*ln(P_urban) + aD*ln(GDP_per_capita)

输入：
  - 02-data/processed/global_urban_q_panel.csv
  - 02-data/processed/global_kstar_ocr_uci.csv  (M1 结果，用于比较)
输出：
  - 02-data/processed/global_kstar_m2_panel.csv
  - 03-analysis/models/kstar_m2_report.txt
  - 04-figures/drafts/fig_kstar_m2.png
依赖：pandas, numpy, statsmodels, scipy, matplotlib, sklearn
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats
from sklearn.cluster import KMeans
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

warnings.filterwarnings('ignore')
np.random.seed(42)

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

report = []  # 累积报告文本

def rpt(line=''):
    """同时打印和记录到报告"""
    print(line)
    report.append(line)

# ============================================================
# 步骤 0：加载数据
# ============================================================
rpt("=" * 70)
rpt("31b_kstar_m2_revised.py — M2 降维 K* 模型")
rpt("=" * 70)
rpt()

# 加载 Urban Q 面板
uq = pd.read_csv(os.path.join(DATA_PROC, 'global_urban_q_panel.csv'))
rpt(f"Urban Q 面板: {uq.shape[0]} 行, {uq['country_code'].nunique()} 国")

# 加载 PWT 补充数据
pwt_path = os.path.join(DATA_RAW, 'penn_world_table.csv')
if os.path.exists(pwt_path):
    pwt = pd.read_csv(pwt_path, encoding='utf-8-sig')
    pwt_sub = pwt[['countrycode', 'year', 'hc', 'rnna', 'rgdpna', 'pop', 'emp', 'csh_i', 'delta']].copy()
    pwt_sub.rename(columns={'countrycode': 'country_code',
                             'hc': 'hc_pwt',
                             'rnna': 'rnna_pwt',
                             'rgdpna': 'rgdpna_pwt'}, inplace=True)
    df = uq.merge(pwt_sub, on=['country_code', 'year'], how='left')
    rpt(f"PWT 合并后: {df.shape[0]} 行")
else:
    df = uq.copy()
    rpt("PWT 文件未找到，仅使用 Urban Q 面板数据")

# 统一关键变量
df['K'] = df['K_best'].fillna(df.get('rnna_pwt', df.get('rnna')))
df['V'] = df['V3']
df['Q'] = df['urban_q']
df['GDP'] = df['gdp_constant_2015']
df['Pu'] = df['urban_pop']
df['H'] = df['hc'].fillna(df.get('hc_pwt', pd.Series(dtype=float)))
df['urban_rate'] = df['urban_pct']
df['total_pop_col'] = df['total_pop']
df['dV_V'] = df['delta_V_ratio']

# GDP per capita（M2 的核心变量）
df['GDP_pc'] = df['GDP'] / df['total_pop_col']

# 收入分组
latest_gdp = df.dropna(subset=['GDP', 'total_pop_col']).copy()
latest_gdp['gdp_pc_tmp'] = latest_gdp['GDP'] / latest_gdp['total_pop_col']
latest = latest_gdp.sort_values('year').groupby('country_code')['gdp_pc_tmp'].last().reset_index()
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

rpt(f"\n收入分组分布:")
for g, n in df.groupby('income_group')['country_code'].nunique().items():
    rpt(f"  {g}: {n} 国")

# ============================================================
# Part A: M2 降维 K* 模型
# ============================================================
rpt("\n" + "=" * 70)
rpt("Part A: M2 降维 K* 模型")
rpt("  ln(K) = a0 + aP*ln(P_urban) + aD*ln(GDP_per_capita) + Region FE")
rpt("=" * 70)

# 准备回归样本
reg_df = df[['country_code', 'region', 'year', 'K', 'Pu', 'GDP_pc', 'H', 'GDP']].dropna(
    subset=['K', 'Pu', 'GDP_pc']
).copy()
reg_df = reg_df[(reg_df['K'] > 0) & (reg_df['Pu'] > 0) & (reg_df['GDP_pc'] > 0)]
rpt(f"\n回归样本: {reg_df.shape[0]} 观测, {reg_df['country_code'].nunique()} 国")

# 取对数
reg_df['ln_K'] = np.log(reg_df['K'])
reg_df['ln_Pu'] = np.log(reg_df['Pu'])
reg_df['ln_D'] = np.log(reg_df['GDP_pc'])  # D = GDP per capita

# -----------------------------------------------------------
# A1. 主模型：Between Estimator
# -----------------------------------------------------------
rpt("\n--- A1. 主模型: Between Estimator ---")
country_means = reg_df.groupby('country_code')[['ln_K', 'ln_Pu', 'ln_D']].mean().reset_index()
country_means = country_means.merge(
    reg_df[['country_code', 'region']].drop_duplicates(),
    on='country_code', how='left'
)
region_dummies_be = pd.get_dummies(country_means['region'], prefix='reg', drop_first=True, dtype=float)

X_between = country_means[['ln_Pu', 'ln_D']].copy()
X_between = pd.concat([X_between, region_dummies_be], axis=1)
X_between = sm.add_constant(X_between)
y_between = country_means['ln_K']

model_between = sm.OLS(y_between, X_between).fit(cov_type='HC1')

rpt(f"  N countries: {len(country_means)}")
rpt(f"  R-squared:   {model_between.rsquared:.6f}")
rpt(f"  Adj R-sq:    {model_between.rsquared_adj:.6f}")
rpt(f"  F-statistic: {model_between.fvalue:.2f}")
rpt()

# 系数表
rpt(f"  {'Variable':<15} {'Coef':>10} {'SE':>10} {'t':>10} {'P>|t|':>12} {'[0.025':>10} {'0.975]':>10}")
rpt("  " + "-" * 80)
for var in model_between.params.index:
    ci = model_between.conf_int().loc[var]
    label = var.replace('reg_', '') if var.startswith('reg_') else var
    rpt(f"  {label:<15} {model_between.params[var]:>10.4f} {model_between.bse[var]:>10.4f} "
        f"{model_between.tvalues[var]:>10.4f} {model_between.pvalues[var]:>12.4e} "
        f"{ci[0]:>10.4f} {ci[1]:>10.4f}")

alpha_P = model_between.params['ln_Pu']
alpha_D = model_between.params['ln_D']
se_P = model_between.bse['ln_Pu']
se_D = model_between.bse['ln_D']

rpt(f"\n  核心弹性:")
rpt(f"    alpha_P = {alpha_P:.4f}: 城镇人口 +1% => K* +{alpha_P:.2f}%")
rpt(f"    alpha_D = {alpha_D:.4f}: 人均 GDP +1% => K* +{alpha_D:.2f}%")

# VIF 诊断
X_vif = country_means[['ln_Pu', 'ln_D']].copy()
X_vif = sm.add_constant(X_vif)
vif_data = pd.DataFrame({
    'Variable': X_vif.columns,
    'VIF': [variance_inflation_factor(X_vif.values, i) for i in range(X_vif.shape[1])]
})
rpt(f"\n  VIF 诊断 (M2 降维模型):")
for _, row in vif_data.iterrows():
    if row['Variable'] != 'const':
        rpt(f"    {row['Variable']}: {row['VIF']:.2f}")

# 与 M1 的 VIF 对比（如果有 H 和 GDP 分开的数据）
reg_m1_check = reg_df.dropna(subset=['H', 'GDP']).copy()
if len(reg_m1_check) > 100:
    reg_m1_check['ln_H'] = np.log(reg_m1_check['H'].clip(lower=0.01))
    reg_m1_check['ln_GDP'] = np.log(reg_m1_check['GDP'])
    cm1 = reg_m1_check.groupby('country_code')[['ln_Pu', 'ln_H', 'ln_GDP']].mean().dropna()
    if len(cm1) > 10:
        X_vif_m1 = sm.add_constant(cm1)
        vif_m1 = [variance_inflation_factor(X_vif_m1.values, i) for i in range(X_vif_m1.shape[1])]
        rpt(f"\n  VIF 诊断 (M1 原模型, 供对比):")
        for var, v in zip(X_vif_m1.columns, vif_m1):
            if var != 'const':
                rpt(f"    {var}: {v:.2f}")

# -----------------------------------------------------------
# A2. 稳健性 1：Mundlak (within)
# -----------------------------------------------------------
rpt("\n--- A2. 稳健性 1: Mundlak (Correlated RE) ---")
for col in ['ln_Pu', 'ln_D']:
    reg_df[f'{col}_bar'] = reg_df.groupby('country_code')[col].transform('mean')

year_dummies = pd.get_dummies(reg_df['year'], prefix='fy', drop_first=True, dtype=float)
X_mundlak = reg_df[['ln_Pu', 'ln_D', 'ln_Pu_bar', 'ln_D_bar']].copy()
X_mundlak = pd.concat([X_mundlak, year_dummies], axis=1)
X_mundlak = sm.add_constant(X_mundlak)
y_mundlak = reg_df['ln_K']

model_mundlak = sm.OLS(y_mundlak, X_mundlak).fit(
    cov_type='cluster', cov_kwds={'groups': reg_df['country_code']}
)

rpt(f"  N observations: {model_mundlak.nobs:.0f}")
rpt(f"  R-squared:      {model_mundlak.rsquared:.6f}")
rpt()
for v in ['ln_Pu', 'ln_D', 'ln_Pu_bar', 'ln_D_bar']:
    rpt(f"  {v:<15} = {model_mundlak.params[v]:>8.4f} (SE={model_mundlak.bse[v]:.4f}, p={model_mundlak.pvalues[v]:.4e})")

alpha_P_mundlak_between = model_mundlak.params['ln_Pu'] + model_mundlak.params['ln_Pu_bar']
alpha_D_mundlak_between = model_mundlak.params['ln_D'] + model_mundlak.params['ln_D_bar']
rpt(f"\n  Between 效应 (within + bar):")
rpt(f"    alpha_P_between = {alpha_P_mundlak_between:.4f}")
rpt(f"    alpha_D_between = {alpha_D_mundlak_between:.4f}")

# -----------------------------------------------------------
# A3. 稳健性 2：TWFE
# -----------------------------------------------------------
rpt("\n--- A3. 稳健性 2: TWFE (Country + Year FE) ---")
country_dummies = pd.get_dummies(reg_df['country_code'], prefix='fc', drop_first=True, dtype=float)
X_twfe = reg_df[['ln_Pu', 'ln_D']].copy()
X_twfe = pd.concat([X_twfe, country_dummies, year_dummies], axis=1)
X_twfe = sm.add_constant(X_twfe)
y_twfe = reg_df['ln_K']

model_twfe = sm.OLS(y_twfe, X_twfe).fit(cov_type='HC1')

rpt(f"  N observations: {model_twfe.nobs:.0f}")
rpt(f"  R-squared:      {model_twfe.rsquared:.6f}")
for v in ['ln_Pu', 'ln_D']:
    rpt(f"  {v:<10} = {model_twfe.params[v]:>8.4f} (SE={model_twfe.bse[v]:.4f}, p={model_twfe.pvalues[v]:.4e})")

# -----------------------------------------------------------
# A4. 三种估计的比较汇总
# -----------------------------------------------------------
rpt("\n--- A4. 三种估计比较 ---")
rpt(f"  {'Estimator':<20} {'alpha_P':>10} {'alpha_D':>10} {'R2':>10} {'Sign consistent':>18}")
rpt("  " + "-" * 70)
rpt(f"  {'Between':<20} {alpha_P:>10.4f} {alpha_D:>10.4f} {model_between.rsquared:>10.4f} {'--':>18}")
rpt(f"  {'Mundlak (between)':<20} {alpha_P_mundlak_between:>10.4f} {alpha_D_mundlak_between:>10.4f} {model_mundlak.rsquared:>10.4f} "
    f"{'Yes' if alpha_P_mundlak_between > 0 and alpha_D_mundlak_between > 0 else 'NO':>18}")
twfe_aP = model_twfe.params['ln_Pu']
twfe_aD = model_twfe.params['ln_D']
rpt(f"  {'TWFE (within)':<20} {twfe_aP:>10.4f} {twfe_aD:>10.4f} {model_twfe.rsquared:>10.4f} "
    f"{'Yes' if twfe_aP > 0 and twfe_aD > 0 else 'NO':>18}")

# 与 M1 比较：M1 的 alpha_H 符号反转问题
rpt(f"\n  关键改进: M1 alpha_H Between=+3.978, TWFE=-3.965 (符号反转)")
rpt(f"           M2 alpha_D Between={alpha_D:+.4f}, TWFE={twfe_aD:+.4f} "
    f"({'符号一致' if (alpha_D > 0) == (twfe_aD > 0) else '符号反转'})")

# -----------------------------------------------------------
# A5. Translog 函数形式检验
# -----------------------------------------------------------
rpt("\n--- A5. Translog 函数形式检验 ---")
rpt("  ln(K) = a + b1*lnP + b2*lnD + b3*(lnP)^2 + b4*(lnD)^2 + b5*lnP*lnD")

country_means['ln_Pu_sq'] = country_means['ln_Pu'] ** 2
country_means['ln_D_sq'] = country_means['ln_D'] ** 2
country_means['ln_Pu_ln_D'] = country_means['ln_Pu'] * country_means['ln_D']

X_translog = country_means[['ln_Pu', 'ln_D', 'ln_Pu_sq', 'ln_D_sq', 'ln_Pu_ln_D']].copy()
X_translog = pd.concat([X_translog, region_dummies_be], axis=1)
X_translog = sm.add_constant(X_translog)

model_translog = sm.OLS(y_between, X_translog).fit(cov_type='HC1')

rpt(f"  N countries: {len(country_means)}")
rpt(f"  R-squared:   {model_translog.rsquared:.6f}")
rpt()
for v in ['ln_Pu', 'ln_D', 'ln_Pu_sq', 'ln_D_sq', 'ln_Pu_ln_D']:
    rpt(f"  {v:<15} = {model_translog.params[v]:>8.4f} (SE={model_translog.bse[v]:.4f}, p={model_translog.pvalues[v]:.4e})")

# F 检验: Cobb-Douglas 约束 (b3=b4=b5=0)
# 受限模型 = model_between (Cobb-Douglas), 无限制模型 = model_translog
RSS_r = model_between.ssr
RSS_u = model_translog.ssr
q = 3  # 3 个约束
n = len(country_means)
k_u = len(model_translog.params)
F_stat = ((RSS_r - RSS_u) / q) / (RSS_u / (n - k_u))
p_F = 1 - stats.f.cdf(F_stat, q, n - k_u)

rpt(f"\n  Cobb-Douglas 约束检验 (H0: b3=b4=b5=0):")
rpt(f"    F({q}, {n - k_u}) = {F_stat:.4f}")
rpt(f"    p-value = {p_F:.6f}")
if p_F > 0.05:
    rpt(f"    => 不能拒绝 Cobb-Douglas 约束 (p > 0.05)，M2 的 C-D 形式可接受")
else:
    rpt(f"    => 拒绝 Cobb-Douglas 约束 (p < 0.05)，Translog 拟合更优")
    rpt(f"    => 但 C-D 作为简约模型仍有解释价值，可在论文中讨论")


# ============================================================
# Part B: 全球 OCR 重算
# ============================================================
rpt("\n" + "=" * 70)
rpt("Part B: 用 M2 重算全球 OCR")
rpt("=" * 70)

# B1. 计算 K*(i,t) 使用 M2 Between Estimator
rpt("\n--- B1. 计算 K*(i,t) ---")

# 为 reg_df 构建预测矩阵
X_pred = reg_df[['ln_Pu', 'ln_D']].copy()
reg_regions = pd.get_dummies(reg_df['region'], prefix='reg', drop_first=True, dtype=float)
X_pred = pd.concat([X_pred, reg_regions], axis=1)
X_pred = sm.add_constant(X_pred)

# 确保列对齐
for col in X_between.columns:
    if col not in X_pred.columns:
        X_pred[col] = 0
X_pred = X_pred[X_between.columns]

reg_df['ln_K_hat_m2'] = model_between.predict(X_pred)
reg_df['K_star_m2'] = np.exp(reg_df['ln_K_hat_m2'])

rpt(f"  K* 预测完成: {reg_df['K_star_m2'].notna().sum()} 观测")

# 合并回主面板
kstar_cols = reg_df[['country_code', 'year', 'K_star_m2', 'ln_K_hat_m2']].copy()
df = df.merge(kstar_cols, on=['country_code', 'year'], how='left')

# OCR_m2 = K / K*_m2
df['OCR_m2'] = df['K'] / df['K_star_m2']

rpt(f"  OCR_m2 计算完成: {df['OCR_m2'].notna().sum()} 观测")

# B2. 比较 M1 和 M2 的 OCR
rpt("\n--- B2. M1 vs M2 OCR 比较 ---")

# 加载 M1 结果
m1_path = os.path.join(DATA_PROC, 'global_kstar_ocr_uci.csv')
if os.path.exists(m1_path):
    m1_df = pd.read_csv(m1_path)
    m1_ocr = m1_df[['country_code', 'year', 'OCR', 'K_star']].rename(
        columns={'OCR': 'OCR_m1', 'K_star': 'K_star_m1'}
    )
    df = df.merge(m1_ocr, on=['country_code', 'year'], how='left')

    # Spearman rank correlation（使用最新年份截面数据）
    latest_ocr = df.dropna(subset=['OCR_m1', 'OCR_m2']).sort_values('year').groupby('country_code').last().reset_index()
    spearman_r, spearman_p = stats.spearmanr(latest_ocr['OCR_m1'], latest_ocr['OCR_m2'])
    pearson_r, pearson_p = stats.pearsonr(latest_ocr['OCR_m1'], latest_ocr['OCR_m2'])

    rpt(f"  比较样本: {len(latest_ocr)} 国 (最新年份截面)")
    rpt(f"  Spearman rank correlation: rho = {spearman_r:.4f}, p = {spearman_p:.4e}")
    rpt(f"  Pearson correlation:       r   = {pearson_r:.4f}, p = {pearson_p:.4e}")

    # 前 20 / 后 20 重叠度
    top20_m1 = set(latest_ocr.nlargest(20, 'OCR_m1')['country_code'])
    top20_m2 = set(latest_ocr.nlargest(20, 'OCR_m2')['country_code'])
    bot20_m1 = set(latest_ocr.nsmallest(20, 'OCR_m1')['country_code'])
    bot20_m2 = set(latest_ocr.nsmallest(20, 'OCR_m2')['country_code'])

    rpt(f"\n  Top-20 过度建设国 重叠: {len(top20_m1 & top20_m2)}/20")
    rpt(f"    M1 only: {sorted(top20_m1 - top20_m2)}")
    rpt(f"    M2 only: {sorted(top20_m2 - top20_m1)}")
    rpt(f"  Bottom-20 建设不足国 重叠: {len(bot20_m1 & bot20_m2)}/20")
    rpt(f"    M1 only: {sorted(bot20_m1 - bot20_m2)}")
    rpt(f"    M2 only: {sorted(bot20_m2 - bot20_m1)}")

    # 中国比较
    chn_m1 = latest_ocr[latest_ocr['country_code'] == 'CHN']
    if len(chn_m1) > 0:
        r = chn_m1.iloc[0]
        rpt(f"\n  中国 (CHN) 比较:")
        rpt(f"    OCR_m1 = {r['OCR_m1']:.4f}")
        rpt(f"    OCR_m2 = {r['OCR_m2']:.4f}")
        rpt(f"    差异   = {r['OCR_m2'] - r['OCR_m1']:+.4f}")
        # 排名
        rank_m1 = (latest_ocr['OCR_m1'] > r['OCR_m1']).sum() + 1
        rank_m2 = (latest_ocr['OCR_m2'] > r['OCR_m2']).sum() + 1
        rpt(f"    排名 M1: {rank_m1}/{len(latest_ocr)} (从高到低)")
        rpt(f"    排名 M2: {rank_m2}/{len(latest_ocr)} (从高到低)")
    has_m1 = True
else:
    rpt("  M1 结果文件不存在，跳过比较")
    has_m1 = False

# B3. OCR 标准化
rpt("\n--- B3. OCR 标准化 ---")
high_income = df[(df['income_group'] == 'High') & df['OCR_m2'].notna()]
ocr_high_median = high_income.groupby('country_code')['OCR_m2'].median().median()
rpt(f"  高收入国家 OCR_m2 中位数: {ocr_high_median:.4f}")
df['OCR_m2_norm'] = df['OCR_m2'] / ocr_high_median
rpt(f"  OCR_m2_norm = OCR_m2 / {ocr_high_median:.4f}")
rpt(f"  含义: >1 表示超过高收入国家典型水平")

# OCR 描述性统计
ocr_valid = df['OCR_m2'].dropna()
q01, q99 = ocr_valid.quantile(0.01), ocr_valid.quantile(0.99)
trimmed = ocr_valid[(ocr_valid >= q01) & (ocr_valid <= q99)]
rpt(f"\n  OCR_m2 描述性统计 (N={len(ocr_valid)}, trimmed={len(trimmed)}):")
rpt(f"    Mean:   {trimmed.mean():.4f}")
rpt(f"    Median: {trimmed.median():.4f}")
rpt(f"    Std:    {trimmed.std():.4f}")
rpt(f"    P25:    {trimmed.quantile(0.25):.4f}")
rpt(f"    P75:    {trimmed.quantile(0.75):.4f}")

rpt(f"\n  过度建设 (OCR > 1): {(ocr_valid > 1).sum()} / {len(ocr_valid)} ({100*(ocr_valid > 1).mean():.1f}%)")
rpt(f"  建设不足 (OCR < 1): {(ocr_valid < 1).sum()} / {len(ocr_valid)} ({100*(ocr_valid < 1).mean():.1f}%)")

rpt(f"\n  OCR_m2 按收入组 (中位数):")
ocr_by_inc = df.dropna(subset=['OCR_m2', 'income_group']).groupby('income_group')['OCR_m2'].agg(
    ['count', 'mean', 'median', 'std']
)
for g in ['Low', 'Lower-middle', 'Upper-middle', 'High']:
    if g in ocr_by_inc.index:
        r = ocr_by_inc.loc[g]
        rpt(f"    {g:<15} n={r['count']:.0f}  mean={r['mean']:.3f}  median={r['median']:.3f}  std={r['std']:.3f}")


# ============================================================
# Part C: 全球 UCI 简化版
# ============================================================
rpt("\n" + "=" * 70)
rpt("Part C: UCI 简化版")
rpt("  UCI = Q / OCR = (V/K) / (K/K*) = V*K* / K^2")
rpt("  此处 Q 使用 urban_q (= V2/K 或 V3/K)")
rpt("=" * 70)

# C1. 计算 UCI
df['UCI_m2'] = df['Q'] / df['OCR_m2']

uci_valid = df['UCI_m2'].dropna()
uci_valid_trimmed = uci_valid[(uci_valid >= uci_valid.quantile(0.01)) & (uci_valid <= uci_valid.quantile(0.99))]
rpt(f"\n  UCI_m2 描述性统计 (N={len(uci_valid)}, trimmed={len(uci_valid_trimmed)}):")
rpt(f"    Mean:   {uci_valid_trimmed.mean():.4f}")
rpt(f"    Median: {uci_valid_trimmed.median():.4f}")
rpt(f"    Std:    {uci_valid_trimmed.std():.4f}")

# C2. 四色分级（K-means, 数据驱动阈值）
rpt("\n--- C2. UCI 四色分级 (K-means) ---")
uci_for_kmeans = df.dropna(subset=['UCI_m2']).copy()
uci_for_kmeans = uci_for_kmeans[(uci_for_kmeans['UCI_m2'] > uci_for_kmeans['UCI_m2'].quantile(0.005)) &
                                 (uci_for_kmeans['UCI_m2'] < uci_for_kmeans['UCI_m2'].quantile(0.995))]

if len(uci_for_kmeans) > 100:
    km = KMeans(n_clusters=4, random_state=42, n_init=10)
    uci_for_kmeans['uci_cluster'] = km.fit_predict(uci_for_kmeans[['UCI_m2']].values)

    # 按 UCI 均值排序集群
    cluster_means = uci_for_kmeans.groupby('uci_cluster')['UCI_m2'].mean().sort_values()
    cluster_map = {old: new for new, old in enumerate(cluster_means.index)}
    uci_for_kmeans['uci_grade'] = uci_for_kmeans['uci_cluster'].map(cluster_map)

    grade_labels = {0: 'Red (low)', 1: 'Orange (below avg)', 2: 'Yellow (above avg)', 3: 'Green (high)'}
    uci_for_kmeans['uci_color'] = uci_for_kmeans['uci_grade'].map(grade_labels)

    rpt(f"  K-means 阈值 (基于 cluster 边界):")
    for g in range(4):
        sub = uci_for_kmeans[uci_for_kmeans['uci_grade'] == g]['UCI_m2']
        rpt(f"    {grade_labels[g]:<25} n={len(sub):>5}  range=[{sub.min():.3f}, {sub.max():.3f}]  mean={sub.mean():.3f}")

    # 合并分级回主面板
    df = df.merge(
        uci_for_kmeans[['country_code', 'year', 'uci_grade', 'uci_color']],
        on=['country_code', 'year'], how='left'
    )
else:
    rpt("  UCI 有效样本不足，跳过 K-means 分级")

# C3. M1 vs M2 分级变化率
if has_m1:
    rpt("\n--- C3. M1 vs M2 分级变化 ---")
    df['UCI_m1'] = df['Q'] / df['OCR_m1']

    # 用相同阈值对 M1 的 UCI 进行分级
    if len(uci_for_kmeans) > 100:
        # 获取 M2 的阈值边界
        boundaries = []
        for g in range(3):
            g_max = uci_for_kmeans[uci_for_kmeans['uci_grade'] == g]['UCI_m2'].max()
            boundaries.append(g_max)

        def assign_grade(val, bounds):
            if pd.isna(val):
                return np.nan
            for i, b in enumerate(bounds):
                if val <= b:
                    return i
            return 3

        compare_df = df.dropna(subset=['UCI_m1', 'UCI_m2']).copy()
        compare_df['grade_m1'] = compare_df['UCI_m1'].apply(lambda x: assign_grade(x, boundaries))
        compare_df['grade_m2'] = compare_df['UCI_m2'].apply(lambda x: assign_grade(x, boundaries))
        compare_df['grade_changed'] = compare_df['grade_m1'] != compare_df['grade_m2']

        change_rate = compare_df['grade_changed'].mean() * 100
        rpt(f"  比较样本: {len(compare_df)} 观测")
        rpt(f"  分级变化率: {change_rate:.1f}%")

        # 变化方向
        compare_df['grade_diff'] = compare_df['grade_m2'] - compare_df['grade_m1']
        upgraded = (compare_df['grade_diff'] > 0).sum()
        downgraded = (compare_df['grade_diff'] < 0).sum()
        rpt(f"    升级 (M2 > M1): {upgraded} ({100*upgraded/len(compare_df):.1f}%)")
        rpt(f"    降级 (M2 < M1): {downgraded} ({100*downgraded/len(compare_df):.1f}%)")


# ============================================================
# Part D: Bootstrap 弹性 CI
# ============================================================
rpt("\n" + "=" * 70)
rpt("Part D: Bootstrap 弹性置信区间 (1000 次)")
rpt("=" * 70)

n_boot = 1000
n_countries = len(country_means)
boot_alphaP = np.zeros(n_boot)
boot_alphaD = np.zeros(n_boot)

# 对国家层面做 bootstrap（保持截面结构）
country_codes = country_means['country_code'].values

for b in range(n_boot):
    # 有放回抽样国家
    idx = np.random.choice(n_countries, size=n_countries, replace=True)
    boot_sample = country_means.iloc[idx].reset_index(drop=True)

    # 重建区域虚拟变量
    boot_regions = pd.get_dummies(boot_sample['region'], prefix='reg', drop_first=True, dtype=float)
    X_b = boot_sample[['ln_Pu', 'ln_D']].copy()
    X_b = pd.concat([X_b, boot_regions], axis=1)
    X_b = sm.add_constant(X_b)

    # 确保列对齐
    for col in X_between.columns:
        if col not in X_b.columns:
            X_b[col] = 0
    X_b = X_b[X_between.columns]

    y_b = boot_sample['ln_K']

    try:
        m_b = sm.OLS(y_b, X_b).fit()
        boot_alphaP[b] = m_b.params['ln_Pu']
        boot_alphaD[b] = m_b.params['ln_D']
    except Exception:
        boot_alphaP[b] = np.nan
        boot_alphaD[b] = np.nan

# 清理 NaN
valid_boot = ~(np.isnan(boot_alphaP) | np.isnan(boot_alphaD))
boot_alphaP_valid = boot_alphaP[valid_boot]
boot_alphaD_valid = boot_alphaD[valid_boot]
n_valid = valid_boot.sum()

rpt(f"\n  有效 bootstrap 次数: {n_valid}/{n_boot}")

# 95% CI (percentile method)
ci_P = np.percentile(boot_alphaP_valid, [2.5, 97.5])
ci_D = np.percentile(boot_alphaD_valid, [2.5, 97.5])

rpt(f"\n  alpha_P: point = {alpha_P:.4f}, 95% CI = [{ci_P[0]:.4f}, {ci_P[1]:.4f}]")
rpt(f"  alpha_D: point = {alpha_D:.4f}, 95% CI = [{ci_D[0]:.4f}, {ci_D[1]:.4f}]")
rpt(f"  alpha_P SE(boot): {boot_alphaP_valid.std():.4f}")
rpt(f"  alpha_D SE(boot): {boot_alphaD_valid.std():.4f}")

# OCR 不确定性带（用 bootstrap 分布计算中国的 OCR 区间作为示例）
rpt("\n--- OCR 不确定性带 (中国示例) ---")
chn = df[(df['country_code'] == 'CHN') & df['ln_K_hat_m2'].notna()].copy()
if len(chn) > 0:
    chn_latest = chn.sort_values('year').iloc[-1]
    ln_Pu_chn = np.log(chn_latest['Pu'])
    ln_D_chn = np.log(chn_latest['GDP_pc'])

    # 简化：只变动核心弹性，忽略截距和区域 FE 的不确定性
    # K*_boot = exp(a0_hat + aP_boot * lnPu + aD_boot * lnD + region_FE_hat)
    # 近似：OCR_boot / OCR_point ~ K*_point / K*_boot
    # ln(K*) 的变化 = (aP_boot - aP)*lnPu + (aD_boot - aD)*lnD
    delta_lnKstar = (boot_alphaP_valid - alpha_P) * ln_Pu_chn + (boot_alphaD_valid - alpha_D) * ln_D_chn
    ocr_boot_ratio = np.exp(-delta_lnKstar)  # OCR_boot / OCR_point
    ocr_point = chn_latest['OCR_m2']
    ocr_boot = ocr_point * ocr_boot_ratio
    ocr_ci = np.percentile(ocr_boot, [2.5, 97.5])

    rpt(f"  CHN latest year: {int(chn_latest['year'])}")
    rpt(f"  OCR_m2 point: {ocr_point:.4f}")
    rpt(f"  OCR_m2 95% CI (bootstrap): [{ocr_ci[0]:.4f}, {ocr_ci[1]:.4f}]")


# ============================================================
# 输出：报告文件
# ============================================================
report_path = os.path.join(MODELS, 'kstar_m2_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))
print(f"\n报告已保存: {report_path}")


# ============================================================
# 输出：面板数据
# ============================================================
out_cols = ['country_code', 'country_name', 'region', 'income_group', 'year',
            'K', 'V', 'Q', 'GDP', 'GDP_pc', 'Pu', 'H', 'urban_rate',
            'K_star_m2', 'OCR_m2', 'OCR_m2_norm', 'UCI_m2']
if 'uci_grade' in df.columns:
    out_cols += ['uci_grade', 'uci_color']
if 'OCR_m1' in df.columns:
    out_cols += ['OCR_m1', 'UCI_m1']

# 仅保留存在的列
out_cols = [c for c in out_cols if c in df.columns]
out_df = df[out_cols].copy()
out_df = out_df.sort_values(['country_code', 'year']).reset_index(drop=True)

csv_path = os.path.join(DATA_PROC, 'global_kstar_m2_panel.csv')
out_df.to_csv(csv_path, index=False)
print(f"面板数据已保存: {csv_path}")
print(f"  总行数: {out_df.shape[0]}")
print(f"  含 K*_m2 的行数: {out_df['K_star_m2'].notna().sum()}")
print(f"  含 OCR_m2 的行数: {out_df['OCR_m2'].notna().sum()}")
print(f"  含 UCI_m2 的行数: {out_df['UCI_m2'].notna().sum()}")

# 代表性国家
print("\n代表性国家最新年份 (M2):")
showcase = ['CHN', 'USA', 'JPN', 'DEU', 'GBR', 'BRA', 'IND', 'NGA', 'SAU']
latest_show = out_df.dropna(subset=['UCI_m2']).sort_values('year').groupby('country_code').last()
for cc in showcase:
    if cc in latest_show.index:
        r = latest_show.loc[cc]
        extra = ""
        if 'OCR_m1' in r.index and pd.notna(r.get('OCR_m1')):
            extra = f"  (M1: OCR={r['OCR_m1']:.3f})"
        print(f"  {cc} ({int(r['year'])}): Q={r['Q']:.3f}, OCR_m2={r['OCR_m2']:.3f}, UCI_m2={r['UCI_m2']:.3f}{extra}")


# ============================================================
# 输出：图表 (4 panel)
# ============================================================
print("\n生成图表...")

fig = plt.figure(figsize=(20, 16))
gs = gridspec.GridSpec(2, 2, hspace=0.35, wspace=0.30)

# --- 图 A: M2 Between Estimator 拟合 ---
ax1 = fig.add_subplot(gs[0, 0])
plot_df = reg_df.dropna(subset=['ln_K', 'ln_K_hat_m2']).copy()
if len(plot_df) > 3000:
    plot_sample = plot_df.sample(3000, random_state=42)
else:
    plot_sample = plot_df

ax1.scatter(plot_sample['ln_K_hat_m2'], plot_sample['ln_K'],
            alpha=0.15, s=8, color='#2166AC', edgecolors='none')
lims = [min(plot_sample['ln_K_hat_m2'].min(), plot_sample['ln_K'].min()),
        max(plot_sample['ln_K_hat_m2'].max(), plot_sample['ln_K'].max())]
ax1.plot(lims, lims, 'k--', linewidth=1, alpha=0.7, label='45-degree line')
ax1.set_xlabel('Predicted ln(K) [M2]', fontsize=11)
ax1.set_ylabel('Actual ln(K)', fontsize=11)
ax1.set_title(f'A. M2 K* Regression Fit (Between Estimator)\n'
              f'$R^2$ = {model_between.rsquared:.4f}, N = {len(country_means)} countries',
              fontsize=11, fontweight='bold')
ax1.legend(fontsize=9)

textstr = (f'$\\alpha_P$ = {alpha_P:.3f} [{ci_P[0]:.3f}, {ci_P[1]:.3f}]\n'
           f'$\\alpha_D$ = {alpha_D:.3f} [{ci_D[0]:.3f}, {ci_D[1]:.3f}]')
ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=9,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

corr_panel = np.corrcoef(plot_df['ln_K'], plot_df['ln_K_hat_m2'])[0, 1]
ax1.text(0.05, 0.78, f'Panel $r$ = {corr_panel:.3f}', transform=ax1.transAxes, fontsize=9,
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# --- 图 B: M1 vs M2 OCR 散点图 ---
ax2 = fig.add_subplot(gs[0, 1])
if has_m1:
    compare_latest = df.dropna(subset=['OCR_m1', 'OCR_m2']).sort_values('year').groupby('country_code').last().reset_index()
    compare_latest = compare_latest[(compare_latest['OCR_m1'].between(0.05, 10)) &
                                     (compare_latest['OCR_m2'].between(0.05, 10))]

    color_map = {'Low': '#D73027', 'Lower-middle': '#FC8D59',
                 'Upper-middle': '#91BFDB', 'High': '#4575B4'}
    for group in ['Low', 'Lower-middle', 'Upper-middle', 'High']:
        sub = compare_latest[compare_latest['income_group'] == group]
        if len(sub) > 0:
            ax2.scatter(sub['OCR_m1'], sub['OCR_m2'], alpha=0.7, s=25,
                        color=color_map[group], label=group, edgecolors='white', linewidths=0.3)

    lims2 = [0, min(compare_latest['OCR_m1'].quantile(0.98), compare_latest['OCR_m2'].quantile(0.98))]
    ax2.plot([0, lims2[1]*1.1], [0, lims2[1]*1.1], 'k--', linewidth=1, alpha=0.5, label='45-degree')
    ax2.axhline(1.0, color='gray', linestyle=':', linewidth=0.5, alpha=0.5)
    ax2.axvline(1.0, color='gray', linestyle=':', linewidth=0.5, alpha=0.5)

    # 标注中国
    chn_pt = compare_latest[compare_latest['country_code'] == 'CHN']
    if len(chn_pt) > 0:
        ax2.annotate('CHN', (chn_pt.iloc[0]['OCR_m1'], chn_pt.iloc[0]['OCR_m2']),
                      fontsize=8, fontweight='bold',
                      xytext=(5, 5), textcoords='offset points',
                      bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow', alpha=0.6))

    ax2.set_xlabel('OCR (M1: Pu + H + GDP)', fontsize=11)
    ax2.set_ylabel('OCR (M2: Pu + GDP/cap)', fontsize=11)
    ax2.set_title(f'B. M1 vs M2 OCR Comparison\n'
                  f'Spearman $\\rho$ = {spearman_r:.3f}',
                  fontsize=11, fontweight='bold')
    ax2.legend(fontsize=8, loc='upper left')
else:
    ax2.text(0.5, 0.5, 'M1 data not available', transform=ax2.transAxes,
             ha='center', va='center', fontsize=14)

# --- 图 C: OCR_m2 按收入组箱线图 ---
ax3 = fig.add_subplot(gs[1, 0])
ocr_plot = df.dropna(subset=['OCR_m2', 'income_group']).copy()
ocr_plot = ocr_plot[ocr_plot['OCR_m2'].between(0.1, 5.0)]
income_order = ['Low', 'Lower-middle', 'Upper-middle', 'High']
ocr_groups = [ocr_plot[ocr_plot['income_group'] == g]['OCR_m2'].values for g in income_order]
valid_groups = [(g, data) for g, data in zip(income_order, ocr_groups) if len(data) > 0]
labels_box = [g for g, _ in valid_groups]
data_box = [d for _, d in valid_groups]

bp = ax3.boxplot(data_box, labels=labels_box, patch_artist=True,
                 showfliers=False, widths=0.6)
colors_box = ['#D73027', '#FC8D59', '#91BFDB', '#4575B4'][:len(labels_box)]
for patch, color in zip(bp['boxes'], colors_box):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax3.axhline(y=1.0, color='red', linestyle='--', linewidth=1, alpha=0.7, label='OCR = 1')
ax3.set_ylabel('OCR_m2 (K / K*)', fontsize=11)
ax3.set_xlabel('Income Group', fontsize=11)
ax3.set_title('C. M2 Overcapacity Ratio by Income Group', fontsize=11, fontweight='bold')
ax3.legend(fontsize=8)

for i, (g, d) in enumerate(valid_groups):
    med = np.median(d)
    ax3.text(i + 1, med + 0.08, f'{med:.2f}\n(n={len(d)})', ha='center', fontsize=7.5)

# --- 图 D: Bootstrap 分布 ---
ax4 = fig.add_subplot(gs[1, 1])
ax4.hist(boot_alphaP_valid, bins=50, alpha=0.6, color='#2166AC', label=f'$\\alpha_P$ (mean={boot_alphaP_valid.mean():.3f})', density=True)
ax4.hist(boot_alphaD_valid, bins=50, alpha=0.6, color='#D73027', label=f'$\\alpha_D$ (mean={boot_alphaD_valid.mean():.3f})', density=True)
ax4.axvline(alpha_P, color='#2166AC', linestyle='--', linewidth=1.5, alpha=0.8)
ax4.axvline(alpha_D, color='#D73027', linestyle='--', linewidth=1.5, alpha=0.8)
# CI 标注
ax4.axvline(ci_P[0], color='#2166AC', linestyle=':', linewidth=0.8, alpha=0.5)
ax4.axvline(ci_P[1], color='#2166AC', linestyle=':', linewidth=0.8, alpha=0.5)
ax4.axvline(ci_D[0], color='#D73027', linestyle=':', linewidth=0.8, alpha=0.5)
ax4.axvline(ci_D[1], color='#D73027', linestyle=':', linewidth=0.8, alpha=0.5)
ax4.set_xlabel('Elasticity estimate', fontsize=11)
ax4.set_ylabel('Density', fontsize=11)
ax4.set_title('D. Bootstrap Distribution of Elasticities (N=1000)', fontsize=11, fontweight='bold')
ax4.legend(fontsize=9)

plt.suptitle('Figure: M2 Reduced-Form K* Estimation, OCR & Bootstrap CI',
             fontsize=13, fontweight='bold', y=1.01)
fig_path = os.path.join(FIGS, 'fig_kstar_m2.png')
plt.savefig(fig_path, dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
print(f"图表已保存: {fig_path}")


# ============================================================
# 完成
# ============================================================
print("\n" + "=" * 70)
print("全部完成!")
print(f"  报告: {report_path}")
print(f"  数据: {csv_path}")
print(f"  图表: {fig_path}")
print("=" * 70)
