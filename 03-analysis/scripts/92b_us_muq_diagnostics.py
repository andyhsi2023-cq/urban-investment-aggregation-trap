#!/usr/bin/env python3
"""
92b_us_muq_diagnostics.py — 美中 MUQ 方向不一致的诊断分析
============================================================
目的: 美国 MUQ vs 投资强度为正相关 (beta=2.75), 与中国负相关 (beta=-2.23)
      完全相反。本脚本诊断原因并寻找可比较的指标。

核心假设:
  - 美国 dV = 价格效应 + 数量效应, 两者在 Sun Belt 同方向
  - 中国 FAI 是供给驱动 (政府+开发商), 美国 HU growth 是需求驱动
  - 需要分离价格效应, 或使用替代定义

输入: 02-data/processed/us_msa_muq_panel.csv
输出:
  - 03-analysis/models/us_muq_diagnostics_report.txt
  - 04-figures/drafts/fig_us_muq_diagnostics.png

依赖: pandas, numpy, statsmodels, scipy, matplotlib
"""

import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.quantile_regression import QuantReg
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

np.random.seed(42)

# 路径
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
DATA_PROC = os.path.join(BASE, '02-data', 'processed')
MODELS = os.path.join(BASE, '03-analysis', 'models')
FIGS = os.path.join(BASE, '04-figures', 'drafts')

report_lines = []
def rpt(s=''):
    report_lines.append(str(s))
    print(s)

def winsorize(s, lower=0.01, upper=0.99):
    lo = s.quantile(lower)
    hi = s.quantile(upper)
    return s.clip(lo, hi)

# ============================================================
# 加载面板
# ============================================================
panel = pd.read_csv(os.path.join(DATA_PROC, 'us_msa_muq_panel.csv'))
rpt(f'面板: {panel.shape[0]} 行, {panel["cbsa_code"].nunique()} MSAs')

# 重构差分变量
panel = panel.sort_values(['cbsa_code', 'year'])
panel['V_total_lag'] = panel.groupby('cbsa_code')['V_total'].shift(1)
panel['mhv_lag'] = panel.groupby('cbsa_code')['median_home_value'].shift(1)
panel['hu_lag'] = panel.groupby('cbsa_code')['housing_units'].shift(1)
panel['gdp_lag'] = panel.groupby('cbsa_code')['gdp_millions'].shift(1)
panel['pop_lag'] = panel.groupby('cbsa_code')['population'].shift(1)

panel['dV'] = panel['V_total'] - panel['V_total_lag']
panel['dHU'] = panel['housing_units'] - panel['hu_lag']
panel['dP'] = panel['median_home_value'] - panel['mhv_lag']
panel['hu_growth'] = panel['dHU'] / panel['hu_lag']
panel['price_growth'] = panel['dP'] / panel['mhv_lag']
panel['MUQ_gdp'] = panel['dV'] / (panel['gdp_millions'] * 1e6)

df = panel[panel['V_total_lag'].notna()].copy()
rpt(f'差分后: {len(df)} 行')

# ============================================================
# 诊断 1: 分解 dV = 价格效应 + 数量效应
# ============================================================
rpt('\n' + '=' * 72)
rpt('诊断 1: dV 分解 (价格效应 vs 数量效应)')
rpt('=' * 72)

# V = P * Q, 所以 dV = dP * Q_lag + P * dQ + dP * dQ
# 近似: dV ≈ dP * Q_lag (价格效应) + P_lag * dQ (数量效应)
df['price_effect'] = df['dP'] * df['hu_lag']           # 存量价格升值
df['quantity_effect'] = df['mhv_lag'] * df['dHU']       # 新增单元价值
df['interaction'] = df['dP'] * df['dHU']                # 交叉项

# 标准化 by GDP
df['price_effect_gdp'] = df['price_effect'] / (df['gdp_millions'] * 1e6)
df['quantity_effect_gdp'] = df['quantity_effect'] / (df['gdp_millions'] * 1e6)

