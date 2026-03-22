"""
城市级 MUQ 分布分析 — 290 城市 x 2010-2016
==============================================

目的: 利用中国城市面板的真实 FAI 窗口 (2010-2016) 计算城市级 MUQ,
      分析其分布演化、与投资强度的关系、区域差异和预测能力。

输入: 02-data/processed/china_city_panel_real.csv
输出:
  - 03-analysis/models/city_muq_distribution_report.txt
  - 04-figures/drafts/fig_city_muq_distribution.png

依赖: pandas, numpy, scipy, statsmodels, matplotlib, sklearn
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
from scipy import stats
from io import StringIO
import statsmodels.api as sm
from statsmodels.regression.quantile_regression import QuantReg
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# =============================================================================
# 路径配置
# =============================================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
DATA_PATH = os.path.join(BASE, '02-data/processed/china_city_panel_real.csv')
REPORT_PATH = os.path.join(BASE, '03-analysis/models/city_muq_distribution_report.txt')
FIG_PATH = os.path.join(BASE, '04-figures/drafts/fig_city_muq_distribution.png')

# 随机种子
np.random.seed(42)
DELTA = 0.05  # 折旧率，与面板 K 构建一致

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

def mann_kendall_test(x):
    """Mann-Kendall 趋势检验"""
    n = len(x)
    s = 0
    for k in range(n - 1):
        for j in range(k + 1, n):
            s += np.sign(x[j] - x[k])
    # 方差
    unique, counts = np.unique(x, return_counts=True)
    var_s = (n * (n - 1) * (2 * n + 5)) / 18
    for c in counts:
        if c > 1:
            var_s -= c * (c - 1) * (2 * c + 5) / 18
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    tau = s / (n * (n - 1) / 2)
    return z, p, tau

def robust_ols(y, X, cluster=None):
    """OLS with HC1 or clustered standard errors"""
    model = sm.OLS(y, sm.add_constant(X)).fit(
        cov_type='cluster' if cluster is not None else 'HC1',
        cov_kwds={'groups': cluster} if cluster is not None else {}
    )
    return model

# =============================================================================
# 1. 数据加载与清洗
# =============================================================================
rprint('=' * 80)
rprint('城市级 MUQ 分布分析 — 中国 290 城市 x 2010-2016')
rprint('=' * 80)
rprint()

df = pd.read_csv(DATA_PATH)
rprint(f'原始数据: {len(df)} 行, {df["city"].nunique()} 城市, '
       f'年份 {df["year"].min()}-{df["year"].max()}')

# 筛选 2010-2016 真实 FAI 窗口
panel = df[(df['year'] >= 2010) & (df['year'] <= 2016)].copy()
rprint(f'2010-2016 窗口: {len(panel)} 行, {panel["city"].nunique()} 城市')

# 计算 V（对于缺失 V 但有 house_price 的城市重建）
# V_100m = house_price * per_capita_area_m2 * pop_10k * 10000 / 1e8
mask_v_missing = panel['V_100m'].isna() & panel['house_price'].notna()
panel.loc[mask_v_missing, 'V_100m'] = (
    panel.loc[mask_v_missing, 'house_price'] *
    panel.loc[mask_v_missing, 'per_capita_area_m2'] *
    panel.loc[mask_v_missing, 'pop_10k'] * 10000 / 1e8
)
rprint(f'V 重建后覆盖: {panel["V_100m"].notna().sum()}/{len(panel)} 行')

# =============================================================================
# 2. 计算城市级 MUQ
# =============================================================================
rprint()
rprint('-' * 60)
rprint('Part A: 城市级 MUQ 计算')
rprint('-' * 60)

# 排序以确保正确的时间差分
panel = panel.sort_values(['city', 'year']).reset_index(drop=True)

# 计算 ΔV = V(t) - V(t-1)
panel['V_lag'] = panel.groupby('city')['V_100m'].shift(1)
panel['delta_V'] = panel['V_100m'] - panel['V_lag']

# 投资 I = FAI (当年固定资产投资)
panel['I'] = panel['fai_100m']

# MUQ = ΔV / I
# 过滤: I 须为正且大于一定阈值（避免除以接近 0 的数）
panel['MUQ'] = np.where(
    (panel['I'] > 0) & (panel['delta_V'].notna()),
    panel['delta_V'] / panel['I'],
    np.nan
)

# 2011-2016 才有 MUQ（需要前一年的 V）
muq_panel = panel[panel['year'] >= 2011].copy()

# 过滤 I 过小的观测（< 1 亿元）
too_small_I = muq_panel['I'] < 1
rprint(f'投资额 < 1 亿元的观测数: {too_small_I.sum()} (排除)')
muq_panel.loc[too_small_I, 'MUQ'] = np.nan

# MUQ 覆盖率
rprint()
rprint('MUQ 可计算的城市数 (按年份):')
for yr in range(2011, 2017):
    n = muq_panel[(muq_panel['year'] == yr) & muq_panel['MUQ'].notna()].shape[0]
    flag = ' ** 警告: 覆盖率低' if n < 50 else ''
    rprint(f'  {yr}: {n} 城市{flag}')

# Winsorize MUQ at 1%/99%
muq_valid = muq_panel[muq_panel['MUQ'].notna()].copy()
muq_valid['MUQ_raw'] = muq_valid['MUQ'].copy()
muq_valid['MUQ'] = winsorize(muq_valid['MUQ'], 0.01, 0.99)

rprint(f'\nMUQ 描述统计 (winsorized 1%/99%):')
rprint(f'  N = {len(muq_valid)}')
rprint(f'  Mean = {muq_valid["MUQ"].mean():.4f}')
rprint(f'  Median = {muq_valid["MUQ"].median():.4f}')
rprint(f'  Std = {muq_valid["MUQ"].std():.4f}')
rprint(f'  Min = {muq_valid["MUQ"].min():.4f}')
rprint(f'  Max = {muq_valid["MUQ"].max():.4f}')
rprint(f'  Q25 = {muq_valid["MUQ"].quantile(0.25):.4f}')
rprint(f'  Q75 = {muq_valid["MUQ"].quantile(0.75):.4f}')

# =============================================================================
# Part B: MUQ 分布的时间演化
# =============================================================================
rprint()
rprint('-' * 60)
rprint('Part B: MUQ 分布的时间演化')
rprint('-' * 60)

# B1: 逐年统计
yearly_stats = []
for yr in range(2011, 2017):
    sub = muq_valid[muq_valid['year'] == yr]['MUQ']
    if len(sub) < 5:
        continue
    yearly_stats.append({
        'year': yr,
        'N': len(sub),
        'mean': sub.mean(),
        'median': sub.median(),
        'std': sub.std(),
        'pct_negative': (sub < 0).mean() * 100,
        'n_negative': (sub < 0).sum(),
        'q25': sub.quantile(0.25),
        'q75': sub.quantile(0.75),
    })

ystats = pd.DataFrame(yearly_stats)
rprint()
rprint('逐年 MUQ 分布统计:')
rprint(ystats.to_string(index=False, float_format='%.4f'))

# B2: MUQ < 0 的城市比例趋势
rprint()
rprint('MUQ < 0 城市比例:')
for _, row in ystats.iterrows():
    rprint(f'  {int(row["year"])}: {row["pct_negative"]:.1f}% '
           f'({int(row["n_negative"])}/{int(row["N"])} 城市)')

# B3: Mann-Kendall 检验 (中位数时间趋势)
if len(ystats) >= 4:
    mk_z, mk_p, mk_tau = mann_kendall_test(ystats['median'].values)
    rprint(f'\nMann-Kendall 检验 (MUQ 中位数趋势):')
    rprint(f'  Kendall tau = {mk_tau:.4f}')
    rprint(f'  Z = {mk_z:.4f}')
    rprint(f'  p = {mk_p:.4f}')
    rprint(f'  趋势方向: {"下降" if mk_tau < 0 else "上升"}')
    rprint(f'  结论: {"显著" if mk_p < 0.05 else "不显著"} (alpha = 0.05)')

    # 也对 MUQ 均值做检验
    mk_z2, mk_p2, mk_tau2 = mann_kendall_test(ystats['mean'].values)
    rprint(f'\nMann-Kendall 检验 (MUQ 均值趋势):')
    rprint(f'  Kendall tau = {mk_tau2:.4f}, Z = {mk_z2:.4f}, p = {mk_p2:.4f}')

# B4: 分城市等级分析
# 按人口规模划分城市等级（使用最新一年可用的 pop_10k）
rprint()
rprint('--- 城市分级 (按常住人口) ---')
# 取 2016 年人口
pop_ref = panel[panel['year'] == 2016][['city', 'pop_10k']].dropna()
pop_ref = pop_ref.rename(columns={'pop_10k': 'pop_ref'})

# 一线: >2000万; 新一线: 1000-2000; 二线: 500-1000; 三线: 300-500; 四五线: <300
# 注意 pop_10k 单位是万人
def city_tier(pop):
    if pop >= 2000:
        return '一线(>2000万)'
    elif pop >= 1000:
        return '新一线(1000-2000万)'
    elif pop >= 500:
        return '二线(500-1000万)'
    elif pop >= 300:
        return '三线(300-500万)'
    else:
        return '四五线(<300万)'

pop_ref['tier'] = pop_ref['pop_ref'].apply(city_tier)
rprint(f'城市等级分布:')
rprint(pop_ref['tier'].value_counts().to_string())

muq_valid = muq_valid.merge(pop_ref[['city', 'tier', 'pop_ref']], on='city', how='left')

rprint()
rprint('各等级城市 MUQ 均值 (全年份):')
tier_stats = muq_valid.groupby('tier')['MUQ'].agg(['mean', 'median', 'std', 'count'])
rprint(tier_stats.to_string(float_format='%.4f'))

# =============================================================================
# Part C: MUQ 与投资强度的关系
# =============================================================================
rprint()
rprint('-' * 60)
rprint('Part C: MUQ 与投资强度的关系')
rprint('-' * 60)

# C1: MUQ vs FAI/GDP (投资强度)
muq_valid['fai_gdp'] = muq_valid['fai_gdp_ratio']

# 截面回归: pooled OLS
c1_data = muq_valid[['MUQ', 'fai_gdp', 'city', 'year']].dropna()
rprint(f'\nC1: MUQ vs FAI/GDP (Pooled OLS)')
rprint(f'  N = {len(c1_data)}')
if len(c1_data) > 10:
    model_c1 = robust_ols(c1_data['MUQ'], c1_data['fai_gdp'])
    rprint(f'  beta(FAI/GDP) = {model_c1.params.iloc[1]:.4f}')
    rprint(f'  95% CI = [{model_c1.conf_int().iloc[1, 0]:.4f}, {model_c1.conf_int().iloc[1, 1]:.4f}]')
    rprint(f'  t = {model_c1.tvalues.iloc[1]:.3f}, p = {model_c1.pvalues.iloc[1]:.6f}')
    rprint(f'  R-squared = {model_c1.rsquared:.4f}')

# C2: 分位数回归
rprint()
rprint('C2: MUQ vs FAI/GDP (分位数回归)')
c2_data = muq_valid[['MUQ', 'fai_gdp']].dropna()
if len(c2_data) > 20:
    X_qr = sm.add_constant(c2_data['fai_gdp'])
    for q in [0.10, 0.25, 0.50, 0.75, 0.90]:
        qr = QuantReg(c2_data['MUQ'], X_qr).fit(q=q)
        rprint(f'  Q{int(q*100):02d}: beta = {qr.params.iloc[1]:.4f}, '
               f'95% CI = [{qr.conf_int().iloc[1, 0]:.4f}, {qr.conf_int().iloc[1, 1]:.4f}], '
               f'p = {qr.pvalues.iloc[1]:.6f}')

# C3: 面板固定效应回归
rprint()
rprint('C3: 面板固定效应回归')
rprint('  MUQ(i,t) = alpha + beta*FAI_GDP(i,t) + controls + city_FE + year_FE')

# 准备控制变量
fe_data = muq_valid[['MUQ', 'fai_gdp', 'city', 'year', 'gdp_per_capita',
                      'tertiary_share_pct']].dropna().copy()

if len(fe_data) > 50:
    # 城市和年份固定效应 (用 dummies)
    fe_data['year_str'] = fe_data['year'].astype(str)
    city_dummies = pd.get_dummies(fe_data['city'], drop_first=True, prefix='city', dtype=float)
    year_dummies = pd.get_dummies(fe_data['year_str'], drop_first=True, prefix='yr', dtype=float)

    X_fe = pd.concat([
        fe_data[['fai_gdp', 'gdp_per_capita', 'tertiary_share_pct']],
        city_dummies, year_dummies
    ], axis=1)

    # 标准化连续变量以帮助收敛
    for col in ['gdp_per_capita']:
        X_fe[col] = X_fe[col] / 10000  # 万元转为万

    model_fe = sm.OLS(fe_data['MUQ'], sm.add_constant(X_fe)).fit(
        cov_type='cluster', cov_kwds={'groups': fe_data['city']}
    )

    rprint(f'  N = {model_fe.nobs:.0f}')
    rprint(f'  R-squared = {model_fe.rsquared:.4f}')
    rprint(f'  Adj. R-squared = {model_fe.rsquared_adj:.4f}')
    rprint(f'  核心变量:')
    for var in ['fai_gdp', 'gdp_per_capita', 'tertiary_share_pct']:
        if var in model_fe.params.index:
            idx = list(model_fe.params.index).index(var)
            rprint(f'    {var}: beta = {model_fe.params[var]:.4f}, '
                   f'95% CI = [{model_fe.conf_int().loc[var].iloc[0]:.4f}, {model_fe.conf_int().loc[var].iloc[1]:.4f}], '
                   f'p = {model_fe.pvalues[var]:.6f}')
else:
    rprint(f'  数据不足: N = {len(fe_data)}, 跳过面板回归')

# C3b: 简化版 — 组内去均值 (Mundlak / within estimator)
rprint()
rprint('C3b: Within 估计器 (组内去均值)')
within_data = muq_valid[['MUQ', 'fai_gdp', 'city', 'year', 'gdp_per_capita',
                          'tertiary_share_pct']].dropna().copy()
if len(within_data) > 50:
    for col in ['MUQ', 'fai_gdp', 'gdp_per_capita', 'tertiary_share_pct']:
        city_mean = within_data.groupby('city')[col].transform('mean')
        within_data[f'{col}_dm'] = within_data[col] - city_mean

    year_dummies_w = pd.get_dummies(within_data['year'].astype(str), drop_first=True, prefix='yr', dtype=float)
    X_within = pd.concat([
        within_data[['fai_gdp_dm', 'gdp_per_capita_dm', 'tertiary_share_pct_dm']],
        year_dummies_w
    ], axis=1)

    model_within = sm.OLS(within_data['MUQ_dm'], X_within).fit(
        cov_type='cluster', cov_kwds={'groups': within_data['city']}
    )
    rprint(f'  N = {model_within.nobs:.0f}')
    for var in ['fai_gdp_dm', 'gdp_per_capita_dm', 'tertiary_share_pct_dm']:
        if var in model_within.params.index:
            rprint(f'    {var}: beta = {model_within.params[var]:.4f}, '
                   f'95% CI = [{model_within.conf_int().loc[var].iloc[0]:.4f}, {model_within.conf_int().loc[var].iloc[1]:.4f}], '
                   f'p = {model_within.pvalues[var]:.6f}')

# =============================================================================
# Part D: MUQ 的空间格局
# =============================================================================
rprint()
rprint('-' * 60)
rprint('Part D: MUQ 的空间格局')
rprint('-' * 60)

# D1: 区域分布
rprint()
rprint('D1: 区域 MUQ 分布')
region_stats = muq_valid.groupby('region')['MUQ'].agg(['mean', 'median', 'std', 'count'])
rprint(region_stats.to_string(float_format='%.4f'))

# 区域间差异检验 (Kruskal-Wallis)
regions = muq_valid['region'].dropna().unique()
region_groups = [muq_valid[muq_valid['region'] == r]['MUQ'].values for r in regions]
region_groups = [g for g in region_groups if len(g) > 5]
if len(region_groups) >= 2:
    kw_stat, kw_p = stats.kruskal(*region_groups)
    rprint(f'\nKruskal-Wallis 检验 (区域差异):')
    rprint(f'  H = {kw_stat:.3f}, p = {kw_p:.6f}')

# D2: 城市规模梯度
rprint()
rprint('D2: 城市规模与 MUQ')
# MUQ vs log(population)
pop_data = muq_valid[['MUQ', 'pop_ref']].dropna()
if len(pop_data) > 20:
    pop_data['log_pop'] = np.log(pop_data['pop_ref'])
    model_pop = robust_ols(pop_data['MUQ'], pop_data['log_pop'])
    rprint(f'  MUQ ~ log(population): beta = {model_pop.params.iloc[1]:.4f}, '
           f'95% CI = [{model_pop.conf_int().iloc[1, 0]:.4f}, {model_pop.conf_int().iloc[1, 1]:.4f}], '
           f'p = {model_pop.pvalues.iloc[1]:.6f}, R2 = {model_pop.rsquared:.4f}')

# D3: Q 水平与 MUQ 的关系
rprint()
rprint('D3: Q 水平与 MUQ')
q_data = muq_valid[['MUQ', 'urban_q']].dropna()
if len(q_data) > 20:
    model_q = robust_ols(q_data['MUQ'], q_data['urban_q'])
    rprint(f'  MUQ ~ urban_q: beta = {model_q.params.iloc[1]:.4f}, '
           f'95% CI = [{model_q.conf_int().iloc[1, 0]:.4f}, {model_q.conf_int().iloc[1, 1]:.4f}], '
           f'p = {model_q.pvalues.iloc[1]:.6f}, R2 = {model_q.rsquared:.4f}')

# =============================================================================
# Part E: 预测性检验 (Out-of-sample)
# =============================================================================
rprint()
rprint('-' * 60)
rprint('Part E: 预测性检验')
rprint('-' * 60)

# 用 2011-2013 的城市特征预测 2014-2016 的 Q 变化
# 计算每个城市的特征
early = muq_valid[muq_valid['year'].isin([2011, 2012, 2013])].copy()
late = panel[panel['year'].isin([2014, 2015, 2016])].copy()

if len(early) > 20 and len(late) > 20:
    # 早期城市特征
    early_feat = early.groupby('city').agg({
        'MUQ': 'mean',
        'fai_gdp': 'mean',
    }).rename(columns={'MUQ': 'muq_early', 'fai_gdp': 'fai_gdp_early'})

    # 早期 Q 均值
    early_q = panel[panel['year'].isin([2011, 2012, 2013])].groupby('city')['urban_q'].mean()
    early_feat['q_early'] = early_q

    # 后期 Q 变化
    q_2013 = panel[panel['year'] == 2013].set_index('city')['urban_q']
    q_2016 = panel[panel['year'] == 2016].set_index('city')['urban_q']
    delta_q = (q_2016 - q_2013).dropna()
    delta_q.name = 'delta_q'

    pred_data = early_feat.join(delta_q, how='inner').dropna()
    rprint(f'可用于预测的城市数: {len(pred_data)}')

    if len(pred_data) > 15:
        X_pred = pred_data[['muq_early', 'fai_gdp_early', 'q_early']]
        y_pred = pred_data['delta_q']

        # 样本内拟合
        model_pred = robust_ols(y_pred, X_pred)
        rprint(f'\nOLS: delta_Q(2013-2016) ~ MUQ_early + FAI_GDP_early + Q_early')
        rprint(f'  N = {model_pred.nobs:.0f}')
        rprint(f'  R-squared = {model_pred.rsquared:.4f}')
        rprint(f'  Adj. R-squared = {model_pred.rsquared_adj:.4f}')
        for var in ['muq_early', 'fai_gdp_early', 'q_early']:
            rprint(f'  {var}: beta = {model_pred.params[var]:.4f}, '
                   f'p = {model_pred.pvalues[var]:.6f}')

        # Leave-one-out 交叉验证 R2
        lr = LinearRegression()
        cv_scores = cross_val_score(lr, X_pred, y_pred, cv=min(5, len(pred_data)),
                                     scoring='r2')
        rprint(f'\n5-fold CV R-squared: {cv_scores.mean():.4f} (std = {cv_scores.std():.4f})')
else:
    rprint('数据不足，跳过预测检验')

# =============================================================================
# Part F: 重点年份深度分析 — 2016 截面 (213 城市)
# =============================================================================
rprint()
rprint('-' * 60)
rprint('Part F: 2016 截面深度分析 (最大样本)')
rprint('-' * 60)

muq_2016 = muq_valid[muq_valid['year'] == 2016].copy()
rprint(f'2016 年 MUQ 有效样本: {len(muq_2016)} 城市')

if len(muq_2016) > 20:
    rprint(f'  Mean = {muq_2016["MUQ"].mean():.4f}')
    rprint(f'  Median = {muq_2016["MUQ"].median():.4f}')
    rprint(f'  Std = {muq_2016["MUQ"].std():.4f}')
    rprint(f'  MUQ < 0: {(muq_2016["MUQ"] < 0).sum()}/{len(muq_2016)} '
           f'({(muq_2016["MUQ"] < 0).mean()*100:.1f}%)')
    rprint(f'  MUQ < 1: {(muq_2016["MUQ"] < 1).sum()}/{len(muq_2016)} '
           f'({(muq_2016["MUQ"] < 1).mean()*100:.1f}%)')

    # 单样本 t 检验: MUQ 是否显著不同于 1 (盈亏平衡点)
    t_stat, t_p = stats.ttest_1samp(muq_2016['MUQ'].dropna(), 1.0)
    rprint(f'\n单样本 t 检验 (H0: MUQ = 1):')
    rprint(f'  t = {t_stat:.3f}, p = {t_p:.6f}')
    rprint(f'  均值 95% CI: [{muq_2016["MUQ"].mean() - 1.96*muq_2016["MUQ"].std()/np.sqrt(len(muq_2016)):.4f}, '
           f'{muq_2016["MUQ"].mean() + 1.96*muq_2016["MUQ"].std()/np.sqrt(len(muq_2016)):.4f}]')

    # 2016 区域差异
    rprint('\n2016 区域 MUQ:')
    for r in sorted(muq_2016['region'].dropna().unique()):
        rsub = muq_2016[muq_2016['region'] == r]['MUQ']
        rprint(f'  {r}: mean={rsub.mean():.4f}, median={rsub.median():.4f}, '
               f'N={len(rsub)}, MUQ<0: {(rsub<0).sum()} ({(rsub<0).mean()*100:.1f}%)')

    # 2016 等级差异
    rprint('\n2016 城市等级 MUQ:')
    for t in ['一线(>2000万)', '新一线(1000-2000万)', '二线(500-1000万)',
              '三线(300-500万)', '四五线(<300万)']:
        tsub = muq_2016[muq_2016['tier'] == t]['MUQ']
        if len(tsub) > 0:
            rprint(f'  {t}: mean={tsub.mean():.4f}, median={tsub.median():.4f}, '
                   f'N={len(tsub)}, MUQ<0: {(tsub<0).sum()} ({(tsub<0).mean()*100:.1f}%)')

# =============================================================================
# 图表绘制
# =============================================================================
rprint()
rprint('-' * 60)
rprint('生成图表...')
rprint('-' * 60)

# 设置全局字体 — 支持中文
plt.rcParams['font.family'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 9

fig = plt.figure(figsize=(16, 14))
gs = gridspec.GridSpec(3, 2, hspace=0.35, wspace=0.30,
                       left=0.08, right=0.95, top=0.95, bottom=0.06)

# --- Panel (a): MUQ 分布逐年演化 ---
ax_a = fig.add_subplot(gs[0, 0])
colors_yr = plt.cm.RdYlBu_r(np.linspace(0.15, 0.85, 6))
years_plot = range(2011, 2017)
for i, yr in enumerate(years_plot):
    sub = muq_valid[muq_valid['year'] == yr]['MUQ']
    if len(sub) < 5:
        continue
    # KDE if enough data
    try:
        from scipy.stats import gaussian_kde
        kde = gaussian_kde(sub.values, bw_method=0.3)
        x_range = np.linspace(sub.quantile(0.01), sub.quantile(0.99), 200)
        ax_a.plot(x_range, kde(x_range), color=colors_yr[i], lw=1.8,
                  label=f'{yr} (N={len(sub)})', alpha=0.85)
        ax_a.fill_between(x_range, kde(x_range), alpha=0.08, color=colors_yr[i])
    except Exception:
        ax_a.hist(sub, bins=30, density=True, alpha=0.4, color=colors_yr[i],
                  label=f'{yr} (N={len(sub)})')

ax_a.axvline(x=0, color='red', ls='--', lw=1, alpha=0.7)
ax_a.axvline(x=1, color='gray', ls=':', lw=1, alpha=0.5)
ax_a.set_xlabel('MUQ (Marginal Urban Q)')
ax_a.set_ylabel('Density')
ax_a.set_title('(a) MUQ Distribution by Year (2011-2016)')
ax_a.legend(fontsize=7, loc='upper right')

# --- Panel (b): MUQ < 0 比例 + 中位数时间趋势 ---
ax_b = fig.add_subplot(gs[0, 1])
ax_b2 = ax_b.twinx()

if len(ystats) > 0:
    ax_b.bar(ystats['year'], ystats['pct_negative'], color='#e74c3c', alpha=0.6,
             width=0.4, label='% cities with MUQ < 0')
    ax_b.set_ylabel('% cities with MUQ < 0', color='#e74c3c')
    ax_b.tick_params(axis='y', labelcolor='#e74c3c')

    ax_b2.plot(ystats['year'], ystats['median'], 'o-', color='#2c3e50', lw=2,
               markersize=6, label='Median MUQ')
    ax_b2.fill_between(ystats['year'], ystats['q25'], ystats['q75'],
                        alpha=0.15, color='#2c3e50')
    ax_b2.axhline(y=0, color='red', ls='--', lw=0.8, alpha=0.5)
    ax_b2.axhline(y=1, color='gray', ls=':', lw=0.8, alpha=0.5)
    ax_b2.set_ylabel('MUQ (median, IQR)', color='#2c3e50')
    ax_b2.tick_params(axis='y', labelcolor='#2c3e50')

    # 标注样本量
    for _, row in ystats.iterrows():
        ax_b.annotate(f'N={int(row["N"])}', (row['year'], row['pct_negative'] + 1),
                      ha='center', fontsize=6, color='gray')

ax_b.set_xlabel('Year')
ax_b.set_title('(b) MUQ < 0 Share & Median Trend')

# --- Panel (c): MUQ vs FAI/GDP 散点图 ---
ax_c = fig.add_subplot(gs[1, 0])
scatter_data = muq_valid[['MUQ', 'fai_gdp', 'year', 'region']].dropna()

if len(scatter_data) > 10:
    # 按区域着色
    region_colors = {'东部': '#3498db', '中部': '#2ecc71', '西部': '#e67e22'}
    for r, color in region_colors.items():
        rsub = scatter_data[scatter_data['region'] == r]
        ax_c.scatter(rsub['fai_gdp'], rsub['MUQ'], c=color, alpha=0.35,
                     s=15, label=f'{r} (N={len(rsub)})', edgecolors='none')

    # 拟合线
    x_fit = np.linspace(scatter_data['fai_gdp'].quantile(0.02),
                         scatter_data['fai_gdp'].quantile(0.98), 100)
    z = np.polyfit(scatter_data['fai_gdp'], scatter_data['MUQ'], 1)
    ax_c.plot(x_fit, np.polyval(z, x_fit), 'k-', lw=2, alpha=0.7)

    # 分位数回归线
    X_qr_plot = sm.add_constant(scatter_data['fai_gdp'])
    for q, ls in [(0.25, ':'), (0.75, ':')]:
        try:
            qr = QuantReg(scatter_data['MUQ'], X_qr_plot).fit(q=q)
            ax_c.plot(x_fit, qr.params.iloc[0] + qr.params.iloc[1] * x_fit,
                      ls=ls, color='gray', lw=1, alpha=0.6)
        except Exception:
            pass

    ax_c.axhline(y=0, color='red', ls='--', lw=0.8, alpha=0.5)
    ax_c.axhline(y=1, color='gray', ls=':', lw=0.8, alpha=0.3)

ax_c.set_xlabel('FAI / GDP')
ax_c.set_ylabel('MUQ')
ax_c.set_title('(c) MUQ vs Investment Intensity')
ax_c.legend(fontsize=7, loc='upper right')

# --- Panel (d): 区域/等级梯度 ---
ax_d = fig.add_subplot(gs[1, 1])
tier_order = ['一线(>2000万)', '新一线(1000-2000万)', '二线(500-1000万)',
              '三线(300-500万)', '四五线(<300万)']
tier_labels_short = ['Tier-1\n(>20M)', 'New T-1\n(10-20M)', 'Tier-2\n(5-10M)',
                     'Tier-3\n(3-5M)', 'Tier-4/5\n(<3M)']

bp_data = []
bp_labels = []
for i, t in enumerate(tier_order):
    d = muq_valid[muq_valid['tier'] == t]['MUQ'].dropna()
    if len(d) > 3:
        bp_data.append(d.values)
        bp_labels.append(tier_labels_short[i])

if bp_data:
    bplot = ax_d.boxplot(bp_data, tick_labels=bp_labels, patch_artist=True,
                         widths=0.5, showfliers=False,
                         medianprops=dict(color='black', lw=1.5))
    colors_tier = ['#e74c3c', '#e67e22', '#3498db', '#2ecc71', '#95a5a6']
    for patch, color in zip(bplot['boxes'], colors_tier[:len(bp_data)]):
        patch.set_facecolor(color)
        patch.set_alpha(0.5)

    # 标注 N
    for i, d in enumerate(bp_data):
        ax_d.annotate(f'N={len(d)}', (i + 1, ax_d.get_ylim()[1] * 0.95),
                      ha='center', fontsize=6, color='gray')

ax_d.axhline(y=0, color='red', ls='--', lw=0.8, alpha=0.5)
ax_d.axhline(y=1, color='gray', ls=':', lw=0.8, alpha=0.3)
ax_d.set_ylabel('MUQ')
ax_d.set_title('(d) MUQ by City Tier (population)')

# --- Panel (e): 区域分布 ---
ax_e = fig.add_subplot(gs[2, 0])
region_order = ['东部', '中部', '西部']
region_labels_en = ['East', 'Central', 'West']
region_colors_box = ['#3498db', '#2ecc71', '#e67e22']

bp_data_r = []
bp_labels_r = []
for i, r in enumerate(region_order):
    d = muq_valid[muq_valid['region'] == r]['MUQ'].dropna()
    if len(d) > 3:
        bp_data_r.append(d.values)
        bp_labels_r.append(region_labels_en[i])

if bp_data_r:
    bplot_r = ax_e.boxplot(bp_data_r, tick_labels=bp_labels_r, patch_artist=True,
                            widths=0.5, showfliers=False,
                            medianprops=dict(color='black', lw=1.5))
    for patch, color in zip(bplot_r['boxes'], region_colors_box[:len(bp_data_r)]):
        patch.set_facecolor(color)
        patch.set_alpha(0.5)

    for i, d in enumerate(bp_data_r):
        ax_e.annotate(f'N={len(d)}\nMUQ<0: {(d<0).sum()}',
                      (i + 1, ax_e.get_ylim()[0] + 0.05 * (ax_e.get_ylim()[1] - ax_e.get_ylim()[0])),
                      ha='center', fontsize=6, color='gray')

ax_e.axhline(y=0, color='red', ls='--', lw=0.8, alpha=0.5)
ax_e.axhline(y=1, color='gray', ls=':', lw=0.8, alpha=0.3)
ax_e.set_ylabel('MUQ')
ax_e.set_title('(e) MUQ by Region')

# --- Panel (f): 2016 截面 MUQ vs Q ---
ax_f = fig.add_subplot(gs[2, 1])
qmuq = muq_2016[['MUQ', 'urban_q', 'fai_gdp']].dropna() if len(muq_2016) > 0 else pd.DataFrame()

if len(qmuq) > 10:
    sc = ax_f.scatter(qmuq['urban_q'], qmuq['MUQ'],
                      c=qmuq['fai_gdp'], cmap='RdYlBu_r',
                      alpha=0.6, s=20, edgecolors='gray', linewidths=0.3)
    plt.colorbar(sc, ax=ax_f, label='FAI/GDP', shrink=0.8)

    # 拟合线
    z2 = np.polyfit(qmuq['urban_q'], qmuq['MUQ'], 1)
    x_fit2 = np.linspace(qmuq['urban_q'].quantile(0.02),
                          qmuq['urban_q'].quantile(0.98), 100)
    ax_f.plot(x_fit2, np.polyval(z2, x_fit2), 'k-', lw=2, alpha=0.7)

    ax_f.axhline(y=0, color='red', ls='--', lw=0.8, alpha=0.5)
    ax_f.axvline(x=1, color='gray', ls=':', lw=0.8, alpha=0.3)

ax_f.set_xlabel('Urban Q (V/K)')
ax_f.set_ylabel('MUQ (dV/I)')
ax_f.set_title('(f) MUQ vs Q Level (2016 cross-section)')

plt.savefig(FIG_PATH, dpi=200, bbox_inches='tight')
plt.close()
rprint(f'图表已保存: {FIG_PATH}')

# =============================================================================
# 保存报告
# =============================================================================
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
rprint(f'\n报告已保存: {REPORT_PATH}')

print('\n=== 分析完成 ===')
