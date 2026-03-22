#!/usr/bin/env python3
"""
97_main_figures_v2.py
Revised main figures for Nature submission — post-reviewer-3 split

Fig 1: Simpson's Paradox (3 panels) — standalone flagship
Fig 2: China city-level evidence (2 panels)
Fig 3: China-US institutional contrast (2 panels, unified DeltaV/GDP metric)

Author: Figure Designer Agent
Date: 2026-03-21
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
from scipy.ndimage import uniform_filter1d
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

# Income group colors (colorblind-safe: warm to cool)
INCOME_COLORS = {
    'Low income':          '#CC3311',
    'Lower middle income': '#EE7733',
    'Upper middle income': '#009988',
    'High income':         '#0077BB',
}
INCOME_SHORT = {
    'Low income': 'LI',
    'Lower middle income': 'LMI',
    'Upper middle income': 'UMI',
    'High income': 'HI',
}

CHINA_COLOR = '#c44e52'
US_COLOR = '#4c72b0'

# City tier colors (viridis-inspired)
import matplotlib.cm as cm
_viridis = cm.get_cmap('viridis', 5)
TIER_COLORS = {
    '一线':   _viridis(0.0),
    '新一线': _viridis(0.25),
    '二线':   _viridis(0.5),
    '三线':   _viridis(0.75),
    '四五线': _viridis(1.0),
}
TIER_LABELS = {
    '一线': 'Tier 1', '新一线': 'New Tier 1', '二线': 'Tier 2',
    '三线': 'Tier 3', '四五线': 'Tier 4-5',
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
GLOBAL_PANEL   = f'{BASE}/02-data/processed/global_q_revised_panel.csv'
CHINA_CITY_275 = f'{BASE}/02-data/processed/china_275_city_panel.csv'
CHINA_REAL_FAI = f'{BASE}/02-data/processed/china_city_real_fai_panel.csv'
US_MSA         = f'{BASE}/02-data/processed/us_msa_muq_panel.csv'

OUT_DIR        = f'{BASE}/04-figures/final'
SRC_DIR        = f'{BASE}/04-figures/source-data'

# =============================================================================
# Helper functions
# =============================================================================
def add_panel_label(ax, label, x=-0.12, y=1.08):
    """Bold lowercase panel label in Nature style."""
    ax.text(x, y, label, transform=ax.transAxes,
            fontsize=10, fontweight='bold', va='top', ha='left')

def remove_top_right(ax):
    """Remove top and right spines."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

def lowess_smooth(x, y, frac=0.3, num_points=200):
    """Simple LOWESS-like smoothing using sorted binning + moving average."""
    order = np.argsort(x)
    xs, ys = x[order], y[order]
    # Bin into num_points bins
    n = len(xs)
    window = max(int(n * frac), 5)
    # Use uniform filter on sorted data
    x_smooth = uniform_filter1d(xs.astype(float), size=window)
    y_smooth = uniform_filter1d(ys.astype(float), size=window)
    # Subsample
    idx = np.linspace(0, n-1, num_points).astype(int)
    return x_smooth[idx], y_smooth[idx]

def binned_stats(x, y, bins=20, percentiles=(25, 75)):
    """Compute binned median and IQR."""
    bin_edges = np.linspace(x.min(), x.max(), bins + 1)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    medians, lowers, uppers, counts = [], [], [], []
    for i in range(bins):
        if i == bins - 1:
            mask = (x >= bin_edges[i]) & (x <= bin_edges[i+1])
        else:
            mask = (x >= bin_edges[i]) & (x < bin_edges[i+1])
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
# Load all data
# =============================================================================
print("Loading data...")

# Global panel
gdf = pd.read_csv(GLOBAL_PANEL)
gdf = gdf.dropna(subset=['MUQ', 'urban_pct'])
lo_g, hi_g = gdf['MUQ'].quantile(0.01), gdf['MUQ'].quantile(0.99)
gdf['MUQ_w'] = gdf['MUQ'].clip(lo_g, hi_g)
print(f"  Global: {len(gdf)} obs, {gdf['country_code'].nunique()} countries")

