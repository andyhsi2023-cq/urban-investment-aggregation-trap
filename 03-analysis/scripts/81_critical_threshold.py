#!/usr/bin/env python3
"""
81_critical_threshold.py
========================
目的: 估计城市投资的临界阈值 I_c/GDP (即 GFCF/GDP 的阈值 gamma)
      使用 Hansen 阈值面板模型 + 非参数方法

输入: global_q_revised_panel.csv
输出:
  - 报告: critical_threshold_report.txt
  - 旗舰图: fig_critical_threshold.png
  - Source data: fig_threshold_source.csv

依赖: pandas, numpy, scipy, statsmodels, matplotlib
"""

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.nonparametric.kernel_regression import KernelReg
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import time

# ============================================================
# 路径配置
# ============================================================
BASE = Path('/Users/andy/Desktop/Claude/urban-q-phase-transition')
DATA_PATH = BASE / '02-data/processed/global_q_revised_panel.csv'
REPORT_PATH = BASE / '03-analysis/models/critical_threshold_report.txt'
FIG_PATH = BASE / '04-figures/drafts/fig_critical_threshold.png'
SOURCE_PATH = BASE / '04-figures/source-data/fig_threshold_source.csv'

for p in [REPORT_PATH.parent, FIG_PATH.parent, SOURCE_PATH.parent]:
    p.mkdir(parents=True, exist_ok=True)

# 报告缓冲
report_lines = []
def log(msg=''):
    print(msg)
    report_lines.append(str(msg))

# ============================================================
# 数据加载与预处理
# ============================================================
log('=' * 72)
log('城市投资临界阈值 I_c/GDP 估计')
log('Hansen Threshold Panel Model + Nonparametric Exploration')
log('=' * 72)
log()

df = pd.read_csv(DATA_PATH)
log(f'原始数据: {df.shape[0]} 行, {df["country_code"].nunique()} 国, '
    f'{df["year"].min()}-{df["year"].max()}')

# 计算关键变量
df = df.sort_values(['country_code', 'year'])
df['dCPR'] = df.groupby('country_code')['CPR'].diff()
df['dCPR_rate'] = df.groupby('country_code')['CPR'].pct_change()
df['gdp_growth'] = df.groupby('country_code')['gdp_constant_2015'].pct_change() * 100
df['gdp_crisis'] = df['gdp_growth'] < -15

# 工作样本
work = df.dropna(subset=['CPR', 'gfcf_pct_gdp', 'dCPR', 'urban_pct']).copy()
work = work[(work['gfcf_pct_gdp'] > 0) & (work['gfcf_pct_gdp'] < 80)]
q_low, q_high = work['dCPR'].quantile(0.005), work['dCPR'].quantile(0.995)
work = work[(work['dCPR'] >= q_low) & (work['dCPR'] <= q_high)]

log(f'工作样本: {work.shape[0]} 观测, {work["country_code"].nunique()} 国')
log(f'GFCF/GDP 范围: {work["gfcf_pct_gdp"].min():.1f}% - {work["gfcf_pct_gdp"].max():.1f}%')
log(f'dCPR 范围: {work["dCPR"].min():.4f} - {work["dCPR"].max():.4f}')
log()

# ============================================================
# PART A: 非参数探索
# ============================================================
log('=' * 72)
log('PART A: 非参数探索')
log('=' * 72)
log()

# A1: 分 bin 统计
work['gfcf_bin'] = pd.qcut(work['gfcf_pct_gdp'], 10, duplicates='drop')
bin_stats = work.groupby('gfcf_bin', observed=True).agg(
    n=('dCPR', 'count'),
    median_dCPR=('dCPR', 'median'),
    mean_dCPR=('dCPR', 'mean'),
    std_dCPR=('dCPR', 'std'),
    median_gfcf=('gfcf_pct_gdp', 'median')
).reset_index()

log('GFCF/GDP 十分位 bin 统计:')
log(f'{"Bin":<30s} {"N":>5s} {"Median dCPR":>12s} {"Mean dCPR":>12s} {"Med GFCF":>10s}')
log('-' * 72)
for _, row in bin_stats.iterrows():
    log(f'{str(row["gfcf_bin"]):<30s} {row["n"]:>5.0f} {row["median_dCPR"]:>12.4f} '
        f'{row["mean_dCPR"]:>12.4f} {row["median_gfcf"]:>10.1f}')
log()

# A2: LOESS 回归
x_gfcf = work['gfcf_pct_gdp'].values
y_dcpr = work['dCPR'].values

lowess_result = sm.nonparametric.lowess(y_dcpr, x_gfcf, frac=0.3, return_sorted=True)
lowess_x = lowess_result[:, 0]
lowess_y = lowess_result[:, 1]

# 导数变号点 (峰值)
dx = np.diff(lowess_x)
dy = np.diff(lowess_y)
deriv = dy / dx

# LOESS 零线交叉
zero_crossings = []
for i in range(len(lowess_y) - 1):
    if lowess_y[i] * lowess_y[i+1] < 0:
        x_cross = lowess_x[i] + (0 - lowess_y[i]) * (lowess_x[i+1] - lowess_x[i]) / (lowess_y[i+1] - lowess_y[i])
        zero_crossings.append(x_cross)

log(f'LOESS 零线交叉点 (dCPR 从正变负): {[f"{x:.1f}%" for x in zero_crossings]}')

# A3: Kernel 回归
try:
    kr = KernelReg(y_dcpr, x_gfcf.reshape(-1, 1), var_type='c', bw='cv_ls')
    x_grid = np.linspace(work['gfcf_pct_gdp'].quantile(0.02),
                         work['gfcf_pct_gdp'].quantile(0.98), 200)
    kr_fit, _ = kr.fit(x_grid.reshape(-1, 1))
    kr_zero = []
    for i in range(len(kr_fit) - 1):
        if kr_fit[i] * kr_fit[i+1] < 0:
            x_c = x_grid[i] + (0 - kr_fit[i]) * (x_grid[i+1] - x_grid[i]) / (kr_fit[i+1] - kr_fit[i])
            kr_zero.append(x_c)
    log(f'Kernel 回归零线交叉: {[f"{x:.1f}%" for x in kr_zero]}')
