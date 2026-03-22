#!/usr/bin/env python3
"""
15_extract_country_data.py -- 从 World Bank / PWT / BIS / UN 真实数据中提取四国面板

目的:
    从已有的 A 类权威数据源中自动提取日本、美国、英国、中国的核心宏观变量，
    生成统一面板数据集，用于替代 03/04/05 脚本中的硬编码数据。

输入数据:
    - 02-data/raw/world_bank_all_countries.csv  (World Bank, 217国, 1960-2023)
    - 02-data/raw/penn_world_table.csv           (PWT 10.01, 183国, 1950-2019)
    - 02-data/raw/bis_property_prices.csv        (BIS 房价指数, 48国)
    - 02-data/raw/un_population.csv              (UN 人口数据, 218国)

输出:
    - 02-data/processed/four_country_wb_pwt_panel.csv  -- 四国统一面板

依赖包:
    pandas, numpy

Author: data-analyst
Date: 2026-03-21
"""

import pandas as pd
import numpy as np
import os
import sys

# ============================================================
# 0. 路径设置
# ============================================================
PROJECT_ROOT = "/Users/andy/Desktop/Claude/urban-q-phase-transition"
RAW_DIR = os.path.join(PROJECT_ROOT, "02-data/raw")
OUT_DIR = os.path.join(PROJECT_ROOT, "02-data/processed")
os.makedirs(OUT_DIR, exist_ok=True)

OUTPUT_PATH = os.path.join(OUT_DIR, "four_country_wb_pwt_panel.csv")

# 目标国家
COUNTRIES = ["JPN", "USA", "GBR", "CHN"]
COUNTRY_NAMES = {"JPN": "Japan", "USA": "United States", "GBR": "United Kingdom", "CHN": "China"}

print("=" * 70)
print("四国数据提取: World Bank + PWT + BIS + UN -> 统一面板")
print("=" * 70)

# ============================================================
# 1. 读取 World Bank 数据
# ============================================================
print("\n[1/4] 读取 World Bank 数据...")

wb_path = os.path.join(RAW_DIR, "world_bank_all_countries.csv")
wb = pd.read_csv(wb_path)

# 筛选目标国家
wb = wb[wb["country_iso3"].isin(COUNTRIES)].copy()
wb["year"] = wb["year"].astype(int)

# 重命名列 -> 可读变量名
# World Bank 指标代码对照:
#   NY.GDP.MKTP.CD     = GDP (current US$)
#   NY.GDP.MKTP.KD     = GDP (constant 2015 US$)
#   NE.GDI.FTOT.ZS     = GFCF (% of GDP)
#   NE.GDI.FTOT.CD     = GFCF (current US$)
#   NE.CON.GOVT.ZS     = Government consumption (% of GDP)
#   NV.SRV.TOTL.ZS     = Services, value added (% of GDP) -- 三产占比
#   NV.IND.TOTL.ZS     = Industry, value added (% of GDP) -- 二产占比
#   NV.AGR.TOTL.ZS     = Agriculture, value added (% of GDP) -- 一产占比
#   SP.URB.TOTL.IN.ZS  = Urban population (% of total) -- 城镇化率
#   SP.URB.TOTL         = Urban population (absolute)
#   SP.POP.TOTL         = Population, total
#   SP.POP.1564.TO.ZS  = Population ages 15-64 (% of total) -- 劳动年龄人口占比
#   SP.POP.65UP.TO.ZS  = Population ages 65+ (% of total) -- 老龄化率