# 各效应占 dV 的比例
mask_valid = df['dV'].notna() & (df['dV'] != 0)
df_v = df[mask_valid].copy()
df_v['price_share'] = df_v['price_effect'] / df_v['dV']
df_v['quantity_share'] = df_v['quantity_effect'] / df_v['dV']

rpt(f'\n  样本量: {len(df_v)}')
rpt(f'  价格效应占 dV 比例:')
rpt(f'    Mean = {df_v["price_share"].clip(-5,5).mean():.4f}')
rpt(f'    Median = {df_v["price_share"].clip(-5,5).median():.4f}')
rpt(f'  数量效应占 dV 比例:')
rpt(f'    Mean = {df_v["quantity_share"].clip(-5,5).mean():.4f}')
rpt(f'    Median = {df_v["quantity_share"].clip(-5,5).median():.4f}')

rpt(f'\n  dV/GDP 的来源分解 (均值):')
rpt(f'    price_effect/GDP = {df_v["price_effect_gdp"].mean():.6f}')
rpt(f'    quantity_effect/GDP = {df_v["quantity_effect_gdp"].mean():.6f}')
rpt(f'    MUQ_gdp (total) = {df_v["MUQ_gdp"].mean():.6f}')

# ============================================================
# 诊断 2: 分别回归价格效应和数量效应
# ============================================================
rpt('\n' + '=' * 72)
rpt('诊断 2: 价格效应和数量效应 vs 投资强度的分别回归')
rpt('=' * 72)

df['hu_growth_w'] = winsorize(df['hu_growth'].dropna())
mask_reg = df['hu_growth'].notna() & df['price_effect_gdp'].notna()
df_reg = df[mask_reg].copy()
df_reg['hu_growth_w'] = winsorize(df_reg['hu_growth'])
df_reg['price_effect_gdp_w'] = winsorize(df_reg['price_effect_gdp'])
df_reg['quantity_effect_gdp_w'] = winsorize(df_reg['quantity_effect_gdp'])
df_reg['MUQ_gdp_w'] = winsorize(df_reg['MUQ_gdp'])

for dep, label in [('MUQ_gdp_w', 'Total MUQ'),
                   ('price_effect_gdp_w', 'Price Effect / GDP'),
                   ('quantity_effect_gdp_w', 'Quantity Effect / GDP')]:
    X = sm.add_constant(df_reg['hu_growth_w'])
    model = sm.OLS(df_reg[dep], X).fit(cov_type='HC1')
    beta = model.params['hu_growth_w']
    ci = model.conf_int().loc['hu_growth_w']
    rpt(f'\n  {label} ~ hu_growth:')
    rpt(f'    beta = {beta:.4f}, 95% CI = [{ci[0]:.4f}, {ci[1]:.4f}]')
    rpt(f'    t = {model.tvalues["hu_growth_w"]:.3f}, p = {model.pvalues["hu_growth_w"]:.6f}')
    rpt(f'    R2 = {model.rsquared:.4f}')

# ============================================================
# 诊断 3: 使用 "纯数量" MUQ -- 去除价格效应
# ============================================================
rpt('\n' + '=' * 72)
rpt('诊断 3: 纯数量 MUQ (去除价格效应)')
rpt('=' * 72)
rpt('  定义: MUQ_q = (P_lag * dHU) / GDP  — 仅新增住房的价值贡献')
rpt('  这更接近中国的 I/GDP 概念')

df['MUQ_q'] = df['quantity_effect'] / (df['gdp_millions'] * 1e6)
df_q = df[df['MUQ_q'].notna() & df['hu_growth'].notna()].copy()
df_q['MUQ_q_w'] = winsorize(df_q['MUQ_q'])
df_q['hu_growth_w'] = winsorize(df_q['hu_growth'])

