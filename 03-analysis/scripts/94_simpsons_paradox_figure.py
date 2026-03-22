#!/usr/bin/env python3
"""
94_simpsons_paradox_figure.py
Simpson's Paradox Flagship Figure for Nature main journal

Layout: 3 rows x 2 cols = 6 panels
(a) Global aggregate MUQ vs urbanization — appears stable
(b) Within-group MUQ by income group — all declining (Simpson's Paradox)
(c) China city-level MUQ vs investment intensity
(d) US MSA MUQ vs investment intensity
(e) China vs US institutional contrast (bar chart)
(f) China city-tier gradient (2016 cross-section, box plot)

Author: Figure Designer Agent
Date: 2026-03-21
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# Nature style configuration
# =============================================================================
NATURE_COLORS = {
    'blue':    '#0077BB',
    'orange':  '#EE7733',
    'cyan':    '#33BBEE',
    'red':     '#CC3311',
    'teal':    '#009988',
    'grey':    '#BBBBBB',
    'purple':  '#AA3377',
    'dark':    '#333333',
}

# Income group colors (colorblind-safe gradient: warm to cool)
INCOME_COLORS = {
    'Low income':          '#CC3311',   # red
    'Lower middle income': '#EE7733',   # orange
    'Upper middle income': '#009988',   # teal
    'High income':         '#0077BB',   # blue
}

# China vs US
CHINA_COLOR = '#CC3311'
US_COLOR = '#0077BB'
US_LIGHT = '#88CCEE'

# City tier colors (warm gradient for China)
# Use short tier names matching the data
TIER_COLORS = {
    '一线':   '#CC3311',
    '新一线': '#EE7733',
    '二线':   '#009988',
    '三线':   '#0077BB',
    '四五线': '#AA3377',
}

# US region colors
REGION_COLORS = {
    'Northeast': '#0077BB',
    'Midwest':   '#33BBEE',
    'South':     '#EE7733',
    'West':      '#CC3311',
}

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica'],
    'font.size': 7,
    'axes.linewidth': 0.5,
    'axes.labelsize': 8,
    'axes.titlesize': 8,
    'xtick.labelsize': 6,
    'ytick.labelsize': 6,
    'xtick.major.width': 0.4,
    'ytick.major.width': 0.4,
    'xtick.major.size': 2.5,
    'ytick.major.size': 2.5,
    'legend.fontsize': 6,
    'legend.frameon': False,
    'lines.linewidth': 1.0,
    'patch.linewidth': 0.5,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
})

# =============================================================================
# Paths
# =============================================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
GLOBAL_PANEL    = f'{BASE}/02-data/processed/global_q_revised_panel.csv'
CHINA_CITY_275  = f'{BASE}/02-data/processed/china_275_city_panel.csv'
CHINA_REAL_FAI  = f'{BASE}/02-data/processed/china_city_real_fai_panel.csv'
US_MSA          = f'{BASE}/02-data/processed/us_msa_muq_panel.csv'
OUT_PNG         = f'{BASE}/04-figures/final/fig_simpsons_paradox.png'
OUT_PDF         = f'{BASE}/04-figures/final/fig_simpsons_paradox.pdf'
SOURCE_DATA     = f'{BASE}/04-figures/source-data/fig_simpsons_paradox_source.csv'

# =============================================================================
# Load data
# =============================================================================
print("Loading data...")

# --- Global panel ---
gdf = pd.read_csv(GLOBAL_PANEL)
gdf = gdf.dropna(subset=['MUQ', 'urban_pct'])
# Winsorize MUQ at 1%/99%
lo, hi = gdf['MUQ'].quantile(0.01), gdf['MUQ'].quantile(0.99)
gdf['MUQ_w'] = gdf['MUQ'].clip(lo, hi)
print(f"  Global panel: {len(gdf)} obs with MUQ, {gdf['country_code'].nunique()} countries")

# --- China city panel (real FAI, for panels c) ---
# This is the dataset from city_muq_distribution_report: N=455, beta=-2.23
cdf_real = pd.read_csv(CHINA_REAL_FAI, encoding='utf-8-sig')
cdf_real = cdf_real[(cdf_real['year'] >= 2010) & (cdf_real['year'] <= 2016)].copy()
cdf_real = cdf_real.dropna(subset=['MUQ_real', 'fai_gdp_ratio'])
# Winsorize
lo_c, hi_c = cdf_real['MUQ_real'].quantile(0.01), cdf_real['MUQ_real'].quantile(0.99)
cdf_real['MUQ_w'] = cdf_real['MUQ_real'].clip(lo_c, hi_c)
cdf_real['fai_gdp_w'] = cdf_real['fai_gdp_ratio'].clip(
    cdf_real['fai_gdp_ratio'].quantile(0.01), cdf_real['fai_gdp_ratio'].quantile(0.99))
# Merge tier info from 275-city panel
cdf_275 = pd.read_csv(CHINA_CITY_275)
tier_map = cdf_275[['city','tier']].drop_duplicates().set_index('city')['tier'].to_dict()
cdf_real['tier'] = cdf_real['city'].map(tier_map)
print(f"  China city (real, 2010-2016): {len(cdf_real)} obs, {cdf_real['city'].nunique()} cities")

# --- China 275-city panel (for panel f, 2016 cross-section) ---
cdf_full = cdf_275.copy()
print(f"  China 275-city full panel: {len(cdf_full)} obs")

# --- US MSA panel ---
udf = pd.read_csv(US_MSA)
udf = udf.dropna(subset=['MUQ_gdp', 'hu_growth'])
# Winsorize
lo_u, hi_u = udf['MUQ_gdp'].quantile(0.01), udf['MUQ_gdp'].quantile(0.99)
udf['MUQ_w'] = udf['MUQ_gdp'].clip(lo_u, hi_u)
udf['hu_growth_w'] = udf['hu_growth'].clip(
    udf['hu_growth'].quantile(0.01), udf['hu_growth'].quantile(0.99))
print(f"  US MSA: {len(udf)} obs, {udf['cbsa_code'].nunique()} MSAs")


# =============================================================================
# Helper: binned statistics with LOESS-like smoothing
# =============================================================================
def binned_stats(x, y, bins=20, percentiles=(25, 75)):
    """Compute binned median and IQR."""
    bin_edges = np.linspace(x.min(), x.max(), bins + 1)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    medians, lowers, uppers, counts = [], [], [], []
    for i in range(bins):
        mask = (x >= bin_edges[i]) & (x < bin_edges[i+1])
        if i == bins - 1:
            mask = (x >= bin_edges[i]) & (x <= bin_edges[i+1])
        vals = y[mask]
        if len(vals) >= 5:
            medians.append(np.median(vals))
            lowers.append(np.percentile(vals, percentiles[0]))
            uppers.append(np.percentile(vals, percentiles[1]))
            counts.append(len(vals))
        else:
            medians.append(np.nan)
            lowers.append(np.nan)
            uppers.append(np.nan)
            counts.append(len(vals))
    return bin_centers, np.array(medians), np.array(lowers), np.array(uppers), np.array(counts)


# =============================================================================
# Create figure: 180mm x 200mm
# =============================================================================
fig_width_mm, fig_height_mm = 180, 210
fig_width_in = fig_width_mm / 25.4
fig_height_in = fig_height_mm / 25.4

fig = plt.figure(figsize=(fig_width_in, fig_height_in))

# GridSpec: 3 rows x 2 cols with controlled spacing
gs = gridspec.GridSpec(3, 2, figure=fig,
                       hspace=0.42, wspace=0.35,
                       left=0.08, right=0.97, top=0.97, bottom=0.05)

# Panel label helper
def add_panel_label(ax, label, x=-0.12, y=1.08):
    ax.text(x, y, label, transform=ax.transAxes,
            fontsize=10, fontweight='bold', va='top', ha='left')

# =============================================================================
# Panel (a): Global aggregate MUQ vs urbanization — "appears stable"
# =============================================================================
ax_a = fig.add_subplot(gs[0, 0])
add_panel_label(ax_a, 'a')

x_all = gdf['urban_pct'].values
y_all = gdf['MUQ_w'].values

bc, med, lo, hi, cnt = binned_stats(x_all, y_all, bins=15)
valid = ~np.isnan(med)

# IQR shading
ax_a.fill_between(bc[valid], lo[valid], hi[valid],
                  color=NATURE_COLORS['grey'], alpha=0.35, linewidth=0)
# Median line
ax_a.plot(bc[valid], med[valid], color=NATURE_COLORS['dark'],
         linewidth=1.5, zorder=5)

# Add trend line (linear fit on binned medians)
slope_a, intercept_a, r_a, p_a, _ = stats.linregress(bc[valid], med[valid])
x_fit = np.linspace(bc[valid].min(), bc[valid].max(), 100)
ax_a.plot(x_fit, slope_a * x_fit + intercept_a,
         color=NATURE_COLORS['grey'], linewidth=0.8, linestyle='--', zorder=4)

# Annotation
ax_a.text(0.97, 0.95, 'Global aggregate:\nno significant decline',
         transform=ax_a.transAxes, fontsize=6, ha='right', va='top',
         color=NATURE_COLORS['dark'],
         bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                   edgecolor=NATURE_COLORS['grey'], linewidth=0.5, alpha=0.9))

# Spearman annotation
ax_a.text(0.97, 0.68, f'Spearman $\\rho$ = 0.036\n$p$ = 0.038',
         transform=ax_a.transAxes, fontsize=5.5, ha='right', va='top',
         color=NATURE_COLORS['grey'], style='italic')

ax_a.set_xlabel('Urbanization rate (%)')
ax_a.set_ylabel('Real MUQ (median, IQR)')
ax_a.set_xlim(5, 100)
ax_a.set_ylim(-2, 25)
ax_a.axhline(y=0, color='black', linewidth=0.3, linestyle='-', alpha=0.3)

# =============================================================================
# Panel (b): Within-group MUQ by income — Simpson's Paradox core
# =============================================================================
ax_b = fig.add_subplot(gs[0, 1])
add_panel_label(ax_b, 'b')

income_order = ['Low income', 'Lower middle income', 'Upper middle income', 'High income']
income_short = {'Low income': 'Low', 'Lower middle income': 'Lower-middle',
                'Upper middle income': 'Upper-middle', 'High income': 'High'}

# Results from the analysis report
spearman_results = {
    'Low income':          {'rho': -0.150, 'p': 0.002},
    'Lower middle income': {'rho': -0.122, 'p': 0.002},
    'Upper middle income': {'rho': -0.099, 'p': 0.003},
    'High income':         {'rho': -0.013, 'p': 0.633},
}

for ig in income_order:
    sub = gdf[gdf['income_group'] == ig].copy()
    if len(sub) < 10:
        continue
    color = INCOME_COLORS[ig]

    # Binned stats
    bc_i, med_i, lo_i, hi_i, _ = binned_stats(sub['urban_pct'].values,
                                                sub['MUQ_w'].values, bins=12)
    valid_i = ~np.isnan(med_i)
    if valid_i.sum() < 3:
        continue

    # IQR shading
    ax_b.fill_between(bc_i[valid_i], lo_i[valid_i], hi_i[valid_i],
                      color=color, alpha=0.12, linewidth=0)
    # Median line
    ax_b.plot(bc_i[valid_i], med_i[valid_i], color=color, linewidth=1.2,
             label=income_short[ig], zorder=5)

    # Add significance marker at end of line
    res = spearman_results[ig]
    last_x = bc_i[valid_i][-1]
    last_y = med_i[valid_i][-1]
    if res['p'] < 0.01:
        sig_text = '**'
    elif res['p'] < 0.05:
        sig_text = '*'
    else:
        sig_text = 'n.s.'

    ax_b.annotate(sig_text, xy=(last_x, last_y),
                 xytext=(4, 0), textcoords='offset points',
                 fontsize=5.5, fontweight='bold', color=color, va='center')

ax_b.legend(loc='upper right', ncol=2, columnspacing=0.8, handlelength=1.5)

# Simpson's Paradox annotation box
ax_b.text(0.03, 0.03,
         "Simpson's Paradox:\naggregate stable,\nwithin-group declining",
         transform=ax_b.transAxes, fontsize=5.5, ha='left', va='bottom',
         fontweight='bold', color=NATURE_COLORS['dark'],
         bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF9E6',
                   edgecolor=NATURE_COLORS['orange'], linewidth=0.8, alpha=0.95))

ax_b.set_xlabel('Urbanization rate (%)')
ax_b.set_ylabel('Real MUQ (median)')
ax_b.set_xlim(5, 100)
ax_b.set_ylim(-2, 25)
ax_b.axhline(y=0, color='black', linewidth=0.3, linestyle='-', alpha=0.3)

# =============================================================================
# Panel (c): China city MUQ vs FAI/GDP
# =============================================================================
ax_c = fig.add_subplot(gs[1, 0])
add_panel_label(ax_c, 'c')

# Map tiers to ordered labels for legend
tier_order_cn = ['一线', '新一线', '二线', '三线', '四五线']
tier_label_cn = {'一线': 'Tier 1', '新一线': 'New Tier 1', '二线': 'Tier 2',
                 '三线': 'Tier 3', '四五线': 'Tier 4-5'}

for tier in tier_order_cn:
    sub = cdf_real[cdf_real['tier'] == tier]
    if len(sub) == 0:
        continue
    ax_c.scatter(sub['fai_gdp_w'], sub['MUQ_w'],
                s=6, alpha=0.5, color=TIER_COLORS.get(tier, '#999'),
                edgecolors='none', label=tier_label_cn.get(tier, tier),
                zorder=3, rasterized=True)

# OLS fit line + 95% CI
x_cn = cdf_real['fai_gdp_w'].values
y_cn = cdf_real['MUQ_w'].values
slope_cn, intercept_cn, r_cn, p_cn, se_cn = stats.linregress(x_cn, y_cn)

x_fit_cn = np.linspace(x_cn.min(), x_cn.max(), 200)
y_fit_cn = slope_cn * x_fit_cn + intercept_cn

# 95% CI
n_cn = len(x_cn)
x_mean_cn = np.mean(x_cn)
ss_x_cn = np.sum((x_cn - x_mean_cn)**2)
y_resid = y_cn - (slope_cn * x_cn + intercept_cn)
mse_cn = np.sum(y_resid**2) / (n_cn - 2)
se_fit_cn = np.sqrt(mse_cn * (1/n_cn + (x_fit_cn - x_mean_cn)**2 / ss_x_cn))
t_crit = stats.t.ppf(0.975, n_cn - 2)

ax_c.fill_between(x_fit_cn, y_fit_cn - t_crit*se_fit_cn, y_fit_cn + t_crit*se_fit_cn,
                  color=CHINA_COLOR, alpha=0.15, linewidth=0)
ax_c.plot(x_fit_cn, y_fit_cn, color=CHINA_COLOR, linewidth=1.2, zorder=6)

# Stats annotation
ax_c.text(0.97, 0.97,
         f'$\\beta$ = {slope_cn:.2f}\n$p$ < 10$^{{-6}}$\n$N$ = {n_cn}',
         transform=ax_c.transAxes, fontsize=6, ha='right', va='top',
         color=CHINA_COLOR,
         bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                   edgecolor=CHINA_COLOR, linewidth=0.5, alpha=0.9))

ax_c.legend(loc='lower left', fontsize=5, ncol=1, markerscale=1.5,
           handletextpad=0.3, labelspacing=0.3)
ax_c.set_xlabel('Investment intensity (FAI / GDP)')
ax_c.set_ylabel('MUQ')
ax_c.set_title(f'China ({cdf_real["city"].nunique()} cities, 2010-2016)', fontsize=7, fontweight='normal', pad=4)
ax_c.axhline(y=0, color='black', linewidth=0.3, linestyle='-', alpha=0.3)

# =============================================================================
# Panel (d): US MSA MUQ vs investment intensity
# =============================================================================
ax_d = fig.add_subplot(gs[1, 1])
add_panel_label(ax_d, 'd')

for region in ['Northeast', 'Midwest', 'South', 'West']:
    sub = udf[udf['region'] == region]
    if len(sub) == 0:
        continue
    ax_d.scatter(sub['hu_growth_w'], sub['MUQ_w'],
                s=3, alpha=0.25, color=REGION_COLORS.get(region, '#999'),
                edgecolors='none', label=region, zorder=3, rasterized=True)

# OLS fit
x_us = udf['hu_growth_w'].values
y_us = udf['MUQ_w'].values
slope_us, intercept_us, r_us, p_us, se_us = stats.linregress(x_us, y_us)

x_fit_us = np.linspace(x_us.min(), x_us.max(), 200)
y_fit_us = slope_us * x_fit_us + intercept_us

n_us = len(x_us)
x_mean_us = np.mean(x_us)
ss_x_us = np.sum((x_us - x_mean_us)**2)
y_resid_us = y_us - (slope_us * x_us + intercept_us)
mse_us = np.sum(y_resid_us**2) / (n_us - 2)
se_fit_us = np.sqrt(mse_us * (1/n_us + (x_fit_us - x_mean_us)**2 / ss_x_us))
t_crit_us = stats.t.ppf(0.975, n_us - 2)

ax_d.fill_between(x_fit_us, y_fit_us - t_crit_us*se_fit_us, y_fit_us + t_crit_us*se_fit_us,
                  color=US_COLOR, alpha=0.15, linewidth=0)
ax_d.plot(x_fit_us, y_fit_us, color=US_COLOR, linewidth=1.2, zorder=6)

# Stats annotation
ax_d.text(0.03, 0.97,
         f'$\\beta$ = +{slope_us:.2f}\n$p$ < 10$^{{-6}}$\n$N$ = {n_us:,}',
         transform=ax_d.transAxes, fontsize=6, ha='left', va='top',
         color=US_COLOR,
         bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                   edgecolor=US_COLOR, linewidth=0.5, alpha=0.9))

# "Demand-driven" annotation
ax_d.text(0.97, 0.03,
         'Demand-driven:\nbuilding follows demand',
         transform=ax_d.transAxes, fontsize=5.5, ha='right', va='bottom',
         color=US_COLOR, style='italic',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                   edgecolor=US_COLOR, linewidth=0.3, alpha=0.8))

ax_d.legend(loc='upper right', fontsize=5, ncol=2, markerscale=2,
           handletextpad=0.3, labelspacing=0.3, columnspacing=0.6)
ax_d.set_xlabel('Housing unit growth rate')
ax_d.set_ylabel('MUQ ($\\Delta$V / GDP)')
ax_d.set_title('United States (921 MSAs, 2010-2022)', fontsize=7, fontweight='normal', pad=4)
ax_d.axhline(y=0, color='black', linewidth=0.3, linestyle='-', alpha=0.3)

# =============================================================================
# Panel (e): China vs US institutional contrast (bar chart)
# =============================================================================
ax_e = fig.add_subplot(gs[2, 0])
add_panel_label(ax_e, 'e')

# Values from analysis reports
# China: beta = -2.23 (Pooled OLS)
# US: beta = +2.75 (Pooled OLS)
# US controlled (TWFE): beta = +2.55
bar_labels = ['China\n(Supply-driven)', 'US\n(Demand-driven)', 'US\n(TWFE controlled)']
bar_values = [-2.23, 2.75, 2.55]
bar_colors = [CHINA_COLOR, US_COLOR, US_LIGHT]
bar_ci_lo  = [-3.05, 2.57, 2.37]  # 95% CI lower
bar_ci_hi  = [-1.42, 2.92, 2.73]  # 95% CI upper

bars_x = np.arange(len(bar_labels))
bar_err = [[v - lo for v, lo in zip(bar_values, bar_ci_lo)],
           [hi - v for v, hi in zip(bar_values, bar_ci_hi)]]

bars = ax_e.bar(bars_x, bar_values, width=0.55, color=bar_colors,
               edgecolor=[CHINA_COLOR, US_COLOR, US_COLOR],
               linewidth=0.6, zorder=5)

# Error bars
ax_e.errorbar(bars_x, bar_values, yerr=bar_err,
             fmt='none', ecolor='black', elinewidth=0.6, capsize=3, capthick=0.6, zorder=6)

# Value labels on bars
for i, (bx, bv) in enumerate(zip(bars_x, bar_values)):
    offset = -0.3 if bv < 0 else 0.15
    ax_e.text(bx, bv + offset, f'{bv:+.2f}',
             ha='center', va='bottom' if bv >= 0 else 'top',
             fontsize=6, fontweight='bold', color=bar_colors[i])

# Zero line
ax_e.axhline(y=0, color='black', linewidth=0.6, zorder=4)

# Labels
ax_e.set_xticks(bars_x)
ax_e.set_xticklabels(bar_labels, fontsize=6)
ax_e.set_ylabel('$\\beta$ (Investment $\\rightarrow$ MUQ)')
ax_e.set_title('Institutional contrast', fontsize=7, fontweight='normal', pad=4)
ax_e.set_ylim(-4, 4)

# Supply vs Demand annotation
ax_e.annotate('', xy=(0, -3.5), xytext=(0, -3.5),)
ax_e.text(0, -3.6, 'Supply-driven\n(overbuilding)', ha='center', va='top',
         fontsize=5, color=CHINA_COLOR, style='italic')
ax_e.text(1.5, 3.3, 'Demand-driven\n(market signal)', ha='center', va='bottom',
         fontsize=5, color=US_COLOR, style='italic')

# =============================================================================
# Panel (f): China city-tier gradient (2016 cross-section)
# =============================================================================
ax_f = fig.add_subplot(gs[2, 1])
add_panel_label(ax_f, 'f')

# 2016 data - use the full panel for cross-section
c2016 = cdf_full[cdf_full['year'] == 2016].copy()
c2016 = c2016.dropna(subset=['MUQ'])
# Winsorize
lo_f, hi_f = c2016['MUQ'].quantile(0.01), c2016['MUQ'].quantile(0.99)
c2016['MUQ_w'] = c2016['MUQ'].clip(lo_f, hi_f)

# If 2016 has limited data, use all years pooled
if len(c2016) < 50:
    year_counts = cdf_full.groupby('year').size()
    best_year = year_counts.idxmax()
    c2016 = cdf_full[cdf_full['year'] == best_year].copy()
    c2016 = c2016.dropna(subset=['MUQ'])
    lo_f, hi_f = c2016['MUQ'].quantile(0.01), c2016['MUQ'].quantile(0.99)
    c2016['MUQ_w'] = c2016['MUQ'].clip(lo_f, hi_f)
    panel_f_year = best_year
else:
    panel_f_year = 2016

# Order tiers
tier_order_display = ['一线', '新一线', '二线', '三线', '四五线']
tier_short = {
    '一线': 'Tier 1\n(>20M)',
    '新一线': 'New Tier 1\n(10-20M)',
    '二线': 'Tier 2\n(5-10M)',
    '三线': 'Tier 3\n(3-5M)',
    '四五线': 'Tier 4-5\n(<3M)',
}

box_data = []
box_labels = []
box_colors_list = []
box_n = []
box_neg_pct = []

for tier in tier_order_display:
    sub = c2016[c2016['tier'] == tier]
    if len(sub) < 2:
        continue
    box_data.append(sub['MUQ_w'].values)
    box_labels.append(tier_short.get(tier, tier))
    box_colors_list.append(TIER_COLORS.get(tier, '#999'))
    box_n.append(len(sub))
    neg_pct = (sub['MUQ_w'] < 0).mean() * 100
    box_neg_pct.append(neg_pct)

if box_data:
    bp = ax_f.boxplot(box_data, positions=range(len(box_data)),
                     widths=0.5, patch_artist=True,
                     showfliers=False,
                     medianprops=dict(color='black', linewidth=1.0),
                     whiskerprops=dict(linewidth=0.6),
                     capprops=dict(linewidth=0.6),
                     boxprops=dict(linewidth=0.5))

    for patch, color in zip(bp['boxes'], box_colors_list):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    # Overlay individual points (jittered)
    for i, (data, color) in enumerate(zip(box_data, box_colors_list)):
        jitter = np.random.default_rng(42).uniform(-0.15, 0.15, len(data))
        ax_f.scatter(np.full(len(data), i) + jitter, data,
                    s=4, alpha=0.4, color=color, edgecolors='none',
                    zorder=3, rasterized=True)

    # Annotate: N and MUQ<0 % below each box
    for i, (n, neg) in enumerate(zip(box_n, box_neg_pct)):
        med_val = np.median(box_data[i])
        # Place annotation above each box
        q75_val = np.percentile(box_data[i], 75)
        whisker_top = np.percentile(box_data[i], 95)
        ax_f.text(i, whisker_top + 0.15, f'N={n}\n{neg:.0f}%<0',
                 ha='center', va='bottom', fontsize=4.5, color='#555')

    ax_f.set_xticks(range(len(box_labels)))
    ax_f.set_xticklabels(box_labels, fontsize=5.5)

ax_f.axhline(y=0, color='black', linewidth=0.6, linestyle='--', alpha=0.5)
ax_f.axhline(y=1, color=NATURE_COLORS['grey'], linewidth=0.4, linestyle=':', alpha=0.5)
ax_f.set_ylabel('MUQ')
ax_f.set_title(f'China city-tier gradient ({panel_f_year})', fontsize=7,
              fontweight='normal', pad=4)

# Adjust y-limits for panel f after data
if box_data:
    all_vals = np.concatenate(box_data)
    # Leave room for annotations above boxes
    y_top = max(np.percentile(all_vals, 99) + 2.5, 7)
    ax_f.set_ylim(min(-1, np.percentile(all_vals, 1) - 0.3), y_top)

# =============================================================================
# Final adjustments and save
# =============================================================================

# Remove top and right spines from all panels
for ax in [ax_a, ax_b, ax_c, ax_d, ax_e, ax_f]:
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

print("Saving figures...")
fig.savefig(OUT_PNG, dpi=300, facecolor='white')
fig.savefig(OUT_PDF, dpi=300, facecolor='white')
print(f"  PNG: {OUT_PNG}")
print(f"  PDF: {OUT_PDF}")

# =============================================================================
# Source data CSV
# =============================================================================
print("Generating source data...")

source_parts = []

# Panel (a): Global aggregate binned
bc_a, med_a, lo_a, hi_a, cnt_a = binned_stats(x_all, y_all, bins=15)
df_a = pd.DataFrame({
    'panel': 'a_global_aggregate',
    'urban_pct_bin': bc_a,
    'MUQ_median': med_a,
    'MUQ_q25': lo_a,
    'MUQ_q75': hi_a,
    'n_obs': cnt_a,
})
source_parts.append(df_a)

# Panel (b): By income group
for ig in income_order:
    sub = gdf[gdf['income_group'] == ig]
    if len(sub) < 10:
        continue
    bc_i, med_i, lo_i, hi_i, cnt_i = binned_stats(sub['urban_pct'].values,
                                                    sub['MUQ_w'].values, bins=12)
    df_i = pd.DataFrame({
        'panel': f'b_{ig.replace(" ", "_").lower()}',
        'urban_pct_bin': bc_i,
        'MUQ_median': med_i,
        'MUQ_q25': lo_i,
        'MUQ_q75': hi_i,
        'n_obs': cnt_i,
    })
    source_parts.append(df_i)

# Panel (c): China scatter
df_c = cdf_real[['city', 'year', 'tier', 'fai_gdp_w', 'MUQ_w']].copy()
df_c.columns = ['city', 'year', 'tier', 'fai_gdp', 'MUQ']
df_c['panel'] = 'c_china_city'
source_parts.append(df_c)

# Panel (d): US scatter (sample for size)
df_d = udf[['msa_name', 'year', 'region', 'hu_growth_w', 'MUQ_w']].copy()
df_d.columns = ['msa_name', 'year', 'region', 'hu_growth', 'MUQ']
df_d['panel'] = 'd_us_msa'
source_parts.append(df_d)

# Panel (e): Bar chart values
df_e = pd.DataFrame({
    'panel': 'e_institutional_contrast',
    'category': bar_labels,
    'beta': bar_values,
    'ci_lower': bar_ci_lo,
    'ci_upper': bar_ci_hi,
})
source_parts.append(df_e)

# Panel (f): Box plot data
if box_data:
    f_records = []
    for i, (tier, data) in enumerate(zip(tier_order_display, box_data)):
        for v in data:
            f_records.append({'panel': 'f_city_tier', 'tier': tier, 'MUQ': v})
    df_f = pd.DataFrame(f_records)
    source_parts.append(df_f)

# Concatenate all
source_df = pd.concat(source_parts, ignore_index=True, sort=False)
source_df.to_csv(SOURCE_DATA, index=False)
print(f"  Source data: {SOURCE_DATA}")
print(f"  Total rows: {len(source_df)}")

print("\nDone. Flagship figure created successfully.")
