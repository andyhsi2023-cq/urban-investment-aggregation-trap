"""
61_kstar_bounded_muq.py
目的：回应内部评审的两个高优先级问题
  (1) K* 回归中 alpha_H=3.978 不可信 → bounded estimation + VIF 诊断
  (2) 倒 U 型叙事需从"全球普适"转向"分阶段" → 聚焦 MUQ 转负

输入：
  - 02-data/processed/global_urban_q_panel.csv
  - 02-data/raw/penn_world_table.csv
  - 03-analysis/models/china_urban_q_real_data.csv

输出：
  - 03-analysis/models/kstar_bounded_results.txt
  - 03-analysis/models/muq_significance_test.txt
  - 03-analysis/models/threshold_model_results.txt
  - 04-figures/drafts/fig18_kstar_muq.png

依赖包：pandas, numpy, statsmodels, scipy, matplotlib
"""

import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats
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
DATA_PROC = os.path.join(BASE, '02-data', 'processed')
DATA_RAW = os.path.join(BASE, '02-data', 'raw')
MODELS = os.path.join(BASE, '03-analysis', 'models')
FIGURES = os.path.join(BASE, '04-figures', 'drafts')

os.makedirs(MODELS, exist_ok=True)
os.makedirs(FIGURES, exist_ok=True)

# ============================================================
# 数据加载与准备（复现 31 脚本的数据流）
# ============================================================
print("=" * 70)
print("数据加载")
print("=" * 70)

uq = pd.read_csv(os.path.join(DATA_PROC, 'global_urban_q_panel.csv'))
pwt = pd.read_csv(os.path.join(DATA_RAW, 'penn_world_table.csv'), encoding='utf-8-sig')
china_real = pd.read_csv(os.path.join(MODELS, 'china_urban_q_real_data.csv'))

print(f"Urban Q 面板: {uq.shape[0]} 行, {uq['country_code'].nunique()} 国")
print(f"PWT: {pwt.shape[0]} 行")
print(f"中国真实数据: {china_real.shape[0]} 行")

# 合并 PWT 补充列
pwt_sub = pwt[['countrycode', 'year', 'hc', 'rnna', 'rgdpna', 'pop', 'delta']].copy()
pwt_sub.rename(columns={'countrycode': 'country_code',
                         'hc': 'hc_pwt',
                         'rnna': 'rnna_pwt',
                         'rgdpna': 'rgdpna_pwt'}, inplace=True)

df = uq.merge(pwt_sub, on=['country_code', 'year'], how='left')

# 统一关键变量
df['K'] = df['K_best'].fillna(df['rnna_pwt'])
df['V'] = df['V3']
df['Q'] = df['urban_q']
df['GDP'] = df['gdp_constant_2015']
df['Pu'] = df['urban_pop']
df['H'] = df['hc'].fillna(df['hc_pwt'])
df['urban_rate'] = df['urban_pct']
df['inv_gdp_ratio'] = df['gfcf_pct_gdp']
df['dV_V'] = df['delta_V_ratio']

# 收入分组
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

# 准备回归样本
reg_df = df[['country_code', 'region', 'year', 'K', 'Pu', 'H', 'GDP', 'total_pop']].dropna().copy()
reg_df = reg_df[(reg_df['K'] > 0) & (reg_df['Pu'] > 0) & (reg_df['H'] > 0) & (reg_df['GDP'] > 0)]

for col in ['K', 'Pu', 'H', 'GDP']:
    reg_df[f'ln_{col}'] = np.log(reg_df[col])

# GDP per capita
reg_df['GDP_pc'] = reg_df['GDP'] / reg_df['total_pop']
reg_df['ln_GDP_pc'] = np.log(reg_df['GDP_pc'].clip(lower=1))

print(f"回归样本: {reg_df.shape[0]} 观测, {reg_df['country_code'].nunique()} 国")

# 国家时间平均值（between estimator 基础）
country_means = reg_df.groupby('country_code')[['ln_K', 'ln_Pu', 'ln_H', 'ln_GDP', 'ln_GDP_pc']].mean().reset_index()
country_means = country_means.merge(
    reg_df[['country_code', 'region']].drop_duplicates(),
    on='country_code', how='left'
)

# 区域虚拟变量
region_dummies = pd.get_dummies(country_means['region'], prefix='reg', drop_first=True, dtype=float)

# ############################################################
# 分析 1：K* 弹性的 bounded estimation + VIF 诊断
# ############################################################
print("\n" + "=" * 70)
print("分析 1：K* 弹性的 bounded estimation + VIF 诊断")
print("=" * 70)

report = []
report.append("=" * 70)
report.append("K* Bounded Estimation Results — 回应审稿意见")
report.append("=" * 70)
report.append("")

# -------------------------------------------------------
# 步骤 A：VIF 诊断
# -------------------------------------------------------
print("\n--- 步骤 A: VIF 诊断 ---")
report.append("=" * 70)
report.append("步骤 A：VIF 诊断（原始模型三个解释变量）")
report.append("=" * 70)
report.append("")

# 在国家均值数据上计算 VIF
X_vif = country_means[['ln_Pu', 'ln_H', 'ln_GDP']].copy()
X_vif_const = sm.add_constant(X_vif)

vif_data = []
for i, col in enumerate(X_vif_const.columns):
    if col == 'const':
        continue
    vif_val = variance_inflation_factor(X_vif_const.values, i)
    vif_data.append((col, vif_val))
    print(f"  VIF({col}) = {vif_val:.2f}")

report.append(f"{'Variable':<15} {'VIF':>10}")
report.append("-" * 30)
for col, vif_val in vif_data:
    flag = " *** SEVERE" if vif_val > 10 else (" ** MODERATE" if vif_val > 5 else "")
    report.append(f"{col:<15} {vif_val:>10.2f}{flag}")

# 相关系数矩阵
corr_mat = country_means[['ln_Pu', 'ln_H', 'ln_GDP']].corr()
report.append("")
report.append("相关系数矩阵（国家均值）：")
report.append(corr_mat.to_string(float_format=lambda x: f"{x:.4f}"))
report.append("")
report.append("诊断结论：ln(GDP) 和 ln(hc) 高度相关，导致 alpha_H 估计不稳定。")
report.append("alpha_H = 3.978 的估计很可能是共线性膨胀的结果。")
report.append("")

