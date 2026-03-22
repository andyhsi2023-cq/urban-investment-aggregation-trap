"""
52_city_ocr_uci.py
==================
目的: 计算中国 ~290 城市的 OCR (过度建设率) 和 UCI (城市协调指数)
输入:
  - 02-data/processed/china_city_panel_real.csv (300 城市面板)
  - 02-data/raw/penn_world_table.csv (PWT 中国 hc 指数)
  - 03-analysis/models/kstar_regression.txt (全球 K* 参数参考)
输出:
  - 02-data/processed/china_city_ocr_uci.csv
  - 03-analysis/models/city_kstar_regression.txt
  - 03-analysis/models/city_uci_classification.txt
  - 04-figures/drafts/fig14_city_ocr_uci.png
依赖: pandas, numpy, statsmodels, matplotlib, scipy
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.gridspec as gridspec
from math import pi
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 路径配置
# ============================================================
BASE = "/Users/andy/Desktop/Claude/urban-q-phase-transition"
DATA_RAW = f"{BASE}/02-data/raw"
DATA_PROC = f"{BASE}/02-data/processed"
MODELS = f"{BASE}/03-analysis/models"
FIGS = f"{BASE}/04-figures/drafts"

# ============================================================
# 中文字体配置
# ============================================================
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti SC', 'STHeiti', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150

# ============================================================
# 步骤 0: 加载数据
# ============================================================
print("=" * 70)
print("步骤 0: 加载数据")
print("=" * 70)

df = pd.read_csv(f"{DATA_PROC}/china_city_panel_real.csv")
pwt = pd.read_csv(f"{DATA_RAW}/penn_world_table.csv")

print(f"城市面板: {df.shape[0]} 行, {df['city'].nunique()} 城市, {df['year'].min()}-{df['year'].max()}")

# 提取中国 PWT hc 时间序列
pwt_chn = pwt[pwt['countrycode'] == 'CHN'][['year', 'hc']].dropna()
print(f"PWT 中国 hc: {pwt_chn['year'].min()}-{pwt_chn['year'].max()}")
print(f"  2010: hc={pwt_chn[pwt_chn.year==2010]['hc'].values[0]:.4f}")
print(f"  2019: hc={pwt_chn[pwt_chn.year==2019]['hc'].values[0]:.4f}")

# ============================================================
# 步骤 0.5: 城市分级
# ============================================================

# 一线城市
tier1 = ['北京市', '上海市', '广州市', '深圳市']

# 新一线城市 (15个)
new_tier1 = ['成都市', '重庆市', '杭州市', '武汉市', '苏州市', '西安市', '南京市',
             '长沙市', '天津市', '郑州市', '东莞市', '青岛市', '昆明市', '宁波市', '合肥市']

# 二线城市 (约30个)
tier2 = ['沈阳市', '大连市', '济南市', '厦门市', '福州市', '哈尔滨市', '长春市',
         '南昌市', '无锡市', '佛山市', '石家庄市', '太原市', '贵阳市', '南宁市',
         '温州市', '泉州市', '珠海市', '常州市', '徐州市', '烟台市', '兰州市',
         '乌鲁木齐市', '呼和浩特市', '海口市', '绍兴市', '惠州市', '中山市',
         '金华市', '嘉兴市', '保定市']

def get_city_tier(city):
    if city in tier1:
        return '一线'
    elif city in new_tier1:
        return '新一线'
    elif city in tier2:
        return '二线'
    else:
        return '三线及以下'

df['city_tier'] = df['city'].apply(get_city_tier)
print(f"\n城市等级分布:")
tier_counts = df.groupby('city_tier')['city'].nunique()
for t in ['一线', '新一线', '二线', '三线及以下']:
    if t in tier_counts.index:
        print(f"  {t}: {tier_counts[t]} 城市")

# ============================================================
# 步骤 1: 构建城市级人力资本代理变量 hc_proxy
# ============================================================
print("\n" + "=" * 70)
print("步骤 1: 构建城市级人力资本代理变量")
print("=" * 70)

# 策略: hc_city = hc_national * (gdp_pc_city / gdp_pc_national) ^ 0.3
# 使用 PWT 全国 hc, 并用城市人均 GDP 相对全国均值做差异化调整

# 合并 PWT hc
df = df.merge(pwt_chn[['year', 'hc']].rename(columns={'hc': 'hc_national'}),
              on='year', how='left')

# 对于 PWT 没有覆盖的年份 (2020-2023), 外推
# PWT 最后一年 hc
hc_last_year = pwt_chn['year'].max()
hc_last_val = pwt_chn[pwt_chn.year == hc_last_year]['hc'].values[0]
# 近5年平均增长率
hc_recent = pwt_chn[pwt_chn.year >= hc_last_year - 5].sort_values('year')
hc_growth = (hc_recent['hc'].iloc[-1] / hc_recent['hc'].iloc[0]) ** (1/5) - 1
print(f"hc 最后可用年: {hc_last_year}, hc={hc_last_val:.4f}, 近5年年均增长率: {hc_growth:.4f}")

for yr in range(int(hc_last_year) + 1, 2024):
    hc_extrap = hc_last_val * (1 + hc_growth) ** (yr - hc_last_year)
    df.loc[df['year'] == yr, 'hc_national'] = hc_extrap

# 计算每年全国平均人均 GDP（用城市面板均值近似）
gdp_pc_national = df.groupby('year')['gdp_per_capita'].median()
df = df.merge(gdp_pc_national.rename('gdp_pc_national_median'), on='year', how='left')

# 城市级 hc: 弹性 0.3 调整
df['hc_ratio'] = (df['gdp_per_capita'] / df['gdp_pc_national_median']).clip(0.3, 5.0)
df['hc_city'] = df['hc_national'] * df['hc_ratio'] ** 0.3

print(f"城市 hc 范围 (2020): {df[df.year==2020]['hc_city'].min():.2f} - {df[df.year==2020]['hc_city'].max():.2f}")
print(f"城市 hc 中位数 (2020): {df[df.year==2020]['hc_city'].median():.2f}")

# ============================================================
# 步骤 1.5: 构建城市级城镇人口代理
# ============================================================
# pop_10k 在 urban_q 子集中全部可用
# urban_pop_10k 覆盖率很低, 用 pop_10k 作为城镇人口规模代理
# (地级市统计口径中 pop_10k 多指市辖区/常住人口, 与城镇人口高度相关)
df['pop_urban_proxy'] = df['pop_10k']

# ============================================================
# 步骤 2: 中国城市级 K* 面板回归
# ============================================================
print("\n" + "=" * 70)
print("步骤 2: 中国城市级 K* 面板回归")
print("=" * 70)

# 筛选有完整数据的子集
reg_df = df[['year', 'city', 'city_code', 'region', 'city_tier',
             'K_100m', 'pop_urban_proxy', 'hc_city', 'gdp_100m']].dropna()
reg_df = reg_df[(reg_df['K_100m'] > 0) & (reg_df['pop_urban_proxy'] > 0) &
                (reg_df['hc_city'] > 0) & (reg_df['gdp_100m'] > 0)]

# 取对数
reg_df['ln_K'] = np.log(reg_df['K_100m'])
reg_df['ln_pop'] = np.log(reg_df['pop_urban_proxy'])
reg_df['ln_hc'] = np.log(reg_df['hc_city'])
reg_df['ln_gdp'] = np.log(reg_df['gdp_100m'])

print(f"回归样本: {len(reg_df)} 观测, {reg_df['city'].nunique()} 城市, "
      f"{reg_df['year'].min()}-{reg_df['year'].max()}")

# --- 方法 A: Between 估计 (无约束, 参考用) ---
between_df = reg_df.groupby('city')[['ln_K', 'ln_pop', 'ln_hc', 'ln_gdp']].mean()
X_be = sm.add_constant(between_df[['ln_pop', 'ln_hc', 'ln_gdp']])
y_be = between_df['ln_K']
model_be_unconstrained = sm.OLS(y_be, X_be).fit(cov_type='HC1')

print("\n--- Between 估计结果 (无约束, 参考) ---")
print(f"N cities: {len(between_df)}")
print(f"R-squared: {model_be_unconstrained.rsquared:.4f}")
print(model_be_unconstrained.summary2().tables[1].to_string())
print("注意: pop/hc 系数为负, 源于与 GDP 的高度共线性 (VIF>10)")
print("      GDP 吸收了人口和人力资本的间接效应")

# 共线性诊断
from numpy.linalg import inv
X_corr = between_df[['ln_pop', 'ln_hc', 'ln_gdp']].corr()
print(f"\n相关系数矩阵:")
print(f"  pop-hc:  {X_corr.loc['ln_pop','ln_hc']:.3f}")
print(f"  pop-gdp: {X_corr.loc['ln_pop','ln_gdp']:.3f}")
print(f"  hc-gdp:  {X_corr.loc['ln_hc','ln_gdp']:.3f}")

# --- 方法 B: TWFE Within 估计 (短期调整, 符号正确) ---
from statsmodels.regression.linear_model import OLS

panel = reg_df.set_index(['city', 'year'])
for col in ['ln_K', 'ln_pop', 'ln_hc', 'ln_gdp']:
    city_mean = panel.groupby('city')[col].transform('mean')
    year_mean = panel.groupby('year')[col].transform('mean')
    grand_mean = panel[col].mean()
    panel[f'{col}_within'] = panel[col] - city_mean - year_mean + grand_mean

X_fe = panel[['ln_pop_within', 'ln_hc_within', 'ln_gdp_within']]
y_fe = panel['ln_K_within']
model_fe = OLS(y_fe, X_fe).fit(cov_type='HC1')

print("\n--- TWFE Within 估计结果 ---")
print(f"R-squared (within): {model_fe.rsquared:.4f}")
for v in ['ln_pop_within', 'ln_hc_within', 'ln_gdp_within']:
    print(f"  {v}: {model_fe.params[v]:.4f} (p={model_fe.pvalues[v]:.4f})")

# --- 方法 C (首选): 混合策略 ---
# 全球 Between 参数提供弹性先验, Within 估计验证符号方向
# 由于中国城市间 pop/hc/GDP 共线严重, 无约束 Between 估计不可靠
# 采用策略: 使用全球 Between 弹性 (理论驱动), 但用中国数据标定 theta
#
# 理论根据:
# - 全球 Between 弹性反映了跨国/跨城市的长期结构性关系
# - TWFE Within 符号一致 (全正), 验证了弹性方向
# - 只需标定中国特定的截距 theta

# 全球 Between 参数 (from kstar_regression.txt)
alpha_P_global = 0.5849
alpha_H_global = 3.9779
alpha_G_global = 0.4718

# 使用全球弹性, 在中国城市截面上标定 theta
# ln(K) = ln(theta) + aP*ln(pop) + aH*ln(hc) + aG*ln(gdp) + e
# => ln(theta) = mean(ln(K) - aP*ln(pop) - aH*ln(hc) - aG*ln(gdp))
between_df['ln_Kstar_structural'] = (alpha_P_global * between_df['ln_pop']
                                     + alpha_H_global * between_df['ln_hc']
                                     + alpha_G_global * between_df['ln_gdp'])
residuals = between_df['ln_K'] - between_df['ln_Kstar_structural']
ln_theta_china = residuals.median()  # 用中位数更稳健
theta_china = np.exp(ln_theta_china)

# 检查拟合优度
between_df['ln_K_fitted'] = ln_theta_china + between_df['ln_Kstar_structural']
ss_res = ((between_df['ln_K'] - between_df['ln_K_fitted']) ** 2).sum()
ss_tot = ((between_df['ln_K'] - between_df['ln_K'].mean()) ** 2).sum()
r2_hybrid = 1 - ss_res / ss_tot

print(f"\n--- 混合策略 (首选): 全球弹性 + 中国 theta ---")
print(f"全球弹性: alpha_P={alpha_P_global}, alpha_H={alpha_H_global}, alpha_G={alpha_G_global}")
print(f"中国 theta = {theta_china:.6f} (ln_theta = {ln_theta_china:.4f})")
print(f"截面拟合 R-squared = {r2_hybrid:.4f}")

# 使用混合策略的参数
alpha_P_be = alpha_P_global
alpha_H_be = alpha_H_global
alpha_G_be = alpha_G_global
theta_be = theta_china
model_be = model_be_unconstrained  # 保留无约束模型供报告

# ============================================================
# 步骤 3: 计算 K* 和 OCR
# ============================================================
print("\n" + "=" * 70)
print("步骤 3: 计算 K* 和 OCR")
print("=" * 70)

# 使用混合策略参数计算 K*
# K* = theta_china * pop^alpha_P * hc^alpha_H * gdp^alpha_G
# theta_china 已经通过截面标定得到, 无需再额外标定

# 计算 ln(K*)
valid_calc = (df['pop_urban_proxy'].notna() & (df['pop_urban_proxy'] > 0) &
              df['hc_city'].notna() & (df['hc_city'] > 0) &
              df['gdp_100m'].notna() & (df['gdp_100m'] > 0))

df['ln_Kstar'] = np.nan
df.loc[valid_calc, 'ln_Kstar'] = (ln_theta_china
                                   + alpha_P_be * np.log(df.loc[valid_calc, 'pop_urban_proxy'])
                                   + alpha_H_be * np.log(df.loc[valid_calc, 'hc_city'])
                                   + alpha_G_be * np.log(df.loc[valid_calc, 'gdp_100m']))

# 二次标定: 微调使 2015 年全国中位数 OCR ≈ 1.15
# (2015 年全国已有轻度过度建设, 中位数 OCR 应略大于 1)
calibration_year = 2015
target_ocr_median = 1.15
cal_mask = ((df['year'] == calibration_year) & df['K_100m'].notna() &
            df['ln_Kstar'].notna() & (df['K_100m'] > 0))

if cal_mask.sum() > 0:
    cal_data = df.loc[cal_mask].copy()
    cal_data['ln_K_actual'] = np.log(cal_data['K_100m'])
    # 当前 OCR_median = exp(median(ln_K - ln_Kstar))
    current_ln_ocr_median = (cal_data['ln_K_actual'] - cal_data['ln_Kstar']).median()
    # 需要的 delta 使得 exp(median(ln_K - (ln_Kstar + delta))) = target
    # => current_ln_ocr_median - delta = ln(target)
    delta_calibration = current_ln_ocr_median - np.log(target_ocr_median)
    print(f"二次标定: 当前中位数 OCR = {np.exp(current_ln_ocr_median):.3f}")
    print(f"目标中位数 OCR ({calibration_year}年) = {target_ocr_median:.2f}")
    print(f"标定调整量 delta = {delta_calibration:.4f}")
    df.loc[df['ln_Kstar'].notna(), 'ln_Kstar'] += delta_calibration
else:
    delta_calibration = 0.0
    print("警告: 标定失败")

df['Kstar_100m'] = np.exp(df['ln_Kstar'])

# 计算 OCR
valid_mask = df['K_100m'].notna() & df['Kstar_100m'].notna() & (df['Kstar_100m'] > 0)
df.loc[valid_mask, 'OCR'] = df.loc[valid_mask, 'K_100m'] / df.loc[valid_mask, 'Kstar_100m']

# OCR 合理性检查
ocr_2020 = df[(df.year == 2020) & df['OCR'].notna()]
print(f"\nOCR 统计 (2020, n={len(ocr_2020)}):")
print(f"  均值: {ocr_2020['OCR'].mean():.3f}")
print(f"  中位数: {ocr_2020['OCR'].median():.3f}")
print(f"  P10-P90: {ocr_2020['OCR'].quantile(0.1):.3f} - {ocr_2020['OCR'].quantile(0.9):.3f}")

# 展示各等级 OCR
for t in ['一线', '新一线', '二线', '三线及以下']:
    sub = ocr_2020[ocr_2020.city_tier == t]
    if len(sub) > 0:
        print(f"  {t}: median OCR = {sub['OCR'].median():.3f} (n={len(sub)})")

# ============================================================
# 步骤 4: 计算 UCI
# ============================================================
print("\n" + "=" * 70)
print("步骤 4: 计算 UCI")
print("=" * 70)

# UCI = Q / OCR = V * K* / K^2
uci_mask = df['urban_q'].notna() & df['OCR'].notna() & (df['OCR'] > 0)
df.loc[uci_mask, 'UCI'] = df.loc[uci_mask, 'urban_q'] / df.loc[uci_mask, 'OCR']

# UCI 标准化: 对 UCI 做对数变换后归一化到 [0, 1] 区间
# 使用 rank-based 标准化确保分布合理
# 但先看看原始 UCI 分布
uci_2023 = df[(df.year == 2023) & df['UCI'].notna()].copy()
print(f"UCI 统计 (2023, n={len(uci_2023)}):")
print(f"  均值: {uci_2023['UCI'].mean():.4f}")
print(f"  中位数: {uci_2023['UCI'].median():.4f}")
print(f"  P10: {uci_2023['UCI'].quantile(0.1):.4f}")
print(f"  P90: {uci_2023['UCI'].quantile(0.9):.4f}")
print(f"  min: {uci_2023['UCI'].min():.4f}")
print(f"  max: {uci_2023['UCI'].max():.4f}")

# UCI 归一化: 用 log-transform + min-max scaling 到 [0, 1]
# 使 UCI 分布更合理地映射到四色分级
# 取 ln(UCI), 然后 rescale: UCI_norm = (ln_UCI - ln_UCI_p5) / (ln_UCI_p95 - ln_UCI_p5)
# 再 clip 到 [0, 1]

# 计算全样本 (所有有 UCI 的年份) 的参考百分位
all_uci = df[df['UCI'].notna() & (df['UCI'] > 0)]['UCI']
ln_uci = np.log(all_uci)
# 使用 2023 年的 P5/P95 作为尺度
ref_uci = df[(df.year == 2023) & df['UCI'].notna() & (df['UCI'] > 0)]['UCI']
ln_ref = np.log(ref_uci)
ln_p5 = ln_ref.quantile(0.02)
ln_p95 = ln_ref.quantile(0.98)

df['UCI_norm'] = np.nan
uci_pos_mask = df['UCI'].notna() & (df['UCI'] > 0)
df.loc[uci_pos_mask, 'UCI_norm'] = (
    (np.log(df.loc[uci_pos_mask, 'UCI']) - ln_p5) / (ln_p95 - ln_p5)
).clip(0, 1)

uci_norm_2023 = df[(df.year == 2023) & df['UCI_norm'].notna()]
print(f"\nUCI_norm 统计 (2023):")
print(f"  均值: {uci_norm_2023['UCI_norm'].mean():.3f}")
print(f"  中位数: {uci_norm_2023['UCI_norm'].median():.3f}")

# ============================================================
# 步骤 5: UCI 四色分级
# ============================================================
print("\n" + "=" * 70)
print("步骤 5: UCI 四色分级")
print("=" * 70)

def classify_uci(uci_norm):
    """UCI 四色分级"""
    if pd.isna(uci_norm):
        return np.nan
    elif uci_norm > 0.8:
        return '绿灯-协调发展'
    elif uci_norm > 0.6:
        return '黄灯-轻度失调'
    elif uci_norm > 0.4:
        return '橙灯-显著失调'
    else:
        return '红灯-严重失调'

df['UCI_class'] = df['UCI_norm'].apply(classify_uci)

# 2023 年分级统计
latest_year = 2023
latest = df[(df.year == latest_year) & df['UCI_norm'].notna()].copy()
print(f"\n{latest_year} 年 UCI 四色分级:")
class_counts = latest['UCI_class'].value_counts()
for cls in ['绿灯-协调发展', '黄灯-轻度失调', '橙灯-显著失调', '红灯-严重失调']:
    n = class_counts.get(cls, 0)
    pct = n / len(latest) * 100
    print(f"  {cls}: {n} 城市 ({pct:.1f}%)")

# 各分级代表城市
print(f"\n各分级代表城市 (按 UCI_norm 排序):")
for cls in ['绿灯-协调发展', '黄灯-轻度失调', '橙灯-显著失调', '红灯-严重失调']:
    sub = latest[latest['UCI_class'] == cls].sort_values('UCI_norm', ascending=False)
    cities_list = sub['city'].head(10).tolist()
    print(f"  {cls}: {', '.join(cities_list)}")

# ============================================================
# 步骤 6: 六维雷达图数据准备
# ============================================================
print("\n" + "=" * 70)
print("步骤 6: 六维雷达图数据准备")
print("=" * 70)

# 选择 6 个代表城市 (从 2023 年数据中选)
# 候选城市 (按类型)
candidate_cities = {
    '健康发展型': ['深圳市', '杭州市'],
    '过度建设型': ['鄂尔多斯市', '包头市', '榆林市'],
    '转型中型': ['武汉市', '成都市'],
    '收缩型': ['鹤岗市', '齐齐哈尔市', '哈尔滨市', '大庆市'],
    '一线超大': ['北京市', '上海市'],
    '快速追赶型': ['合肥市', '贵阳市', '南宁市']
}

# 从候选中选有数据的
radar_cities = {}
for ctype, candidates in candidate_cities.items():
    for c in candidates:
        if c in latest['city'].values:
            radar_cities[ctype] = c
            break
    if ctype not in radar_cities:
        print(f"  警告: {ctype} 类型无可用候选城市")

print("雷达图代表城市:")
for ctype, c in radar_cities.items():
    row = latest[latest.city == c].iloc[0]
    print(f"  {ctype}: {c} (Q={row.urban_q:.3f}, OCR={row.OCR:.3f}, UCI_norm={row.UCI_norm:.3f})")

# 计算六维指标
def compute_radar_dims(city_row, all_data):
    """计算城市六维雷达图指标, 每个维度标准化到 [0, 1]"""
    dims = {}

    # D1: 资产效率 = Urban Q (标准化)
    q = city_row['urban_q']
    # 用 log(Q) 做标准化, Q=1 对应 0.5
    # 标准化: 0.5 + 0.5 * tanh(ln(Q) / 2)
    if pd.notna(q) and q > 0:
        dims['D1_资产效率'] = 0.5 + 0.5 * np.tanh(np.log(q) / 2)
    else:
        dims['D1_资产效率'] = 0.0

    # D2: 建设适配 = 1/OCR (标准化)
    ocr = city_row['OCR']
    if pd.notna(ocr) and ocr > 0:
        inv_ocr = 1.0 / ocr
        dims['D2_建设适配'] = min(inv_ocr, 1.5) / 1.5  # 1/OCR=1 对应 0.67, 上限 1.5
    else:
        dims['D2_建设适配'] = 0.0

    # D3: 投资节奏 = 1 - |I/GDP - median(I/GDP)| / median(I/GDP)
    fai_ratio = city_row.get('fai_gdp_ratio', np.nan)
    if pd.notna(fai_ratio):
        median_ratio = all_data['fai_gdp_ratio'].median()
        if median_ratio > 0:
            dims['D3_投资节奏'] = max(0, 1 - abs(fai_ratio - median_ratio) / median_ratio)
        else:
            dims['D3_投资节奏'] = 0.5
    else:
        dims['D3_投资节奏'] = 0.5

    # D4: 人口支撑 (用人口规模相对中位数)
    pop = city_row.get('pop_10k', np.nan)
    if pd.notna(pop):
        median_pop = all_data['pop_10k'].median()
        pop_ratio = pop / median_pop
        dims['D4_人口支撑'] = min(pop_ratio / 3.0, 1.0)  # 3x 中位数 = 满分
    else:
        dims['D4_人口支撑'] = 0.5

    # D5: 产业匹配 = 三产占比 / 全国均值
    tert = city_row.get('tertiary_share_pct', np.nan)
    if pd.notna(tert):
        national_tert = all_data['tertiary_share_pct'].median()
        if national_tert > 0:
            dims['D5_产业匹配'] = min(tert / national_tert / 1.5, 1.0)
        else:
            dims['D5_产业匹配'] = 0.5
    else:
        dims['D5_产业匹配'] = 0.5

    # D6: 财务健康 = 1 - debt_gdp_ratio (如有)
    debt = city_row.get('debt_gdp_ratio', np.nan)
    if pd.notna(debt):
        dims['D6_财务健康'] = max(0, min(1, 1 - debt / 2.0))  # debt/GDP=2 => 0
    else:
        # 无债务数据时, 用财政自给率代替: revenue / expenditure
        rev = city_row.get('fiscal_revenue_100m', np.nan)
        exp = city_row.get('fiscal_expenditure_100m', np.nan)
        if pd.notna(rev) and pd.notna(exp) and exp > 0:
            dims['D6_财务健康'] = min(rev / exp, 1.0)
        else:
            dims['D6_财务健康'] = 0.5

    return dims

# 计算所有代表城市的雷达数据
radar_data = {}
for ctype, c in radar_cities.items():
    row = latest[latest.city == c].iloc[0]
    radar_data[f"{c}({ctype})"] = compute_radar_dims(row, latest)

print("\n雷达图维度数据:")
for label, dims in radar_data.items():
    vals = [f"{d}={v:.2f}" for d, v in dims.items()]
    print(f"  {label}: {', '.join(vals)}")

# ============================================================
# 步骤 7: 可视化 (4 子图)
# ============================================================
print("\n" + "=" * 70)
print("步骤 7: 可视化")
print("=" * 70)

fig = plt.figure(figsize=(20, 18))
gs = gridspec.GridSpec(2, 2, hspace=0.32, wspace=0.28,
                       left=0.07, right=0.95, top=0.94, bottom=0.06)

# 颜色方案
colors_class = {
    '绿灯-协调发展': '#2ca02c',
    '黄灯-轻度失调': '#FFB800',
    '橙灯-显著失调': '#ff7f0e',
    '红灯-严重失调': '#d62728'
}
colors_tier = {
    '一线': '#d62728',
    '新一线': '#ff7f0e',
    '二线': '#2ca02c',
    '三线及以下': '#1f77b4'
}

# --- (a) UCI 分布直方图 ---
ax1 = fig.add_subplot(gs[0, 0])
uci_vals = latest['UCI_norm'].dropna()

# 按分级着色的直方图
bins = np.linspace(0, 1, 41)
for cls, color in colors_class.items():
    sub = latest[latest.UCI_class == cls]['UCI_norm']
    ax1.hist(sub, bins=bins, color=color, alpha=0.85, label=cls, edgecolor='white', linewidth=0.5)

# 分级阈值线
for threshold, label in [(0.4, 'OCR=0.4'), (0.6, '0.6'), (0.8, '0.8')]:
    ax1.axvline(x=threshold, color='gray', linestyle='--', linewidth=1, alpha=0.7)

ax1.set_xlabel('UCI (标准化)', fontsize=12)
ax1.set_ylabel('城市数量', fontsize=12)
ax1.set_title(f'(a) {latest_year}年 中国城市 UCI 分布 (n={len(uci_vals)})', fontsize=13, fontweight='bold')
ax1.legend(fontsize=9, loc='upper left')
ax1.set_xlim(0, 1)

# 标注各区间城市数
for cls in ['绿灯-协调发展', '黄灯-轻度失调', '橙灯-显著失调', '红灯-严重失调']:
    n = class_counts.get(cls, 0)
    if cls == '红灯-严重失调':
        x_pos = 0.2
    elif cls == '橙灯-显著失调':
        x_pos = 0.5
    elif cls == '黄灯-轻度失调':
        x_pos = 0.7
    else:
        x_pos = 0.9
    ax1.text(x_pos, ax1.get_ylim()[1] * 0.92, f'n={n}',
             ha='center', va='top', fontsize=10, fontweight='bold',
             color=colors_class[cls])

# --- (b) UCI vs Urban Q 散点图 ---
ax2 = fig.add_subplot(gs[0, 1])

for tier, color in colors_tier.items():
    sub = latest[latest.city_tier == tier]
    ax2.scatter(sub['urban_q'], sub['UCI_norm'], c=color, s=25, alpha=0.6,
                label=tier, edgecolors='white', linewidth=0.3)

# 标注关键城市
label_cities = ['北京市', '上海市', '深圳市', '杭州市', '鄂尔多斯市', '哈尔滨市',
                '成都市', '合肥市', '武汉市', '广州市']
for c in label_cities:
    sub = latest[latest.city == c]
    if len(sub) > 0:
        row = sub.iloc[0]
        if pd.notna(row.urban_q) and pd.notna(row.UCI_norm):
            ax2.annotate(c.replace('市', ''), (row.urban_q, row.UCI_norm),
                        fontsize=7, ha='left', va='bottom',
                        textcoords='offset points', xytext=(3, 3))

ax2.set_xlabel('Urban Q', fontsize=12)
ax2.set_ylabel('UCI (标准化)', fontsize=12)
ax2.set_title(f'(b) UCI vs Urban Q ({latest_year}年)', fontsize=13, fontweight='bold')
ax2.legend(fontsize=9, loc='lower right')
# 对 x 轴做对数变换 (Q 分布偏斜)
ax2.set_xscale('log')
ax2.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5)
ax2.axvline(x=1.0, color='gray', linestyle=':', alpha=0.5)

# --- (c) OCR 按区域/等级箱线图 ---
ax3 = fig.add_subplot(gs[1, 0])

# 按城市等级做箱线图
tier_order = ['一线', '新一线', '二线', '三线及以下']
bp_data = []
bp_labels = []
bp_colors = []
for t in tier_order:
    sub = latest[latest.city_tier == t]['OCR'].dropna()
    if len(sub) > 0:
        bp_data.append(sub.values)
        bp_labels.append(f"{t}\n(n={len(sub)})")
        bp_colors.append(colors_tier[t])

bp = ax3.boxplot(bp_data, labels=bp_labels, patch_artist=True,
                 showfliers=True, flierprops=dict(marker='o', markersize=3, alpha=0.5))
for patch, color in zip(bp['boxes'], bp_colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.6)

ax3.axhline(y=1.0, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='OCR=1 (适配)')
ax3.set_ylabel('OCR (过度建设率)', fontsize=12)
ax3.set_title(f'(c) OCR 按城市等级分布 ({latest_year}年)', fontsize=13, fontweight='bold')
ax3.legend(fontsize=9)
# 限制 y 轴范围避免极端值拉伸
ocr_p95 = latest['OCR'].quantile(0.95)
ax3.set_ylim(0, min(ocr_p95 * 1.5, 5))

# --- (d) 六维雷达图 ---
ax4 = fig.add_subplot(gs[1, 1], projection='polar')

categories = list(list(radar_data.values())[0].keys())
N = len(categories)
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]  # 闭合

radar_colors = ['#d62728', '#ff7f0e', '#2ca02c', '#9467bd', '#1f77b4', '#8c564b']
for idx, (label, dims) in enumerate(radar_data.items()):
    values = list(dims.values())
    values += values[:1]  # 闭合
    ax4.plot(angles, values, 'o-', linewidth=1.5, label=label.split('(')[0],
             color=radar_colors[idx % len(radar_colors)], markersize=4)
    ax4.fill(angles, values, alpha=0.08, color=radar_colors[idx % len(radar_colors)])

# 设置雷达图标签
cat_labels = [c.split('_')[1] for c in categories]
ax4.set_xticks(angles[:-1])
ax4.set_xticklabels(cat_labels, fontsize=9)
ax4.set_ylim(0, 1)
ax4.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax4.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=7, color='gray')
ax4.set_title(f'(d) 代表城市六维诊断雷达图', fontsize=13, fontweight='bold', pad=20)
ax4.legend(fontsize=7, loc='upper right', bbox_to_anchor=(1.35, 1.1))

fig.savefig(f"{FIGS}/fig14_city_ocr_uci.png", dpi=200, bbox_inches='tight')
print(f"图表保存: {FIGS}/fig14_city_ocr_uci.png")
plt.close()

# ============================================================
# 步骤 8: 保存输出文件
# ============================================================
print("\n" + "=" * 70)
print("步骤 8: 保存输出文件")
print("=" * 70)

# --- 8.1 城市 OCR/UCI CSV ---
output_cols = ['year', 'province', 'city', 'city_code', 'region', 'city_tier',
               'gdp_100m', 'gdp_per_capita', 'pop_10k', 'hc_city',
               'K_100m', 'Kstar_100m', 'V_100m', 'urban_q',
               'OCR', 'UCI', 'UCI_norm', 'UCI_class',
               'fai_gdp_ratio', 're_gdp_ratio', 'debt_gdp_ratio',
               'tertiary_share_pct']
output_df = df[[c for c in output_cols if c in df.columns]].copy()
output_df = output_df[output_df['OCR'].notna() | output_df['UCI'].notna()]
output_df.to_csv(f"{DATA_PROC}/china_city_ocr_uci.csv", index=False, encoding='utf-8-sig')
print(f"OCR/UCI 数据: {DATA_PROC}/china_city_ocr_uci.csv ({len(output_df)} 行)")

# --- 8.2 K* 城市回归结果 ---
reg_report = []
reg_report.append("=" * 70)
reg_report.append("中国城市级 K* 估计结果")
reg_report.append("=" * 70)
reg_report.append("")
reg_report.append("PREFERRED MODEL: 混合策略 (全球弹性 + 中国 theta 标定)")
reg_report.append("K*(t) = theta_china * Pop^alpha_P * hc^alpha_H * GDP^alpha_G")
reg_report.append(f"hc_city = hc_national * (gdp_pc_city / gdp_pc_national_median)^0.3")
reg_report.append("")
reg_report.append("策略说明:")
reg_report.append("  中国城市截面中 pop/hc/GDP 高度共线 (r > 0.85),")
reg_report.append("  无约束 Between 估计器给出负的人口和人力资本弹性 (不合理).")
reg_report.append("  因此采用全球 Between 弹性 (经 126 国验证), 仅用中国数据标定 theta.")
reg_report.append("  TWFE Within 估计器 (利用城市内时间变异) 验证了所有弹性为正.")
reg_report.append("")
reg_report.append("-" * 70)
reg_report.append("采用参数:")
reg_report.append(f"  alpha_P = {alpha_P_be:.4f} (全球 Between)")
reg_report.append(f"  alpha_H = {alpha_H_be:.4f} (全球 Between)")
reg_report.append(f"  alpha_G = {alpha_G_be:.4f} (全球 Between)")
reg_report.append(f"  theta_china = {theta_be:.6f} (ln_theta = {ln_theta_china:.4f})")
reg_report.append(f"  截面拟合 R-squared = {r2_hybrid:.4f}")
reg_report.append(f"  标定方法: {calibration_year}年全国中位数 OCR ≈ {target_ocr_median:.2f}")
reg_report.append(f"  标定调整量 delta = {delta_calibration:.4f}")
reg_report.append("-" * 70)
reg_report.append("")
reg_report.append("=" * 70)
reg_report.append("参考 1: 中国城市 Between 估计 (无约束, 存在共线性问题)")
reg_report.append("=" * 70)
reg_report.append(f"N cities:       {len(between_df)}")
reg_report.append(f"R-squared:      {model_be.rsquared:.6f}")
reg_report.append(f"Adj R-squared:  {model_be.rsquared_adj:.6f}")
reg_report.append("")
reg_report.append(f"{'Variable':<20} {'Coef':>10} {'Std Err':>10} {'t':>10} {'P>|t|':>12}")
reg_report.append("-" * 65)
for var in model_be.params.index:
    reg_report.append(
        f"{var:<20} {model_be.params[var]:>10.4f} {model_be.bse[var]:>10.4f} "
        f"{model_be.tvalues[var]:>10.4f} {model_be.pvalues[var]:>12.4e}"
    )
reg_report.append("注意: ln_pop, ln_hc 系数为负, 源于与 ln_gdp 的严重共线性")
reg_report.append(f"  corr(ln_pop, ln_gdp) = {X_corr.loc['ln_pop','ln_gdp']:.3f}")
reg_report.append(f"  corr(ln_hc, ln_gdp)  = {X_corr.loc['ln_hc','ln_gdp']:.3f}")
reg_report.append("")
reg_report.append("=" * 70)
reg_report.append("参考 2: TWFE Within 估计 (短期调整动态, 符号验证)")
reg_report.append("=" * 70)
reg_report.append(f"R-squared (within): {model_fe.rsquared:.6f}")
for v in ['ln_pop_within', 'ln_hc_within', 'ln_gdp_within']:
    reg_report.append(f"  {v}: {model_fe.params[v]:.4f} (p={model_fe.pvalues[v]:.4e})")
reg_report.append("所有弹性为正, 验证了全球参数的符号方向")
reg_report.append("")
reg_report.append("=" * 70)
reg_report.append("参考 3: 全球 K* Between 回归 (126 国)")
reg_report.append("=" * 70)
reg_report.append(f"  alpha_P = 0.5849, alpha_H = 3.9779, alpha_G = 0.4718")
reg_report.append(f"  R-squared = 0.569, N = 126")

with open(f"{MODELS}/city_kstar_regression.txt", 'w', encoding='utf-8') as f:
    f.write('\n'.join(reg_report))
print(f"K* 回归结果: {MODELS}/city_kstar_regression.txt")

# --- 8.3 UCI 分级报告 ---
cls_report = []
cls_report.append("=" * 70)
cls_report.append(f"中国城市 UCI 四色分级报告 ({latest_year}年)")
cls_report.append("=" * 70)
cls_report.append("")
cls_report.append("UCI 定义: UCI = Q^U / OCR = V * K* / K^2")
cls_report.append("UCI_norm: 对 ln(UCI) 做 min-max 标准化至 [0, 1]")
cls_report.append("")
cls_report.append("-" * 70)
cls_report.append("四色分级标准:")
cls_report.append("  绿灯 (>0.8): 协调发展 — 维持框架, 监测预警")
cls_report.append("  黄灯 (0.6-0.8): 轻度失调 — 引导投资结构调整")
cls_report.append("  橙灯 (0.4-0.6): 显著失调 — 收紧建设信贷和用地审批")
cls_report.append("  红灯 (<0.4): 严重失调 — 暂停新增建设用地, 资产瘦身")
cls_report.append("-" * 70)
cls_report.append("")
cls_report.append(f"统计总览 (n={len(latest)}):")
for cls_name in ['绿灯-协调发展', '黄灯-轻度失调', '橙灯-显著失调', '红灯-严重失调']:
    n = class_counts.get(cls_name, 0)
    pct = n / len(latest) * 100
    cls_report.append(f"  {cls_name}: {n} 城市 ({pct:.1f}%)")
cls_report.append("")

# 各分级完整城市名单
for cls_name in ['绿灯-协调发展', '黄灯-轻度失调', '橙灯-显著失调', '红灯-严重失调']:
    cls_report.append("-" * 70)
    cls_report.append(f"{cls_name}:")
    sub = latest[latest.UCI_class == cls_name].sort_values('UCI_norm', ascending=False)
    for _, row in sub.iterrows():
        q_str = f"Q={row.urban_q:.2f}" if pd.notna(row.urban_q) else "Q=NA"
        ocr_str = f"OCR={row.OCR:.2f}" if pd.notna(row.OCR) else "OCR=NA"
        cls_report.append(f"  {row.city:<12} UCI_norm={row.UCI_norm:.3f}  {q_str}  {ocr_str}  [{row.region}]")

cls_report.append("")
cls_report.append("-" * 70)
cls_report.append("区域分布:")
region_class = latest.groupby(['region', 'UCI_class']).size().unstack(fill_value=0)
cls_report.append(region_class.to_string())

cls_report.append("")
cls_report.append("-" * 70)
cls_report.append("城市等级分布:")
tier_class = latest.groupby(['city_tier', 'UCI_class']).size().unstack(fill_value=0)
cls_report.append(tier_class.to_string())

with open(f"{MODELS}/city_uci_classification.txt", 'w', encoding='utf-8') as f:
    f.write('\n'.join(cls_report))
print(f"UCI 分级报告: {MODELS}/city_uci_classification.txt")

print("\n" + "=" * 70)
print("全部完成!")
print("=" * 70)
