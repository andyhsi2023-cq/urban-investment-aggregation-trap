#!/usr/bin/env python3
"""
n06_betav_decomposition.py — beta_V 机械成分分解分析
=====================================================
目的: 将 V ~ N^beta_V 分解为机械成分 (Pop 贡献 beta=1) 和经济信号 (beta_A + beta_P)
      V = Pop * PerCapitaArea * Price  =>  ln(V) = ln(Pop) + ln(PCA) + ln(Price)
      因此 beta_V = 1 + beta_A + beta_P

      beta_A = d ln(PCA) / d ln(Pop)  — 人均面积对城市规模的标度
      beta_P = d ln(Price) / d ln(Pop) — 价格对城市规模的标度
      经济信号 = beta_A + beta_P = beta_V - 1

输入: china_275_city_panel.csv, us_msa_muq_panel.csv
输出: betav_decomposition_report.txt
依赖: numpy, pandas, scipy, statsmodels
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
import sys

np.random.seed(42)

# ============================================================
# 路径配置
# ============================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
DATA_DIR = f'{BASE}/02-data/processed'
REPORT_OUT = f'{BASE}/03-analysis/models/betav_decomposition_report.txt'

report_lines = []
def rpt(s=''):
    report_lines.append(s)
    print(s)

# ============================================================
# 辅助函数
# ============================================================

def ols_log_scaling(y, x, label_y='y', label_x='x'):
    """对 ln(y) ~ ln(x) 做 OLS，返回 beta, se, ci, p, R2, n"""
    mask = (y > 0) & (x > 0) & np.isfinite(y) & np.isfinite(x)
    ly = np.log(y[mask].values)
    lx = np.log(x[mask].values)
    X = sm.add_constant(lx)
    model = sm.OLS(ly, X).fit(cov_type='HC1')
    beta = model.params[1]
    se = model.bse[1]
    ci_arr = model.conf_int()
    if hasattr(ci_arr, 'iloc'):
        ci_lo, ci_hi = ci_arr.iloc[1]
    else:
        ci_lo, ci_hi = ci_arr[1]
    p_val = model.pvalues[1]
    r2 = model.rsquared
    n = len(ly)
    return {
        'label': f'ln({label_y}) ~ ln({label_x})',
        'beta': beta, 'se': se, 'ci_lo': ci_lo, 'ci_hi': ci_hi,
        'p': p_val, 'R2': r2, 'n': n, 'model': model,
        'ly': ly, 'lx': lx
    }


def bootstrap_beta(y, x, n_boot=2000):
    """Bootstrap 估计 beta 的分布"""
    mask = (y > 0) & (x > 0) & np.isfinite(y) & np.isfinite(x)
    ly = np.log(y[mask].values)
    lx = np.log(x[mask].values)
    n = len(ly)
    betas = []
    for _ in range(n_boot):
        idx = np.random.choice(n, n, replace=True)
        X = sm.add_constant(lx[idx])
        try:
            m = sm.OLS(ly[idx], X).fit()
            betas.append(m.params[1])
        except Exception:
            pass
    betas = np.array(betas)
    return betas


def format_result(res, indent='  '):
    """格式化单个回归结果"""
    return (f"{indent}{res['label']}:\n"
            f"{indent}  beta = {res['beta']:.4f}  (SE = {res['se']:.4f})\n"
            f"{indent}  95% CI = [{res['ci_lo']:.4f}, {res['ci_hi']:.4f}]\n"
            f"{indent}  p = {res['p']:.2e},  R2 = {res['R2']:.4f},  n = {res['n']}")


# ============================================================
# PART 1: 中国城市 beta_V 分解
# ============================================================
rpt('=' * 72)
rpt('n06_betav_decomposition.py')
rpt('beta_V 机械成分分解: V = Pop * PerCapitaArea * Price')
rpt('=' * 72)
rpt()

df_cn = pd.read_csv(f'{DATA_DIR}/china_275_city_panel.csv')
rpt(f'中国数据: {df_cn.shape[0]} 行, {df_cn["city"].nunique()} 城市, '
    f'{df_cn["year"].min()}-{df_cn["year"].max()}')

# 构造变量
# urban_pop_10k -> Pop (万人)
# housing_stock_10k_m2 / urban_pop_10k -> PerCapitaArea (m2/人)
# housing_price_yuan_m2 -> Price (元/m2)
# V_housing_100m -> V (亿元)
df_cn['Pop'] = df_cn['urban_pop_10k']
df_cn['PCA'] = df_cn['housing_stock_10k_m2'] / df_cn['urban_pop_10k']
df_cn['Price'] = df_cn['housing_price_yuan_m2']
df_cn['V'] = df_cn['V_housing_100m']

# 验证恒等式: V = Pop * PCA * Price (单位换算)
# V_100m = Pop_10k * PCA_m2 * Price_yuan_m2
# = (Pop * 1e4) * PCA * Price / 1e8
# = Pop * PCA * Price * 1e4 / 1e8
# = Pop * PCA * Price / 1e4
df_cn['V_check'] = df_cn['Pop'] * df_cn['PCA'] * df_cn['Price'] / 1e4
identity_err = np.abs(df_cn['V'] - df_cn['V_check']).max()
rpt(f'恒等式验证 max|V - Pop*PCA*Price| = {identity_err:.6f} 亿元')
rpt()

# ---- 逐年截面回归 ----
rpt('-' * 72)
rpt('PART 1A: 中国 — 逐年截面回归 (Cross-sectional OLS with HC1 SE)')
rpt('-' * 72)

cn_yearly = []
for yr in sorted(df_cn['year'].unique()):
    sub = df_cn[df_cn['year'] == yr].copy()
    r_v = ols_log_scaling(sub['V'], sub['Pop'], 'V', 'Pop')
    r_a = ols_log_scaling(sub['PCA'], sub['Pop'], 'PCA', 'Pop')
    r_p = ols_log_scaling(sub['Price'], sub['Pop'], 'Price', 'Pop')
    cn_yearly.append({
        'year': yr, 'n': r_v['n'],
        'beta_V': r_v['beta'], 'se_V': r_v['se'], 'R2_V': r_v['R2'],
        'beta_A': r_a['beta'], 'se_A': r_a['se'], 'R2_A': r_a['R2'],
        'beta_P': r_p['beta'], 'se_P': r_p['se'], 'R2_P': r_p['R2'],
    })
    cn_yearly[-1]['sum_1AP'] = 1 + r_a['beta'] + r_p['beta']
    cn_yearly[-1]['econ_signal'] = r_a['beta'] + r_p['beta']

df_cn_yr = pd.DataFrame(cn_yearly)

rpt(f'{"Year":>6} {"n":>5} {"beta_V":>8} {"1+bA+bP":>8} {"beta_A":>8} {"beta_P":>8} {"Econ":>8} {"R2_V":>6}')
rpt('-' * 70)
for _, r in df_cn_yr.iterrows():
    rpt(f'{int(r["year"]):>6} {int(r["n"]):>5} {r["beta_V"]:>8.4f} {r["sum_1AP"]:>8.4f} '
        f'{r["beta_A"]:>8.4f} {r["beta_P"]:>8.4f} {r["econ_signal"]:>8.4f} {r["R2_V"]:>6.3f}')
rpt()

# 全年份均值
rpt('中国逐年均值:')
rpt(f'  mean(beta_V) = {df_cn_yr["beta_V"].mean():.4f} +/- {df_cn_yr["beta_V"].std():.4f}')
rpt(f'  mean(beta_A) = {df_cn_yr["beta_A"].mean():.4f} +/- {df_cn_yr["beta_A"].std():.4f}')
rpt(f'  mean(beta_P) = {df_cn_yr["beta_P"].mean():.4f} +/- {df_cn_yr["beta_P"].std():.4f}')
rpt(f'  mean(econ_signal) = {df_cn_yr["econ_signal"].mean():.4f}')
rpt(f'  mean(1+bA+bP) = {df_cn_yr["sum_1AP"].mean():.4f}  (should ≈ mean beta_V)')
rpt()

# ---- 池化截面回归 (Pooled OLS) ----
rpt('-' * 72)
rpt('PART 1B: 中国 — 池化截面回归 (Pooled OLS with clustered SE by city)')
rpt('-' * 72)

# 需要聚类标准误 — 对 city 聚类
mask_cn = (df_cn['V'] > 0) & (df_cn['Pop'] > 0) & (df_cn['PCA'] > 0) & (df_cn['Price'] > 0)
df_pool = df_cn[mask_cn].copy()
df_pool['lnV'] = np.log(df_pool['V'])
df_pool['lnPop'] = np.log(df_pool['Pop'])
df_pool['lnPCA'] = np.log(df_pool['PCA'])
df_pool['lnPrice'] = np.log(df_pool['Price'])

# 加入年份虚拟变量控制时间趋势
year_dummies = pd.get_dummies(df_pool['year'], prefix='yr', drop_first=True).astype(float)
df_pool = pd.concat([df_pool.reset_index(drop=True), year_dummies.reset_index(drop=True)], axis=1)
yr_cols = [c for c in df_pool.columns if c.startswith('yr_')]

# city codes for clustering
city_codes = pd.Categorical(df_pool['city']).codes

def run_pooled_ols(dep_var, indep_var, label_y, label_x, add_year_fe=True):
    """池化 OLS + 城市聚类标准误 + 年份固定效应"""
    if add_year_fe:
        X = sm.add_constant(df_pool[[indep_var] + yr_cols])
    else:
        X = sm.add_constant(df_pool[[indep_var]])
    y = df_pool[dep_var]
    model = sm.OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': city_codes})
    beta = model.params[indep_var]
    se = model.bse[indep_var]
    ci = model.conf_int().loc[indep_var]
    p_val = model.pvalues[indep_var]
    rpt(f'  ln({label_y}) ~ ln({label_x}) + year FE:')
    rpt(f'    beta = {beta:.4f}  (cluster SE = {se:.4f})')
    rpt(f'    95% CI = [{ci.iloc[0]:.4f}, {ci.iloc[1]:.4f}]')
    rpt(f'    p = {p_val:.2e},  R2 = {model.rsquared:.4f},  n = {len(y)}')
    return {'beta': beta, 'se': se, 'ci_lo': ci.iloc[0], 'ci_hi': ci.iloc[1],
            'p': p_val, 'R2': model.rsquared, 'model': model}

res_V_cn = run_pooled_ols('lnV', 'lnPop', 'V', 'Pop')
res_A_cn = run_pooled_ols('lnPCA', 'lnPop', 'PCA', 'Pop')
res_P_cn = run_pooled_ols('lnPrice', 'lnPop', 'Price', 'Pop')

rpt()
rpt('分解验证 (池化):')
rpt(f'  beta_V = {res_V_cn["beta"]:.4f}')
rpt(f'  1 + beta_A + beta_P = {1 + res_A_cn["beta"] + res_P_cn["beta"]:.4f}')
rpt(f'  经济信号 (beta_A + beta_P) = {res_A_cn["beta"] + res_P_cn["beta"]:.4f}')
rpt(f'  机械成分 (=1) 占 beta_V 比例 = {1/res_V_cn["beta"]*100:.1f}%')
rpt(f'  经济信号占 beta_V 比例 = {(res_A_cn["beta"]+res_P_cn["beta"])/res_V_cn["beta"]*100:.1f}%')
rpt()

# ============================================================
# PART 2: 美国 MSA beta_V 分解
# ============================================================
rpt('=' * 72)
rpt('PART 2: 美国 MSA — beta_V 分解')
rpt('=' * 72)
rpt()

df_us = pd.read_csv(f'{DATA_DIR}/us_msa_muq_panel.csv')
rpt(f'美国数据: {df_us.shape[0]} 行, {df_us["cbsa_code"].nunique()} MSAs, '
    f'{df_us["year"].min()}-{df_us["year"].max()}')

# V = median_home_value * housing_units
# V_per_capita = V / Pop = (median_home_value * housing_units) / Pop
#              = median_home_value * hu_per_capita
# 所以 V = Pop * hu_per_capita * median_home_value
df_us['Pop'] = df_us['population']
df_us['HU_PC'] = df_us['housing_units'] / df_us['population']  # 人均住房套数
df_us['Price'] = df_us['median_home_value']
df_us['V'] = df_us['V_millions']

# 验证: V_millions = median_home_value * housing_units / 1e6
df_us['V_check'] = df_us['median_home_value'] * df_us['housing_units'] / 1e6
identity_err_us = np.abs(df_us['V'] - df_us['V_check']).max()
rpt(f'恒等式验证 max|V - Price*HU| = {identity_err_us:.4f} million USD')
rpt()

# 逐年截面回归
rpt('-' * 72)
rpt('PART 2A: 美国 — 逐年截面回归')
rpt('-' * 72)

us_yearly = []
for yr in sorted(df_us['year'].unique()):
    sub = df_us[df_us['year'] == yr].copy()
    sub = sub[(sub['V'] > 0) & (sub['Pop'] > 0) & (sub['HU_PC'] > 0) & (sub['Price'] > 0)]
    r_v = ols_log_scaling(sub['V'], sub['Pop'], 'V', 'Pop')
    r_a = ols_log_scaling(sub['HU_PC'], sub['Pop'], 'HU_PC', 'Pop')
    r_p = ols_log_scaling(sub['Price'], sub['Pop'], 'Price', 'Pop')
    us_yearly.append({
        'year': yr, 'n': r_v['n'],
        'beta_V': r_v['beta'], 'se_V': r_v['se'], 'R2_V': r_v['R2'],
        'beta_A': r_a['beta'], 'se_A': r_a['se'], 'R2_A': r_a['R2'],
        'beta_P': r_p['beta'], 'se_P': r_p['se'], 'R2_P': r_p['R2'],
    })
    us_yearly[-1]['sum_1AP'] = 1 + r_a['beta'] + r_p['beta']
    us_yearly[-1]['econ_signal'] = r_a['beta'] + r_p['beta']

df_us_yr = pd.DataFrame(us_yearly)

rpt(f'{"Year":>6} {"n":>5} {"beta_V":>8} {"1+bA+bP":>8} {"beta_A":>8} {"beta_P":>8} {"Econ":>8} {"R2_V":>6}')
rpt('-' * 70)
for _, r in df_us_yr.iterrows():
    rpt(f'{int(r["year"]):>6} {int(r["n"]):>5} {r["beta_V"]:>8.4f} {r["sum_1AP"]:>8.4f} '
        f'{r["beta_A"]:>8.4f} {r["beta_P"]:>8.4f} {r["econ_signal"]:>8.4f} {r["R2_V"]:>6.3f}')
rpt()

rpt('美国逐年均值:')
rpt(f'  mean(beta_V) = {df_us_yr["beta_V"].mean():.4f} +/- {df_us_yr["beta_V"].std():.4f}')
rpt(f'  mean(beta_A) = {df_us_yr["beta_A"].mean():.4f} +/- {df_us_yr["beta_A"].std():.4f}')
rpt(f'  mean(beta_P) = {df_us_yr["beta_P"].mean():.4f} +/- {df_us_yr["beta_P"].std():.4f}')
rpt(f'  mean(econ_signal) = {df_us_yr["econ_signal"].mean():.4f}')
rpt()

# 池化回归
rpt('-' * 72)
rpt('PART 2B: 美国 — 池化 OLS + MSA 聚类标准误 + 年份 FE')
rpt('-' * 72)

mask_us = (df_us['V'] > 0) & (df_us['Pop'] > 0) & (df_us['HU_PC'] > 0) & (df_us['Price'] > 0)
df_us_pool = df_us[mask_us].copy()
df_us_pool['lnV'] = np.log(df_us_pool['V'])
df_us_pool['lnPop'] = np.log(df_us_pool['Pop'])
df_us_pool['lnHUPC'] = np.log(df_us_pool['HU_PC'])
df_us_pool['lnPrice'] = np.log(df_us_pool['Price'])

yr_dum_us = pd.get_dummies(df_us_pool['year'], prefix='yr', drop_first=True).astype(float)
df_us_pool = pd.concat([df_us_pool.reset_index(drop=True), yr_dum_us.reset_index(drop=True)], axis=1)
yr_cols_us = [c for c in df_us_pool.columns if c.startswith('yr_')]
msa_codes = pd.Categorical(df_us_pool['cbsa_code']).codes

def run_pooled_us(dep_var, indep_var, label_y, label_x):
    X = sm.add_constant(df_us_pool[[indep_var] + yr_cols_us])
    y = df_us_pool[dep_var]
    model = sm.OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': msa_codes})
    beta = model.params[indep_var]
    se = model.bse[indep_var]
    ci = model.conf_int().loc[indep_var]
    p_val = model.pvalues[indep_var]
    rpt(f'  ln({label_y}) ~ ln({label_x}) + year FE:')
    rpt(f'    beta = {beta:.4f}  (cluster SE = {se:.4f})')
    rpt(f'    95% CI = [{ci.iloc[0]:.4f}, {ci.iloc[1]:.4f}]')
    rpt(f'    p = {p_val:.2e},  R2 = {model.rsquared:.4f},  n = {len(y)}')
    return {'beta': beta, 'se': se, 'ci_lo': ci.iloc[0], 'ci_hi': ci.iloc[1],
            'p': p_val, 'R2': model.rsquared, 'model': model}

res_V_us = run_pooled_us('lnV', 'lnPop', 'V', 'Pop')
res_A_us = run_pooled_us('lnHUPC', 'lnPop', 'HU_PC', 'Pop')
res_P_us = run_pooled_us('lnPrice', 'lnPop', 'Price', 'Pop')

rpt()
rpt('分解验证 (池化):')
rpt(f'  beta_V = {res_V_us["beta"]:.4f}')
rpt(f'  1 + beta_A + beta_P = {1 + res_A_us["beta"] + res_P_us["beta"]:.4f}')
rpt(f'  经济信号 (beta_A + beta_P) = {res_A_us["beta"] + res_P_us["beta"]:.4f}')
rpt(f'  机械成分占 beta_V 比例 = {1/res_V_us["beta"]*100:.1f}%')
rpt(f'  经济信号占 beta_V 比例 = {(res_A_us["beta"]+res_P_us["beta"])/res_V_us["beta"]*100:.1f}%')
rpt()

# ============================================================
# PART 3: Delta-beta 的经济信号含量
# ============================================================
rpt('=' * 72)
rpt('PART 3: Delta-beta 经济信号含量')
rpt('=' * 72)
rpt()

# Delta-beta = beta_V(CN) - beta_V(US)
delta_beta_total = res_V_cn['beta'] - res_V_us['beta']
# 经济信号中的 delta
delta_econ_cn = res_A_cn['beta'] + res_P_cn['beta']
delta_econ_us = res_A_us['beta'] + res_P_us['beta']
delta_beta_econ = delta_econ_cn - delta_econ_us
# 机械成分中的 delta = 1 - 1 = 0 (自动消去)

rpt('Delta-beta 分解:')
rpt(f'  Delta-beta(total) = beta_V(CN) - beta_V(US) = {res_V_cn["beta"]:.4f} - {res_V_us["beta"]:.4f} = {delta_beta_total:.4f}')
rpt(f'  Delta-beta(mechanical) = 1 - 1 = 0  (机械成分在差分中自动消去)')
rpt(f'  Delta-beta(economic) = econ(CN) - econ(US) = {delta_econ_cn:.4f} - {delta_econ_us:.4f} = {delta_beta_econ:.4f}')
rpt()
rpt(f'  关键结论: Delta-beta 100% 为经济信号（机械成分恰好消去）')
rpt()

# 进一步分解: Delta-beta 来自面积差异还是价格差异？
delta_A = res_A_cn['beta'] - res_A_us['beta']
delta_P = res_P_cn['beta'] - res_P_us['beta']
rpt('Delta-beta 经济信号来源分解:')
rpt(f'  Delta(beta_A) = {res_A_cn["beta"]:.4f} - {res_A_us["beta"]:.4f} = {delta_A:.4f}')
rpt(f'  Delta(beta_P) = {res_P_cn["beta"]:.4f} - {res_P_us["beta"]:.4f} = {delta_P:.4f}')
rpt(f'  面积标度贡献 = {delta_A/delta_beta_econ*100:.1f}%')
rpt(f'  价格标度贡献 = {delta_P/delta_beta_econ*100:.1f}%')
rpt()

# ============================================================
# PART 4: SUR (似不相关回归) — 两方程系统估计经济信号的联合标准误
# ============================================================
rpt('=' * 72)
rpt('PART 4: SUR 估计 — 两方程系统 (PCA 和 Price)')
rpt('=' * 72)
rpt()
rpt('注: 由于 ln(V) = ln(Pop) + ln(PCA) + ln(Price) 为恒等式，')
rpt('    V 方程的残差 = PCA 方程残差 + Price 方程残差 (完全线性相关)。')
rpt('    因此只估计两个独立方程 (PCA, Price)，用 SUR 获取联合协方差。')
rpt('    beta_V = 1 + beta_A + beta_P 为确定性恒等式，无需估计。')
rpt()

def run_sur_2eq(df_work, pop_col, pca_col, price_col, label):
    """
    SUR 两方程:
      eq1: ln(PCA) = a1 + beta_A * ln(Pop) + e1
      eq2: ln(Price) = a2 + beta_P * ln(Pop) + e2
    获取 beta_A, beta_P 的联合方差-协方差矩阵，
    由此计算 econ_signal = beta_A + beta_P 的正确标准误。
    """
    mask = (df_work[pop_col] > 0) & (df_work[pca_col] > 0) & (df_work[price_col] > 0)
    d = df_work[mask].copy()

    lnPop = np.log(d[pop_col].values)
    lnPCA = np.log(d[pca_col].values)
    lnPrice = np.log(d[price_col].values)

    n = len(lnPop)
    X_eq = sm.add_constant(lnPop)  # [1, lnPop]
    k = X_eq.shape[1]  # 2

    # Step 1: OLS 每个方程获取残差
    resid = np.zeros((n, 2))
    betas_ols = []
    for j, y_j in enumerate([lnPCA, lnPrice]):
        m = sm.OLS(y_j, X_eq).fit()
        resid[:, j] = m.resid
        betas_ols.append(m.params)

    # Step 2: 估计误差协方差矩阵 Sigma (2x2)
    Sigma = resid.T @ resid / n

    # Step 3: FGLS (Zellner SUR)
    # 注: 当所有方程有相同的 X 时，SUR = OLS (数值上等价)
    # 但 SUR 的价值在于提供 beta_A 和 beta_P 之间的协方差估计
    Sigma_inv = np.linalg.inv(Sigma)

    Y_eqs = [lnPCA, lnPrice]
    XtOiX = np.zeros((2 * k, 2 * k))
    XtOiY = np.zeros(2 * k)

    for i in range(2):
        for j in range(2):
            XtOiX[i*k:(i+1)*k, j*k:(j+1)*k] = Sigma_inv[i, j] * (X_eq.T @ X_eq)
            XtOiY[i*k:(i+1)*k] += Sigma_inv[i, j] * (X_eq.T @ Y_eqs[j])

    V_beta = np.linalg.inv(XtOiX)
    beta_sur = V_beta @ XtOiY

    beta_A_sur = beta_sur[1]
    beta_P_sur = beta_sur[k + 1]

    se_A = np.sqrt(V_beta[1, 1])
    se_P = np.sqrt(V_beta[k+1, k+1])
    cov_AP = V_beta[1, k+1]  # beta_A 和 beta_P 之间的协方差

    # 经济信号 = beta_A + beta_P
    econ_signal = beta_A_sur + beta_P_sur
    # Var(beta_A + beta_P) = Var(A) + Var(P) + 2*Cov(A,P)
    var_econ = V_beta[1,1] + V_beta[k+1,k+1] + 2*cov_AP
    econ_se = np.sqrt(max(var_econ, 0))
    econ_ci_lo = econ_signal - 1.96 * econ_se
    econ_ci_hi = econ_signal + 1.96 * econ_se

    # beta_V = 1 + econ_signal, 其方差与 econ_signal 相同
    beta_V_sur = 1 + econ_signal
    se_V = econ_se  # 因为常数 1 无方差

    # 误差相关系数
    corr_AP = Sigma[0,1] / np.sqrt(Sigma[0,0] * Sigma[1,1])

    rpt(f'  [{label}] SUR 两方程估计 (n = {n}):')
    rpt(f'    beta_A = {beta_A_sur:.4f}  (SE = {se_A:.4f})')
    rpt(f'    beta_P = {beta_P_sur:.4f}  (SE = {se_P:.4f})')
    rpt(f'    Cov(beta_A, beta_P) = {cov_AP:.6f}')
    rpt(f'    Corr(e_A, e_P) = {corr_AP:.4f}')
    rpt(f'    经济信号 (beta_A + beta_P) = {econ_signal:.4f}  (SUR SE = {econ_se:.4f})')
    rpt(f'    95% CI = [{econ_ci_lo:.4f}, {econ_ci_hi:.4f}]')
    rpt(f'    推导 beta_V = 1 + {econ_signal:.4f} = {beta_V_sur:.4f}  (SE = {se_V:.4f})')
    rpt()

    return {
        'beta_A': beta_A_sur, 'se_A': se_A,
        'beta_P': beta_P_sur, 'se_P': se_P,
        'beta_V': beta_V_sur, 'se_V': se_V,
        'econ_signal': econ_signal, 'econ_se': econ_se,
        'cov_AP': cov_AP, 'corr_AP': corr_AP,
        'n': n,
    }


# 中国: 逐年 SUR
rpt('-' * 72)
rpt('PART 4A: 中国 SUR (逐年)')
rpt('-' * 72)

cn_sur_yearly = {}
for yr in sorted(df_cn['year'].unique()):
    sub = df_cn[df_cn['year'] == yr].copy()
    cn_sur_yearly[yr] = run_sur_2eq(sub, 'Pop', 'PCA', 'Price', f'中国 {yr}')

# 美国: 逐年 SUR
rpt('-' * 72)
rpt('PART 4B: 美国 SUR (逐年)')
rpt('-' * 72)

us_sur_yearly = {}
for yr in sorted(df_us['year'].unique()):
    sub = df_us[df_us['year'] == yr].copy()
    us_sur_yearly[yr] = run_sur_2eq(sub, 'Pop', 'HU_PC', 'Price', f'美国 {yr}')

# ============================================================
# PART 5: Delta-beta SUR 标准误
# ============================================================
rpt('=' * 72)
rpt('PART 5: Delta-beta 的正确标准误 (逐年)')
rpt('=' * 72)
rpt()

# 中美独立样本，联合方差 = Var(CN) + Var(US)
common_years = sorted(set(cn_sur_yearly.keys()) & set(us_sur_yearly.keys()))
rpt(f'共同年份: {common_years}')
rpt()
rpt('注: Delta-beta(total) = Delta-beta(econ) 因为机械成分 1-1=0 已消去')
rpt()

rpt(f'{"Year":>6} {"Db_total":>9} {"SE":>8} {"t":>8} {"p":>10} {"DbA":>8} {"DbP":>8}')
rpt('-' * 70)

delta_results = []
for yr in common_years:
    cn = cn_sur_yearly[yr]
    us = us_sur_yearly[yr]

    # Delta-beta_V = Delta_econ (因为 Delta_mechanical = 0)
    db_econ = cn['econ_signal'] - us['econ_signal']
    se_db_econ = np.sqrt(cn['econ_se']**2 + us['econ_se']**2)
    t_val = db_econ / se_db_econ if se_db_econ > 0 else np.nan
    p_val = 2 * (1 - stats.norm.cdf(abs(t_val))) if not np.isnan(t_val) else np.nan

    db_A = cn['beta_A'] - us['beta_A']
    db_P = cn['beta_P'] - us['beta_P']

    rpt(f'{yr:>6} {db_econ:>9.4f} {se_db_econ:>8.4f} {t_val:>8.3f} {p_val:>10.4e} '
        f'{db_A:>8.4f} {db_P:>8.4f}')

    delta_results.append({
        'year': yr, 'db_econ': db_econ, 'se_db_econ': se_db_econ,
        't': t_val, 'p': p_val,
        'db_A': db_A, 'db_P': db_P
    })

df_delta = pd.DataFrame(delta_results)
rpt()

rpt('逐年 Delta-beta 汇总:')
rpt(f'  mean Delta-beta = {df_delta["db_econ"].mean():.4f} +/- {df_delta["db_econ"].std():.4f}')
rpt(f'  mean Delta(beta_A) = {df_delta["db_A"].mean():.4f}')
rpt(f'  mean Delta(beta_P) = {df_delta["db_P"].mean():.4f}')
sig_count = (df_delta['p'] < 0.05).sum()
rpt(f'  显著年份 (p<0.05): {sig_count} / {len(df_delta)}')
rpt()

# ============================================================
# PART 6: Bootstrap 确认
# ============================================================
rpt('=' * 72)
rpt('PART 6: Bootstrap 确认 (2019年截面, 2000次重抽样)')
rpt('=' * 72)
rpt()

# 中国 2019
cn_2019 = df_cn[df_cn['year'] == 2019].copy()
boot_A_cn = bootstrap_beta(cn_2019['PCA'], cn_2019['Pop'])
boot_P_cn = bootstrap_beta(cn_2019['Price'], cn_2019['Pop'])
boot_V_cn = bootstrap_beta(cn_2019['V'], cn_2019['Pop'])
boot_econ_cn = boot_A_cn + boot_P_cn

# 美国 2019
us_2019 = df_us[df_us['year'] == 2019].copy()
boot_A_us = bootstrap_beta(us_2019['HU_PC'], us_2019['Pop'])
boot_P_us = bootstrap_beta(us_2019['Price'], us_2019['Pop'])
boot_V_us = bootstrap_beta(us_2019['V'], us_2019['Pop'])
boot_econ_us = boot_A_us + boot_P_us

# Delta-beta bootstrap (独立样本)
n_boot = min(len(boot_econ_cn), len(boot_econ_us))
boot_delta_econ = boot_econ_cn[:n_boot] - boot_econ_us[:n_boot]
boot_delta_V = boot_V_cn[:n_boot] - boot_V_us[:n_boot]

def boot_summary(arr, label):
    ci = np.percentile(arr, [2.5, 97.5])
    rpt(f'  {label}: mean = {arr.mean():.4f}, median = {np.median(arr):.4f}, '
        f'95% CI = [{ci[0]:.4f}, {ci[1]:.4f}]')

rpt('中国 2019 Bootstrap:')
boot_summary(boot_V_cn, 'beta_V')
boot_summary(boot_A_cn, 'beta_A')
boot_summary(boot_P_cn, 'beta_P')
boot_summary(boot_econ_cn, 'econ_signal')
rpt()

rpt('美国 2019 Bootstrap:')
boot_summary(boot_V_us, 'beta_V')
boot_summary(boot_A_us, 'beta_A (HU_PC)')
boot_summary(boot_P_us, 'beta_P')
boot_summary(boot_econ_us, 'econ_signal')
rpt()

rpt('Delta-beta 2019 Bootstrap:')
boot_summary(boot_delta_V, 'Delta-beta(total)')
boot_summary(boot_delta_econ, 'Delta-beta(econ)')
rpt()

# ============================================================
# PART 7: 总结
# ============================================================
rpt('=' * 72)
rpt('PART 7: 审稿人关切的回应摘要')
rpt('=' * 72)
rpt()

rpt('1. 审稿人关切: beta_V 包含机械成分 (Pop 贡献 beta=1)')
rpt('   回应: 完全正确。V = Pop * PCA * Price, 因此 beta_V = 1 + beta_A + beta_P')
rpt()

rpt('2. 经济信号提取:')
rpt(f'   中国: beta_V = {res_V_cn["beta"]:.4f}, 其中机械成分 = 1.0000, '
    f'经济信号 = {res_A_cn["beta"] + res_P_cn["beta"]:.4f}')
rpt(f'   美国: beta_V = {res_V_us["beta"]:.4f}, 其中机械成分 = 1.0000, '
    f'经济信号 = {res_A_us["beta"] + res_P_us["beta"]:.4f}')
rpt()

rpt('3. Delta-beta 不受机械成分影响:')
rpt(f'   Delta-beta(total) = {delta_beta_total:.4f}')
rpt(f'   Delta-beta(econ)  = {delta_beta_econ:.4f}')
rpt(f'   差异 = {abs(delta_beta_total - delta_beta_econ):.6f} (应 ≈ 0, 因为 1-1=0)')
rpt()

rpt('4. 经济信号的来源:')
rpt(f'   中国 beta_A (人均面积标度) = {res_A_cn["beta"]:.4f}')
rpt(f'   中国 beta_P (价格标度)     = {res_P_cn["beta"]:.4f}')
rpt(f'   美国 beta_A (人均住房标度) = {res_A_us["beta"]:.4f}')
rpt(f'   美国 beta_P (价格标度)     = {res_P_us["beta"]:.4f}')
rpt()

rpt('5. 经济学解释:')
rpt('   beta_A > 0: 大城市人均住房面积/套数更多 (住房供给规模效应)')
rpt('   beta_A < 0: 大城市人均住房面积/套数更少 (拥挤效应)')
rpt('   beta_P > 0: 大城市房价更高 (聚集溢价 / agglomeration premium)')
rpt('   中美差异主要来自哪个成分，反映了不同的城市化模式')
rpt()

# ============================================================
# 保存报告
# ============================================================
with open(REPORT_OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
    f.write('\n')

rpt()
rpt(f'报告已保存至: {REPORT_OUT}')