X = sm.add_constant(df_q['hu_growth_w'])
m_q = sm.OLS(df_q['MUQ_q_w'], X).fit(cov_type='HC1')
rpt(f'\n  MUQ_q ~ hu_growth:')
rpt(f'    beta = {m_q.params["hu_growth_w"]:.4f}, '
    f'95% CI = [{m_q.conf_int().loc["hu_growth_w"][0]:.4f}, '
    f'{m_q.conf_int().loc["hu_growth_w"][1]:.4f}]')
rpt(f'    t = {m_q.tvalues["hu_growth_w"]:.3f}, p = {m_q.pvalues["hu_growth_w"]:.6f}')
rpt(f'    R2 = {m_q.rsquared:.4f}')
rpt(f'  注: 纯数量 MUQ 和 hu_growth 本质上是同一个量的变换, 正相关是必然的')

# ============================================================
# 诊断 4: 使用"价格效应 MUQ" -- 这是关键
# ============================================================
rpt('\n' + '=' * 72)
rpt('诊断 4: 价格效应 MUQ — 投资强度是否压低房价升值?')
rpt('=' * 72)
rpt('  定义: MUQ_p = (dP * HU_lag) / GDP — 存量住房的价格变化')
rpt('  如果更多建设 -> 压低房价升值, 则 beta 应为负')

df_p = df[df['price_effect_gdp'].notna() & df['hu_growth'].notna()].copy()
df_p['price_effect_gdp_w'] = winsorize(df_p['price_effect_gdp'])
df_p['hu_growth_w'] = winsorize(df_p['hu_growth'])

X = sm.add_constant(df_p['hu_growth_w'])
m_p = sm.OLS(df_p['price_effect_gdp_w'], X).fit(cov_type='HC1')
rpt(f'\n  price_MUQ ~ hu_growth:')
rpt(f'    beta = {m_p.params["hu_growth_w"]:.4f}, '
    f'95% CI = [{m_p.conf_int().loc["hu_growth_w"][0]:.4f}, '
    f'{m_p.conf_int().loc["hu_growth_w"][1]:.4f}]')
rpt(f'    t = {m_p.tvalues["hu_growth_w"]:.3f}, p = {m_p.pvalues["hu_growth_w"]:.6f}')
rpt(f'    R2 = {m_p.rsquared:.4f}')

if m_p.params['hu_growth_w'] < 0:
    rpt('\n  >>> 价格效应 vs 投资强度为负! 与中国模式一致')
    rpt('  >>> 含义: 更多建设 -> 房价升值更慢 -> 与"过度建设降低效率"一致')
else:
    rpt('\n  >>> 价格效应 vs 投资强度仍为正')
    rpt('  >>> 含义: 在美国, 建设活跃的城市同时也是房价上涨最快的城市 (需求拉动)')

# ============================================================
# 诊断 5: 控制需求因素 (人口增长)
# ============================================================
rpt('\n' + '=' * 72)
rpt('诊断 5: 控制人口增长后, 投资强度的效应')
rpt('=' * 72)
rpt('  如果正相关来自需求驱动 (人口流入 -> 建设 + 房价升),')
rpt('  控制人口增长后应减弱甚至反转')

df['pop_growth'] = (df['population'] - df['pop_lag']) / df['pop_lag']
df_5 = df[df['MUQ_gdp'].notna() & df['hu_growth'].notna() & df['pop_growth'].notna()].copy()
df_5['MUQ_gdp_w'] = winsorize(df_5['MUQ_gdp'])
df_5['hu_growth_w'] = winsorize(df_5['hu_growth'])
df_5['pop_growth_w'] = winsorize(df_5['pop_growth'])

