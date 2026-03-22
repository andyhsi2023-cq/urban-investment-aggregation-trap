"""
95_mechanical_correlation_test.py -- MUQ vs FAI/GDP 机械相关检验与替代度量分析
================================================================================

目的:
  审稿人指出 MUQ = DeltaV / FAI 与 FAI/GDP 共享 FAI，构成负向机械相关。
  本脚本通过蒙特卡洛模拟量化机械相关的预期大小，并用不受机械相关影响的
  替代度量重新估计核心关系，判断 Finding 2 是否需要重构。

输入:
  - 02-data/processed/china_city_panel_real.csv
  - 02-data/processed/us_msa_muq_panel.csv

输出:
  - 03-analysis/models/mechanical_correlation_report.txt
  - 04-figures/drafts/fig_mechanical_correlation.png

依赖: pandas, numpy, scipy, statsmodels, matplotlib
"""

import os
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# =============================================================================
# 路径配置与随机种子
# =============================================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
CHINA_PATH = os.path.join(BASE, '02-data/processed/china_city_panel_real.csv')
US_PATH = os.path.join(BASE, '02-data/processed/us_msa_muq_panel.csv')
REPORT_PATH = os.path.join(BASE, '03-analysis/models/mechanical_correlation_report.txt')
FIG_PATH = os.path.join(BASE, '04-figures/drafts/fig_mechanical_correlation.png')

np.random.seed(20260321)
N_MC = 10000  # 蒙特卡洛模拟次数

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

def robust_ols(y, X, cluster=None):
    """OLS with HC1 or clustered standard errors"""
    model = sm.OLS(y, sm.add_constant(X)).fit(
        cov_type='cluster' if cluster is not None else 'HC1',
        cov_kwds={'groups': cluster} if cluster is not None else {}
    )
    return model

# =============================================================================
# 1. 数据加载 -- 中国城市面板
# =============================================================================
rprint('=' * 80)
rprint('P0: MUQ vs FAI/GDP 机械相关检验与替代度量分析')
rprint('=' * 80)
rprint(f'日期: 2026-03-21')
rprint(f'随机种子: 20260321, 蒙特卡洛次数: {N_MC}')
rprint()

df = pd.read_csv(CHINA_PATH)
panel = df[(df['year'] >= 2010) & (df['year'] <= 2016)].copy()

# 重建缺失 V
mask_v = panel['V_100m'].isna() & panel['house_price'].notna()
panel.loc[mask_v, 'V_100m'] = (
    panel.loc[mask_v, 'house_price'] *
    panel.loc[mask_v, 'per_capita_area_m2'] *
    panel.loc[mask_v, 'pop_10k'] * 10000 / 1e8
)

# 排序并计算 DeltaV 和 MUQ
panel = panel.sort_values(['city', 'year']).reset_index(drop=True)
panel['V_lag'] = panel.groupby('city')['V_100m'].shift(1)
panel['delta_V'] = panel['V_100m'] - panel['V_lag']
panel['I'] = panel['fai_100m']
panel['MUQ'] = np.where(
    (panel['I'] > 1) & (panel['delta_V'].notna()),
    panel['delta_V'] / panel['I'],
    np.nan
)
panel['fai_gdp'] = panel['fai_gdp_ratio']

# 筛选有效观测 (2011-2016, 有 MUQ 和 fai_gdp)
muq_panel = panel[(panel['year'] >= 2011)].copy()
muq_valid = muq_panel.dropna(subset=['MUQ', 'fai_gdp', 'delta_V', 'I', 'gdp_100m']).copy()

# Winsorize
muq_valid['MUQ_w'] = winsorize(muq_valid['MUQ'])
muq_valid['fai_gdp_w'] = winsorize(muq_valid['fai_gdp'])

rprint(f'中国城市面板: {len(muq_valid)} 观测, {muq_valid["city"].nunique()} 城市')
rprint(f'年份范围: {muq_valid["year"].min()}-{muq_valid["year"].max()}')

# 基准回归: 重现 beta = -2.23
model_base = robust_ols(muq_valid['MUQ_w'], muq_valid['fai_gdp_w'])
beta_real = model_base.params.iloc[1]
ci_real = model_base.conf_int().iloc[1].values
se_real = model_base.bse.iloc[1]
t_real = model_base.tvalues.iloc[1]
p_real = model_base.pvalues.iloc[1]