# China real FAI panel
cdf_real = pd.read_csv(CHINA_REAL_FAI, encoding='utf-8-sig')
cdf_real = cdf_real[(cdf_real['year'] >= 2010) & (cdf_real['year'] <= 2016)].copy()
cdf_real = cdf_real.dropna(subset=['MUQ_real', 'fai_gdp_ratio'])
lo_c, hi_c = cdf_real['MUQ_real'].quantile(0.01), cdf_real['MUQ_real'].quantile(0.99)
cdf_real['MUQ_w'] = cdf_real['MUQ_real'].clip(lo_c, hi_c)
cdf_real['fai_gdp_w'] = cdf_real['fai_gdp_ratio'].clip(
    cdf_real['fai_gdp_ratio'].quantile(0.01), cdf_real['fai_gdp_ratio'].quantile(0.99))

# Compute delta_V / GDP for China (unified metric)
cdf_real_full = pd.read_csv(CHINA_REAL_FAI, encoding='utf-8-sig')
cdf_real_full = cdf_real_full.sort_values(['city', 'year'])
cdf_real_full['V_real_lag'] = cdf_real_full.groupby('city')['V_real'].shift(1)
cdf_real_full['delta_V_real'] = cdf_real_full['V_real'] - cdf_real_full['V_real_lag']
# GDP is in 100m yuan; V_real is likely in 100m yuan too
cdf_real_full['dV_GDP'] = cdf_real_full['delta_V_real'] / cdf_real_full['gdp_100m']
cdf_china_dv = cdf_real_full[(cdf_real_full['year'] >= 2011) & (cdf_real_full['year'] <= 2016)].copy()
cdf_china_dv = cdf_china_dv.dropna(subset=['dV_GDP', 'fai_gdp_ratio'])
# Winsorize
lo_dv, hi_dv = cdf_china_dv['dV_GDP'].quantile(0.01), cdf_china_dv['dV_GDP'].quantile(0.99)
cdf_china_dv['dV_GDP_w'] = cdf_china_dv['dV_GDP'].clip(lo_dv, hi_dv)
cdf_china_dv['fai_gdp_w'] = cdf_china_dv['fai_gdp_ratio'].clip(
    cdf_china_dv['fai_gdp_ratio'].quantile(0.01), cdf_china_dv['fai_gdp_ratio'].quantile(0.99))
print(f"  China dV/GDP: {len(cdf_china_dv)} obs")

# Merge tier info
cdf_275 = pd.read_csv(CHINA_CITY_275)
tier_map = cdf_275[['city', 'tier']].drop_duplicates().set_index('city')['tier'].to_dict()
cdf_real['tier'] = cdf_real['city'].map(tier_map)
cdf_china_dv['tier'] = cdf_china_dv['city'].map(tier_map)

# China 275-city panel (for 2016 cross-section boxplot)
cdf_full = cdf_275.copy()
print(f"  China 275: {len(cdf_full)} obs")

# US MSA panel
udf = pd.read_csv(US_MSA)
udf = udf.dropna(subset=['MUQ_gdp', 'hu_growth'])
lo_u, hi_u = udf['MUQ_gdp'].quantile(0.01), udf['MUQ_gdp'].quantile(0.99)
udf['MUQ_w'] = udf['MUQ_gdp'].clip(lo_u, hi_u)
udf['hu_growth_w'] = udf['hu_growth'].clip(
    udf['hu_growth'].quantile(0.01), udf['hu_growth'].quantile(0.99))
# dV_GDP for US
udf_dv = udf.dropna(subset=['dV_GDP', 'invest_intensity']).copy()
lo_udv, hi_udv = udf_dv['dV_GDP'].quantile(0.01), udf_dv['dV_GDP'].quantile(0.99)
udf_dv['dV_GDP_w'] = udf_dv['dV_GDP'].clip(lo_udv, hi_udv)
udf_dv['invest_w'] = udf_dv['invest_intensity'].clip(
    udf_dv['invest_intensity'].quantile(0.01), udf_dv['invest_intensity'].quantile(0.99))