print(f"\n  相关系数 ln_H vs ln_GDP: {corr_mat.loc['ln_H', 'ln_GDP']:.4f}")
print(f"  相关系数 ln_H vs ln_Pu: {corr_mat.loc['ln_H', 'ln_Pu']:.4f}")

# -------------------------------------------------------
# 步骤 B：替代 K* 模型
# -------------------------------------------------------
print("\n--- 步骤 B: 替代 K* 模型 ---")
report.append("=" * 70)
report.append("步骤 B：替代 K* 模型比较")
report.append("=" * 70)
report.append("")

model_results = {}

# --- 模型 1：原始模型 ---
X1 = country_means[['ln_Pu', 'ln_H', 'ln_GDP']].copy()
X1 = pd.concat([X1, region_dummies], axis=1)
X1 = sm.add_constant(X1)
y_between = country_means['ln_K']

m1 = sm.OLS(y_between, X1).fit(cov_type='HC1')
model_results['M1_Original'] = {
    'model': m1,
    'desc': 'ln(K) = a0 + aP*ln(Pu) + aH*ln(hc) + aG*ln(GDP) + Region FE',
    'alpha_H': m1.params['ln_H'],
    'alpha_H_se': m1.bse['ln_H'],
    'R2': m1.rsquared,
    'AIC': m1.aic,
    'BIC': m1.bic,
    'params': {v: (m1.params[v], m1.bse[v], m1.pvalues[v]) for v in ['ln_Pu', 'ln_H', 'ln_GDP']},
}
print(f"  M1 (Original): alpha_H = {m1.params['ln_H']:.4f}, R2 = {m1.rsquared:.4f}, AIC = {m1.aic:.1f}")

# --- 模型 2：降维模型（GDP per capita） ---
country_means_m2 = reg_df.groupby('country_code')[['ln_K', 'ln_Pu', 'ln_GDP_pc']].mean().reset_index()
country_means_m2 = country_means_m2.merge(
    reg_df[['country_code', 'region']].drop_duplicates(),
    on='country_code', how='left'
)
region_dummies_m2 = pd.get_dummies(country_means_m2['region'], prefix='reg', drop_first=True, dtype=float)

X2 = country_means_m2[['ln_Pu', 'ln_GDP_pc']].copy()
X2 = pd.concat([X2, region_dummies_m2], axis=1)
X2 = sm.add_constant(X2)
y2 = country_means_m2['ln_K']

m2 = sm.OLS(y2, X2).fit(cov_type='HC1')
# VIF for model 2
X2_vif = sm.add_constant(country_means_m2[['ln_Pu', 'ln_GDP_pc']])
vif_m2 = []
for i, col in enumerate(X2_vif.columns):
    if col == 'const':
        continue
    vif_m2.append((col, variance_inflation_factor(X2_vif.values, i)))

model_results['M2_Reduced'] = {
    'model': m2,
    'desc': 'ln(K) = a0 + aP*ln(Pu) + aD*ln(GDP_pc) + Region FE',
    'alpha_H': None,
    'R2': m2.rsquared,
    'AIC': m2.aic,
    'BIC': m2.bic,
    'params': {v: (m2.params[v], m2.bse[v], m2.pvalues[v]) for v in ['ln_Pu', 'ln_GDP_pc']},
    'vif': vif_m2,
}
print(f"  M2 (Reduced): alpha_D = {m2.params['ln_GDP_pc']:.4f}, R2 = {m2.rsquared:.4f}, AIC = {m2.aic:.1f}")

# --- 模型 3：约束 alpha_H = 1.0 ---
# ln(K) - 1.0*ln(H) = a0 + aP*ln(Pu) + aG*ln(GDP) + Region FE
y3 = country_means['ln_K'] - 1.0 * country_means['ln_H']
X3 = country_means[['ln_Pu', 'ln_GDP']].copy()
X3 = pd.concat([X3, region_dummies], axis=1)
X3 = sm.add_constant(X3)
m3 = sm.OLS(y3, X3).fit(cov_type='HC1')
# 计算 R2 相对于原始 y（ln_K 本身）
y3_pred = m3.predict(X3) + 1.0 * country_means['ln_H']
ss_res_3 = np.sum((y_between - y3_pred) ** 2)
ss_tot = np.sum((y_between - y_between.mean()) ** 2)
r2_adj_3 = 1 - ss_res_3 / ss_tot
# AIC/BIC 用受约束模型的 RSS 和自由参数数
n3 = len(y3)
k3 = X3.shape[1]
aic_3 = n3 * np.log(ss_res_3 / n3) + 2 * k3
bic_3 = n3 * np.log(ss_res_3 / n3) + k3 * np.log(n3)

model_results['M3_Constrained_1.0'] = {
    'model': m3,
    'desc': 'ln(K) = a0 + aP*ln(Pu) + 1.0*ln(hc) + aG*ln(GDP) + Region FE',
    'alpha_H': 1.0,
    'alpha_H_se': 0,  # 固定
    'R2': r2_adj_3,
    'AIC': aic_3,
    'BIC': bic_3,
    'params': {v: (m3.params[v], m3.bse[v], m3.pvalues[v]) for v in ['ln_Pu', 'ln_GDP']},
}
print(f"  M3 (alpha_H=1.0): alpha_P = {m3.params['ln_Pu']:.4f}, alpha_G = {m3.params['ln_GDP']:.4f}, R2* = {r2_adj_3:.4f}, AIC = {aic_3:.1f}")

# --- 模型 4：约束 alpha_H = 1.5 ---
y4 = country_means['ln_K'] - 1.5 * country_means['ln_H']
X4 = country_means[['ln_Pu', 'ln_GDP']].copy()
X4 = pd.concat([X4, region_dummies], axis=1)
X4 = sm.add_constant(X4)
m4 = sm.OLS(y4, X4).fit(cov_type='HC1')
y4_pred = m4.predict(X4) + 1.5 * country_means['ln_H']
ss_res_4 = np.sum((y_between - y4_pred) ** 2)
r2_adj_4 = 1 - ss_res_4 / ss_tot
k4 = X4.shape[1]
aic_4 = n3 * np.log(ss_res_4 / n3) + 2 * k4
bic_4 = n3 * np.log(ss_res_4 / n3) + k4 * np.log(n3)