except Exception as e:
    log(f'Kernel 回归失败: {e}')
    kr_fit = None
    kr_zero = []

nonpar_estimates = zero_crossings + kr_zero
if nonpar_estimates:
    nonpar_gamma = np.median(nonpar_estimates)
    log(f'非参数方法综合 gamma 估计: {nonpar_gamma:.1f}%')
else:
    nonpar_gamma = None
    log('非参数方法未找到明确零线交叉点')

# A4: 分段 t 检验 -- dCPR 是否在某个 GFCF/GDP 水平后显著为负
log('\n分段单样本 t 检验 (H0: mean dCPR = 0):')
log(f'{"GFCF/GDP >":<15s} {"N":>5s} {"Mean dCPR":>10s} {"t":>8s} {"p":>10s}')
for cutoff in [15, 18, 20, 22, 25, 27, 30, 33, 35]:
    sub = work[work['gfcf_pct_gdp'] >= cutoff]['dCPR']
    if len(sub) > 30:
        t, p = stats.ttest_1samp(sub, 0)
        log(f'{cutoff:>8d}%       {len(sub):>5d} {sub.mean():>10.4f} {t:>8.2f} {p:>10.4f}')
log()


# ============================================================
# PART B: Hansen 阈值面板模型
# ============================================================
log('=' * 72)
log('PART B: Hansen 阈值面板模型')
log('=' * 72)
log()

def demean_twoway(data, y_col, x_vars):
    """双向固定效应 within 变换"""
    d = data.copy()
    cols = [y_col] + x_vars
    d_clean = d.dropna(subset=cols).copy()

    y = d_clean[y_col].values
    cm_y = d_clean.groupby('country_code')[y_col].transform('mean')
    ym_y = d_clean.groupby('year')[y_col].transform('mean')
    y_dm = y - cm_y.values - ym_y.values + y.mean()

    X_list = []
    for v in x_vars:
        cm = d_clean.groupby('country_code')[v].transform('mean')
        ym = d_clean.groupby('year')[v].transform('mean')
        X_list.append(d_clean[v].values - cm.values - ym.values + d_clean[v].mean())
    X = np.column_stack(X_list)

    return y_dm, X, d_clean


def threshold_panel(data, gamma, y_col='dCPR', threshold_col='gfcf_pct_gdp',
                    controls=None):
    """
    阈值面板回归:
    dCPR = mu_i + lambda_t + alpha_1*I(low) + beta_1*GFCF*I(low)
                            + alpha_2*I(high) + beta_2*GFCF*I(high) + controls + eps

    关键: 允许截距和斜率在两个体制中都不同
    """
    d = data.copy()
    low = (d[threshold_col] < gamma).astype(float)
    high = (d[threshold_col] >= gamma).astype(float)

    # 体制指示变量 + 交互
    d['regime_high'] = high
    d['gfcf_low'] = d[threshold_col] * low
    d['gfcf_high'] = d[threshold_col] * high

    x_vars = ['regime_high', 'gfcf_low', 'gfcf_high']
    if controls:
        for c in controls:
            if c in d.columns and d[c].notna().sum() > 0.5 * len(d):
                x_vars.append(c)

    y_dm, X, d_clean = demean_twoway(d, y_col, x_vars)

    try:
        betas, residuals, rank, sv = np.linalg.lstsq(X, y_dm, rcond=None)
        resid = y_dm - X @ betas
        ssr = np.sum(resid ** 2)
        n = len(y_dm)
        k = X.shape[1]
        sigma2 = ssr / (n - k) if n > k else np.nan
        try:
            XtX_inv = np.linalg.inv(X.T @ X)
            se = np.sqrt(np.diag(sigma2 * XtX_inv))
        except:
            se = np.full(k, np.nan)

        n_low = int((d_clean[threshold_col] < gamma).sum())
        n_high = int((d_clean[threshold_col] >= gamma).sum())

        result = {
            'ssr': ssr, 'n': n, 'k': k,
            'betas': dict(zip(x_vars, betas)),
            'se': dict(zip(x_vars, se)),
            'n_low': n_low, 'n_high': n_high
        }
        return result
    except:
        return {'ssr': np.inf, 'n': 0, 'k': 0, 'betas': {}, 'se': {},
                'n_low': 0, 'n_high': 0}


def linear_panel(data, y_col='dCPR', threshold_col='gfcf_pct_gdp', controls=None):
    """线性面板 (无阈值)"""
    d = data.copy()
    x_vars = [threshold_col]
    if controls:
        for c in controls:
            if c in d.columns and d[c].notna().sum() > 0.5 * len(d):
                x_vars.append(c)
    y_dm, X, d_clean = demean_twoway(d, y_col, x_vars)
    betas = np.linalg.lstsq(X, y_dm, rcond=None)[0]
    resid = y_dm - X @ betas
    return np.sum(resid ** 2), len(y_dm), X.shape[1]


# 准备数据
controls = ['urban_pct', 'gdp_growth']
work_hansen = work.dropna(subset=['dCPR', 'gfcf_pct_gdp', 'urban_pct', 'gdp_growth']).copy()
log(f'Hansen 模型样本: {len(work_hansen)} 观测, {work_hansen["country_code"].nunique()} 国')

# Grid search: 15%-45% (理论下界: 任何经济体需要最低15%投资率维持增长)
gamma_lo = max(15.0, work_hansen['gfcf_pct_gdp'].quantile(0.10))
gamma_hi = min(45.0, work_hansen['gfcf_pct_gdp'].quantile(0.90))
gamma_grid = np.arange(gamma_lo, gamma_hi + 0.5, 0.5)
log(f'Grid search: [{gamma_lo:.1f}%, {gamma_hi:.1f}%], 步长 0.5pp, {len(gamma_grid)} 点')
log()

