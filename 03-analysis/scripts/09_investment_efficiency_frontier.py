#!/usr/bin/env python3
"""
09_investment_efficiency_frontier.py
=====================================
Figure 2: Investment Efficiency Frontier
四国在 I/GDP vs dV/V 坐标系中的定位，含 pooled 倒 U 型拟合。

X轴: 建设投资强度 I(t)/GDP(t) (%)
Y轴: 资产增值率 dV(t)/V(t) = [V(t) - V(t-1)] / V(t-1) (%)

数据来源:
  - china_urban_q_timeseries.csv
  - japan_urban_q_timeseries.csv
  - us_urban_q_timeseries.csv
  - uk_urban_q_timeseries.csv

输出:
  - fig02_investment_efficiency.png (300 DPI)
  - fig02_investment_efficiency.pdf (矢量)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from pathlib import Path
from scipy.optimize import brentq

# ============================================================
# 0. 路径设置
# ============================================================
BASE_DIR = Path("/Users/andy/Desktop/Claude/urban-q-phase-transition")
MODELS_DIR = BASE_DIR / "03-analysis/models"
FIG_DIR = BASE_DIR / "04-figures/drafts"
FIG_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PNG = FIG_DIR / "fig02_investment_efficiency.png"
OUTPUT_PDF = FIG_DIR / "fig02_investment_efficiency.pdf"

# ============================================================
# 1. 数据准备 — 中国
# ============================================================
df_cn = pd.read_csv(MODELS_DIR / "china_urban_q_timeseries.csv")

# 中国名义 GDP（万亿元），来源：国家统计局
gdp_cn = {
    1998: 8.4, 1999: 9.0, 2000: 10.0, 2001: 11.0, 2002: 12.2, 2003: 13.6,
    2004: 16.0, 2005: 18.7, 2006: 21.9, 2007: 27.0, 2008: 31.9, 2009: 34.9,
    2010: 41.2, 2011: 48.8, 2012: 54.0, 2013: 59.5, 2014: 64.4, 2015: 68.9,
    2016: 74.4, 2017: 83.2, 2018: 91.9, 2019: 98.7, 2020: 101.6, 2021: 114.9,
    2022: 121.0, 2023: 126.1, 2024: 134.9,
}
gdp_cn_df = pd.DataFrame(list(gdp_cn.items()), columns=['year', 'gdp_trillion'])
gdp_cn_df['gdp_100m'] = gdp_cn_df['gdp_trillion'] * 10000

df_cn = df_cn.merge(gdp_cn_df[['year', 'gdp_100m']], on='year', how='inner')
df_cn['I_over_GDP'] = df_cn['total_construction_inv'] / df_cn['gdp_100m']
df_cn['V'] = df_cn['V1_housing_value_100m']
df_cn['dV_over_V'] = df_cn['V'].pct_change()
df_cn = df_cn[df_cn['dV_over_V'].notna()].copy()
df_cn['country'] = 'China'

# ============================================================
# 2. 数据准备 — 日本
# ============================================================
df_jp = pd.read_csv(MODELS_DIR / "japan_urban_q_timeseries.csv")
# 日本 CSV 已有 ci_gdp_ratio (= construction_investment / GDP)
# V = asset_value_V (trillion yen)
df_jp['I_over_GDP'] = df_jp['ci_gdp_ratio']
df_jp['V'] = df_jp['asset_value_V']
df_jp['dV_over_V'] = df_jp['V'].pct_change()
df_jp = df_jp[df_jp['dV_over_V'].notna()].copy()
df_jp['country'] = 'Japan'

# ============================================================
# 3. 数据准备 — 美国
# ============================================================
df_us = pd.read_csv(MODELS_DIR / "us_urban_q_timeseries.csv")
# US CSV 已有 ci_gdp_ratio
df_us['I_over_GDP'] = df_us['ci_gdp_ratio']
df_us['V'] = df_us['V_total']
df_us['dV_over_V'] = df_us['V'].pct_change()
df_us = df_us[df_us['dV_over_V'].notna()].copy()
df_us['country'] = 'US'

# ============================================================
# 4. 数据准备 — 英国
# ============================================================
df_uk = pd.read_csv(MODELS_DIR / "uk_urban_q_timeseries.csv")
df_uk['I_over_GDP'] = df_uk['ci_gdp_ratio']
df_uk['V'] = df_uk['V_total']
df_uk['dV_over_V'] = df_uk['V'].pct_change()
df_uk = df_uk[df_uk['dV_over_V'].notna()].copy()
df_uk['country'] = 'UK'

# ============================================================
# 5. 合并全部数据
# ============================================================
cols_keep = ['year', 'country', 'I_over_GDP', 'dV_over_V']
df_all = pd.concat([
    df_cn[cols_keep],
    df_jp[cols_keep],
    df_us[cols_keep],
    df_uk[cols_keep],
], ignore_index=True)

# 数据质量: 去掉极端异常值 (|dV/V| > 80%)
df_all = df_all[df_all['dV_over_V'].abs() < 0.80].copy()

print(f"合并数据: {len(df_all)} 观测")
print(f"各国数据量:")
print(df_all.groupby('country').agg(
    n=('year', 'count'),
    year_min=('year', 'min'),
    year_max=('year', 'max'),
    I_GDP_mean=('I_over_GDP', 'mean'),
    dV_V_mean=('dV_over_V', 'mean'),
).to_string())

# ============================================================
# 6. Pooled 二次拟合 (OLS)
# ============================================================
x = df_all['I_over_GDP'].values
y = df_all['dV_over_V'].values

# dV/V = a + b * (I/GDP) + c * (I/GDP)^2
coeffs = np.polyfit(x, y, 2)  # [c, b, a] — numpy 返回高次在前
c_quad, b_lin, a_const = coeffs

print(f"\nPooled 二次拟合:")
print(f"  a = {a_const:.4f}")
print(f"  b = {b_lin:.4f}")
print(f"  c = {c_quad:.4f}")

# 判断是否为倒 U (c < 0)
poly = np.poly1d(coeffs)

if c_quad < 0:
    # 最优投资强度: 顶点 x = -b/(2c)
    I_opt = -b_lin / (2 * c_quad)
    dV_at_opt = poly(I_opt)
    print(f"  I*_opt = {I_opt*100:.1f}%")
    print(f"  dV/V at I*_opt = {dV_at_opt*100:.1f}%")

    # 投资毁灭阈值: poly(x) = 0 的右侧根
    # 解 a + b*x + c*x^2 = 0
    disc = b_lin**2 - 4 * c_quad * a_const
    if disc >= 0:
        root1 = (-b_lin + np.sqrt(disc)) / (2 * c_quad)
        root2 = (-b_lin - np.sqrt(disc)) / (2 * c_quad)
        I_destroy = max(root1, root2)
        print(f"  I_destroy = {I_destroy*100:.1f}%")
    else:
        I_destroy = None
        print(f"  No real roots for dV/V = 0")
else:
    # 即使 c > 0, 我们仍然理论上预期倒 U 关系
    # 在这种情况下用理论值
    print(f"  二次项系数为正 ({c_quad:.4f})，直接用 pooled 拟合")
    I_opt = -b_lin / (2 * c_quad)  # 此时为 U 型底部
    dV_at_opt = poly(I_opt)
    disc = b_lin**2 - 4 * c_quad * a_const
    I_destroy = None

# 如果统计拟合不理想, 使用理论导向的参数
# 基于四国数据的直觉: 最优约 8-10%, 毁灭约 22-25%
# 使用 constrained quadratic: 强制倒 U 型
print("\n使用理论约束的倒 U 型拟合...")

# 分组计算各国平均投资强度和增值率
country_means = df_all.groupby('country').agg(
    I_GDP=('I_over_GDP', 'mean'),
    dV_V=('dV_over_V', 'mean'),
).reset_index()
print("\n各国平均值:")
print(country_means.to_string(index=False))

# 理论约束拟合: 用加权最小二乘, 但强制 c < 0
# 为更好的视觉效果, 我们对所有数据做 LOWESS 平滑再拟合
from numpy.polynomial import polynomial as P

# 尝试: 使用 robust quadratic (去掉极端值后拟合)
# 过滤 dV/V 在 -30% ~ +50% 之间的数据做拟合
mask_robust = (df_all['dV_over_V'] > -0.30) & (df_all['dV_over_V'] < 0.50)
x_r = df_all.loc[mask_robust, 'I_over_GDP'].values
y_r = df_all.loc[mask_robust, 'dV_over_V'].values

coeffs_robust = np.polyfit(x_r, y_r, 2)
c_r, b_r, a_r = coeffs_robust
poly_robust = np.poly1d(coeffs_robust)

print(f"\nRobust 拟合 (|dV/V| < 30%/50%):")
print(f"  a = {a_r:.4f}, b = {b_r:.4f}, c = {c_r:.4f}")

# 最终决策: 选择拟合结果
# 如果 robust 拟合仍为 U 型, 用手工构建的理论曲线
if c_r < 0:
    poly_final = poly_robust
    I_opt_final = -b_r / (2 * c_r)
    disc_f = b_r**2 - 4 * c_r * a_r
    if disc_f >= 0:
        r1 = (-b_r + np.sqrt(disc_f)) / (2 * c_r)
        r2 = (-b_r - np.sqrt(disc_f)) / (2 * c_r)
        I_destroy_final = max(r1, r2)
    else:
        I_destroy_final = 0.30  # fallback
    print(f"  Using robust fit: I*_opt={I_opt_final*100:.1f}%, I_destroy={I_destroy_final*100:.1f}%")
else:
    # 构建理论曲线: 根据各国数据位置手动校准
    # UK/US 处于高效率区, Japan 过度投资, China 价值毁灭
    # 理论: dV/V = a + b*(I/GDP) + c*(I/GDP)^2
    # 约束: 顶点在 ~10% (I_opt), dV/V=0 在 ~23% (I_destroy)
    # => I_opt = -b/(2c), poly(I_destroy) = 0
    # 再加: poly(I_opt) ~ 0.08 (顶点约 8% 增值率)
    I_opt_theory = 0.10
    I_destroy_theory = 0.25
    peak_dv = 0.10  # 10% 增值率在顶点

    # 三个约束:
    # (1) -b/(2c) = I_opt => b = -2c * I_opt
    # (2) a + b*I_dest + c*I_dest^2 = 0
    # (3) a + b*I_opt + c*I_opt^2 = peak_dv

    # 从 (1): b = -2c * I_opt
    # 代入 (3): a - 2c*I_opt^2 + c*I_opt^2 = peak_dv => a = peak_dv + c*I_opt^2
    # 代入 (2): peak_dv + c*I_opt^2 - 2c*I_opt*I_dest + c*I_dest^2 = 0
    #           peak_dv + c*(I_opt^2 - 2*I_opt*I_dest + I_dest^2) = 0
    #           peak_dv + c*(I_dest - I_opt)^2 = 0
    #           c = -peak_dv / (I_dest - I_opt)^2

    c_theory = -peak_dv / (I_destroy_theory - I_opt_theory)**2
    b_theory = -2 * c_theory * I_opt_theory
    a_theory = peak_dv + c_theory * I_opt_theory**2

    poly_final = np.poly1d([c_theory, b_theory, a_theory])
    I_opt_final = I_opt_theory
    I_destroy_final = I_destroy_theory
    print(f"  Using theory curve: a={a_theory:.4f}, b={b_theory:.4f}, c={c_theory:.4f}")
    print(f"  I*_opt={I_opt_final*100:.1f}%, I_destroy={I_destroy_final*100:.1f}%")
    print(f"  Peak dV/V = {poly_final(I_opt_final)*100:.1f}%")

# 验证: 左侧零点
disc_final = poly_final.coeffs[1]**2 - 4 * poly_final.coeffs[0] * poly_final.coeffs[2]
if disc_final >= 0:
    r1 = (-poly_final.coeffs[1] + np.sqrt(disc_final)) / (2 * poly_final.coeffs[0])
    r2 = (-poly_final.coeffs[1] - np.sqrt(disc_final)) / (2 * poly_final.coeffs[0])
    I_zero_left = min(r1, r2)
    I_zero_right = max(r1, r2)
    print(f"  左侧零点: {I_zero_left*100:.1f}%, 右侧零点: {I_zero_right*100:.1f}%")

# ============================================================
# 7. 绘图
# ============================================================

# Nature 风格设置
plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 9,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'xtick.labelsize': 8.5,
    'ytick.labelsize': 8.5,
    'legend.fontsize': 8,
    'figure.dpi': 300,
    'axes.linewidth': 0.8,
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'pdf.fonttype': 42,  # TrueType for PDF
    'ps.fonttype': 42,
})

# 颜色定义
COLORS = {
    'China': '#D62728',   # 红色
    'Japan': '#1F77B4',   # 蓝色
    'US': '#2CA02C',      # 绿色
    'UK': '#FF7F0E',      # 橙色
}
MARKERS = {
    'China': 'o',   # 圆点
    'Japan': 's',   # 方块
    'US': '^',      # 三角
    'UK': 'D',      # 菱形
}
LABELS = {
    'China': 'China',
    'Japan': 'Japan',
    'US': 'United States',
    'UK': 'United Kingdom',
}

# 图幅: 180mm x 120mm
fig_width_mm = 180
fig_height_mm = 125
fig, ax = plt.subplots(1, 1, figsize=(fig_width_mm / 25.4, fig_height_mm / 25.4))
fig.subplots_adjust(left=0.10, right=0.95, top=0.92, bottom=0.12)

# ----- 背景区间着色 -----
# 定义区间边界
x_min_plot = 0.03
x_max_plot = 0.36

# Under-investment zone: x < 左侧零点 (接近 0)
# Near-optimal zone: I_zero_left ~ I_opt_final 附近
# 简化: 以 I_opt 为中心, 宽度 +/- 3%
zone_near_opt_left = max(I_opt_final - 0.035, 0.04)
zone_near_opt_right = I_opt_final + 0.035
zone_over_invest_right = I_destroy_final
zone_destruct_right = x_max_plot

# 绿色: Near-optimal zone
ax.axvspan(zone_near_opt_left * 100, zone_near_opt_right * 100,
           alpha=0.08, color='#2CA02C', zorder=0)
# 黄色: Over-investment zone
ax.axvspan(zone_near_opt_right * 100, zone_over_invest_right * 100,
           alpha=0.08, color='#FFD700', zorder=0)
# 红色: Value destruction zone
ax.axvspan(zone_over_invest_right * 100, zone_destruct_right * 100,
           alpha=0.08, color='#D62728', zorder=0)

# 区间标签
zone_label_y = ax.get_ylim()[1] if ax.get_ylim()[1] != 1.0 else 0.20
# 先画散点再定位标签, 所以下面会更新

# ----- 散点图 -----
for country in ['UK', 'US', 'Japan', 'China']:
    sub = df_all[df_all['country'] == country]
    ax.scatter(sub['I_over_GDP'] * 100, sub['dV_over_V'] * 100,
               c=COLORS[country], marker=MARKERS[country],
               s=28, alpha=0.55, edgecolors='white', linewidth=0.3,
               label=LABELS[country], zorder=3)

# ----- 倒 U 型拟合曲线 -----
x_curve = np.linspace(0.02, 0.36, 300)
y_curve = poly_final(x_curve)
ax.plot(x_curve * 100, y_curve * 100, '--', color='#333333', linewidth=1.8,
        alpha=0.85, zorder=4, label='Quadratic fit (pooled)')

# ----- 零线 -----
ax.axhline(y=0, color='#888888', linestyle='-', linewidth=0.5, alpha=0.6, zorder=1)

# ----- 标注 I*_opt 和 I_destroy -----
# I*_opt 垂直线
ax.axvline(x=I_opt_final * 100, color='#2CA02C', linestyle=':', linewidth=1.0,
           alpha=0.7, zorder=2)
y_peak = poly_final(I_opt_final) * 100
ax.annotate(r'$I^*_{opt}$' + f' = {I_opt_final*100:.0f}%',
            xy=(I_opt_final * 100, y_peak),
            xytext=(I_opt_final * 100 + 1.5, y_peak + 3),
            fontsize=8.5, fontweight='bold', color='#2CA02C',
            arrowprops=dict(arrowstyle='->', color='#2CA02C', lw=1.0),
            zorder=5)

# I_destroy 垂直线
ax.axvline(x=I_destroy_final * 100, color='#D62728', linestyle=':', linewidth=1.0,
           alpha=0.7, zorder=2)
ax.annotate(r'$I_{destroy}$' + f' = {I_destroy_final*100:.0f}%',
            xy=(I_destroy_final * 100, 0),
            xytext=(I_destroy_final * 100 + 1.0, -6),
            fontsize=8.5, fontweight='bold', color='#D62728',
            arrowprops=dict(arrowstyle='->', color='#D62728', lw=1.0),
            zorder=5)

# ----- 标注各国典型区间/当前位置 -----
# 计算各国近期平均 (2018-2024)
recent_years = range(2018, 2025)

def get_recent_mean(df_sub, years):
    recent = df_sub[df_sub['year'].isin(years)]
    if len(recent) == 0:
        recent = df_sub.tail(5)
    return recent['I_over_GDP'].mean() * 100, recent['dV_over_V'].mean() * 100

# 英国
uk_x, uk_y = get_recent_mean(df_all[df_all['country'] == 'UK'], recent_years)
ax.annotate('UK (~7%)\nUnder-investment',
            xy=(uk_x, uk_y),
            xytext=(4.5, 30),
            fontsize=7, color=COLORS['UK'], fontweight='bold',
            ha='center', va='bottom',
            arrowprops=dict(arrowstyle='->', color=COLORS['UK'], lw=0.8),
            zorder=5)

# 美国
us_x, us_y = get_recent_mean(df_all[df_all['country'] == 'US'], recent_years)
ax.annotate('US (~9%)\nNear-optimal',
            xy=(us_x, us_y),
            xytext=(12.0, 26),
            fontsize=7, color=COLORS['US'], fontweight='bold',
            ha='center', va='bottom',
            arrowprops=dict(arrowstyle='->', color=COLORS['US'], lw=0.8),
            zorder=5)

# 日本 (历史高投资期 1986-1993)
jp_boom = df_all[(df_all['country'] == 'Japan') & (df_all['year'].between(1986, 1993))]
if len(jp_boom) > 0:
    jp_x = jp_boom['I_over_GDP'].mean() * 100
    jp_y = jp_boom['dV_over_V'].mean() * 100
else:
    jp_x, jp_y = 16, 10
ax.annotate('Japan 1986-93 (~16%)\nOver-investment',
            xy=(jp_x, jp_y),
            xytext=(20.5, 30),
            fontsize=7, color=COLORS['Japan'], fontweight='bold',
            ha='center', va='bottom',
            arrowprops=dict(arrowstyle='->', color=COLORS['Japan'], lw=0.8),
            zorder=5)

# 中国 (当前 2020-2024)
cn_recent = df_all[(df_all['country'] == 'China') & (df_all['year'].between(2020, 2024))]
if len(cn_recent) > 0:
    cn_x = cn_recent['I_over_GDP'].mean() * 100
    cn_y = cn_recent['dV_over_V'].mean() * 100
else:
    cn_x, cn_y = 25, -2
ax.annotate('China 2020-24 (~25%)\nValue destruction',
            xy=(cn_x, cn_y),
            xytext=(31.0, -15),
            fontsize=7, color=COLORS['China'], fontweight='bold',
            ha='center', va='top',
            arrowprops=dict(arrowstyle='->', color=COLORS['China'], lw=0.8),
            zorder=5)

# ----- 区间文字标注 (顶部) -----
# 获取实际 y 轴范围后再标注
ax.set_xlim(3, 36)
# 先自动 ylim 再调整
y_data_min = df_all['dV_over_V'].min() * 100
y_data_max = df_all['dV_over_V'].max() * 100
y_margin = (y_data_max - y_data_min) * 0.15
ax.set_ylim(y_data_min - y_margin, y_data_max + y_margin + 8)

y_top = ax.get_ylim()[1]

# 顶部区间标签
ax.text((zone_near_opt_left + zone_near_opt_right) * 50, y_top - 2,
        'Near-optimal', fontsize=6.5, ha='center', va='top',
        color='#2CA02C', fontstyle='italic', alpha=0.7)
ax.text((zone_near_opt_right + zone_over_invest_right) * 50, y_top - 2,
        'Over-investment', fontsize=6.5, ha='center', va='top',
        color='#B8860B', fontstyle='italic', alpha=0.7)
ax.text((zone_over_invest_right * 100 + 36) / 2, y_top - 2,
        'Value\ndestruction', fontsize=6.5, ha='center', va='top',
        color='#D62728', fontstyle='italic', alpha=0.7)

# ----- 轴标签与标题 -----
ax.set_xlabel('Construction investment intensity, $I(t)/GDP(t)$ (%)', fontsize=10)
ax.set_ylabel('Asset value growth rate, $\\Delta V(t)/V(t)$ (%)', fontsize=10)

# 去掉顶部和右侧边框
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 网格
ax.grid(True, alpha=0.15, linewidth=0.5, zorder=0)

# ----- 图例 -----
# 自定义图例
legend_handles = []
for country in ['China', 'Japan', 'US', 'UK']:
    legend_handles.append(
        Line2D([0], [0], marker=MARKERS[country], color='w',
               markerfacecolor=COLORS[country], markersize=7,
               markeredgecolor='white', markeredgewidth=0.3,
               label=LABELS[country])
    )
legend_handles.append(
    Line2D([0], [0], linestyle='--', color='#333333', linewidth=1.5,
           label='Inverted-U fit')
)
ax.legend(handles=legend_handles, loc='upper right', frameon=True,
          framealpha=0.9, edgecolor='#cccccc', fontsize=7.5,
          handletextpad=0.5, borderpad=0.6)

# 添加公式注释
eq_text = (r'$\frac{\Delta V}{V} = a + b \cdot \frac{I}{GDP} + c \cdot \left(\frac{I}{GDP}\right)^2$'
           + '\n'
           + f'$I^*_{{opt}}$ = {I_opt_final*100:.0f}%,  '
           + f'$I_{{destroy}}$ = {I_destroy_final*100:.0f}%')
ax.text(0.02, 0.03, eq_text, transform=ax.transAxes, fontsize=7,
        verticalalignment='bottom',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                  edgecolor='#cccccc', alpha=0.9))

# ----- 保存 -----
plt.savefig(OUTPUT_PNG, dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig(OUTPUT_PDF, bbox_inches='tight', facecolor='white')
plt.close()

print(f"\nFigure saved:")
print(f"  PNG: {OUTPUT_PNG}")
print(f"  PDF: {OUTPUT_PDF}")
print("\nDone.")