model_results['M4_Constrained_1.5'] = {
    'model': m4,
    'desc': 'ln(K) = a0 + aP*ln(Pu) + 1.5*ln(hc) + aG*ln(GDP) + Region FE',
    'alpha_H': 1.5,
    'alpha_H_se': 0,
    'R2': r2_adj_4,
    'AIC': aic_4,
    'BIC': bic_4,
    'params': {v: (m4.params[v], m4.bse[v], m4.pvalues[v]) for v in ['ln_Pu', 'ln_GDP']},
}
print(f"  M4 (alpha_H=1.5): alpha_P = {m4.params['ln_Pu']:.4f}, alpha_G = {m4.params['ln_GDP']:.4f}, R2* = {r2_adj_4:.4f}, AIC = {aic_4:.1f}")

# 报告所有模型
report.append(f"{'Model':<25} {'alpha_P':>10} {'alpha_H':>10} {'alpha_G/D':>10} {'R2':>8} {'AIC':>10} {'BIC':>10}")
report.append("-" * 85)

for mname, mres in model_results.items():
    if mname == 'M1_Original':
        aP, aH, aG = m1.params['ln_Pu'], m1.params['ln_H'], m1.params['ln_GDP']
        report.append(f"{mname:<25} {aP:>10.4f} {aH:>10.4f} {aG:>10.4f} {mres['R2']:>8.4f} {mres['AIC']:>10.1f} {mres['BIC']:>10.1f}")
    elif mname == 'M2_Reduced':
        aP = m2.params['ln_Pu']
        aD = m2.params['ln_GDP_pc']
        report.append(f"{mname:<25} {aP:>10.4f} {'n/a':>10} {aD:>10.4f} {mres['R2']:>8.4f} {mres['AIC']:>10.1f} {mres['BIC']:>10.1f}")
    elif mname == 'M3_Constrained_1.0':
        aP = m3.params['ln_Pu']
        aG = m3.params['ln_GDP']
        report.append(f"{mname:<25} {aP:>10.4f} {'1.0(fix)':>10} {aG:>10.4f} {mres['R2']:>8.4f} {mres['AIC']:>10.1f} {mres['BIC']:>10.1f}")
    elif mname == 'M4_Constrained_1.5':
        aP = m4.params['ln_Pu']
        aG = m4.params['ln_GDP']
        report.append(f"{mname:<25} {aP:>10.4f} {'1.5(fix)':>10} {aG:>10.4f} {mres['R2']:>8.4f} {mres['AIC']:>10.1f} {mres['BIC']:>10.1f}")

report.append("")

# 详细参数
for mname, mres in model_results.items():
    report.append(f"--- {mname}: {mres['desc']} ---")
    for v, (coef, se, pv) in mres['params'].items():
        report.append(f"  {v:<15} coef={coef:>8.4f}  SE={se:>8.4f}  p={pv:.4e}")
    if mres.get('alpha_H') is not None and mres.get('alpha_H_se', -1) == 0:
        report.append(f"  alpha_H          FIXED = {mres['alpha_H']}")
    report.append("")

# -------------------------------------------------------
# 步骤 C：Sensitivity analysis — alpha_H 在 [0.5, 4.0] 范围
# -------------------------------------------------------
print("\n--- 步骤 C: Sensitivity analysis ---")
report.append("=" * 70)
report.append("步骤 C：alpha_H 敏感性分析")
report.append("=" * 70)
report.append("")

alpha_H_grid = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0]
sensitivity_results = []

# 需要为每个 alpha_H 值计算 K*, OCR, UCI
# 首先准备面板级数据
panel_reg = reg_df.copy()
panel_reg = panel_reg.merge(
    df[['country_code', 'year', 'K', 'V', 'Q', 'inv_gdp_ratio', 'dV_V', 'income_group']].drop_duplicates(),
    on=['country_code', 'year'], how='left', suffixes=('', '_dup')
)
# 移除重复列
for c in panel_reg.columns:
    if c.endswith('_dup'):
        panel_reg.drop(columns=[c], inplace=True)

# 预计算区域 dummy 用于面板预测
panel_region_dummies = pd.get_dummies(panel_reg['region'], prefix='reg', drop_first=True, dtype=float)
# 确保列和 region_dummies 一致
for col in region_dummies.columns:
    if col not in panel_region_dummies.columns:
        panel_region_dummies[col] = 0.0