print(f"  US MSA: {len(udf)} obs, dV/GDP available: {len(udf_dv)}")

# =============================================================================
# Spearman results from robustness report (hard-coded for annotation accuracy)
# =============================================================================
SPEARMAN_GLOBAL = {'rho': 0.038, 'p': 0.030}
SPEARMAN_BY_GROUP = {
    'Low income':          {'rho': -0.150, 'p': 0.002},
    'Lower middle income': {'rho': -0.122, 'p': 0.002},
    'Upper middle income': {'rho': -0.099, 'p': 0.003},
    'High income':         {'rho': -0.013, 'p': 0.633},
}
WITHIN_RHO = -0.076
BETWEEN_COMPONENT = +0.114


# ############################################################################
#                         FIGURE 1: SIMPSON'S PARADOX
# ############################################################################
print("\n=== Creating Fig 1: Simpson's Paradox ===")

fig1_w, fig1_h = 180 / 25.4, 100 / 25.4  # mm to inches
fig1, axes1 = plt.subplots(1, 3, figsize=(fig1_w, fig1_h))
fig1.subplots_adjust(wspace=0.38, left=0.07, right=0.98, top=0.90, bottom=0.15)

# --- Panel (a): Global aggregate scatter + LOESS ---
ax = axes1[0]
add_panel_label(ax, 'a', x=-0.15, y=1.12)

x_all = gdf['urban_pct'].values
y_all = gdf['MUQ_w'].values

# Scatter (light, small)
ax.scatter(x_all, y_all, s=2, alpha=0.08, color=NATURE_COLORS['grey'],
           edgecolors='none', rasterized=True, zorder=2)

# LOESS line (binned median as proxy)
bc, med, lo, hi, cnt = binned_stats(x_all, y_all, bins=20)
valid = ~np.isnan(med)
ax.plot(bc[valid], med[valid], color=NATURE_COLORS['dark'],
        linewidth=1.5, zorder=5, label='LOESS (binned median)')
ax.fill_between(bc[valid], lo[valid], hi[valid],
                color=NATURE_COLORS['grey'], alpha=0.25, linewidth=0)

# Zero line
ax.axhline(y=0, color='black', linewidth=0.3, alpha=0.3)

# Annotation
ax.text(0.97, 0.95,
        f'Global aggregate\n$\\rho$ = +0.04, $p$ = 0.04',
        transform=ax.transAxes, fontsize=6, ha='right', va='top',
        color=NATURE_COLORS['dark'],
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                  edgecolor=NATURE_COLORS['grey'], linewidth=0.5, alpha=0.9))

ax.set_xlabel('Urbanization rate (%)')
ax.set_ylabel('Real MUQ')
ax.set_xlim(5, 100)
ax.set_ylim(-5, 30)
remove_top_right(ax)

# --- Panel (b): By income group, 4 LOESS lines ---
ax = axes1[1]
add_panel_label(ax, 'b', x=-0.15, y=1.12)

income_order = ['Low income', 'Lower middle income', 'Upper middle income', 'High income']
linestyles = {'Low income': '-', 'Lower middle income': '-',
              'Upper middle income': '-', 'High income': '--'}

for ig in income_order:
    sub = gdf[gdf['income_group'] == ig]
    if len(sub) < 10:
        continue
    color = INCOME_COLORS[ig]
    ls = linestyles[ig]

    bc_i, med_i, lo_i, hi_i, _ = binned_stats(
        sub['urban_pct'].values, sub['MUQ_w'].values, bins=12)
    valid_i = ~np.isnan(med_i)
    if valid_i.sum() < 3:
        continue

    res = SPEARMAN_BY_GROUP[ig]
    if res['p'] < 0.01:
        sig = '**'
    elif res['p'] < 0.05:
        sig = '*'
    else:
        sig = 'n.s.'
    lbl = f"{INCOME_SHORT[ig]}: $\\rho$={res['rho']:+.2f}{sig}"

    ax.fill_between(bc_i[valid_i], lo_i[valid_i], hi_i[valid_i],
                    color=color, alpha=0.10, linewidth=0)
    ax.plot(bc_i[valid_i], med_i[valid_i], color=color, linewidth=1.2,
            linestyle=ls, zorder=5, label=lbl)