rprint()
rprint('--- 基准回归 (重现) ---')
rprint(f'  MUQ ~ FAI/GDP (Pooled OLS, HC1)')
rprint(f'  N = {len(muq_valid)}')
rprint(f'  beta = {beta_real:.4f}')
rprint(f'  95% CI = [{ci_real[0]:.4f}, {ci_real[1]:.4f}]')
rprint(f'  t = {t_real:.3f}, p = {p_real:.6e}')
rprint(f'  R-squared = {model_base.rsquared:.4f}')

# =============================================================================
# 2. 蒙特卡洛模拟 -- 量化机械相关
# =============================================================================
rprint()
rprint('=' * 80)
rprint('Step 2: 蒙特卡洛模拟 -- 量化纯机械相关的预期 beta')
rprint('=' * 80)

# 提取原始变量的边际分布
delta_V_vals = muq_valid['delta_V'].values.copy()
fai_vals = muq_valid['I'].values.copy()
gdp_vals = muq_valid['gdp_100m'].values.copy()

rprint()
rprint('--- MC 方案 A: 打乱 DeltaV 和 FAI (保留 GDP) ---')
rprint('  逻辑: 打破 DeltaV-FAI-GDP 之间的真实经济关联，保留边际分布')
rprint(f'  模拟次数: {N_MC}')

betas_mc_a = np.full(N_MC, np.nan)
for i in range(N_MC):
    # 独立打乱 DeltaV 和 FAI
    dv_shuf = np.random.permutation(delta_V_vals)
    fai_shuf = np.random.permutation(fai_vals)
    # GDP 保持原位
    muq_rand = dv_shuf / fai_shuf
    fai_gdp_rand = fai_shuf / gdp_vals
    # Winsorize
    lo_m, hi_m = np.percentile(muq_rand, [1, 99])
    muq_rand = np.clip(muq_rand, lo_m, hi_m)
    lo_f, hi_f = np.percentile(fai_gdp_rand, [1, 99])
    fai_gdp_rand = np.clip(fai_gdp_rand, lo_f, hi_f)
    # 回归
    mask_finite = np.isfinite(muq_rand) & np.isfinite(fai_gdp_rand)
    if mask_finite.sum() > 10:
        X_mc = sm.add_constant(fai_gdp_rand[mask_finite])
        try:
            m = sm.OLS(muq_rand[mask_finite], X_mc).fit()
            betas_mc_a[i] = m.params[1]
        except Exception:
            pass

betas_mc_a = betas_mc_a[np.isfinite(betas_mc_a)]
mc_a_mean = np.mean(betas_mc_a)
mc_a_median = np.median(betas_mc_a)
mc_a_ci = np.percentile(betas_mc_a, [2.5, 97.5])
mc_a_p = np.mean(betas_mc_a <= beta_real)  # 经验 p 值

rprint(f'  成功模拟: {len(betas_mc_a)}/{N_MC}')
rprint(f'  MC beta 均值 = {mc_a_mean:.4f}')
rprint(f'  MC beta 中位数 = {mc_a_median:.4f}')
rprint(f'  MC beta 95% CI = [{mc_a_ci[0]:.4f}, {mc_a_ci[1]:.4f}]')
rprint(f'  真实 beta = {beta_real:.4f}')
rprint(f'  经验 p 值 (MC beta <= 真实 beta) = {mc_a_p:.4f}')

if mc_a_ci[0] <= beta_real <= mc_a_ci[1]:
    rprint('  >> 判断: 真实 beta 落在 MC 95% CI 内 -- 机械相关可能占主导')
    mc_a_pass = False
else:
    rprint('  >> 判断: 真实 beta 落在 MC 95% CI 外 -- 存在超出机械相关的真实效应')
    mc_a_pass = True

rprint()
rprint('--- MC 方案 B: 固定 FAI, 只打乱 DeltaV 和 GDP 的配对 ---')
rprint('  逻辑: 更严格检验 -- 保留 FAI 的真实城市分布，只打破 DeltaV/GDP 的经济含义')