wb_rename = {
    "country_iso3": "iso3",
    "country_name": "country_name",
    "year": "year",
    "NY.GDP.MKTP.CD": "wb_gdp_current_usd",          # 可替代硬编码 GDP（美元口径）
    "NY.GDP.MKTP.KD": "wb_gdp_constant_usd",          # 实际 GDP（2015 美元）
    "NE.GDI.FTOT.ZS": "wb_gfcf_pct_gdp",              # GFCF/GDP 比率
    "NE.GDI.FTOT.CD": "wb_gfcf_current_usd",           # GFCF 绝对额（美元）
    "NE.CON.GOVT.ZS": "wb_gov_consumption_pct_gdp",    # 政府消费占比
    "NV.SRV.TOTL.ZS": "wb_services_pct_gdp",           # 三产占比（可替代硬编码）
    "NV.IND.TOTL.ZS": "wb_industry_pct_gdp",           # 二产占比
    "NV.AGR.TOTL.ZS": "wb_agriculture_pct_gdp",        # 一产占比
    "SP.URB.TOTL.IN.ZS": "wb_urban_pct",               # 城镇化率（可替代硬编码）
    "SP.URB.TOTL": "wb_urban_pop",                      # 城镇人口
    "SP.POP.TOTL": "wb_total_pop",                      # 总人口（可替代硬编码）
    "SP.POP.1564.TO.ZS": "wb_working_age_pct",          # 劳动年龄人口占比
    "SP.POP.65UP.TO.ZS": "wb_pop_65plus_pct",           # 老龄化率
}

wb = wb.rename(columns=wb_rename)
wb_cols = [c for c in wb_rename.values() if c in wb.columns]
# 去掉多余列
wb = wb[wb_cols].copy()

print(f"  World Bank: {len(wb)} 行, {wb['year'].min()}-{wb['year'].max()}")
for iso in COUNTRIES:
    n = wb[wb["iso3"] == iso].shape[0]
    print(f"    {iso} ({COUNTRY_NAMES[iso]}): {n} 年")

# ============================================================
# 2. 读取 Penn World Table 数据
# ============================================================
print("\n[2/4] 读取 Penn World Table 10.01 数据...")

pwt_path = os.path.join(RAW_DIR, "penn_world_table.csv")
# PWT 文件有 BOM (UTF-8-BOM)
pwt = pd.read_csv(pwt_path, encoding="utf-8-sig")

# PWT 列名首列可能有 BOM 残留，确保清理
pwt.columns = [c.strip().replace("\ufeff", "") for c in pwt.columns]

pwt = pwt[pwt["countrycode"].isin(COUNTRIES)].copy()
pwt["year"] = pwt["year"].astype(int)

# PWT 核心变量说明:
#   hc      = Human capital index (based on years of schooling + returns)
#   rnna    = Capital stock at constant 2017 national prices (mil. 2017 LCU)
#   rkna    = Capital services at constant 2017 national prices
#   rgdpna  = Real GDP at constant 2017 national prices (mil. 2017 LCU)
#   pop     = Population (millions)
#   emp     = Persons engaged (millions)
#   csh_i   = Share of GFCF at current PPPs
#   delta   = Average depreciation rate of capital stock
#   labsh   = Share of labour compensation in GDP at current national prices
#   irr     = Real internal rate of return
#   ctfp    = TFP level at current PPPs (USA=1)
#   rtfpna  = TFP at constant national prices (2017=1)

pwt_rename = {
    "countrycode": "iso3",
    "year": "year",
    "hc": "pwt_hc",                  # 人力资本指数
    "rnna": "pwt_capital_stock",      # 实际资本存量（百万本币 2017 价）
    "rkna": "pwt_capital_services",   # 资本服务
    "rgdpna": "pwt_real_gdp",         # 实际 GDP（百万本币 2017 价）
    "pop": "pwt_pop_mil",             # 人口（百万）
    "emp": "pwt_employment_mil",      # 就业人口（百万）
    "csh_i": "pwt_investment_share",  # 投资/GDP 占比（PPP）
    "delta": "pwt_depreciation_rate", # 资本折旧率
    "labsh": "pwt_labor_share",       # 劳动报酬占 GDP 比
    "irr": "pwt_real_return_rate",    # 实际资本回报率
    "ctfp": "pwt_tfp_level",          # TFP 水平（美国=1）
    "rtfpna": "pwt_tfp_national",     # TFP（国内 2017=1）
}