ax.axhline(y=0, color='black', linewidth=0.3, alpha=0.3)
ax.legend(loc='upper right', fontsize=5.5, handlelength=1.5, labelspacing=0.35)
ax.set_xlabel('Urbanization rate (%)')
ax.set_ylabel('Real MUQ (median)')
ax.set_xlim(5, 100)
ax.set_ylim(-5, 30)
remove_top_right(ax)

# --- Panel (c): Within / Between decomposition bar chart ---
ax = axes1[2]
add_panel_label(ax, 'c', x=-0.15, y=1.12)

bar_labels = ['Within\n(weighted avg)', 'Between\n(composition)']
bar_values = [WITHIN_RHO, BETWEEN_COMPONENT]
bar_colors = [NATURE_COLORS['teal'], NATURE_COLORS['orange']]

bars = ax.bar([0, 1], bar_values, width=0.55, color=bar_colors,
              edgecolor=[c for c in bar_colors], linewidth=0.6, zorder=5)

# Zero line
ax.axhline(y=0, color='black', linewidth=0.6, zorder=4)

# Value labels
for i, (bv, bc_col) in enumerate(zip(bar_values, bar_colors)):
    offset = 0.008 if bv >= 0 else -0.008
    ax.text(i, bv + offset, f'{bv:+.3f}',
            ha='center', va='bottom' if bv >= 0 else 'top',
            fontsize=7, fontweight='bold', color=bc_col)

# Pooled rho annotation
ax.text(0.5, 0.95,
        f'Pooled $\\rho$ = +0.038\n= within + between',
        transform=ax.transAxes, fontsize=6, ha='center', va='top',
        color=NATURE_COLORS['dark'],
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF9E6',
                  edgecolor=NATURE_COLORS['orange'], linewidth=0.5, alpha=0.9))

ax.set_xticks([0, 1])
ax.set_xticklabels(bar_labels, fontsize=6.5)
ax.set_ylabel('$\\rho$ component')
ax.set_ylim(-0.15, 0.18)
remove_top_right(ax)

# Save Fig 1
fig1.savefig(f'{OUT_DIR}/fig01_simpsons_paradox_v2.png', dpi=300, facecolor='white')
fig1.savefig(f'{OUT_DIR}/fig01_simpsons_paradox_v2.pdf', dpi=300, facecolor='white')
print(f"  Saved: fig01_simpsons_paradox_v2.png/pdf")
plt.close(fig1)


# ############################################################################
#                      FIGURE 2: CHINA CITY-LEVEL EVIDENCE
# ############################################################################
print("\n=== Creating Fig 2: China city-level evidence ===")

fig2_w, fig2_h = 180 / 25.4, 80 / 25.4
fig2, axes2 = plt.subplots(1, 2, figsize=(fig2_w, fig2_h))
fig2.subplots_adjust(wspace=0.35, left=0.08, right=0.97, top=0.90, bottom=0.17)

# --- Panel (a): MUQ vs FAI/GDP scatter + OLS + quantile regression ---
ax = axes2[0]
add_panel_label(ax, 'a', x=-0.13, y=1.12)

tier_order = ['一线', '新一线', '二线', '三线', '四五线']
for tier in tier_order:
    sub = cdf_real[cdf_real['tier'] == tier]
    if len(sub) == 0:
        continue
    ax.scatter(sub['fai_gdp_w'], sub['MUQ_w'],
               s=8, alpha=0.55, color=TIER_COLORS.get(tier, '#999'),
               edgecolors='none', label=TIER_LABELS.get(tier, tier),
               zorder=3, rasterized=True)

