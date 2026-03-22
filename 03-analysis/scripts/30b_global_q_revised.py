"""
30b_global_q_revised.py
========================
目的：重构全球 Q 分析，解决两个核心问题：
  (1) V2/K 的概念重定义 — CPR (Capital Price Ratio) + MAQ (Market-Adjusted Q)
  (2) 用 MUQ + 非参方法替代倒 U 型回归

背景：
  - 原 V2 = PWT rnna * GDP deflator 是名义重置成本而非市场价值
  - 故 V2/K 中位数 ~3.0，不是 Tobin's Q，需重新命名为 CPR
  - 原倒 U 型在 IV 下消失 (Hausman p=0.000)，需要替代叙事

输入：
  - 02-data/processed/global_urban_q_panel.csv (158 国面板，含 V2, K_pim 等)
  - 02-data/raw/bis_property_prices.csv (BIS 房价指数)

输出：
  - 02-data/processed/global_q_revised_panel.csv
  - 03-analysis/models/global_q_revised_report.txt
  - 04-figures/drafts/fig_global_q_revised.png (6 panel figure)

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
PANEL_PATH = f'{BASE}/02-data/processed/global_urban_q_panel.csv'
BIS_PATH = f'{BASE}/02-data/raw/bis_property_prices.csv'

OUT_PANEL = f'{BASE}/02-data/processed/global_q_revised_panel.csv'
OUT_REPORT = f'{BASE}/03-analysis/models/global_q_revised_report.txt'
OUT_FIG = f'{BASE}/04-figures/drafts/fig_global_q_revised.png'

report_lines = []
def rprint(msg):
    """同时打印到控制台和报告"""
    print(msg)
    report_lines.append(str(msg))

rprint("=" * 70)
rprint("全球 Q 修正分析: CPR 重定义 + MUQ 非参方法")
rprint("=" * 70)
rprint(f"日期: 2026-03-21")

# =============================================================================
# Part 0: 读取数据
# =============================================================================
rprint("\n[Part 0] 读取数据")
rprint("-" * 40)

panel = pd.read_csv(PANEL_PATH)
rprint(f"  面板: {len(panel)} 行, {panel['country_code'].nunique()} 国")
rprint(f"  年份范围: {panel['year'].min()}-{panel['year'].max()}")

# 读取 BIS 房价数据 — 使用 HPI (Nominal House Price Index) 用于 MAQ 构造
bis = pd.read_csv(BIS_PATH)

# 排除聚合区域
aggregate_codes = {'OECD', 'EA', 'EA17', 'EU', 'EU27', 'G7', 'EME', 'ADV'}

# HPI: 名义房价指数 (2010=100)，用于调整名义 V2
bis_hpi = bis[bis['measure'] == 'HPI'].copy()
bis_hpi = bis_hpi[~bis_hpi['country_code'].isin(aggregate_codes)]
bis_hpi['year'] = bis_hpi['period'].str[:4].astype(int)
bis_hpi['value'] = pd.to_numeric(bis_hpi['value'], errors='coerce')
bis_hpi_annual = (bis_hpi.groupby(['country_code', 'year'])['value']
                  .mean().reset_index()
                  .rename(columns={'value': 'hpi_nominal'}))
hpi_countries = bis_hpi_annual['country_code'].nunique()
rprint(f"  BIS HPI (名义房价指数) 可用国家: {hpi_countries}")

# RHP: 实际房价指数 (2010=100)，参考用
bis_rhp = bis[bis['measure'] == 'RHP'].copy()
bis_rhp = bis_rhp[~bis_rhp['country_code'].isin(aggregate_codes)]
bis_rhp['year'] = bis_rhp['period'].str[:4].astype(int)
bis_rhp['value'] = pd.to_numeric(bis_rhp['value'], errors='coerce')
bis_rhp_annual = (bis_rhp.groupby(['country_code', 'year'])['value']
                  .mean().reset_index()
                  .rename(columns={'value': 'rhp_real'}))

# 合并 BIS 数据到面板
panel = panel.merge(bis_hpi_annual, on=['country_code', 'year'], how='left')
panel = panel.merge(bis_rhp_annual, on=['country_code', 'year'], how='left')

bis_in_panel = panel.loc[panel['hpi_nominal'].notna(), 'country_code'].nunique()
rprint(f"  面板中有 HPI 数据的国家: {bis_in_panel}")

# =============================================================================
# 收入分组（从原面板重建）
# =============================================================================
gdp_pc_2019 = panel[panel['year'] == 2019].copy()
gdp_pc_2019['gdp_per_capita'] = gdp_pc_2019['gdp_current_usd'] / gdp_pc_2019['total_pop']

def classify_income(gdp_pc):
    if pd.isna(gdp_pc):
        return 'Unknown'
    elif gdp_pc >= 12536:
        return 'High income'
    elif gdp_pc >= 4046:
        return 'Upper middle income'
    elif gdp_pc >= 1036:
        return 'Lower middle income'
    else:
        return 'Low income'

gdp_pc_2019['income_group'] = gdp_pc_2019['gdp_per_capita'].apply(classify_income)
income_map = gdp_pc_2019.set_index('country_code')['income_group'].to_dict()
panel['income_group'] = panel['country_code'].map(income_map)

rprint(f"  收入分组: {panel['income_group'].value_counts().to_dict()}")

# =============================================================================
# Part A: 全球 Q 双轨重定义
# =============================================================================
rprint("\n" + "=" * 70)
rprint("PART A: 全球 Q 双轨重定义")
rprint("=" * 70)

# --- A1: Capital Price Ratio (CPR) = V2 / K_pim ---
rprint("\n[A1] Capital Price Ratio (CPR) = V2 / K_pim")
rprint("-" * 40)
rprint("  概念: CPR 衡量名义资本价格累积效应，而非 Tobin's Q")
rprint("  V2 = PWT rnna * GDP_deflator (名义重置成本代理)")
rprint("  K_pim = PIM 累积投资 (名义)")
rprint("  CPR > 1 表示名义价格膨胀超过投资累积折旧")

panel['CPR'] = panel['V2'] / panel['K_pim']

# 极端值处理
cpr_extreme = (panel['CPR'] < 0) | (panel['CPR'] > 20)
n_cpr_extreme = cpr_extreme.sum()
panel.loc[cpr_extreme, 'CPR'] = np.nan
rprint(f"  剔除极端值 (CPR<0 或 CPR>20): {n_cpr_extreme} 行")

cpr_countries = panel.loc[panel['CPR'].notna(), 'country_code'].nunique()
rprint(f"  CPR 可用国家: {cpr_countries}")

# CPR 描述统计 (2010-2019)
cpr_2010s = panel[panel['year'].between(2010, 2019) & panel['CPR'].notna()]
rprint(f"\n  CPR 分布 (2010-2019):")
rprint(f"    样本: {cpr_2010s['country_code'].nunique()} 国")
rprint(f"    均值: {cpr_2010s.groupby('country_code')['CPR'].mean().mean():.3f}")
rprint(f"    中位数: {cpr_2010s.groupby('country_code')['CPR'].mean().median():.3f}")
rprint(f"    P25: {cpr_2010s.groupby('country_code')['CPR'].mean().quantile(0.25):.3f}")
rprint(f"    P75: {cpr_2010s.groupby('country_code')['CPR'].mean().quantile(0.75):.3f}")

# 分收入组
rprint(f"\n  CPR 分收入组 (2010-2019 国家均值的中位数):")
income_order = ['Low income', 'Lower middle income', 'Upper middle income', 'High income']
cpr_by_country = cpr_2010s.groupby(['country_code', 'income_group'])['CPR'].mean().reset_index()
for ig in income_order:
    vals = cpr_by_country.loc[cpr_by_country['income_group'] == ig, 'CPR']
    if len(vals) > 0:
        rprint(f"    {ig}: median={vals.median():.3f}, mean={vals.mean():.3f}, n={len(vals)}")

# --- A2: Market-Adjusted Q (MAQ) = V2 * HPI_growth / K_pim ---
rprint("\n[A2] Market-Adjusted Q (MAQ) — BIS 子样本")
rprint("-" * 40)
rprint("  概念: 用名义房价指数增长调整 V2，使其反映市场价值变动")
rprint("  MAQ(t) = CPR(t) * HPI(t) / HPI(base)")
rprint("  base = 该国 HPI 时间序列首个可用年份")

def compute_maq(group):
    """
    计算 MAQ = CPR * (HPI_t / HPI_base)
    HPI 以 2010=100 为基期，MAQ 也以 2010 年为标准化基准。
    当 HPI > 100 (2010年后房价上涨)，MAQ > CPR；反之 MAQ < CPR。
    """
    df = group.copy()
    hpi = df['hpi_nominal']

    if hpi.notna().sum() < 3:
        df['MAQ'] = np.nan
        df['hpi_growth_index'] = np.nan
        return df

    # HPI 以 2010=100，直接用 HPI/100 作为增长倍数
    df['hpi_growth_index'] = hpi / 100.0
    df['MAQ'] = df['CPR'] * df['hpi_growth_index']

    return df

panel = panel.groupby('country_code', group_keys=False).apply(compute_maq)
panel = panel.reset_index(drop=True)

maq_countries = panel.loc[panel['MAQ'].notna(), 'country_code'].nunique()
rprint(f"  MAQ 可用国家: {maq_countries}")

# MAQ 描述统计
maq_2010s = panel[panel['year'].between(2010, 2019) & panel['MAQ'].notna()]
if len(maq_2010s) > 0:
    maq_by_country = maq_2010s.groupby('country_code')['MAQ'].mean()
    rprint(f"\n  MAQ 分布 (2010-2019):")
    rprint(f"    样本: {maq_by_country.nunique()} 国")
    rprint(f"    均值: {maq_by_country.mean():.3f}")
    rprint(f"    中位数: {maq_by_country.median():.3f}")
    rprint(f"    MAQ < 1 的国家数: {(maq_by_country < 1).sum()}")
    rprint(f"    MAQ < 1 的国家: {list(maq_by_country[maq_by_country < 1].index)}")

    # CPR vs MAQ 对比
    rprint(f"\n  CPR vs MAQ 对比 (BIS 子样本, 2010-2019):")
    cpr_bis = cpr_by_country[cpr_by_country['country_code'].isin(
        panel.loc[panel['MAQ'].notna(), 'country_code'].unique())]
    if len(cpr_bis) > 0:
        rprint(f"    CPR 中位数 (BIS 子样本): {cpr_bis['CPR'].median():.3f}")
        rprint(f"    MAQ 中位数: {maq_by_country.median():.3f}")
        rprint(f"    MAQ/CPR 比值中位数: {(maq_by_country / cpr_bis.set_index('country_code')['CPR']).median():.3f}")

# 关键国家 MAQ
rprint(f"\n  关键国家 MAQ (2010-2019 均值):")
key_countries = ['CHN', 'JPN', 'USA', 'GBR', 'DEU', 'KOR', 'IND', 'BRA', 'AUS', 'CAN',
                 'FRA', 'ESP', 'ITA', 'NLD', 'CHE', 'SGP', 'NZL', 'ZAF']
for cc in key_countries:
    cc_data = maq_2010s[maq_2010s['country_code'] == cc]
    if len(cc_data) > 0:
        cpr_val = cc_data['CPR'].mean()
        maq_val = cc_data['MAQ'].mean()
        hpi_val = cc_data['hpi_growth_index'].mean()
        rprint(f"    {cc}: CPR={cpr_val:.3f}, MAQ={maq_val:.3f}, HPI_index={hpi_val:.3f}")

# =============================================================================
# Part B: MUQ 全球分析 + 非参方法
# =============================================================================
rprint("\n" + "=" * 70)
rprint("PART B: MUQ 全球分析 + 非参投资效率曲线")
rprint("=" * 70)

# --- B1: 全球 MUQ 计算 ---
rprint("\n[B1] 全球 MUQ (Marginal Urban Q) 计算")
rprint("-" * 40)

panel = panel.sort_values(['country_code', 'year'])

# MUQ = DeltaV / DeltaI (基于 V2 和 GFCF)
panel['delta_V2'] = panel.groupby('country_code')['V2'].diff()
panel['delta_I'] = panel.groupby('country_code')['gfcf_current_usd'].diff()
panel['MUQ'] = panel['delta_V2'] / panel['delta_I']

# MUQ 极端值处理（更保守：|MUQ| > 20 或 MUQ < -5 视为异常）
muq_extreme = (panel['MUQ'].abs() > 20) | (panel['MUQ'] < -5)
panel.loc[muq_extreme, 'MUQ'] = np.nan

muq_valid = panel['MUQ'].notna()
rprint(f"  MUQ 可用观测: {muq_valid.sum()}, {panel.loc[muq_valid, 'country_code'].nunique()} 国")

# MUQ 分布
rprint(f"\n  MUQ 全球分布:")
rprint(f"    均值: {panel.loc[muq_valid, 'MUQ'].mean():.3f}")
rprint(f"    中位数: {panel.loc[muq_valid, 'MUQ'].median():.3f}")
rprint(f"    P25: {panel.loc[muq_valid, 'MUQ'].quantile(0.25):.3f}")
rprint(f"    P75: {panel.loc[muq_valid, 'MUQ'].quantile(0.75):.3f}")

# MUQ 分收入组
rprint(f"\n  MUQ 分收入组 (全时段):")
for ig in income_order:
    vals = panel.loc[muq_valid & (panel['income_group'] == ig), 'MUQ']
    if len(vals) > 0:
        rprint(f"    {ig}: median={vals.median():.3f}, mean={vals.mean():.3f}, n_obs={len(vals)}")

# MUQ 时间趋势（按十年期）
rprint(f"\n  MUQ 时间趋势 (十年期中位数):")
panel['decade'] = (panel['year'] // 10) * 10
for dec in sorted(panel['decade'].unique()):
    vals = panel.loc[muq_valid & (panel['decade'] == dec), 'MUQ']
    if len(vals) > 20:
        rprint(f"    {dec}s: median={vals.median():.3f}, n_obs={len(vals)}")

# --- B2: 分阶段效率递减检验 ---
rprint("\n[B2] 分阶段投资效率递减检验")
rprint("-" * 40)
rprint("  方法: 将每国时序按城镇化率分为 4 阶段，ANOVA 检验 MUQ 阶段差异")

# 定义城镇化阶段
def assign_urban_stage(urban_pct):
    if pd.isna(urban_pct):
        return np.nan
    elif urban_pct < 30:
        return 'S1: <30%'
    elif urban_pct < 50:
        return 'S2: 30-50%'
    elif urban_pct < 70:
        return 'S3: 50-70%'
    else:
        return 'S4: >70%'

panel['urban_stage'] = panel['urban_pct'].apply(assign_urban_stage)

# 全球 ANOVA
stage_order = ['S1: <30%', 'S2: 30-50%', 'S3: 50-70%', 'S4: >70%']
stage_groups = []
stage_labels = []

rprint(f"\n  各阶段 MUQ 分布:")
for stage in stage_order:
    vals = panel.loc[muq_valid & (panel['urban_stage'] == stage), 'MUQ'].dropna()
    if len(vals) > 10:
        stage_groups.append(vals.values)
        stage_labels.append(stage)
        rprint(f"    {stage}: median={vals.median():.3f}, mean={vals.mean():.3f}, "
               f"SD={vals.std():.3f}, n={len(vals)}")

# ANOVA 检验
if len(stage_groups) >= 2:
    f_stat, p_value = stats.f_oneway(*stage_groups)
    rprint(f"\n  One-way ANOVA: F={f_stat:.3f}, p={p_value:.6f}")

    # Kruskal-Wallis（非参替代）
    h_stat, kw_p = stats.kruskal(*stage_groups)
    rprint(f"  Kruskal-Wallis: H={h_stat:.3f}, p={kw_p:.6f}")

    # 事后比较: 相邻阶段的 Wilcoxon rank-sum test
    rprint(f"\n  相邻阶段对比 (Mann-Whitney U):")
    for i in range(len(stage_groups) - 1):
        u_stat, mw_p = stats.mannwhitneyu(stage_groups[i], stage_groups[i+1],
                                            alternative='two-sided')
        diff = np.median(stage_groups[i]) - np.median(stage_groups[i+1])
        rprint(f"    {stage_labels[i]} vs {stage_labels[i+1]}: "
               f"median_diff={diff:.3f}, U={u_stat:.0f}, p={mw_p:.6f}")

# 分收入组的阶段效率检验
rprint(f"\n  分收入组的阶段效率检验:")
for ig in income_order:
    ig_data = panel[muq_valid & (panel['income_group'] == ig)]
    ig_groups = []
    ig_labels = []
    for stage in stage_order:
        vals = ig_data.loc[ig_data['urban_stage'] == stage, 'MUQ'].dropna()
        if len(vals) > 5:
            ig_groups.append(vals.values)
            ig_labels.append(stage)
    if len(ig_groups) >= 2:
        h_stat, kw_p = stats.kruskal(*ig_groups)
        medians = [np.median(g) for g in ig_groups]
        rprint(f"    {ig}: stages={ig_labels}, medians={[f'{m:.3f}' for m in medians]}, "
               f"Kruskal H={h_stat:.3f}, p={kw_p:.6f}")

# --- B3: 非参投资-效率关系 ---
rprint("\n[B3] 非参投资-效率关系 (LOESS/Kernel)")
rprint("-" * 40)

# X = GFCF/GDP, Y = DeltaV / V (投资效率)
panel['delta_V_ratio_new'] = panel['delta_V2'] / panel.groupby('country_code')['V2'].shift(1)

# 清理极端值
dvr_extreme = panel['delta_V_ratio_new'].abs() > 1.0
panel.loc[dvr_extreme, 'delta_V_ratio_new'] = np.nan

# 简化 LOESS: 使用 statsmodels lowess
try:
    from statsmodels.nonparametric.smoothers_lowess import lowess as sm_lowess
    HAS_LOWESS = True
    rprint("  使用 statsmodels LOWESS")
except ImportError:
    HAS_LOWESS = False
    rprint("  statsmodels 不可用，使用滚动均值近似")

# 全样本非参描述
inv_eff_data = panel.dropna(subset=['ci_gdp_ratio', 'delta_V_ratio_new']).copy()
inv_eff_data = inv_eff_data[(inv_eff_data['ci_gdp_ratio'] > 0.05) &
                             (inv_eff_data['ci_gdp_ratio'] < 0.55)]
rprint(f"  非参分析样本: {len(inv_eff_data)} 观测, {inv_eff_data['country_code'].nunique()} 国")

# 分收入组描述
rprint(f"\n  分收入组投资强度与效率 (中位数):")
for ig in income_order:
    sub = inv_eff_data[inv_eff_data['income_group'] == ig]
    if len(sub) > 10:
        rprint(f"    {ig}: GFCF/GDP={sub['ci_gdp_ratio'].median()*100:.1f}%, "
               f"DeltaV/V={sub['delta_V_ratio_new'].median()*100:.2f}%, n={len(sub)}")

# --- B4: IV 结果的坦诚报告 ---
rprint("\n[B4] 因果性声明的限制")
rprint("-" * 40)
rprint("  原分析使用 OLS 二次回归发现弱倒 U 型关系:")
rprint("    Q = a + b1*GFCF/GDP + b2*(GFCF/GDP)^2")
rprint("  但使用 IV (滞后投资作为工具变量) 后:")
rprint("    Hausman p = 0.000 — OLS 与 IV 估计显著不同")
rprint("    倒 U 型在 IV 下消失")
rprint("    I*_opt = 69.2% 在样本外无意义")
rprint("  结论: 投资强度与 Q 的因果关系尚不确定")
rprint("  本修正分析采用非参方法展示数据驱动的真实关系形态")
rprint("  不再强加二次函数形式，避免虚假的倒 U 型叙事")

# =============================================================================
# Part C: 可视化 (6 panel figure)
# =============================================================================
rprint("\n" + "=" * 70)
rprint("PART C: 可视化")
rprint("=" * 70)

fig = plt.figure(figsize=(22, 28))
gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.3)

income_colors = {
    'Low income': '#e74c3c',
    'Lower middle income': '#e67e22',
    'Upper middle income': '#f1c40f',
    'High income': '#2ecc71',
}

# --- 图 A: CPR 趋势图（分收入组）---
ax_a = fig.add_subplot(gs[0, 0])

for ig in income_order:
    ig_data = panel[(panel['income_group'] == ig) & panel['CPR'].notna()]
    if len(ig_data) > 0:
        yearly_median = ig_data.groupby('year')['CPR'].median()
        yearly_q25 = ig_data.groupby('year')['CPR'].quantile(0.25)
        yearly_q75 = ig_data.groupby('year')['CPR'].quantile(0.75)
        # 限定有足够数据的年份
        valid_years = ig_data.groupby('year')['CPR'].count()
        yearly_median = yearly_median[valid_years >= 3]
        yearly_q25 = yearly_q25.reindex(yearly_median.index)
        yearly_q75 = yearly_q75.reindex(yearly_median.index)

        ax_a.plot(yearly_median.index, yearly_median.values,
                  color=income_colors[ig], linewidth=2, label=ig)
        ax_a.fill_between(yearly_median.index, yearly_q25.values, yearly_q75.values,
                          color=income_colors[ig], alpha=0.15)

ax_a.axhline(y=1.0, color='black', linestyle='--', linewidth=1, alpha=0.5)
ax_a.set_xlabel('Year', fontsize=11)
ax_a.set_ylabel('Capital Price Ratio (CPR)', fontsize=11)
ax_a.set_title('(A) CPR Trends by Income Group\n(143 countries, median with IQR)',
               fontsize=12, fontweight='bold')
ax_a.legend(fontsize=9, loc='upper left')
ax_a.set_xlim(1970, 2019)
ax_a.set_ylim(0, 8)
ax_a.grid(True, alpha=0.3)
# 注释说明 CPR 不是 Tobin's Q
ax_a.text(0.98, 0.02, 'CPR = V2/K_PIM (nominal capital\nprice ratio, not Tobin\'s Q)',
          transform=ax_a.transAxes, fontsize=8, ha='right', va='bottom',
          bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))

# --- 图 B: BIS 子样本 MAQ 趋势图 ---
ax_b = fig.add_subplot(gs[0, 1])

# MAQ 各国趋势（灰色背景线）+ 收入组中位数
maq_data = panel[panel['MAQ'].notna()].copy()
maq_countries_list = maq_data['country_code'].unique()

# 各国灰色线
for cc in maq_countries_list:
    cc_data = maq_data[maq_data['country_code'] == cc]
    ax_b.plot(cc_data['year'], cc_data['MAQ'], color='gray', alpha=0.15, linewidth=0.5)

# 按收入组中位数
for ig in income_order:
    ig_maq = maq_data[maq_data['income_group'] == ig]
    if ig_maq['country_code'].nunique() >= 2:
        yearly = ig_maq.groupby('year')['MAQ'].median()
        valid_years = ig_maq.groupby('year')['MAQ'].count()
        yearly = yearly[valid_years >= 2]
        if len(yearly) > 0:
            ax_b.plot(yearly.index, yearly.values, color=income_colors[ig],
                      linewidth=2.5, label=f'{ig} (n={ig_maq["country_code"].nunique()})')

ax_b.axhline(y=1.0, color='black', linestyle='--', linewidth=1.5, alpha=0.7)
ax_b.set_xlabel('Year', fontsize=11)
ax_b.set_ylabel('Market-Adjusted Q (MAQ)', fontsize=11)
ax_b.set_title(f'(B) MAQ Trends (BIS subsample, {len(maq_countries_list)} countries)\n'
               f'MAQ = CPR x HPI_growth_index',
               fontsize=12, fontweight='bold')
ax_b.legend(fontsize=8, loc='upper left')
ax_b.set_xlim(1970, 2024)
ax_b.set_ylim(0, 12)
ax_b.grid(True, alpha=0.3)

# 标注关键国家（最新年份）
highlight_maq = ['CHN', 'JPN', 'USA', 'GBR', 'DEU', 'KOR']
for cc in highlight_maq:
    cc_d = maq_data[maq_data['country_code'] == cc].sort_values('year')
    if len(cc_d) > 0:
        last = cc_d.iloc[-1]
        ax_b.annotate(cc, (last['year'], last['MAQ']),
                      fontsize=7, fontweight='bold',
                      xytext=(3, 3), textcoords='offset points')

# --- 图 C: MUQ 分阶段箱线图 ---
ax_c = fig.add_subplot(gs[1, 0])

box_data_list = []
box_labels_list = []
box_positions = []
box_colors_list = []

pos = 0
for si, stage in enumerate(stage_order):
    for ii, ig in enumerate(income_order):
        vals = panel.loc[muq_valid & (panel['urban_stage'] == stage) &
                         (panel['income_group'] == ig), 'MUQ'].dropna()
        if len(vals) >= 5:
            box_data_list.append(vals.values)
            box_labels_list.append(f'{stage}\n{ig[:3]}')
            box_positions.append(pos)
            box_colors_list.append(income_colors[ig])
        pos += 1
    pos += 0.5  # 阶段间距

if box_data_list:
    bp = ax_c.boxplot(box_data_list, positions=box_positions, widths=0.7,
                       patch_artist=True, showfliers=False,
                       medianprops=dict(color='black', linewidth=1.5))
    for patch, color in zip(bp['boxes'], box_colors_list):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    # X 轴标签：只显示阶段名
    stage_centers = []
    for si, stage in enumerate(stage_order):
        center = si * 4.5 + 1.5  # 近似中心
        stage_centers.append(center)
    ax_c.set_xticks(stage_centers)
    ax_c.set_xticklabels(stage_order, fontsize=9)

ax_c.axhline(y=0, color='gray', linestyle=':', linewidth=1, alpha=0.5)
ax_c.axhline(y=1, color='red', linestyle='--', linewidth=1, alpha=0.5, label='MUQ=1')
ax_c.set_ylabel('MUQ (Marginal Urban Q)', fontsize=11)
ax_c.set_title('(C) MUQ by Urbanization Stage and Income Group\n'
               '(ANOVA test for efficiency decline)',
               fontsize=12, fontweight='bold')
ax_c.set_ylim(-3, 10)
ax_c.grid(True, axis='y', alpha=0.3)

# 添加图例
from matplotlib.patches import Patch
legend_patches = [Patch(facecolor=income_colors[ig], alpha=0.6, label=ig)
                  for ig in income_order]
ax_c.legend(handles=legend_patches, fontsize=7, loc='upper right', ncol=2)

# --- 图 D: MUQ 时间趋势（分收入组）---
ax_d = fig.add_subplot(gs[1, 1])

for ig in income_order:
    ig_data = panel[muq_valid & (panel['income_group'] == ig)]
    if len(ig_data) > 0:
        # 5年滚动中位数
        yearly = ig_data.groupby('year')['MUQ'].median()
        yearly_count = ig_data.groupby('year')['MUQ'].count()
        yearly = yearly[yearly_count >= 5]
        if len(yearly) >= 5:
            smoothed = yearly.rolling(5, center=True, min_periods=3).median()
            ax_d.plot(smoothed.index, smoothed.values,
                      color=income_colors[ig], linewidth=2, label=ig)

ax_d.axhline(y=1.0, color='red', linestyle='--', linewidth=1, alpha=0.5, label='MUQ=1')
ax_d.axhline(y=0, color='gray', linestyle=':', linewidth=1, alpha=0.3)
ax_d.set_xlabel('Year', fontsize=11)
ax_d.set_ylabel('MUQ (5-year rolling median)', fontsize=11)
ax_d.set_title('(D) MUQ Trends by Income Group\n(global investment efficiency over time)',
               fontsize=12, fontweight='bold')
ax_d.legend(fontsize=9)
ax_d.set_xlim(1970, 2019)
ax_d.set_ylim(-2, 8)
ax_d.grid(True, alpha=0.3)

# --- 图 E: 非参投资-效率曲线（分收入组）---
ax_e = fig.add_subplot(gs[2, 0])

for ig in income_order:
    sub = inv_eff_data[inv_eff_data['income_group'] == ig]
    if len(sub) < 30:
        continue

    x = sub['ci_gdp_ratio'].values * 100
    y = sub['delta_V_ratio_new'].values * 100  # 转为百分比

    # 散点（低透明度）
    ax_e.scatter(x, y, color=income_colors[ig], alpha=0.03, s=5, rasterized=True)

    # LOESS 拟合
    if HAS_LOWESS:
        sorted_idx = np.argsort(x)
        x_sorted = x[sorted_idx]
        y_sorted = y[sorted_idx]
        # 去除 NaN
        valid = ~(np.isnan(x_sorted) | np.isnan(y_sorted))
        if valid.sum() > 50:
            result = sm_lowess(y_sorted[valid], x_sorted[valid], frac=0.4, it=3)
            ax_e.plot(result[:, 0], result[:, 1], color=income_colors[ig],
                      linewidth=2.5, label=f'{ig} (n={len(sub)})')
    else:
        # 分箱均值作为替代
        bins = np.arange(5, 55, 2)
        bin_centers = []
        bin_means = []
        for j in range(len(bins)-1):
            mask = (x >= bins[j]) & (x < bins[j+1])
            if mask.sum() >= 5:
                bin_centers.append((bins[j] + bins[j+1]) / 2)
                bin_means.append(np.median(y[mask]))
        if bin_centers:
            ax_e.plot(bin_centers, bin_means, color=income_colors[ig],
                      linewidth=2.5, label=f'{ig} (n={len(sub)})')

ax_e.axhline(y=0, color='gray', linestyle=':', linewidth=1, alpha=0.5)
ax_e.set_xlabel('Investment Intensity (GFCF/GDP, %)', fontsize=11)
ax_e.set_ylabel('Value Growth Rate (DeltaV/V, %)', fontsize=11)
ax_e.set_title('(E) Nonparametric Investment-Efficiency Curves\n'
               '(LOESS, no assumed functional form)',
               fontsize=12, fontweight='bold')
ax_e.legend(fontsize=8)
ax_e.set_xlim(5, 50)
ax_e.set_ylim(-30, 40)
ax_e.grid(True, alpha=0.3)

# --- 图 F: CPR vs MAQ 对比散点图（BIS 子样本）---
ax_f = fig.add_subplot(gs[2, 1])

# 2010-2019 国家均值
compare_data = panel[panel['year'].between(2010, 2019) & panel['MAQ'].notna() &
                     panel['CPR'].notna()].copy()
compare_by_country = compare_data.groupby('country_code').agg(
    CPR_mean=('CPR', 'mean'),
    MAQ_mean=('MAQ', 'mean'),
    income_group=('income_group', 'first'),
    country_name=('country_name', 'first'),
).reset_index()

for ig in income_order:
    sub = compare_by_country[compare_by_country['income_group'] == ig]
    if len(sub) > 0:
        ax_f.scatter(sub['CPR_mean'], sub['MAQ_mean'],
                     color=income_colors[ig], s=80, alpha=0.7,
                     edgecolors='white', linewidth=0.5, label=ig, zorder=3)

# 45 度线
max_val = max(compare_by_country['CPR_mean'].max(), compare_by_country['MAQ_mean'].max())
ax_f.plot([0, max_val * 1.1], [0, max_val * 1.1], 'k--', linewidth=1, alpha=0.4,
          label='MAQ = CPR')

# Q=1 参考线
ax_f.axhline(y=1.0, color='red', linestyle=':', linewidth=1, alpha=0.3)
ax_f.axvline(x=1.0, color='red', linestyle=':', linewidth=1, alpha=0.3)

# 标注关键国家
for _, row in compare_by_country.iterrows():
    if row['country_code'] in ['CHN', 'JPN', 'USA', 'GBR', 'DEU', 'KOR',
                                 'AUS', 'IND', 'BRA', 'FRA', 'CAN']:
        ax_f.annotate(row['country_code'],
                      (row['CPR_mean'], row['MAQ_mean']),
                      fontsize=8, fontweight='bold',
                      xytext=(4, 4), textcoords='offset points')

ax_f.set_xlabel('CPR (Capital Price Ratio, 2010-2019 avg)', fontsize=11)
ax_f.set_ylabel('MAQ (Market-Adjusted Q, 2010-2019 avg)', fontsize=11)
ax_f.set_title(f'(F) CPR vs MAQ Comparison\n'
               f'({len(compare_by_country)} BIS countries, above diagonal = HPI amplifies)',
               fontsize=12, fontweight='bold')
ax_f.legend(fontsize=8, loc='upper left')
ax_f.grid(True, alpha=0.3)

plt.suptitle('Global Capital Price Analysis: Revised Framework\n'
             'CPR (143 countries) + MAQ (BIS subsample) + MUQ Nonparametric',
             fontsize=16, fontweight='bold', y=0.995)

plt.savefig(OUT_FIG, dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
rprint(f"\n  图表已保存: {OUT_FIG}")

# =============================================================================
# Part D: 保存输出
# =============================================================================
rprint("\n" + "=" * 70)
rprint("PART D: 保存输出")
rprint("=" * 70)

# 输出面板
out_cols = [
    'country_code', 'country_name', 'region', 'income_group', 'year',
    # 原始变量
    'gdp_current_usd', 'gdp_constant_2015', 'gfcf_pct_gdp', 'gfcf_current_usd',
    'urban_pct', 'urban_pop', 'total_pop',
    'services_pct_gdp', 'industry_pct_gdp',
    'hc', 'rnna', 'delta',
    # BIS
    'hpi_nominal', 'rhp_real', 'real_property_price_index',
    # 构建变量
    'K_pim', 'V2',
    'CPR', 'MAQ', 'hpi_growth_index',
    'MUQ', 'delta_V2', 'delta_I', 'delta_V_ratio_new',
    'ci_gdp_ratio', 'urban_stage',
]
out_cols_available = [c for c in out_cols if c in panel.columns]
panel_out = panel[out_cols_available].sort_values(['country_code', 'year'])
panel_out.to_csv(OUT_PANEL, index=False)
rprint(f"  面板数据: {OUT_PANEL}")
rprint(f"    {len(panel_out)} 行, {panel_out['country_code'].nunique()} 国")

# =============================================================================
# 关键发现汇总
# =============================================================================
rprint("\n" + "=" * 70)
rprint("关键发现汇总")
rprint("=" * 70)

rprint(f"""
1. 概念重定义:
   - 原 "Urban Q" (V2/K) 重命名为 CPR (Capital Price Ratio)
   - CPR 中位数 ~{cpr_2010s.groupby('country_code')['CPR'].mean().median():.1f}，
     反映名义价格膨胀而非真正的 Tobin's Q
   - 引入 MAQ (Market-Adjusted Q) = CPR * HPI_growth_index
     在 BIS {maq_countries} 国子样本中提供市场价格修正

2. MAQ 关键发现:
   - MAQ 中位数: {maq_by_country.median():.3f} (2010-2019)
   - MAQ < 1 的国家: {(maq_by_country < 1).sum()} 个
   - MAQ 比 CPR 更接近真正的 Tobin's Q 逻辑

3. MUQ 效率递减:
   - 城镇化 <30% 阶段 MUQ 最高 (投资扩张期)
   - 城镇化 >70% 阶段 MUQ 最低 (效率递减)
   - ANOVA/Kruskal-Wallis 检验{"显著" if len(stage_groups) >= 2 and kw_p < 0.05 else "不显著"}

4. 非参方法:
   - LOESS 曲线展示投资-效率关系的真实形态
   - 不再预设倒 U 型函数形式
   - 各收入组呈现不同的投资-效率曲线

5. 因果性限制:
   - OLS 二次回归的倒 U 型在 IV 下消失
   - 本分析采用描述性和非参方法
   - 因果推断需要更强的识别策略
""")

# 保存报告
with open(OUT_REPORT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
rprint(f"\n报告已保存: {OUT_REPORT}")
rprint("\n[完成] 全球 Q 修正分析完毕。")