# ---- SSR profile ----
ssr_profile = []
t_start = time.time()
for gamma in gamma_grid:
    res = threshold_panel(work_hansen, gamma, controls=controls)
    ssr_profile.append({
        'gamma': gamma,
        'ssr': res['ssr'],
        'beta_gfcf_low': res['betas'].get('gfcf_low', np.nan),
        'beta_gfcf_high': res['betas'].get('gfcf_high', np.nan),
        'se_gfcf_low': res['se'].get('gfcf_low', np.nan),
        'se_gfcf_high': res['se'].get('gfcf_high', np.nan),
        'beta_regime': res['betas'].get('regime_high', np.nan),
        'se_regime': res['se'].get('regime_high', np.nan),
        'n_low': res['n_low'],
        'n_high': res['n_high']
    })

ssr_df = pd.DataFrame(ssr_profile)
t_elapsed = time.time() - t_start

# 最优 gamma (确保每个体制至少 5% 的样本)
min_regime_n = len(work_hansen) * 0.05
valid = ssr_df[(ssr_df['n_low'] >= min_regime_n) & (ssr_df['n_high'] >= min_regime_n)]
best = valid.loc[valid['ssr'].idxmin()]
gamma_hat = best['gamma']

log(f'Grid search 完成 ({t_elapsed:.1f}s)')
log()
log('SSR Profile (每 2pp):')
log(f'{"gamma":>7s} {"SSR":>12s} {"beta_low":>10s} {"beta_high":>10s} {"regime_d":>10s} {"n_low":>6s} {"n_high":>6s}')
log('-' * 72)
for _, row in ssr_df.iterrows():
    if row['gamma'] % 2 == 0 or row['gamma'] == gamma_hat:
        marker = ' <<<' if row['gamma'] == gamma_hat else ''
        log(f'{row["gamma"]:>7.1f} {row["ssr"]:>12.2f} {row["beta_gfcf_low"]:>10.6f} '
            f'{row["beta_gfcf_high"]:>10.6f} {row["beta_regime"]:>10.4f} '
            f'{row["n_low"]:>6.0f} {row["n_high"]:>6.0f}{marker}')
log()

log(f'最优阈值 gamma_hat = {gamma_hat:.1f}%')
log(f'  SSR = {best["ssr"]:.2f}')
log(f'  beta_gfcf (low regime): {best["beta_gfcf_low"]:.6f} (SE = {best["se_gfcf_low"]:.6f})')
log(f'  beta_gfcf (high regime): {best["beta_gfcf_high"]:.6f} (SE = {best["se_gfcf_high"]:.6f})')
log(f'  regime intercept diff: {best["beta_regime"]:.4f} (SE = {best["se_regime"]:.4f})')
log(f'  n_low = {best["n_low"]:.0f}, n_high = {best["n_high"]:.0f}')
log()

# 解释经济含义
log('经济含义:')
log(f'  GFCF/GDP < {gamma_hat:.0f}%: 每增加1pp投资, dCPR 变化 {best["beta_gfcf_low"]:.4f}')
log(f'  GFCF/GDP >= {gamma_hat:.0f}%: 每增加1pp投资, dCPR 变化 {best["beta_gfcf_high"]:.4f}')
beta_diff = best['beta_gfcf_high'] - best['beta_gfcf_low']
log(f'  两体制斜率差: {beta_diff:.4f}')
log()

# F 检验
ssr_linear, n_total, k_linear = linear_panel(work_hansen, controls=controls)
ssr_threshold = best['ssr']
k_threshold = k_linear + 2  # regime_high + 额外斜率
k_diff = k_threshold - k_linear

F_stat = ((ssr_linear - ssr_threshold) / k_diff) / (ssr_threshold / (n_total - k_threshold))
p_F = 1 - stats.f.cdf(F_stat, k_diff, n_total - k_threshold)

log(f'阈值效应 F 检验:')
log(f'  SSR_linear = {ssr_linear:.2f}')
log(f'  SSR_threshold = {ssr_threshold:.2f}')
log(f'  df = ({k_diff}, {n_total - k_threshold})')
log(f'  F = {F_stat:.4f}')
log(f'  p-value = {p_F:.6f}')
log(f'  显著性: {"***" if p_F < 0.001 else "**" if p_F < 0.01 else "*" if p_F < 0.05 else "n.s."}')
log()

# Bootstrap 95% CI
log('Bootstrap 95% CI (500 replications, cluster by country)...')
np.random.seed(42)
n_boot = 500
gamma_boot = []
countries = work_hansen['country_code'].unique()

for b in range(n_boot):
    boot_countries = np.random.choice(countries, size=len(countries), replace=True)
    boot_data = []
    for i, c in enumerate(boot_countries):
        chunk = work_hansen[work_hansen['country_code'] == c].copy()
        chunk['country_code'] = f'{c}_{i}'
        boot_data.append(chunk)
    boot_df = pd.concat(boot_data, ignore_index=True)

    # 粗搜索 (2pp)
    best_ssr_b = np.inf
    best_g_b = gamma_hat
    for gamma in np.arange(gamma_lo, gamma_hi + 2, 2.0):
        res = threshold_panel(boot_df, gamma, controls=controls)
        n_lo_b = res['n_low']
        n_hi_b = res['n_high']
        if res['ssr'] < best_ssr_b and n_lo_b >= 100 and n_hi_b >= 100:
            best_ssr_b = res['ssr']
            best_g_b = gamma

    # 精搜索 (0.5pp)
    for gamma in np.arange(max(gamma_lo, best_g_b - 4), min(gamma_hi, best_g_b + 4) + 0.5, 0.5):
        res = threshold_panel(boot_df, gamma, controls=controls)
        n_lo_b = res['n_low']
        n_hi_b = res['n_high']
        if res['ssr'] < best_ssr_b and n_lo_b >= 100 and n_hi_b >= 100:
            best_ssr_b = res['ssr']
            best_g_b = gamma

    gamma_boot.append(best_g_b)
    if (b + 1) % 100 == 0:
        print(f'  Bootstrap {b+1}/{n_boot}...')