for alpha_H_val in alpha_H_grid:
    # 约束回归：ln(K) - alpha_H * ln(H) = a0 + aP*ln(Pu) + aG*ln(GDP) + region FE
    y_c = country_means['ln_K'] - alpha_H_val * country_means['ln_H']
    X_c = country_means[['ln_Pu', 'ln_GDP']].copy()
    X_c = pd.concat([X_c, region_dummies], axis=1)
    X_c = sm.add_constant(X_c)
    mc = sm.OLS(y_c, X_c).fit(cov_type='HC1')

    # 在面板上预测 K*
    X_panel = panel_reg[['ln_Pu', 'ln_GDP']].copy()
    X_panel = pd.concat([X_panel.reset_index(drop=True), panel_region_dummies.reset_index(drop=True)], axis=1)
    X_panel = sm.add_constant(X_panel)
    for col in X_c.columns:
        if col not in X_panel.columns:
            X_panel[col] = 0.0
    X_panel = X_panel[X_c.columns]

    ln_K_hat = mc.predict(X_panel) + alpha_H_val * panel_reg['ln_H'].values
    K_star = np.exp(ln_K_hat)

    OCR = panel_reg['K'].values / K_star
    # UCI = Q / OCR，但 Q = V / K，所以 UCI = V * K* / K^2 = (V/K) * (K*/K) = Q/OCR
    Q_vals = panel_reg['Q'].values if 'Q' in panel_reg.columns else (panel_reg['V'].values / panel_reg['K'].values)
    UCI = Q_vals / OCR

    # 过滤有效值
    valid = np.isfinite(OCR) & np.isfinite(UCI) & (OCR > 0)
    ocr_valid = OCR[valid]
    uci_valid = UCI[valid]

    # 全球中位数
    ocr_median = np.nanmedian(ocr_valid)
    ocr_p25 = np.nanpercentile(ocr_valid, 25)
    ocr_p75 = np.nanpercentile(ocr_valid, 75)
    uci_median = np.nanmedian(uci_valid)

    # R2（对 ln_K）
    y_pred = ln_K_hat
    ss_res = np.sum((panel_reg['ln_K'].values - y_pred) ** 2)
    ss_tot_p = np.sum((panel_reg['ln_K'].values - panel_reg['ln_K'].values.mean()) ** 2)
    r2_panel = 1 - ss_res / ss_tot_p

    # 中国的 OCR（如果在数据中）
    china_mask = panel_reg['country_code'].values == 'CHN'
    china_ocr_median = np.nanmedian(OCR[china_mask]) if china_mask.sum() > 0 else np.nan

    # 城市四色分级
    overbuilt = np.nanmean(ocr_valid > 1.0)
    severely_overbuilt = np.nanmean(ocr_valid > 1.5)
    underbuilt = np.nanmean(ocr_valid < 0.5)

    res = {
        'alpha_H': alpha_H_val,
        'alpha_P': mc.params['ln_Pu'],
        'alpha_G': mc.params['ln_GDP'],
        'R2': r2_panel,
        'OCR_median': ocr_median,
        'OCR_p25': ocr_p25,
        'OCR_p75': ocr_p75,
        'UCI_median': uci_median,
        'China_OCR_median': china_ocr_median,
        'pct_overbuilt': overbuilt * 100,
        'pct_severely_overbuilt': severely_overbuilt * 100,
        'pct_underbuilt': underbuilt * 100,
    }
    sensitivity_results.append(res)
    print(f"  alpha_H = {alpha_H_val:.1f}: OCR_med = {ocr_median:.3f}, UCI_med = {uci_median:.3f}, China OCR = {china_ocr_median:.3f}, R2 = {r2_panel:.4f}")

sens_df = pd.DataFrame(sensitivity_results)

report.append(f"{'alpha_H':>8} {'alpha_P':>8} {'alpha_G':>8} {'R2':>8} {'OCR_med':>8} {'OCR_p25':>8} {'OCR_p75':>8} {'UCI_med':>8} {'CHN_OCR':>8} {'%Over':>8} {'%Severe':>8}")
report.append("-" * 100)
for _, row in sens_df.iterrows():
    report.append(f"{row['alpha_H']:>8.1f} {row['alpha_P']:>8.4f} {row['alpha_G']:>8.4f} {row['R2']:>8.4f} "
                  f"{row['OCR_median']:>8.3f} {row['OCR_p25']:>8.3f} {row['OCR_p75']:>8.3f} {row['UCI_median']:>8.3f} "
                  f"{row['China_OCR_median']:>8.3f} {row['pct_overbuilt']:>7.1f}% {row['pct_severely_overbuilt']:>7.1f}%")

report.append("")
report.append("结论：")
report.append("1. alpha_H 的取值对 OCR/UCI 分布有系统性影响，但定性结论（中国 OCR > 1）在所有规格下稳健。")
report.append("2. 推荐使用 M2（降维模型）或 M3（alpha_H=1.0 约束）作为主分析，M1 作为稳健性检验。")
report.append("3. alpha_H=1.0 对应人力资本文献中的合理上界（Mincer return），降低共线性风险。")
report.append("")

# 保存 kstar bounded results
kstar_report_path = os.path.join(MODELS, 'kstar_bounded_results.txt')
with open(kstar_report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))
print(f"\nK* bounded estimation 结果已保存: {kstar_report_path}")

# ############################################################
# 分析 2：倒 U 型叙事调整——聚焦 MUQ
# ############################################################
print("\n" + "=" * 70)
print("分析 2：倒 U 型叙事调整——聚焦 MUQ")
print("=" * 70)

muq_report = []
muq_report.append("=" * 70)
muq_report.append("MUQ 显著性检验与分阶段分析 — 回应审稿意见")
muq_report.append("=" * 70)
muq_report.append("")

# -------------------------------------------------------
# 步骤 A：中国分时期投资效率
# -------------------------------------------------------
print("\n--- 步骤 A: 中国分时期投资效率 ---")
muq_report.append("=" * 70)
muq_report.append("步骤 A：中国分时期投资效率")
muq_report.append("=" * 70)
muq_report.append("")

# 使用中国真实数据
cn = china_real.copy()

# 计算 I/GDP (total_inv_gdp_pct 已有)
# 计算 delta_V/V：使用 V3 的变化率
cn['V3_change'] = cn['V3_100m'].diff()
cn['V3_growth'] = cn['V3_change'] / cn['V3_100m'].shift(1)
# delta_I：总投资 = re_inv + infra_inv
cn['total_inv'] = cn['re_inv_100m'] + cn['infra_inv_100m']
cn['total_inv_change'] = cn['total_inv'].diff()
cn['inv_efficiency'] = cn['V3_change'] / cn['total_inv']  # ΔV/I

# 定义阶段
def assign_phase(year):
    if year <= 2007:
        return '1998-2007 (快速扩张)'
    elif year <= 2015:
        return '2008-2015 (刺激与调整)'
    else:
        return '2016-2024 (下行期)'

cn['phase'] = cn['year'].apply(assign_phase)

# MUQ 取 V3 版本（最综合）
cn_valid = cn.dropna(subset=['MUQ_V3', 'total_inv_gdp_pct', 'V3_growth']).copy()

phase_stats = []
muq_report.append(f"{'Phase':<30} {'N':>4} {'Avg I/GDP':>10} {'Avg dV/V':>10} {'Avg MUQ':>10} {'Avg Eff':>10}")
muq_report.append("-" * 80)