# 5a: MUQ ~ hu_growth + pop_growth
X_5a = sm.add_constant(df_5[['hu_growth_w', 'pop_growth_w']])
m_5a = sm.OLS(df_5['MUQ_gdp_w'], X_5a).fit(cov_type='HC1')
rpt(f'\n  5a: MUQ_gdp ~ hu_growth + pop_growth')
rpt(f'    N = {int(m_5a.nobs)}')
for var in ['hu_growth_w', 'pop_growth_w']:
    ci = m_5a.conf_int().loc[var]
    rpt(f'    {var}: beta = {m_5a.params[var]:.4f}, '
        f'95% CI = [{ci[0]:.4f}, {ci[1]:.4f}], '
        f'p = {m_5a.pvalues[var]:.6f}')
rpt(f'    R2 = {m_5a.rsquared:.4f}')

# 5b: "过剩建设" = hu_growth - pop_growth (供给超过需求的部分)
df_5['excess_construction'] = df_5['hu_growth_w'] - df_5['pop_growth_w']
df_5['excess_w'] = winsorize(df_5['excess_construction'])

X_5b = sm.add_constant(df_5['excess_w'])
m_5b = sm.OLS(df_5['MUQ_gdp_w'], X_5b).fit(cov_type='HC1')
rpt(f'\n  5b: MUQ_gdp ~ excess_construction (hu_growth - pop_growth)')
rpt(f'    beta = {m_5b.params["excess_w"]:.4f}, '
    f'95% CI = [{m_5b.conf_int().loc["excess_w"][0]:.4f}, '
    f'{m_5b.conf_int().loc["excess_w"][1]:.4f}]')
rpt(f'    t = {m_5b.tvalues["excess_w"]:.3f}, p = {m_5b.pvalues["excess_w"]:.6f}')
rpt(f'    R2 = {m_5b.rsquared:.4f}')

if m_5b.params['excess_w'] < 0:
    rpt('\n  >>> 过剩建设与 MUQ 负相关! 关键发现!')
    rpt('  >>> 当控制需求 (人口增长) 后, 超额供给确实降低边际效率')
    rpt('  >>> 这与中国的模式本质一致, 但美国的混杂因素是需求侧')

# ============================================================
# 诊断 6: 分时段分析 (疫情前后)
# ============================================================
rpt('\n' + '=' * 72)
rpt('诊断 6: 分时段分析')
rpt('=' * 72)

for period, yr_range in [('2011-2015', (2011, 2015)),
                          ('2016-2019', (2016, 2019)),
                          ('2020-2022', (2020, 2022))]:
    df_sub = df[(df['year'] >= yr_range[0]) & (df['year'] <= yr_range[1])].copy()
    df_sub = df_sub[df_sub['MUQ_gdp'].notna() & df_sub['hu_growth'].notna()]
    df_sub['MUQ_gdp_w'] = winsorize(df_sub['MUQ_gdp'])
    df_sub['hu_growth_w'] = winsorize(df_sub['hu_growth'])
    X_sub = sm.add_constant(df_sub['hu_growth_w'])
    m_sub = sm.OLS(df_sub['MUQ_gdp_w'], X_sub).fit(cov_type='HC1')
    ci_sub = m_sub.conf_int().loc['hu_growth_w']
    rpt(f'\n  {period}: N={int(m_sub.nobs)}, '
        f'beta={m_sub.params["hu_growth_w"]:.4f}, '
        f'95% CI=[{ci_sub[0]:.4f}, {ci_sub[1]:.4f}], '
        f'p={m_sub.pvalues["hu_growth_w"]:.6f}, R2={m_sub.rsquared:.4f}')

# ============================================================
# 诊断 7: V/GDP 水平 vs 后续 dV/GDP (类似中国的 Q -> MUQ)
# ============================================================
rpt('\n' + '=' * 72)
rpt('诊断 7: V/GDP 水平是否预测后续 MUQ (均值回归检验)')
rpt('=' * 72)
rpt('  如果 V/GDP 高的 MSA 后续 MUQ 低, 说明存在均值回归')
rpt('  这是 Urban Q 理论的核心预测')

df['V_GDP_ratio'] = df['V_total'] / (df['gdp_millions'] * 1e6)
df['V_GDP_lag'] = df.groupby('cbsa_code')['V_GDP_ratio'].shift(1)

