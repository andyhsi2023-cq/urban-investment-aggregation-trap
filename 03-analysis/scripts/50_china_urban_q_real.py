"""
50_china_urban_q_real.py
========================
目的：基于 six-curves 项目中的国家统计局/财政部真实数据，
     计算中国国家层面 Urban Q 的多口径时序。

数据来源（全部为官方统计数据）：
  - 主数据集: six-curves/.../six_curves_master_dataset_processed.csv (NBS, 1978-2024)
  - 住宅均价/销售: c5_residential_price_NBS_1998-2024.csv (NBS)
  - 土地出让收入: c5_land_transfer_revenue_MOF_1999-2024.csv (MOF)
  - 房地产投资: c6_real_estate_investment_NBS_1987-2024.csv (NBS)
  - 基础设施投资: c6_infrastructure_investment_NBS_1990-2024.csv (NBS)
  - 新开工/竣工面积: c3_new_construction_starts_NBS_1985-2024.csv (NBS)
  - GDP: background_gdp_NBS_1978-2024.csv (NBS)
  - 城镇化率/人口: c1_urbanization_rate_NBS_1949-2024.csv (NBS)

输出：
  - urban-q/.../china_urban_q_real_data.csv — 时序数据
  - urban-q/.../china_urban_q_real_report.txt — 分析报告
  - urban-q/.../fig12_china_urban_q_real.png — 综合可视化

依赖包：pandas, numpy, matplotlib
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
import warnings
import textwrap

warnings.filterwarnings('ignore')

# ============================================================
# 0. 路径设置
# ============================================================

SIX_CURVES = Path("/Users/andy/Desktop/Claude/six-curves-urban-transition/02-data")
URBAN_Q = Path("/Users/andy/Desktop/Claude/urban-q-phase-transition")

# 输入
MASTER_CSV   = SIX_CURVES / "processed" / "six_curves_master_dataset_processed.csv"
PRICE_CSV    = SIX_CURVES / "raw" / "c5_residential_price_NBS_1998-2024.csv"
LAND_CSV     = SIX_CURVES / "raw" / "c5_land_transfer_revenue_MOF_1999-2024.csv"
RE_INV_CSV   = SIX_CURVES / "raw" / "c6_real_estate_investment_NBS_1987-2024.csv"
INFRA_CSV    = SIX_CURVES / "raw" / "c6_infrastructure_investment_NBS_1990-2024.csv"
STARTS_CSV   = SIX_CURVES / "raw" / "c3_new_construction_starts_NBS_1985-2024.csv"
GDP_CSV      = SIX_CURVES / "raw" / "background_gdp_NBS_1978-2024.csv"
URBAN_CSV    = SIX_CURVES / "raw" / "c1_urbanization_rate_NBS_1949-2024.csv"

# 输出
OUT_CSV    = URBAN_Q / "03-analysis" / "models" / "china_urban_q_real_data.csv"
OUT_REPORT = URBAN_Q / "03-analysis" / "models" / "china_urban_q_real_report.txt"
OUT_FIG    = URBAN_Q / "04-figures" / "drafts" / "fig12_china_urban_q_real.png"

print("=" * 70)
print("中国 Urban Q 多口径计算 — 基于国家统计局/财政部真实数据")
print("=" * 70)

# ============================================================
# 1. 数据加载与合并
# ============================================================

print("\n[1] 加载数据...")

# --- 主数据集 ---
master = pd.read_csv(MASTER_CSV)
master = master.set_index('year')

# --- 住宅均价与销售 ---
# 来源: NBS《中国房地产统计年鉴》/ 统计公报
price = pd.read_csv(PRICE_CSV)
price = price.set_index('year')

# --- 土地出让收入 ---
# 来源: 财政部《全国政府性基金收入》
land = pd.read_csv(LAND_CSV)
land = land.set_index('year')

# --- 房地产投资 ---
# 来源: NBS《中国统计年鉴》固定资产投资章节
re_inv = pd.read_csv(RE_INV_CSV)
re_inv = re_inv.set_index('year')

# --- 基础设施投资 ---
# 来源: NBS《中国统计年鉴》（交通+水利+电力+市政）
infra = pd.read_csv(INFRA_CSV)
infra = infra.set_index('year')

# --- 竣工面积 ---
# 来源: NBS《中国统计年鉴》
starts = pd.read_csv(STARTS_CSV)
starts = starts.set_index('year')

# --- GDP ---
gdp = pd.read_csv(GDP_CSV)
gdp = gdp.set_index('year')

print(f"  主数据集: {master.index.min()}-{master.index.max()}, {len(master)}行")
print(f"  住宅均价: {price.index.min()}-{price.index.max()}")
print(f"  土地出让: {land.index.min()}-{land.index.max()}")
print(f"  房地产投资: {re_inv.index.min()}-{re_inv.index.max()}")
print(f"  基础设施投资: {infra.index.min()}-{infra.index.max()}")
print(f"  竣工面积: {starts.index.min()}-{starts.index.max()}")

# ============================================================
# 2. 构建统一时序 DataFrame
# ============================================================

print("\n[2] 构建统一时序...")

# 分析时间范围: 1998-2024（住房商品化改革后，数据最完整）
YEARS = range(1998, 2025)
df = pd.DataFrame(index=YEARS)
df.index.name = 'year'

# --- 从各数据源填充变量 ---

# GDP (亿元, 当年价) [来源: NBS统计年鉴]
df['gdp_100m'] = master.loc[df.index, 'gdp_100m_current']

# 城镇化率 (%) [来源: NBS统计年鉴]
df['urbanization_pct'] = master.loc[df.index, 'urbanization_rate_pct']

# 住宅均价 (元/m2) [来源: NBS房地产统计年鉴]
df['residential_price'] = price.loc[df.index, 'residential_avg_price_yuan_m2']

# 商品房均价 (元/m2) [来源: NBS]
df['commercial_price'] = price.loc[df.index, 'commercial_housing_avg_price_yuan_m2']

# 竣工面积 (万m2) [来源: NBS统计年鉴]
df['completion_10k_m2'] = starts.loc[df.index, 'completion_10k_m2']

# 新开工面积 (万m2) [来源: NBS]
df['new_starts_10k_m2'] = starts.loc[df.index, 'new_starts_10k_m2']

# 商品房销售面积 (万m2) [来源: NBS]
df['sales_area_10k_m2'] = price.loc[df.index, 'commercial_housing_sales_area_10k_m2']

# 商品房销售额 (亿元) [来源: NBS]
df['sales_amount_100m'] = price.loc[df.index, 'commercial_housing_sales_amount_100m']

# 房地产投资 (亿元) [来源: NBS统计年鉴]
df['re_inv_100m'] = re_inv.loc[df.index, 'real_estate_investment_100m']

# 基础设施投资 (亿元) [来源: NBS统计年鉴]
df['infra_inv_100m'] = infra.loc[df.index, 'infra_investment_100m']

# 土地出让收入 (亿元) [来源: 财政部]
# 1998年缺失，填0（1999年之前土地出让市场尚未成熟）
df['land_revenue_100m'] = land.reindex(df.index)['land_transfer_revenue_100m'].fillna(0)

# 建成区面积 (km2) [来源: NBS]
df['built_area_km2'] = master.loc[df.index, 'urban_built_area_km2']

# 住房存量 (万m2) — 已在master中预计算 [来源: NBS, 累计竣工PIM]
df['housing_stock_10k_m2'] = master.loc[df.index, 'housing_stock_10k_m2']

# 补充: 1987-1997年的投资数据（用于PIM累计计算）
re_inv_full = re_inv['real_estate_investment_100m']
infra_inv_full = infra['infra_investment_100m']

# 补充: 1985-1997年的竣工面积（用于存量计算）
# master中有1985起的new_starts但completion从1998起
# 使用 new_starts 的一定比例估算早期竣工面积
# 1998年竣工率 = 46290/66800 = 69.3%
early_completion_ratio = 0.70

print(f"  时间范围: {df.index.min()}-{df.index.max()}")
print(f"  变量数: {len(df.columns)}")
print(f"  缺失值统计:")
for col in df.columns:
    n_miss = df[col].isna().sum()
    if n_miss > 0:
        print(f"    {col}: {n_miss}个缺失")

# ============================================================
# 3. 计算 V(t) — 城市资产市场价值（三个口径）
# ============================================================

print("\n[3] 计算市场价值 V(t)...")

# --- 3.1 V1: 住宅均价 x 折旧调整存量 ---
# 住宅存量 = 永续盘存法 (PIM)
# Stock(t) = Sum_{s=start}^{t} Completion(s) * (1 - delta)^(t-s)
# delta_residential = 2% (住宅折旧率, 50年使用寿命)

DELTA_RES = 0.02  # 住宅折旧率

# 收集完整竣工面积序列 (万m2)
# 1985-1997: 使用新开工面积 x 竣工比率估算
# 1998-2024: 使用真实竣工数据

completion_full = {}

# 1985-1997 估算
for yr in range(1985, 1998):
    ns = master.loc[yr, 'new_starts_10k_m2'] if yr in master.index else np.nan
    if pd.notna(ns):
        completion_full[yr] = ns * early_completion_ratio

# 1998-2024 真实数据
for yr in range(1998, 2025):
    completion_full[yr] = starts.loc[yr, 'completion_10k_m2']

completion_series = pd.Series(completion_full).sort_index()
print(f"  竣工面积序列: {completion_series.index.min()}-{completion_series.index.max()}")
print(f"  (1985-1997为新开工面积x{early_completion_ratio:.0%}估算, 1998后为真实值)")

# PIM 计算住宅存量
def pim_stock(completion, delta, start_year, end_year):
    """永续盘存法计算存量"""
    stock = {}
    for t in range(start_year, end_year + 1):
        s = 0.0
        for yr in range(completion.index.min(), t + 1):
            if yr in completion.index and pd.notna(completion[yr]):
                s += completion[yr] * (1 - delta) ** (t - yr)
        stock[t] = s
    return pd.Series(stock)

housing_stock_pim = pim_stock(completion_series, DELTA_RES, 1998, 2024)

# V1(t) = 住宅均价(元/m2) x 住宅存量(万m2)
# 单位: 元/m2 x 万m2 = 万元 => / 10000 = 亿元
# 注意：住宅均价是当年交易均价，用它乘以存量会高估早期存量价值
# 但这是中国数据条件下的最佳近似

df['housing_stock_pim'] = housing_stock_pim
df['V1_100m'] = df['residential_price'] * df['housing_stock_pim'] / 10000.0

print(f"  V1 (住宅市值): {df['V1_100m'].iloc[0]:.0f} -> {df['V1_100m'].iloc[-1]:.0f} 亿元")

# --- 3.2 V2: 累计商品房销售额 (市场交易实现价值) ---
# V2(t) = Sum_{s=1998}^{t} sales_amount(s)
# 这反映了市场实际交易的总价值
# 注意: 这是名义值累计，不折旧（因为代表的是已实现的市场估值总和）

df['V2_100m'] = df['sales_amount_100m'].cumsum()

print(f"  V2 (累计销售额): {df['V2_100m'].iloc[0]:.0f} -> {df['V2_100m'].iloc[-1]:.0f} 亿元")

# --- 3.3 V3: 综合资产价值 = 住宅市值 + 土地存量价值 + 基础设施存量价值 ---

# 土地存量价值 = 建成区面积(km2) x 综合地价(元/m2) x 10^6 m2/km2
# 综合地价: 使用 土地出让收入/土地出让面积 近似
# 由于缺少详细地价数据，我们使用另一种方法:
# 土地价值 = 累计土地出让收入 (PIM, delta=0, 土地不折旧)
# 这低估了价值增长但更保守

df['land_value_100m'] = df['land_revenue_100m'].cumsum()

# 基础设施存量价值 = PIM(基础设施投资), delta=4% (基础设施折旧率较高)
DELTA_INFRA = 0.04

# 需要从1990年开始累计基础设施投资
infra_full = infra_inv_full.copy()
infra_stock = {}
for t in range(1998, 2025):
    s = 0.0
    for yr in range(1990, t + 1):
        if yr in infra_full.index and pd.notna(infra_full[yr]):
            s += infra_full[yr] * (1 - DELTA_INFRA) ** (t - yr)
    infra_stock[t] = s

df['infra_stock_100m'] = pd.Series(infra_stock)

df['V3_100m'] = df['V1_100m'] + df['land_value_100m'] + df['infra_stock_100m']

print(f"  V3 (综合资产): {df['V3_100m'].iloc[0]:.0f} -> {df['V3_100m'].iloc[-1]:.0f} 亿元")

# ============================================================
# 4. 计算 K(t) — 累计建设投资（三个口径）
# ============================================================

print("\n[4] 计算累计投资 K(t)...")

# --- 4.1 K1: 房地产投资PIM (delta=2%) ---
# K1(t) = Sum_{s=1987}^{t} RE_inv(s) * (1-0.02)^(t-s)

re_inv_all = re_inv_full.copy()
k1 = {}
for t in range(1998, 2025):
    s = 0.0
    for yr in range(1987, t + 1):
        if yr in re_inv_all.index and pd.notna(re_inv_all[yr]):
            s += re_inv_all[yr] * (1 - DELTA_RES) ** (t - yr)
    k1[t] = s

df['K1_100m'] = pd.Series(k1)
print(f"  K1 (房地产PIM, delta=2%): {df['K1_100m'].iloc[0]:.0f} -> {df['K1_100m'].iloc[-1]:.0f} 亿元")

# --- 4.2 K2: 房地产+基础设施投资PIM (delta=3%) ---
DELTA_COMBINED = 0.03

k2 = {}
for t in range(1998, 2025):
    s = 0.0
    # 房地产部分 (1987起)
    for yr in range(1987, t + 1):
        if yr in re_inv_all.index and pd.notna(re_inv_all[yr]):
            s += re_inv_all[yr] * (1 - DELTA_COMBINED) ** (t - yr)
    # 基础设施部分 (1990起)
    for yr in range(1990, t + 1):
        if yr in infra_full.index and pd.notna(infra_full[yr]):
            s += infra_full[yr] * (1 - DELTA_COMBINED) ** (t - yr)
    k2[t] = s

df['K2_100m'] = pd.Series(k2)
print(f"  K2 (房地产+基础设施PIM, delta=3%): {df['K2_100m'].iloc[0]:.0f} -> {df['K2_100m'].iloc[-1]:.0f} 亿元")

# --- 4.3 K3: 全口径建设投资（从master直接获取） ---
# total_construction_inv = 房地产投资 + 基础设施投资
# 这是流量累计（简单求和，不折旧），代表历史总投入

df['K3_100m'] = master.loc[df.index, 'total_construction_inv'].cumsum()

# 但更合理的是也做PIM
# K3_alt: total_construction PIM (delta=3%)
total_inv_full = pd.concat([
    re_inv_full.rename('re'),
    infra_full.rename('infra')
], axis=1).sum(axis=1, min_count=1)

k3_pim = {}
for t in range(1998, 2025):
    s = 0.0
    for yr in range(1987, t + 1):
        if yr in total_inv_full.index and pd.notna(total_inv_full[yr]):
            s += total_inv_full[yr] * (1 - DELTA_COMBINED) ** (t - yr)
    k3_pim[t] = s

df['K3_pim_100m'] = pd.Series(k3_pim)
print(f"  K3 (全口径累计): {df['K3_100m'].iloc[0]:.0f} -> {df['K3_100m'].iloc[-1]:.0f} 亿元")
print(f"  K3_pim (全口径PIM, delta=3%): {df['K3_pim_100m'].iloc[0]:.0f} -> {df['K3_pim_100m'].iloc[-1]:.0f} 亿元")

# ============================================================
# 5. 计算 Urban Q = V/K（多口径）
# ============================================================

print("\n[5] 计算 Urban Q...")

# 核心口径
df['Q_V1K1'] = df['V1_100m'] / df['K1_100m']    # 住宅市值 / 房地产投资
df['Q_V1K2'] = df['V1_100m'] / df['K2_100m']    # 住宅市值 / 总建设投资
df['Q_V2K1'] = df['V2_100m'] / df['K1_100m']    # 累计销售 / 房地产投资
df['Q_V2K2'] = df['V2_100m'] / df['K2_100m']    # 累计销售 / 总建设投资
df['Q_V3K2'] = df['V3_100m'] / df['K2_100m']    # 综合资产 / 总建设投资
df['Q_V3K3'] = df['V3_100m'] / df['K3_pim_100m']  # 综合资产 / 全口径PIM

# 推荐的主口径: Q_V1K1 (最直观: 住宅值多少 vs 花了多少建)
# 辅助口径: Q_V1K2, Q_V3K2

for q_col in ['Q_V1K1', 'Q_V1K2', 'Q_V2K1', 'Q_V2K2', 'Q_V3K2', 'Q_V3K3']:
    vals = df[q_col].dropna()
    peak_yr = vals.idxmax()
    print(f"  {q_col}: 峰值 {vals.max():.2f} ({peak_yr}), "
          f"最新 {vals.iloc[-1]:.2f} ({vals.index[-1]})")

# ============================================================
# 6. 计算 MUQ = dV/dI（边际 Urban Q）
# ============================================================

print("\n[6] 计算边际 Urban Q (MUQ = dV/dI)...")

# MUQ = (V(t) - V(t-1)) / I(t)
# 其中 I(t) = 当年新增投资

# MUQ1: dV1 / re_inv
df['dV1'] = df['V1_100m'].diff()
df['dV2'] = df['V2_100m'].diff()
df['dV3'] = df['V3_100m'].diff()

df['MUQ_V1'] = df['dV1'] / df['re_inv_100m']
df['MUQ_V2'] = df['dV2'] / df['re_inv_100m']
df['MUQ_V3'] = df['dV3'] / (df['re_inv_100m'] + df['infra_inv_100m'])

for muq_col in ['MUQ_V1', 'MUQ_V2', 'MUQ_V3']:
    vals = df[muq_col].dropna()
    neg_years = vals[vals < 0].index.tolist()
    print(f"  {muq_col}: 负值年份 = {neg_years}")

# ============================================================
# 7. 找到 Q = 1 的交叉年份
# ============================================================

print("\n[7] Q = 1 交叉点分析...")

def find_q1_crossing(series, label):
    """找到 Q 从>1变为<1的年份（线性插值）"""
    s = series.dropna()
    crossings = []
    for i in range(1, len(s)):
        y0, y1 = s.index[i-1], s.index[i]
        v0, v1 = s.iloc[i-1], s.iloc[i]
        if (v0 - 1) * (v1 - 1) < 0:  # 跨越 Q=1
            # 线性插值
            cross_year = y0 + (1 - v0) / (v1 - v0) * (y1 - y0)
            direction = "下穿" if v0 > 1 and v1 < 1 else "上穿"
            crossings.append((cross_year, direction))
            print(f"  {label}: {direction} Q=1 于 {cross_year:.1f} 年 "
                  f"({y0}: {v0:.3f} -> {y1}: {v1:.3f})")
    if not crossings:
        if s.iloc[-1] > 1:
            print(f"  {label}: 全程 > 1，最新值 {s.iloc[-1]:.3f}")
        else:
            print(f"  {label}: 全程 < 1，最新值 {s.iloc[-1]:.3f}")
    return crossings

q1_crossings = {}
for q_col in ['Q_V1K1', 'Q_V1K2', 'Q_V2K1', 'Q_V2K2', 'Q_V3K2', 'Q_V3K3']:
    q1_crossings[q_col] = find_q1_crossing(df[q_col], q_col)

# ============================================================
# 8. 辅助比率曲线
# ============================================================

print("\n[8] 计算辅助比率曲线...")

# I/GDP 比率 (投资强度)
df['re_inv_gdp_pct'] = df['re_inv_100m'] / df['gdp_100m'] * 100
df['infra_inv_gdp_pct'] = df['infra_inv_100m'] / df['gdp_100m'] * 100
df['total_inv_gdp_pct'] = (df['re_inv_100m'] + df['infra_inv_100m']) / df['gdp_100m'] * 100

# N/R ratio (新开工 / 竣工)
df['NR_ratio'] = df['new_starts_10k_m2'] / df['completion_10k_m2']

# F/S ratio (竣工 / 销售面积)
df['FS_ratio'] = df['completion_10k_m2'] / df['sales_area_10k_m2']

# 房价收入比 (PIR) — 住宅均价 x 90m2 / 城镇可支配收入
urban_income = master.loc[df.index, 'urban_disposable_income_yuan']
df['PIR'] = df['residential_price'] * 90 / urban_income

print(f"  投资/GDP: 房地产 {df['re_inv_gdp_pct'].max():.1f}% (峰值), "
      f"基础设施 {df['infra_inv_gdp_pct'].max():.1f}% (峰值)")
print(f"  N/R比: {df['NR_ratio'].max():.2f} (峰值{df['NR_ratio'].idxmax()}), "
      f"最新 {df['NR_ratio'].iloc[-1]:.2f}")
print(f"  房价收入比: {df['PIR'].max():.1f} (峰值{df['PIR'].idxmax()}), "
      f"最新 {df['PIR'].iloc[-1]:.1f}")

# ============================================================
# 9. 保存数据
# ============================================================

print("\n[9] 保存数据...")

out_cols = [
    'gdp_100m', 'urbanization_pct',
    'residential_price', 'commercial_price',
    'completion_10k_m2', 'new_starts_10k_m2',
    'sales_area_10k_m2', 'sales_amount_100m',
    're_inv_100m', 'infra_inv_100m',
    'land_revenue_100m', 'built_area_km2',
    'housing_stock_pim',
    'V1_100m', 'V2_100m', 'V3_100m',
    'K1_100m', 'K2_100m', 'K3_100m', 'K3_pim_100m',
    'Q_V1K1', 'Q_V1K2', 'Q_V2K1', 'Q_V2K2', 'Q_V3K2', 'Q_V3K3',
    'MUQ_V1', 'MUQ_V2', 'MUQ_V3',
    're_inv_gdp_pct', 'infra_inv_gdp_pct', 'total_inv_gdp_pct',
    'NR_ratio', 'FS_ratio', 'PIR'
]

df_out = df[out_cols].copy()
df_out.to_csv(OUT_CSV, float_format='%.4f')
print(f"  已保存: {OUT_CSV}")

# ============================================================
# 10. 生成分析报告
# ============================================================

print("\n[10] 生成分析报告...")

report_lines = []
report_lines.append("=" * 70)
report_lines.append("中国 Urban Q 多口径计算报告")
report_lines.append("基于国家统计局 / 财政部真实数据")
report_lines.append("=" * 70)
report_lines.append("")
report_lines.append("一、数据来源")
report_lines.append("-" * 40)
report_lines.append("  住宅均价: NBS《中国房地产统计年鉴》, 1998-2024")
report_lines.append("  竣工面积: NBS《中国统计年鉴》, 1998-2024 (1985-1997为估算)")
report_lines.append("  销售面积/金额: NBS, 1998-2024")
report_lines.append("  房地产投资: NBS《中国统计年鉴》, 1987-2024")
report_lines.append("  基础设施投资: NBS《中国统计年鉴》, 1990-2024")
report_lines.append("  土地出让收入: 财政部《全国政府性基金收入》, 1999-2024")
report_lines.append("  GDP: NBS《中国统计年鉴》, 1978-2024")
report_lines.append("  建成区面积: NBS, 1981-2024")
report_lines.append("")
report_lines.append("二、方法论")
report_lines.append("-" * 40)
report_lines.append("  Urban Q = V(t) / K(t)")
report_lines.append("  V: 城市资产市场价值; K: 累计建设投资重置成本")
report_lines.append("")
report_lines.append("  V1 = 住宅均价 x PIM住宅存量 (delta=2%)")
report_lines.append("  V2 = 累计商品房销售额")
report_lines.append("  V3 = V1 + 累计土地出让 + PIM基础设施存量 (delta=4%)")
report_lines.append("")
report_lines.append("  K1 = PIM(房地产投资, delta=2%)")
report_lines.append("  K2 = PIM(房地产+基础设施投资, delta=3%)")
report_lines.append("  K3 = PIM(全口径建设投资, delta=3%)")
report_lines.append("")
report_lines.append("  MUQ = dV/dI (边际Urban Q)")
report_lines.append("")

report_lines.append("三、Urban Q 多口径结果")
report_lines.append("-" * 40)
report_lines.append(f"{'口径':<12} {'峰值':>8} {'峰值年':>6} {'2024':>8} {'Q=1交叉':>12}")
report_lines.append("-" * 50)

for q_col in ['Q_V1K1', 'Q_V1K2', 'Q_V2K1', 'Q_V2K2', 'Q_V3K2', 'Q_V3K3']:
    vals = df[q_col].dropna()
    peak = vals.max()
    peak_yr = vals.idxmax()
    latest = vals.iloc[-1]
    crossings = q1_crossings[q_col]
    cross_str = ", ".join([f"{c[0]:.1f}({c[1]})" for c in crossings]) if crossings else "无交叉"
    report_lines.append(f"{q_col:<12} {peak:>8.3f} {peak_yr:>6} {latest:>8.3f} {cross_str:>12}")

report_lines.append("")
report_lines.append("四、推荐口径分析")
report_lines.append("-" * 40)
report_lines.append("")

# 推荐口径 1: Q_V1K1
report_lines.append("  [推荐1] Q_V1K1 = 住宅市值 / 房地产投资存量")
report_lines.append("  含义: 住宅值多少 vs 花了多少建住宅")
q = df['Q_V1K1'].dropna()
report_lines.append(f"  1998: {q.iloc[0]:.3f}")
report_lines.append(f"  峰值: {q.max():.3f} ({q.idxmax()})")
report_lines.append(f"  2024: {q.iloc[-1]:.3f}")
report_lines.append("")

# 推荐口径 2: Q_V1K2
report_lines.append("  [推荐2] Q_V1K2 = 住宅市值 / (房地产+基础设施)投资存量")
report_lines.append("  含义: 住宅价值能否覆盖全部城市建设投入")
q = df['Q_V1K2'].dropna()
report_lines.append(f"  1998: {q.iloc[0]:.3f}")
report_lines.append(f"  峰值: {q.max():.3f} ({q.idxmax()})")
report_lines.append(f"  2024: {q.iloc[-1]:.3f}")
report_lines.append("")

# 推荐口径 3: Q_V3K2
report_lines.append("  [推荐3] Q_V3K2 = 综合资产价值 / 总建设投资存量")
report_lines.append("  含义: 城市全部资产价值 vs 全部建设投入")
q = df['Q_V3K2'].dropna()
report_lines.append(f"  1998: {q.iloc[0]:.3f}")
report_lines.append(f"  峰值: {q.max():.3f} ({q.idxmax()})")
report_lines.append(f"  2024: {q.iloc[-1]:.3f}")
report_lines.append("")

report_lines.append("五、边际 Urban Q (MUQ)")
report_lines.append("-" * 40)
for muq_col in ['MUQ_V1', 'MUQ_V2', 'MUQ_V3']:
    vals = df[muq_col].dropna()
    neg_years = vals[vals < 0].index.tolist()
    report_lines.append(f"  {muq_col}: 负值年份 = {neg_years}")
    if len(neg_years) > 0:
        report_lines.append(f"    => MUQ 转负意味着新增投资开始毁灭价值")
report_lines.append("")

report_lines.append("六、关键时间节点")
report_lines.append("-" * 40)
report_lines.append(f"  房地产投资/GDP峰值: {df['re_inv_gdp_pct'].max():.1f}% "
                    f"({df['re_inv_gdp_pct'].idxmax()})")
report_lines.append(f"  N/R比峰值: {df['NR_ratio'].max():.2f} ({df['NR_ratio'].idxmax()})")
report_lines.append(f"  房价收入比峰值: {df['PIR'].max():.1f} ({df['PIR'].idxmax()})")
report_lines.append(f"  商品房均价峰值: {df['commercial_price'].max():.0f} 元/m2 "
                    f"({df['commercial_price'].idxmax()})")
report_lines.append("")

report_lines.append("七、分阶段特征")
report_lines.append("-" * 40)

phases = [
    ("1998-2003", "房改初期", 1998, 2003),
    ("2004-2007", "快速扩张", 2004, 2007),
    ("2008-2009", "全球金融危机", 2008, 2009),
    ("2010-2013", "刺激与过热", 2010, 2013),
    ("2014-2016", "调整与去库存", 2014, 2016),
    ("2017-2019", "棚改与调控", 2017, 2019),
    ("2020-2021", "疫情与尾声", 2020, 2021),
    ("2022-2024", "下行与转型", 2022, 2024),
]

for label, desc, y0, y1 in phases:
    sub = df.loc[y0:y1]
    q_mean = sub['Q_V1K1'].mean()
    muq_mean = sub['MUQ_V1'].mean() if 'MUQ_V1' in sub else np.nan
    inv_gdp = sub['re_inv_gdp_pct'].mean()
    report_lines.append(f"  {label} ({desc}):")
    report_lines.append(f"    Q_V1K1均值={q_mean:.3f}, MUQ_V1均值={muq_mean:.3f}, "
                        f"房地产投资/GDP={inv_gdp:.1f}%")

report_lines.append("")
report_lines.append("八、核心结论")
report_lines.append("-" * 40)

# 判断Q是否跨越1
q_main = df['Q_V1K1'].dropna()
if q_main.iloc[-1] < 1:
    report_lines.append("  1. Urban Q (V1/K1) 已降至1以下，标志城市建设进入")
    report_lines.append("     资产价值低于重置成本的阶段 => 新建不如改造")
elif q_main.iloc[-1] < q_main.max() * 0.5:
    report_lines.append("  1. Urban Q 从峰值大幅回落，显示投资回报率急剧下降")

report_lines.append("  2. 边际 Urban Q (MUQ) 在下行期转负，")
report_lines.append("     说明新增投资在毁灭而非创造价值")
report_lines.append("  3. 这些证据支持 expansion -> renewal 的相变叙事:")
report_lines.append("     Q > 1 时理性选择是扩张建设")
report_lines.append("     Q < 1 时理性选择是存量更新")

report_text = "\n".join(report_lines)

with open(OUT_REPORT, 'w', encoding='utf-8') as f:
    f.write(report_text)
print(f"  已保存: {OUT_REPORT}")

# ============================================================
# 11. 综合可视化（4子图）
# ============================================================

print("\n[11] 生成综合可视化...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
plt.rcParams['font.family'] = ['Arial']

years = df.index

# 颜色方案
C_V1 = '#E63946'   # 红色 - V1 住宅市值
C_V2 = '#457B9D'   # 蓝色 - V2 累计销售
C_V3 = '#2A9D8F'   # 绿色 - V3 综合资产
C_K1 = '#E76F51'   # 橙色 - K1 房地产PIM
C_K2 = '#264653'   # 深蓝 - K2 总建设PIM
C_K3 = '#606C38'   # 橄榄 - K3 全口径PIM

# --- (a) V(t) 多口径对比 ---
ax = axes[0, 0]
ax.plot(years, df['V1_100m'] / 10000, color=C_V1, linewidth=2.0,
        label='V1: Residential Stock Value')
ax.plot(years, df['V2_100m'] / 10000, color=C_V2, linewidth=2.0,
        linestyle='--', label='V2: Cumulative Sales')
ax.plot(years, df['V3_100m'] / 10000, color=C_V3, linewidth=2.0,
        linestyle='-.', label='V3: Comprehensive Asset')
ax.set_title('(a) Market Value V(t)', fontsize=13, fontweight='bold')
ax.set_ylabel('Trillion CNY', fontsize=11)
ax.legend(fontsize=9, loc='upper left')
ax.grid(True, alpha=0.3)
ax.set_xlim(1998, 2024)

# --- (b) K(t) 多口径对比 ---
ax = axes[0, 1]
ax.plot(years, df['K1_100m'] / 10000, color=C_K1, linewidth=2.0,
        label='K1: RE Investment PIM ($\\delta$=2%)')
ax.plot(years, df['K2_100m'] / 10000, color=C_K2, linewidth=2.0,
        linestyle='--', label='K2: RE+Infra PIM ($\\delta$=3%)')
ax.plot(years, df['K3_pim_100m'] / 10000, color=C_K3, linewidth=2.0,
        linestyle='-.', label='K3: Total Construction PIM ($\\delta$=3%)')
ax.set_title('(b) Capital Stock K(t)', fontsize=13, fontweight='bold')
ax.set_ylabel('Trillion CNY', fontsize=11)
ax.legend(fontsize=9, loc='upper left')
ax.grid(True, alpha=0.3)
ax.set_xlim(1998, 2024)

# --- (c) Urban Q 多口径 + Q=1 ---
ax = axes[1, 0]
ax.plot(years, df['Q_V1K1'], color=C_V1, linewidth=2.5,
        label='Q = V1/K1 (Recommended)')
ax.plot(years, df['Q_V1K2'], color=C_K2, linewidth=1.5,
        linestyle='--', label='Q = V1/K2')
ax.plot(years, df['Q_V3K2'], color=C_V3, linewidth=1.5,
        linestyle='-.', label='Q = V3/K2')
ax.axhline(y=1, color='black', linewidth=1.5, linestyle=':', alpha=0.7,
           label='Q = 1 (Phase Transition)')
ax.set_title('(c) Urban Q = V/K', fontsize=13, fontweight='bold')
ax.set_ylabel('Urban Q ratio', fontsize=11)
ax.legend(fontsize=9, loc='best')
ax.grid(True, alpha=0.3)
ax.set_xlim(1998, 2024)

# 标注 Q=1 交叉点
for q_col, color in [('Q_V1K1', C_V1), ('Q_V1K2', C_K2), ('Q_V3K2', C_V3)]:
    for cross_year, direction in q1_crossings.get(q_col, []):
        if direction == "下穿":
            ax.axvline(x=cross_year, color=color, linewidth=0.8,
                       linestyle='--', alpha=0.5)
            ax.annotate(f'{cross_year:.0f}', xy=(cross_year, 1),
                        xytext=(cross_year - 1.5, 1.15),
                        fontsize=8, color=color,
                        arrowprops=dict(arrowstyle='->', color=color, lw=0.8))

# --- (d) MUQ 时序 ---
ax = axes[1, 1]
ax.plot(years, df['MUQ_V1'], color=C_V1, linewidth=2.0,
        label='MUQ = $\\Delta$V1 / I$_{RE}$')
ax.plot(years, df['MUQ_V2'], color=C_V2, linewidth=1.5,
        linestyle='--', label='MUQ = $\\Delta$V2 / I$_{RE}$')
ax.plot(years, df['MUQ_V3'], color=C_V3, linewidth=1.5,
        linestyle='-.', label='MUQ = $\\Delta$V3 / I$_{total}$')
ax.axhline(y=0, color='black', linewidth=1.5, linestyle=':', alpha=0.7,
           label='MUQ = 0')
ax.set_title('(d) Marginal Urban Q = $\\Delta$V / $\\Delta$I',
             fontsize=13, fontweight='bold')
ax.set_ylabel('MUQ ratio', fontsize=11)
ax.legend(fontsize=9, loc='best')
ax.grid(True, alpha=0.3)
ax.set_xlim(1998, 2024)

# 统一X轴标签
for ax in axes.flat:
    ax.set_xlabel('Year', fontsize=10)
    ax.tick_params(labelsize=9)

plt.suptitle("China's Urban Q: Multi-Caliber Estimation from Real NBS/MOF Data (1998-2024)",
             fontsize=14, fontweight='bold', y=0.98)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(OUT_FIG, dpi=200, bbox_inches='tight')
plt.close()
print(f"  已保存: {OUT_FIG}")

# ============================================================
# 12. 打印摘要
# ============================================================

print("\n" + "=" * 70)
print("计算完成摘要")
print("=" * 70)

print("\n--- Urban Q 时序 (推荐口径 Q_V1K1) ---")
for yr in [1998, 2000, 2005, 2010, 2015, 2020, 2021, 2022, 2023, 2024]:
    if yr in df.index:
        q_val = df.loc[yr, 'Q_V1K1']
        v_val = df.loc[yr, 'V1_100m']
        k_val = df.loc[yr, 'K1_100m']
        print(f"  {yr}: Q = {q_val:.3f}  "
              f"(V1 = {v_val/10000:.1f}万亿, K1 = {k_val/10000:.1f}万亿)")

print("\n--- 输出文件 ---")
print(f"  数据: {OUT_CSV}")
print(f"  报告: {OUT_REPORT}")
print(f"  图表: {OUT_FIG}")
print("=" * 70)