betas_mc_b = np.full(N_MC, np.nan)
for i in range(N_MC):
    # FAI 保持原位，打乱 DeltaV 和 GDP
    dv_shuf = np.random.permutation(delta_V_vals)
    gdp_shuf = np.random.permutation(gdp_vals)
    muq_rand = dv_shuf / fai_vals
    fai_gdp_rand = fai_vals / gdp_shuf
    # Winsorize
    lo_m, hi_m = np.percentile(muq_rand, [1, 99])
    muq_rand = np.clip(muq_rand, lo_m, hi_m)
    lo_f, hi_f = np.percentile(fai_gdp_rand, [1, 99])
    fai_gdp_rand = np.clip(fai_gdp_rand, lo_f, hi_f)
    mask_finite = np.isfinite(muq_rand) & np.isfinite(fai_gdp_rand)
    if mask_finite.sum() > 10:
        X_mc = sm.add_constant(fai_gdp_rand[mask_finite])
        try:
            m = sm.OLS(muq_rand[mask_finite], X_mc).fit()
            betas_mc_b[i] = m.params[1]
        except Exception:
            pass

betas_mc_b = betas_mc_b[np.isfinite(betas_mc_b)]
mc_b_mean = np.mean(betas_mc_b)
mc_b_median = np.median(betas_mc_b)
mc_b_ci = np.percentile(betas_mc_b, [2.5, 97.5])
mc_b_p = np.mean(betas_mc_b <= beta_real)

rprint(f'  成功模拟: {len(betas_mc_b)}/{N_MC}')
rprint(f'  MC beta 均值 = {mc_b_mean:.4f}')
rprint(f'  MC beta 中位数 = {mc_b_median:.4f}')
rprint(f'  MC beta 95% CI = [{mc_b_ci[0]:.4f}, {mc_b_ci[1]:.4f}]')
rprint(f'  真实 beta = {beta_real:.4f}')
rprint(f'  经验 p 值 (MC beta <= 真实 beta) = {mc_b_p:.4f}')

if mc_b_ci[0] <= beta_real <= mc_b_ci[1]:
    rprint('  >> 判断: 真实 beta 落在 MC 95% CI 内 -- 机械相关可能占主导 (严格版)')
    mc_b_pass = False
else:
    rprint('  >> 判断: 真实 beta 落在 MC 95% CI 外 -- 真实效应超出机械相关 (严格版)')
    mc_b_pass = True

# =============================================================================
# 3. 替代度量分析
# =============================================================================
rprint()
rprint('=' * 80)
rprint('Step 3: 替代度量分析 -- 使用不受机械相关影响的变量')
rprint('=' * 80)

# --- 3a. DeltaV/GDP ~ FAI/GDP (移除 FAI 共享) ---
rprint()
rprint('-' * 60)
rprint('3a: DeltaV/GDP ~ FAI/GDP (消除 FAI 作为共享分母)')
rprint('-' * 60)

muq_valid['dv_gdp'] = muq_valid['delta_V'] / muq_valid['gdp_100m']
muq_valid['dv_gdp_w'] = winsorize(muq_valid['dv_gdp'])

model_3a = robust_ols(muq_valid['dv_gdp_w'], muq_valid['fai_gdp_w'])
b_3a = model_3a.params.iloc[1]
ci_3a = model_3a.conf_int().iloc[1].values
p_3a = model_3a.pvalues.iloc[1]

rprint(f'  N = {len(muq_valid)}')
rprint(f'  beta(FAI/GDP) = {b_3a:.4f}')
rprint(f'  95% CI = [{ci_3a[0]:.4f}, {ci_3a[1]:.4f}]')
rprint(f'  t = {model_3a.tvalues.iloc[1]:.3f}, p = {p_3a:.6e}')
rprint(f'  R-squared = {model_3a.rsquared:.4f}')
if p_3a < 0.05 and b_3a < 0:
    rprint('  >> 判断: DeltaV/GDP 与 FAI/GDP 显著负相关 -- 核心关系稳健')
    test_3a_pass = True
elif b_3a < 0:
    rprint(f'  >> 判断: 系数为负但不显著 (p={p_3a:.4f}) -- 方向一致但精度不足')
    test_3a_pass = 'partial'
