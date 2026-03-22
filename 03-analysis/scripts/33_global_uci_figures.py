#!/usr/bin/env python3
"""
Figure 5: 全球 UCI 诊断分析图 (Global UCI Diagnostic Analysis)
Urban Q Phase Transition Project

4-panel Nature-style figure:
  a) Top/Bottom 15 国家 UCI_norm 水平条形图
  b) Urban Q vs OCR_norm 散点图（气泡 = GDP, 颜色 = 收入组）
  c) 6 个代表国家 UCI_norm 时间演化
  d) 收入组 UCI 箱线图

输出:
  - fig15_global_uci_diagnosis.png (300 DPI)
  - fig15_global_uci_diagnosis.pdf (矢量)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ── 路径设置 ──────────────────────────────────────────────────────
BASE = Path("/Users/andy/Desktop/Claude/urban-q-phase-transition")
PANEL_CSV = BASE / "02-data/processed/global_ocr_uci_normalized.csv"
SUMMARY_CSV = BASE / "02-data/processed/global_urban_q_summary.csv"
OUT_DIR = BASE / "04-figures/drafts"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── 全局样式（Nature 风格）──────────────────────────────────────
plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 8,
    'axes.titlesize': 9,
    'axes.labelsize': 8,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'legend.fontsize': 7,
    'axes.linewidth': 0.6,
    'xtick.major.width': 0.5,
    'ytick.major.width': 0.5,
    'xtick.major.size': 3,
    'ytick.major.size': 3,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
})

# ── 色盲友好配色 ────────────────────────────────────────────────
# 收入组配色（ColorBrewer Set2 变体）
INCOME_COLORS = {
    'High':         '#4477AA',  # 蓝
    'Upper-middle': '#66CCEE',  # 青
    'Lower-middle': '#CCBB44',  # 黄
    'Low':          '#EE6677',  # 红
}

# UCI 四色分级
UCI_COLORS = {
    'coordinated':      '#228B22',  # 绿 >0.8 (用相对阈值)
    'mild':             '#DAA520',  # 黄 0.6-0.8
    'significant':      '#E07020',  # 橙 0.4-0.6
    'severe':           '#CC3333',  # 红 <0.4
}

def uci_color(val):
    """根据 UCI_norm 值返回颜色（相对于中位数的比例）"""
    # 使用论文中的标准：UCI_norm 基于高收入国家中位数标准化
    # >2: 高效, 1-2: 协调, 0.5-1: 轻度失调, <0.5: 严重失调
    if val >= 2.0:
        return '#228B22'
    elif val >= 1.0:
        return '#66AA55'
    elif val >= 0.5:
        return '#DAA520'
    else:
        return '#CC3333'


# ── 数据加载 ────────────────────────────────────────────────────
print("加载数据...")
panel = pd.read_csv(PANEL_CSV)
summary = pd.read_csv(SUMMARY_CSV)

# 统一收入组标签（summary 用全称，panel 用缩写）
income_map_summary = {
    'High income': 'High',
    'Upper middle income': 'Upper-middle',
    'Lower middle income': 'Lower-middle',
    'Low income': 'Low',
    'Unknown': 'Unknown'
}
summary['income_short'] = summary['income_group'].map(income_map_summary)

# 合并 GDP 数据到 panel 的最新年份
gdp_lookup = summary.set_index('country_code')['gdp_per_capita'].to_dict()

# 获取每国最新 UCI_norm 数据
latest = (panel.dropna(subset=['UCI_norm'])
          .sort_values('year')
          .groupby('country_code')
          .last()
          .reset_index())
latest['gdp_per_capita'] = latest['country_code'].map(gdp_lookup)

print(f"  面板数据: {len(panel)} 行, {panel['country_code'].nunique()} 国")
print(f"  有 UCI_norm 的最新截面: {len(latest)} 国")


# ── 创建图表 ────────────────────────────────────────────────────
fig = plt.figure(figsize=(180/25.4, 240/25.4))  # 180mm x 240mm

# 自定义 GridSpec: 上半 a+b, 下半 c+d
gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.35,
                      left=0.10, right=0.96, top=0.96, bottom=0.05)

ax_a = fig.add_subplot(gs[0, 0])
ax_b = fig.add_subplot(gs[0, 1])
ax_c = fig.add_subplot(gs[1, 0])
ax_d = fig.add_subplot(gs[1, 1])


# ═══════════════════════════════════════════════════════════════════
# Panel a: Top 15 & Bottom 15 UCI_norm 水平条形图
# ═══════════════════════════════════════════════════════════════════
print("绘制 Panel a: UCI_norm 排名条形图...")

top15 = latest.nlargest(15, 'UCI_norm')[['country_name', 'country_code', 'UCI_norm', 'income_group', 'region']].copy()
bot15 = latest.nsmallest(15, 'UCI_norm')[['country_name', 'country_code', 'UCI_norm', 'income_group', 'region']].copy()

# 合并：底部15在上，顶部15在下（翻转后底部在下方）
combined = pd.concat([bot15.sort_values('UCI_norm', ascending=False),
                      top15.sort_values('UCI_norm', ascending=False)], ignore_index=True)

# 简化国名
name_short = {
    'Syrian Arab Republic': 'Syria',
    'Egypt, Arab Rep.': 'Egypt',
    'Yemen, Rep.': 'Yemen',
    'Iran, Islamic Rep.': 'Iran',
    'Kyrgyz Republic': 'Kyrgyzstan',
    'Burkina Faso': 'Burkina Faso',
    'Sierra Leone': 'Sierra Leone',
    'Venezuela, RB': 'Venezuela',
    'Congo, Rep.': 'Congo Rep.',
}
combined['short_name'] = combined['country_name'].map(
    lambda x: name_short.get(x, x))

# 颜色
bar_colors = [uci_color(v) for v in combined['UCI_norm']]

y_pos = np.arange(len(combined))
bars = ax_a.barh(y_pos, combined['UCI_norm'], height=0.7, color=bar_colors,
                 edgecolor='white', linewidth=0.3)

ax_a.set_yticks(y_pos)
ax_a.set_yticklabels(combined['short_name'], fontsize=5.5)
ax_a.set_xlabel('UCI$_{norm}$')
ax_a.set_title('Global UCI ranking', fontsize=9, fontweight='bold', loc='left')

# 参考线 UCI_norm = 1
ax_a.axvline(x=1.0, color='#333333', linestyle='--', linewidth=0.7, alpha=0.7)
ax_a.text(1.05, len(combined)-0.5, 'UCI$_{norm}$=1', fontsize=5.5,
          color='#333333', va='top')

# 分隔线区分 top/bottom
ax_a.axhline(y=14.5, color='grey', linestyle='-', linewidth=0.4, alpha=0.5)
ax_a.text(max(combined['UCI_norm'])*0.65, 22, 'Top 15', fontsize=6,
          color='#228B22', fontstyle='italic', ha='center')
ax_a.text(max(combined['UCI_norm'])*0.65, 7, 'Bottom 15', fontsize=6,
          color='#CC3333', fontstyle='italic', ha='center')

# X 轴上限 — 截断极端值以提高可读性
x_cap = 18
for i, (val, bar) in enumerate(zip(combined['UCI_norm'], bars)):
    if val > x_cap:
        bar.set_width(x_cap)
        ax_a.text(x_cap + 0.2, i, f'{val:.1f}', fontsize=5, va='center', color='#555555')
ax_a.set_xlim(0, x_cap + 3)
ax_a.invert_yaxis()


# ═══════════════════════════════════════════════════════════════════
# Panel b: Urban Q vs OCR_norm 散点图
# ═══════════════════════════════════════════════════════════════════
print("绘制 Panel b: Q vs OCR_norm 散点图...")

scatter_data = latest.dropna(subset=['Q', 'OCR_norm', 'gdp_per_capita']).copy()

# 气泡大小 = GDP per capita（对数缩放）
gdp_log = np.log10(scatter_data['gdp_per_capita'].clip(lower=100))
size_min, size_max = 15, 120
gdp_norm = (gdp_log - gdp_log.min()) / (gdp_log.max() - gdp_log.min())
scatter_data['bubble_size'] = size_min + gdp_norm * (size_max - size_min)

# 按收入组绘制
for ig, color in INCOME_COLORS.items():
    mask = scatter_data['income_group'] == ig
    sub = scatter_data[mask]
    if len(sub) == 0:
        continue
    ax_b.scatter(sub['OCR_norm'], sub['Q'],
                 s=sub['bubble_size'], c=color, alpha=0.65,
                 edgecolors='white', linewidth=0.3,
                 label=ig, zorder=3)

# UCI_norm = 1 的等值线: Q = OCR_norm (因为 UCI_norm = Q / OCR_norm)
x_line = np.linspace(0, 25, 100)
ax_b.plot(x_line, x_line, color='#333333', linestyle='--', linewidth=0.7,
          alpha=0.6, zorder=2)
# 标注区域
ax_b.text(0.8, 6.5, 'UCI$_{norm}$ > 1\n(efficient)', fontsize=5.5,
          color='#228B22', alpha=0.8, fontstyle='italic', ha='center')
ax_b.text(4.5, 0.6, 'UCI$_{norm}$ < 1\n(over-built)', fontsize=5.5,
          color='#CC3333', alpha=0.8, fontstyle='italic', ha='center')

# 标注关键国家
label_countries = ['CHN', 'JPN', 'USA', 'IND', 'BRA', 'KOR', 'GBR', 'DEU', 'TZA', 'NGA']
# 标注偏移量（手动微调）
offsets = {
    'CHN': (0.3, -0.5), 'JPN': (0.3, 0.3), 'USA': (0.3, -0.3),
    'IND': (-0.6, 0.4), 'BRA': (-0.7, 0.3), 'KOR': (0.3, 0.3),
    'GBR': (0.3, -0.3), 'DEU': (0.3, -0.4), 'TZA': (-0.5, -0.3),
}
for _, row in scatter_data.iterrows():
    if row['country_code'] in label_countries:
        cc = row['country_code']
        dx, dy = offsets.get(cc, (0.3, 0.2))
        ax_b.annotate(cc, (row['OCR_norm'], row['Q']),
                      xytext=(row['OCR_norm']+dx, row['Q']+dy),
                      fontsize=5, fontweight='bold',
                      arrowprops=dict(arrowstyle='-', color='grey',
                                     lw=0.4),
                      zorder=5)

ax_b.set_xlabel('OCR$_{norm}$')
ax_b.set_ylabel('Urban Q')
ax_b.set_title('Urban Q vs overcapacity', fontsize=9, fontweight='bold', loc='left')

# 限制轴范围（排除极端值以聚焦主体分布）
q95 = scatter_data['Q'].quantile(0.92)
ocr95 = scatter_data['OCR_norm'].quantile(0.92)
ax_b.set_xlim(-0.2, min(ocr95 * 1.3, 8))
ax_b.set_ylim(-0.2, min(q95 * 1.3, 8))

# 图例
leg_b = ax_b.legend(loc='upper right', frameon=True, framealpha=0.9,
                    edgecolor='grey', markerscale=0.8, handletextpad=0.3,
                    borderpad=0.3)
leg_b.get_frame().set_linewidth(0.4)


# ═══════════════════════════════════════════════════════════════════
# Panel c: 6 国 UCI_norm 时间演化
# ═══════════════════════════════════════════════════════════════════
print("绘制 Panel c: 代表国家 UCI_norm 轨迹...")

# 代表国家（覆盖不同发展阶段）
rep_countries = {
    'CHN': {'name': 'China',   'color': '#E41A1C', 'ls': '-'},
    'JPN': {'name': 'Japan',   'color': '#377EB8', 'ls': '-'},
    'USA': {'name': 'USA',     'color': '#4DAF4A', 'ls': '-'},
    'IND': {'name': 'India',   'color': '#FF7F00', 'ls': '-'},
    'BRA': {'name': 'Brazil',  'color': '#984EA3', 'ls': '-'},
    'TZA': {'name': 'Tanzania','color': '#A65628', 'ls': '--'},
}

# 末端标注偏移（避免重叠）
end_label_offsets = {
    'CHN': 1.15,   # 略上移
    'JPN': 0.85,   # 略下移
    'USA': 1.0,
    'IND': 1.25,
    'BRA': 0.80,
    'TZA': 1.0,
}

for cc, meta in rep_countries.items():
    sub = panel[(panel['country_code'] == cc) & panel['UCI_norm'].notna()].sort_values('year')
    if len(sub) == 0:
        continue
    ax_c.plot(sub['year'], sub['UCI_norm'], color=meta['color'],
              linestyle=meta['ls'], linewidth=1.2, label=meta['name'],
              zorder=3)
    # 末端标注国名（带偏移避免重叠）
    last = sub.iloc[-1]
    y_offset = end_label_offsets.get(cc, 1.0)
    ax_c.text(last['year'] + 0.8, last['UCI_norm'] * y_offset, meta['name'],
              fontsize=5.5, color=meta['color'], va='center',
              fontweight='bold',
              path_effects=[pe.withStroke(linewidth=2.5, foreground='white')])

# UCI_norm = 1 参考线
ax_c.axhline(y=1.0, color='#333333', linestyle='--', linewidth=0.7, alpha=0.6)
ax_c.text(1962, 1.05, 'UCI$_{norm}$=1', fontsize=5.5, color='#555555')

ax_c.set_xlabel('Year')
ax_c.set_ylabel('UCI$_{norm}$')
ax_c.set_title('UCI trajectories by country', fontsize=9, fontweight='bold', loc='left')
ax_c.set_xlim(1960, 2024)

# Y 轴使用对数刻度（因为范围差异大）
ax_c.set_yscale('log')
ax_c.yaxis.set_major_formatter(mticker.ScalarFormatter())
ax_c.yaxis.set_minor_formatter(mticker.NullFormatter())
ax_c.set_yticks([0.1, 0.3, 1, 3, 10, 30])
ax_c.set_yticklabels(['0.1', '0.3', '1', '3', '10', '30'])
ax_c.set_ylim(0.05, 50)

# 填充区域
ax_c.axhspan(0, 1, alpha=0.04, color='#CC3333', zorder=0)
ax_c.axhspan(1, 100, alpha=0.04, color='#228B22', zorder=0)


# ═══════════════════════════════════════════════════════════════════
# Panel d: 收入组 UCI_norm 箱线图
# ═══════════════════════════════════════════════════════════════════
print("绘制 Panel d: 收入组 UCI 箱线图...")

income_order = ['Low', 'Lower-middle', 'Upper-middle', 'High']
income_labels = ['Low\nincome', 'Lower\nmiddle', 'Upper\nmiddle', 'High\nincome']

box_data = []
box_colors = []
for ig in income_order:
    vals = latest[latest['income_group'] == ig]['UCI_norm'].dropna()
    box_data.append(vals.values)
    box_colors.append(INCOME_COLORS[ig])

bp = ax_d.boxplot(box_data, positions=range(len(income_order)),
                  widths=0.55, patch_artist=True,
                  showfliers=True,
                  flierprops=dict(marker='o', markersize=2, alpha=0.4,
                                 markeredgewidth=0.3),
                  medianprops=dict(color='#333333', linewidth=1.2),
                  whiskerprops=dict(linewidth=0.6),
                  capprops=dict(linewidth=0.6),
                  boxprops=dict(linewidth=0.5))

for patch, color in zip(bp['boxes'], box_colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

# 叠加抖动散点
np.random.seed(42)
for i, (ig, vals) in enumerate(zip(income_order, box_data)):
    jitter = np.random.normal(0, 0.08, size=len(vals))
    ax_d.scatter(np.full(len(vals), i) + jitter, vals,
                 s=8, c=INCOME_COLORS[ig], alpha=0.4,
                 edgecolors='white', linewidth=0.2, zorder=3)

# 参考线
ax_d.axhline(y=1.0, color='#333333', linestyle='--', linewidth=0.7, alpha=0.6)
ax_d.text(3.35, 1.05, 'UCI$_{norm}$=1', fontsize=5.5, color='#555555')

ax_d.set_xticks(range(len(income_order)))
ax_d.set_xticklabels(income_labels, fontsize=6.5)
ax_d.set_ylabel('UCI$_{norm}$')
ax_d.set_title('UCI by income group', fontsize=9, fontweight='bold', loc='left')

# Y 轴对数（范围大）
ax_d.set_yscale('log')
ax_d.yaxis.set_major_formatter(mticker.ScalarFormatter())
ax_d.yaxis.set_minor_formatter(mticker.NullFormatter())
ax_d.set_yticks([0.1, 0.3, 1, 3, 10, 30])
ax_d.set_yticklabels(['0.1', '0.3', '1', '3', '10', '30'])

# 添加每组 N 和中位数（放在箱线图上方）
for i, vals in enumerate(box_data):
    n = len(vals)
    med = np.median(vals)
    ax_d.text(i, 35, f'n={n}', ha='center', va='bottom', fontsize=5, color='#555555')


# ── 子图标签 a, b, c, d ─────────────────────────────────────────
for ax, label in zip([ax_a, ax_b, ax_c, ax_d], ['a', 'b', 'c', 'd']):
    ax.text(-0.12, 1.08, label, transform=ax.transAxes,
            fontsize=12, fontweight='bold', va='top', ha='left')


# ── 保存 ────────────────────────────────────────────────────────
out_png = OUT_DIR / "fig15_global_uci_diagnosis.png"
out_pdf = OUT_DIR / "fig15_global_uci_diagnosis.pdf"

fig.savefig(out_png, dpi=300, facecolor='white')
fig.savefig(out_pdf, facecolor='white')
plt.close()

print(f"\n输出完成:")
print(f"  PNG: {out_png}")
print(f"  PDF: {out_pdf}")
print(f"  图幅: 180mm x 240mm, 300 DPI")
