"""
12_city_panel_urban_q.py
========================
目的：构造中国 275 城市面板数据（2005-2019），计算 Urban Q 和 MUQ，
      进行倒 U 型截面检验，生成可视化

**重要说明：本脚本使用基于城市类型学构造的代理数据，待替换为《中国城市统计年鉴》真实数据**

构造策略：
  - 275 个城市分为 5 类（一线/新一线/二线/三线/四五线）
  - 参数校准参考 six-curves 项目中的 city_re_gdp_ratio.csv 真实分布
  - 时间趋势模拟中国 2005-2019 的宏观特征

输出：
  - china_275_city_panel.csv — 275 城市面板数据
  - city_panel_regression.txt — 倒 U 型回归结果
  - fig09_city_panel.png — 3 子图可视化

依赖包：pandas, numpy, matplotlib, statsmodels
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import statsmodels.api as sm
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 0. 路径与随机种子
# ============================================================

np.random.seed(42)

OUTPUT_DIR = Path("/Users/andy/Desktop/Claude/urban-q-phase-transition")
SIX_CURVES_DIR = Path("/Users/andy/Desktop/Claude/six-curves-urban-transition")

DATA_OUT = OUTPUT_DIR / "02-data/processed/china_275_city_panel.csv"
REG_OUT = OUTPUT_DIR / "03-analysis/models/city_panel_regression.txt"
FIG_OUT = OUTPUT_DIR / "04-figures/drafts/fig09_city_panel.png"

# ============================================================
# 1. 定义城市类型学和代表性城市名称
# ============================================================

years = np.arange(2005, 2020)  # 2005-2019
T = len(years)

# --- 城市名称 ---
tier1_names = ["北京市", "上海市", "广州市", "深圳市"]

tier_new1_names = [
    "成都市", "杭州市", "武汉市", "南京市", "重庆市",
    "天津市", "苏州市", "长沙市", "西安市", "郑州市",
    "东莞市", "青岛市", "合肥市", "宁波市", "沈阳市"
]

tier2_names = [
    "福州市", "济南市", "昆明市", "大连市", "哈尔滨市",
    "厦门市", "无锡市", "温州市", "石家庄市", "太原市",
    "长春市", "南昌市", "贵阳市", "南宁市", "兰州市",
    "乌鲁木齐市", "呼和浩特市", "海口市", "珠海市", "佛山市",
    "常州市", "烟台市", "徐州市", "中山市", "惠州市",
    "泉州市", "绍兴市", "嘉兴市", "金华市", "台州市"
]

# 三线城市（80个）：一般地级市
tier3_base = [
    "潍坊市", "临沂市", "洛阳市", "芜湖市", "淄博市",
    "扬州市", "南通市", "镇江市", "盐城市", "泰州市",
    "连云港市", "宿迁市", "淮安市", "漳州市", "莆田市",
    "龙岩市", "三明市", "南平市", "宜昌市", "襄阳市",
    "荆州市", "黄冈市", "株洲市", "衡阳市", "岳阳市",
    "常德市", "邯郸市", "保定市", "沧州市", "廊坊市",
    "邢台市", "湖州市", "衢州市", "丽水市", "舟山市",
    "赣州市", "九江市", "上饶市", "宜春市", "吉安市",
    "遵义市", "曲靖市", "玉溪市", "大理市", "绵阳市",
    "德阳市", "乐山市", "南充市", "宜宾市", "泸州市",
    "咸阳市", "宝鸡市", "汉中市", "渭南市", "延安市",
    "柳州市", "桂林市", "北海市", "玉林市", "梧州市",
    "吉林市", "四平市", "通化市", "白山市", "松原市",
    "大庆市", "牡丹江市", "佳木斯市", "齐齐哈尔市", "鞍山市",
    "抚顺市", "本溪市", "锦州市", "营口市", "丹东市",
    "包头市", "鄂尔多斯市", "赤峰市", "通辽市", "银川市"
]
tier3_names = tier3_base[:80]

# 四五线城市（146个）：用"X_NNNN"格式生成（代理数据中无需真实城市名）
tier45_names = [f"四五线城市_{i+1:03d}" for i in range(146)]

all_city_names = tier1_names + tier_new1_names + tier2_names + tier3_names + tier45_names
assert len(all_city_names) == 275, f"城市数量不等于275: {len(all_city_names)}"

# --- 城市等级标签 ---
tier_labels = (
    ["一线"] * 4 +
    ["新一线"] * 15 +
    ["二线"] * 30 +
    ["三线"] * 80 +
    ["四五线"] * 146
)

# ============================================================
# 2. 参数设定（基于中国城市统计年鉴的经验分布校准）
# ============================================================
# 参考 six-curves 项目 city_re_gdp_ratio.csv:
#   全样本 re_gdp_pct 均值 ~17%, GDP 分布高度偏斜
#   一线城市 GDP >> 其余

# 基年 (2005) 参数：{ 均值, 标准差 }
# GDP 单位：亿元
city_params = {
    "一线": {
        "n": 4,
        "gdp_2005": (8000, 2000),       # 亿元
        "inv_gdp_2005": (0.18, 0.03),   # 固定资产投资/GDP
        "re_gdp_2005": (0.14, 0.03),    # 房地产投资/GDP
        "urban_rate_2005": (0.82, 0.04), # 城镇化率
        "ter_share_2005": (0.58, 0.06),  # 三产占比
        "urban_pop_2005": (1200, 300),   # 城镇人口（万人）
        "housing_stock_2005": (35000, 8000),  # 住宅存量（万平方米）
        "price_2005": (7000, 2000),      # 房价（元/平方米）
        "gdp_growth_early": (0.13, 0.02),  # 2005-2014 GDP增速
        "gdp_growth_late": (0.07, 0.01),   # 2015-2019 GDP增速
        "price_growth_early": (0.12, 0.04),  # 房价年增速（前期）
        "price_growth_late": (0.08, 0.03),   # 房价年增速（后期）
        "urban_rate_growth": (0.005, 0.002), # 城镇化率年增量
    },
    "新一线": {
        "n": 15,
        "gdp_2005": (3000, 1000),
        "inv_gdp_2005": (0.25, 0.05),
        "re_gdp_2005": (0.16, 0.04),
        "urban_rate_2005": (0.55, 0.08),
        "ter_share_2005": (0.42, 0.06),
        "urban_pop_2005": (500, 200),
        "housing_stock_2005": (15000, 5000),
        "price_2005": (4000, 1000),
        "gdp_growth_early": (0.14, 0.02),
        "gdp_growth_late": (0.07, 0.015),
        "price_growth_early": (0.10, 0.03),
        "price_growth_late": (0.07, 0.03),
        "urban_rate_growth": (0.012, 0.003),
    },
    "二线": {
        "n": 30,
        "gdp_2005": (1500, 600),
        "inv_gdp_2005": (0.30, 0.06),
        "re_gdp_2005": (0.18, 0.05),
        "urban_rate_2005": (0.48, 0.08),
        "ter_share_2005": (0.38, 0.05),
        "urban_pop_2005": (250, 100),
        "housing_stock_2005": (8000, 3000),
        "price_2005": (3500, 800),
        "gdp_growth_early": (0.14, 0.025),
        "gdp_growth_late": (0.065, 0.015),
        "price_growth_early": (0.08, 0.03),
        "price_growth_late": (0.05, 0.02),
        "urban_rate_growth": (0.014, 0.003),
    },
    "三线": {
        "n": 80,
        "gdp_2005": (600, 300),
        "inv_gdp_2005": (0.35, 0.08),
        "re_gdp_2005": (0.15, 0.05),
        "urban_rate_2005": (0.38, 0.08),
        "ter_share_2005": (0.34, 0.05),
        "urban_pop_2005": (100, 50),
        "housing_stock_2005": (3000, 1500),
        "price_2005": (2500, 600),
        "gdp_growth_early": (0.13, 0.03),
        "gdp_growth_late": (0.06, 0.02),
        "price_growth_early": (0.06, 0.02),
        "price_growth_late": (0.03, 0.02),
        "urban_rate_growth": (0.016, 0.004),
    },
    "四五线": {
        "n": 146,
        "gdp_2005": (250, 150),
        "inv_gdp_2005": (0.38, 0.10),
        "re_gdp_2005": (0.10, 0.05),
        "urban_rate_2005": (0.32, 0.08),
        "ter_share_2005": (0.30, 0.06),
        "urban_pop_2005": (40, 20),
        "housing_stock_2005": (1000, 600),
        "price_2005": (1800, 500),
        "gdp_growth_early": (0.12, 0.03),
        "gdp_growth_late": (0.05, 0.02),
        "price_growth_early": (0.04, 0.02),
        "price_growth_late": (0.02, 0.015),
        "urban_rate_growth": (0.018, 0.005),
    }
}

# ============================================================
# 3. 生成面板数据
# ============================================================

print("=" * 60)
print("生成 275 城市面板数据 (2005-2019)")
print("=" * 60)

records = []

city_idx = 0
for tier_name, params in city_params.items():
    n = params["n"]
    for j in range(n):
        city = all_city_names[city_idx]
        tier = tier_labels[city_idx]
        city_idx += 1

        # --- 基年参数抽样 ---
        gdp_0 = max(50, np.random.normal(*params["gdp_2005"]))
        inv_gdp_0 = np.clip(np.random.normal(*params["inv_gdp_2005"]), 0.05, 0.65)
        re_gdp_0 = np.clip(np.random.normal(*params["re_gdp_2005"]), 0.03, 0.40)
        urban_rate_0 = np.clip(np.random.normal(*params["urban_rate_2005"]), 0.15, 0.95)
        ter_share_0 = np.clip(np.random.normal(*params["ter_share_2005"]), 0.15, 0.85)
        urban_pop_0 = max(10, np.random.normal(*params["urban_pop_2005"]))
        housing_stock_0 = max(200, np.random.normal(*params["housing_stock_2005"]))
        price_0 = max(800, np.random.normal(*params["price_2005"]))

        # 城市特定增速
        gdp_gr_early = np.clip(np.random.normal(*params["gdp_growth_early"]), 0.03, 0.25)
        gdp_gr_late = np.clip(np.random.normal(*params["gdp_growth_late"]), 0.01, 0.12)
        price_gr_early = np.clip(np.random.normal(*params["price_growth_early"]), -0.02, 0.20)
        price_gr_late = np.clip(np.random.normal(*params["price_growth_late"]), -0.03, 0.15)
        urban_rate_gr = np.clip(np.random.normal(*params["urban_rate_growth"]), 0.002, 0.030)

        # --- 逐年生成 ---
        gdp = gdp_0
        price = price_0
        urban_rate = urban_rate_0
        ter_share = ter_share_0
        urban_pop = urban_pop_0
        housing_stock = housing_stock_0

        for t, year in enumerate(years):
            # GDP 增长（带随机扰动）
            if year <= 2014:
                g_rate = gdp_gr_early + np.random.normal(0, 0.015)
            else:
                g_rate = gdp_gr_late + np.random.normal(0, 0.01)
            # 2008-2009 金融危机冲击
            if year == 2009:
                g_rate *= 0.7
            # 2015 股灾/经济下行
            if year == 2015:
                g_rate *= 0.85
            g_rate = max(0.01, g_rate)
            if t > 0:
                gdp = gdp * (1 + g_rate)

            # 投资强度（I/GDP）随时间先升后稳）
            # 2005-2012 上升，2012-2019 趋稳或微降
            if year <= 2012:
                inv_gdp_trend = inv_gdp_0 * (1 + 0.03 * (year - 2005))
            else:
                inv_gdp_trend = inv_gdp_0 * (1 + 0.03 * 7) * (1 - 0.01 * (year - 2012))
            inv_gdp = np.clip(inv_gdp_trend + np.random.normal(0, 0.02), 0.05, 0.70)

            # 固定资产投资
            fai = gdp * inv_gdp

            # 房地产投资/GDP
            if year <= 2014:
                re_gdp = re_gdp_0 * (1 + 0.04 * (year - 2005)) + np.random.normal(0, 0.01)
            else:
                re_gdp = re_gdp_0 * (1 + 0.04 * 9) * (1 - 0.02 * (year - 2014)) + np.random.normal(0, 0.01)
            re_gdp = np.clip(re_gdp, 0.02, 0.45)
            re_invest = gdp * re_gdp

            # 基础设施投资 = FAI - 房地产投资（简化）
            infra_invest = max(0, fai - re_invest)

            # 房价
            if year <= 2014:
                p_rate = price_gr_early + np.random.normal(0, 0.02)
            else:
                p_rate = price_gr_late + np.random.normal(0, 0.02)
            # 2008-2009 短暂调整
            if year == 2008:
                p_rate *= 0.5
            if year == 2009:
                p_rate *= 0.6
            # 2014-2015 短暂调整
            if year == 2014:
                p_rate *= 0.6
            if t > 0:
                price = price * (1 + max(-0.10, p_rate))

            # 城镇化率
            if t > 0:
                du = urban_rate_gr + np.random.normal(0, 0.002)
                du = max(0.001, du)
                urban_rate = min(0.98, urban_rate + du)

            # 三产占比（逐年缓慢上升）
            if t > 0:
                d_ter = 0.005 + np.random.normal(0, 0.003)
                ter_share = min(0.85, ter_share + d_ter)

            # 城镇人口
            if t > 0:
                pop_gr = 0.02 + np.random.normal(0, 0.005)  # 城镇人口增速（含迁入）
                # 一线/新一线吸引力更强
                if tier in ["一线", "新一线"]:
                    pop_gr += 0.01
                # 四五线可能人口流出
                if tier == "四五线" and year >= 2015:
                    pop_gr -= 0.015
                pop_gr = max(-0.01, pop_gr)
                urban_pop = urban_pop * (1 + pop_gr)

            # 住宅存量（每年新增 = 竣工面积，按投资推算）
            if t > 0:
                # 新增住宅面积 ≈ 房地产投资 / 建安成本（元/m2）
                # 建安成本随时间上升：2005年约2000，2019年约4000
                construction_cost = 2000 + 150 * (year - 2005)  # 元/m2
                new_housing = re_invest * 1e8 / construction_cost / 1e4  # 转换为万平方米
                # 加上折旧减少
                depreciation = housing_stock * 0.01  # 1% 年折旧
                housing_stock = housing_stock + new_housing * 0.6 - depreciation  # 60%用于住宅

            # --- 计算 Urban Q 相关变量 ---
            # V = 住宅市场价值 = 住宅存量(万m2) * 价格(元/m2) / 1e8 → 亿元
            V_housing = housing_stock * 1e4 * price / 1e8  # 亿元

            records.append({
                "city": city,
                "tier": tier,
                "year": year,
                "gdp_100m": gdp,          # 亿元
                "fai_100m": fai,           # 固定资产投资（亿元）
                "re_invest_100m": re_invest,  # 房地产投资（亿元）
                "infra_invest_100m": infra_invest,  # 基础设施投资（亿元）
                "inv_gdp_ratio": inv_gdp,  # 固定资产投资/GDP
                "re_gdp_ratio": re_gdp,    # 房地产投资/GDP
                "urban_rate": urban_rate,   # 城镇化率
                "ter_share": ter_share,     # 三产占比
                "urban_pop_10k": urban_pop, # 城镇人口（万人）
                "housing_stock_10k_m2": housing_stock,  # 住宅存量（万m2）
                "housing_price_yuan_m2": price,  # 房价（元/m2）
                "V_housing_100m": V_housing,  # 住宅市场价值（亿元）
            })

df = pd.DataFrame(records)
print(f"面板数据维度: {df.shape[0]} 行 x {df.shape[1]} 列")
print(f"城市数: {df['city'].nunique()}")
print(f"年份范围: {df['year'].min()} - {df['year'].max()}")

# ============================================================
# 4. 计算 K(t)、Urban Q、MUQ
# ============================================================

print("\n" + "=" * 60)
print("计算 Urban Q 和 MUQ")
print("=" * 60)

# K(t): PIM 法累计资本存量
# K(t) = K(t-1) * (1 - delta) + I(t)
# delta = 2.5% (建筑物综合折旧率)
delta = 0.025

# 按城市排序后逐城市计算
df = df.sort_values(["city", "year"]).reset_index(drop=True)

k_values = []
for city in df["city"].unique():
    mask = df["city"] == city
    city_data = df.loc[mask].copy()
    k_stock = []
    for i, (_, row) in enumerate(city_data.iterrows()):
        total_inv = row["fai_100m"]
        if i == 0:
            # 基期假设：2005年之前累计投资约为当年的 6 倍
            k_stock.append(total_inv * 6)
        else:
            k_stock.append(k_stock[-1] * (1 - delta) + total_inv)
    k_values.extend(k_stock)

df["K_pim_100m"] = k_values

# Urban Q = V / K
df["urban_q"] = df["V_housing_100m"] / df["K_pim_100m"]

# MUQ = delta_V / delta_I（按城市计算差分）
df["delta_V"] = df.groupby("city")["V_housing_100m"].diff()
df["delta_V_over_V"] = df.groupby("city")["V_housing_100m"].pct_change()
df["MUQ"] = df["delta_V"] / df["fai_100m"]

# 人口增速
df["pop_growth"] = df.groupby("city")["urban_pop_10k"].pct_change()

print(f"Urban Q 统计摘要:")
print(df.groupby("tier")["urban_q"].describe().round(3))

# ============================================================
# 5. 倒 U 型截面检验
# ============================================================

print("\n" + "=" * 60)
print("倒 U 型面板回归检验")
print("=" * 60)

# 模型: delta_V/V = a + b*(I/GDP) - c*(I/GDP)^2 + X*gamma + mu_i + lambda_t + epsilon
# 使用 OLS + 城市/年份哑变量实现双向固定效应

# 准备回归数据（去除首年无差分值的观测）
reg_df = df.dropna(subset=["delta_V_over_V", "inv_gdp_ratio", "pop_growth"]).copy()

# 去除极端值（ΔV/V 超过 ±100% 的极端观测）
reg_df = reg_df[reg_df["delta_V_over_V"].between(-1.0, 2.0)].copy()

# 核心变量
reg_df["I_GDP"] = reg_df["inv_gdp_ratio"]
reg_df["I_GDP_sq"] = reg_df["I_GDP"] ** 2

# 控制变量
reg_df["urban_rate_ctrl"] = reg_df["urban_rate"]
reg_df["ter_share_ctrl"] = reg_df["ter_share"]
reg_df["pop_growth_ctrl"] = reg_df["pop_growth"]

# --- 尝试使用 linearmodels PanelOLS ---
try:
    from linearmodels.panel import PanelOLS
    USE_PANEL = True
except ImportError:
    USE_PANEL = False

reg_results = {}

if USE_PANEL:
    print("使用 linearmodels.PanelOLS 估计双向固定效应模型")
    panel_df = reg_df.set_index(["city", "year"])

    # 模型 1: 仅核心变量
    y = panel_df["delta_V_over_V"]
    X1 = sm.add_constant(panel_df[["I_GDP", "I_GDP_sq"]])
    mod1 = PanelOLS(y, X1, entity_effects=True, time_effects=True)
    res1 = mod1.fit(cov_type="clustered", cluster_entity=True)
    reg_results["Model 1: Core"] = res1

    # 模型 2: 加控制变量
    X2 = sm.add_constant(panel_df[["I_GDP", "I_GDP_sq",
                                    "urban_rate_ctrl", "ter_share_ctrl", "pop_growth_ctrl"]])
    mod2 = PanelOLS(y, X2, entity_effects=True, time_effects=True)
    res2 = mod2.fit(cov_type="clustered", cluster_entity=True)
    reg_results["Model 2: Full"] = res2

else:
    print("linearmodels 未安装，使用 OLS + 哑变量实现固定效应")

    # 城市和年份哑变量
    city_dummies = pd.get_dummies(reg_df["city"], prefix="city", drop_first=True, dtype=float)
    year_dummies = pd.get_dummies(reg_df["year"], prefix="yr", drop_first=True, dtype=float)

    # 模型 1: 仅核心变量 + FE
    X1_cols = ["I_GDP", "I_GDP_sq"]
    X1 = sm.add_constant(pd.concat([reg_df[X1_cols].reset_index(drop=True),
                                     city_dummies.reset_index(drop=True),
                                     year_dummies.reset_index(drop=True)], axis=1))
    y1 = reg_df["delta_V_over_V"].reset_index(drop=True)
    mod1 = sm.OLS(y1, X1).fit(cov_type="HC1")
    reg_results["Model 1: Core"] = mod1

    # 模型 2: 加控制变量 + FE
    X2_cols = ["I_GDP", "I_GDP_sq", "urban_rate_ctrl", "ter_share_ctrl", "pop_growth_ctrl"]
    X2 = sm.add_constant(pd.concat([reg_df[X2_cols].reset_index(drop=True),
                                     city_dummies.reset_index(drop=True),
                                     year_dummies.reset_index(drop=True)], axis=1))
    y2 = reg_df["delta_V_over_V"].reset_index(drop=True)
    mod2 = sm.OLS(y2, X2).fit(cov_type="HC1")
    reg_results["Model 2: Full"] = mod2

# --- 提取关键结果 ---
report_lines = []
report_lines.append("=" * 70)
report_lines.append("275 城市面板 Urban Q 倒 U 型检验报告")
report_lines.append("=" * 70)
report_lines.append(f"分析日期: 2026-03-20")
report_lines.append(f"样本: 中国 275 城市面板 (代理数据), 2005-2019")
report_lines.append(f"观测数: {len(reg_df)} (去除缺失和极端值后)")
report_lines.append(f"城市数: {reg_df['city'].nunique()}")
report_lines.append(f"估计方法: {'PanelOLS (linearmodels)' if USE_PANEL else 'OLS + 城市/年份哑变量'}")
report_lines.append("")
report_lines.append("重要说明: 本分析使用基于城市类型学构造的代理数据")
report_lines.append("         结果仅用于方法验证，待替换为真实数据后更新")
report_lines.append("")

for model_name, res in reg_results.items():
    report_lines.append("-" * 50)
    report_lines.append(f"模型: {model_name}")
    report_lines.append("-" * 50)

    if USE_PANEL:
        b_val = res.params.get("I_GDP", np.nan)
        c_val = res.params.get("I_GDP_sq", np.nan)
        b_se = res.std_errors.get("I_GDP", np.nan)
        c_se = res.std_errors.get("I_GDP_sq", np.nan)
        b_p = res.pvalues.get("I_GDP", np.nan)
        c_p = res.pvalues.get("I_GDP_sq", np.nan)
        r2 = res.rsquared_within
    else:
        b_val = res.params.get("I_GDP", np.nan)
        c_val = res.params.get("I_GDP_sq", np.nan)
        b_se = res.bse.get("I_GDP", np.nan)
        c_se = res.bse.get("I_GDP_sq", np.nan)
        b_p = res.pvalues.get("I_GDP", np.nan)
        c_p = res.pvalues.get("I_GDP_sq", np.nan)
        r2 = res.rsquared

    report_lines.append(f"  一次项 b(I/GDP):     {b_val:+.4f}  (SE={b_se:.4f}, p={b_p:.4f})")
    report_lines.append(f"  二次项 c(I/GDP)^2:   {c_val:+.4f}  (SE={c_se:.4f}, p={c_p:.4f})")
    report_lines.append(f"  R-squared:           {r2:.4f}")

    # 倒 U 型检验
    if b_val > 0 and c_val < 0:
        inv_u = True
        I_opt = -b_val / (2 * c_val)
        I_destroy = -b_val / c_val
        report_lines.append(f"  --> 倒 U 型成立: b > 0, c < 0")
        report_lines.append(f"  --> I*_opt/GDP  = {I_opt:.4f} ({I_opt*100:.1f}%)")
        report_lines.append(f"  --> I_destroy/GDP = {I_destroy:.4f} ({I_destroy*100:.1f}%)")
    elif b_val < 0 and c_val > 0:
        report_lines.append(f"  --> U 型关系 (非倒 U): b < 0, c > 0")
        inv_u = False
        I_opt = np.nan
        I_destroy = np.nan
    else:
        report_lines.append(f"  --> 倒 U 型不成立 (b 和 c 符号不符合预期)")
        inv_u = False
        I_opt = np.nan
        I_destroy = np.nan

    # 控制变量（仅模型2）
    if "Full" in model_name:
        for ctrl in ["urban_rate_ctrl", "ter_share_ctrl", "pop_growth_ctrl"]:
            if USE_PANEL:
                cv = res.params.get(ctrl, np.nan)
                cp = res.pvalues.get(ctrl, np.nan)
            else:
                cv = res.params.get(ctrl, np.nan)
                cp = res.pvalues.get(ctrl, np.nan)
            report_lines.append(f"  控制变量 {ctrl}: {cv:+.4f} (p={cp:.4f})")

    report_lines.append("")

# --- 分城市等级的 Q 值统计 ---
report_lines.append("=" * 50)
report_lines.append("城市分类分析")
report_lines.append("=" * 50)

# 最新年份(2019)的统计
df_2019 = df[df["year"] == 2019].copy()

report_lines.append("\n--- 2019 年各等级城市 Urban Q 统计 ---")
for tier in ["一线", "新一线", "二线", "三线", "四五线"]:
    sub = df_2019[df_2019["tier"] == tier]
    q_mean = sub["urban_q"].mean()
    q_std = sub["urban_q"].std()
    q_med = sub["urban_q"].median()
    q_min = sub["urban_q"].min()
    q_max = sub["urban_q"].max()
    n_above1 = (sub["urban_q"] > 1).sum()
    n_below1 = (sub["urban_q"] < 1).sum()
    inv_gdp_mean = sub["inv_gdp_ratio"].mean()
    report_lines.append(f"\n{tier} ({len(sub)} 城市):")
    report_lines.append(f"  Q 均值: {q_mean:.3f} (SD={q_std:.3f})")
    report_lines.append(f"  Q 中位数: {q_med:.3f}")
    report_lines.append(f"  Q 范围: [{q_min:.3f}, {q_max:.3f}]")
    report_lines.append(f"  Q > 1: {n_above1} 城市, Q < 1: {n_below1} 城市")
    report_lines.append(f"  I/GDP 均值: {inv_gdp_mean*100:.1f}%")

# 总体统计
report_lines.append(f"\n--- 全部 275 城市 (2019) ---")
report_lines.append(f"  Q > 1: {(df_2019['urban_q'] > 1).sum()} 城市 ({(df_2019['urban_q'] > 1).mean()*100:.1f}%)")
report_lines.append(f"  Q < 1: {(df_2019['urban_q'] < 1).sum()} 城市 ({(df_2019['urban_q'] < 1).mean()*100:.1f}%)")
report_lines.append(f"  Q 均值: {df_2019['urban_q'].mean():.3f}")
report_lines.append(f"  Q 中位数: {df_2019['urban_q'].median():.3f}")

# --- 投资强度与 Q 的分组分析 ---
report_lines.append(f"\n--- 投资强度分组 x Urban Q (2019) ---")
df_2019["inv_group"] = pd.qcut(df_2019["inv_gdp_ratio"], 5,
                                labels=["Q1(低)", "Q2", "Q3", "Q4", "Q5(高)"])
for grp in ["Q1(低)", "Q2", "Q3", "Q4", "Q5(高)"]:
    sub = df_2019[df_2019["inv_group"] == grp]
    report_lines.append(f"  {grp}: I/GDP={sub['inv_gdp_ratio'].mean()*100:.1f}%, "
                        f"Q={sub['urban_q'].mean():.3f}, "
                        f"ΔV/V={sub['delta_V_over_V'].mean()*100:.1f}%")

report_lines.append("")
report_lines.append("=" * 50)
report_lines.append("分析完成")
report_lines.append("=" * 50)

report_text = "\n".join(report_lines)
print(report_text)

# 保存回归报告
with open(REG_OUT, "w", encoding="utf-8") as f:
    f.write(report_text)
print(f"\n回归结果已保存: {REG_OUT}")

# ============================================================
# 6. 保存面板数据
# ============================================================

df.to_csv(DATA_OUT, index=False, float_format="%.4f")
print(f"面板数据已保存: {DATA_OUT}")

# ============================================================
# 7. 可视化：3 子图
# ============================================================

print("\n" + "=" * 60)
print("生成可视化")
print("=" * 60)

# 中文字体（macOS）
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Heiti SC', 'PingFang SC', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# Nature 风格
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

# 城市等级颜色
TIER_COLORS = {
    "一线": "#D62728",    # 红色
    "新一线": "#FF7F0E",  # 橙色
    "二线": "#2CA02C",    # 绿色
    "三线": "#1F77B4",    # 蓝色
    "四五线": "#9467BD",  # 紫色
}

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.subplots_adjust(wspace=0.35, top=0.90, bottom=0.12, left=0.06, right=0.97)

# ------ 子图1: Urban Q 分布直方图 (2019) ------
ax = axes[0]
q_2019 = df_2019["urban_q"].values

# 各等级分层直方图
bins = np.linspace(0, df_2019["urban_q"].quantile(0.99), 40)
for tier in ["四五线", "三线", "二线", "新一线", "一线"]:
    sub = df_2019[df_2019["tier"] == tier]["urban_q"]
    ax.hist(sub, bins=bins, alpha=0.6, color=TIER_COLORS[tier],
            label=f"{tier} (n={len(sub)})", edgecolor="white", linewidth=0.3)

ax.axvline(x=1.0, color="black", linestyle="--", linewidth=1.0, alpha=0.7)
ax.text(1.02, ax.get_ylim()[1] * 0.9, "Q = 1", fontsize=8, color="black", va="top")
ax.axvline(x=df_2019["urban_q"].median(), color="gray", linestyle=":", linewidth=0.8)
ax.text(df_2019["urban_q"].median() + 0.02, ax.get_ylim()[1] * 0.75,
        f'Median={df_2019["urban_q"].median():.2f}', fontsize=7, color="gray")

ax.set_xlabel("Urban Q (V/K)")
ax.set_ylabel("城市数量")
ax.set_title("A. Urban Q 分布 (2019)", fontweight="bold", loc="left")
ax.legend(loc="upper right", frameon=False, fontsize=6.5)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# ------ 子图2: 投资效率散点图 ------
ax = axes[1]

# 使用所有年份数据（去除缺失）
plot_df = df.dropna(subset=["delta_V_over_V", "inv_gdp_ratio"]).copy()
# 去除极端值
plot_df = plot_df[plot_df["delta_V_over_V"].between(-0.5, 1.5)]

for tier in ["一线", "新一线", "二线", "三线", "四五线"]:
    sub = plot_df[plot_df["tier"] == tier]
    ax.scatter(sub["inv_gdp_ratio"] * 100, sub["delta_V_over_V"] * 100,
               s=8, alpha=0.25, color=TIER_COLORS[tier], label=tier, zorder=2)

# 二次拟合线
x_fit = np.linspace(5, 65, 200)
# 全样本拟合
X_poly = np.column_stack([plot_df["inv_gdp_ratio"], plot_df["inv_gdp_ratio"] ** 2])
X_poly = sm.add_constant(X_poly)
y_poly = plot_df["delta_V_over_V"]
fit_poly = sm.OLS(y_poly, X_poly).fit()
y_fit = (fit_poly.params[0] + fit_poly.params[1] * (x_fit / 100) +
         fit_poly.params[2] * (x_fit / 100) ** 2) * 100
ax.plot(x_fit, y_fit, "k-", linewidth=2, label="二次拟合", zorder=5)

# 标注峰值
if fit_poly.params[2] < 0:  # 倒 U 型
    peak_x = -fit_poly.params[1] / (2 * fit_poly.params[2]) * 100
    peak_y = (fit_poly.params[0] + fit_poly.params[1] * peak_x / 100 +
              fit_poly.params[2] * (peak_x / 100) ** 2) * 100
    if 5 < peak_x < 65:
        ax.axvline(x=peak_x, color="gray", linestyle=":", linewidth=0.8, alpha=0.6)
        ax.annotate(f"I*_opt={peak_x:.0f}%", xy=(peak_x, peak_y),
                    xytext=(peak_x + 5, peak_y + 5), fontsize=7,
                    arrowprops=dict(arrowstyle="->", color="gray", lw=0.8))

ax.axhline(y=0, color="black", linestyle="-", linewidth=0.4, alpha=0.3)
ax.set_xlabel("投资强度 I/GDP (%)")
ax.set_ylabel("资产增值率 ΔV/V (%)")
ax.set_title("B. 投资效率散点图", fontweight="bold", loc="left")
ax.legend(loc="upper right", frameon=False, fontsize=6, ncol=2)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# ------ 子图3: Urban Q 随时间演化 ------
ax = axes[2]

for tier in ["一线", "新一线", "二线", "三线", "四五线"]:
    sub = df[df["tier"] == tier].groupby("year")["urban_q"].mean()
    ax.plot(sub.index, sub.values, "-o", color=TIER_COLORS[tier],
            markersize=3, linewidth=1.5, label=tier)

ax.axhline(y=1.0, color="black", linestyle="--", linewidth=1.0, alpha=0.5)
ax.text(2019.3, 1.02, "Q = 1", fontsize=7, color="black", va="bottom")

ax.set_xlabel("年份")
ax.set_ylabel("Urban Q (组均值)")
ax.set_title("C. Urban Q 时间演化", fontweight="bold", loc="left")
ax.legend(loc="best", frameon=False, fontsize=7)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_xlim(2004.5, 2019.5)

# 保存
fig.savefig(FIG_OUT, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"图表已保存: {FIG_OUT}")

# ============================================================
# 8. 终端摘要
# ============================================================

print("\n" + "=" * 60)
print("关键结果摘要")
print("=" * 60)

# 2019 年 Q 值
print(f"\n2019 年 Urban Q:")
for tier in ["一线", "新一线", "二线", "三线", "四五线"]:
    sub = df_2019[df_2019["tier"] == tier]
    print(f"  {tier:6s}: Q = {sub['urban_q'].mean():.3f} (SD={sub['urban_q'].std():.3f}), "
          f"I/GDP = {sub['inv_gdp_ratio'].mean()*100:.1f}%")

print(f"\n全样本 Q 均值: {df_2019['urban_q'].mean():.3f}")
print(f"Q > 1 的城市比例: {(df_2019['urban_q'] > 1).mean()*100:.1f}%")

# 倒 U 型关键参数
if not np.isnan(I_opt):
    print(f"\n倒 U 型回归（全样本双向 FE）:")
    print(f"  I*_opt/GDP = {I_opt*100:.1f}%")
    print(f"  I_destroy/GDP = {I_destroy*100:.1f}%")
    # 超过 I_destroy 的城市
    n_destroy = (df_2019["inv_gdp_ratio"] > I_destroy).sum()
    print(f"  2019年超过毁灭阈值的城市: {n_destroy} ({n_destroy/275*100:.1f}%)")

print("\n分析完成。")