else:
    rprint('  >> 判断: 系数不为负 -- 原关系可能由机械相关驱动')
    test_3a_pass = False

# --- 3b. DeltaV 水平值 ~ FAI + GDP + controls ---
rprint()
rprint('-' * 60)
rprint('3b: DeltaV ~ FAI + GDP + controls (水平值回归)')
rprint('-' * 60)

muq_valid['ln_gdp'] = np.log(muq_valid['gdp_100m'].clip(lower=1))
muq_valid['ln_fai'] = np.log(muq_valid['I'].clip(lower=1))
muq_valid['delta_V_w'] = winsorize(muq_valid['delta_V'])
muq_valid['fai_w'] = winsorize(muq_valid['I'])
muq_valid['gdp_w'] = winsorize(muq_valid['gdp_100m'])

X_3b = muq_valid[['fai_w', 'gdp_w']].copy()
model_3b = robust_ols(muq_valid['delta_V_w'], X_3b)

rprint(f'  N = {len(muq_valid)}')
rprint(f'  DeltaV ~ FAI + GDP (Pooled OLS, HC1)')
for j, name in enumerate(['const', 'FAI', 'GDP']):
    rprint(f'    {name:12s}: coef = {model_3b.params.iloc[j]:10.4f}, '
           f't = {model_3b.tvalues.iloc[j]:7.3f}, p = {model_3b.pvalues.iloc[j]:.6e}')
rprint(f'  R-squared = {model_3b.rsquared:.4f}')

b_fai_3b = model_3b.params.iloc[1]
p_fai_3b = model_3b.pvalues.iloc[1]
if b_fai_3b < 0 and p_fai_3b < 0.05:
    rprint('  >> 判断: FAI 系数显著为负 -- 更多投资确实压低价值增量')
    test_3b_pass = True
elif b_fai_3b < 1 and p_fai_3b < 0.05:
    rprint(f'  >> 判断: FAI 系数为正 ({b_fai_3b:.4f}) 但 < 1 -- 投资回报递减')
    test_3b_pass = 'partial'
else:
    rprint(f'  >> 判断: FAI 系数 = {b_fai_3b:.4f}, p = {p_fai_3b:.4f}')
    test_3b_pass = False

# --- 3c. ln(DeltaV) ~ ln(FAI) 弹性估计 ---
rprint()
rprint('-' * 60)
rprint('3c: ln(DeltaV) ~ ln(FAI) 弹性估计')
rprint('-' * 60)

# DeltaV 可能为负，只用正值子样本估计弹性
pos_dv = muq_valid[muq_valid['delta_V'] > 0].copy()
rprint(f'  DeltaV > 0 的观测: {len(pos_dv)}/{len(muq_valid)} ({100*len(pos_dv)/len(muq_valid):.1f}%)')

if len(pos_dv) > 30:
    pos_dv['ln_dv'] = np.log(pos_dv['delta_V'])
    pos_dv['ln_fai'] = np.log(pos_dv['I'])
    pos_dv['ln_dv_w'] = winsorize(pos_dv['ln_dv'])
    pos_dv['ln_fai_w'] = winsorize(pos_dv['ln_fai'])

    model_3c = robust_ols(pos_dv['ln_dv_w'], pos_dv['ln_fai_w'])
    elasticity = model_3c.params.iloc[1]
    ci_3c = model_3c.conf_int().iloc[1].values
    p_3c = model_3c.pvalues.iloc[1]

    rprint(f'  ln(DeltaV) ~ ln(FAI) (正 DeltaV 子样本)')
    rprint(f'  N = {len(pos_dv)}')
    rprint(f'  弹性 = {elasticity:.4f}')
    rprint(f'  95% CI = [{ci_3c[0]:.4f}, {ci_3c[1]:.4f}]')
    rprint(f'  p = {p_3c:.6e}')
    rprint(f'  R-squared = {model_3c.rsquared:.4f}')

    if elasticity < 1 and p_3c < 0.05:
        rprint(f'  >> 判断: 弹性 = {elasticity:.4f} < 1 -- 边际递减成立')
        test_3c_pass = True
    elif elasticity < 1:
        rprint(f'  >> 判断: 弹性 < 1 但不显著 -- 方向一致但精度不足')
        test_3c_pass = 'partial'
    else:
        rprint(f'  >> 判断: 弹性 >= 1 -- 无边际递减证据')
        test_3c_pass = False

    # 也检查是否与 1 显著不同
    t_vs_1 = (elasticity - 1) / model_3c.bse.iloc[1]
    p_vs_1 = 2 * stats.t.cdf(t_vs_1, df=model_3c.df_resid)  # 左尾
    rprint(f'  H0: elasticity = 1, t = {t_vs_1:.3f}, p(one-sided, <1) = {p_vs_1/2:.6e}')