# OLS fit
x_cn = cdf_real['fai_gdp_w'].values
y_cn = cdf_real['MUQ_w'].values
slope_cn, intercept_cn, r_cn, p_cn, se_cn = stats.linregress(x_cn, y_cn)

x_fit = np.linspace(x_cn.min(), x_cn.max(), 200)
y_fit_ols = slope_cn * x_fit + intercept_cn

# OLS 95% CI
n_cn = len(x_cn)
x_mean = np.mean(x_cn)
ss_x = np.sum((x_cn - x_mean)**2)
y_resid = y_cn - (slope_cn * x_cn + intercept_cn)
mse = np.sum(y_resid**2) / (n_cn - 2)
se_fit = np.sqrt(mse * (1/n_cn + (x_fit - x_mean)**2 / ss_x))
t_crit = stats.t.ppf(0.975, n_cn - 2)

ax.fill_between(x_fit, y_fit_ols - t_crit*se_fit, y_fit_ols + t_crit*se_fit,
                color=CHINA_COLOR, alpha=0.12, linewidth=0)
ax.plot(x_fit, y_fit_ols, color=CHINA_COLOR, linewidth=1.2, zorder=6,
        label=f'OLS ($\\beta$={slope_cn:.2f})')

# Quantile regression lines (approximate via np.percentile in bins)
for qtl, ls, alpha_line in [(0.50, '-', 0.7), (0.90, '--', 0.5)]:
    bin_edges = np.linspace(x_cn.min(), x_cn.max(), 15)
    bin_centers_q = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    q_vals = []
    for j in range(len(bin_edges)-1):
        if j == len(bin_edges)-2:
            mask = (x_cn >= bin_edges[j]) & (x_cn <= bin_edges[j+1])
        else:
            mask = (x_cn >= bin_edges[j]) & (x_cn < bin_edges[j+1])
        vals = y_cn[mask]
        if len(vals) >= 3:
            q_vals.append(np.percentile(vals, qtl*100))
        else:
            q_vals.append(np.nan)
    q_arr = np.array(q_vals)
    valid_q = ~np.isnan(q_arr)
    if valid_q.sum() >= 3:
        ax.plot(bin_centers_q[valid_q], q_arr[valid_q],
                color=CHINA_COLOR, linewidth=0.8, linestyle=ls,
                alpha=alpha_line, zorder=5,
                label=f'Q{int(qtl*100)}')

ax.axhline(y=0, color='black', linewidth=0.3, alpha=0.3)
ax.legend(loc='upper right', fontsize=5, ncol=2, markerscale=1.2,
          handletextpad=0.3, labelspacing=0.3, columnspacing=0.6)
ax.set_xlabel('Investment intensity (FAI / GDP)')
ax.set_ylabel('MUQ')
ax.set_title(f'China ({cdf_real["city"].nunique()} cities, 2010-2016)',
             fontsize=7, fontweight='normal', pad=4)
remove_top_right(ax)

# --- Panel (b): 2016 cross-section box plot by tier ---
ax = axes2[1]
add_panel_label(ax, 'b', x=-0.13, y=1.12)

c2016 = cdf_full[cdf_full['year'] == 2016].copy()
c2016 = c2016.dropna(subset=['MUQ'])
lo_f, hi_f = c2016['MUQ'].quantile(0.01), c2016['MUQ'].quantile(0.99)
c2016['MUQ_w'] = c2016['MUQ'].clip(lo_f, hi_f)

if len(c2016) < 50:
    best_year = cdf_full.groupby('year').size().idxmax()
    c2016 = cdf_full[cdf_full['year'] == best_year].copy()
    c2016 = c2016.dropna(subset=['MUQ'])
    lo_f, hi_f = c2016['MUQ'].quantile(0.01), c2016['MUQ'].quantile(0.99)
    c2016['MUQ_w'] = c2016['MUQ'].clip(lo_f, hi_f)
    panel_year = best_year
else:
    panel_year = 2016

tier_display = ['一线', '新一线', '二线', '三线', '四五线']
tier_short_labels = {
    '一线': 'T1', '新一线': 'NT1', '二线': 'T2',
    '三线': 'T3', '四五线': 'T4-5',
}