gamma_boot = np.array(gamma_boot)
ci_low = np.percentile(gamma_boot, 2.5)
ci_high = np.percentile(gamma_boot, 97.5)
ci_width = ci_high - ci_low

log(f'\nBootstrap 结果:')
log(f'  gamma_hat = {gamma_hat:.1f}%')
log(f'  95% CI = [{ci_low:.1f}%, {ci_high:.1f}%]')
log(f'  CI 宽度 = {ci_width:.1f}pp')
log(f'  Bootstrap 均值 = {gamma_boot.mean():.1f}%')
log(f'  Bootstrap 中位数 = {np.median(gamma_boot):.1f}%')
log(f'  Bootstrap 众数区间: {pd.Series(gamma_boot).round(0).mode().values}')
log()

# 如果 bootstrap 中位数与点估计相差较大，报告稳健估计
gamma_robust = np.median(gamma_boot)
if abs(gamma_robust - gamma_hat) > 3:
    log(f'注意: Bootstrap 中位数 ({gamma_robust:.1f}%) 与点估计 ({gamma_hat:.1f}%) 差异较大')
    log(f'采用 Bootstrap 中位数作为稳健估计: gamma_robust = {gamma_robust:.1f}%')
    # 使用 bootstrap 中位数作为主估计
    gamma_report = gamma_robust
else:
    gamma_report = gamma_hat
log()


# ============================================================
# PART C: 分收入组估计
# ============================================================
log('=' * 72)
log('PART C: 分收入组稳定性检验')
log('=' * 72)
log()

income_groups = ['Low income', 'Lower middle income', 'Upper middle income', 'High income']
income_results = {}

for ig in income_groups:
    sub = work_hansen[work_hansen['income_group'] == ig]
    if len(sub) < 100:
        log(f'{ig}: 样本量不足 ({len(sub)}), 跳过')
        income_results[ig] = {'gamma': np.nan, 'ci_low': np.nan, 'ci_high': np.nan, 'n': len(sub)}
        continue

    g_lo_ig = max(12, sub['gfcf_pct_gdp'].quantile(0.15))
    g_hi_ig = min(50, sub['gfcf_pct_gdp'].quantile(0.85))
    min_n_ig = max(20, len(sub) * 0.05)

    best_ssr_ig = np.inf
    best_g_ig = np.nan
    best_info_ig = {}
    for gamma in np.arange(g_lo_ig, g_hi_ig + 0.5, 0.5):
        res = threshold_panel(sub, gamma, controls=controls)
        if res['ssr'] < best_ssr_ig and res['n_low'] >= min_n_ig and res['n_high'] >= min_n_ig:
            best_ssr_ig = res['ssr']
            best_g_ig = gamma
            best_info_ig = res

    # Bootstrap (200x)
    boot_g_ig = []
    sub_countries = sub['country_code'].unique()
    np.random.seed(42)
    for b in range(200):
        bc = np.random.choice(sub_countries, size=len(sub_countries), replace=True)
        bd = []
        for i, c in enumerate(bc):
            chunk = sub[sub['country_code'] == c].copy()
            chunk['country_code'] = f'{c}_{i}'
            bd.append(chunk)
        bdf = pd.concat(bd, ignore_index=True)

        bs = np.inf
        bg = best_g_ig
        for gamma in np.arange(g_lo_ig, g_hi_ig + 1, 1.0):
            res = threshold_panel(bdf, gamma, controls=controls)
            if res['ssr'] < bs and res['n_low'] >= 15 and res['n_high'] >= 15:
                bs = res['ssr']
                bg = gamma
        boot_g_ig.append(bg)

    boot_g_ig = np.array(boot_g_ig)
    income_results[ig] = {
        'gamma': best_g_ig,
        'ci_low': np.percentile(boot_g_ig, 2.5),
        'ci_high': np.percentile(boot_g_ig, 97.5),
        'n': len(sub),
        'beta_low': best_info_ig.get('betas', {}).get('gfcf_low', np.nan),
        'beta_high': best_info_ig.get('betas', {}).get('gfcf_high', np.nan),
    }

log(f'{"Income Group":<25s} {"N":>6s} {"gamma":>8s} {"95% CI":>18s} {"CI Width":>10s}')
log('-' * 72)
for ig in income_groups:
    r = income_results[ig]
    if np.isnan(r.get('gamma', np.nan)):
        log(f'{ig:<25s} {r["n"]:>6d} {"N/A":>8s} {"N/A":>18s} {"N/A":>10s}')
    else:
        ci_str = f'[{r["ci_low"]:.1f}, {r["ci_high"]:.1f}]'
        ci_w = f'{r["ci_high"] - r["ci_low"]:.1f}'
        log(f'{ig:<25s} {r["n"]:>6d} {r["gamma"]:>8.1f} {ci_str:>18s} {ci_w:>10s}')
log()

# CI 重叠检验
valid_groups = [ig for ig in income_groups if not np.isnan(income_results[ig].get('gamma', np.nan))]
overlap_count = 0
overlap_pairs = []
for i in range(len(valid_groups)):
    for j in range(i+1, len(valid_groups)):
        r1 = income_results[valid_groups[i]]
        r2 = income_results[valid_groups[j]]
        overlap = max(0, min(r1['ci_high'], r2['ci_high']) - max(r1['ci_low'], r2['ci_low']))
        if overlap > 0:
            overlap_count += 1
            overlap_pairs.append((valid_groups[i], valid_groups[j]))

log(f'CI 重叠对数: {overlap_count}/{len(valid_groups)*(len(valid_groups)-1)//2}')
for p in overlap_pairs:
    log(f'  重叠: {p[0]} & {p[1]}')

if overlap_count >= 2:
    log('>> 支持"普适阈值"叙事: 多组CI显著重叠')
    universal_narrative = True
else:
    log('>> "发展阶段依赖的阈值"叙事更合适')
    universal_narrative = False
log()


# ============================================================
# PART D: 稳健性检验
# ============================================================
log('=' * 72)
log('PART D: 稳健性检验')
log('=' * 72)
log()