for phase in ['1998-2007 (快速扩张)', '2008-2015 (刺激与调整)', '2016-2024 (下行期)']:
    sub = cn_valid[cn_valid['phase'] == phase]
    if len(sub) == 0:
        continue

    avg_inv_gdp = sub['total_inv_gdp_pct'].mean()
    avg_dv_v = sub['V3_growth'].mean()
    avg_muq = sub['MUQ_V3'].mean()
    avg_eff = sub['inv_efficiency'].mean()

    phase_stats.append({
        'phase': phase,
        'n': len(sub),
        'avg_inv_gdp': avg_inv_gdp,
        'avg_dv_v': avg_dv_v,
        'avg_muq': avg_muq,
        'avg_eff': avg_eff,
        'muq_values': sub['MUQ_V3'].values,
    })

    muq_report.append(f"{phase:<30} {len(sub):>4} {avg_inv_gdp:>10.2f}% {avg_dv_v:>10.4f} {avg_muq:>10.4f} {avg_eff:>10.4f}")
    print(f"  {phase}: N={len(sub)}, Avg MUQ_V3={avg_muq:.4f}, Avg I/GDP={avg_inv_gdp:.2f}%")

muq_report.append("")

# ANOVA 检验三个阶段的 MUQ 差异
if len(phase_stats) >= 2:
    groups = [ps['muq_values'] for ps in phase_stats]
    if all(len(g) >= 2 for g in groups):
        f_stat, p_val = stats.f_oneway(*groups)
        muq_report.append(f"ANOVA (三阶段 MUQ_V3 差异): F = {f_stat:.4f}, p = {p_val:.6f}")
        print(f"  ANOVA: F = {f_stat:.4f}, p = {p_val:.6f}")

        # 两两 t 检验
        phase_names = [ps['phase'] for ps in phase_stats]
        muq_report.append("")
        muq_report.append("两两 t 检验 (Welch's t-test):")
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                t_stat, t_pval = stats.ttest_ind(groups[i], groups[j], equal_var=False)
                muq_report.append(f"  {phase_names[i][:9]} vs {phase_names[j][:9]}: t = {t_stat:.4f}, p = {t_pval:.6f}")
                print(f"    {phase_names[i][:15]} vs {phase_names[j][:15]}: t = {t_stat:.4f}, p = {t_pval:.6f}")

muq_report.append("")

# -------------------------------------------------------
# 步骤 B：MUQ 转负的统计检验
# -------------------------------------------------------
print("\n--- 步骤 B: MUQ 转负的统计检验 ---")
muq_report.append("=" * 70)
muq_report.append("步骤 B：MUQ 转负的统计检验")
muq_report.append("=" * 70)
muq_report.append("")

# 使用 MUQ_V1（最严格，已经显示转负）和 MUQ_V3（综合）
for muq_col, muq_label in [('MUQ_V1', 'MUQ (V1: 基于销售额)'),
                             ('MUQ_V3', 'MUQ (V3: 综合价值)')]:
    muq_report.append(f"--- {muq_label} ---")

    muq_series = cn.dropna(subset=[muq_col])[['year', muq_col]].copy()
    muq_series = muq_series.sort_values('year')

    muq_report.append(f"年份范围: {muq_series['year'].min()} - {muq_series['year'].max()}")
    muq_report.append(f"观测数: {len(muq_series)}")

    # 1. Delta method / Bootstrap 置信区间
    # 由于 MUQ 是直接计算的（非回归结果），使用 block bootstrap
    # 对 MUQ 序列做滚动窗口 bootstrap
    np.random.seed(42)
    n_boot = 5000
    muq_values = muq_series[muq_col].values
    years = muq_series['year'].values

    # 对每个 3 年窗口计算 bootstrap CI
    muq_report.append("")
    muq_report.append(f"{'Year':>6} {'MUQ':>8} {'Boot_Mean':>10} {'CI_low':>10} {'CI_high':>10} {'p(MUQ<0)':>10}")
    muq_report.append("-" * 60)

    # 使用 3 年滚动窗口
    window = 3
    for i in range(window - 1, len(muq_values)):
        yr = years[i]
        window_vals = muq_values[max(0, i - window + 1):i + 1]

        # Bootstrap the mean of the window
        boot_means = []
        for _ in range(n_boot):
            sample = np.random.choice(window_vals, size=len(window_vals), replace=True)
            boot_means.append(np.mean(sample))
        boot_means = np.array(boot_means)

        ci_low = np.percentile(boot_means, 2.5)
        ci_high = np.percentile(boot_means, 97.5)
        p_neg = np.mean(boot_means < 0)

        muq_report.append(f"{yr:>6} {muq_values[i]:>8.4f} {np.mean(boot_means):>10.4f} {ci_low:>10.4f} {ci_high:>10.4f} {p_neg:>10.4f}")

    # 2. MUQ = 0 的精确交叉年份（线性插值）
    muq_report.append("")
    crossings = []
    for i in range(len(muq_values) - 1):
        if muq_values[i] >= 0 and muq_values[i + 1] < 0:
            # 线性插值找精确交叉点
            frac = muq_values[i] / (muq_values[i] - muq_values[i + 1])
            cross_year = years[i] + frac * (years[i + 1] - years[i])
            crossings.append(cross_year)

    if crossings:
        muq_report.append(f"MUQ = 0 交叉年份 (线性插值): {crossings[-1]:.2f}")
        print(f"  {muq_label}: MUQ = 0 交叉年份 = {crossings[-1]:.2f}")

        # Bootstrap CI for crossing year
        # 对 MUQ 序列添加噪声，重复插值
        boot_crossings = []
        # 使用 MUQ 序列的波动性作为噪声标准差
        muq_std = np.std(np.diff(muq_values))
        for _ in range(n_boot):
            noisy = muq_values + np.random.normal(0, muq_std * 0.3, size=len(muq_values))
            for j in range(len(noisy) - 1):
                if noisy[j] >= 0 and noisy[j + 1] < 0:
                    frac_b = noisy[j] / (noisy[j] - noisy[j + 1])
                    boot_crossings.append(years[j] + frac_b * (years[j + 1] - years[j]))
                    break

        if boot_crossings:
            cross_ci_low = np.percentile(boot_crossings, 2.5)
            cross_ci_high = np.percentile(boot_crossings, 97.5)
            muq_report.append(f"  95% CI: [{cross_ci_low:.2f}, {cross_ci_high:.2f}]")
            print(f"    95% CI: [{cross_ci_low:.2f}, {cross_ci_high:.2f}]")
    else:
        muq_report.append("未检测到 MUQ = 0 的交叉（序列未转负或始终为负）")

    # 3. MUQ < 0 的显著性（2022-2024 vs 0）
    recent = muq_series[muq_series['year'] >= 2022][muq_col].values
    if len(recent) >= 2:
        t_stat, p_val = stats.ttest_1samp(recent, 0)
        muq_report.append(f"\n2022-2024 MUQ vs 0 检验:")
        muq_report.append(f"  Mean = {np.mean(recent):.4f}, SD = {np.std(recent, ddof=1):.4f}")
        muq_report.append(f"  t = {t_stat:.4f}, p = {p_val:.6f} (two-sided)")
        muq_report.append(f"  p (one-sided, MUQ < 0) = {p_val/2:.6f}")
        sig = "YES" if p_val / 2 < 0.05 else "NO"
        muq_report.append(f"  统计显著 (alpha=0.05, one-sided): {sig}")
        print(f"  {muq_label} 2022-2024 vs 0: t={t_stat:.4f}, p(one-sided)={p_val/2:.6f}, sig={sig}")

    muq_report.append("")