box_data, box_labels_list, box_colors_list, box_n = [], [], [], []
for tier in tier_display:
    sub = c2016[c2016['tier'] == tier]
    if len(sub) < 2:
        continue
    box_data.append(sub['MUQ_w'].values)
    box_labels_list.append(tier_short_labels.get(tier, tier))
    box_colors_list.append(TIER_COLORS.get(tier, '#999'))
    box_n.append(len(sub))

if box_data:
    bp = ax.boxplot(box_data, positions=range(len(box_data)),
                    widths=0.5, patch_artist=True, showfliers=False,
                    medianprops=dict(color='black', linewidth=1.0),
                    whiskerprops=dict(linewidth=0.5),
                    capprops=dict(linewidth=0.5),
                    boxprops=dict(linewidth=0.5))
    for patch, color in zip(bp['boxes'], box_colors_list):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    # Jittered points
    rng = np.random.default_rng(42)
    for i, (data, color) in enumerate(zip(box_data, box_colors_list)):
        jitter = rng.uniform(-0.15, 0.15, len(data))
        ax.scatter(np.full(len(data), i) + jitter, data,
                   s=4, alpha=0.35, color=color, edgecolors='none',
                   zorder=3, rasterized=True)

    # N annotations
    for i, n in enumerate(box_n):
        whisker_top = np.percentile(box_data[i], 95)
        ax.text(i, whisker_top + 0.08, f'N={n}',
                ha='center', va='bottom', fontsize=5, color='#555')

    ax.set_xticks(range(len(box_labels_list)))
    ax.set_xticklabels(box_labels_list, fontsize=6)

# Reference lines
ax.axhline(y=0, color='black', linewidth=0.6, linestyle='--', alpha=0.5,
           label='MUQ = 0')
ax.axhline(y=1, color=NATURE_COLORS['grey'], linewidth=0.4, linestyle=':',
           alpha=0.5, label='MUQ = 1')
ax.legend(loc='upper right', fontsize=5)
ax.set_ylabel('MUQ')
ax.set_title(f'City-tier gradient ({panel_year})', fontsize=7, fontweight='normal', pad=4)
remove_top_right(ax)

# Save Fig 2
fig2.savefig(f'{OUT_DIR}/fig02_china_cities_v2.png', dpi=300, facecolor='white')
fig2.savefig(f'{OUT_DIR}/fig02_china_cities_v2.pdf', dpi=300, facecolor='white')
print(f"  Saved: fig02_china_cities_v2.png/pdf")
plt.close(fig2)


# ############################################################################
#                   FIGURE 3: CHINA-US INSTITUTIONAL CONTRAST
# ############################################################################
print("\n=== Creating Fig 3: China-US contrast (unified DeltaV/GDP) ===")

fig3_w, fig3_h = 180 / 25.4, 80 / 25.4
fig3, axes3 = plt.subplots(1, 2, figsize=(fig3_w, fig3_h))
fig3.subplots_adjust(wspace=0.35, left=0.08, right=0.97, top=0.90, bottom=0.17)

# --- Panel (a): US MSA scatter (DeltaV/GDP vs invest_intensity) ---
ax = axes3[0]
add_panel_label(ax, 'a', x=-0.13, y=1.12)

# US regions
REGION_COLORS = {
    'Northeast': '#0077BB',
    'Midwest':   '#33BBEE',
    'South':     '#EE7733',
    'West':      '#CC3311',
}

for region in ['Northeast', 'Midwest', 'South', 'West']:
    sub = udf_dv[udf_dv['region'] == region]
    if len(sub) == 0:
        continue
    ax.scatter(sub['invest_w'], sub['dV_GDP_w'],
               s=3, alpha=0.2, color=REGION_COLORS.get(region, '#999'),
               edgecolors='none', label=region, zorder=3, rasterized=True)

# OLS fit for US: dV_GDP ~ invest_intensity
x_us = udf_dv['invest_w'].values
y_us = udf_dv['dV_GDP_w'].values
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

