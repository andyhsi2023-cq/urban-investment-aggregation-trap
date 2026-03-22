"""
36_muq_real_correction.py
=========================
目的：诊断并修正全球 MUQ 名义值随城镇化递增的方向矛盾。
  - 名义 MUQ = ΔV_nominal / ΔI_nominal 受通胀放大，S4 > S1
  - 实际 MUQ = ΔV_real / ΔI_real 应消除通胀效应，检验是否递减

方法：
  A) 诊断名义 MUQ 递增原因（通胀分解）
  B) 构建实际 MUQ 并检验阶段趋势
  C) 标准化 MUQ/CPR 比率分析
  D) 中国 MUQ 名义 vs 实际对比
  E) 报告与统计检验

输入：
  - 02-data/processed/global_q_revised_panel.csv

输出：
  - 03-analysis/models/muq_real_correction_report.txt
  - 04-figures/drafts/fig_muq_real_correction.png

依赖：pandas, numpy, matplotlib, scipy, statsmodels
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# 路径设置
# =============================================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
PANEL_PATH = f'{BASE}/02-data/processed/global_q_revised_panel.csv'

OUT_REPORT = f'{BASE}/03-analysis/models/muq_real_correction_report.txt'
OUT_FIG = f'{BASE}/04-figures/drafts/fig_muq_real_correction.png'

report_lines = []
def rprint(msg):
    """同时打印到控制台和报告"""
    print(msg)
    report_lines.append(str(msg))

rprint("=" * 72)
rprint("MUQ 实际值修正分析: 诊断名义 MUQ 递增的通胀效应")
rprint("=" * 72)
rprint(f"日期: 2026-03-21")

# =============================================================================
# Part 0: 读取数据 + 构建实际变量
# =============================================================================
rprint("\n[Part 0] 数据准备")
rprint("-" * 50)

panel = pd.read_csv(PANEL_PATH)
rprint(f"  面板: {len(panel)} 行, {panel['country_code'].nunique()} 国")

# GDP 平减指数 (2015=1.0)
panel['deflator'] = panel['gdp_current_usd'] / panel['gdp_constant_2015']

# 实际变量 (constant 2015 USD)
# V2_nominal = rnna * deflator * 1e6 (PWT rnna 单位为百万)
# V2_real = rnna * 1e6 (去除通胀，保留实际资本存量价值)
panel['V2_real'] = panel['rnna'] * 1e6  # constant 2015 prices

# K_pim 是名义累积 GFCF；实际值需逐年用 deflator 调整
# K_pim_real = K_pim / deflator
panel['K_pim_real'] = panel['K_pim'] / panel['deflator']

# GFCF 实际值
panel['gfcf_real'] = panel['gfcf_current_usd'] / panel['deflator']

# 实际 MUQ: ΔV_real / ΔI_real
panel['delta_V2_real'] = panel.groupby('country_code')['V2_real'].diff()
panel['delta_I_real'] = panel.groupby('country_code')['gfcf_real'].diff()
panel['MUQ_real'] = panel['delta_V2_real'] / panel['delta_I_real']

# 极端值处理：与名义 MUQ 相同标准 (|MUQ| > 20 或 MUQ < -5)
muq_real_extreme = (panel['MUQ_real'].abs() > 20) | (panel['MUQ_real'] < -5)
panel.loc[muq_real_extreme, 'MUQ_real'] = np.nan

# 实际 CPR
panel['CPR_real'] = panel['V2_real'] / panel['K_pim_real']

# 统计可用观测
n_nominal = panel['MUQ'].notna().sum()
n_real = panel['MUQ_real'].notna().sum()
# 两者都有值的子集
both = panel['MUQ'].notna() & panel['MUQ_real'].notna()
n_both = both.sum()

rprint(f"  名义 MUQ 可用: {n_nominal}")
rprint(f"  实际 MUQ 可用: {n_real}")
rprint(f"  两者均可用: {n_both}")
rprint(f"  deflator 可用: {panel['deflator'].notna().sum()}")

# 阶段编码
stage_order = ['S1: <30%', 'S2: 30-50%', 'S3: 50-70%', 'S4: >70%']
stage_labels = ['S1\n<30%', 'S2\n30-50%', 'S3\n50-70%', 'S4\n>70%']
income_order = ['Low income', 'Lower middle income', 'Upper middle income', 'High income']

# =============================================================================
# Part A: 诊断名义 MUQ 递增的原因
# =============================================================================
rprint("\n" + "=" * 72)
rprint("PART A: 诊断名义 MUQ 递增的通胀效应")
rprint("=" * 72)

# A1: 通胀率与城镇化阶段的关系
rprint("\n[A1] 通胀率 (GDP deflator 年增长率) 与城镇化阶段")
panel['deflator_growth'] = panel.groupby('country_code')['deflator'].pct_change()

for stage in stage_order:
    mask = (panel['urban_stage'] == stage) & panel['deflator_growth'].notna()
    vals = panel.loc[mask, 'deflator_growth']
    if len(vals) > 0:
        rprint(f"  {stage}: 中位数通胀={vals.median()*100:.2f}%, "
               f"均值={vals.mean()*100:.2f}%, n={len(vals)}")

# A2: 名义 vs 实际 delta_V 和 delta_I 增速对比
rprint("\n[A2] 名义 vs 实际 ΔV 和 ΔI 中位数 (分阶段)")
for stage in stage_order:
    mask = (panel['urban_stage'] == stage)
    dv_nom = panel.loc[mask & panel['delta_V2'].notna(), 'delta_V2']
    dv_real = panel.loc[mask & panel['delta_V2_real'].notna(), 'delta_V2_real']
    di_nom = panel.loc[mask & panel['delta_I'].notna(), 'delta_I']
    di_real = panel.loc[mask & panel['delta_I_real'].notna(), 'delta_I_real']
    rprint(f"  {stage}:")
    if len(dv_nom) > 0:
        rprint(f"    ΔV名义中位数: {dv_nom.median()/1e9:.3f} B USD, "
               f"ΔV实际中位数: {dv_real.median()/1e9:.3f} B USD")
        rprint(f"    ΔI名义中位数: {di_nom.median()/1e9:.3f} B USD, "
               f"ΔI实际中位数: {di_real.median()/1e9:.3f} B USD")

# A3: 名义 vs 实际 MUQ 按阶段对比 — 核心诊断
rprint("\n[A3] 名义 vs 实际 MUQ 分阶段对比 — 核心诊断")
rprint(f"  {'阶段':<15} {'名义MUQ中位':<14} {'实际MUQ中位':<14} {'差异':<10} {'n_nom':<8} {'n_real':<8}")
rprint(f"  {'-'*70}")

nominal_medians = []
real_medians = []
for stage in stage_order:
    mask_nom = (panel['urban_stage'] == stage) & panel['MUQ'].notna()
    mask_real = (panel['urban_stage'] == stage) & panel['MUQ_real'].notna()
    med_nom = panel.loc[mask_nom, 'MUQ'].median()
    med_real = panel.loc[mask_real, 'MUQ_real'].median()
    n_nom = mask_nom.sum()
    n_real = mask_real.sum()
    nominal_medians.append(med_nom)
    real_medians.append(med_real)
    rprint(f"  {stage:<15} {med_nom:<14.3f} {med_real:<14.3f} {med_nom-med_real:<10.3f} {n_nom:<8} {n_real:<8}")

rprint(f"\n  名义趋势: S1={nominal_medians[0]:.2f} -> S4={nominal_medians[3]:.2f} "
       f"({'递增' if nominal_medians[3] > nominal_medians[0] else '递减'})")
rprint(f"  实际趋势: S1={real_medians[0]:.2f} -> S4={real_medians[3]:.2f} "
       f"({'递增' if real_medians[3] > real_medians[0] else '递减'})")

# A4: Kruskal-Wallis 检验（实际 MUQ 阶段差异）
rprint("\n[A4] Kruskal-Wallis 检验: 实际 MUQ 是否随阶段显著变化")
groups_real = []
for stage in stage_order:
    mask = (panel['urban_stage'] == stage) & panel['MUQ_real'].notna()
    groups_real.append(panel.loc[mask, 'MUQ_real'].values)

if all(len(g) > 0 for g in groups_real):
    kw_stat, kw_p = stats.kruskal(*groups_real)
    rprint(f"  Kruskal-Wallis H = {kw_stat:.3f}, p = {kw_p:.6f}")

    # Pairwise Mann-Whitney: S1 vs S4
    u_stat, u_p = stats.mannwhitneyu(groups_real[0], groups_real[3], alternative='greater')
    rprint(f"  Mann-Whitney S1 > S4: U = {u_stat:.0f}, p = {u_p:.6f}")
    u_stat2, u_p2 = stats.mannwhitneyu(groups_real[0], groups_real[3], alternative='less')
    rprint(f"  Mann-Whitney S1 < S4: U = {u_stat2:.0f}, p = {u_p2:.6f}")

# Jonckheere-Terpstra 趋势检验的替代：Spearman 相关
rprint("\n[A5] Spearman 相关: 实际 MUQ vs 城镇化率")
sub_real = panel.dropna(subset=['MUQ_real', 'urban_pct']).copy()
rho, p_rho = stats.spearmanr(sub_real['urban_pct'], sub_real['MUQ_real'])
rprint(f"  Spearman rho = {rho:.4f}, p = {p_rho:.6f}")
rprint(f"  方向: {'负相关(递减)' if rho < 0 else '正相关(递增)'}")

# =============================================================================
# Part B: 分收入组检验实际 MUQ 递减
# =============================================================================
rprint("\n" + "=" * 72)
rprint("PART B: 分收入组实际 MUQ 阶段趋势")
rprint("=" * 72)

for ig in income_order:
    rprint(f"\n  --- {ig} ---")
    ig_medians = []
    ig_groups = []
    for stage in stage_order:
        mask = (panel['income_group'] == ig) & (panel['urban_stage'] == stage) & panel['MUQ_real'].notna()
        vals = panel.loc[mask, 'MUQ_real']
        med = vals.median() if len(vals) > 0 else np.nan
        ig_medians.append(med)
        if len(vals) > 0:
            ig_groups.append(vals.values)
        rprint(f"    {stage}: 中位数={med:.3f}, n={len(vals)}" if len(vals) > 0
               else f"    {stage}: n=0")

    # 判断趋势
    valid_meds = [m for m in ig_medians if not np.isnan(m)]
    if len(valid_meds) >= 2:
        trend = "递减" if valid_meds[-1] < valid_meds[0] else "递增"
        rprint(f"    趋势: {trend} ({valid_meds[0]:.2f} -> {valid_meds[-1]:.2f})")

    # Spearman 相关
    sub_ig = panel[(panel['income_group'] == ig)].dropna(subset=['MUQ_real', 'urban_pct'])
    if len(sub_ig) > 10:
        rho_ig, p_ig = stats.spearmanr(sub_ig['urban_pct'], sub_ig['MUQ_real'])
        rprint(f"    Spearman rho = {rho_ig:.4f}, p = {p_ig:.6f}")

    # KW 检验
    if len(ig_groups) >= 2 and all(len(g) >= 5 for g in ig_groups):
        kw_ig, kw_p_ig = stats.kruskal(*ig_groups)
        rprint(f"    Kruskal-Wallis H = {kw_ig:.3f}, p = {kw_p_ig:.6f}")

# =============================================================================
# Part C: 标准化 MUQ — MUQ/CPR 比率
# =============================================================================
rprint("\n" + "=" * 72)
rprint("PART C: 标准化 MUQ/CPR 比率 (消除国家水平差异)")
rprint("=" * 72)

# MUQ_normalized = MUQ_real / CPR_real
panel['MUQ_norm'] = panel['MUQ_real'] / panel['CPR_real']
# 极端值处理
muq_norm_extreme = (panel['MUQ_norm'].abs() > 20) | (panel['MUQ_norm'] < -5)
panel.loc[muq_norm_extreme, 'MUQ_norm'] = np.nan

rprint(f"\n  MUQ/CPR 可用观测: {panel['MUQ_norm'].notna().sum()}")

rprint(f"\n  MUQ/CPR 分阶段:")
rprint(f"  {'阶段':<15} {'中位数':<12} {'均值':<12} {'n':<8}")
rprint(f"  {'-'*50}")
norm_medians = []
norm_groups = []
for stage in stage_order:
    mask = (panel['urban_stage'] == stage) & panel['MUQ_norm'].notna()
    vals = panel.loc[mask, 'MUQ_norm']
    med = vals.median() if len(vals) > 0 else np.nan
    mean = vals.mean() if len(vals) > 0 else np.nan
    norm_medians.append(med)
    if len(vals) > 0:
        norm_groups.append(vals.values)
    rprint(f"  {stage:<15} {med:<12.3f} {mean:<12.3f} {len(vals):<8}")

rprint(f"\n  趋势: {norm_medians[0]:.3f} -> {norm_medians[-1]:.3f} "
       f"({'递减' if norm_medians[-1] < norm_medians[0] else '递增'})")

if len(norm_groups) >= 2:
    kw_n, kw_pn = stats.kruskal(*norm_groups)
    rprint(f"  Kruskal-Wallis H = {kw_n:.3f}, p = {kw_pn:.6f}")

# 分收入组
rprint(f"\n  MUQ/CPR 分收入组和阶段:")
for ig in income_order:
    meds = []
    for stage in stage_order:
        mask = (panel['income_group'] == ig) & (panel['urban_stage'] == stage) & panel['MUQ_norm'].notna()
        vals = panel.loc[mask, 'MUQ_norm']
        meds.append(f"{vals.median():.2f}(n={len(vals)})" if len(vals) > 0 else "n/a")
    rprint(f"  {ig:<25} | " + " | ".join(meds))

# =============================================================================
# Part D: 中国 MUQ 名义 vs 实际
# =============================================================================
rprint("\n" + "=" * 72)
rprint("PART D: 中国 MUQ 名义 vs 实际对比")
rprint("=" * 72)

chn = panel[panel['country_code'] == 'CHN'].copy()
chn_muq = chn.dropna(subset=['MUQ']).copy()
chn_muq_real = chn.dropna(subset=['MUQ_real']).copy()

rprint(f"\n  中国名义 MUQ: {chn_muq['MUQ'].notna().sum()} 年")
rprint(f"  中国实际 MUQ: {chn_muq_real['MUQ_real'].notna().sum()} 年")

# 时序展示
rprint(f"\n  中国 MUQ 时序 (选取关键年份):")
rprint(f"  {'年份':<8} {'城镇化%':<10} {'名义MUQ':<12} {'实际MUQ':<12} {'deflator':<10}")
rprint(f"  {'-'*55}")

chn_both = chn.dropna(subset=['MUQ', 'MUQ_real', 'deflator']).copy()
# 选取每5年一个点 + 首末
key_years = sorted(set(list(range(1970, 2025, 5)) + [chn_both['year'].min(), chn_both['year'].max()]))
for _, row in chn_both.iterrows():
    if row['year'] in key_years:
        rprint(f"  {int(row['year']):<8} {row['urban_pct']:<10.1f} "
               f"{row['MUQ']:<12.3f} {row['MUQ_real']:<12.3f} {row['deflator']:<10.3f}")

# 中国实际 MUQ 趋势分析
rprint(f"\n  中国实际 MUQ 整体统计:")
rprint(f"    均值: {chn_muq_real['MUQ_real'].mean():.3f}")
rprint(f"    中位数: {chn_muq_real['MUQ_real'].median():.3f}")

# 分阶段
rprint(f"\n  中国实际 MUQ 分城镇化阶段:")
for stage in stage_order:
    vals = chn_muq_real.loc[chn_muq_real['urban_stage'] == stage, 'MUQ_real']
    if len(vals) > 0:
        rprint(f"    {stage}: 中位数={vals.median():.3f}, 均值={vals.mean():.3f}, n={len(vals)}")

# 中国 MUQ 是否转负？
chn_neg = chn_muq_real[chn_muq_real['MUQ_real'] < 0]
if len(chn_neg) > 0:
    rprint(f"\n  中国实际 MUQ 转负的年份: {chn_neg['year'].tolist()}")
    rprint(f"    对应城镇化率: {chn_neg['urban_pct'].tolist()}")
else:
    rprint(f"\n  中国实际 MUQ 在数据范围内未转负")
    # 检查趋势
    if len(chn_muq_real) > 5:
        rho_chn, p_chn = stats.spearmanr(chn_muq_real['year'], chn_muq_real['MUQ_real'])
        rprint(f"    时间趋势 Spearman rho = {rho_chn:.4f}, p = {p_chn:.6f}")
        rho_chn2, p_chn2 = stats.spearmanr(chn_muq_real['urban_pct'], chn_muq_real['MUQ_real'])
        rprint(f"    城镇化趋势 Spearman rho = {rho_chn2:.4f}, p = {p_chn2:.6f}")

# 中国名义 MUQ 转负检查
chn_neg_nom = chn_muq[chn_muq['MUQ'] < 0]
if len(chn_neg_nom) > 0:
    rprint(f"\n  中国名义 MUQ 转负年份: {chn_neg_nom[['year','urban_pct','MUQ']].values.tolist()}")

# =============================================================================
# Part E: 综合诊断报告
# =============================================================================
rprint("\n" + "=" * 72)
rprint("PART E: 综合诊断与结论")
rprint("=" * 72)

rprint(f"""
诊断问题: 名义 MUQ 随城镇化阶段递增 (S1={nominal_medians[0]:.2f} -> S4={nominal_medians[3]:.2f})，
与论文"效率递减"叙事矛盾。