else:
    rprint('  >> 正 DeltaV 观测不足，跳过弹性估计')
    elasticity = np.nan
    test_3c_pass = False

# --- 3d. MUQ ~ FAI/GDP + ln(FAI) 控制 FAI 水平 ---
rprint()
rprint('-' * 60)
rprint('3d: MUQ ~ FAI/GDP + ln(FAI) (控制 FAI 水平后检查 FAI/GDP 是否存活)')
rprint('-' * 60)

X_3d = muq_valid[['fai_gdp_w']].copy()
X_3d['ln_fai'] = winsorize(np.log(muq_valid['I'].clip(lower=1)))
model_3d = robust_ols(muq_valid['MUQ_w'], X_3d)

rprint(f'  N = {len(muq_valid)}')
rprint(f'  MUQ ~ FAI/GDP + ln(FAI) (Pooled OLS, HC1)')
for j, name in enumerate(['const', 'FAI/GDP', 'ln(FAI)']):
    rprint(f'    {name:12s}: coef = {model_3d.params.iloc[j]:10.4f}, '
           f't = {model_3d.tvalues.iloc[j]:7.3f}, p = {model_3d.pvalues.iloc[j]:.6e}')
rprint(f'  R-squared = {model_3d.rsquared:.4f}')

b_fg_3d = model_3d.params.iloc[1]
p_fg_3d = model_3d.pvalues.iloc[1]
if b_fg_3d < 0 and p_fg_3d < 0.05:
    rprint('  >> 判断: 控制 ln(FAI) 后 FAI/GDP 仍显著为负 -- 机械相关已控制')
    test_3d_pass = True
else:
    rprint(f'  >> 判断: 控制 ln(FAI) 后 FAI/GDP 不再显著 (p={p_fg_3d:.4f}) -- 效应被 FAI 水平吸收')
    test_3d_pass = False

# --- 3e. 中美统一度量: DeltaV/GDP ---
rprint()
rprint('-' * 60)
rprint('3e: 中美统一度量 DeltaV/GDP -- 检查符号反转是否在统一度量下成立')
rprint('-' * 60)

# 中国: DeltaV/GDP ~ FAI/GDP (已在 3a 中完成)
rprint(f'  中国: DeltaV/GDP ~ FAI/GDP')
rprint(f'    beta = {b_3a:.4f}, p = {p_3a:.6e}')
rprint(f'    方向: {"负" if b_3a < 0 else "正"}')

# 美国
us_df = pd.read_csv(US_PATH)
rprint(f'  美国面板: {len(us_df)} 行, 列: {list(us_df.columns[:15])}...')

# 美国的 DeltaV/GDP
us_valid = us_df.dropna(subset=['dV', 'gdp_millions', 'hu_growth']).copy()
us_valid = us_valid[us_valid['gdp_millions'] > 0].copy()
us_valid['dv_gdp'] = us_valid['dV'] / (us_valid['gdp_millions'] * 1e6)  # dV 是美元, gdp 是百万美元
# 检查 invest_intensity 列
if 'invest_intensity' in us_valid.columns:
    us_valid = us_valid.dropna(subset=['invest_intensity'])
    us_valid['invest_w'] = winsorize(us_valid['invest_intensity'])
    invest_col = 'invest_w'
    invest_label = 'invest_intensity'
else:
    us_valid['hu_growth_w'] = winsorize(us_valid['hu_growth'])
    invest_col = 'hu_growth_w'
    invest_label = 'hu_growth'

