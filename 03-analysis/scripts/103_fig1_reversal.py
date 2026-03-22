#!/usr/bin/env python3
"""
103_fig1_reversal.py
====================
Fig 1 "The Reversal" -- flagship figure for Nature submission.

Design rationale (Expert 4 "3-second rule"):
  Second 1: Green panel -- pooled data looks stable
  Second 2: Red panels -- every income group actually declines
  Second 3: Cognitive dissonance resolved -- Simpson's Paradox

Layout:
  Row 1 (a):  Full-width panel, mint-green background
              All 158 countries pooled, MUQ_real vs urbanization
              LOESS smooth + 95% CI -- visually FLAT
  Row 2 (b-e): Four equal panels (LI | LMI | UMI | HI)
              b-d: pink/red background, downward LOESS
              e: grey background, flat LOESS (n.s.)

Output:
  04-figures/final/fig01_reversal_v4.png  (300 dpi)
  04-figures/final/fig01_reversal_v4.pdf  (vector)
  04-figures/source-data/fig01_reversal_source.csv

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
# Paths
# =============================================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
PANEL_PATH = f'{BASE}/02-data/processed/global_q_revised_panel.csv'
OUT_PNG = f'{BASE}/04-figures/final/fig01_reversal_v4.png'
OUT_PDF = f'{BASE}/04-figures/final/fig01_reversal_v4.pdf'
OUT_SOURCE = f'{BASE}/04-figures/source-data/fig01_reversal_source.csv'

# =============================================================================
# Nature style
# =============================================================================
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica'],
    'font.size': 7,
    'axes.linewidth': 0.5,
    'axes.labelsize': 8,
    'xtick.labelsize': 6,
    'ytick.labelsize': 6,
    'legend.fontsize': 6,
    'lines.linewidth': 0.75,
    'patch.linewidth': 0.5,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
    'mathtext.default': 'regular',
})

# =============================================================================
# Color scheme -- green (stable) vs red (decline)
# =============================================================================
GREEN_BG = '#E8F5E9'       # Mint green background (row 1)
GREEN_ACCENT = '#2E7D32'   # Dark green for text annotations
RED_BG = '#FFEBEE'         # Pink background (row 2, b-d)
RED_LINE = '#C62828'        # Deep red for LOESS lines
RED_ACCENT = '#B71C1C'     # Dark red for annotations
GREY_BG = '#F5F5F5'        # Grey background (row 2, e)
GREY_LINE = '#757575'      # Grey for HI LOESS line
SCATTER_ALPHA = 0.25        # Scatter dot transparency
SCATTER_GREEN = '#66BB6A'  # Green scatter dots (row 1)
SCATTER_RED = '#EF9A9A'    # Pink scatter dots (row 2, b-d)
SCATTER_GREY = '#BDBDBD'   # Grey scatter dots (row 2, e)
CI_ALPHA = 0.20             # Confidence interval band alpha

# =============================================================================
# Data preparation
# =============================================================================
print("[1/5] Loading data...")
panel = pd.read_csv(PANEL_PATH)

# Compute real MUQ (same method as script 36)
panel['deflator'] = panel['gdp_current_usd'] / panel['gdp_constant_2015']
panel['V2_real'] = panel['rnna'] * 1e6  # constant 2015 prices
panel['gfcf_real'] = panel['gfcf_current_usd'] / panel['deflator']
panel['delta_V2_real'] = panel.groupby('country_code')['V2_real'].diff()
panel['delta_I_real'] = panel.groupby('country_code')['gfcf_real'].diff()
panel['MUQ_real'] = panel['delta_V2_real'] / panel['delta_I_real']

# Extreme value trimming (same as script 36)
extreme = (panel['MUQ_real'].abs() > 20) | (panel['MUQ_real'] < -5)
panel.loc[extreme, 'MUQ_real'] = np.nan

# Working subset
df = panel.dropna(subset=['MUQ_real', 'urban_pct', 'income_group']).copy()
df = df[df['income_group'] != 'Unknown'].copy()

print(f"  Working dataset: {len(df)} obs, {df['country_code'].nunique()} countries")
print(f"  Income groups: {df['income_group'].value_counts().to_dict()}")

# Income group order and labels
INCOME_ORDER = ['Low income', 'Lower middle income', 'Upper middle income', 'High income']
INCOME_LABELS = ['LI', 'LMI', 'UMI', 'HI']

# =============================================================================
# LOESS smoothing (using statsmodels lowess)
# =============================================================================
from statsmodels.nonparametric.smoothers_lowess import lowess

def loess_with_ci(x, y, frac=0.6, n_grid=200, n_boot=200):
    """Compute LOESS smooth + bootstrap 95% CI."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]

    # Grid for evaluation
    x_grid = np.linspace(np.percentile(x, 2), np.percentile(x, 98), n_grid)

    # Main LOESS
    smooth = lowess(y, x, frac=frac, return_sorted=True)
    y_main = np.interp(x_grid, smooth[:, 0], smooth[:, 1])

    # Bootstrap CI
    rng = np.random.RandomState(42)
    boot_curves = []
    n = len(x)
    for _ in range(n_boot):
        idx = rng.choice(n, size=n, replace=True)
        try:
            s = lowess(y[idx], x[idx], frac=frac, return_sorted=True)
            y_boot = np.interp(x_grid, s[:, 0], s[:, 1])
            boot_curves.append(y_boot)
        except Exception:
            continue

    boot_arr = np.array(boot_curves)
    ci_lo = np.percentile(boot_arr, 2.5, axis=0)
    ci_hi = np.percentile(boot_arr, 97.5, axis=0)

    return x_grid, y_main, ci_lo, ci_hi


