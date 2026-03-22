#!/usr/bin/env python3
"""
07_inverted_u_test.py
=====================
目的：检验中国国家层面投资-价值的倒 U 型关系。
     估计 ΔV/V = a + b*(I/GDP) - c*(I/GDP)^2 + ε

理论背景（研究框架 v2.0 第四节 4.3）：
  投资强度（I/GDP）与资产增值率（ΔV/V）之间存在倒 U 型关系：
  - 低投资阶段：投资带来正向资产增值
  - 最优投资强度 I*_opt/GDP = b/(2c)：资产增值率最大化
  - 投资毁灭阈值 I_destroy/GDP = b/c：超过此值 ΔV < 0
  - 中国在2022年后MUQ<0，可能已越过毁灭阈值

输入数据：
  - china_urban_q_timeseries.csv（V(t), I(t) 等已计算数据）
  - 硬编码：中国名义 GDP 数据（NBS 公开数据）

输出：
  - inverted_u_regression.txt（回归结果）
  - fig07_inverted_u.png（散点图 + 二次拟合曲线）

依赖包：pandas, numpy, matplotlib, statsmodels
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from pathlib import Path

# ============================================================
# 0. 路径设置
# ============================================================
BASE_DIR = Path("/Users/andy/Desktop/Claude/urban-q-phase-transition")
Q_CSV = BASE_DIR / "03-analysis/models/china_urban_q_timeseries.csv"
OUTPUT_TXT = BASE_DIR / "03-analysis/models/inverted_u_regression.txt"
OUTPUT_FIG = BASE_DIR / "04-figures/drafts/fig07_inverted_u.png"

# ============================================================
# 1. 读取已有数据
# ============================================================
df_q = pd.read_csv(Q_CSV)

# ============================================================
# 2. 构建 GDP 数据
# ============================================================
# 硬编码中国名义 GDP（万亿元），来源：国家统计局
# 注：此处 GDP 单位为万亿元，需转换为亿元（× 10000）以与 V、I 单位一致
gdp_data = {
    2000: 10.0, 2002: 12.2, 2004: 16.0, 2005: 18.7,
    2006: 21.9, 2007: 27.0, 2008: 31.9, 2009: 34.9,
    2010: 41.2, 2011: 48.8, 2012: 54.0, 2013: 59.5,
    2014: 64.4, 2015: 68.9, 2016: 74.4, 2017: 83.2,
    2018: 91.9, 2019: 98.7, 2020: 101.6, 2021: 114.9,
    2022: 121.0, 2023: 126.1, 2024: 134.9,
}

gdp_df = pd.DataFrame(list(gdp_data.items()), columns=['year', 'gdp_trillion'])
gdp_df['gdp_100m'] = gdp_df['gdp_trillion'] * 10000  # 转换为亿元

# 对缺失年份做线性插值（2001, 2003）
all_years_gdp = pd.DataFrame({'year': range(2000, 2025)})
gdp_df = all_years_gdp.merge(gdp_df, on='year', how='left')
gdp_df['gdp_trillion'] = gdp_df['gdp_trillion'].interpolate(method='linear')
gdp_df['gdp_100m'] = gdp_df['gdp_trillion'] * 10000

# ============================================================
# 3. 合并数据并构建回归变量
# ============================================================
df = df_q.merge(gdp_df[['year', 'gdp_trillion', 'gdp_100m']], on='year', how='inner')

# 过滤有效数据
df = df[df['V1_housing_value_100m'].notna() & df['total_construction_inv'].notna() &
        df['gdp_100m'].notna()].copy()

# 被解释变量: ΔV/V — 资产增值率
df['delta_V'] = df['V1_housing_value_100m'].diff()
df['dV_over_V'] = df['delta_V'] / df['V1_housing_value_100m'].shift(1)

# 核心解释变量: I/GDP — 投资强度
df['I_over_GDP'] = df['total_construction_inv'] / df['gdp_100m']

# 平方项
df['I_over_GDP_sq'] = df['I_over_GDP'] ** 2

# 去掉第一年（没有ΔV）
df_reg = df[df['dV_over_V'].notna()].copy()

print(f"回归样本: {df_reg['year'].min()}-{df_reg['year'].max()}, N={len(df_reg)}")
print(f"\n数据概览:")
print(df_reg[['year', 'I_over_GDP', 'dV_over_V', 'total_construction_inv', 'gdp_100m']].to_string(index=False))

# ============================================================
# 4. OLS 回归: ΔV/V = a + b*(I/GDP) - c*(I/GDP)^2
# ============================================================

X = df_reg[['I_over_GDP', 'I_over_GDP_sq']]
X = sm.add_constant(X)
y = df_reg['dV_over_V']

model = sm.OLS(y, X).fit(cov_type='HC1')  # 异方差稳健标准误

print("\n" + "=" * 60)
print("OLS 回归结果")
print("=" * 60)
print(model.summary())

# 提取关键系数
a_hat = model.params['const']
b_hat = model.params['I_over_GDP']
c_hat = -model.params['I_over_GDP_sq']  # 注意：模型中 I_over_GDP_sq 系数预期为负

# 注意：如果 I_over_GDP_sq 系数为负，则 c_hat > 0（符合倒U型预期）
# 模型形式: ΔV/V = a + b*(I/GDP) + coef_sq*(I/GDP)^2
# 倒U型要求: coef_sq < 0, 即 c = -coef_sq > 0
coef_sq = model.params['I_over_GDP_sq']

# ============================================================
# 5. 计算关键衍生量
# ============================================================

report_lines = []
report_lines.append("=" * 70)
report_lines.append("投资-价值倒 U 型关系检验报告")
report_lines.append("=" * 70)
report_lines.append(f"分析日期: 2026-03-20")
report_lines.append(f"样本: 中国国家时序数据 {int(df_reg['year'].min())}-{int(df_reg['year'].max())}")
report_lines.append(f"观测数: {len(df_reg)}")
report_lines.append("")

report_lines.append("一、模型设定")
report_lines.append("-" * 40)
report_lines.append("  ΔV(t)/V(t-1) = a + b * [I(t)/GDP(t)] + c_sq * [I(t)/GDP(t)]^2 + epsilon")
report_lines.append("  其中:")
report_lines.append("    V = 住宅市场总价值 (V1_housing_value_100m)")
report_lines.append("    I = 总建设投资 (total_construction_inv)")
report_lines.append("    GDP = 名义GDP")
report_lines.append("  异方差稳健标准误 (HC1)")
report_lines.append("")

report_lines.append("二、回归结果")
report_lines.append("-" * 40)
report_lines.append(f"  截距 a = {model.params['const']:.4f} (p={model.pvalues['const']:.4f})")
report_lines.append(f"  一次项 b = {model.params['I_over_GDP']:.4f} (p={model.pvalues['I_over_GDP']:.4f})")
report_lines.append(f"  二次项 c_sq = {coef_sq:.4f} (p={model.pvalues['I_over_GDP_sq']:.4f})")
report_lines.append(f"  R-squared = {model.rsquared:.4f}")
report_lines.append(f"  Adj R-squared = {model.rsquared_adj:.4f}")
report_lines.append(f"  F-statistic = {model.fvalue:.4f} (p={model.f_pvalue:.6f})")
report_lines.append(f"  AIC = {model.aic:.2f}")
report_lines.append(f"  BIC = {model.bic:.2f}")
report_lines.append("")

report_lines.append("三、倒 U 型检验")
report_lines.append("-" * 40)

if coef_sq < 0:
    report_lines.append(f"  二次项系数为负 ({coef_sq:.4f})，支持倒 U 型假设")
    c_positive = -coef_sq  # c > 0
    b_val = model.params['I_over_GDP']

    if b_val > 0:
        I_opt = b_val / (2 * c_positive)
        I_destroy = b_val / c_positive
        report_lines.append(f"  最优投资强度 I*_opt/GDP = b/(2c) = {I_opt:.4f} ({I_opt*100:.2f}%)")
        report_lines.append(f"  投资毁灭阈值 I_destroy/GDP = b/c = {I_destroy:.4f} ({I_destroy*100:.2f}%)")

        # 当前中国位置
        current_year = int(df_reg['year'].max())
        current_i_gdp = df_reg[df_reg['year'] == current_year]['I_over_GDP'].values[0]
        current_dv = df_reg[df_reg['year'] == current_year]['dV_over_V'].values[0]
        report_lines.append("")
        report_lines.append(f"  中国当前位置 ({current_year}年):")
        report_lines.append(f"    I/GDP = {current_i_gdp:.4f} ({current_i_gdp*100:.2f}%)")
        report_lines.append(f"    ΔV/V = {current_dv:.4f} ({current_dv*100:.2f}%)")

        if current_i_gdp > I_destroy:
            report_lines.append(f"    已超过投资毁灭阈值 ({current_i_gdp*100:.2f}% > {I_destroy*100:.2f}%)")
        elif current_i_gdp > I_opt:
            report_lines.append(f"    已超过最优投资强度 ({current_i_gdp*100:.2f}% > {I_opt*100:.2f}%)")
            report_lines.append(f"    但尚未达到毁灭阈值 ({current_i_gdp*100:.2f}% < {I_destroy*100:.2f}%)")
        else:
            report_lines.append(f"    尚在最优投资强度以下")
    else:
        I_opt = None
        I_destroy = None
        report_lines.append(f"  注意: 一次项系数为负 ({b_val:.4f})，倒 U 型顶点在负区域")
        report_lines.append(f"  这意味着在当前数据范围内，投资增加始终降低资产增值率")
else:
    I_opt = None
    I_destroy = None
    report_lines.append(f"  二次项系数为正 ({coef_sq:.4f})，不支持倒 U 型假设")
    report_lines.append(f"  数据显示 U 型关系（投资效率先降后升），可能需要更长时间序列或面板数据验证")

# ============================================================
# 5b. 补充：仅用线性模型作为对照
# ============================================================
report_lines.append("")
report_lines.append("四、线性模型对照")
report_lines.append("-" * 40)

X_linear = sm.add_constant(df_reg[['I_over_GDP']])
model_linear = sm.OLS(y, X_linear).fit(cov_type='HC1')
report_lines.append(f"  线性模型: ΔV/V = {model_linear.params['const']:.4f} + {model_linear.params['I_over_GDP']:.4f} * (I/GDP)")
report_lines.append(f"  R-squared = {model_linear.rsquared:.4f}")
report_lines.append(f"  AIC = {model_linear.aic:.2f} (二次模型 AIC = {model.aic:.2f})")
if model.aic < model_linear.aic:
    report_lines.append(f"  二次模型 AIC 更低，优于线性模型")
else:
    report_lines.append(f"  线性模型 AIC 更低或相当")

# ============================================================
# 5c. 按时期分组分析
# ============================================================
report_lines.append("")
report_lines.append("五、分时期投资效率")
report_lines.append("-" * 40)
report_lines.append(f"  {'时期':>12} {'I/GDP均值':>12} {'ΔV/V均值':>12} {'N':>4}")

periods = [(2000, 2007, "2000-2007"), (2008, 2014, "2008-2014"),
           (2015, 2019, "2015-2019"), (2020, 2024, "2020-2024")]
for y1, y2, label in periods:
    sub = df_reg[(df_reg['year'] >= y1) & (df_reg['year'] <= y2)]
    if len(sub) > 0:
        report_lines.append(f"  {label:>12} {sub['I_over_GDP'].mean()*100:>10.2f}% {sub['dV_over_V'].mean()*100:>10.2f}% {len(sub):>4}")

# ============================================================
# 6. 可视化
# ============================================================

# 中文字体配置
plt.rcParams['font.family'] = ['PingFang HK', 'Songti SC', 'STHeiti', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

plt.rcParams.update({
    'font.size': 9,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 7.5,
    'figure.dpi': 300,
    'axes.linewidth': 0.8,
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
})

COLORS = {
    'scatter_early': '#4393C3',   # 蓝色 — 早期
    'scatter_late': '#D6604D',    # 红色 — 晚期
    'fit': '#2166AC',             # 深蓝 — 拟合曲线
    'opt': '#2CA02C',             # 绿色 — 最优点
    'destroy': '#B2182B',         # 深红 — 毁灭点
    'ref': '#666666',
}

fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
fig.subplots_adjust(wspace=0.30, top=0.90, bottom=0.12, left=0.08, right=0.95)

# ------ Panel A: 散点图 + 二次拟合 ------
ax = axes[0]

# 用年份着色散点
sc = ax.scatter(df_reg['I_over_GDP'] * 100, df_reg['dV_over_V'] * 100,
                c=df_reg['year'], cmap='RdYlBu_r', s=50, edgecolors='white',
                linewidth=0.5, zorder=3)

# 标注关键年份
for _, row in df_reg.iterrows():
    yr = int(row['year'])
    if yr in [2000, 2004, 2008, 2010, 2014, 2018, 2021, 2024]:
        ax.annotate(str(yr), (row['I_over_GDP']*100, row['dV_over_V']*100),
                    fontsize=6.5, ha='left', va='bottom',
                    xytext=(3, 3), textcoords='offset points')

# 二次拟合曲线
x_range = np.linspace(df_reg['I_over_GDP'].min() * 0.8,
                      max(df_reg['I_over_GDP'].max() * 1.2, 0.40), 200)
y_fit = model.params['const'] + model.params['I_over_GDP'] * x_range + model.params['I_over_GDP_sq'] * x_range**2
ax.plot(x_range * 100, y_fit * 100, '-', color=COLORS['fit'], linewidth=2.0,
        label='二次拟合', zorder=2)

# 标注最优点和毁灭点
if I_opt is not None and b_hat > 0:
    # 最优投资强度
    y_at_opt = model.params['const'] + model.params['I_over_GDP'] * I_opt + model.params['I_over_GDP_sq'] * I_opt**2
    ax.axvline(x=I_opt*100, color=COLORS['opt'], linestyle='--', linewidth=1.0, alpha=0.8)
    ax.annotate(f'I*_opt={I_opt*100:.1f}%',
                xy=(I_opt*100, y_at_opt*100), xytext=(I_opt*100+1, y_at_opt*100+3),
                fontsize=8, fontweight='bold', color=COLORS['opt'],
                arrowprops=dict(arrowstyle='->', color=COLORS['opt'], lw=0.8))

    # 毁灭阈值
    if I_destroy < x_range.max():
        ax.axvline(x=I_destroy*100, color=COLORS['destroy'], linestyle='--', linewidth=1.0, alpha=0.8)
        ax.annotate(f'I_destroy={I_destroy*100:.1f}%',
                    xy=(I_destroy*100, 0), xytext=(I_destroy*100+0.5, -5),
                    fontsize=8, fontweight='bold', color=COLORS['destroy'],
                    arrowprops=dict(arrowstyle='->', color=COLORS['destroy'], lw=0.8))

# 当前中国位置高亮
current = df_reg[df_reg['year'] == df_reg['year'].max()].iloc[0]
ax.scatter(current['I_over_GDP']*100, current['dV_over_V']*100,
           s=120, facecolors='none', edgecolors='red', linewidth=2.0, zorder=5)
ax.annotate(f'中国{int(current["year"])}',
            xy=(current['I_over_GDP']*100, current['dV_over_V']*100),
            xytext=(current['I_over_GDP']*100-3, current['dV_over_V']*100-5),
            fontsize=9, fontweight='bold', color='red',
            arrowprops=dict(arrowstyle='->', color='red', lw=1.2))

ax.axhline(y=0, color=COLORS['ref'], linestyle='-', linewidth=0.6, alpha=0.5)
cbar = plt.colorbar(sc, ax=ax, shrink=0.8, pad=0.02)
cbar.set_label('年份', fontsize=8)

ax.set_xlabel('投资强度 I/GDP (%)')
ax.set_ylabel('资产增值率 ΔV/V (%)')
ax.set_title('A. 投资-价值倒 U 型关系', fontweight='bold', loc='left')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, alpha=0.2, linewidth=0.5)

# 添加回归方程文本框
eq_text = f'$\\Delta V/V = {model.params["const"]:.3f} + {model.params["I_over_GDP"]:.2f} \\cdot (I/GDP) '
eq_text += f'{model.params["I_over_GDP_sq"]:+.2f} \\cdot (I/GDP)^2$'
eq_text += f'\n$R^2 = {model.rsquared:.3f}$, $N = {len(df_reg)}$'
ax.text(0.05, 0.05, eq_text, transform=ax.transAxes, fontsize=7,
        verticalalignment='bottom', bbox=dict(boxstyle='round,pad=0.3',
        facecolor='white', edgecolor='#cccccc', alpha=0.9))

# ------ Panel B: 时序对比图（I/GDP 和 ΔV/V 双轴） ------
ax = axes[1]
ax2 = ax.twinx()

# I/GDP 柱状图（左轴）
bars = ax.bar(df_reg['year'], df_reg['I_over_GDP']*100,
              color='#4393C3', alpha=0.5, width=0.8, label='I/GDP (%)')

# ΔV/V 折线图（右轴）
colors_dv = ['#2CA02C' if v >= 0 else '#D62728' for v in df_reg['dV_over_V']]
ax2.plot(df_reg['year'], df_reg['dV_over_V']*100, '-o', color='#D6604D',
         markersize=4, linewidth=1.5, label='ΔV/V (%)', zorder=3)
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.6, alpha=0.5)

# 标注 I*_opt 水平线
if I_opt is not None and b_hat > 0:
    ax.axhline(y=I_opt*100, color=COLORS['opt'], linestyle='--', linewidth=1.0, alpha=0.8)
    ax.text(2024.5, I_opt*100, f'I*_opt={I_opt*100:.1f}%', fontsize=7,
            color=COLORS['opt'], va='center')
    if I_destroy * 100 < ax.get_ylim()[1] * 1.5:
        ax.axhline(y=I_destroy*100, color=COLORS['destroy'], linestyle='--', linewidth=1.0, alpha=0.6)
        ax.text(2024.5, I_destroy*100, f'I_dest={I_destroy*100:.1f}%', fontsize=7,
                color=COLORS['destroy'], va='center')

ax.set_xlabel('年份')
ax.set_ylabel('投资强度 I/GDP (%)', color='#4393C3')
ax2.set_ylabel('资产增值率 ΔV/V (%)', color='#D6604D')
ax.tick_params(axis='y', colors='#4393C3')
ax2.tick_params(axis='y', colors='#D6604D')

# 合并图例
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
handles = [Patch(facecolor='#4393C3', alpha=0.5, label='I/GDP (%)'),
           Line2D([0], [0], color='#D6604D', marker='o', markersize=4, label='ΔV/V (%)')]
if I_opt is not None and b_hat > 0:
    handles.append(Line2D([0], [0], color=COLORS['opt'], linestyle='--', label=f'I*_opt={I_opt*100:.1f}%'))
ax.legend(handles=handles, loc='upper left', frameon=True, framealpha=0.9,
          edgecolor='#cccccc', fontsize=7)

ax.set_title('B. 投资强度与资产增值率时序', fontweight='bold', loc='left')
ax.spines['top'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax.set_xlim(1999, 2025)

fig.suptitle('中国投资-价值倒 U 型关系检验 (2000-2024)', fontsize=13, fontweight='bold')

plt.savefig(OUTPUT_FIG, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f"\n图表已保存: {OUTPUT_FIG}")

# ============================================================
# 7. 保存回归报告
# ============================================================
report_lines.append("")
report_lines.append("六、完整回归输出")
report_lines.append("-" * 40)
report_lines.append(model.summary().as_text())

report_lines.append("")
report_lines.append("七、数据来源说明")
report_lines.append("-" * 40)
report_lines.append("  V(t): 住宅市场总价值 = 存量面积 x 均价 (china_urban_q_timeseries.csv)")
report_lines.append("  I(t): 总建设投资 = 房地产投资 + 基础设施投资 (china_urban_q_timeseries.csv)")
report_lines.append("  GDP: 国家统计局名义GDP数据（万亿元，硬编码）")
report_lines.append("")
report_lines.append("八、局限与注意事项")
report_lines.append("-" * 40)
report_lines.append("  1. 样本量有限（N=24），统计功效不足，应视为初步探索性分析")
report_lines.append("  2. 时间序列数据存在序列相关，OLS标准误可能低估")
report_lines.append("  3. V(t)的测量依赖于住宅均价，受房价周期影响大")
report_lines.append("  4. I/GDP可能存在内生性（投资和增值率互相影响），后续需IV方法")
report_lines.append("  5. 核心结论需要城市面板数据（275城市）的验证")

report = "\n".join(report_lines)
print(report)

with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
    f.write(report)
print(f"\n回归报告已保存: {OUTPUT_TXT}")

print("\n分析完成。")