us_valid['dv_gdp_w'] = winsorize(us_valid['dv_gdp'])

rprint(f'  美国有效观测: {len(us_valid)}')

if len(us_valid) > 30:
    model_us = robust_ols(us_valid['dv_gdp_w'], us_valid[invest_col])
    b_us = model_us.params.iloc[1]
    ci_us = model_us.conf_int().iloc[1].values
    p_us = model_us.pvalues.iloc[1]

    rprint(f'  美国: DeltaV/GDP ~ {invest_label}')
    rprint(f'    N = {len(us_valid)}')
    rprint(f'    beta = {b_us:.4f}')
    rprint(f'    95% CI = [{ci_us[0]:.4f}, {ci_us[1]:.4f}]')
    rprint(f'    p = {p_us:.6e}')
    rprint(f'    方向: {"正" if b_us > 0 else "负"}')
    rprint(f'    R-squared = {model_us.rsquared:.4f}')

    if (b_3a < 0 and b_us > 0):
        rprint('  >> 判断: 统一度量下中美符号反转成立')
        test_3e_pass = True
    elif (b_3a < 0 and b_us < 0):
        rprint('  >> 判断: 统一度量下美国也为负 -- 符号反转不成立，可能是度量差异')
        test_3e_pass = False
    else:
        rprint('  >> 判断: 中国不为负 -- 原关系不稳健')
        test_3e_pass = False
else:
    rprint('  美国有效观测不足，跳过')
    b_us = np.nan
    test_3e_pass = False

# 也用 hu_growth 做美国的替代
if 'hu_growth' in us_valid.columns and invest_label != 'hu_growth':
    us_valid['hu_w'] = winsorize(us_valid['hu_growth'])
    model_us_hu = robust_ols(us_valid['dv_gdp_w'], us_valid['hu_w'])
    rprint(f'  美国 (hu_growth): beta = {model_us_hu.params.iloc[1]:.4f}, '
           f'p = {model_us_hu.pvalues.iloc[1]:.6e}')

# =============================================================================
# 4. 汇总判断
# =============================================================================
rprint()
rprint('=' * 80)
rprint('Step 4: 汇总判断')
rprint('=' * 80)
rprint()
rprint(f'{"检验":<45s} {"结果":<12s} {"判断"}')
rprint('-' * 90)

def fmt_pass(v):
    if v is True:
        return 'PASS'
    elif v == 'partial':
        return 'PARTIAL'
    else:
        return 'FAIL'

tests = [
    ('MC-A: 打乱DeltaV+FAI, beta 95%CI不含真实beta', mc_a_pass,
     '机械相关不占主导' if mc_a_pass else '机械相关可能占主导'),
    ('MC-B: 固定FAI, 打乱DeltaV+GDP配对', mc_b_pass,
     '真实效应超出机械相关' if mc_b_pass else '机械相关可能占主导'),
    ('3a: DeltaV/GDP ~ FAI/GDP 显著为负', test_3a_pass,
     '核心关系稳健(无共享分母)' if test_3a_pass is True else '方向一致但精度不足' if test_3a_pass == 'partial' else '需要重构'),
    ('3b: DeltaV ~ FAI + GDP, FAI系数', test_3b_pass,
     '投资压低价值增量' if test_3b_pass is True else '回报递减' if test_3b_pass == 'partial' else '无直接证据'),
    ('3c: ln(DeltaV) ~ ln(FAI) 弹性 < 1', test_3c_pass,
     f'弹性={elasticity:.3f}<1' if test_3c_pass is True else '无边际递减证据'),
    ('3d: 控制ln(FAI)后FAI/GDP仍显著', test_3d_pass,
     'FAI/GDP效应独立于FAI水平' if test_3d_pass else 'FAI/GDP被FAI水平吸收'),
    ('3e: 中美统一度量DeltaV/GDP符号反转', test_3e_pass,
     '制度差异稳健' if test_3e_pass else '可能是度量差异'),
]

n_pass = 0
n_total = len(tests)
for name, result, desc in tests:
    status = fmt_pass(result)
    rprint(f'  {name:<45s} {status:<12s} {desc}')
    if result is True:
        n_pass += 1

rprint()
rprint(f'总计: {n_pass}/{n_total} 项通过')
rprint()