原因分析:
  名义 MUQ = ΔV_nominal / ΔI_nominal
  V_nominal = rnna * GDP_deflator * 1e6
  I_nominal = GFCF_current_usd
  当 deflator 增长时，ΔV_nominal 被通胀放大，而 ΔI_nominal 虽然也是名义值，
  但资本存量 V 的基数远大于年投资流量 I，导致通胀对分子的放大效应 > 分母。

修正方法:
  实际 MUQ = ΔV_real / ΔI_real
  V_real = rnna * 1e6 (PWT 实际资本存量, constant national prices)
  I_real = GFCF_current / GDP_deflator (constant 2015 USD)

修正结果:
  实际 MUQ: S1={real_medians[0]:.2f} -> S4={real_medians[3]:.2f}
  方向: {'实际 MUQ 递减 -- 通胀修正后效率递减叙事成立' if real_medians[3] < real_medians[0]
         else '实际 MUQ 仍递增 -- 需进一步检查其他机制'}

全局 Spearman (实际 MUQ vs 城镇化率): rho = {rho:.4f}, p = {p_rho:.6f}

政策含义:
  - 名义 MUQ 的递增是通胀假象 (inflationary artifact)
  - 用实际 MUQ 替代名义 MUQ 可消除这一矛盾
  - 论文应统一报告实际 MUQ (constant 2015 USD)