def spearman_stats(x, y):
    """Compute Spearman rho and p-value."""
    mask = np.isfinite(x) & np.isfinite(y)
    rho, p = stats.spearmanr(x[mask], y[mask])
    return rho, p, mask.sum()


# =============================================================================
# Compute all statistics
# =============================================================================
print("[2/5] Computing LOESS + statistics...")

# Panel (a): All countries pooled
x_all = df['urban_pct'].values
y_all = df['MUQ_real'].values
xg_a, ym_a, ci_lo_a, ci_hi_a = loess_with_ci(x_all, y_all, frac=0.6)
rho_a, p_a, n_a = spearman_stats(x_all, y_all)
print(f"  Pooled: rho={rho_a:.4f}, p={p_a:.6f}, n={n_a}")

# Panels (b-e): By income group
loess_results = {}
stat_results = {}
for ig in INCOME_ORDER:
    sub = df[df['income_group'] == ig]
    x_sub = sub['urban_pct'].values
    y_sub = sub['MUQ_real'].values
    xg, ym, cl, ch = loess_with_ci(x_sub, y_sub, frac=0.6)
    loess_results[ig] = (xg, ym, cl, ch)
    rho, p, n = spearman_stats(x_sub, y_sub)
    stat_results[ig] = (rho, p, n)
    print(f"  {ig}: rho={rho:.4f}, p={p:.6f}, n={n}")

# =============================================================================
# Figure construction
# =============================================================================
print("[3/5] Building figure...")

# Nature double-column: 183mm wide, target ~140mm tall
fig_w_mm, fig_h_mm = 180, 140
fig_w_in = fig_w_mm / 25.4
fig_h_in = fig_h_mm / 25.4

fig = plt.figure(figsize=(fig_w_in, fig_h_in))

# GridSpec: 2 rows (40:60), bottom row has 4 columns
gs = gridspec.GridSpec(
    2, 4,
    height_ratios=[0.40, 0.60],
    hspace=0.42,
    wspace=0.30,
    left=0.07, right=0.97,
    top=0.96, bottom=0.08,
)

# --- Panel (a): Full-width top ---
ax_a = fig.add_subplot(gs[0, :])

# Green background
ax_a.set_facecolor(GREEN_BG)

# Scatter
ax_a.scatter(x_all, y_all, s=4, alpha=SCATTER_ALPHA, color=SCATTER_GREEN,
             edgecolors='none', rasterized=True, zorder=2)

# LOESS line + CI
ax_a.fill_between(xg_a, ci_lo_a, ci_hi_a, alpha=CI_ALPHA, color=GREEN_ACCENT, zorder=3)
ax_a.plot(xg_a, ym_a, color=GREEN_ACCENT, linewidth=2.0, zorder=4)

# Reference line at y=0
ax_a.axhline(0, color='#999999', linewidth=0.4, linestyle='--', zorder=1)

# Annotation: statistic
sig_str = f"$\\rho$ = {rho_a:+.2f}, p = {p_a:.3f}"
ax_a.text(0.98, 0.92, sig_str,
          transform=ax_a.transAxes, fontsize=7, fontweight='normal',
          ha='right', va='top', color=GREEN_ACCENT,
          bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.85, edgecolor='none'))

# Large annotation: "Aggregate: apparently stable"
ax_a.text(0.50, 0.12, 'Aggregate: apparently stable',
          transform=ax_a.transAxes, fontsize=11, fontweight='bold',
          ha='center', va='bottom', color=GREEN_ACCENT, alpha=0.55,
          zorder=5, style='italic')

# Labels
ax_a.set_xlabel('Urbanization rate (%)', fontsize=8)
ax_a.set_ylabel('Real MUQ', fontsize=8)
ax_a.set_xlim(0, 100)
ax_a.set_ylim(-5, 20)

# Panel label
ax_a.text(-0.04, 1.05, 'a', transform=ax_a.transAxes,
          fontsize=10, fontweight='bold', va='top', ha='right')

# Subtitle
ax_a.set_title(f'All {df["country_code"].nunique()} countries pooled (n = {n_a:,})',
               fontsize=7, color='#555555', pad=4)

