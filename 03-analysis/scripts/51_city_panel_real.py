"""
51_city_panel_real.py
=====================
目的：从真实数据源构建中国城市面板，计算城市级 Urban Q

数据来源：
  1. 中国城市数据库6.0版（马克数据网）— 300+ 城市，1990-2023，214 列
  2. 58同城房价数据 — 365 城市，2010-2024
  3. 安居客房价数据 — 补充验证
  4. 地级市债务数据 — 2006-2023
  5. 省级真实数据 — 31 省，2005-2023

输出：
  - china_city_panel_real.csv — 城市面板（含 Urban Q）
  - china_provincial_panel_real.csv — 省级面板（含 Urban Q）
  - 数据摘要报告（控制台输出）

依赖包：pandas, numpy, openpyxl
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
import sys
import time

warnings.filterwarnings('ignore')

# ============================================================
# 0. 路径定义
# ============================================================

BASE = Path("/Users/andy/Desktop/Claude/urban-q-phase-transition")
SIX = Path("/Users/andy/Desktop/Claude/six-curves-urban-transition")

# 输入数据
CITY_DB = SIX / "02-data/面板数据/中国城市数据库6.0版.xlsx"
ECON_DB = SIX / "02-data/面板数据/全国地级市2000-2023年国民经济指标.xlsx"
PRICE_58 = SIX / "02-data/面板数据/地级市房价商品房均价数据/地级市-房价数据（58同城、安居客）（2010-2024年）00/58同城房价（2010-2024）.xlsx"
PRICE_AJK = SIX / "02-data/面板数据/地级市房价商品房均价数据/地级市-房价数据（58同城、安居客）（2010-2024年）00/安居客房价（2015-2024）.xlsx"
DEBT_FILE = SIX / "02-data/面板数据/地方债务/全国地方债务余额(省级+地级市)2006-2023/地级市/整合.csv"
PROV_DATA = BASE / "02-data/raw/china_provincial_real_data.csv"

# 输出
OUT_CITY = BASE / "02-data/processed/china_city_panel_real.csv"
OUT_PROV = BASE / "02-data/processed/china_provincial_panel_real.csv"

# 确保输出目录存在
OUT_CITY.parent.mkdir(parents=True, exist_ok=True)

# ============================================================
# 1. 读取中国城市数据库（线性插值版，缺失值已处理）
# ============================================================

print("=" * 70)
print("步骤 1：读取中国城市数据库6.0版（线性插值 sheet）")
print("=" * 70)
t0 = time.time()

# 使用线性插值 sheet（缺失值已填补）
city_db = pd.read_excel(
    CITY_DB,
    sheet_name='线性插值',
    engine='openpyxl'
)

print(f"  读取完成，耗时 {time.time()-t0:.1f}s")
print(f"  原始维度: {city_db.shape[0]} 行 x {city_db.shape[1]} 列")

# 提取关键变量
key_cols = {
    '年份': 'year',
    '省份': 'province',
    '城市': 'city',
    '省份代码': 'province_code',
    '城市代码': 'city_code',
    '所属地域': 'region',
    '胡焕庸线': 'huhuanyong',
    '地区生产总值(万元)': 'gdp_10k',                    # 万元
    '第一产业增加值(万元)': 'gdp_primary_10k',
    '第二产业增加值(万元)': 'gdp_secondary_10k',
    '第三产业增加值(万元)': 'gdp_tertiary_10k',
    '第一产业增加值占GDP比重(%)': 'primary_share_pct',
    '第二产业增加值占GDP比重(%)': 'secondary_share_pct',
    '第三产业增加值占GDP比重(%)': 'tertiary_share_pct',
    '人均地区生产总值(元)': 'gdp_per_capita',
    '户籍人口(万人)': 'hukou_pop_10k',                  # 万人
    '常住人口(万人)': 'resident_pop_10k',
    '城镇常住人口(万人)': 'urban_pop_10k',
    '常住人口城镇化率(%)': 'urbanization_rate_pct',
    '固定资产投资总额(万元)': 'fai_10k',                 # 万元
    '房地产开发投资完成额(万元)': 're_invest_10k',
    '住宅开发投资完成额(万元)': 'res_invest_10k',
    '城镇非私营单位在岗职工平均工资(元)': 'avg_wage',
    '行政区域土地面积(平方公里)': 'land_area_km2',
    '地方财政一般预算内收入(万元)': 'fiscal_revenue_10k',
    '地方财政一般预算内支出(万元)': 'fiscal_expenditure_10k',
    '年末金融机构各项贷款余额(万元)': 'loan_balance_10k',
    '年末金融机构存款余额(万元)': 'deposit_balance_10k',
    '地区生产总值增长率(%)': 'gdp_growth_pct',
}

# 筛选存在的列
available_cols = {k: v for k, v in key_cols.items() if k in city_db.columns}
missing_cols = set(key_cols.keys()) - set(available_cols.keys())
if missing_cols:
    print(f"  警告：以下列不在数据中: {missing_cols}")

df_city = city_db[list(available_cols.keys())].rename(columns=available_cols)

# 基本清洗
df_city['year'] = df_city['year'].astype(int)
df_city['city_code'] = pd.to_numeric(df_city['city_code'], errors='coerce')

# 标准化城市名（去掉"市"后缀用于后续匹配）
df_city['city_clean'] = df_city['city'].str.replace('市$', '', regex=True).str.strip()
# 省份也清洗
df_city['province_clean'] = df_city['province'].str.replace('省$|市$|自治区$|壮族自治区$|回族自治区$|维吾尔自治区$|特别行政区$', '', regex=True).str.strip()

# 转换单位：万元 -> 亿元
for col in ['gdp_10k', 'gdp_primary_10k', 'gdp_secondary_10k', 'gdp_tertiary_10k',
            'fai_10k', 're_invest_10k', 'res_invest_10k',
            'fiscal_revenue_10k', 'fiscal_expenditure_10k',
            'loan_balance_10k', 'deposit_balance_10k']:
    new_col = col.replace('_10k', '_100m')
    if col in df_city.columns:
        df_city[new_col] = df_city[col] / 10000  # 万元 -> 亿元
        df_city.drop(columns=[col], inplace=True)

# 人口：万人 -> 万人（保持不变，但确保数值型）
for col in ['hukou_pop_10k', 'resident_pop_10k', 'urban_pop_10k']:
    if col in df_city.columns:
        df_city[col] = pd.to_numeric(df_city[col], errors='coerce')

print(f"  整理后维度: {df_city.shape[0]} 行 x {df_city.shape[1]} 列")
print(f"  城市数: {df_city['city'].nunique()}")
print(f"  年份范围: {df_city['year'].min()} - {df_city['year'].max()}")

# ============================================================
# 2. 读取房价数据（58同城 + 安居客）
# ============================================================

print("\n" + "=" * 70)
print("步骤 2：读取房价数据")
print("=" * 70)

# 58同城（2010-2024，覆盖更广）
df_58 = pd.read_excel(PRICE_58, sheet_name='Sheet1', engine='openpyxl')
df_58 = df_58[['省份', '城市', '年份', '价格(元/㎡）']].rename(columns={
    '省份': 'province_hp',
    '城市': 'city_hp',
    '年份': 'year',
    '价格(元/㎡）': 'price_58'
})
df_58['year'] = pd.to_numeric(df_58['year'], errors='coerce')
df_58['price_58'] = pd.to_numeric(df_58['price_58'], errors='coerce')
df_58 = df_58.dropna(subset=['year', 'price_58'])
df_58['year'] = df_58['year'].astype(int)
# 去重：同一城市同一年份保留第一条
df_58 = df_58.drop_duplicates(subset=['city_hp', 'year'], keep='first')  # 去重
print(f"  58同城: {len(df_58)} 条记录, {df_58['city_hp'].nunique()} 城市, {df_58['year'].min()}-{df_58['year'].max()}")

# 安居客（2015-2024）
df_ajk = pd.read_excel(PRICE_AJK, sheet_name='Sheet1', engine='openpyxl')
df_ajk = df_ajk[['省份', '城市', '年份', '价格（元/㎡）']].rename(columns={
    '省份': 'province_hp',
    '城市': 'city_hp',
    '年份': 'year',
    '价格（元/㎡）': 'price_ajk'
})
df_ajk['year'] = pd.to_numeric(df_ajk['year'], errors='coerce')
df_ajk['price_ajk'] = pd.to_numeric(df_ajk['price_ajk'], errors='coerce')
df_ajk = df_ajk.dropna(subset=['year', 'price_ajk'])
df_ajk['year'] = df_ajk['year'].astype(int)
# 去重：安居客数据有大量重复行
df_ajk = df_ajk.drop_duplicates(subset=['city_hp', 'year'], keep='first')
print(f"  安居客: {len(df_ajk)} 条记录, {df_ajk['city_hp'].nunique()} 城市, {df_ajk['year'].min()}-{df_ajk['year'].max()}")

# 标准化城市名用于匹配
df_58['city_clean'] = df_58['city_hp'].str.replace('市$', '', regex=True).str.strip()
df_ajk['city_clean'] = df_ajk['city_hp'].str.replace('市$', '', regex=True).str.strip()

# 合并两个房价源：以 58同城 为主，安居客补充
price_merged = df_58[['city_clean', 'year', 'price_58']].merge(
    df_ajk[['city_clean', 'year', 'price_ajk']],
    on=['city_clean', 'year'],
    how='outer'
)

# 取均值作为最终房价（两源都有时取均值，只有一源时取该值）
price_merged['house_price'] = price_merged[['price_58', 'price_ajk']].mean(axis=1)
price_merged['price_source'] = np.where(
    price_merged['price_58'].notna() & price_merged['price_ajk'].notna(), 'both',
    np.where(price_merged['price_58'].notna(), '58tc', 'anjuke')
)

# 确保合并后无重复
price_merged = price_merged.drop_duplicates(subset=['city_clean', 'year'], keep='first')

print(f"  合并后: {len(price_merged)} 条记录")
print(f"  来源分布: {price_merged['price_source'].value_counts().to_dict()}")

# ============================================================
# 3. 读取债务数据
# ============================================================

print("\n" + "=" * 70)
print("步骤 3：读取地级市债务数据")
print("=" * 70)

df_debt = pd.read_csv(DEBT_FILE, encoding='utf-8-sig')
df_debt.columns = df_debt.columns.str.strip().str.replace('\t', '')

# 重命名关键列
debt_cols = {
    '城市': 'city_debt',
    'year': 'year',
    '地方政府债-债券余额(亿)': 'gov_bond_balance',
    '城投债-债券余额(亿)': 'lgfv_bond_balance',
    '总计-债券余额(亿)': 'total_bond_balance',
    '地方政府债-债券数量(只)': 'gov_bond_count',
    '城投债-债券数量(只)': 'lgfv_bond_count',
    '总计-债券数量(只)': 'total_bond_count',
}
available_debt = {k: v for k, v in debt_cols.items() if k in df_debt.columns}
df_debt = df_debt[list(available_debt.keys())].rename(columns=available_debt)

# 类型转换
df_debt['year'] = pd.to_numeric(df_debt['year'], errors='coerce').astype(int)
for col in ['gov_bond_balance', 'lgfv_bond_balance', 'total_bond_balance']:
    if col in df_debt.columns:
        df_debt[col] = pd.to_numeric(df_debt[col], errors='coerce')

# 标准化城市名
df_debt['city_clean'] = df_debt['city_debt'].str.replace('市$', '', regex=True).str.strip()

# 去重：同一城市同一年份保留余额较大的（更完整的记录）
df_debt = df_debt.sort_values('total_bond_balance', ascending=False)
df_debt = df_debt.drop_duplicates(subset=['city_clean', 'year'], keep='first')

print(f"  债务数据: {len(df_debt)} 条记录, {df_debt['city_clean'].nunique()} 城市")
print(f"  年份范围: {df_debt['year'].min()} - {df_debt['year'].max()}")

# ============================================================
# 4. 合并数据集
# ============================================================

print("\n" + "=" * 70)
print("步骤 4：合并数据集")
print("=" * 70)

# 4a. 匹配房价到城市面板
# 城市数据库中的 city_clean 和房价的 city_clean 匹配
df_panel = df_city.merge(
    price_merged[['city_clean', 'year', 'house_price', 'price_58', 'price_ajk', 'price_source']],
    on=['city_clean', 'year'],
    how='left'
)

n_matched_hp = df_panel['house_price'].notna().sum()
n_cities_hp = df_panel.loc[df_panel['house_price'].notna(), 'city'].nunique()
print(f"  房价匹配: {n_matched_hp} 条记录, {n_cities_hp} 城市")

# 诊断：找出未匹配的房价城市
hp_cities = set(price_merged['city_clean'].unique())
db_cities = set(df_city['city_clean'].unique())
unmatched_hp = hp_cities - db_cities
if unmatched_hp:
    print(f"  未匹配的房价城市 ({len(unmatched_hp)}): {sorted(list(unmatched_hp))[:20]}...")

# 4b. 匹配债务数据
df_panel = df_panel.merge(
    df_debt[['city_clean', 'year', 'gov_bond_balance', 'lgfv_bond_balance', 'total_bond_balance']],
    on=['city_clean', 'year'],
    how='left'
)

n_matched_debt = df_panel['total_bond_balance'].notna().sum()
n_cities_debt = df_panel.loc[df_panel['total_bond_balance'].notna(), 'city'].nunique()
print(f"  债务匹配: {n_matched_debt} 条记录, {n_cities_debt} 城市")

# ============================================================
# 5. 计算城市级 Urban Q
# ============================================================

print("\n" + "=" * 70)
print("步骤 5：计算城市级 Urban Q")
print("=" * 70)

# --- 5a. 人口序列修正 ---
# 问题：常住人口仅在2020年(七普)后才有，户籍人口在之前有
# 使用2020年 resident/hukou 比率对之前年份的户籍人口进行缩放
# 这样得到一致的"估计常住人口"序列

def fix_population(group):
    """修正人口序列：用2020年常住/户籍比率缩放历史户籍人口"""
    group = group.sort_values('year').copy()

    # 计算2020年的 resident/hukou ratio
    mask_2020 = group['year'] == 2020
    ratio = np.nan
    if mask_2020.any():
        res = group.loc[mask_2020, 'resident_pop_10k'].values[0]
        huk = group.loc[mask_2020, 'hukou_pop_10k'].values[0]
        if pd.notna(res) and pd.notna(huk) and huk > 0:
            ratio = res / huk

    # 构建一致的人口序列
    pop = group['resident_pop_10k'].copy()
    if pd.notna(ratio) and ratio > 0:
        # 有常住/户籍比率：对缺失常住人口的年份，用 hukou * ratio 填补
        missing_mask = pop.isna() & group['hukou_pop_10k'].notna()
        pop.loc[missing_mask] = group.loc[missing_mask, 'hukou_pop_10k'] * ratio
    else:
        # 无比率：直接用户籍人口（全国平均 ratio ~1.0 对于大多数城市）
        pop = pop.fillna(group['hukou_pop_10k'])

    group['pop_10k'] = pop
    return group

print("  修正人口序列（常住人口一致性校准）...")
df_panel = df_panel.groupby('city', group_keys=False).apply(fix_population)
print(f"  人口非空记录: {df_panel['pop_10k'].notna().sum()}")

# --- 5b. FAI 填补（2017-2023 缺失）---
# 中国自2017年起停止公布城市级固定资产投资绝对值
# 策略：用最后已知年份的 FAI/GDP 比率 x 当年 GDP 估算
# 对于 FAI/GDP ratio，取 2014-2016 均值（避免单年异常）

def impute_fai(group):
    """对2017年后缺失的FAI进行估算"""
    group = group.sort_values('year').copy()

    # 计算 2014-2016 的 FAI/GDP ratio 均值
    mask = (group['year'] >= 2014) & (group['year'] <= 2016)
    sub = group.loc[mask]
    valid = sub.loc[sub['fai_100m'].notna() & sub['gdp_100m'].notna() & (sub['gdp_100m'] > 0)]

    if len(valid) > 0:
        avg_ratio = (valid['fai_100m'] / valid['gdp_100m']).mean()
        # 限制合理范围
        avg_ratio = min(avg_ratio, 2.0)

        # 对缺失年份用 ratio x GDP 填补
        missing_mask = group['fai_100m'].isna() & group['gdp_100m'].notna() & (group['year'] >= 2017)
        group.loc[missing_mask, 'fai_100m'] = group.loc[missing_mask, 'gdp_100m'] * avg_ratio
        group.loc[missing_mask, 'fai_imputed'] = True

    return group

df_panel['fai_imputed'] = False
print("  估算2017-2023年FAI（基于FAI/GDP比率）...")
df_panel = df_panel.groupby('city', group_keys=False).apply(impute_fai)
n_imputed = df_panel['fai_imputed'].sum()
print(f"  FAI 估算记录: {n_imputed}")

# --- 5c. V(t): 城市不动产市场价值 ---
# V(t) = 房价 (元/m2) x 常住人口 x 人均住房面积 (m2/人)
# 人均住房面积：基于统计局数据
# 2000: ~20, 2010: ~32, 2020: ~41.76, 2023: ~42.5

area_lookup = {}
for y in range(1990, 2025):
    if y <= 2000:
        area_lookup[y] = 20.0
    elif y <= 2020:
        area_lookup[y] = 20.0 + (41.76 - 20.0) * (y - 2000) / 20
    else:
        area_lookup[y] = 41.76 + 0.25 * (y - 2020)

df_panel['per_capita_area_m2'] = df_panel['year'].map(area_lookup)

# V(t) = 房价(元/m2) x 人口(万人) x 1万 x 人均面积(m2/人) / 1亿 -> 亿元
df_panel['V_100m'] = (
    df_panel['house_price'] *          # 元/m2
    df_panel['pop_10k'] * 10000 *      # 人
    df_panel['per_capita_area_m2'] /   # m2/人
    1e8                                 # 转换为亿元
)

print(f"  V(t) 非空记录: {df_panel['V_100m'].notna().sum()}")

# --- 5d. K(t): 城市资本存量（永续盘存法 PIM）---
# K(t) = K(t-1) * (1 - delta) + I(t)
# delta = 折旧率 = 0.05（基建常用）

DELTA = 0.05  # 年折旧率

def compute_pim(group):
    """永续盘存法计算资本存量"""
    group = group.sort_values('year').copy()
    fai = group['fai_100m'].values
    n = len(group)

    K = np.full(n, np.nan)

    valid_idx = np.where(~np.isnan(fai))[0]
    if len(valid_idx) == 0:
        group['K_100m'] = np.nan
        return group

    first_valid = valid_idx[0]

    # 初始增长率估计
    if len(valid_idx) >= 3:
        early_fai = fai[valid_idx[:5]]
        early_fai = early_fai[early_fai > 0]
        if len(early_fai) >= 2:
            g = np.mean(np.diff(early_fai) / early_fai[:-1])
            g = max(0.02, min(g, 0.30))
        else:
            g = 0.10
    else:
        g = 0.10

    if fai[first_valid] > 0:
        K[first_valid] = fai[first_valid] / (g + DELTA)
    else:
        K[first_valid] = 0

    for i in range(first_valid + 1, n):
        if np.isnan(K[i-1]):
            if not np.isnan(fai[i]) and fai[i] > 0:
                K[i] = fai[i] / (g + DELTA)
            continue
        inv = fai[i] if not np.isnan(fai[i]) else 0
        K[i] = K[i-1] * (1 - DELTA) + inv

    group['K_100m'] = K
    return group

print("  计算资本存量 (PIM)...")
df_panel = df_panel.groupby('city', group_keys=False).apply(compute_pim)
print(f"  K(t) 非空记录: {df_panel['K_100m'].notna().sum()}")

# --- Urban Q = V / K ---
df_panel['urban_q'] = df_panel['V_100m'] / df_panel['K_100m']

# 清理极端值：Q < 0 或 Q > 20 视为异常
df_panel.loc[df_panel['urban_q'] < 0, 'urban_q'] = np.nan
df_panel.loc[df_panel['urban_q'] > 20, 'urban_q'] = np.nan

n_q = df_panel['urban_q'].notna().sum()
n_cities_q = df_panel.loc[df_panel['urban_q'].notna(), 'city'].nunique()
print(f"  Urban Q 有效记录: {n_q}, 覆盖 {n_cities_q} 城市")

# --- 补充指标 ---
# FAI/GDP 比率
df_panel['fai_gdp_ratio'] = df_panel['fai_100m'] / df_panel['gdp_100m']
df_panel.loc[df_panel['fai_gdp_ratio'] > 3, 'fai_gdp_ratio'] = np.nan  # 去极端

# 房地产投资占GDP比重
df_panel['re_gdp_ratio'] = df_panel['re_invest_100m'] / df_panel['gdp_100m']

# 债务/GDP 比率
df_panel['debt_gdp_ratio'] = df_panel['total_bond_balance'] / df_panel['gdp_100m']

# ============================================================
# 6. 省级 Urban Q（从省级真实数据计算）
# ============================================================

print("\n" + "=" * 70)
print("步骤 6：计算省级 Urban Q")
print("=" * 70)

df_prov = pd.read_csv(PROV_DATA, encoding='utf-8-sig')
df_prov.columns = df_prov.columns.str.replace('\ufeff', '')
df_prov['year'] = pd.to_numeric(df_prov['year'], errors='coerce').astype(int)

# 转换数值列
for col in ['gdp_billion_yuan', 'urbanization_rate_pct', 'tertiary_share_pct',
            'fai_billion_yuan', 'fai_gdp_ratio']:
    df_prov[col] = pd.to_numeric(df_prov[col], errors='coerce')

print(f"  省级数据: {len(df_prov)} 行, {df_prov['province'].nunique()} 省, {df_prov['year'].min()}-{df_prov['year'].max()}")

# 从城市面板中聚合省级数据
# (a) 省级房价：人口加权平均
# (b) 省级总人口：汇总（注意：城市数据库覆盖了全部地级市，人口汇总接近省总人口）
prov_hp = df_panel.loc[df_panel['house_price'].notna()].copy()
prov_hp_agg = prov_hp.groupby(['province', 'year']).apply(
    lambda g: pd.Series({
        'avg_house_price': np.average(g['house_price'], weights=g['pop_10k'].fillna(1)),
        'n_cities_hp': g['house_price'].notna().sum(),
    })
).reset_index()

# 省级总人口（从城市面板中所有城市汇总，不仅有房价的）
prov_pop_agg = df_panel.groupby(['province', 'year']).agg(
    total_pop_10k=('pop_10k', 'sum'),
    total_gdp_100m=('gdp_100m', 'sum'),
    total_fai_100m=('fai_100m', 'sum'),
).reset_index()

# 合并
prov_agg = prov_hp_agg.merge(prov_pop_agg, on=['province', 'year'], how='outer')

# 清洗省份名用于匹配
prov_agg['province_clean'] = prov_agg['province'].str.replace(
    '省$|市$|自治区$|壮族自治区$|回族自治区$|维吾尔自治区$|特别行政区$', '', regex=True
).str.strip()

df_prov['province_clean'] = df_prov['province'].str.strip()

# 匹配
df_prov = df_prov.merge(
    prov_agg[['province_clean', 'year', 'avg_house_price', 'total_pop_10k',
              'total_gdp_100m', 'total_fai_100m']],
    on=['province_clean', 'year'],
    how='left'
)

# 省级 V(t) = 房价 x 省总人口 x 人均面积
# 使用城市面板汇总的人口（覆盖全部地级市，接近实际省人口）
df_prov['per_capita_area_m2'] = df_prov['year'].map(area_lookup)

df_prov['V_billion'] = (
    df_prov['avg_house_price'] *                    # 元/m2
    df_prov['total_pop_10k'] * 10000 *              # 人
    df_prov['per_capita_area_m2'] /                 # m2/人
    1e9                                              # 转换为十亿元
)

# 省级 K(t) 用 PIM
# fai_billion_yuan 已有
def compute_pim_prov(group):
    group = group.sort_values('year').copy()
    fai = group['fai_billion_yuan'].values
    n = len(group)
    K = np.full(n, np.nan)

    valid_idx = np.where(~np.isnan(fai))[0]
    if len(valid_idx) == 0:
        group['K_billion'] = np.nan
        return group

    first_valid = valid_idx[0]
    if len(valid_idx) >= 3:
        early = fai[valid_idx[:5]]
        early = early[early > 0]
        if len(early) >= 2:
            g = np.mean(np.diff(early) / early[:-1])
            g = max(0.02, min(g, 0.30))
        else:
            g = 0.10
    else:
        g = 0.10

    if fai[first_valid] > 0:
        K[first_valid] = fai[first_valid] / (g + DELTA)
    else:
        K[first_valid] = 0

    for i in range(first_valid + 1, n):
        if np.isnan(K[i-1]):
            if not np.isnan(fai[i]) and fai[i] > 0:
                K[i] = fai[i] / (g + DELTA)
            continue
        inv = fai[i] if not np.isnan(fai[i]) else 0
        K[i] = K[i-1] * (1 - DELTA) + inv

    group['K_billion'] = K
    return group

df_prov = df_prov.groupby('province', group_keys=False).apply(compute_pim_prov)

# 省级 Urban Q
df_prov['urban_q'] = df_prov['V_billion'] / df_prov['K_billion']
df_prov.loc[df_prov['urban_q'] < 0, 'urban_q'] = np.nan
df_prov.loc[df_prov['urban_q'] > 20, 'urban_q'] = np.nan

n_prov_q = df_prov['urban_q'].notna().sum()
print(f"  省级 Urban Q 有效记录: {n_prov_q}")

# ============================================================
# 7. 输出
# ============================================================

print("\n" + "=" * 70)
print("步骤 7：输出数据")
print("=" * 70)

# 城市面板：选择关键列输出
city_out_cols = [
    'year', 'province', 'city', 'city_code', 'region', 'huhuanyong',
    'gdp_100m', 'gdp_primary_100m', 'gdp_secondary_100m', 'gdp_tertiary_100m',
    'primary_share_pct', 'secondary_share_pct', 'tertiary_share_pct',
    'gdp_per_capita', 'gdp_growth_pct',
    'hukou_pop_10k', 'resident_pop_10k', 'urban_pop_10k', 'urbanization_rate_pct',
    'pop_10k',
    'fai_100m', 're_invest_100m', 'res_invest_100m',
    'avg_wage', 'land_area_km2',
    'fiscal_revenue_100m', 'fiscal_expenditure_100m',
    'loan_balance_100m', 'deposit_balance_100m',
    'house_price', 'price_58', 'price_ajk', 'price_source',
    'gov_bond_balance', 'lgfv_bond_balance', 'total_bond_balance',
    'per_capita_area_m2',
    'fai_imputed',
    'V_100m', 'K_100m', 'urban_q',
    'fai_gdp_ratio', 're_gdp_ratio', 'debt_gdp_ratio',
]
# 只保留实际存在的列
city_out_cols = [c for c in city_out_cols if c in df_panel.columns]

df_panel[city_out_cols].to_csv(OUT_CITY, index=False, encoding='utf-8-sig')
print(f"  城市面板已保存: {OUT_CITY}")
print(f"    维度: {df_panel.shape[0]} x {len(city_out_cols)}")

# 省级面板
prov_out_cols = [
    'province', 'province_en', 'year', 'data_type',
    'gdp_billion_yuan', 'urbanization_rate_pct', 'tertiary_share_pct',
    'fai_billion_yuan', 'fai_gdp_ratio',
    'avg_house_price', 'total_pop_10k', 'total_gdp_100m', 'total_fai_100m',
    'per_capita_area_m2',
    'V_billion', 'K_billion', 'urban_q',
    'source',
]
prov_out_cols = [c for c in prov_out_cols if c in df_prov.columns]

df_prov[prov_out_cols].to_csv(OUT_PROV, index=False, encoding='utf-8-sig')
print(f"  省级面板已保存: {OUT_PROV}")
print(f"    维度: {df_prov.shape[0]} x {len(prov_out_cols)}")

# ============================================================
# 8. 数据摘要报告
# ============================================================

print("\n" + "=" * 70)
print("数据摘要报告")
print("=" * 70)

print("\n--- 城市面板概况 ---")
print(f"  总记录数: {len(df_panel)}")
print(f"  城市数: {df_panel['city'].nunique()}")
print(f"  年份范围: {df_panel['year'].min()} - {df_panel['year'].max()}")

print("\n--- 关键变量覆盖率 ---")
for col, label in [
    ('gdp_100m', 'GDP'),
    ('fai_100m', '固定资产投资'),
    ('re_invest_100m', '房地产投资'),
    ('house_price', '房价'),
    ('resident_pop_10k', '常住人口'),
    ('urbanization_rate_pct', '城镇化率'),
    ('total_bond_balance', '债务余额'),
    ('V_100m', '市场价值 V'),
    ('K_100m', '资本存量 K'),
    ('urban_q', 'Urban Q'),
]:
    if col in df_panel.columns:
        n_valid = df_panel[col].notna().sum()
        pct = n_valid / len(df_panel) * 100
        n_city = df_panel.loc[df_panel[col].notna(), 'city'].nunique()
        print(f"  {label:12s}: {n_valid:6d} 记录 ({pct:5.1f}%), {n_city:3d} 城市")

print("\n--- Urban Q 描述统计（有房价年份，2010-2024）---")
q_valid = df_panel.loc[df_panel['urban_q'].notna() & (df_panel['year'] >= 2010)]
if len(q_valid) > 0:
    print(f"  有效记录: {len(q_valid)}, 城市数: {q_valid['city'].nunique()}")
    print(f"  Urban Q: mean={q_valid['urban_q'].mean():.3f}, "
          f"median={q_valid['urban_q'].median():.3f}, "
          f"sd={q_valid['urban_q'].std():.3f}")
    print(f"           min={q_valid['urban_q'].min():.3f}, "
          f"max={q_valid['urban_q'].max():.3f}, "
          f"P25={q_valid['urban_q'].quantile(0.25):.3f}, "
          f"P75={q_valid['urban_q'].quantile(0.75):.3f}")

    # 按年份统计
    print("\n  按年份 Urban Q 均值:")
    for yr in sorted(q_valid['year'].unique()):
        sub = q_valid[q_valid['year'] == yr]
        print(f"    {yr}: mean={sub['urban_q'].mean():.3f}, n={len(sub)}")

    # 按地域统计
    print("\n  按地域 Urban Q 均值（全部年份）:")
    for region in sorted(q_valid['region'].dropna().unique()):
        sub = q_valid[q_valid['region'] == region]
        print(f"    {region}: mean={sub['urban_q'].mean():.3f}, n={len(sub)}")

    # Top/Bottom 城市（2020年）
    q2020 = q_valid[q_valid['year'] == 2020].sort_values('urban_q', ascending=False)
    if len(q2020) > 0:
        print(f"\n  2020年 Urban Q Top 10:")
        for _, row in q2020.head(10).iterrows():
            print(f"    {row['city']:8s}: Q={row['urban_q']:.3f}, "
                  f"房价={row['house_price']:.0f}元/m2, GDP={row['gdp_100m']:.0f}亿")
        print(f"\n  2020年 Urban Q Bottom 10:")
        for _, row in q2020.tail(10).iterrows():
            print(f"    {row['city']:8s}: Q={row['urban_q']:.3f}, "
                  f"房价={row['house_price']:.0f}元/m2, GDP={row['gdp_100m']:.0f}亿")

print("\n--- 省级 Urban Q 概况 ---")
pq = df_prov.loc[df_prov['urban_q'].notna()]
if len(pq) > 0:
    print(f"  有效记录: {len(pq)}, 省份数: {pq['province'].nunique()}")
    print(f"  Urban Q: mean={pq['urban_q'].mean():.3f}, median={pq['urban_q'].median():.3f}")

print("\n--- 数据来源声明 ---")
print("  [1] 中国城市数据库6.0版 (马克数据网), 1990-2023, 线性插值版")
print("  [2] 58同城房价数据, 2010-2024")
print("  [3] 安居客房价数据, 2015-2024")
print("  [4] 地级市债务数据 (地方政府债+城投债), 2006-2023")
print("  [5] 省级数据 (中国统计年鉴), 2005-2023")
print("  [6] 人均住房面积: 基于第七次人口普查(2020年41.76m2/人)的线性插值")

print("\n完成!")