pwt = pwt.rename(columns=pwt_rename)
pwt_cols = [c for c in pwt_rename.values() if c in pwt.columns]
pwt = pwt[pwt_cols].copy()

print(f"  PWT: {len(pwt)} 行, {pwt['year'].min()}-{pwt['year'].max()}")
for iso in COUNTRIES:
    sub = pwt[(pwt["iso3"] == iso) & (pwt["pwt_hc"].notna())]
    print(f"    {iso}: hc 有效 {sub['year'].min()}-{sub['year'].max()} ({len(sub)} 年)")

# ============================================================
# 3. 读取 BIS 房价指数
# ============================================================
print("\n[3/4] 读取 BIS 房价指数...")

bis_path = os.path.join(RAW_DIR, "bis_property_prices.csv")
bis = pd.read_csv(bis_path)

# BIS 年度数据中 HPI/RHP 仅有基期值 (2015=100)，实际时序在季度数据中。
# 策略: 对季度 HPI/RHP 取年均值聚合为年度; 同时提取年度 HPI_YDH (price-to-income)。
bis_target = bis[bis["country_code"].isin(COUNTRIES)].copy()

# --- 季度 HPI/RHP -> 年度均值 ---
bis_q = bis_target[
    (bis_target["frequency"] == "Q") &
    (bis_target["measure"].isin(["HPI", "RHP"]))
].copy()
# 从 "2010-Q4" 中提取年份
bis_q["year"] = bis_q["period"].str[:4].astype(int)
bis_q["value"] = pd.to_numeric(bis_q["value"], errors="coerce")

# 按国家-年-指标取年均值
bis_q_annual = bis_q.groupby(["country_code", "year", "measure"])["value"].mean().reset_index()

bis_hpi = bis_q_annual[bis_q_annual["measure"] == "HPI"][["country_code", "year", "value"]].rename(
    columns={"country_code": "iso3", "value": "bis_hpi_nominal"}
)
bis_rhp = bis_q_annual[bis_q_annual["measure"] == "RHP"][["country_code", "year", "value"]].rename(
    columns={"country_code": "iso3", "value": "bis_hpi_real"}
)

# --- 年度 HPI_YDH (price-to-income ratio) ---
bis_a_ydi = bis_target[
    (bis_target["frequency"] == "A") &
    (bis_target["measure"] == "HPI_YDH")
].copy()
bis_a_ydi["year"] = bis_a_ydi["period"].astype(int)
bis_a_ydi["value"] = pd.to_numeric(bis_a_ydi["value"], errors="coerce")
bis_ydi = bis_a_ydi[["country_code", "year", "value"]].rename(
    columns={"country_code": "iso3", "value": "bis_price_to_income"}
)

# --- 年度 HPI_RPI (price-to-rent ratio) ---
bis_a_rpi = bis_target[
    (bis_target["frequency"] == "A") &
    (bis_target["measure"] == "HPI_RPI")
].copy()
bis_a_rpi["year"] = bis_a_rpi["period"].astype(int)
bis_a_rpi["value"] = pd.to_numeric(bis_a_rpi["value"], errors="coerce")
bis_rpi = bis_a_rpi[["country_code", "year", "value"]].rename(
    columns={"country_code": "iso3", "value": "bis_price_to_rent"}
)

# 合并 BIS 四列
bis_wide = pd.merge(bis_hpi, bis_rhp, on=["iso3", "year"], how="outer")
bis_wide = pd.merge(bis_wide, bis_ydi, on=["iso3", "year"], how="outer")
bis_wide = pd.merge(bis_wide, bis_rpi, on=["iso3", "year"], how="outer")

print(f"  BIS: {len(bis_wide)} 行")
for iso in COUNTRIES:
    sub = bis_wide[bis_wide["iso3"] == iso]
    if len(sub) > 0:
        print(f"    {iso}: {sub['year'].min()}-{sub['year'].max()} ({len(sub)} 年)")
    else:
        print(f"    {iso}: 无数据")