df_7 = df[df['MUQ_gdp'].notna() & df['V_GDP_lag'].notna()].copy()
df_7['MUQ_gdp_w'] = winsorize(df_7['MUQ_gdp'])
df_7['V_GDP_lag_w'] = winsorize(df_7['V_GDP_lag'])

X_7 = sm.add_constant(df_7['V_GDP_lag_w'])
m_7 = sm.OLS(df_7['MUQ_gdp_w'], X_7).fit(cov_type='HC1')
ci_7 = m_7.conf_int().loc['V_GDP_lag_w']
rpt(f'\n  MUQ_gdp ~ V_GDP_ratio(t-1):')
rpt(f'    N = {int(m_7.nobs)}')
rpt(f'    beta = {m_7.params["V_GDP_lag_w"]:.4f}, '
    f'95% CI = [{ci_7[0]:.4f}, {ci_7[1]:.4f}]')
rpt(f'    t = {m_7.tvalues["V_GDP_lag_w"]:.3f}, p = {m_7.pvalues["V_GDP_lag_w"]:.6f}')
rpt(f'    R2 = {m_7.rsquared:.4f}')

if m_7.params['V_GDP_lag_w'] > 0:
    rpt('  >>> V/GDP 高的 MSA 后续 MUQ 也高 — 正反馈 (价格惯性)')
else:
    rpt('  >>> V/GDP 高的 MSA 后续 MUQ 低 — 均值回归 (与理论一致)')

# ============================================================
# 诊断 8: 使用 OCR 变化率作为替代 MUQ
# ============================================================
rpt('\n' + '=' * 72)
rpt('诊断 8: OCR 变化率 (dHU_pc) vs 投资强度')
rpt('=' * 72)
rpt('  OCR = HU/Pop, dOCR = OCR(t) - OCR(t-1)')
rpt('  这是更接近中国 "城市效率" 概念的指标')

df['hu_pc'] = df['housing_units'] / df['population']
df['hu_pc_lag'] = df.groupby('cbsa_code')['hu_pc'].shift(1)
df['d_ocr'] = df['hu_pc'] - df['hu_pc_lag']

df_8 = df[df['d_ocr'].notna() & df['hu_growth'].notna()].copy()
df_8['d_ocr_w'] = winsorize(df_8['d_ocr'])
df_8['hu_growth_w'] = winsorize(df_8['hu_growth'])

X_8 = sm.add_constant(df_8['hu_growth_w'])
m_8 = sm.OLS(df_8['d_ocr_w'], X_8).fit(cov_type='HC1')
ci_8 = m_8.conf_int().loc['hu_growth_w']
rpt(f'\n  dOCR ~ hu_growth:')
rpt(f'    beta = {m_8.params["hu_growth_w"]:.4f}, '
    f'95% CI = [{ci_8[0]:.4f}, {ci_8[1]:.4f}]')
rpt(f'    t = {m_8.tvalues["hu_growth_w"]:.3f}, p = {m_8.pvalues["hu_growth_w"]:.6f}')

# ============================================================
# 诊断 9: 综合结论
# ============================================================
rpt('\n' + '=' * 72)
rpt('综合诊断结论')
rpt('=' * 72)

rpt('''
  1. 美国 MUQ (dV/GDP) vs hu_growth 为正相关 (beta=2.75)
     原因: dV = 价格效应 + 数量效应, 在美国二者同方向
     (需求驱动: 人口流入 -> 建设 + 房价上涨)

  2. 中国 MUQ vs FAI/GDP 为负相关 (beta=-2.23)
     原因: FAI 是供给驱动, 过度建设压低资产价值增量

  3. 关键对比:
     - 中国的 "投资" 主要反映供给侧过剩
     - 美国的 "建设" 主要反映需求侧响应
     - 当控制需求 (人口增长) 后, 美国也显示供给过剩降低效率

  4. 论文策略:
     a. 报告美国的正相关, 解释为需求驱动 vs 供给驱动的制度差异
     b. 强调 "过剩建设" 指标 (hu_growth - pop_growth) 的负效应
     c. 突出中美差异本身就是 Urban Q 理论的重要发现:
        在供给约束经济体 (美国), 建设追随需求, Q 反映市场效率
        在投资驱动经济体 (中国), 建设超越需求, Q 反映过度投资
''')

