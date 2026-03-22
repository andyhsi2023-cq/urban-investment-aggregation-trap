#!/usr/bin/env python3
"""
70_nature_main_figures.py
=========================
Nature 出版级主图生成脚本（5 张主图）

Fig 1: The Global Urban Investment Landscape (3 panels)
Fig 2: China's Regime Shift (3 panels)
Fig 3: Overbuilding Across China's Cities (2 panels)
Fig 4: Staged Efficiency Decline (2 panels)
Fig 5: Early Warning and Carbon Cost (2 panels)

Nature 技术规范：
  - 字体: Helvetica/Arial, 5-7pt 印刷
  - 单栏 89mm / 双栏 183mm
  - 线宽: 0.25-1 pt
  - 色盲安全配色
  - PDF 矢量输出

输出：
  - 04-figures/final/fig0{1-5}_*.pdf + .png
  - 04-figures/source-data/fig{1-5}_source_data.csv
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch
from scipy import stats
from scipy.ndimage import uniform_filter1d
import statsmodels.api as sm
from statsmodels.nonparametric.smoothers_lowess import lowess

warnings.filterwarnings('ignore')

# ============================================================
# 路径设置
# ============================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
DATA = os.path.join(BASE, '02-data', 'processed')
MODELS = os.path.join(BASE, '03-analysis', 'models')
FIG_OUT = os.path.join(BASE, '04-figures', 'final')
SRC_OUT = os.path.join(BASE, '04-figures', 'source-data')

os.makedirs(FIG_OUT, exist_ok=True)
os.makedirs(SRC_OUT, exist_ok=True)

# ============================================================
# Nature 色彩方案 (色盲安全)
# ============================================================
COLORS = {
    'blue':   '#0077BB',
    'orange': '#EE7733',
    'cyan':   '#33BBEE',
    'red':    '#CC3311',
    'grey':   '#BBBBBB',
    'teal':   '#009988',
    'magenta':'#EE3377',
    'light_blue': '#77AADD',
    'light_orange': '#EEBB88',
}

# 四国配色
COUNTRY_COLORS = {
    'CHN': COLORS['blue'],
    'JPN': COLORS['orange'],
    'USA': COLORS['cyan'],
    'GBR': COLORS['grey'],
}
COUNTRY_LABELS = {
    'CHN': 'China',
    'JPN': 'Japan',
    'USA': 'United States',
    'GBR': 'United Kingdom',
}

# 收入组配色
INCOME_COLORS = {
    'Low income':          COLORS['red'],
    'Lower middle income': COLORS['orange'],
    'Upper middle income': COLORS['cyan'],
    'High income':         COLORS['blue'],
}

# 城市等级配色
TIER_COLORS = {
    '一线':     COLORS['blue'],
    '新一线':   COLORS['cyan'],
    '二线':     COLORS['orange'],
    '三线及以下': COLORS['grey'],
}
TIER_ORDER = ['一线', '新一线', '二线', '三线及以下']
TIER_LABELS_EN = {
    '一线': 'Tier 1',
    '新一线': 'New Tier 1',
    '二线': 'Tier 2',
    '三线及以下': 'Tier 3+',
}


# ============================================================
# Nature 样式函数
# ============================================================
def nature_style():
    """设置 Nature 出版级全局样式"""
    plt.rcParams.update({
        'font.family': 'Arial',
        'font.size': 7,
        'axes.titlesize': 8,
        'axes.labelsize': 7,
        'xtick.labelsize': 6,
        'ytick.labelsize': 6,
        'legend.fontsize': 6,
        'axes.linewidth': 0.5,
        'xtick.major.width': 0.5,
        'ytick.major.width': 0.5,
        'xtick.minor.width': 0.3,
        'ytick.minor.width': 0.3,
        'xtick.major.size': 3,
        'ytick.major.size': 3,
        'xtick.minor.size': 1.5,
        'ytick.minor.size': 1.5,
        'lines.linewidth': 0.75,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.05,
        'pdf.fonttype': 42,  # TrueType (Nature 要求)
        'ps.fonttype': 42,
    })

nature_style()

# mm -> inches
MM2IN = 1 / 25.4
SINGLE_COL = 89 * MM2IN     # ~3.5 in
DOUBLE_COL = 183 * MM2IN    # ~7.2 in


def panel_label(ax, label, x=-0.12, y=1.08):
    """在面板左上角添加 bold 小写标签 (a), (b), (c)"""
    ax.text(x, y, f'({label})', transform=ax.transAxes,
            fontsize=8, fontweight='bold', va='top', ha='left')


def save_fig(fig, name):
    """同时保存 PDF 和 PNG"""
    pdf_path = os.path.join(FIG_OUT, f'{name}.pdf')
    png_path = os.path.join(FIG_OUT, f'{name}.png')
    fig.savefig(pdf_path, format='pdf')
    fig.savefig(png_path, format='png', dpi=300)
    print(f'  -> {pdf_path}')
    print(f'  -> {png_path}')


def save_source(df, name):
    """保存 Source Data CSV"""
    path = os.path.join(SRC_OUT, f'{name}_source_data.csv')
    df.to_csv(path, index=False)
    print(f'  -> {path}')


# ============================================================
# 加载数据
# ============================================================
print('Loading data...')
china_q = pd.read_csv(os.path.join(MODELS, 'china_q_adjusted.csv'))
global_panel = pd.read_csv(os.path.join(DATA, 'global_q_revised_panel.csv'))
city_panel = pd.read_csv(os.path.join(DATA, 'china_city_real_window.csv'))
four_country = pd.read_csv(os.path.join(DATA, 'four_country_wb_pwt_panel.csv'))
print(f'  china_q: {len(china_q)} rows')
print(f'  global_panel: {len(global_panel)} rows, {global_panel.country_code.nunique()} countries')
print(f'  city_panel: {len(city_panel)} cities')
print(f'  four_country: {len(four_country)} rows')


# ############################################################
# FIG 1: The Global Urban Investment Landscape
# ############################################################
def fig1_global_landscape():
    """
    三面板双栏图:
    (a) 四国 CPR 时序对比
    (b) 全球 CPR 按收入组趋势 + 置信区间
    (c) GFCF/GDP vs CPR 变化率散点图
    """
    print('\n=== Fig 1: The Global Urban Investment Landscape ===')

    fig = plt.figure(figsize=(DOUBLE_COL, DOUBLE_COL * 0.42))
    gs = GridSpec(1, 3, figure=fig, wspace=0.35, hspace=0.3,
                  left=0.06, right=0.97, top=0.90, bottom=0.15)

    # --- (a) 四国 CPR 时序 ---
    ax_a = fig.add_subplot(gs[0, 0])
    panel_label(ax_a, 'a')

    four_cpr = global_panel[global_panel.country_code.isin(['CHN', 'JPN', 'USA', 'GBR'])]
    four_cpr = four_cpr.dropna(subset=['CPR'])
    source_a = []
    for cc in ['CHN', 'JPN', 'USA', 'GBR']:
        sub = four_cpr[four_cpr.country_code == cc].sort_values('year')
        ax_a.plot(sub.year, sub.CPR, color=COUNTRY_COLORS[cc],
                  label=COUNTRY_LABELS[cc], linewidth=0.9, zorder=3)
        for _, r in sub.iterrows():
            source_a.append({'country': cc, 'year': int(r.year), 'CPR': r.CPR})

    ax_a.axhline(y=1, color='k', linestyle='--', linewidth=0.4, alpha=0.6, zorder=1)
    ax_a.text(2020.5, 1.05, 'Value destruction\nthreshold', fontsize=5, ha='right',
              va='bottom', color='#555555', style='italic')

    ax_a.set_xlabel('Year')
    ax_a.set_ylabel('Capital price ratio (V/K)')
    ax_a.set_title('Four-country CPR trajectories', fontsize=7, fontweight='bold')
    ax_a.legend(loc='upper right', frameon=False, fontsize=5.5)
    ax_a.set_xlim(1968, 2021)

    # --- (b) 全球 CPR 按收入组 ---
    ax_b = fig.add_subplot(gs[0, 1])
    panel_label(ax_b, 'b')

    income_order = ['Low income', 'Lower middle income', 'Upper middle income', 'High income']
    income_labels_short = {'Low income': 'Low', 'Lower middle income': 'Lower middle',
                           'Upper middle income': 'Upper middle', 'High income': 'High'}

    valid = global_panel.dropna(subset=['CPR', 'income_group'])
    valid = valid[valid.income_group.isin(income_order)]
    source_b = []

    for ig in income_order:
        sub = valid[valid.income_group == ig]
        grouped = sub.groupby('year')['CPR'].agg(['median', 'mean', 'std', 'count'])
        grouped = grouped[grouped['count'] >= 3].reset_index()
        grouped['se'] = grouped['std'] / np.sqrt(grouped['count'])
        grouped['ci_lo'] = grouped['median'] - 1.645 * grouped['se']
        grouped['ci_hi'] = grouped['median'] + 1.645 * grouped['se']
        grouped = grouped.sort_values('year')

        ax_b.plot(grouped.year, grouped['median'], color=INCOME_COLORS[ig],
                  label=income_labels_short[ig], linewidth=0.8)
        ax_b.fill_between(grouped.year, grouped.ci_lo, grouped.ci_hi,
                          color=INCOME_COLORS[ig], alpha=0.12)
        for _, r in grouped.iterrows():
            source_b.append({'income_group': ig, 'year': int(r.year),
                             'CPR_median': r['median'], 'CPR_ci_lo': r.ci_lo,
                             'CPR_ci_hi': r.ci_hi, 'n_countries': int(r['count'])})

    ax_b.axhline(y=1, color='k', linestyle='--', linewidth=0.4, alpha=0.6)
    ax_b.set_xlabel('Year')
    ax_b.set_ylabel('Capital price ratio (V/K)')
    ax_b.set_title('CPR by income group (median, 90% CI)', fontsize=7, fontweight='bold')
    ax_b.legend(loc='upper right', frameon=False, fontsize=5, title='Income group',
                title_fontsize=5.5)
    ax_b.set_xlim(1968, 2021)

    # --- (c) GFCF/GDP vs CPR 变化率 ---
    ax_c = fig.add_subplot(gs[0, 2])
    panel_label(ax_c, 'c')

    # 计算每个国家最近 10 年的平均 GFCF/GDP 和 CPR 年均变化率
    recent = valid[valid.year.between(2005, 2019)]
    country_stats = recent.groupby('country_code').agg(
        gfcf_mean=('gfcf_pct_gdp', 'mean'),
        income_group=('income_group', 'first'),
        country_name=('country_name', 'first'),
    ).dropna()

    # CPR 年均变化率: 线性回归斜率 / 均值
    cpr_changes = []
    for cc in country_stats.index:
        sub = recent[recent.country_code == cc].dropna(subset=['CPR']).sort_values('year')
        if len(sub) >= 5:
            slope, _, _, _, _ = stats.linregress(sub.year, sub.CPR)
            mean_cpr = sub.CPR.mean()
            cpr_changes.append({'country_code': cc, 'cpr_annual_change': slope,
                                'cpr_pct_change': slope / mean_cpr * 100 if mean_cpr > 0 else np.nan})
    cpr_df = pd.DataFrame(cpr_changes).set_index('country_code')
    merged = country_stats.join(cpr_df).dropna()

    # 标注重点国家
    highlight = {'CHN': 'China', 'JPN': 'Japan', 'IND': 'India',
                 'USA': 'USA', 'GBR': 'UK', 'VNM': 'Vietnam', 'IDN': 'Indonesia'}

    source_c = []
    for ig in income_order:
        sub = merged[merged.income_group == ig]
        ax_c.scatter(sub.gfcf_mean, sub.cpr_pct_change, color=INCOME_COLORS[ig],
                     s=8, alpha=0.5, edgecolors='none', label=income_labels_short[ig],
                     zorder=2)
        for cc in sub.index:
            source_c.append({'country_code': cc, 'country_name': sub.loc[cc, 'country_name'],
                             'income_group': ig, 'gfcf_pct_gdp': sub.loc[cc, 'gfcf_mean'],
                             'cpr_annual_pct_change': sub.loc[cc, 'cpr_pct_change']})

    # 标注关键国家
    for cc, lbl in highlight.items():
        if cc in merged.index:
            x, y = merged.loc[cc, 'gfcf_mean'], merged.loc[cc, 'cpr_pct_change']
            ax_c.annotate(lbl, (x, y), fontsize=4.5, ha='left', va='bottom',
                          xytext=(2, 2), textcoords='offset points',
                          color=INCOME_COLORS.get(merged.loc[cc, 'income_group'], '#333'))

    ax_c.axhline(y=0, color='k', linestyle='--', linewidth=0.4, alpha=0.6)
    ax_c.set_xlabel('Gross fixed capital formation (% of GDP)')
    ax_c.set_ylabel('CPR annual change (%)')
    ax_c.set_title('Investment intensity vs. CPR trend', fontsize=7, fontweight='bold')
    ax_c.legend(loc='lower left', frameon=False, fontsize=5)

    save_fig(fig, 'fig01_global_landscape')
    # Source data
    src_all = pd.DataFrame(source_a)
    save_source(src_all, 'fig1a')
    save_source(pd.DataFrame(source_b), 'fig1b')
    save_source(pd.DataFrame(source_c), 'fig1c')
    plt.close(fig)


# ############################################################
# FIG 2: China's Regime Shift
# ############################################################
def fig2_china_regime_shift():
    """
    三面板双栏图:
    (a) Q_weighted 时序 + MC 不确定性带 + Q=1 交叉 + Bai-Perron 断点
    (b) Q=1 交叉年份 MC 密度分布
    (c) MUQ 柱状图 (正值蓝，负值橙，标注 value destruction)
    """
    print('\n=== Fig 2: China\'s Regime Shift ===')

    fig = plt.figure(figsize=(DOUBLE_COL, DOUBLE_COL * 0.42))
    gs = GridSpec(1, 3, figure=fig, wspace=0.38, hspace=0.3,
                  left=0.06, right=0.97, top=0.90, bottom=0.15)

    cq = china_q.copy()

    # --- (a) Q_weighted + MC uncertainty band ---
    ax_a = fig.add_subplot(gs[0, 0])
    panel_label(ax_a, 'a')

    # MC 90% CI band
    ax_a.fill_between(cq.year, cq.Q_mc_p05, cq.Q_mc_p95,
                      color=COLORS['blue'], alpha=0.10, label='90% MC interval')
    ax_a.fill_between(cq.year, cq.Q_mc_p25, cq.Q_mc_p75,
                      color=COLORS['blue'], alpha=0.20, label='50% MC interval')
    ax_a.plot(cq.year, cq.Q_weighted, color=COLORS['blue'], linewidth=1.0,
              label='Weighted Q', zorder=5)
    ax_a.plot(cq.year, cq.Q_mc_median, color=COLORS['blue'], linewidth=0.5,
              linestyle=':', label='MC median', zorder=4)

    # Q=1 threshold
    ax_a.axhline(y=1, color='k', linestyle='--', linewidth=0.4, alpha=0.7)
    ax_a.text(1999, 1.03, 'Q = 1', fontsize=5, color='#555555')

    # 寻找 Q_weighted 首次跌破 1 的年份
    cross_years = cq[cq.Q_weighted < 1]
    if len(cross_years) > 0:
        cross_yr = cross_years.iloc[0].year
        ax_a.axvline(x=cross_yr, color=COLORS['red'], linestyle=':', linewidth=0.5, alpha=0.7)
        ax_a.annotate(f'Q < 1\n({int(cross_yr)})', xy=(cross_yr, 1), xytext=(cross_yr - 5, 0.6),
                      fontsize=5, color=COLORS['red'], ha='center',
                      arrowprops=dict(arrowstyle='->', color=COLORS['red'], lw=0.5))

    # Bai-Perron 断点 (从论文分析中标注近似值)
    bp_year = 2010
    ax_a.axvspan(2008, 2012, alpha=0.06, color=COLORS['orange'], zorder=0)
    ax_a.text(2010, cq.Q_weighted.max() * 0.95, 'Structural\nbreak', fontsize=4.5,
              ha='center', color=COLORS['orange'], style='italic')

    ax_a.set_xlabel('Year')
    ax_a.set_ylabel('Urban Tobin\'s Q (V/K)')
    ax_a.set_title('China\'s Q trajectory with uncertainty', fontsize=7, fontweight='bold')
    ax_a.legend(loc='upper right', frameon=False, fontsize=4.5)
    ax_a.set_xlim(1997, 2025)

    # --- (b) MC density of Q=1 crossing year ---
    ax_b = fig.add_subplot(gs[0, 1])
    panel_label(ax_b, 'b')

    # 对每条 MC 轨道模拟 Q=1 交叉年份
    np.random.seed(42)
    n_sim = 5000
    cross_years_mc = []

    for _ in range(n_sim):
        # 模拟每年的 Q 值：在 MC 分位数之间的正态分布
        q_sim = np.random.normal(cq.Q_mc_mean.values,
                                 (cq.Q_mc_p95.values - cq.Q_mc_p05.values) / 3.29)
        below = np.where(q_sim < 1)[0]
        if len(below) > 0:
            cross_years_mc.append(cq.year.values[below[0]])

    cross_years_mc = np.array(cross_years_mc)
    median_cross = np.median(cross_years_mc)
    p05_cross = np.percentile(cross_years_mc, 5)
    p95_cross = np.percentile(cross_years_mc, 95)

    # KDE
    from scipy.stats import gaussian_kde
    if len(cross_years_mc) > 10:
        kde = gaussian_kde(cross_years_mc, bw_method=0.3)
        x_grid = np.linspace(cross_years_mc.min() - 2, cross_years_mc.max() + 2, 200)
        ax_b.fill_between(x_grid, kde(x_grid), color=COLORS['blue'], alpha=0.25)
        ax_b.plot(x_grid, kde(x_grid), color=COLORS['blue'], linewidth=0.8)

    ax_b.axvline(x=median_cross, color=COLORS['red'], linestyle='-', linewidth=0.6)
    ax_b.axvspan(p05_cross, p95_cross, alpha=0.08, color=COLORS['red'])

    # 获取当前 y 轴范围后标注
    ylim = ax_b.get_ylim()
    ax_b.text(median_cross + 0.3, ylim[1] * 0.85 if ylim[1] > 0 else 0.5,
              f'Median: {int(median_cross)}\n90% CI: [{int(p05_cross)}, {int(p95_cross)}]',
              fontsize=5, color=COLORS['red'], va='top')

    ax_b.set_xlabel('Year of Q = 1 crossing')
    ax_b.set_ylabel('Density')
    ax_b.set_title('Monte Carlo distribution of regime shift', fontsize=7, fontweight='bold')
    ax_b.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:.2f}'))

    # --- (c) MUQ bar chart ---
    ax_c = fig.add_subplot(gs[0, 2])
    panel_label(ax_c, 'c')

    # 计算 MUQ from china_q: MUQ = delta_V / delta_K
    cq_muq = cq.copy()
    cq_muq['delta_V'] = cq_muq['V1_adj_mid_100m'].diff()
    cq_muq['delta_K'] = cq_muq['K2_100m'].diff()
    cq_muq['MUQ'] = cq_muq['delta_V'] / cq_muq['delta_K']
    cq_muq = cq_muq.dropna(subset=['MUQ'])

    # 正值蓝色，负值橙色
    colors_bar = [COLORS['blue'] if v >= 0 else COLORS['orange'] for v in cq_muq.MUQ]

    ax_c.bar(cq_muq.year, cq_muq.MUQ, color=colors_bar, width=0.8, edgecolor='none')
    ax_c.axhline(y=0, color='k', linewidth=0.4)

    # 高亮 2022-2024 (value destruction 区间)
    for yr in [2022, 2023, 2024]:
        row = cq_muq[cq_muq.year == yr]
        if len(row) > 0:
            val = row.MUQ.values[0]
            ax_c.bar(yr, val, color=COLORS['red'], width=0.8, edgecolor='none', zorder=5)

    # 标注 value destruction zone
    vd_years = cq_muq[cq_muq.year.between(2022, 2024)]
    if len(vd_years) > 0:
        vd_min = vd_years.MUQ.min()
        ax_c.annotate('Value\ndestruction', xy=(2023, vd_min),
                      xytext=(2015, vd_min * 1.5 if vd_min < 0 else vd_min - 0.5),
                      fontsize=5, color=COLORS['red'], ha='center',
                      arrowprops=dict(arrowstyle='->', color=COLORS['red'], lw=0.5))

    ax_c.set_xlabel('Year')
    ax_c.set_ylabel('Marginal Urban Q (MUQ = \u0394V/\u0394K)')
    ax_c.set_title('Marginal investment efficiency', fontsize=7, fontweight='bold')

    save_fig(fig, 'fig02_china_regime_shift')
    # Source data
    src_a = cq[['year', 'Q_weighted', 'Q_mc_median', 'Q_mc_mean',
                 'Q_mc_p05', 'Q_mc_p25', 'Q_mc_p75', 'Q_mc_p95']].copy()
    save_source(src_a, 'fig2a')
    src_b = pd.DataFrame({'cross_year': cross_years_mc})
    save_source(src_b, 'fig2b')
    src_c = cq_muq[['year', 'MUQ', 'delta_V', 'delta_K']].copy()
    save_source(src_c, 'fig2c')
    plt.close(fig)


# ############################################################
# FIG 3: Overbuilding Across China's Cities
# ############################################################
def fig3_city_overbuilding():
    """
    双面板双栏图:
    (a) 城市 Q 箱线图（按城市等级）+ jitter 散点
    (b) 城市 OCR 箱线图（按等级）
    """
    print('\n=== Fig 3: Overbuilding Across China\'s Cities ===')

    fig = plt.figure(figsize=(DOUBLE_COL, DOUBLE_COL * 0.38))
    gs = GridSpec(1, 2, figure=fig, wspace=0.30, left=0.07, right=0.97,
                  top=0.90, bottom=0.15)

    cp = city_panel.copy()
    cp['tier_order'] = cp['city_tier'].map({t: i for i, t in enumerate(TIER_ORDER)})
    cp = cp.sort_values('tier_order')

    # --- (a) Q 箱线图 ---
    ax_a = fig.add_subplot(gs[0, 0])
    panel_label(ax_a, 'a')

    positions = list(range(len(TIER_ORDER)))
    bp_data = []
    for tier in TIER_ORDER:
        sub = cp[cp.city_tier == tier]['Q_w1'].dropna()
        bp_data.append(sub.values)

    bp = ax_a.boxplot(bp_data, positions=positions, widths=0.5,
                      patch_artist=True, showfliers=False,
                      medianprops=dict(color='k', linewidth=0.7),
                      whiskerprops=dict(linewidth=0.5),
                      capprops=dict(linewidth=0.5))

    for i, (patch, tier) in enumerate(zip(bp['boxes'], TIER_ORDER)):
        patch.set_facecolor(TIER_COLORS[tier])
        patch.set_alpha(0.6)
        patch.set_linewidth(0.5)

        # Jitter scatter
        sub = cp[cp.city_tier == tier]['Q_w1'].dropna()
        jitter = np.random.normal(0, 0.08, len(sub))
        ax_a.scatter(i + jitter, sub.values, color=TIER_COLORS[tier],
                     s=4, alpha=0.3, edgecolors='none', zorder=3)

    ax_a.axhline(y=1, color='k', linestyle='--', linewidth=0.4, alpha=0.7)
    ax_a.text(3.4, 1.08, 'Q = 1', fontsize=5, color='#555555')
    ax_a.set_xticks(positions)
    ax_a.set_xticklabels([TIER_LABELS_EN[t] for t in TIER_ORDER])
    ax_a.set_ylabel('Urban Q (V/K)')
    ax_a.set_title('Urban Q by city tier', fontsize=7, fontweight='bold')

    # --- (b) OCR 箱线图 ---
    ax_b = fig.add_subplot(gs[0, 1])
    panel_label(ax_b, 'b')

    bp_data_ocr = []
    for tier in TIER_ORDER:
        sub = cp[cp.city_tier == tier]['OCR_w1'].dropna()
        bp_data_ocr.append(sub.values)

    bp2 = ax_b.boxplot(bp_data_ocr, positions=positions, widths=0.5,
                       patch_artist=True, showfliers=False,
                       medianprops=dict(color='k', linewidth=0.7),
                       whiskerprops=dict(linewidth=0.5),
                       capprops=dict(linewidth=0.5))

    for i, (patch, tier) in enumerate(zip(bp2['boxes'], TIER_ORDER)):
        patch.set_facecolor(TIER_COLORS[tier])
        patch.set_alpha(0.6)
        patch.set_linewidth(0.5)

        sub = cp[cp.city_tier == tier]['OCR_w1'].dropna()
        jitter = np.random.normal(0, 0.08, len(sub))
        ax_b.scatter(i + jitter, sub.values, color=TIER_COLORS[tier],
                     s=4, alpha=0.3, edgecolors='none', zorder=3)

    ax_b.axhline(y=1, color='k', linestyle='--', linewidth=0.4, alpha=0.7)
    ax_b.text(3.4, 1.08, 'OCR = 1', fontsize=5, color='#555555')
    ax_b.set_xticks(positions)
    ax_b.set_xticklabels([TIER_LABELS_EN[t] for t in TIER_ORDER])
    ax_b.set_ylabel('Overcapitalisation ratio (K/K*)')
    ax_b.set_title('Overcapitalisation ratio by city tier', fontsize=7, fontweight='bold')

    save_fig(fig, 'fig03_city_overbuilding')
    src = cp[['city', 'city_tier', 'Q_w1', 'OCR_w1', 'region4', 'province']].copy()
    src['city_tier_en'] = src.city_tier.map(TIER_LABELS_EN)
    save_source(src, 'fig3')
    plt.close(fig)


# ############################################################
# FIG 4: Staged Efficiency Decline
# ############################################################
def fig4_staged_efficiency():
    """
    双面板双栏图:
    (a) 实际 MUQ 按收入组 x 城镇化阶段的 bar + error bar
    (b) LOESS 非参投资效率曲线（GFCF/GDP vs 实际 MUQ）
    """
    print('\n=== Fig 4: Staged Efficiency Decline ===')

    fig = plt.figure(figsize=(DOUBLE_COL, DOUBLE_COL * 0.38))
    gs = GridSpec(1, 2, figure=fig, wspace=0.30, left=0.08, right=0.97,
                  top=0.90, bottom=0.15)

    # 构建实际 MUQ（复现 36_muq_real_correction.py 的逻辑）
    panel = global_panel.copy()
    panel['deflator'] = panel['gdp_current_usd'] / panel['gdp_constant_2015']
    panel['V2_real'] = panel['rnna'] * 1e6
    panel['K_pim_real'] = panel['K_pim'] / panel['deflator']
    panel['gfcf_real'] = panel['gfcf_current_usd'] / panel['deflator']
    panel['delta_V2_real'] = panel.groupby('country_code')['V2_real'].diff()
    panel['delta_I_real'] = panel.groupby('country_code')['gfcf_real'].diff()
    panel['MUQ_real'] = panel['delta_V2_real'] / panel['delta_I_real']
    extreme = (panel['MUQ_real'].abs() > 20) | (panel['MUQ_real'] < -5)
    panel.loc[extreme, 'MUQ_real'] = np.nan

    stage_order = ['S1: <30%', 'S2: 30-50%', 'S3: 50-70%', 'S4: >70%']
    stage_short = {'S1: <30%': 'S1\n(<30%)', 'S2: 30-50%': 'S2\n(30-50%)',
                   'S3: 50-70%': 'S3\n(50-70%)', 'S4: >70%': 'S4\n(>70%)'}
    income_order = ['Low income', 'Lower middle income', 'Upper middle income', 'High income']
    income_short = {'Low income': 'Low', 'Lower middle income': 'Lower\nmiddle',
                    'Upper middle income': 'Upper\nmiddle', 'High income': 'High'}

    valid = panel.dropna(subset=['MUQ_real', 'urban_stage', 'income_group'])
    valid = valid[valid.income_group.isin(income_order) & valid.urban_stage.isin(stage_order)]

    # --- (a) Grouped bar chart ---
    ax_a = fig.add_subplot(gs[0, 0])
    panel_label(ax_a, 'a')

    n_stages = len(stage_order)
    n_income = len(income_order)
    bar_width = 0.18
    x_base = np.arange(n_stages)

    source_a = []
    for j, ig in enumerate(income_order):
        medians = []
        ci_los = []
        ci_his = []
        for stage in stage_order:
            sub = valid[(valid.income_group == ig) & (valid.urban_stage == stage)]['MUQ_real']
            if len(sub) >= 5:
                med = sub.median()
                q25 = sub.quantile(0.25)
                q75 = sub.quantile(0.75)
            else:
                med = sub.median() if len(sub) > 0 else np.nan
                q25 = med
                q75 = med
            medians.append(med)
            ci_los.append(med - q25 if not np.isnan(med) else 0)
            ci_his.append(q75 - med if not np.isnan(med) else 0)
            source_a.append({'income_group': ig, 'urban_stage': stage,
                             'MUQ_real_median': med, 'Q25': q25, 'Q75': q75, 'n': len(sub)})

        offset = (j - n_income / 2 + 0.5) * bar_width
        ax_a.bar(x_base + offset, medians, bar_width * 0.9,
                 color=INCOME_COLORS[ig], alpha=0.8,
                 label=income_short[ig].replace('\n', ' '))
        ax_a.errorbar(x_base + offset, medians,
                      yerr=[ci_los, ci_his],
                      fmt='none', ecolor='k', elinewidth=0.4, capsize=1.5, capthick=0.4)

    ax_a.axhline(y=0, color='k', linewidth=0.4)
    ax_a.set_xticks(x_base)
    ax_a.set_xticklabels([stage_short[s] for s in stage_order], fontsize=5.5)
    ax_a.set_ylabel('Real MUQ (median, constant 2015 USD)')
    ax_a.set_title('Investment efficiency by urbanisation stage', fontsize=7, fontweight='bold')
    ax_a.legend(loc='upper right', frameon=False, fontsize=5, ncol=2,
                title='Income group', title_fontsize=5)

    # --- (b) LOESS curves ---
    ax_b = fig.add_subplot(gs[0, 1])
    panel_label(ax_b, 'b')

    valid_loess = valid.dropna(subset=['gfcf_pct_gdp', 'MUQ_real'])
    valid_loess = valid_loess[(valid_loess.gfcf_pct_gdp > 5) & (valid_loess.gfcf_pct_gdp < 60)]

    source_b = []
    for ig in income_order:
        sub = valid_loess[valid_loess.income_group == ig]
        if len(sub) < 20:
            continue

        sorted_sub = sub.sort_values('gfcf_pct_gdp')
        result = lowess(sorted_sub.MUQ_real.values, sorted_sub.gfcf_pct_gdp.values,
                        frac=0.5, return_sorted=True)
        ax_b.plot(result[:, 0], result[:, 1], color=INCOME_COLORS[ig],
                  linewidth=1.0, label=income_short[ig].replace('\n', ' '))
        ax_b.scatter(sub.gfcf_pct_gdp, sub.MUQ_real, color=INCOME_COLORS[ig],
                     s=2, alpha=0.08, edgecolors='none')

        for x, y in result:
            source_b.append({'income_group': ig, 'gfcf_pct_gdp': x, 'MUQ_real_loess': y})

    ax_b.axhline(y=0, color='k', linewidth=0.4, linestyle='--', alpha=0.5)
    ax_b.set_xlabel('Gross fixed capital formation (% of GDP)')
    ax_b.set_ylabel('Real MUQ (LOESS smoothed)')
    ax_b.set_title('Investment intensity vs. marginal efficiency', fontsize=7, fontweight='bold')
    ax_b.legend(loc='upper right', frameon=False, fontsize=5)

    save_fig(fig, 'fig04_staged_efficiency')
    save_source(pd.DataFrame(source_a), 'fig4a')
    save_source(pd.DataFrame(source_b), 'fig4b')
    plt.close(fig)


# ############################################################
# FIG 5: Early Warning and Carbon Cost
# ############################################################
def fig5_ews_carbon():
    """
    双面板双栏图:
    (a) 中国 + 日本 AR(1) 滚动窗口时序 (EWS)
    (b) 中国过度建设累计碳成本时序
    """
    print('\n=== Fig 5: Early Warning and Carbon Cost ===')

    fig = plt.figure(figsize=(DOUBLE_COL, DOUBLE_COL * 0.38))
    gs = GridSpec(1, 2, figure=fig, wspace=0.30, left=0.08, right=0.97,
                  top=0.90, bottom=0.15)

    # ===== (a) EWS: AR(1) rolling window =====
    ax_a = fig.add_subplot(gs[0, 0])
    panel_label(ax_a, 'a')

    gp = global_panel.copy()
    window = 8  # 8年滚动窗口

    source_a = []
    for cc, label, color in [('CHN', 'China', COLORS['blue']),
                              ('JPN', 'Japan', COLORS['orange'])]:
        sub = gp[(gp.country_code == cc)].dropna(subset=['CPR']).sort_values('year')
        cpr_vals = sub.CPR.values
        years = sub.year.values

        ar1_vals = []
        ar1_years = []
        for i in range(window, len(cpr_vals)):
            segment = cpr_vals[i - window:i]
            if len(segment) >= window:
                corr = np.corrcoef(segment[:-1], segment[1:])[0, 1]
                ar1_vals.append(corr)
                ar1_years.append(years[i])
                source_a.append({'country': cc, 'year': int(years[i]), 'AR1': corr})

        ax_a.plot(ar1_years, ar1_vals, color=color, linewidth=0.9, label=label)

    # CPR 峰值年份标注
    chn_cpr = gp[gp.country_code == 'CHN'].dropna(subset=['CPR']).sort_values('year')
    jpn_cpr = gp[gp.country_code == 'JPN'].dropna(subset=['CPR']).sort_values('year')
    chn_peak_yr = chn_cpr.loc[chn_cpr.CPR.idxmax(), 'year']
    jpn_peak_yr = jpn_cpr.loc[jpn_cpr.CPR.idxmax(), 'year']

    ax_a.axvline(x=chn_peak_yr, color=COLORS['blue'], linestyle=':', linewidth=0.5, alpha=0.6)
    ax_a.axvline(x=jpn_peak_yr, color=COLORS['orange'], linestyle=':', linewidth=0.5, alpha=0.6)
    ax_a.text(chn_peak_yr + 0.5, 0.95, f'China\nCPR peak\n({int(chn_peak_yr)})',
              fontsize=4.5, color=COLORS['blue'], va='top')
    ax_a.text(jpn_peak_yr - 0.5, -0.65, f'Japan\nCPR peak\n({int(jpn_peak_yr)})',
              fontsize=4.5, color=COLORS['orange'], va='bottom', ha='right')

    ax_a.axhline(y=0, color='k', linestyle='--', linewidth=0.3, alpha=0.5)
    ax_a.set_xlabel('Year')
    ax_a.set_ylabel(f'Rolling AR(1) coefficient ({window}-year window)')
    ax_a.set_title('Early warning signal: critical slowing down', fontsize=7, fontweight='bold')
    ax_a.legend(loc='lower left', frameon=False, fontsize=5.5)
    ax_a.set_ylim(-1.0, 1.1)

    # ===== (b) Carbon cost =====
    ax_b = fig.add_subplot(gs[0, 1])
    panel_label(ax_b, 'b')

    cq = china_q.copy()
    INTENSITY = 0.65  # tCO2/万元
    china_total = {
        2000: 3.4, 2001: 3.5, 2002: 3.7, 2003: 4.1, 2004: 4.7,
        2005: 5.4, 2006: 5.9, 2007: 6.3, 2008: 6.5, 2009: 6.8,
        2010: 7.5, 2011: 8.1, 2012: 8.5, 2013: 8.9, 2014: 9.0,
        2015: 9.0, 2016: 9.1, 2017: 9.3, 2018: 9.6, 2019: 9.9,
        2020: 10.0, 2021: 10.7, 2022: 10.9, 2023: 11.5, 2024: 11.6,
    }

    cq['Kstar_100m'] = cq['V1_adj_mid_100m']
    cq['excess_K'] = np.maximum(0, cq['K2_100m'] - cq['Kstar_100m'])
    cq['delta_excess_K'] = cq['excess_K'].diff()
    first_excess = cq[cq['excess_K'] > 0].index
    if len(first_excess) > 0:
        fi = first_excess[0]
        if pd.isna(cq.loc[fi, 'delta_excess_K']) or cq.loc[fi, 'delta_excess_K'] == 0:
            cq.loc[fi, 'delta_excess_K'] = cq.loc[fi, 'excess_K']

    cq['annual_carbon_Mt'] = np.maximum(0, cq['delta_excess_K']) * 10000 * INTENSITY / 1e6
    cq['cumul_carbon_Mt'] = cq['annual_carbon_Mt'].cumsum()
    cq['china_total_Gt'] = cq['year'].map(china_total)
    cq['pct_of_total'] = cq['annual_carbon_Mt'] / (cq['china_total_Gt'] * 1000) * 100

    carb = cq[cq.year.between(2000, 2024)].copy()

    # 双轴：左轴累计碳排放，右轴占比
    color_cum = COLORS['red']
    color_pct = COLORS['blue']

    ax_b.fill_between(carb.year, 0, carb.cumul_carbon_Mt / 1000,
                      color=color_cum, alpha=0.2, step='mid')
    line1, = ax_b.plot(carb.year, carb.cumul_carbon_Mt / 1000, color=color_cum,
                       linewidth=1.0, label='Cumulative excess CO\u2082')
    ax_b.set_ylabel('Cumulative excess CO\u2082 (GtCO\u2082)', color=color_cum)
    ax_b.tick_params(axis='y', labelcolor=color_cum)

    # 标注最终累计值
    final_val = carb.cumul_carbon_Mt.iloc[-1] / 1000
    ax_b.annotate(f'Cumulative:\n{final_val:.1f} GtCO\u2082',
                  xy=(2024, final_val), xytext=(2015, final_val * 0.85),
                  fontsize=5.5, color=color_cum, fontweight='bold',
                  arrowprops=dict(arrowstyle='->', color=color_cum, lw=0.5))

    # 右轴：年度占比
    ax_b2 = ax_b.twinx()
    line2, = ax_b2.plot(carb.year, carb.pct_of_total, color=color_pct,
                        linewidth=0.7, linestyle='--', label='% of China total')
    ax_b2.set_ylabel('Share of China total emissions (%)', color=color_pct)
    ax_b2.tick_params(axis='y', labelcolor=color_pct)
    ax_b2.spines['right'].set_visible(True)
    ax_b2.spines['right'].set_linewidth(0.5)

    # 标注峰值占比
    peak_idx = carb.pct_of_total.idxmax()
    peak_yr = carb.loc[peak_idx, 'year']
    peak_pct = carb.loc[peak_idx, 'pct_of_total']
    ax_b2.annotate(f'Peak: {peak_pct:.1f}%\n({int(peak_yr)})',
                   xy=(peak_yr, peak_pct), xytext=(peak_yr - 6, peak_pct * 1.1),
                   fontsize=5, color=color_pct,
                   arrowprops=dict(arrowstyle='->', color=color_pct, lw=0.5))

    ax_b.set_xlabel('Year')
    ax_b.set_title('Carbon cost of overbuilding', fontsize=7, fontweight='bold')

    lines = [line1, line2]
    labels = [l.get_label() for l in lines]
    ax_b.legend(lines, labels, loc='upper left', frameon=False, fontsize=5)

    save_fig(fig, 'fig05_ews_carbon')
    save_source(pd.DataFrame(source_a), 'fig5a')
    src_b = carb[['year', 'Q_weighted', 'excess_K', 'annual_carbon_Mt',
                   'cumul_carbon_Mt', 'pct_of_total']].copy()
    src_b.columns = ['year', 'Q_weighted', 'excess_K_100m_yuan',
                     'annual_excess_CO2_Mt', 'cumulative_excess_CO2_Mt',
                     'pct_of_china_total']
    save_source(src_b, 'fig5b')
    plt.close(fig)


# ============================================================
# 主函数
# ============================================================
def main():
    print('=' * 60)
    print('Generating Nature main figures (5 figures)')
    print('=' * 60)

    fig1_global_landscape()
    fig2_china_regime_shift()
    fig3_city_overbuilding()
    fig4_staged_efficiency()
    fig5_ews_carbon()

    print('\n' + '=' * 60)
    print('All 5 figures generated successfully.')
    print(f'PDF + PNG: {FIG_OUT}/')
    print(f'Source data: {SRC_OUT}/')
    print('=' * 60)


if __name__ == '__main__':
    main()