# ============================================================
# 4. 读取 UN 人口数据
# ============================================================
print("\n[4/4] 读取 UN 人口数据...")

un_path = os.path.join(RAW_DIR, "un_population.csv")
un = pd.read_csv(un_path)

un = un[un["iso3"].isin(COUNTRIES)].copy()
un["year"] = un["year"].astype(int)

un_rename = {
    "iso3": "iso3",
    "year": "year",
    "crude_birth_rate": "un_birth_rate",
    "crude_death_rate": "un_death_rate",
    "dependency_ratio": "un_dependency_ratio",
    "life_expectancy": "un_life_expectancy",
    "old_dependency_ratio": "un_old_dependency_ratio",
    "pop_0_14_pct": "un_pop_0_14_pct",
    "pop_15_64_pct": "un_pop_15_64_pct",        # 劳动年龄人口占比
    "pop_65plus_pct": "un_pop_65plus_pct",       # 老龄化率
    "pop_growth_rate": "un_pop_growth_rate",
    "tfr": "un_tfr",                             # 总和生育率
    "total_population": "un_total_pop",
    "urban_pop_pct": "un_urban_pct",
    "working_age_pct": "un_working_age_pct",
    "aging_rate": "un_aging_rate",
}

un = un.rename(columns=un_rename)
un_cols = [c for c in un_rename.values() if c in un.columns]
un = un[un_cols].copy()

print(f"  UN: {len(un)} 行, {un['year'].min()}-{un['year'].max()}")

# ============================================================
# 5. 合并四源数据
# ============================================================
print("\n[5/6] 合并四源数据为统一面板...")

# 以 World Bank 为主表，逐步 left join
panel = wb.copy()
panel = pd.merge(panel, pwt, on=["iso3", "year"], how="outer")
panel = pd.merge(panel, bis_wide, on=["iso3", "year"], how="outer")
panel = pd.merge(panel, un, on=["iso3", "year"], how="outer")

# 排序
panel = panel.sort_values(["iso3", "year"]).reset_index(drop=True)

# 添加国家名称（补全 outer join 带来的空值）
panel["country_name"] = panel["iso3"].map(COUNTRY_NAMES)

# 调整列顺序: iso3, country_name, year 在前
id_cols = ["iso3", "country_name", "year"]
other_cols = [c for c in panel.columns if c not in id_cols]
panel = panel[id_cols + sorted(other_cols)]

print(f"  合并后: {len(panel)} 行, {panel['year'].min()}-{panel['year'].max()}")
print(f"  国家: {panel['iso3'].unique().tolist()}")
print(f"  变量数: {len(panel.columns)}")

# ============================================================
# 6. 变量覆盖率统计
# ============================================================
print("\n[6/6] 变量覆盖率统计...")
print("-" * 70)

# 按国家打印覆盖率
for iso in COUNTRIES:
    sub = panel[panel["iso3"] == iso]
    yr_range = f"{sub['year'].min()}-{sub['year'].max()}"
    n_years = len(sub)
    print(f"\n  {iso} ({COUNTRY_NAMES[iso]}), {yr_range}, {n_years} 年:")
    print(f"  {'变量':<35} {'有效数':>5} {'覆盖率':>8} {'起止年份':<15}")
    print(f"  {'-'*65}")

    for col in sorted(other_cols):
        valid = sub[col].notna().sum()
        pct = valid / n_years * 100 if n_years > 0 else 0
        if valid > 0:
            valid_years = sub.loc[sub[col].notna(), "year"]
            yr_str = f"{valid_years.min()}-{valid_years.max()}"
        else:
            yr_str = "N/A"
        # 只打印有部分数据的变量
        if valid > 0:
            print(f"  {col:<35} {valid:>5} {pct:>7.1f}% {yr_str:<15}")