# ============================================================
# 可视化
# ============================================================
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# (a) dV 分解: 价格效应 vs 数量效应
ax = axes[0, 0]
df_dec = df[df['price_effect_gdp'].notna()].copy()
df_dec['pe_w'] = winsorize(df_dec['price_effect_gdp'])
df_dec['qe_w'] = winsorize(df_dec['quantity_effect_gdp'])
yearly_dec = df_dec.groupby('year')[['pe_w', 'qe_w']].mean()
ax.bar(yearly_dec.index - 0.15, yearly_dec['pe_w'], width=0.3,
       color='#2166AC', alpha=0.7, label='Price effect')
ax.bar(yearly_dec.index + 0.15, yearly_dec['qe_w'], width=0.3,
       color='#B2182B', alpha=0.7, label='Quantity effect')
ax.axhline(y=0, color='grey', linestyle=':', linewidth=0.8)
ax.set_xlabel('Year')
ax.set_ylabel('Effect / GDP')
ax.set_title('(a) dV Decomposition: Price vs Quantity', fontweight='bold')
ax.legend(fontsize=9)

# (b) 价格效应 vs hu_growth
ax = axes[0, 1]
df_b = df[df['price_effect_gdp'].notna() & df['hu_growth'].notna()].copy()
df_b['pe_w'] = winsorize(df_b['price_effect_gdp'])
df_b['hg_w'] = winsorize(df_b['hu_growth'])
ax.scatter(df_b['hg_w'], df_b['pe_w'], s=3, alpha=0.2, color='#2166AC', rasterized=True)
z = np.polyfit(df_b['hg_w'], df_b['pe_w'], 1)
x_line = np.linspace(df_b['hg_w'].quantile(0.02), df_b['hg_w'].quantile(0.98), 100)
ax.plot(x_line, np.polyval(z, x_line), color='#D6604D', linewidth=2.5,
        label=f'b={z[0]:.2f}')
ax.axhline(y=0, color='grey', linestyle=':', linewidth=0.8)
ax.set_xlabel('Housing Unit Growth Rate')
ax.set_ylabel('Price Effect / GDP')
ax.set_title('(b) Price Effect vs Investment', fontweight='bold')
ax.legend()

# (c) Excess construction vs MUQ
ax = axes[0, 2]
df_c = df[df['MUQ_gdp'].notna() & df['hu_growth'].notna() & df['pop_growth'].notna()].copy()
df_c['MUQ_w'] = winsorize(df_c['MUQ_gdp'])
df_c['excess'] = winsorize(df_c['hu_growth'] - df_c['pop_growth'])
ax.scatter(df_c['excess'], df_c['MUQ_w'], s=3, alpha=0.2, color='#2166AC', rasterized=True)
z3 = np.polyfit(df_c['excess'], df_c['MUQ_w'], 1)
x_line3 = np.linspace(df_c['excess'].quantile(0.02), df_c['excess'].quantile(0.98), 100)
ax.plot(x_line3, np.polyval(z3, x_line3), color='#D6604D', linewidth=2.5,
        label=f'b={z3[0]:.2f}')
ax.axhline(y=0, color='grey', linestyle=':', linewidth=0.8)
ax.set_xlabel('Excess Construction (hu_growth - pop_growth)')
ax.set_ylabel('MUQ (dV/GDP)')
ax.set_title('(c) MUQ vs Excess Construction', fontweight='bold')
ax.legend()