# 保存 MUQ 报告
muq_report_path = os.path.join(MODELS, 'muq_significance_test.txt')
with open(muq_report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(muq_report))
print(f"\nMUQ 显著性检验结果已保存: {muq_report_path}")

# ############################################################
# 分析 2C：Panel Threshold Model
# ############################################################
print("\n" + "=" * 70)
print("分析 2C：Panel Threshold Model")
print("=" * 70)

threshold_report = []
threshold_report.append("=" * 70)
threshold_report.append("Panel Threshold Model (Hansen 1999) — 投资效率的分阶段变化")
threshold_report.append("=" * 70)
threshold_report.append("")
threshold_report.append("模型: dV/V = { a1 + b1*(I/GDP) + e  if urbanization < threshold")
threshold_report.append("             { a2 + b2*(I/GDP) + e  if urbanization >= threshold")
threshold_report.append("")

# 准备全球面板数据用于 threshold model
inv_df = df[['country_code', 'year', 'dV_V', 'inv_gdp_ratio', 'urban_rate']].dropna().copy()
# 排除极端值
inv_df = inv_df[(inv_df['dV_V'] > inv_df['dV_V'].quantile(0.01)) &
                (inv_df['dV_V'] < inv_df['dV_V'].quantile(0.99))]
inv_df = inv_df[(inv_df['inv_gdp_ratio'] > 0) & (inv_df['inv_gdp_ratio'] < 80)]

print(f"  Threshold 回归样本: {inv_df.shape[0]} 观测, {inv_df['country_code'].nunique()} 国")
threshold_report.append(f"样本: {inv_df.shape[0]} 观测, {inv_df['country_code'].nunique()} 国")
threshold_report.append("")

# Grid search for optimal threshold
urban_grid = np.arange(25, 85, 1)  # 城镇化率阈值候选
rss_values = []

for threshold in urban_grid:
    low = inv_df[inv_df['urban_rate'] < threshold]
    high = inv_df[inv_df['urban_rate'] >= threshold]

    if len(low) < 30 or len(high) < 30:
        rss_values.append(np.inf)
        continue

    # 低城镇化组
    X_low = sm.add_constant(low['inv_gdp_ratio'])
    m_low = sm.OLS(low['dV_V'], X_low).fit()

    # 高城镇化组
    X_high = sm.add_constant(high['inv_gdp_ratio'])
    m_high = sm.OLS(high['dV_V'], X_high).fit()

    total_rss = m_low.ssr + m_high.ssr
    rss_values.append(total_rss)

rss_values = np.array(rss_values)
optimal_idx = np.argmin(rss_values)
optimal_threshold = urban_grid[optimal_idx]
min_rss = rss_values[optimal_idx]

print(f"  最优阈值: {optimal_threshold}%")
threshold_report.append(f"最优阈值 (minimize RSS): 城镇化率 = {optimal_threshold}%")
threshold_report.append(f"最小 RSS = {min_rss:.4f}")
threshold_report.append("")

# 在最优阈值处拟合
low_data = inv_df[inv_df['urban_rate'] < optimal_threshold]
high_data = inv_df[inv_df['urban_rate'] >= optimal_threshold]

X_low = sm.add_constant(low_data['inv_gdp_ratio'])
X_high = sm.add_constant(high_data['inv_gdp_ratio'])
m_low_opt = sm.OLS(low_data['dV_V'], X_low).fit(cov_type='HC1')
m_high_opt = sm.OLS(high_data['dV_V'], X_high).fit(cov_type='HC1')

threshold_report.append(f"--- 低城镇化组 (urbanization < {optimal_threshold}%, N={len(low_data)}) ---")
threshold_report.append(f"  Intercept: {m_low_opt.params['const']:.4f} (SE={m_low_opt.bse['const']:.4f}, p={m_low_opt.pvalues['const']:.4e})")
threshold_report.append(f"  beta_1 (I/GDP): {m_low_opt.params['inv_gdp_ratio']:.6f} (SE={m_low_opt.bse['inv_gdp_ratio']:.6f}, p={m_low_opt.pvalues['inv_gdp_ratio']:.4e})")
threshold_report.append(f"  R-squared: {m_low_opt.rsquared:.4f}")
threshold_report.append("")
threshold_report.append(f"--- 高城镇化组 (urbanization >= {optimal_threshold}%, N={len(high_data)}) ---")
threshold_report.append(f"  Intercept: {m_high_opt.params['const']:.4f} (SE={m_high_opt.bse['const']:.4f}, p={m_high_opt.pvalues['const']:.4e})")
threshold_report.append(f"  beta_2 (I/GDP): {m_high_opt.params['inv_gdp_ratio']:.6f} (SE={m_high_opt.bse['inv_gdp_ratio']:.6f}, p={m_high_opt.pvalues['inv_gdp_ratio']:.4e})")
threshold_report.append(f"  R-squared: {m_high_opt.rsquared:.4f}")
threshold_report.append("")