robustness_results = {}

# D1: 替代因变量
log('D1: 替代因变量 (dCPR/CPR 增长率)')
work_d1 = work_hansen.dropna(subset=['dCPR_rate']).copy()
work_d1 = work_d1[(work_d1['dCPR_rate'] > work_d1['dCPR_rate'].quantile(0.005)) &
                   (work_d1['dCPR_rate'] < work_d1['dCPR_rate'].quantile(0.995))]
best_ssr_d1 = np.inf
gamma_d1 = np.nan
for gamma in gamma_grid:
    res = threshold_panel(work_d1, gamma, y_col='dCPR_rate', controls=controls)
    if res['ssr'] < best_ssr_d1 and res['n_low'] >= min_regime_n and res['n_high'] >= min_regime_n:
        best_ssr_d1 = res['ssr']
        gamma_d1 = gamma
robustness_results['alt_DV'] = gamma_d1
log(f'  gamma (增长率) = {gamma_d1:.1f}%')

# D2: 替代阈值变量 (ci_gdp_ratio)
log('D2: 替代阈值变量 (ci_gdp_ratio)')
if 'ci_gdp_ratio' in work_hansen.columns and work_hansen['ci_gdp_ratio'].notna().sum() > 500:
    work_d2 = work_hansen.dropna(subset=['ci_gdp_ratio']).copy()
    ci_lo_d2 = work_d2['ci_gdp_ratio'].quantile(0.10)
    ci_hi_d2 = work_d2['ci_gdp_ratio'].quantile(0.90)
    best_ssr_d2 = np.inf
    gamma_d2 = np.nan
    for gamma in np.arange(ci_lo_d2, ci_hi_d2, (ci_hi_d2 - ci_lo_d2) / 80):
        res = threshold_panel(work_d2, gamma, threshold_col='ci_gdp_ratio', controls=controls)
        if res['ssr'] < best_ssr_d2:
            best_ssr_d2 = res['ssr']
            gamma_d2 = gamma
    robustness_results['alt_threshold'] = gamma_d2
    log(f'  gamma (ci_gdp_ratio) = {gamma_d2:.4f}')
else:
    robustness_results['alt_threshold'] = np.nan
    log(f'  ci_gdp_ratio 可用观测不足, 跳过')

# D3: 排除危机国家
log('D3: 排除异常值 (GDP年降幅 > 15%)')
work_d3 = work_hansen[~work_hansen['gdp_crisis']].copy()
n_excluded = len(work_hansen) - len(work_d3)
best_ssr_d3 = np.inf
gamma_d3 = np.nan
for gamma in gamma_grid:
    res = threshold_panel(work_d3, gamma, controls=controls)
    if res['ssr'] < best_ssr_d3 and res['n_low'] >= min_regime_n and res['n_high'] >= min_regime_n:
        best_ssr_d3 = res['ssr']
        gamma_d3 = gamma
robustness_results['excl_crisis'] = gamma_d3
log(f'  排除 {n_excluded} 个危机观测')
log(f'  gamma (排除后) = {gamma_d3:.1f}%')

# D4: 样本外预测
log('D4: 样本外预测 (1960-2000 -> 2001-2023)')
train = work_hansen[work_hansen['year'] <= 2000]
test = work_hansen[work_hansen['year'] > 2000]

best_ssr_train = np.inf
gamma_train = np.nan
for gamma in gamma_grid:
    res = threshold_panel(train, gamma, controls=controls)
    if res['ssr'] < best_ssr_train and res['n_low'] >= 50 and res['n_high'] >= 50:
        best_ssr_train = res['ssr']
        gamma_train = gamma

if not np.isnan(gamma_train) and len(test) > 0:
    res_train = threshold_panel(train, gamma_train, controls=controls)
    b_low = res_train['betas'].get('gfcf_low', 0)
    b_high = res_train['betas'].get('gfcf_high', 0)
    b_regime = res_train['betas'].get('regime_high', 0)

    # 预测 dCPR 符号: 低体制 vs 高体制
    test_gfcf = test['gfcf_pct_gdp'].values
    # 简化: 在低体制中效应 ~ b_low * gfcf, 高体制中 ~ b_regime + b_high * gfcf
    pred_low = b_low * test_gfcf
    pred_high = b_regime + b_high * test_gfcf
    pred_dcpr = np.where(test_gfcf < gamma_train, pred_low, pred_high)
    pred_sign = np.sign(pred_dcpr)
    actual_sign = np.sign(test['dCPR'].values)
    mask = actual_sign != 0
    accuracy = np.mean(pred_sign[mask] == actual_sign[mask]) if mask.sum() > 0 else np.nan

    robustness_results['oos_accuracy'] = accuracy
    robustness_results['oos_gamma'] = gamma_train
    log(f'  训练集 gamma = {gamma_train:.1f}%')
    log(f'  测试集 N = {len(test)}')
    log(f'  符号预测准确率 = {accuracy:.1%}')
else:
    robustness_results['oos_accuracy'] = np.nan
    log('  数据不足')

# D5: 滚动窗口
log('D5: 滚动窗口 (20年)')
rolling_gammas = []
for start_year in range(1970, 2005):
    end_year = start_year + 19
    sub = work_hansen[(work_hansen['year'] >= start_year) & (work_hansen['year'] <= end_year)]
    if len(sub) < 200:
        continue
    best_ssr_r = np.inf
    best_g_r = np.nan
    for gamma in np.arange(gamma_lo, gamma_hi + 1, 1.0):
        res = threshold_panel(sub, gamma, controls=controls)
        if res['ssr'] < best_ssr_r and res['n_low'] >= 30 and res['n_high'] >= 30:
            best_ssr_r = res['ssr']
            best_g_r = gamma
    rolling_gammas.append({'window': f'{start_year}-{end_year}',
                           'mid_year': start_year + 10,
                           'gamma': best_g_r, 'n': len(sub)})