ax.fill_between(x_fit_us, y_fit_us - t_crit_us*se_fit_us,
                y_fit_us + t_crit_us*se_fit_us,
                color=US_COLOR, alpha=0.12, linewidth=0)
ax.plot(x_fit_us, y_fit_us, color=US_COLOR, linewidth=1.2, zorder=6)

ax.axhline(y=0, color='black', linewidth=0.3, alpha=0.3)

# Stats
ax.text(0.03, 0.97,
        f'$\\beta$ = +{slope_us:.2f}\n$p$ < 10$^{{-6}}$\n$N$ = {n_us:,}',
        transform=ax.transAxes, fontsize=6, ha='left', va='top',
        color=US_COLOR,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                  edgecolor=US_COLOR, linewidth=0.5, alpha=0.9))

ax.legend(loc='upper right', fontsize=5, ncol=2, markerscale=2,
          handletextpad=0.3, columnspacing=0.6)
ax.set_xlabel('Investment intensity')
ax.set_ylabel('$\\Delta$V / GDP')
ax.set_title(f'United States ({udf_dv["cbsa_code"].nunique()} MSAs)', fontsize=7,
             fontweight='normal', pad=4)
remove_top_right(ax)

# --- Panel (b): Coefficient comparison bar chart (unified DeltaV/GDP) ---
ax = axes3[1]
add_panel_label(ax, 'b', x=-0.13, y=1.12)

# From mechanical_correlation_report.txt:
# China: DeltaV/GDP ~ FAI/GDP => beta = -0.3669, 95% CI [-0.6744, -0.0594]
# US: DeltaV/GDP ~ invest_intensity => beta = +1.7845, 95% CI [1.6592, 1.9097]
china_beta = -0.37
china_ci = [-0.67, -0.06]
us_beta = +1.78
us_ci = [1.66, 1.91]

bar_x = [0, 1]
bar_vals = [china_beta, us_beta]
bar_cols = [CHINA_COLOR, US_COLOR]
bar_ci_lo = [china_beta - china_ci[0], us_beta - us_ci[0]]  # error bar lower
bar_ci_hi = [china_ci[1] - china_beta, us_ci[1] - us_beta]  # error bar upper

bars = ax.bar(bar_x, bar_vals, width=0.5, color=bar_cols,
              edgecolor=bar_cols, linewidth=0.6, zorder=5, alpha=0.8)

# Error bars
ax.errorbar(bar_x, bar_vals, yerr=[
    [abs(china_beta - china_ci[0]), abs(us_beta - us_ci[0])],
    [abs(china_ci[1] - china_beta), abs(us_ci[1] - us_beta)]
], fmt='none', ecolor='black', elinewidth=0.6, capsize=4, capthick=0.6, zorder=6)

# Value labels
for i, (bv, col) in enumerate(zip(bar_vals, bar_cols)):
    offset = 0.08 if bv >= 0 else -0.08
    ax.text(i, bv + offset, f'{bv:+.2f}',
            ha='center', va='bottom' if bv >= 0 else 'top',
            fontsize=8, fontweight='bold', color=col)

# CI text
ax.text(0, china_ci[0] - 0.10, f'95% CI\n[{china_ci[0]:.2f}, {china_ci[1]:.2f}]',
        ha='center', va='top', fontsize=5, color=CHINA_COLOR)
ax.text(1, us_ci[1] + 0.10, f'95% CI\n[{us_ci[0]:.2f}, {us_ci[1]:.2f}]',
        ha='center', va='bottom', fontsize=5, color=US_COLOR)

# Zero line
ax.axhline(y=0, color='black', linewidth=0.6, zorder=4)

# Labels
ax.set_xticks([0, 1])
ax.set_xticklabels(['China\n(Supply-driven)', 'United States\n(Demand-driven)'],
                    fontsize=7)
ax.set_ylabel('$\\beta$ ($\\Delta$V/GDP ~ Investment intensity)')
ax.set_title('Institutional contrast (unified metric)', fontsize=7,
             fontweight='normal', pad=4)