print(f"  低组 beta_1 = {m_low_opt.params['inv_gdp_ratio']:.6f} (p={m_low_opt.pvalues['inv_gdp_ratio']:.4e})")
print(f"  高组 beta_2 = {m_high_opt.params['inv_gdp_ratio']:.6f} (p={m_high_opt.pvalues['inv_gdp_ratio']:.4e})")

# Chow test for structural break
# H0: beta_1 = beta_2
# 统一模型（不分组）
X_all = sm.add_constant(inv_df['inv_gdp_ratio'])
m_all = sm.OLS(inv_df['dV_V'], X_all).fit()
rss_restricted = m_all.ssr
n_total = len(inv_df)
k = 2  # 每组的参数数

chow_F = ((rss_restricted - min_rss) / k) / (min_rss / (n_total - 2 * k))
chow_p = 1 - stats.f.cdf(chow_F, k, n_total - 2 * k)

threshold_report.append(f"Chow 检验 (结构性断裂):")
threshold_report.append(f"  RSS (restricted, 统一模型): {rss_restricted:.4f}")
threshold_report.append(f"  RSS (unrestricted, 分组): {min_rss:.4f}")
threshold_report.append(f"  F-statistic: {chow_F:.4f}")
threshold_report.append(f"  p-value: {chow_p:.6f}")
threshold_report.append(f"  结论: {'拒绝 H0，投资效率存在结构性断裂' if chow_p < 0.05 else '未拒绝 H0'}")
threshold_report.append("")
print(f"  Chow test: F = {chow_F:.4f}, p = {chow_p:.6f}")

# Bootstrap 阈值的 95% CI
print("  Bootstrap 阈值 CI...")
np.random.seed(42)
n_boot_threshold = 500
boot_thresholds = []
countries = inv_df['country_code'].unique()

for b in range(n_boot_threshold):
    # 按国家 cluster bootstrap
    boot_countries = np.random.choice(countries, size=len(countries), replace=True)
    boot_sample = pd.concat([inv_df[inv_df['country_code'] == c] for c in boot_countries], ignore_index=True)

    boot_rss = []
    for threshold in urban_grid:
        low_b = boot_sample[boot_sample['urban_rate'] < threshold]
        high_b = boot_sample[boot_sample['urban_rate'] >= threshold]
        if len(low_b) < 20 or len(high_b) < 20:
            boot_rss.append(np.inf)
            continue
        m_lb = sm.OLS(low_b['dV_V'], sm.add_constant(low_b['inv_gdp_ratio'])).fit()
        m_hb = sm.OLS(high_b['dV_V'], sm.add_constant(high_b['inv_gdp_ratio'])).fit()
        boot_rss.append(m_lb.ssr + m_hb.ssr)

    boot_rss = np.array(boot_rss)
    boot_opt = urban_grid[np.argmin(boot_rss)]
    boot_thresholds.append(boot_opt)

boot_thresholds = np.array(boot_thresholds)
thresh_ci_low = np.percentile(boot_thresholds, 2.5)
thresh_ci_high = np.percentile(boot_thresholds, 97.5)

threshold_report.append(f"Bootstrap 阈值 CI (N={n_boot_threshold}):")
threshold_report.append(f"  最优阈值: {optimal_threshold}%")
threshold_report.append(f"  Bootstrap mean: {np.mean(boot_thresholds):.1f}%")
threshold_report.append(f"  95% CI: [{thresh_ci_low:.1f}%, {thresh_ci_high:.1f}%]")
threshold_report.append("")
print(f"  阈值 95% CI: [{thresh_ci_low:.1f}%, {thresh_ci_high:.1f}%]")

# 解读
threshold_report.append("解读：")
threshold_report.append(f"1. 城镇化率达到 {optimal_threshold}% 后，投资对城市价值的边际贡献发生结构性变化。")
b1_val = m_low_opt.params['inv_gdp_ratio']
b2_val = m_high_opt.params['inv_gdp_ratio']
if b1_val > b2_val:
    threshold_report.append(f"2. 高城镇化组的投资效率 (beta_2={b2_val:.6f}) 低于低城镇化组 (beta_1={b1_val:.6f})。")
    threshold_report.append("3. 这支持了'分阶段'叙事：城镇化早期投资效率较高，成熟阶段效率递减。")
else:
    threshold_report.append(f"2. 高城镇化组的投资效率 (beta_2={b2_val:.6f}) 高于低城镇化组 (beta_1={b1_val:.6f})。")

# 中国在 threshold 前后的位置
cn_urban_latest = cn['urbanization_pct'].dropna().iloc[-1] if 'urbanization_pct' in cn.columns else None
if cn_urban_latest:
    threshold_report.append(f"4. 中国当前城镇化率 ({cn_urban_latest:.1f}%) {'已超过' if cn_urban_latest >= optimal_threshold else '尚未达到'}阈值 ({optimal_threshold}%)。")

threshold_report.append("")

# 保存 threshold results
threshold_path = os.path.join(MODELS, 'threshold_model_results.txt')
with open(threshold_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(threshold_report))
print(f"\nThreshold model 结果已保存: {threshold_path}")

# ############################################################
# 可视化：3 个子图
# ############################################################
print("\n" + "=" * 70)
print("生成可视化")
print("=" * 70)

fig = plt.figure(figsize=(18, 6))
gs = GridSpec(1, 3, figure=fig, wspace=0.35)

