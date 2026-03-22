"""
62_iv_gmm_pvar.py — IV/GMM 估计与面板 VAR 分析
==============================================
目的：
  1. 用工具变量 (2SLS) 处理倒 U 型关系中的内生性问题
  2. 用 System GMM (简化版) 处理动态面板偏差
  3. 用面板 VAR 替代简单 Granger 因果检验

输入数据：
  - 02-data/processed/global_kstar_ocr_uci.csv  (Q, OCR, dV_V, inv_gdp_ratio)
  - 02-data/processed/global_urban_q_panel.csv   (urban_q, delta_V_ratio, ci_gdp_ratio, urban_pct)
  - 02-data/raw/penn_world_table.csv             (pop, hc 等人口变量)

输出：
  - 03-analysis/models/iv_gmm_results.txt
  - 03-analysis/models/panel_var_results.txt
  - 04-figures/drafts/fig19_iv_pvar.png

依赖包：
  pandas, numpy, statsmodels, scipy, matplotlib
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import StringIO

warnings.filterwarnings('ignore')
np.random.seed(42)

# ============================================================
# 路径设置
# ============================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
DATA_PROC = os.path.join(BASE, '02-data/processed')
DATA_RAW = os.path.join(BASE, '02-data/raw')
MODELS_DIR = os.path.join(BASE, '03-analysis/models')
FIG_DIR = os.path.join(BASE, '04-figures/drafts')

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

# ============================================================
# 数据加载与合并
# ============================================================
print("=" * 70)
print("数据加载与合并")
print("=" * 70)

# 主面板数据
df_main = pd.read_csv(os.path.join(DATA_PROC, 'global_kstar_ocr_uci.csv'))
# 补充面板数据（获取 urban_pct, gfcf_pct_gdp 等）
df_panel = pd.read_csv(os.path.join(DATA_PROC, 'global_urban_q_panel.csv'))
# PWT 数据（获取 pop 用于人口增长率 IV）
df_pwt = pd.read_csv(os.path.join(DATA_RAW, 'penn_world_table.csv'))

# 从 df_panel 提取补充变量
panel_cols = df_panel[['country_code', 'year', 'urban_pct', 'gfcf_pct_gdp',
                       'services_pct_gdp', 'pop_15_64_pct', 'total_pop']].copy()

# 从 PWT 提取人口数据（用于计算人口增长率）
pwt_cols = df_pwt[['countrycode', 'year', 'pop', 'hc']].copy()
pwt_cols = pwt_cols.rename(columns={'countrycode': 'country_code', 'pop': 'pwt_pop', 'hc': 'pwt_hc'})

# 合并
df = df_main.merge(panel_cols, on=['country_code', 'year'], how='left')
df = df.merge(pwt_cols, on=['country_code', 'year'], how='left')

# 排序
df = df.sort_values(['country_code', 'year']).reset_index(drop=True)

# 计算人口增长率
df['pop_growth'] = df.groupby('country_code')['pwt_pop'].transform(
    lambda x: x.pct_change() * 100
)

# 计算城镇化率（使用 urban_rate 或 urban_pct）
df['urbanization'] = df['urban_rate'].fillna(df['urban_pct'])

# 生成滞后变量
for lag in [1, 2, 3]:
    df[f'L{lag}_inv_gdp'] = df.groupby('country_code')['inv_gdp_ratio'].shift(lag)
    df[f'L{lag}_urbanization'] = df.groupby('country_code')['urbanization'].shift(lag)
    df[f'L{lag}_pop_growth'] = df.groupby('country_code')['pop_growth'].shift(lag)
    df[f'L{lag}_dV_V'] = df.groupby('country_code')['dV_V'].shift(lag)
    df[f'L{lag}_Q'] = df.groupby('country_code')['Q'].shift(lag)
    df[f'L{lag}_OCR'] = df.groupby('country_code')['OCR'].shift(lag)

# 投资强度的平方项
df['inv_gdp_sq'] = df['inv_gdp_ratio'] ** 2

# 工作样本：去除缺失值
iv_vars = ['dV_V', 'inv_gdp_ratio', 'inv_gdp_sq', 'urbanization',
           'services_share', 'working_age_pct',
           'L2_inv_gdp', 'L2_urbanization', 'L2_pop_growth']
df_iv = df.dropna(subset=iv_vars).copy()

print(f"合并后总样本: {len(df)} 行, {df['country_code'].nunique()} 个国家")
print(f"IV 工作样本: {len(df_iv)} 行, {df_iv['country_code'].nunique()} 个国家")
print(f"年份范围: {df_iv['year'].min()} - {df_iv['year'].max()}")


# ============================================================
# 辅助函数
# ============================================================
def two_stage_ls(y, X_endog, X_exog, Z, return_first_stage=False):
    """
    手动实现 2SLS 估计。

    Parameters
    ----------
    y : array, 因变量
    X_endog : array, 内生解释变量 (含平方项)
    X_exog : array, 外生控制变量 (含常数项)
    Z : array, 工具变量
    return_first_stage : bool

    Returns
    -------
    dict: 包含 2SLS 估计结果
    """
    n = len(y)

    # 第一阶段：对每个内生变量做回归
    # 全部外生变量（工具 + 控制）
    W = np.column_stack([Z, X_exog])
    X_endog_hat = np.zeros_like(X_endog)
    first_stage_results = []

    for j in range(X_endog.shape[1]):
        fs_model = sm.OLS(X_endog[:, j], W).fit()
        X_endog_hat[:, j] = fs_model.fittedvalues
        first_stage_results.append(fs_model)

    # 第二阶段：用拟合值替换内生变量
    X_full = np.column_stack([X_endog_hat, X_exog])
    X_full_original = np.column_stack([X_endog, X_exog])

    # 2SLS 估计
    ss_model = sm.OLS(y, X_full).fit()

    # 但标准误需要用原始 X 的残差来修正
    resid = y - X_full_original @ ss_model.params
    sigma2 = np.sum(resid ** 2) / (n - X_full.shape[1])

    # 正确的 2SLS 方差估计
    # V(beta) = sigma^2 * (X_hat' X_hat)^{-1}
    XhXh_inv = np.linalg.inv(X_full.T @ X_full)
    var_beta = sigma2 * XhXh_inv
    se_beta = np.sqrt(np.diag(var_beta))
    t_stats = ss_model.params / se_beta
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), n - X_full.shape[1]))

    result = {
        'params': ss_model.params,
        'se': se_beta,
        't_stats': t_stats,
        'p_values': p_values,
        'sigma2': sigma2,
        'nobs': n,
        'nvar': X_full.shape[1],
        'resid': resid,
        'r2': 1 - np.sum(resid ** 2) / np.sum((y - y.mean()) ** 2),
        'first_stage': first_stage_results if return_first_stage else None
    }
    return result


def sargan_test(resid, Z, X_exog):
    """Sargan 过度识别检验"""
    n = len(resid)
    W = np.column_stack([Z, X_exog])
    aux = sm.OLS(resid, W).fit()
    stat = n * aux.rsquared
    # 自由度 = 工具变量数 - 内生变量数
    df = Z.shape[1] - 2  # 2 个内生变量 (inv_gdp, inv_gdp_sq 视为 1 个内生来源的 2 个变换)
    # 实际上：内生变量数 = 2 (inv_gdp_ratio, inv_gdp_sq)
    # 工具变量数 = Z.shape[1]
    # 过度识别约束数 = Z.shape[1] - 2
    if df <= 0:
        return np.nan, np.nan, df
    p_val = 1 - stats.chi2.cdf(stat, df)
    return stat, p_val, df


def hausman_test(beta_iv, var_iv, beta_ols, var_ols):
    """Hausman 检验：比较 IV 和 OLS 估计"""
    diff = beta_iv - beta_ols
    var_diff = var_iv - var_ols
    # 仅用可靠的对角元素
    try:
        stat = diff.T @ np.linalg.inv(var_diff) @ diff
        df = len(diff)
        p_val = 1 - stats.chi2.cdf(stat, df)
    except np.linalg.LinAlgError:
        stat, p_val, df = np.nan, np.nan, len(diff)
    return stat, p_val, df


# ============================================================
# 分析 1：IV 估计（倒 U 型关系）
# ============================================================
print("\n" + "=" * 70)
print("分析 1：IV 估计 — 倒 U 型关系的因果识别")
print("=" * 70)

iv_output = StringIO()

def iprint(*args, **kwargs):
    """同时打印到控制台和文件"""
    print(*args, **kwargs)
    print(*args, file=iv_output, **kwargs)

# 准备变量
y = df_iv['dV_V'].values
endog1 = df_iv['inv_gdp_ratio'].values
endog2 = df_iv['inv_gdp_sq'].values
X_endog = np.column_stack([endog1, endog2])

# 控制变量：services_share, working_age_pct, 常数项
controls = df_iv[['services_share', 'working_age_pct']].values
X_exog = sm.add_constant(controls)

# --- OLS 基准 ---
iprint("\n--- OLS 基准回归 ---")
X_ols = np.column_stack([X_endog, X_exog])
ols_model = sm.OLS(y, X_ols).fit(cov_type='cluster',
                                   cov_kwds={'groups': df_iv['country_code'].values})

ols_names = ['inv_gdp_ratio', 'inv_gdp_sq', 'const', 'services_share', 'working_age_pct']
iprint(f"{'变量':<20s} {'系数':>12s} {'标准误':>12s} {'t值':>10s} {'p值':>10s}")
iprint("-" * 66)
for name, coef, se, t, p in zip(ols_names, ols_model.params,
                                  ols_model.bse, ols_model.tvalues, ols_model.pvalues):
    iprint(f"{name:<20s} {coef:>12.6f} {se:>12.6f} {t:>10.3f} {p:>10.4f}")
iprint(f"R-squared: {ols_model.rsquared:.4f}")
iprint(f"N = {ols_model.nobs:.0f}")

# 计算 OLS 倒 U 型顶点
b_ols = ols_model.params[0]
c_ols = ols_model.params[1]
if c_ols < 0:
    peak_ols = -b_ols / (2 * c_ols)
    iprint(f"OLS 倒 U 型顶点: inv_gdp_ratio = {peak_ols:.2f}% of GDP")
else:
    peak_ols = np.nan
    iprint("OLS: 二次项系数为正，无倒 U 型")

# --- IV 策略 1：单一 IV (L2.inv_gdp) ---
iprint("\n--- IV 策略 1: L2.inv_gdp 作为工具变量 ---")
Z1 = df_iv[['L2_inv_gdp']].values
# 为 inv_gdp_sq 添加 L2_inv_gdp^2 作为额外工具
Z1_full = np.column_stack([Z1, Z1**2])

iv1 = two_stage_ls(y, X_endog, X_exog, Z1_full, return_first_stage=True)

iprint(f"\n第一阶段 F 统计量:")
for j, (name, fs) in enumerate(zip(['inv_gdp_ratio', 'inv_gdp_sq'], iv1['first_stage'])):
    iprint(f"  {name}: F = {fs.fvalue:.2f}, p = {fs.f_pvalue:.6f}, R² = {fs.rsquared:.4f}")

iv1_names = ['inv_gdp_ratio', 'inv_gdp_sq', 'const', 'services_share', 'working_age_pct']
iprint(f"\n{'变量':<20s} {'系数':>12s} {'标准误':>12s} {'t值':>10s} {'p值':>10s}")
iprint("-" * 66)
for name, coef, se, t, p in zip(iv1_names, iv1['params'], iv1['se'],
                                  iv1['t_stats'], iv1['p_values']):
    iprint(f"{name:<20s} {coef:>12.6f} {se:>12.6f} {t:>10.3f} {p:>10.4f}")
iprint(f"R-squared (2SLS): {iv1['r2']:.4f}")

if iv1['params'][1] < 0:
    peak_iv1 = -iv1['params'][0] / (2 * iv1['params'][1])
    iprint(f"IV1 倒 U 型顶点: inv_gdp_ratio = {peak_iv1:.2f}% of GDP")

# Sargan 检验
s_stat, s_pval, s_df = sargan_test(iv1['resid'], Z1_full, X_exog)
if not np.isnan(s_stat):
    iprint(f"Sargan 检验: chi2({s_df}) = {s_stat:.3f}, p = {s_pval:.4f}")
    iprint(f"  {'不拒绝工具变量外生性 (通过)' if s_pval > 0.05 else '拒绝工具变量外生性 (未通过)'}")
else:
    iprint("Sargan 检验: 恰好识别，无法进行过度识别检验")

# --- IV 策略 2：多个 IV ---
iprint("\n--- IV 策略 2: L2.inv_gdp + L2.urbanization + pop_growth 作为工具变量 ---")
Z2 = df_iv[['L2_inv_gdp', 'L2_urbanization', 'L2_pop_growth']].values
Z2_full = np.column_stack([Z2, Z2[:, 0]**2])  # 加入 L2_inv_gdp^2

iv2 = two_stage_ls(y, X_endog, X_exog, Z2_full, return_first_stage=True)

iprint(f"\n第一阶段 F 统计量:")
for j, (name, fs) in enumerate(zip(['inv_gdp_ratio', 'inv_gdp_sq'], iv2['first_stage'])):
    iprint(f"  {name}: F = {fs.fvalue:.2f}, p = {fs.f_pvalue:.6f}, R² = {fs.rsquared:.4f}")

iprint(f"\n{'变量':<20s} {'系数':>12s} {'标准误':>12s} {'t值':>10s} {'p值':>10s}")
iprint("-" * 66)
for name, coef, se, t, p in zip(iv1_names, iv2['params'], iv2['se'],
                                  iv2['t_stats'], iv2['p_values']):
    iprint(f"{name:<20s} {coef:>12.6f} {se:>12.6f} {t:>10.3f} {p:>10.4f}")
iprint(f"R-squared (2SLS): {iv2['r2']:.4f}")

if iv2['params'][1] < 0:
    peak_iv2 = -iv2['params'][0] / (2 * iv2['params'][1])
    iprint(f"IV2 倒 U 型顶点: inv_gdp_ratio = {peak_iv2:.2f}% of GDP")

# Sargan 检验（多个工具变量，过度识别）
s_stat2, s_pval2, s_df2 = sargan_test(iv2['resid'], Z2_full, X_exog)
if not np.isnan(s_stat2):
    iprint(f"Sargan 检验: chi2({s_df2}) = {s_stat2:.3f}, p = {s_pval2:.4f}")
    iprint(f"  {'不拒绝工具变量外生性 (通过)' if s_pval2 > 0.05 else '拒绝工具变量外生性 (未通过)'}")

# --- Hausman 检验 ---
iprint("\n--- Hausman 检验: IV vs OLS ---")
# 比较内生变量的系数
idx_endog = [0, 1]  # inv_gdp_ratio, inv_gdp_sq
beta_iv = iv2['params'][idx_endog]
beta_ols = ols_model.params[idx_endog]

# IV 方差
sigma2_iv = iv2['sigma2']
X_endog_hat2 = np.zeros_like(X_endog)
W2 = np.column_stack([Z2_full, X_exog])
for j in range(2):
    X_endog_hat2[:, j] = sm.OLS(X_endog[:, j], W2).fit().fittedvalues
X_full_hat2 = np.column_stack([X_endog_hat2, X_exog])
var_iv_full = sigma2_iv * np.linalg.inv(X_full_hat2.T @ X_full_hat2)
var_iv = var_iv_full[np.ix_(idx_endog, idx_endog)]

# OLS 方差（非稳健，用于 Hausman）
ols_model_nocluster = sm.OLS(y, X_ols).fit()
var_ols = ols_model_nocluster.cov_params()[np.ix_(idx_endog, idx_endog)]

h_stat, h_pval, h_df = hausman_test(beta_iv, var_iv, beta_ols, var_ols)
iprint(f"Hausman 统计量: chi2({h_df}) = {h_stat:.3f}, p = {h_pval:.4f}")
if not np.isnan(h_pval):
    if h_pval < 0.05:
        iprint("结论: OLS 与 IV 估计有显著差异，存在内生性，应使用 IV 估计")
    else:
        iprint("结论: OLS 与 IV 估计无显著差异，OLS 一致，但 IV 效率较低")


# ============================================================
# 分析 2：System GMM（简化版）
# ============================================================
iprint("\n" + "=" * 70)
iprint("分析 2：System GMM（差分 + 滞后工具变量的简化实现）")
iprint("=" * 70)

# 准备动态面板数据
gmm_vars = ['dV_V', 'inv_gdp_ratio', 'inv_gdp_sq', 'services_share',
            'working_age_pct', 'L1_dV_V', 'L2_dV_V', 'L2_inv_gdp']
df_gmm = df.dropna(subset=gmm_vars).copy()

iprint(f"\nGMM 工作样本: {len(df_gmm)} 行, {df_gmm['country_code'].nunique()} 个国家")

# 差分变换消除固定效应
for var in ['dV_V', 'inv_gdp_ratio', 'inv_gdp_sq', 'services_share', 'working_age_pct',
            'L1_dV_V']:
    df_gmm[f'd_{var}'] = df_gmm.groupby('country_code')[var].diff()

df_gmm_clean = df_gmm.dropna(subset=[f'd_{v}' for v in
    ['dV_V', 'inv_gdp_ratio', 'inv_gdp_sq', 'services_share', 'working_age_pct', 'L1_dV_V']]).copy()

# 差分方程的 2SLS：用 L2 水平变量作为工具
y_gmm = df_gmm_clean['d_dV_V'].values
X_gmm = df_gmm_clean[['d_L1_dV_V', 'd_inv_gdp_ratio', 'd_inv_gdp_sq',
                        'd_services_share', 'd_working_age_pct']].values
X_gmm = sm.add_constant(X_gmm)

# 工具变量：L2 水平值
Z_gmm = df_gmm_clean[['L2_dV_V', 'L2_inv_gdp']].values
Z_gmm_full = np.column_stack([Z_gmm, Z_gmm[:, 1]**2])

iprint(f"差分 GMM 样本: {len(df_gmm_clean)} 行")
iprint(f"工具变量数: {Z_gmm_full.shape[1]}")
iprint(f"国家数: {df_gmm_clean['country_code'].nunique()}")
n_countries_gmm = df_gmm_clean['country_code'].nunique()
iprint(f"工具变量 < 国家数: {Z_gmm_full.shape[1]} < {n_countries_gmm} = "
       f"{'是 (合理)' if Z_gmm_full.shape[1] < n_countries_gmm else '否 (可能过多)'}")

# 第一阶段
W_gmm = np.column_stack([Z_gmm_full, X_gmm[:, [0, 4, 5]]])  # 工具 + 外生差分控制 + 常数
gmm_first_stages = []
X_endog_gmm = X_gmm[:, 1:4]  # d_L1_dV_V, d_inv_gdp_ratio, d_inv_gdp_sq
X_exog_gmm = X_gmm[:, [0, 4, 5]]  # const, d_services_share, d_working_age_pct

gmm_result = two_stage_ls(y_gmm, X_endog_gmm, X_exog_gmm, Z_gmm_full, return_first_stage=True)

gmm_names = ['L1.dV_V (差分)', 'inv_gdp (差分)', 'inv_gdp_sq (差分)',
             'const', 'services (差分)', 'work_age (差分)']

iprint(f"\n{'变量':<25s} {'系数':>12s} {'标准误':>12s} {'t值':>10s} {'p值':>10s}")
iprint("-" * 71)
for name, coef, se, t, p in zip(gmm_names, gmm_result['params'], gmm_result['se'],
                                  gmm_result['t_stats'], gmm_result['p_values']):
    iprint(f"{name:<25s} {coef:>12.6f} {se:>12.6f} {t:>10.3f} {p:>10.4f}")

# 动态系数（L1.dV_V 的系数应在 0-1 之间）
rho = gmm_result['params'][0]
iprint(f"\n自回归系数 rho = {rho:.4f}")
if 0 < rho < 1:
    iprint("  rho 在 (0, 1) 之间，符合稳定动态面板预期")
else:
    iprint(f"  rho 不在 (0, 1) 之间，可能存在模型设定问题")

# AR(1) 和 AR(2) 检验（对差分后的残差）
resid_gmm = gmm_result['resid']
# AR(1): 差分残差天然存在一阶自相关（不要求不显著）
# AR(2): 水平残差无二阶自相关才表明模型正确设定
resid_df = df_gmm_clean[['country_code', 'year']].copy()
resid_df['resid'] = resid_gmm
resid_df['L1_resid'] = resid_df.groupby('country_code')['resid'].shift(1)
resid_df['L2_resid'] = resid_df.groupby('country_code')['resid'].shift(2)

ar1_data = resid_df.dropna(subset=['L1_resid'])
ar1_corr = np.corrcoef(ar1_data['resid'], ar1_data['L1_resid'])[0, 1]
ar1_z = ar1_corr * np.sqrt(len(ar1_data))
ar1_p = 2 * (1 - stats.norm.cdf(np.abs(ar1_z)))

ar2_data = resid_df.dropna(subset=['L2_resid'])
ar2_corr = np.corrcoef(ar2_data['resid'], ar2_data['L2_resid'])[0, 1]
ar2_z = ar2_corr * np.sqrt(len(ar2_data))
ar2_p = 2 * (1 - stats.norm.cdf(np.abs(ar2_z)))

iprint(f"\nAR(1) 检验: z = {ar1_z:.3f}, p = {ar1_p:.4f}")
iprint(f"  {'显著（预期中的，差分残差天然存在 AR(1)）' if ar1_p < 0.05 else '不显著'}")
iprint(f"AR(2) 检验: z = {ar2_z:.3f}, p = {ar2_p:.4f}")
iprint(f"  {'不显著（模型设定通过）' if ar2_p > 0.05 else '显著（可能存在模型设定问题）'}")

# Hansen J 检验
s_gmm, sp_gmm, sd_gmm = sargan_test(resid_gmm, Z_gmm_full, X_exog_gmm)
if not np.isnan(s_gmm) and sd_gmm > 0:
    iprint(f"Hansen J 检验: chi2({sd_gmm}) = {s_gmm:.3f}, p = {sp_gmm:.4f}")
    iprint(f"  {'不拒绝过度识别约束 (通过)' if sp_gmm > 0.05 else '拒绝过度识别约束 (未通过)'}")

# GMM 倒 U 型顶点
b_gmm = gmm_result['params'][1]
c_gmm = gmm_result['params'][2]
if c_gmm < 0:
    peak_gmm = -b_gmm / (2 * c_gmm)
    iprint(f"\nGMM 倒 U 型顶点: inv_gdp_ratio = {peak_gmm:.2f}% of GDP")

# --- 估计方法对比汇总 ---
iprint("\n" + "=" * 70)
iprint("倒 U 型估计结果对比")
iprint("=" * 70)
iprint(f"{'方法':<15s} {'β (inv_gdp)':>12s} {'γ (inv_gdp²)':>14s} {'顶点':>10s} {'R²':>8s}")
iprint("-" * 61)

methods = [
    ('OLS', ols_model.params[0], ols_model.params[1],
     peak_ols if c_ols < 0 else np.nan, ols_model.rsquared),
    ('IV (单一)', iv1['params'][0], iv1['params'][1],
     -iv1['params'][0]/(2*iv1['params'][1]) if iv1['params'][1] < 0 else np.nan, iv1['r2']),
    ('IV (多重)', iv2['params'][0], iv2['params'][1],
     -iv2['params'][0]/(2*iv2['params'][1]) if iv2['params'][1] < 0 else np.nan, iv2['r2']),
    ('GMM (差分)', b_gmm, c_gmm,
     peak_gmm if c_gmm < 0 else np.nan, gmm_result['r2']),
]

for name, b, c, peak, r2 in methods:
    peak_str = f"{peak:.4f}" if not np.isnan(peak) else "N/A"
    iprint(f"{name:<15s} {b:>12.6f} {c:>14.6f} {peak_str:>10s} {r2:>8.4f}")

# 保存 IV/GMM 结果
with open(os.path.join(MODELS_DIR, 'iv_gmm_results.txt'), 'w', encoding='utf-8') as f:
    f.write(iv_output.getvalue())
print(f"\nIV/GMM 结果已保存至: {MODELS_DIR}/iv_gmm_results.txt")


# ============================================================
# 分析 3：面板 VAR（Q 与 OCR 的动态联动）
# ============================================================
print("\n" + "=" * 70)
print("分析 3：面板 VAR — Q 与 OCR 的动态联动")
print("=" * 70)

pvar_output = StringIO()

def pprint(*args, **kwargs):
    print(*args, **kwargs)
    print(*args, file=pvar_output, **kwargs)

# 准备面板 VAR 数据
pvar_vars = ['Q', 'OCR', 'L1_Q', 'L2_Q', 'L1_OCR', 'L2_OCR']
df_pvar = df.dropna(subset=pvar_vars).copy()

pprint(f"面板 VAR 工作样本: {len(df_pvar)} 行, {df_pvar['country_code'].nunique()} 个国家")
pprint(f"年份范围: {df_pvar['year'].min()} - {df_pvar['year'].max()}")

# 组内去均值（固定效应）
for var in ['Q', 'OCR', 'L1_Q', 'L2_Q', 'L1_OCR', 'L2_OCR']:
    group_mean = df_pvar.groupby('country_code')[var].transform('mean')
    df_pvar[f'{var}_dm'] = df_pvar[var] - group_mean

# 添加时间虚拟变量的替代：年份去均值
for var in ['Q_dm', 'OCR_dm', 'L1_Q_dm', 'L2_Q_dm', 'L1_OCR_dm', 'L2_OCR_dm']:
    year_mean = df_pvar.groupby('year')[var].transform('mean')
    df_pvar[f'{var}_tw'] = df_pvar[var] - year_mean  # 双向去均值

# --- VAR 方程 1: Q ---
pprint("\n--- VAR 方程 1: Q_it = f(L1.Q, L2.Q, L1.OCR, L2.OCR) ---")
y_q = df_pvar['Q_dm_tw'].values
X_q = df_pvar[['L1_Q_dm_tw', 'L2_Q_dm_tw', 'L1_OCR_dm_tw', 'L2_OCR_dm_tw']].values
X_q = sm.add_constant(X_q)

# Cluster-robust 标准误
q_model = sm.OLS(y_q, X_q).fit(cov_type='cluster',
                                 cov_kwds={'groups': df_pvar['country_code'].values})

q_names = ['const', 'L1.Q', 'L2.Q', 'L1.OCR', 'L2.OCR']
pprint(f"{'变量':<12s} {'系数':>12s} {'Cluster SE':>12s} {'t值':>10s} {'p值':>10s}")
pprint("-" * 58)
for name, coef, se, t, p in zip(q_names, q_model.params, q_model.bse,
                                  q_model.tvalues, q_model.pvalues):
    pprint(f"{name:<12s} {coef:>12.6f} {se:>12.6f} {t:>10.3f} {p:>10.4f}")
pprint(f"R² = {q_model.rsquared:.4f}, N = {q_model.nobs:.0f}")

# Granger 因果检验：OCR → Q（联合检验 L1.OCR 和 L2.OCR 系数 = 0）
R_q = np.zeros((2, X_q.shape[1]))
R_q[0, 3] = 1  # L1.OCR
R_q[1, 4] = 1  # L2.OCR
granger_q = q_model.f_test(R_q)
fval_q = float(np.squeeze(granger_q.fvalue))
pval_q = float(np.squeeze(granger_q.pvalue))
pprint(f"\nGranger 因果: OCR → Q")
pprint(f"  F = {fval_q:.3f}, p = {pval_q:.4f}")
pprint(f"  {'OCR Granger-cause Q (显著)' if pval_q < 0.05 else 'OCR 不 Granger-cause Q (不显著)'}")

# --- VAR 方程 2: OCR ---
pprint("\n--- VAR 方程 2: OCR_it = f(L1.Q, L2.Q, L1.OCR, L2.OCR) ---")
y_ocr = df_pvar['OCR_dm_tw'].values
X_ocr = df_pvar[['L1_Q_dm_tw', 'L2_Q_dm_tw', 'L1_OCR_dm_tw', 'L2_OCR_dm_tw']].values
X_ocr = sm.add_constant(X_ocr)

ocr_model = sm.OLS(y_ocr, X_ocr).fit(cov_type='cluster',
                                       cov_kwds={'groups': df_pvar['country_code'].values})

ocr_names = ['const', 'L1.Q', 'L2.Q', 'L1.OCR', 'L2.OCR']
pprint(f"{'变量':<12s} {'系数':>12s} {'Cluster SE':>12s} {'t值':>10s} {'p值':>10s}")
pprint("-" * 58)
for name, coef, se, t, p in zip(ocr_names, ocr_model.params, ocr_model.bse,
                                  ocr_model.tvalues, ocr_model.pvalues):
    pprint(f"{name:<12s} {coef:>12.6f} {se:>12.6f} {t:>10.3f} {p:>10.4f}")
pprint(f"R² = {ocr_model.rsquared:.4f}, N = {ocr_model.nobs:.0f}")

# Granger 因果检验：Q → OCR
R_ocr = np.zeros((2, X_ocr.shape[1]))
R_ocr[0, 1] = 1  # L1.Q
R_ocr[1, 2] = 1  # L2.Q
granger_ocr = ocr_model.f_test(R_ocr)
fval_ocr = float(np.squeeze(granger_ocr.fvalue))
pval_ocr = float(np.squeeze(granger_ocr.pvalue))
pprint(f"\nGranger 因果: Q → OCR")
pprint(f"  F = {fval_ocr:.3f}, p = {pval_ocr:.4f}")
pprint(f"  {'Q Granger-cause OCR (显著)' if pval_ocr < 0.05 else 'Q 不 Granger-cause OCR (不显著)'}")

# --- 滞后阶数选择 (AIC/BIC) ---
pprint("\n--- 滞后阶数选择 ---")
for max_lag in [1, 2, 3]:
    lag_vars_q = []
    lag_vars_ocr = []
    for l in range(1, max_lag + 1):
        lag_vars_q.extend([f'L{l}_Q_dm_tw', f'L{l}_OCR_dm_tw'])
        lag_vars_ocr.extend([f'L{l}_Q_dm_tw', f'L{l}_OCR_dm_tw'])

    # 需要生成 L3 如果 max_lag=3
    if max_lag == 3:
        for var in ['Q', 'OCR']:
            col = f'L3_{var}'
            if col not in df_pvar.columns:
                df_pvar[col] = df_pvar.groupby('country_code')[var].shift(3)
                group_mean = df_pvar.groupby('country_code')[col].transform('mean')
                df_pvar[f'{col}_dm'] = df_pvar[col] - group_mean
                year_mean = df_pvar.groupby('year')[f'{col}_dm'].transform('mean')
                df_pvar[f'{col}_dm_tw'] = df_pvar[f'{col}_dm'] - year_mean

    available = [v for v in lag_vars_q if v in df_pvar.columns]
    if len(available) == len(lag_vars_q):
        sub = df_pvar.dropna(subset=available + ['Q_dm_tw'])
        X_test = sm.add_constant(sub[available].values)
        y_test = sub['Q_dm_tw'].values
        m = sm.OLS(y_test, X_test).fit()
        pprint(f"  Lag {max_lag}: AIC = {m.aic:.1f}, BIC = {m.bic:.1f}, N = {len(sub)}")

# --- 脉冲响应函数 (IRF) ---
pprint("\n--- 脉冲响应函数 (IRF) ---")

# 提取 VAR 系数矩阵
# 系统: [Q_t, OCR_t]' = A1 [Q_{t-1}, OCR_{t-1}]' + A2 [Q_{t-2}, OCR_{t-2}]' + e_t
A1 = np.array([
    [q_model.params[1], q_model.params[3]],    # Q 方程: L1.Q, L1.OCR
    [ocr_model.params[1], ocr_model.params[3]]  # OCR 方程: L1.Q, L1.OCR
])
A2 = np.array([
    [q_model.params[2], q_model.params[4]],    # Q 方程: L2.Q, L2.OCR
    [ocr_model.params[2], ocr_model.params[4]]  # OCR 方程: L2.Q, L2.OCR
])

pprint(f"\nA1 矩阵 (1 期滞后系数):")
pprint(f"  [{A1[0,0]:.4f}  {A1[0,1]:.4f}]")
pprint(f"  [{A1[1,0]:.4f}  {A1[1,1]:.4f}]")
pprint(f"\nA2 矩阵 (2 期滞后系数):")
pprint(f"  [{A2[0,0]:.4f}  {A2[0,1]:.4f}]")
pprint(f"  [{A2[1,0]:.4f}  {A2[1,1]:.4f}]")

# 计算 IRF（递归方法）
n_periods = 15
irf = np.zeros((n_periods + 1, 2, 2))  # [horizon, response_var, shock_var]

# 残差协方差矩阵
resid_q = q_model.resid
resid_ocr = ocr_model.resid
Sigma = np.cov(resid_q, resid_ocr)

# Cholesky 分解用于正交化冲击
P = np.linalg.cholesky(Sigma)

# 初始冲击：1 标准差
irf[0] = P  # 即时响应

# 递归计算 IRF
# 使用伴随矩阵形式：
# Y_t = A1 Y_{t-1} + A2 Y_{t-2}
# 状态空间: [Y_t; Y_{t-1}] = F [Y_{t-1}; Y_{t-2}]
F = np.zeros((4, 4))
F[:2, :2] = A1
F[:2, 2:] = A2
F[2:, :2] = np.eye(2)

# 用状态空间递归
state = np.zeros((4, 2))
state[:2, :] = P  # 初始冲击
for h in range(1, n_periods + 1):
    state = F @ state
    irf[h] = state[:2, :]

pprint("\nIRF: OCR 冲击 (1 SD) 对 Q 的响应:")
pprint(f"{'期数':>5s} {'响应':>12s}")
for h in range(n_periods + 1):
    pprint(f"{h:>5d} {irf[h, 0, 1]:>12.6f}")  # Q 对 OCR 冲击的响应

pprint("\nIRF: Q 冲击 (1 SD) 对 OCR 的响应:")
pprint(f"{'期数':>5s} {'响应':>12s}")
for h in range(n_periods + 1):
    pprint(f"{h:>5d} {irf[h, 1, 0]:>12.6f}")  # OCR 对 Q 冲击的响应

# --- Bootstrap 置信区间 ---
pprint("\n--- Bootstrap IRF 置信区间 (500 次重抽样) ---")
n_boot = 500
irf_boot = np.zeros((n_boot, n_periods + 1, 2, 2))

countries = df_pvar['country_code'].unique()
n_countries = len(countries)

for b in range(n_boot):
    # 按国家重抽样 (block bootstrap)
    boot_countries = np.random.choice(countries, size=n_countries, replace=True)
    boot_dfs = []
    for i, c in enumerate(boot_countries):
        cdf = df_pvar[df_pvar['country_code'] == c].copy()
        cdf['country_code_boot'] = f'{c}_{i}'
        boot_dfs.append(cdf)
    boot_df = pd.concat(boot_dfs, ignore_index=True)

    # 重新估计 VAR
    y_q_b = boot_df['Q_dm_tw'].values
    X_q_b = boot_df[['L1_Q_dm_tw', 'L2_Q_dm_tw', 'L1_OCR_dm_tw', 'L2_OCR_dm_tw']].values
    X_q_b = sm.add_constant(X_q_b)

    y_ocr_b = boot_df['OCR_dm_tw'].values
    X_ocr_b = boot_df[['L1_Q_dm_tw', 'L2_Q_dm_tw', 'L1_OCR_dm_tw', 'L2_OCR_dm_tw']].values
    X_ocr_b = sm.add_constant(X_ocr_b)

    try:
        q_b = sm.OLS(y_q_b, X_q_b).fit()
        ocr_b = sm.OLS(y_ocr_b, X_ocr_b).fit()

        A1_b = np.array([[q_b.params[1], q_b.params[3]],
                          [ocr_b.params[1], ocr_b.params[3]]])
        A2_b = np.array([[q_b.params[2], q_b.params[4]],
                          [ocr_b.params[2], ocr_b.params[4]]])

        Sigma_b = np.cov(q_b.resid, ocr_b.resid)
        P_b = np.linalg.cholesky(Sigma_b)

        F_b = np.zeros((4, 4))
        F_b[:2, :2] = A1_b
        F_b[:2, 2:] = A2_b
        F_b[2:, :2] = np.eye(2)

        state_b = np.zeros((4, 2))
        state_b[:2, :] = P_b
        irf_boot[b, 0] = P_b
        for h in range(1, n_periods + 1):
            state_b = F_b @ state_b
            irf_boot[b, h] = state_b[:2, :]
    except Exception:
        irf_boot[b] = np.nan

# 去掉失败的 bootstrap
valid = ~np.any(np.isnan(irf_boot.reshape(n_boot, -1)), axis=1)
irf_boot_valid = irf_boot[valid]
pprint(f"有效 bootstrap 样本: {valid.sum()}/{n_boot}")

irf_lo = np.percentile(irf_boot_valid, 2.5, axis=0)
irf_hi = np.percentile(irf_boot_valid, 97.5, axis=0)

# --- 方差分解 (FEVD) ---
pprint("\n--- 预测误差方差分解 (FEVD) ---")

# 累积 IRF 的平方 → 方差贡献
mse = np.zeros((n_periods + 1, 2, 2))  # [horizon, response_var, shock_var]
for h in range(n_periods + 1):
    for j in range(2):  # shock variable
        mse[h, :, j] = np.sum(irf[:h+1, :, j] ** 2, axis=0)

# 总方差
total_mse = mse.sum(axis=2)

# 方差分解比例
fevd = np.zeros_like(mse)
for j in range(2):
    fevd[:, :, j] = mse[:, :, j] / np.maximum(total_mse, 1e-10)

pprint(f"\nQ 的方差分解:")
pprint(f"{'期数':>5s} {'自身 (Q→Q)':>12s} {'OCR→Q':>12s}")
for h in [0, 1, 2, 5, 10, 15]:
    if h <= n_periods:
        pprint(f"{h:>5d} {fevd[h, 0, 0]*100:>11.1f}% {fevd[h, 0, 1]*100:>11.1f}%")

pprint(f"\nOCR 的方差分解:")
pprint(f"{'期数':>5s} {'Q→OCR':>12s} {'自身 (OCR→OCR)':>15s}")
for h in [0, 1, 2, 5, 10, 15]:
    if h <= n_periods:
        pprint(f"{h:>5d} {fevd[h, 1, 0]*100:>11.1f}% {fevd[h, 1, 1]*100:>14.1f}%")

# 保存面板 VAR 结果
with open(os.path.join(MODELS_DIR, 'panel_var_results.txt'), 'w', encoding='utf-8') as f:
    f.write(pvar_output.getvalue())
print(f"\n面板 VAR 结果已保存至: {MODELS_DIR}/panel_var_results.txt")


# ============================================================
# 可视化（3 子图）
# ============================================================
print("\n" + "=" * 70)
print("生成可视化")
print("=" * 70)

fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

# --- (a) IV vs OLS 倒 U 型曲线 ---
ax = axes[0]
x_range = np.linspace(5, 65, 200)  # inv_gdp_ratio 以百分比表示 (e.g., 30 = 30%)

# 散点图（使用原始数据，稀释显示）
sample_idx = np.random.choice(len(df_iv), size=min(2000, len(df_iv)), replace=False)
ax.scatter(df_iv['inv_gdp_ratio'].values[sample_idx],
           df_iv['dV_V'].values[sample_idx],
           alpha=0.08, s=8, c='gray', zorder=1, label='_nolegend_')

# OLS 曲线
y_ols_pred = (ols_model.params[0] * x_range +
              ols_model.params[1] * x_range**2 +
              ols_model.params[2] +
              ols_model.params[3] * df_iv['services_share'].mean() +
              ols_model.params[4] * df_iv['working_age_pct'].mean())
ax.plot(x_range, y_ols_pred, 'b-', linewidth=2.2, label='OLS', zorder=3)

# IV 曲线（使用多重 IV 估计）
y_iv_pred = (iv2['params'][0] * x_range +
             iv2['params'][1] * x_range**2 +
             iv2['params'][2] +
             iv2['params'][3] * df_iv['services_share'].mean() +
             iv2['params'][4] * df_iv['working_age_pct'].mean())
ax.plot(x_range, y_iv_pred, 'r--', linewidth=2.2, label='IV (2SLS)', zorder=3)

# GMM 曲线
y_gmm_pred = (gmm_result['params'][1] * x_range +
              gmm_result['params'][2] * x_range**2 +
              gmm_result['params'][3])
ax.plot(x_range, y_gmm_pred, 'g:', linewidth=2.2, label='GMM (Diff)', zorder=3)

# 标注顶点
for method, peak, color, marker in [
    ('OLS', peak_ols, 'b', 'o'),
    ('IV', -iv2['params'][0]/(2*iv2['params'][1]) if iv2['params'][1] < 0 else np.nan, 'r', 's'),
    ('GMM', peak_gmm if c_gmm < 0 else np.nan, 'g', '^')
]:
    if not np.isnan(peak) and 5 < peak < 65:
        ax.axvline(x=peak, color=color, alpha=0.3, linestyle=':', linewidth=1)

ax.set_xlabel('Investment / GDP (%)', fontsize=11)
ax.set_ylabel(r'$\Delta V / V$', fontsize=11)
ax.set_title('(a) Inverted-U: OLS vs IV vs GMM', fontsize=12, fontweight='bold')
ax.legend(fontsize=9, loc='upper right')
ax.set_xlim(5, 65)

# --- (b) 脉冲响应函数 ---
ax = axes[1]
horizons = np.arange(n_periods + 1)

# OCR → Q
ax.plot(horizons, irf[:, 0, 1], 'b-o', markersize=4, linewidth=1.8, label='OCR shock → Q')
ax.fill_between(horizons, irf_lo[:, 0, 1], irf_hi[:, 0, 1], alpha=0.15, color='b')

# Q → OCR
ax.plot(horizons, irf[:, 1, 0], 'r-s', markersize=4, linewidth=1.8, label='Q shock → OCR')
ax.fill_between(horizons, irf_lo[:, 1, 0], irf_hi[:, 1, 0], alpha=0.15, color='r')

ax.axhline(y=0, color='k', linewidth=0.5, linestyle='-')
ax.set_xlabel('Horizon (years)', fontsize=11)
ax.set_ylabel('Response', fontsize=11)
ax.set_title('(b) Panel VAR Impulse Response', fontsize=12, fontweight='bold')
ax.legend(fontsize=9)
ax.set_xlim(0, n_periods)

# --- (c) 方差分解 ---
ax = axes[2]
horizons_bar = [1, 2, 5, 10, 15]
bar_width = 0.35
x_pos = np.arange(len(horizons_bar))

# Q 的方差分解
q_self = [fevd[h, 0, 0] * 100 for h in horizons_bar]
q_from_ocr = [fevd[h, 0, 1] * 100 for h in horizons_bar]

ax.bar(x_pos - bar_width/2, q_self, bar_width, label='Q → Q (own)', color='steelblue', alpha=0.85)
ax.bar(x_pos - bar_width/2, q_from_ocr, bar_width, bottom=q_self,
       label='OCR → Q', color='lightcoral', alpha=0.85)

# OCR 的方差分解
ocr_from_q = [fevd[h, 1, 0] * 100 for h in horizons_bar]
ocr_self = [fevd[h, 1, 1] * 100 for h in horizons_bar]

ax.bar(x_pos + bar_width/2, ocr_self, bar_width, label='OCR → OCR (own)', color='darkorange', alpha=0.85)
ax.bar(x_pos + bar_width/2, ocr_from_q, bar_width, bottom=ocr_self,
       label='Q → OCR', color='lightblue', alpha=0.85)

ax.set_xticks(x_pos)
ax.set_xticklabels([f'h={h}' for h in horizons_bar])
ax.set_xlabel('Forecast Horizon', fontsize=11)
ax.set_ylabel('Variance Share (%)', fontsize=11)
ax.set_title('(c) Forecast Error Variance Decomposition', fontsize=12, fontweight='bold')
ax.legend(fontsize=8, loc='center right')
ax.set_ylim(0, 105)

# 在柱子上方标注百分比
for i, h in enumerate(horizons_bar):
    ax.text(x_pos[i] - bar_width/2, 102, f'{q_from_ocr[i]:.0f}%',
            ha='center', va='bottom', fontsize=7, color='darkred')
    ax.text(x_pos[i] + bar_width/2, 102, f'{ocr_from_q[i]:.0f}%',
            ha='center', va='bottom', fontsize=7, color='darkblue')

plt.tight_layout()
fig_path = os.path.join(FIG_DIR, 'fig19_iv_pvar.png')
plt.savefig(fig_path, dpi=200, bbox_inches='tight')
plt.close()
print(f"图表已保存至: {fig_path}")

print("\n" + "=" * 70)
print("全部分析完成")
print("=" * 70)