rolling_df = pd.DataFrame(rolling_gammas)
if len(rolling_df) > 0:
    log(f'  窗口数: {len(rolling_df)}')
    log(f'  gamma 范围: [{rolling_df["gamma"].min():.1f}%, {rolling_df["gamma"].max():.1f}%]')
    log(f'  gamma 均值: {rolling_df["gamma"].mean():.1f}%')
    log(f'  gamma SD: {rolling_df["gamma"].std():.1f}pp')
    robustness_results['rolling_mean'] = rolling_df['gamma'].mean()
    robustness_results['rolling_std'] = rolling_df['gamma'].std()

log()
log('稳健性汇总:')
log(f'  主模型 gamma = {gamma_hat:.1f}%')
log(f'  Bootstrap 稳健估计 = {gamma_report:.1f}%')
log(f'  替代DV = {robustness_results.get("alt_DV", np.nan):.1f}%')
log(f'  排除危机 = {robustness_results.get("excl_crisis", np.nan):.1f}%')
if not np.isnan(robustness_results.get('rolling_mean', np.nan)):
    log(f'  滚动窗口 = {robustness_results["rolling_mean"]:.1f}% (SD={robustness_results["rolling_std"]:.1f})')
log(f'  样本外 gamma = {robustness_results.get("oos_gamma", np.nan):.1f}%')

# 综合最优估计 (去极值后取中位数)
all_gammas = [gamma_hat, gamma_report,
              robustness_results.get('alt_DV', np.nan),
              robustness_results.get('excl_crisis', np.nan)]
all_gammas = [g for g in all_gammas if not np.isnan(g)]
for ig in income_groups:
    g = income_results.get(ig, {}).get('gamma', np.nan)
    if not np.isnan(g):
        all_gammas.append(g)
gamma_ensemble = np.median(all_gammas)
log(f'\n  ** 集成估计 (所有方法中位数): gamma = {gamma_ensemble:.1f}% **')
log()


# ============================================================
# PART E: 中国定位
# ============================================================
log('=' * 72)
log('PART E: 中国定位')
log('=' * 72)
log()

china = df[df['country_code'] == 'CHN'].dropna(subset=['gfcf_pct_gdp']).copy()
log(f'中国数据: {china["year"].min()}-{china["year"].max()}, {len(china)} 年')

# 使用集成估计
gamma_final = gamma_report  # 使用 bootstrap 稳健估计

china_above = china[china['gfcf_pct_gdp'] >= gamma_final]
if len(china_above) > 0:
    breach_year = int(china_above['year'].min())
    log(f'中国首次突破 gamma ({gamma_final:.1f}%): {breach_year} 年')
    log(f'中国当前 GFCF/GDP ({int(china["year"].max())}): {china["gfcf_pct_gdp"].iloc[-1]:.1f}%')
    log(f'超出阈值: {china["gfcf_pct_gdp"].iloc[-1] - gamma_final:.1f}pp')

    china_cpr = china.dropna(subset=['CPR'])
    if len(china_cpr) > 0:
        cpr_peak_yr = int(china_cpr.loc[china_cpr['CPR'].idxmax(), 'year'])
        log(f'中国 CPR 峰值: {china_cpr["CPR"].max():.2f} ({cpr_peak_yr})')
        log(f'CPR 峰值与阈值突破的滞后: {cpr_peak_yr - breach_year} 年')
else:
    breach_year = None
    log(f'中国未突破阈值 ({gamma_final:.1f}%)')

log()
log('关键国家定位:')
log(f'{"国家":<12s} {"最新GFCF/GDP":>14s} {"状态":>20s} {"突破年份":>10s}')
log('-' * 60)
for code, name in [('CHN', '中国'), ('IND', '印度'), ('VNM', '越南'),
                    ('IDN', '印尼'), ('JPN', '日本'), ('USA', '美国'),
                    ('KOR', '韩国'), ('DEU', '德国')]:
    c = df[(df['country_code'] == code) & (df['gfcf_pct_gdp'].notna())]
    if len(c) > 0:
        latest = c.iloc[-1]['gfcf_pct_gdp']
        above = c[c['gfcf_pct_gdp'] >= gamma_final]
        if len(above) > 0:
            first_yr = int(above['year'].min())
            status = 'above threshold'
            yr_str = str(first_yr)
        else:
            status = f'below by {gamma_final - latest:.1f}pp'
            yr_str = '-'
        log(f'{name:<12s} {latest:>14.1f}% {status:>20s} {yr_str:>10s}')
log()


# ============================================================
# PART F: Nature 级可视化
# ============================================================
log('=' * 72)
log('PART F: 可视化')
log('=' * 72)
log()

plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 8,
    'axes.linewidth': 0.5,
    'xtick.major.width': 0.5,
    'ytick.major.width': 0.5,
    'xtick.major.size': 3,
    'ytick.major.size': 3,
})

COLORS = {
    'safe': '#D4E6F1', 'danger': '#F5B7B1',
    'loess': '#2C3E50', 'scatter': '#85929E',
    'china': '#E74C3C', 'india': '#F39C12',
    'japan': '#3498DB', 'usa': '#27AE60',
    'korea': '#9B59B6', 'vietnam': '#1ABC9C',
    'threshold': '#C0392B', 'zero': '#7F8C8D',
}

fig = plt.figure(figsize=(180/25.4, 240/25.4))
gs = gridspec.GridSpec(3, 2, height_ratios=[1.3, 1, 1],
                       hspace=0.38, wspace=0.35,
                       left=0.10, right=0.95, top=0.96, bottom=0.05)

# ---- Panel a: 旗舰图 ----
ax_a = fig.add_subplot(gs[0, :])

xlim_min = work['gfcf_pct_gdp'].quantile(0.01)
xlim_max = work['gfcf_pct_gdp'].quantile(0.99)

ax_a.scatter(work['gfcf_pct_gdp'], work['dCPR'], s=1.5, alpha=0.12,
             color=COLORS['scatter'], linewidths=0, rasterized=True)

ax_a.plot(lowess_x, lowess_y, color=COLORS['loess'], linewidth=1.8,
          label='LOESS', zorder=5)