ax.set_ylim(-1.2, 2.5)
remove_top_right(ax)

# Save Fig 3
fig3.savefig(f'{OUT_DIR}/fig03_china_us_contrast_v2.png', dpi=300, facecolor='white')
fig3.savefig(f'{OUT_DIR}/fig03_china_us_contrast_v2.pdf', dpi=300, facecolor='white')
print(f"  Saved: fig03_china_us_contrast_v2.png/pdf")
plt.close(fig3)


# ############################################################################
#                            SOURCE DATA
# ############################################################################
print("\n=== Generating Source Data ===")

source_parts = []

# Fig 1a: Global scatter (binned)
bc_1a, med_1a, lo_1a, hi_1a, cnt_1a = binned_stats(x_all, y_all, bins=20)
source_parts.append(pd.DataFrame({
    'figure': 'fig1', 'panel': 'a_global',
    'urban_pct_bin': bc_1a, 'MUQ_median': med_1a,
    'MUQ_q25': lo_1a, 'MUQ_q75': hi_1a, 'n_obs': cnt_1a,
}))

# Fig 1b: By income group
for ig in income_order:
    sub = gdf[gdf['income_group'] == ig]
    if len(sub) < 10:
        continue
    bc_i, med_i, lo_i, hi_i, cnt_i = binned_stats(
        sub['urban_pct'].values, sub['MUQ_w'].values, bins=12)
    source_parts.append(pd.DataFrame({
        'figure': 'fig1', 'panel': f'b_{ig.replace(" ","_").lower()}',
        'urban_pct_bin': bc_i, 'MUQ_median': med_i,
        'MUQ_q25': lo_i, 'MUQ_q75': hi_i, 'n_obs': cnt_i,
    }))

# Fig 1c: Decomposition
source_parts.append(pd.DataFrame({
    'figure': 'fig1', 'panel': 'c_decomposition',
    'component': ['within', 'between', 'pooled'],
    'rho': [WITHIN_RHO, BETWEEN_COMPONENT, 0.038],
}))

# Fig 2a: China scatter
df_2a = cdf_real[['city', 'year', 'tier', 'fai_gdp_w', 'MUQ_w']].copy()
df_2a.columns = ['city', 'year', 'tier', 'fai_gdp', 'MUQ']
df_2a['figure'] = 'fig2'
df_2a['panel'] = 'a_china_scatter'
source_parts.append(df_2a)

# Fig 2b: Box plot
if box_data:
    records = []
    for tier, data in zip(tier_display, box_data):
        for v in data:
            records.append({'figure': 'fig2', 'panel': 'b_boxplot',
                           'tier': tier, 'MUQ': v, 'year': panel_year})
    source_parts.append(pd.DataFrame(records))

# Fig 3a: US scatter
df_3a = udf_dv[['msa_name', 'year', 'region', 'invest_w', 'dV_GDP_w']].copy()
df_3a.columns = ['msa_name', 'year', 'region', 'invest_intensity', 'dV_GDP']
df_3a['figure'] = 'fig3'
df_3a['panel'] = 'a_us_scatter'
source_parts.append(df_3a)

# Fig 3b: Bar chart
source_parts.append(pd.DataFrame({
    'figure': 'fig3', 'panel': 'b_contrast_bar',
    'country': ['China', 'United States'],
    'beta': [china_beta, us_beta],
    'ci_lower': [china_ci[0], us_ci[0]],
    'ci_upper': [china_ci[1], us_ci[1]],
    'metric': ['DeltaV/GDP ~ FAI/GDP', 'DeltaV/GDP ~ invest_intensity'],
}))

source_df = pd.concat(source_parts, ignore_index=True, sort=False)
source_path = f'{SRC_DIR}/fig01-03_v2_source_data.csv'
source_df.to_csv(source_path, index=False)
print(f"  Source data: {source_path} ({len(source_df)} rows)")

print("\nAll figures created successfully.")