if n_pass >= 5:
    rprint('>> 总体判断: Finding 2 核心结论稳健，机械相关不是主要驱动力。')
    rprint('   建议: 在论文中增加替代度量作为稳健性检验，直接回应审稿人。')
elif n_pass >= 3:
    rprint('>> 总体判断: Finding 2 部分稳健，机械相关有贡献但非全部。')
    rprint('   建议: 在正文中改用 DeltaV/GDP 作为主要度量，MUQ 降级为补充。')
else:
    rprint('>> 总体判断: Finding 2 可能需要重大修改，机械相关贡献显著。')
    rprint('   建议: 重新构建核心论证，避免使用 MUQ = DeltaV/FAI 回归 FAI/GDP。')

# =============================================================================
# 5. 图表绘制
# =============================================================================
rprint()
rprint('生成图表...')

fig = plt.figure(figsize=(16, 12))
gs = gridspec.GridSpec(2, 2, hspace=0.35, wspace=0.30,
                       left=0.08, right=0.96, top=0.94, bottom=0.06)

# 颜色
C_CHINA = '#B2182B'
C_US = '#2166AC'
C_MC = '#636363'
C_REAL = '#E41A1C'

# --- Panel (a): MC beta 分布 vs 真实 beta ---
ax_a = fig.add_subplot(gs[0, 0])

# 方案 A 的分布
ax_a.hist(betas_mc_a, bins=80, density=True, alpha=0.5, color=C_MC,
          edgecolor='none', label=f'MC-A (shuffle DeltaV+FAI)\nmedian={mc_a_median:.3f}')
ax_a.axvline(beta_real, color=C_REAL, linewidth=2.5, linestyle='-',
             label=f'Observed beta={beta_real:.3f}')
ax_a.axvline(mc_a_ci[0], color=C_MC, linewidth=1, linestyle='--', alpha=0.7)
ax_a.axvline(mc_a_ci[1], color=C_MC, linewidth=1, linestyle='--', alpha=0.7,
             label=f'MC 95% CI [{mc_a_ci[0]:.2f}, {mc_a_ci[1]:.2f}]')

# 方案 B
ax_a.hist(betas_mc_b, bins=80, density=True, alpha=0.35, color='#4393C3',
          edgecolor='none', label=f'MC-B (fix FAI)\nmedian={mc_b_median:.3f}')
mc_b_ci_lines = np.percentile(betas_mc_b, [2.5, 97.5])
ax_a.axvline(mc_b_ci_lines[0], color='#4393C3', linewidth=1, linestyle=':', alpha=0.7)
ax_a.axvline(mc_b_ci_lines[1], color='#4393C3', linewidth=1, linestyle=':', alpha=0.7)

ax_a.set_xlabel('beta (MUQ ~ FAI/GDP)', fontsize=11)
ax_a.set_ylabel('Density', fontsize=11)
ax_a.set_title('(a) Monte Carlo: Mechanical Correlation Benchmark', fontsize=12, fontweight='bold')
ax_a.legend(fontsize=8, loc='upper left')
ax_a.spines['top'].set_visible(False)
ax_a.spines['right'].set_visible(False)

# --- Panel (b): DeltaV/GDP ~ FAI/GDP 散点 ---
ax_b = fig.add_subplot(gs[0, 1])

ax_b.scatter(muq_valid['fai_gdp_w'], muq_valid['dv_gdp_w'],
             s=8, alpha=0.3, color=C_CHINA, edgecolors='none')

# 回归线
x_range = np.linspace(muq_valid['fai_gdp_w'].min(), muq_valid['fai_gdp_w'].max(), 100)
y_hat = model_3a.params.iloc[0] + model_3a.params.iloc[1] * x_range
ax_b.plot(x_range, y_hat, color=C_CHINA, linewidth=2,
          label=f'beta={b_3a:.3f}, p={p_3a:.2e}')

ax_b.axhline(0, color='grey', linewidth=0.5, linestyle='--')
ax_b.set_xlabel('FAI/GDP', fontsize=11)
ax_b.set_ylabel('DeltaV/GDP', fontsize=11)
ax_b.set_title('(b) Alternative Metric: DeltaV/GDP ~ FAI/GDP\n(No shared denominator)', fontsize=12, fontweight='bold')
ax_b.legend(fontsize=9)
ax_b.spines['top'].set_visible(False)
ax_b.spines['right'].set_visible(False)

