"""
08_four_country_comparison.py
==============================
目的：生成论文 Figure 1 — 四国 Urban Q 时序对比（投 Nature 主图）

布局：上下两子图，共享 X 轴
  Panel a: 四国 Urban Q 时序 + Q=1 参考线 + 关键事件阴影
  Panel b: 四国建设投资/GDP 比率

输出：
  - fig01_four_country_urban_q.png (300 DPI)
  - fig01_four_country_urban_q.pdf (矢量)

依赖：pandas, numpy, matplotlib
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyArrowPatch
from pathlib import Path

# ============================================================
# 0. 路径设置
# ============================================================

BASE_DIR = Path("/Users/andy/Desktop/Claude/urban-q-phase-transition")
MODEL_DIR = BASE_DIR / "03-analysis/models"
FIG_DIR = BASE_DIR / "04-figures/drafts"

# six-curves 主数据集（取中国 CI/GDP）
SIX_CURVES_MASTER = Path("/Users/andy/Desktop/Claude/six-curves-urban-transition/02-data/processed/six_curves_master_dataset_processed.csv")

# ============================================================
# 1. 读取数据
# ============================================================

china = pd.read_csv(MODEL_DIR / "china_urban_q_timeseries.csv")
japan = pd.read_csv(MODEL_DIR / "japan_urban_q_timeseries.csv")
us = pd.read_csv(MODEL_DIR / "us_urban_q_timeseries.csv")
uk = pd.read_csv(MODEL_DIR / "uk_urban_q_timeseries.csv")

# 中国 CI/GDP 从 six-curves 主数据集补充
china_master = pd.read_csv(SIX_CURVES_MASTER, usecols=['year', 'total_inv_pct_gdp'])
china = china.merge(china_master, on='year', how='left')
# 将百分数转为小数比率（与其他国家一致）
china['ci_gdp_ratio'] = china['total_inv_pct_gdp'] / 100.0

# 选择各国最可比的 Q 口径
# 中国: Q_V1K1 (住宅价值/累计投资 — 最严格口径，最早跌破1)
# 日本/美国/英国: urban_Q (各国脚本中定义的总 Q)
china_q = china[['year', 'Q_V1K1', 'ci_gdp_ratio']].rename(columns={'Q_V1K1': 'urban_Q'})
japan_q = japan[['year', 'urban_Q', 'ci_gdp_ratio']].copy()
us_q = us[['year', 'urban_Q', 'ci_gdp_ratio']].copy()
uk_q = uk[['year', 'urban_Q', 'ci_gdp_ratio']].copy()

# 去除缺失值
china_q = china_q.dropna(subset=['urban_Q'])
japan_q = japan_q.dropna(subset=['urban_Q'])
us_q = us_q.dropna(subset=['urban_Q'])
uk_q = uk_q.dropna(subset=['urban_Q'])

print("=== 数据范围 ===")
print(f"  China: {int(china_q['year'].min())}-{int(china_q['year'].max())} ({len(china_q)} years)")
print(f"  Japan: {int(japan_q['year'].min())}-{int(japan_q['year'].max())} ({len(japan_q)} years)")
print(f"  US:    {int(us_q['year'].min())}-{int(us_q['year'].max())} ({len(us_q)} years)")
print(f"  UK:    {int(uk_q['year'].min())}-{int(uk_q['year'].max())} ({len(uk_q)} years)")

# ============================================================
# 2. 识别 Q=1 交叉点（精确线性插值）
# ============================================================

def find_q1_crossing(years, q_values, direction='down'):
    """找到 Q 从 >1 跌破 1 的精确年份（线性插值）"""
    crossings = []
    for i in range(1, len(years)):
        prev_q, curr_q = q_values.iloc[i-1], q_values.iloc[i]
        if direction == 'down' and prev_q > 1 and curr_q <= 1:
            frac = (1 - prev_q) / (curr_q - prev_q)
            cross_year = years.iloc[i-1] + frac * (years.iloc[i] - years.iloc[i-1])
            crossings.append(cross_year)
        elif direction == 'up' and prev_q < 1 and curr_q >= 1:
            frac = (1 - prev_q) / (curr_q - prev_q)
            cross_year = years.iloc[i-1] + frac * (years.iloc[i] - years.iloc[i-1])
            crossings.append(cross_year)
    return crossings

china_cross = find_q1_crossing(china_q['year'], china_q['urban_Q'], 'down')
japan_cross = find_q1_crossing(japan_q['year'], japan_q['urban_Q'], 'down')

print(f"\n=== Q=1 交叉点 ===")
print(f"  China Q=1: {[f'{y:.1f}' for y in china_cross]}")
print(f"  Japan Q=1: {[f'{y:.1f}' for y in japan_cross]}")
print(f"  US: Q 始终 > 1 (2024: {us_q['urban_Q'].iloc[-1]:.2f})")
print(f"  UK: Q 始终 > 1 (2024: {uk_q['urban_Q'].iloc[-1]:.2f})")

# ============================================================
# 3. 图表设置 — Nature 风格
# ============================================================

# 全局 rcParams
plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 9,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'xtick.labelsize': 8.5,
    'ytick.labelsize': 8.5,
    'legend.fontsize': 8,
    'figure.dpi': 300,
    'axes.linewidth': 0.7,
    'xtick.major.width': 0.5,
    'ytick.major.width': 0.5,
    'xtick.minor.width': 0.3,
    'ytick.minor.width': 0.3,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'xtick.major.size': 3,
    'ytick.major.size': 3,
    'axes.unicode_minus': False,
    'pdf.fonttype': 42,       # TrueType fonts in PDF (Nature requirement)
    'ps.fonttype': 42,
})

# 色盲友好配色方案 (Wong, 2011 - Nature Methods)
COLORS = {
    'china': '#CC3311',    # 红色 — 中国
    'japan': '#0077BB',    # 蓝色 — 日本
    'us':    '#009988',    # 青绿色 — 美国
    'uk':    '#EE7733',    # 橙色 — 英国
    'ref':   '#333333',    # 参考线
    'shade': '#DDDDDD',   # 阴影
}

# 图幅：Nature 双栏 180mm 宽，高度 ~200mm
FIG_WIDTH_MM = 180
FIG_HEIGHT_MM = 200
MM_TO_INCH = 1 / 25.4
fig_w = FIG_WIDTH_MM * MM_TO_INCH
fig_h = FIG_HEIGHT_MM * MM_TO_INCH

# ============================================================
# 4. 绑图
# ============================================================

fig, (ax_a, ax_b) = plt.subplots(
    2, 1,
    figsize=(fig_w, fig_h),
    gridspec_kw={'height_ratios': [2, 1], 'hspace': 0.22},
)

# --- X 轴范围 ---
x_min, x_max = 1958, 2026

# ============================================================
# Panel a: 四国 Urban Q 时序
# ============================================================

# 日本泡沫阴影 (1986-1991)
ax_a.axvspan(1986, 1991, alpha=0.10, color='#0077BB', zorder=0)
ax_a.text(1988.5, 2.55, 'Japan\nbubble', fontsize=6.5, color='#0077BB',
          ha='center', va='bottom', fontstyle='italic', alpha=0.7)

# 美国金融危机阴影 (2007-2009)
ax_a.axvspan(2007, 2009, alpha=0.10, color='#009988', zorder=0)
ax_a.text(2008, 2.55, 'US\nGFC', fontsize=6.5, color='#009988',
          ha='center', va='bottom', fontstyle='italic', alpha=0.7)

# Q = 1 参考线
ax_a.axhline(y=1, color=COLORS['ref'], linestyle='--', linewidth=0.8,
             alpha=0.6, zorder=1)
ax_a.text(x_max - 0.3, 1.04, 'Q = 1 (Phase Transition Threshold)',
          fontsize=7, color=COLORS['ref'], ha='right', va='bottom',
          fontstyle='italic')

# 四国主线
ax_a.plot(china_q['year'], china_q['urban_Q'],
          color=COLORS['china'], linewidth=2.0, linestyle='-',
          label='China', zorder=4)
ax_a.plot(japan_q['year'], japan_q['urban_Q'],
          color=COLORS['japan'], linewidth=1.5, linestyle='-',
          label='Japan', zorder=3)
ax_a.plot(us_q['year'], us_q['urban_Q'],
          color=COLORS['us'], linewidth=1.5, linestyle='--',
          label='United States', zorder=3)
ax_a.plot(uk_q['year'], uk_q['urban_Q'],
          color=COLORS['uk'], linewidth=1.5, linestyle='--',
          label='United Kingdom', zorder=3)

# 标注中国 Q=1 年份
if china_cross:
    cy = china_cross[0]
    ax_a.plot(cy, 1, 'o', color=COLORS['china'], markersize=6,
              markeredgecolor='white', markeredgewidth=1.0, zorder=5)
    ax_a.annotate(f'{cy:.0f}',
                  xy=(cy, 1), xytext=(cy - 3.5, 0.65),
                  fontsize=8, fontweight='bold', color=COLORS['china'],
                  arrowprops=dict(arrowstyle='->', color=COLORS['china'],
                                  lw=0.8, connectionstyle='arc3,rad=0.2'),
                  zorder=5)

# 标注日本 Q=1 年份
if japan_cross:
    jy = japan_cross[0]
    ax_a.plot(jy, 1, 'o', color=COLORS['japan'], markersize=6,
              markeredgecolor='white', markeredgewidth=1.0, zorder=5)
    ax_a.annotate(f'{jy:.0f}',
                  xy=(jy, 1), xytext=(jy + 2, 0.65),
                  fontsize=8, fontweight='bold', color=COLORS['japan'],
                  arrowprops=dict(arrowstyle='->', color=COLORS['japan'],
                                  lw=0.8, connectionstyle='arc3,rad=-0.2'),
                  zorder=5)

# 标注中国2024终值
china_last = china_q.iloc[-1]
ax_a.annotate(f'Q = {china_last["urban_Q"]:.2f}',
              xy=(china_last['year'], china_last['urban_Q']),
              xytext=(china_last['year'] - 6, china_last['urban_Q'] - 0.18),
              fontsize=7, color=COLORS['china'],
              arrowprops=dict(arrowstyle='->', color=COLORS['china'],
                              lw=0.6), zorder=5)

# 标注英国超出范围（Q 远高于其他国家）
# 找到英国曲线进入可见范围的位置，标注其最终值
uk_last = uk_q.iloc[-1]
ax_a.annotate(f'UK (Q = {uk_last["urban_Q"]:.1f})',
              xy=(2000, 2.65),
              fontsize=6.5, color=COLORS['uk'], ha='center', va='top',
              fontstyle='italic')
# 在 y 轴顶部加一个向上箭头表示英国曲线超出
ax_a.annotate('', xy=(1982, 2.68), xytext=(1982, 2.45),
              arrowprops=dict(arrowstyle='->', color=COLORS['uk'],
                              lw=1.2), zorder=5)

# 轴设置
ax_a.set_xlim(x_min, x_max)
ax_a.set_ylim(0.3, 2.7)
ax_a.set_ylabel('Urban Q')
ax_a.yaxis.set_major_locator(mticker.MultipleLocator(0.5))
ax_a.yaxis.set_minor_locator(mticker.MultipleLocator(0.25))
ax_a.xaxis.set_major_locator(mticker.MultipleLocator(10))
ax_a.xaxis.set_minor_locator(mticker.MultipleLocator(5))

# 仅 Y 轴主刻度网格线
ax_a.grid(axis='y', which='major', color='#E0E0E0', linewidth=0.4,
          linestyle='-', zorder=0)
ax_a.set_axisbelow(True)

# 去除上右边框
ax_a.spines['top'].set_visible(False)
ax_a.spines['right'].set_visible(False)

# 图例
ax_a.legend(loc='upper right', frameon=True, framealpha=0.9,
            edgecolor='#CCCCCC', fancybox=False, borderpad=0.6,
            handlelength=2.5)

# 子图标签
ax_a.text(-0.06, 1.02, 'a', transform=ax_a.transAxes,
          fontsize=14, fontweight='bold', va='bottom')

# ============================================================
# Panel b: 四国 CI/GDP 比率
# ============================================================

# 中国 CI/GDP
china_ci = china_q[china_q['ci_gdp_ratio'].notna()]
ax_b.plot(china_ci['year'], china_ci['ci_gdp_ratio'] * 100,
          color=COLORS['china'], linewidth=2.0, linestyle='-',
          label='China', zorder=4)

# 日本 CI/GDP
japan_ci = japan_q[japan_q['ci_gdp_ratio'].notna()]
ax_b.plot(japan_ci['year'], japan_ci['ci_gdp_ratio'] * 100,
          color=COLORS['japan'], linewidth=1.5, linestyle='-',
          label='Japan', zorder=3)

# 美国 CI/GDP
us_ci = us_q[us_q['ci_gdp_ratio'].notna()]
ax_b.plot(us_ci['year'], us_ci['ci_gdp_ratio'] * 100,
          color=COLORS['us'], linewidth=1.5, linestyle='--',
          label='United States', zorder=3)

# 英国 CI/GDP
uk_ci = uk_q[uk_q['ci_gdp_ratio'].notna()]
ax_b.plot(uk_ci['year'], uk_ci['ci_gdp_ratio'] * 100,
          color=COLORS['uk'], linewidth=1.5, linestyle='--',
          label='United Kingdom', zorder=3)

# 阴影区域（与 Panel a 对齐）
ax_b.axvspan(1986, 1991, alpha=0.10, color='#0077BB', zorder=0)
ax_b.axvspan(2007, 2009, alpha=0.10, color='#009988', zorder=0)

# 轴设置
ax_b.set_xlim(x_min, x_max)
ax_b.set_ylim(0, 35)
ax_b.set_xlabel('Year')
ax_b.set_ylabel('Construction Investment / GDP (%)')
ax_b.yaxis.set_major_locator(mticker.MultipleLocator(10))
ax_b.yaxis.set_minor_locator(mticker.MultipleLocator(5))
ax_b.xaxis.set_major_locator(mticker.MultipleLocator(10))
ax_b.xaxis.set_minor_locator(mticker.MultipleLocator(5))

# 仅 Y 轴主刻度网格线
ax_b.grid(axis='y', which='major', color='#E0E0E0', linewidth=0.4,
          linestyle='-', zorder=0)
ax_b.set_axisbelow(True)

# 去除上右边框
ax_b.spines['top'].set_visible(False)
ax_b.spines['right'].set_visible(False)

# 图例
ax_b.legend(loc='upper left', frameon=True, framealpha=0.9,
            edgecolor='#CCCCCC', fancybox=False, borderpad=0.6,
            handlelength=2.5)

# 子图标签
ax_b.text(-0.06, 1.02, 'b', transform=ax_b.transAxes,
          fontsize=14, fontweight='bold', va='bottom')

# ============================================================
# 5. 保存
# ============================================================

# PNG (300 DPI)
png_path = FIG_DIR / "fig01_four_country_urban_q.png"
fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white',
            pad_inches=0.15)
print(f"\nPNG saved: {png_path}")

# PDF (矢量)
pdf_path = FIG_DIR / "fig01_four_country_urban_q.pdf"
fig.savefig(pdf_path, format='pdf', bbox_inches='tight', facecolor='white',
            pad_inches=0.15)
print(f"PDF saved: {pdf_path}")

plt.close()

# ============================================================
# 6. 终端摘要
# ============================================================

print("\n" + "=" * 60)
print("Figure 1 Summary Statistics")
print("=" * 60)

for name, df_q in [('China', china_q), ('Japan', japan_q),
                     ('US', us_q), ('UK', uk_q)]:
    q_min = df_q['urban_Q'].min()
    q_max = df_q['urban_Q'].max()
    q_last = df_q['urban_Q'].iloc[-1]
    yr_min = int(df_q.loc[df_q['urban_Q'].idxmin(), 'year'])
    yr_max = int(df_q.loc[df_q['urban_Q'].idxmax(), 'year'])
    yr_last = int(df_q['year'].iloc[-1])

    ci_max_val = df_q['ci_gdp_ratio'].max() * 100 if df_q['ci_gdp_ratio'].notna().any() else np.nan
    ci_max_yr = int(df_q.loc[df_q['ci_gdp_ratio'].idxmax(), 'year']) if df_q['ci_gdp_ratio'].notna().any() else 'N/A'

    print(f"\n  {name}:")
    print(f"    Q range: {q_min:.3f} ({yr_min}) - {q_max:.3f} ({yr_max})")
    print(f"    Q latest ({yr_last}): {q_last:.3f}")
    print(f"    CI/GDP peak: {ci_max_val:.1f}% ({ci_max_yr})")

print("\nDone.")