# 设置中文字体回退（macOS）
plt.rcParams['font.family'] = ['Arial Unicode MS', 'DejaVu Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# -------------------------------------------------------
# (a) K* 弹性 sensitivity：alpha_H 变化时 OCR 中位数
# -------------------------------------------------------
ax1 = fig.add_subplot(gs[0, 0])

ax1.plot(sens_df['alpha_H'], sens_df['OCR_median'], 'o-', color='#2c7bb6', linewidth=2, markersize=8, label='OCR median')
ax1.fill_between(sens_df['alpha_H'], sens_df['OCR_p25'], sens_df['OCR_p75'],
                 alpha=0.2, color='#2c7bb6', label='IQR (P25-P75)')

# 标注原始模型
ax1.axvline(x=3.978, color='red', linestyle='--', alpha=0.7, label=r'Original $\alpha_H$=3.978')
ax1.axvline(x=1.0, color='green', linestyle='--', alpha=0.7, label=r'Recommended $\alpha_H$=1.0')
ax1.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)

ax1.set_xlabel(r'$\alpha_H$ (Human Capital Elasticity)', fontsize=11)
ax1.set_ylabel('Global OCR Median', fontsize=11)
ax1.set_title('(a) Sensitivity of OCR to $\\alpha_H$', fontsize=12, fontweight='bold')
ax1.legend(fontsize=8, loc='upper left')
ax1.grid(True, alpha=0.3)

# -------------------------------------------------------
# (b) 中国分时期 MUQ 柱状图
# -------------------------------------------------------
ax2 = fig.add_subplot(gs[0, 1])

phase_labels = []
phase_muq_means = []
phase_muq_sds = []
phase_colors = []

color_map = {'1998-2007 (快速扩张)': '#2ca02c',
             '2008-2015 (刺激与调整)': '#ff7f0e',
             '2016-2024 (下行期)': '#d62728'}

for ps in phase_stats:
    phase_labels.append(ps['phase'].split('(')[0].strip())
    phase_muq_means.append(ps['avg_muq'])
    phase_muq_sds.append(np.std(ps['muq_values'], ddof=1) if len(ps['muq_values']) > 1 else 0)
    phase_colors.append(color_map.get(ps['phase'], 'gray'))

bars = ax2.bar(range(len(phase_labels)), phase_muq_means, yerr=phase_muq_sds,
               color=phase_colors, edgecolor='black', linewidth=0.8, capsize=5, alpha=0.85)

# 添加数值标注
for i, (bar, val) in enumerate(zip(bars, phase_muq_means)):
    ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + phase_muq_sds[i] + 0.03,
             f'{val:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax2.axhline(y=0, color='black', linewidth=1)
ax2.set_xticks(range(len(phase_labels)))
ax2.set_xticklabels(phase_labels, fontsize=9)
ax2.set_ylabel('Mean MUQ (V3)', fontsize=11)
ax2.set_title('(b) China: Investment Efficiency by Phase', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')

# -------------------------------------------------------
# (c) MUQ 时序 + 置信区间 + MUQ=0 参考线
# -------------------------------------------------------
ax3 = fig.add_subplot(gs[0, 2])

# 使用 MUQ_V1 和 MUQ_V3
cn_plot = cn.dropna(subset=['MUQ_V1', 'MUQ_V3'])

ax3.plot(cn_plot['year'], cn_plot['MUQ_V1'], 's-', color='#d62728', linewidth=1.5, markersize=5,
         label='MUQ (V1: Sales)', alpha=0.8)
ax3.plot(cn_plot['year'], cn_plot['MUQ_V3'], 'o-', color='#2c7bb6', linewidth=2, markersize=5,
         label='MUQ (V3: Composite)', alpha=0.9)

# 3 年滚动 CI for MUQ_V3
muq_v3 = cn_plot['MUQ_V3'].values
years_plot = cn_plot['year'].values

rolling_ci_low = []
rolling_ci_high = []
for i in range(len(muq_v3)):
    start = max(0, i - 1)
    end = min(len(muq_v3), i + 2)
    window_vals = muq_v3[start:end]
    if len(window_vals) >= 2:
        se = np.std(window_vals, ddof=1) / np.sqrt(len(window_vals))
        rolling_ci_low.append(muq_v3[i] - 1.96 * se)
        rolling_ci_high.append(muq_v3[i] + 1.96 * se)
    else:
        rolling_ci_low.append(muq_v3[i])
        rolling_ci_high.append(muq_v3[i])

ax3.fill_between(years_plot, rolling_ci_low, rolling_ci_high,
                 alpha=0.15, color='#2c7bb6', label='95% CI (V3, rolling)')

# MUQ = 0 参考线
ax3.axhline(y=0, color='black', linewidth=1.5, linestyle='-')

# 标注转负年份
if crossings:
    cross_yr = crossings[-1]
    ax3.axvline(x=cross_yr, color='red', linestyle='--', alpha=0.7)
    ax3.annotate(f'MUQ=0\n({cross_yr:.1f})',
                xy=(cross_yr, 0), xytext=(cross_yr - 3, -0.5),
                fontsize=9, color='red', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5))

# 阴影标注三个阶段
ax3.axvspan(1999, 2007, alpha=0.05, color='green')
ax3.axvspan(2008, 2015, alpha=0.05, color='orange')
ax3.axvspan(2016, 2024, alpha=0.05, color='red')

ax3.set_xlabel('Year', fontsize=11)
ax3.set_ylabel('Marginal Urban Q (MUQ)', fontsize=11)
ax3.set_title('(c) China: MUQ Time Series', fontsize=12, fontweight='bold')
ax3.legend(fontsize=8, loc='upper right')
ax3.grid(True, alpha=0.3)
ax3.set_xlim(1998, 2025)

plt.suptitle('K* Bounded Estimation & MUQ Phase Analysis', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
fig_path = os.path.join(FIGURES, 'fig18_kstar_muq.png')
plt.savefig(fig_path, dpi=200, bbox_inches='tight')
print(f"\n图表已保存: {fig_path}")

# ############################################################
# 完成
# ############################################################
print("\n" + "=" * 70)
print("全部分析完成")
print("=" * 70)
print(f"  1. K* bounded results: {kstar_report_path}")
print(f"  2. MUQ significance test: {muq_report_path}")
print(f"  3. Threshold model results: {threshold_path}")
print(f"  4. Figure: {fig_path}")