# ============================================================
# 7. 输出
# ============================================================
panel.to_csv(OUTPUT_PATH, index=False, float_format="%.6g")
print(f"\n{'=' * 70}")
print(f"面板数据已保存: {OUTPUT_PATH}")
print(f"总计 {len(panel)} 行 x {len(panel.columns)} 列")

# ============================================================
# 8. 替代映射说明: 哪些硬编码可以被替代
# ============================================================
print(f"\n{'=' * 70}")
print("硬编码替代映射 (03/04/05 脚本)")
print("=" * 70)

mapping = """
可直接替代的变量 (本面板已包含):
  -----------------------------------------------------------------------
  硬编码变量               -> 面板列名                  数据源
  -----------------------------------------------------------------------
  urbanization_data        -> wb_urban_pct              World Bank SP.URB.TOTL.IN.ZS
  tertiary_share_data      -> wb_services_pct_gdp       World Bank NV.SRV.TOTL.ZS
  gdp_data (USD)           -> wb_gdp_current_usd        World Bank NY.GDP.MKTP.CD
  population_data          -> wb_total_pop / pwt_pop_mil World Bank / PWT
  hpi_data (房价指数)      -> bis_hpi_nominal           BIS 名义房价指数 (2010=100)
                           -> bis_hpi_real              BIS 实际房价指数 (2010=100)
  GFCF/GDP 比率            -> wb_gfcf_pct_gdp           World Bank NE.GDI.FTOT.ZS
  GFCF 绝对额 (USD)       -> wb_gfcf_current_usd       World Bank NE.GDI.FTOT.CD
  人力资本指数             -> pwt_hc                    PWT hc (schooling-based)
  资本存量                 -> pwt_capital_stock          PWT rnna (2017 national prices)
  劳动年龄人口占比         -> wb_working_age_pct         World Bank SP.POP.1564.TO.ZS
                           -> un_working_age_pct        UN 人口数据
  老龄化率                 -> wb_pop_65plus_pct          World Bank SP.POP.65UP.TO.ZS
                           -> un_pop_65plus_pct         UN 人口数据
  资本折旧率               -> pwt_depreciation_rate     PWT delta
  TFP                      -> pwt_tfp_level / pwt_tfp_national  PWT
  投资占比 (PPP)           -> pwt_investment_share      PWT csh_i

仍需从各国统计局获取的变量 (本面板无法覆盖):
  -----------------------------------------------------------------------
  变量                     所需来源                    涉及脚本
  -----------------------------------------------------------------------
  gdp_data (本币名义)      日本内阁府SNA / BEA / ONS   03/04/05 (Urban Q 计算需本币)
  construction_investment   MLIT建设统计 / BEA / ONS    03/04/05 (建设投资细分)
  housing_starts_data      MLIT着工统计 / Census        03 (住宅开工数)
  land_price_index_data    JREI 都市地价指数            03 (地价指数, 日本特有)
  new_vs_repair_data       MLIT / Census C30 / ONS      03/04/05 (新建vs修缮比)
  res_value_gdp_ratio      BoE / Fed Z.1 / 各国央行     05 (住宅市值/GDP)
  ci_gdp_ratio (建设投资)  各国统计局                   04/05 (建设投资/GDP, 含结构细分)

注意事项:
  1. World Bank GDP 仅有 current USD 口径，03 脚本中日本 GDP 为万亿日元（本币名义）。
     如需本币口径，可用 GDP(USD) / 汇率 粗略折算，但精度不如 SNA 原始数据。
  2. World Bank GFCF 是全口径固定资本形成（含设备、知识产权等），
     而 03/04/05 脚本中 construction_investment 仅为建设投资（structures），
     两者口径不同，不可直接替代。可作为上界参考。
  3. BIS 房价指数以 2010=100 为基期，与脚本中自定义基期不同，使用时需重新基期化。
  4. PWT 数据截至 2019 年，2020+ 年份需从其他来源补充。
"""
print(mapping)

print("脚本执行完成。")