# --- Panel (c): 弹性估计 ln(DeltaV) ~ ln(FAI) ---
ax_c = fig.add_subplot(gs[1, 0])

if len(pos_dv) > 30:
    ax_c.scatter(pos_dv['ln_fai_w'], pos_dv['ln_dv_w'],
                 s=8, alpha=0.3, color='#4DAF4A', edgecolors='none')

    x_range_c = np.linspace(pos_dv['ln_fai_w'].min(), pos_dv['ln_fai_w'].max(), 100)
    y_hat_c = model_3c.params.iloc[0] + model_3c.params.iloc[1] * x_range_c
    ax_c.plot(x_range_c, y_hat_c, color='#4DAF4A', linewidth=2,
              label=f'Elasticity={elasticity:.3f}\n95% CI [{ci_3c[0]:.3f}, {ci_3c[1]:.3f}]')

    # 45 度线 (elasticity=1)
    ax_c.plot(x_range_c, model_3c.params.iloc[0] + 1.0 * x_range_c,
              color='grey', linewidth=1, linestyle='--', label='Elasticity=1 (reference)')

    ax_c.set_xlabel('ln(FAI)', fontsize=11)
    ax_c.set_ylabel('ln(DeltaV)', fontsize=11)
    ax_c.legend(fontsize=9)
else:
    ax_c.text(0.5, 0.5, 'Insufficient positive DeltaV\nobservations',
              ha='center', va='center', transform=ax_c.transAxes, fontsize=12)

ax_c.set_title('(c) Elasticity: ln(DeltaV) ~ ln(FAI)\n(Positive DeltaV subsample)', fontsize=12, fontweight='bold')
ax_c.spines['top'].set_visible(False)
ax_c.spines['right'].set_visible(False)

# --- Panel (d): 中美统一度量对比 ---
ax_d = fig.add_subplot(gs[1, 1])

# 条形图: 中国 vs 美国 的 beta (DeltaV/GDP 度量)
bar_labels = ['China\nDeltaV/GDP ~ FAI/GDP', 'US\nDeltaV/GDP ~ invest']
bar_values = [b_3a, b_us if np.isfinite(b_us) else 0]
bar_colors = [C_CHINA, C_US]
bar_ci_lower = [b_3a - ci_3a[0], (b_us - ci_us[0]) if np.isfinite(b_us) else 0]
bar_ci_upper = [ci_3a[1] - b_3a, (ci_us[1] - b_us) if np.isfinite(b_us) else 0]

bars = ax_d.bar(bar_labels, bar_values, color=bar_colors, alpha=0.7,
                edgecolor='black', linewidth=0.5, width=0.5)
ax_d.errorbar(bar_labels, bar_values,
              yerr=[bar_ci_lower, bar_ci_upper],
              fmt='none', color='black', capsize=8, linewidth=1.5)

ax_d.axhline(0, color='grey', linewidth=1, linestyle='-')
ax_d.set_ylabel('beta (DeltaV/GDP ~ Investment Intensity)', fontsize=11)
ax_d.set_title('(d) China vs US: Unified Metric Comparison\n(DeltaV/GDP eliminates shared FAI)', fontsize=12, fontweight='bold')
ax_d.spines['top'].set_visible(False)
ax_d.spines['right'].set_visible(False)

# 标注数值
for bar, val in zip(bars, bar_values):
    y_pos = val + 0.02 if val > 0 else val - 0.02
    ax_d.text(bar.get_x() + bar.get_width() / 2, y_pos, f'{val:.3f}',
              ha='center', va='bottom' if val > 0 else 'top', fontsize=11, fontweight='bold')

# 保存
fig.savefig(FIG_PATH, dpi=200, bbox_inches='tight')
plt.close()
rprint(f'图表保存至: {FIG_PATH}')

# =============================================================================
# 6. 保存报告
# =============================================================================
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
rprint(f'报告保存至: {REPORT_PATH}')

print('\n--- 完成 ---')