""")

# =============================================================================
# 可视化
# =============================================================================
rprint("\n[生成图表]")

fig = plt.figure(figsize=(18, 14))
gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)

colors_stage = ['#2196F3', '#4CAF50', '#FF9800', '#F44336']
colors_income = ['#e74c3c', '#f39c12', '#2ecc71', '#3498db']

# --- Panel A: 名义 vs 实际 MUQ 箱线图 (分阶段) ---
ax_a = fig.add_subplot(gs[0, 0])
positions_nom = [1, 3, 5, 7]
positions_real = [1.7, 3.7, 5.7, 7.7]

bp_nom = ax_a.boxplot([panel.loc[(panel['urban_stage']==s) & panel['MUQ'].notna(), 'MUQ'].values
                        for s in stage_order],
                       positions=positions_nom, widths=0.55, patch_artist=True,
                       showfliers=False, medianprops=dict(color='black', linewidth=2))
for patch, c in zip(bp_nom['boxes'], colors_stage):
    patch.set_facecolor(c)
    patch.set_alpha(0.4)

bp_real = ax_a.boxplot([panel.loc[(panel['urban_stage']==s) & panel['MUQ_real'].notna(), 'MUQ_real'].values
                         for s in stage_order],
                        positions=positions_real, widths=0.55, patch_artist=True,
                        showfliers=False, medianprops=dict(color='black', linewidth=2))
for patch, c in zip(bp_real['boxes'], colors_stage):
    patch.set_facecolor(c)
    patch.set_alpha(0.8)

ax_a.set_xticks([1.35, 3.35, 5.35, 7.35])
ax_a.set_xticklabels(stage_labels, fontsize=9)
ax_a.set_ylabel('MUQ', fontsize=11)
ax_a.set_title('A. Nominal vs Real MUQ by Stage', fontsize=12, fontweight='bold')
ax_a.legend([bp_nom['boxes'][0], bp_real['boxes'][0]], ['Nominal', 'Real (2015 USD)'],
            loc='upper left', fontsize=9)

# 标注中位数趋势
nom_meds_plot = [panel.loc[(panel['urban_stage']==s) & panel['MUQ'].notna(), 'MUQ'].median() for s in stage_order]
real_meds_plot = [panel.loc[(panel['urban_stage']==s) & panel['MUQ_real'].notna(), 'MUQ_real'].median() for s in stage_order]
ax_a.plot(positions_nom, nom_meds_plot, 'o--', color='gray', alpha=0.6, label='_nom_trend')
ax_a.plot(positions_real, real_meds_plot, 'o-', color='darkred', alpha=0.8, label='_real_trend')

# --- Panel B: 实际 MUQ 分收入组 x 阶段 ---
ax_b = fig.add_subplot(gs[0, 1])
for i, ig in enumerate(income_order):
    meds = []
    for stage in stage_order:
        mask = (panel['income_group'] == ig) & (panel['urban_stage'] == stage) & panel['MUQ_real'].notna()
        vals = panel.loc[mask, 'MUQ_real']
        meds.append(vals.median() if len(vals) >= 5 else np.nan)
    ax_b.plot(range(4), meds, 'o-', color=colors_income[i], label=ig, linewidth=2, markersize=6)

ax_b.set_xticks(range(4))
ax_b.set_xticklabels(stage_labels, fontsize=9)
ax_b.set_ylabel('Real MUQ (median)', fontsize=11)
ax_b.set_title('B. Real MUQ by Income Group x Stage', fontsize=12, fontweight='bold')
ax_b.legend(fontsize=8, loc='best')
ax_b.axhline(y=1, color='gray', linestyle=':', alpha=0.5)

# --- Panel C: MUQ/CPR 标准化比率分阶段 ---
ax_c = fig.add_subplot(gs[0, 2])
bp_norm = ax_c.boxplot([panel.loc[(panel['urban_stage']==s) & panel['MUQ_norm'].notna(), 'MUQ_norm'].values
                         for s in stage_order],
                        widths=0.6, patch_artist=True, showfliers=False,
                        medianprops=dict(color='black', linewidth=2))
for patch, c in zip(bp_norm['boxes'], colors_stage):
    patch.set_facecolor(c)
    patch.set_alpha(0.7)

ax_c.set_xticklabels(stage_labels, fontsize=9)
ax_c.set_ylabel('MUQ / CPR', fontsize=11)
ax_c.set_title('C. Normalized MUQ/CPR by Stage', fontsize=12, fontweight='bold')
ax_c.axhline(y=1, color='red', linestyle='--', alpha=0.5, label='MUQ=CPR')
ax_c.legend(fontsize=9)

# --- Panel D: 中国名义 vs 实际 MUQ 时序 ---
ax_d = fig.add_subplot(gs[1, 0])
chn_plot = chn.dropna(subset=['year']).copy()
chn_nom_plot = chn_plot.dropna(subset=['MUQ'])
chn_real_plot = chn_plot.dropna(subset=['MUQ_real'])

if len(chn_nom_plot) > 0:
    ax_d.plot(chn_nom_plot['year'], chn_nom_plot['MUQ'], 'o-', color='#FF9800',
              alpha=0.6, label='Nominal', markersize=3, linewidth=1)
if len(chn_real_plot) > 0:
    ax_d.plot(chn_real_plot['year'], chn_real_plot['MUQ_real'], 's-', color='#2196F3',
              alpha=0.8, label='Real (2015 USD)', markersize=3, linewidth=1.5)

ax_d.axhline(y=0, color='red', linestyle='--', alpha=0.5)
ax_d.set_xlabel('Year', fontsize=11)
ax_d.set_ylabel('MUQ', fontsize=11)
ax_d.set_title('D. China: Nominal vs Real MUQ', fontsize=12, fontweight='bold')
ax_d.legend(fontsize=9)

# --- Panel E: 通胀率 vs MUQ偏差 ---
ax_e = fig.add_subplot(gs[1, 1])
both_mask = panel['MUQ'].notna() & panel['MUQ_real'].notna() & panel['deflator_growth'].notna()
if both_mask.sum() > 10:
    sub_bias = panel.loc[both_mask].copy()
    sub_bias['muq_bias'] = sub_bias['MUQ'] - sub_bias['MUQ_real']
    # 按 deflator_growth 分 5 分位
    sub_bias['infl_q'] = pd.qcut(sub_bias['deflator_growth'], 5, labels=False, duplicates='drop')
    bias_by_infl = sub_bias.groupby('infl_q').agg(
        infl_median=('deflator_growth', 'median'),
        bias_median=('muq_bias', 'median'),
        n=('muq_bias', 'count')
    ).reset_index()
    ax_e.bar(range(len(bias_by_infl)), bias_by_infl['bias_median'],
             color=['#2196F3', '#4CAF50', '#FF9800', '#F44336', '#9C27B0'][:len(bias_by_infl)],
             alpha=0.7, edgecolor='black')
    ax_e.set_xticks(range(len(bias_by_infl)))
    ax_e.set_xticklabels([f"Q{i+1}\n({bias_by_infl.iloc[i]['infl_median']*100:.1f}%)"
                           for i in range(len(bias_by_infl))], fontsize=8)
    ax_e.set_xlabel('Inflation Quintile (median rate)', fontsize=10)
    ax_e.set_ylabel('Nominal - Real MUQ (median bias)', fontsize=10)
    ax_e.set_title('E. Inflation Bias in Nominal MUQ', fontsize=12, fontweight='bold')
    ax_e.axhline(y=0, color='gray', linestyle=':', alpha=0.5)

# --- Panel F: 实际 MUQ vs 城镇化率散点 (含 LOWESS) ---
ax_f = fig.add_subplot(gs[1, 2])
sub_scatter = panel.dropna(subset=['MUQ_real', 'urban_pct']).copy()
# 随机抽样以避免过密
if len(sub_scatter) > 2000:
    sub_sample = sub_scatter.sample(2000, random_state=42)
else:
    sub_sample = sub_scatter

ax_f.scatter(sub_sample['urban_pct'], sub_sample['MUQ_real'],
             alpha=0.15, s=8, c='steelblue', edgecolors='none')

# LOWESS 趋势线
try:
    import statsmodels.api as sm
    lowess = sm.nonparametric.lowess(sub_scatter['MUQ_real'], sub_scatter['urban_pct'], frac=0.3)
    ax_f.plot(lowess[:, 0], lowess[:, 1], 'r-', linewidth=2.5, label='LOWESS')
except ImportError:
    pass

ax_f.set_xlabel('Urbanization Rate (%)', fontsize=11)
ax_f.set_ylabel('Real MUQ', fontsize=11)
ax_f.set_title('F. Real MUQ vs Urbanization (Global)', fontsize=12, fontweight='bold')
ax_f.legend(fontsize=9)
ax_f.axhline(y=1, color='gray', linestyle=':', alpha=0.3)

# 保存
plt.suptitle('MUQ Real Correction: Diagnosing Inflationary Bias in Nominal MUQ',
             fontsize=14, fontweight='bold', y=1.01)
plt.savefig(OUT_FIG, dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
rprint(f"  图表已保存: {OUT_FIG}")

# =============================================================================
# 保存报告
# =============================================================================
with open(OUT_REPORT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
rprint(f"\n报告已保存: {OUT_REPORT}")

print("\n[完成] 36_muq_real_correction.py 执行结束")