# Spine styling
for sp in ax_a.spines.values():
    sp.set_linewidth(0.5)

# --- Row 2: Panels (b)-(e) ---
panel_labels = ['b', 'c', 'd', 'e']
bg_colors = [RED_BG, RED_BG, RED_BG, GREY_BG]
line_colors = [RED_LINE, RED_LINE, RED_LINE, GREY_LINE]
scatter_colors = [SCATTER_RED, SCATTER_RED, SCATTER_RED, SCATTER_GREY]
line_styles = ['-', '-', '-', '--']

for i, ig in enumerate(INCOME_ORDER):
    ax = fig.add_subplot(gs[1, i])
    ax.set_facecolor(bg_colors[i])

    sub = df[df['income_group'] == ig]
    x_sub = sub['urban_pct'].values
    y_sub = sub['MUQ_real'].values

    # Scatter
    ax.scatter(x_sub, y_sub, s=3, alpha=SCATTER_ALPHA, color=scatter_colors[i],
               edgecolors='none', rasterized=True, zorder=2)

    # LOESS
    xg, ym, cl, ch = loess_results[ig]
    ax.fill_between(xg, cl, ch, alpha=CI_ALPHA, color=line_colors[i], zorder=3)
    ax.plot(xg, ym, color=line_colors[i], linewidth=1.5, linestyle=line_styles[i], zorder=4)

    # Reference at 0
    ax.axhline(0, color='#999999', linewidth=0.3, linestyle='--', zorder=1)

    # Statistics annotation
    rho, p, n = stat_results[ig]
    if p < 0.001:
        sig_marker = '***'
    elif p < 0.01:
        sig_marker = '**'
    elif p < 0.05:
        sig_marker = '*'
    else:
        sig_marker = ' n.s.'

    rho_str = f"$\\rho$ = {rho:.2f}{sig_marker}"
    anno_color = RED_ACCENT if i < 3 else GREY_LINE
    ax.text(0.95, 0.92, rho_str,
            transform=ax.transAxes, fontsize=6.5, fontweight='bold',
            ha='right', va='top', color=anno_color,
            bbox=dict(boxstyle='round,pad=0.25', facecolor='white', alpha=0.85, edgecolor='none'))

    # n annotation
    ax.text(0.95, 0.78, f'n = {n:,}',
            transform=ax.transAxes, fontsize=5.5, ha='right', va='top',
            color='#777777')

    # Axes
    ax.set_xlim(0, 100)
    ax.set_ylim(-5, 20)
    ax.set_xlabel('Urbanization rate (%)', fontsize=7)
    if i == 0:
        ax.set_ylabel('Real MUQ', fontsize=7)
    else:
        ax.set_ylabel('')

    # Title = income group short name
    title_color = RED_ACCENT if i < 3 else GREY_LINE
    ax.set_title(INCOME_LABELS[i], fontsize=8, fontweight='bold',
                 color=title_color, pad=4)

    # Panel label
    ax.text(-0.08, 1.08, panel_labels[i], transform=ax.transAxes,
            fontsize=10, fontweight='bold', va='top', ha='right')

    # Large label for decline (b-d only)
    if i < 3:
        ax.text(0.50, 0.08, 'Decline',
                transform=ax.transAxes, fontsize=9, fontweight='bold',
                ha='center', va='bottom', color=RED_ACCENT, alpha=0.40,
                style='italic', zorder=5)
    else:
        ax.text(0.50, 0.08, 'No trend',
                transform=ax.transAxes, fontsize=9, fontweight='bold',
                ha='center', va='bottom', color=GREY_LINE, alpha=0.40,
                style='italic', zorder=5)

    # Spines
    for sp in ax.spines.values():
        sp.set_linewidth(0.5)

# Add a bridging annotation between rows
fig.text(0.50, 0.575, 'But disaggregated by income group...',
         fontsize=7.5, ha='center', va='center', color='#555555',
         style='italic', fontweight='normal')

# =============================================================================
# Save
# =============================================================================
print("[4/5] Saving figures...")
fig.savefig(OUT_PNG, dpi=300, facecolor='white')
fig.savefig(OUT_PDF, facecolor='white')
plt.close(fig)
print(f"  -> {OUT_PNG}")
print(f"  -> {OUT_PDF}")

# =============================================================================
# Source data
# =============================================================================
print("[5/5] Exporting source data...")
source = df[['country_code', 'country_name', 'income_group', 'year',
             'urban_pct', 'MUQ_real']].copy()
source.columns = ['country_code', 'country_name', 'income_group', 'year',
                   'urbanization_pct', 'real_MUQ']
source = source.sort_values(['income_group', 'country_code', 'year'])
source.to_csv(OUT_SOURCE, index=False, float_format='%.6f')
print(f"  -> {OUT_SOURCE} ({len(source)} rows)")

print("\nDone. Fig 1 'The Reversal' generated.")