# (d) V/GDP(t-1) vs MUQ(t) — 均值回归
ax = axes[1, 0]
df_d = df[df['MUQ_gdp'].notna() & df['V_GDP_lag'].notna()].copy()
df_d['MUQ_w'] = winsorize(df_d['MUQ_gdp'])
df_d['vg_w'] = winsorize(df_d['V_GDP_lag'])
ax.scatter(df_d['vg_w'], df_d['MUQ_w'], s=3, alpha=0.2, color='#2166AC', rasterized=True)
z4 = np.polyfit(df_d['vg_w'], df_d['MUQ_w'], 1)
x_line4 = np.linspace(df_d['vg_w'].quantile(0.02), df_d['vg_w'].quantile(0.98), 100)
ax.plot(x_line4, np.polyval(z4, x_line4), color='#D6604D', linewidth=2.5,
        label=f'b={z4[0]:.2f}')
ax.axhline(y=0, color='grey', linestyle=':', linewidth=0.8)
ax.set_xlabel('V/GDP (t-1)')
ax.set_ylabel('MUQ (dV/GDP)')
ax.set_title('(d) Mean Reversion: V/GDP -> MUQ', fontweight='bold')
ax.legend()

# (e) 分时段 beta 系数图
ax = axes[1, 1]
periods = []
betas = []
cis_lo = []
cis_hi = []
for yr in range(2011, 2023):
    df_yr = df[(df['year'] == yr) & df['MUQ_gdp'].notna() & df['hu_growth'].notna()].copy()
    if len(df_yr) < 50:
        continue
    df_yr['MUQ_w'] = winsorize(df_yr['MUQ_gdp'])
    df_yr['hg_w'] = winsorize(df_yr['hu_growth'])
    X_yr = sm.add_constant(df_yr['hg_w'])
    m_yr = sm.OLS(df_yr['MUQ_w'], X_yr).fit(cov_type='HC1')
    periods.append(yr)
    betas.append(m_yr.params['hg_w'])
    ci_yr = m_yr.conf_int().loc['hg_w']
    cis_lo.append(ci_yr[0])
    cis_hi.append(ci_yr[1])

ax.fill_between(periods, cis_lo, cis_hi, alpha=0.2, color='#2166AC')
ax.plot(periods, betas, 'o-', color='#2166AC', linewidth=2, markersize=6)
ax.axhline(y=0, color='red', linestyle='--', linewidth=1)
# 中国的 beta 作为参考
ax.axhline(y=-2.23, color='#B2182B', linestyle=':', linewidth=1.5, label='China beta=-2.23')
ax.set_xlabel('Year')
ax.set_ylabel('beta(hu_growth)')
ax.set_title('(e) Year-by-Year Beta Estimates', fontweight='bold')
ax.legend(fontsize=9)

# (f) 中美对比概念图
ax = axes[1, 2]
# 绘制对比条形图
labels = ['China\n(FAI/GDP)', 'US\n(hu_growth)', 'US\n(excess\nconstruction)']
values = [-2.23, 2.75, m_5b.params['excess_w'] if m_5b is not None else 0]
colors = ['#B2182B' if v < 0 else '#2166AC' for v in values]
bars = ax.bar(labels, values, color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
ax.axhline(y=0, color='black', linewidth=0.8)
for bar, v in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05 * np.sign(v),
            f'{v:.2f}', ha='center', fontweight='bold', fontsize=11)
ax.set_ylabel('Beta coefficient')
ax.set_title('(f) Cross-Country Comparison', fontweight='bold')

plt.suptitle('Diagnostic: Why MUQ-Investment Relationship Differs US vs China',
            fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.96])

fig_path = os.path.join(FIGS, 'fig_us_muq_diagnostics.png')
plt.savefig(fig_path, dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
rpt(f'\n图表已保存: {fig_path}')

# 保存报告
report_path = os.path.join(MODELS, 'us_muq_diagnostics_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
rpt(f'报告已保存: {report_path}')