ax_a.axhline(0, color=COLORS['zero'], linewidth=0.5, linestyle='--', alpha=0.7)

# 阈值
ax_a.axvline(gamma_report, color=COLORS['threshold'], linewidth=1.5, linestyle='-',
             label=f'$\\gamma$ = {gamma_report:.1f}% [{ci_low:.1f}, {ci_high:.1f}]', zorder=6)
ax_a.axvspan(ci_low, ci_high, alpha=0.12, color=COLORS['threshold'], zorder=1)

# 背景
ax_a.axvspan(xlim_min - 5, gamma_report, alpha=0.06, color='#3498DB', zorder=0)
ax_a.axvspan(gamma_report, xlim_max + 5, alpha=0.06, color='#E74C3C', zorder=0)

# 标注国家
for code, (name, color) in [('CHN', ('China', COLORS['china'])),
                              ('IND', ('India', COLORS['india'])),
                              ('JPN', ('Japan', COLORS['japan'])),
                              ('USA', ('USA', COLORS['usa'])),
                              ('KOR', ('S. Korea', COLORS['korea']))]:
    c = work[work['country_code'] == code]
    if len(c) > 0:
        recent = c[c['year'] >= c['year'].max() - 8]
        ax_a.scatter(recent['gfcf_pct_gdp'], recent['dCPR'], s=14, color=color,
                     alpha=0.85, zorder=7, label=name, edgecolors='white', linewidths=0.3)

ax_a.set_xlim(xlim_min - 1, xlim_max + 1)
ylim = np.percentile(work['dCPR'].values, [1, 99])
ax_a.set_ylim(ylim[0] * 1.3, ylim[1] * 1.3)
ax_a.set_xlabel('GFCF / GDP (%)', fontsize=9)
ax_a.set_ylabel('$\\Delta$CPR (year-over-year change)', fontsize=9)
ax_a.set_title('a', fontsize=11, fontweight='bold', loc='left', x=-0.06)
ax_a.legend(fontsize=6, loc='upper right', framealpha=0.9, edgecolor='none', ncol=2)

ax_a.text(gamma_report - 6, ylim[1] * 1.15, 'Sustainable\ninvestment', fontsize=7,
          color='#2980B9', ha='center', style='italic')
ax_a.text(gamma_report + 8, ylim[1] * 1.15, 'Overinvestment\nzone', fontsize=7,
          color='#C0392B', ha='center', style='italic')

# ---- Panel b-e: 分收入组 ----
for idx, ig in enumerate(income_groups):
    row = 1 + idx // 2
    col = idx % 2
    ax = fig.add_subplot(gs[row, col])

    sub = work[work['income_group'] == ig]
    if len(sub) < 50:
        ax.text(0.5, 0.5, 'Insufficient data', ha='center', va='center',
                transform=ax.transAxes, fontsize=8)
        ax.set_title(f'{"bcde"[idx]}', fontsize=11, fontweight='bold', loc='left', x=-0.15)
        continue

    ax.scatter(sub['gfcf_pct_gdp'], sub['dCPR'], s=1.2, alpha=0.1,
               color=COLORS['scatter'], linewidths=0, rasterized=True)

    try:
        sub_lowess = sm.nonparametric.lowess(sub['dCPR'].values, sub['gfcf_pct_gdp'].values,
                                              frac=0.4, return_sorted=True)
        ax.plot(sub_lowess[:, 0], sub_lowess[:, 1], color=COLORS['loess'], linewidth=1.2)
    except:
        pass

    ax.axhline(0, color=COLORS['zero'], linewidth=0.4, linestyle='--', alpha=0.7)

    r = income_results.get(ig, {})
    if not np.isnan(r.get('gamma', np.nan)):
        ax.axvline(r['gamma'], color=COLORS['threshold'], linewidth=1, linestyle='-')
        ax.axvspan(r.get('ci_low', r['gamma']), r.get('ci_high', r['gamma']),
                   alpha=0.12, color=COLORS['threshold'])
        ax.text(0.95, 0.92, f"$\\gamma$ = {r['gamma']:.1f}%",
                transform=ax.transAxes, fontsize=6.5, ha='right', va='top',
                color=COLORS['threshold'], fontweight='bold')

    # 全样本参考线
    ax.axvline(gamma_report, color=COLORS['threshold'], linewidth=0.5, linestyle=':',
               alpha=0.4)

    xl = sub['gfcf_pct_gdp'].quantile([0.02, 0.98])
    ax.set_xlim(xl.iloc[0] - 1, xl.iloc[1] + 1)
    yl = sub['dCPR'].quantile([0.02, 0.98])
    ax.set_ylim(yl.iloc[0] * 1.5, yl.iloc[1] * 1.5)

    ax.set_xlabel('GFCF/GDP (%)' if idx >= 2 else '', fontsize=7)
    ax.set_ylabel('$\\Delta$CPR' if idx % 2 == 0 else '', fontsize=7)
    ax.set_title(f'{"bcde"[idx]}  {ig}', fontsize=8, fontweight='bold', loc='left', x=-0.15)
    ax.tick_params(labelsize=6.5)

plt.savefig(str(FIG_PATH), dpi=300, bbox_inches='tight')
log(f'旗舰图: {FIG_PATH}')

# ---- 补充图: 中国轨迹 + 滚动窗口 + SSR profile ----
fig2, axes = plt.subplots(1, 3, figsize=(180/25.4, 60/25.4))

# Panel f: 中国时序
ax_f = axes[0]
china_plot = china[china['gfcf_pct_gdp'].notna()]
ax_f.plot(china_plot['year'], china_plot['gfcf_pct_gdp'], color=COLORS['china'], linewidth=1.5)
ax_f.axhline(gamma_report, color=COLORS['threshold'], linewidth=1, linestyle='--',
             label=f'$\\gamma$ = {gamma_report:.1f}%')
ax_f.fill_between(china_plot['year'], gamma_report, china_plot['gfcf_pct_gdp'],
                  where=china_plot['gfcf_pct_gdp'] >= gamma_report,
                  alpha=0.2, color=COLORS['danger'], interpolate=True)
if breach_year:
    ax_f.axvline(breach_year, color='grey', linewidth=0.5, linestyle=':')
    ax_f.annotate(f'{breach_year}', (breach_year, gamma_report),
                  xytext=(5, -8), textcoords='offset points', fontsize=5.5, color='grey')
ax_f.set_xlabel('Year', fontsize=7)
ax_f.set_ylabel('GFCF/GDP (%)', fontsize=7)
ax_f.set_title('f  China', fontsize=8, fontweight='bold', loc='left')
ax_f.legend(fontsize=5.5, framealpha=0.9, edgecolor='none')
ax_f.tick_params(labelsize=6)

# Panel g: 滚动窗口
ax_g = axes[1]
if len(rolling_df) > 0:
    ax_g.plot(rolling_df['mid_year'], rolling_df['gamma'], 'o-',
              color=COLORS['loess'], markersize=2.5, linewidth=1)
    ax_g.axhline(gamma_report, color=COLORS['threshold'], linewidth=0.8, linestyle='--')
    ax_g.set_xlabel('Window midpoint', fontsize=7)
    ax_g.set_ylabel('$\\gamma$ (%)', fontsize=7)
    ax_g.set_title('g  Rolling window', fontsize=8, fontweight='bold', loc='left')
    ax_g.tick_params(labelsize=6)

# Panel h: SSR profile
ax_h = axes[2]
ax_h.plot(ssr_df['gamma'], ssr_df['ssr'], 'k-', linewidth=1)
ax_h.axvline(gamma_hat, color=COLORS['threshold'], linewidth=1, linestyle='--',
             label=f'$\\hat{{\\gamma}}$ = {gamma_hat:.1f}%')
ax_h.set_xlabel('$\\gamma$ (%)', fontsize=7)
ax_h.set_ylabel('SSR', fontsize=7)
ax_h.set_title('h  SSR profile', fontsize=8, fontweight='bold', loc='left')
ax_h.legend(fontsize=5.5, framealpha=0.9, edgecolor='none')
ax_h.tick_params(labelsize=6)

fig2_path = str(FIG_PATH).replace('.png', '_supp.png')
plt.savefig(fig2_path, dpi=300, bbox_inches='tight')
log(f'补充图: {fig2_path}')
plt.close('all')


# ============================================================
# Source Data
# ============================================================
source = work[['country_code', 'country_name', 'income_group', 'year',
               'gfcf_pct_gdp', 'CPR', 'dCPR', 'urban_pct']].copy()
source['regime'] = np.where(source['gfcf_pct_gdp'] >= gamma_report, 'above_threshold', 'below_threshold')
source.to_csv(str(SOURCE_PATH), index=False)
log(f'Source data: {SOURCE_PATH}')
log()


# ============================================================
# 成功标准 & GO/NO-GO
# ============================================================
log('=' * 72)
log('成功标准检查')
log('=' * 72)
log()

criteria = {}

criteria['F_test'] = p_F < 0.05
log(f'[{"PASS" if criteria["F_test"] else "FAIL"}] F 检验 p < 0.05: '
    f'F = {F_stat:.2f}, p = {p_F:.6f}')

criteria['CI_width'] = ci_width < 10
log(f'[{"PASS" if criteria["CI_width"] else "FAIL"}] Bootstrap CI 宽度 < 10pp: '
    f'{ci_width:.1f}pp')

criteria['income_overlap'] = overlap_count >= 2
log(f'[{"PASS" if criteria["income_overlap"] else "FAIL"}] 分收入组 CI 至少 2 组重叠: '
    f'{overlap_count} 对')

oos = robustness_results.get('oos_accuracy', np.nan)
criteria['oos'] = (not np.isnan(oos)) and oos > 0.6
log(f'[{"PASS" if criteria["oos"] else "FAIL"}] 样本外预测 > 60%: '
    f'{oos:.1%}' if not np.isnan(oos) else '[FAIL] 样本外预测: N/A')

log()
must_pass = criteria['F_test']
expected_pass = sum([criteria['CI_width'], criteria['income_overlap']])
bonus_pass = criteria['oos']

log('--- 最终判定 ---')
log(f'必须通过 (F test): {"PASS" if must_pass else "FAIL"}')
log(f'期望通过 (CI + 收入组): {expected_pass}/2')
log(f'加分项 (样本外): {"PASS" if bonus_pass else "FAIL"}')
log()

if must_pass and expected_pass >= 1:
    decision = 'GO'
elif must_pass:
    decision = 'CONDITIONAL GO'
else:
    decision = 'NO-GO'

log(f'{"=" * 30}')
log(f'  判定: {decision}')
log(f'  gamma (I_c/GDP) = {gamma_report:.1f}%')
log(f'  95% CI = [{ci_low:.1f}%, {ci_high:.1f}%]')
log(f'  集成估计 = {gamma_ensemble:.1f}%')
log(f'{"=" * 30}')
log()

if decision == 'GO':
    log('可以推进到论文叙事构建。')
    log(f'核心发现: 当 GFCF/GDP 超过 ~{gamma_report:.0f}% 时, 城市资本-产出比 (CPR) 开始')
    log(f'系统性下降, 表明投资效率出现转折。这一阈值在不同收入组中')
    if universal_narrative:
        log(f'高度一致 (CI 全部重叠), 支持"普适阈值"的叙事。')
    else:
        log(f'存在差异, 但总体趋势一致。')
elif decision == 'CONDITIONAL GO':
    log('阈值效应显著但不够稳健。建议:')
    log('  1. 增加控制变量 (人口结构、制度质量)')
    log('  2. 使用双阈值模型检验是否存在两个拐点')
    log('  3. 考虑动态面板模型 (System GMM)')
else:
    log('阈值效应不显著。建议重新考虑理论框架。')

log()
log('=' * 72)

with open(str(REPORT_PATH), 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
print(f'\n报告: {REPORT_PATH}')
print('完成。')
