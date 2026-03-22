"""
52b_city_real_window.py
======================
目的: 使用严格真实 FAI 数据窗口对中国城市面板进行分析
      FAI 真实数据截止 2016 年。2015-2016 是唯一"双真实"窗口
      （FAI 真实 + 房价覆盖充分），共约 461 个有效观测。

输入:
  - 02-data/processed/china_city_panel_real.csv (300 城市面板)
  - 02-data/processed/global_kstar_m2_panel.csv (M2 弹性 K* 参考)
  - 02-data/raw/penn_world_table.csv (PWT 中国 hc 指数)

输出:
  - 02-data/processed/china_city_real_window.csv
  - 03-analysis/models/city_real_window_report.txt
  - 04-figures/drafts/fig_city_real_window.png

依赖: pandas, numpy, statsmodels, matplotlib, scipy, sklearn
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats
from sklearn.cluster import KMeans
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
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
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti SC', 'STHeiti',
                                    'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150

# 报告缓冲
report_lines = []
def rprint(msg=""):
    """同时打印和记录到报告"""
    print(msg)
    report_lines.append(msg)

# ============================================================
# 步骤 0: 加载数据
# ============================================================
rprint("=" * 70)
rprint("步骤 0: 加载数据")
rprint("=" * 70)

df = pd.read_csv(f"{DATA_PROC}/china_city_panel_real.csv")
global_panel = pd.read_csv(f"{DATA_PROC}/global_kstar_m2_panel.csv")

rprint(f"城市面板: {df.shape[0]} 行, {df['city'].nunique()} 城市, "
       f"{df['year'].min()}-{df['year'].max()}")

# 加载 PWT 用于人力资本代理
try:
    pwt = pd.read_csv(f"{DATA_RAW}/penn_world_table.csv")
    pwt_chn = pwt[pwt['countrycode'] == 'CHN'][['year', 'hc']].dropna()
    has_pwt = True
    rprint(f"PWT 中国 hc: {pwt_chn['year'].min()}-{pwt_chn['year'].max()}")
except FileNotFoundError:
    has_pwt = False
    rprint("警告: PWT 文件不可用, 使用简化 K* 计算")

# ============================================================
# 步骤 0.5: 城市分级与区域划分
# ============================================================
rprint("\n" + "=" * 70)
rprint("步骤 0.5: 城市分级与区域划分")
rprint("=" * 70)

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

# 区域划分: 重新映射为四区域（含东北）
ne_provinces = ['辽宁省', '吉林省', '黑龙江省']
def get_region4(row):
    if row['province'] in ne_provinces:
        return '东北'
    return row['region']

df['region4'] = df.apply(get_region4, axis=1)

rprint("城市等级分布:")
for t in ['一线', '新一线', '二线', '三线及以下']:
    n = df[df['city_tier'] == t]['city'].nunique()
    rprint(f"  {t}: {n} 城市")

rprint("\n区域分布 (四区域):")
for r in ['东部', '中部', '西部', '东北']:
    n = df[df['region4'] == r]['city'].nunique()
    rprint(f"  {r}: {n} 城市")

# ############################################################
# PART A: 数据窗口分层
# ############################################################
rprint("\n" + "#" * 70)
rprint("# PART A: 数据窗口分层")
rprint("#" * 70)

# --- 窗口 1 (Gold Standard): 2015-2016 ---
# FAI 全部真实 (fai_imputed == False) + 房价非空 (urban_q 可计算)
w1_mask = (df['year'].isin([2015, 2016]) &
           (df['fai_imputed'] == False) &
           df['urban_q'].notna())
w1 = df[w1_mask].copy()

rprint(f"\n窗口 1 (Gold Standard): 2015-2016")
rprint(f"  筛选条件: fai_imputed==False & urban_q 非空")
rprint(f"  有效观测: {len(w1)}")
rprint(f"  城市数: {w1['city'].nunique()}")
rprint(f"  年份: {sorted(w1['year'].unique())}")
rprint(f"  Q 统计: mean={w1['urban_q'].mean():.3f}, "
       f"median={w1['urban_q'].median():.3f}")

# --- 窗口 2 (Extended): 2015-2023 ---
# 房价非空 (含估算 FAI)
w2_mask = (df['year'].between(2015, 2023) &
           df['urban_q'].notna())
w2 = df[w2_mask].copy()

rprint(f"\n窗口 2 (Extended): 2015-2023")
rprint(f"  筛选条件: urban_q 非空 (含估算 FAI)")
rprint(f"  有效观测: {len(w2)}")
rprint(f"  城市数: {w2['city'].nunique()}")
rprint(f"  年份: {sorted(w2['year'].unique())}")
rprint(f"  其中 FAI 真实: {(w2['fai_imputed']==False).sum()}")
rprint(f"  其中 FAI 估算: {(w2['fai_imputed']==True).sum()}")

# 按年份细分
rprint("\n  按年份细分:")
for yr in sorted(w2['year'].unique()):
    sub = w2[w2['year'] == yr]
    n_imp = (sub['fai_imputed'] == True).sum()
    rprint(f"    {yr}: {len(sub)} 观测, FAI估算 {n_imp} ({100*n_imp/len(sub):.0f}%)")

# ############################################################
# PART B: 城市 Urban Q 截面分析 (窗口 1)
# ############################################################
rprint("\n" + "#" * 70)
rprint("# PART B: 城市 Urban Q 截面分析 (窗口 1: 2015-2016)")
rprint("#" * 70)

# V = 房价 * PIM 住宅存量 => 已在 V_100m 中计算
# K = FAI 累积的 PIM 资本存量 => 已在 K_100m 中计算
# urban_q = V / K => 已在 urban_q 中计算
# 直接使用面板中预计算的 urban_q

# 按城市取 2015-2016 均值
w1_city = w1.groupby('city').agg({
    'urban_q': 'mean',
    'K_100m': 'mean',
    'V_100m': 'mean',
    'house_price': 'mean',
    'gdp_per_capita': 'mean',
    'gdp_100m': 'mean',
    'pop_10k': 'mean',
    'per_capita_area_m2': 'mean',
    'fai_100m': 'mean',
    'city_tier': 'first',
    'region4': 'first',
    'province': 'first',
    'fai_gdp_ratio': 'mean',
}).reset_index()

rprint(f"\n城市截面 (2015-2016 均值): {len(w1_city)} 城市")

# --- 按城市等级分组统计 ---
rprint("\n--- 按城市等级分组 ---")
rprint(f"{'等级':<10} {'N':>4} {'Q_mean':>8} {'Q_med':>8} {'Q_p25':>8} "
       f"{'Q_p75':>8} {'Q>1%':>8} {'Q<1%':>8}")
rprint("-" * 70)

tier_order = ['一线', '新一线', '二线', '三线及以下']
for t in tier_order:
    sub = w1_city[w1_city['city_tier'] == t]['urban_q']
    if len(sub) == 0:
        continue
    q_gt1 = (sub > 1).sum() / len(sub) * 100
    q_lt1 = (sub < 1).sum() / len(sub) * 100
    rprint(f"{t:<10} {len(sub):>4} {sub.mean():>8.3f} {sub.median():>8.3f} "
           f"{sub.quantile(0.25):>8.3f} {sub.quantile(0.75):>8.3f} "
           f"{q_gt1:>7.1f}% {q_lt1:>7.1f}%")

# 全样本
all_q = w1_city['urban_q']
rprint(f"{'全部':<10} {len(all_q):>4} {all_q.mean():>8.3f} {all_q.median():>8.3f} "
       f"{all_q.quantile(0.25):>8.3f} {all_q.quantile(0.75):>8.3f} "
       f"{(all_q>1).sum()/len(all_q)*100:>7.1f}% {(all_q<1).sum()/len(all_q)*100:>7.1f}%")

# --- 按区域分组统计 ---
rprint("\n--- 按区域分组 (四区域) ---")
rprint(f"{'区域':<10} {'N':>4} {'Q_mean':>8} {'Q_med':>8} {'Q_p25':>8} "
       f"{'Q_p75':>8} {'Q>1%':>8} {'Q<1%':>8}")
rprint("-" * 70)

for r in ['东部', '中部', '西部', '东北']:
    sub = w1_city[w1_city['region4'] == r]['urban_q']
    if len(sub) == 0:
        continue
    q_gt1 = (sub > 1).sum() / len(sub) * 100
    q_lt1 = (sub < 1).sum() / len(sub) * 100
    rprint(f"{r:<10} {len(sub):>4} {sub.mean():>8.3f} {sub.median():>8.3f} "
           f"{sub.quantile(0.25):>8.3f} {sub.quantile(0.75):>8.3f} "
           f"{q_gt1:>7.1f}% {q_lt1:>7.1f}%")

# Q>1 vs Q<1 城市比例
n_gt1 = (all_q > 1).sum()
n_lt1 = (all_q < 1).sum()
n_eq1 = (all_q == 1).sum()
rprint(f"\n总体: Q>1 的城市 {n_gt1} ({100*n_gt1/len(all_q):.1f}%), "
       f"Q<1 的城市 {n_lt1} ({100*n_lt1/len(all_q):.1f}%)")

# 典型城市
rprint("\nQ 最高 10 个城市:")
top10 = w1_city.nlargest(10, 'urban_q')[['city', 'city_tier', 'region4',
                                          'urban_q', 'house_price', 'K_100m']]
for _, row in top10.iterrows():
    rprint(f"  {row['city']:<10} {row['city_tier']:<8} {row['region4']:<4} "
           f"Q={row['urban_q']:.3f}  房价={row['house_price']:.0f}")

rprint("\nQ 最低 10 个城市:")
bot10 = w1_city.nsmallest(10, 'urban_q')[['city', 'city_tier', 'region4',
                                           'urban_q', 'house_price', 'K_100m']]
for _, row in bot10.iterrows():
    rprint(f"  {row['city']:<10} {row['city_tier']:<8} {row['region4']:<4} "
           f"Q={row['urban_q']:.3f}  房价={row['house_price']:.0f}")

# ############################################################
# PART C: 城市 OCR 计算 (用 M2 弹性)
# ############################################################
rprint("\n" + "#" * 70)
rprint("# PART C: 城市 OCR 计算 (用 M2 弹性)")
rprint("#" * 70)

# --- C.1: 从全球 M2 面板提取中国参数 ---
china_global = global_panel[global_panel['country_name'] == 'China'].copy()
china_2015 = china_global[china_global['year'] == 2015].iloc[0]
china_2016 = china_global[china_global['year'] == 2016].iloc[0]

rprint(f"\n全球 M2 面板 - 中国参数:")
rprint(f"  2015: K_star_m2={china_2015['K_star_m2']:.2e}, "
       f"OCR_m2={china_2015['OCR_m2']:.3f}, GDP_pc={china_2015['GDP_pc']:.0f}, "
       f"Pu={china_2015['Pu']:.0f}")
rprint(f"  2016: K_star_m2={china_2016['K_star_m2']:.2e}, "
       f"OCR_m2={china_2016['OCR_m2']:.3f}, GDP_pc={china_2016['GDP_pc']:.0f}, "
       f"Pu={china_2016['Pu']:.0f}")

# --- C.2: 从全球面板反推 M2 弹性 ---
# K_star_m2 = alpha_P * GDP_pc^alpha_D * Pu
# 取对数: ln(K_star/Pu) = ln(alpha_P) + alpha_D * ln(GDP_pc)
gp = global_panel[(global_panel['K_star_m2'] > 0) &
                   (global_panel['GDP_pc'] > 0) &
                   (global_panel['Pu'] > 0)].copy()
gp['log_kstar_per_pu'] = np.log(gp['K_star_m2'] / gp['Pu'])
gp['log_gdppc'] = np.log(gp['GDP_pc'])
mask_valid = np.isfinite(gp['log_kstar_per_pu']) & np.isfinite(gp['log_gdppc'])
gp_valid = gp[mask_valid]

X_m2 = sm.add_constant(gp_valid['log_gdppc'])
y_m2 = gp_valid['log_kstar_per_pu']
m2_model = sm.OLS(y_m2, X_m2).fit(cov_type='HC1')

alpha_D_m2 = m2_model.params['log_gdppc']
alpha_P_m2 = np.exp(m2_model.params['const'])

rprint(f"\nM2 弹性回归 (全球面板, N={len(gp_valid)}):")
rprint(f"  K*/Pu = {alpha_P_m2:.4f} * GDP_pc^{alpha_D_m2:.4f}")
rprint(f"  R-squared = {m2_model.rsquared:.4f}")
rprint(f"  alpha_D = {alpha_D_m2:.4f} (SE={m2_model.bse['log_gdppc']:.4f}, "
       f"p={m2_model.pvalues['log_gdppc']:.2e})")

# 验证: 用反推参数计算中国 2015 K*
kstar_verify = alpha_P_m2 * (china_2015['GDP_pc'] ** alpha_D_m2) * china_2015['Pu']
rprint(f"\n验证 (中国2015): K*_actual={china_2015['K_star_m2']:.2e}, "
       f"K*_formula={kstar_verify:.2e}, ratio={kstar_verify/china_2015['K_star_m2']:.3f}")

# --- C.3: 构建城市级人力资本代理并计算 K* ---
# 策略: 使用混合方法 (与 52_city_ocr_uci.py 一致)
# 全球弹性参数 (from kstar_regression.txt, 与 52 脚本一致)
alpha_P_global = 0.5849
alpha_H_global = 3.9779
alpha_G_global = 0.4718

rprint(f"\n使用混合策略计算城市 K*:")
rprint(f"  全球弹性: alpha_P={alpha_P_global}, alpha_H={alpha_H_global}, "
       f"alpha_G={alpha_G_global}")

# 构建人力资本代理
if has_pwt:
    df = df.merge(pwt_chn[['year', 'hc']].rename(columns={'hc': 'hc_national'}),
                  on='year', how='left')
    # 外推 PWT 缺失年份
    hc_last_year = pwt_chn['year'].max()
    hc_last_val = pwt_chn[pwt_chn.year == hc_last_year]['hc'].values[0]
    hc_recent = pwt_chn[pwt_chn.year >= hc_last_year - 5].sort_values('year')
    hc_growth = (hc_recent['hc'].iloc[-1] / hc_recent['hc'].iloc[0]) ** (1/5) - 1
    for yr in range(int(hc_last_year) + 1, 2024):
        hc_extrap = hc_last_val * (1 + hc_growth) ** (yr - hc_last_year)
        df.loc[df['year'] == yr, 'hc_national'] = hc_extrap

    # 城市级 hc
    gdp_pc_nat = df.groupby('year')['gdp_per_capita'].median()
    df = df.merge(gdp_pc_nat.rename('gdp_pc_nat_median'), on='year', how='left')
    df['hc_ratio'] = (df['gdp_per_capita'] / df['gdp_pc_nat_median']).clip(0.3, 5.0)
    df['hc_city'] = df['hc_national'] * df['hc_ratio'] ** 0.3
    rprint(f"  人力资本代理: hc_city (PWT + GDP调整)")
else:
    # 无 PWT 时简化: 用 GDP_pc 的幂函数近似
    df['hc_city'] = (df['gdp_per_capita'] / 10000).clip(0.1, 20.0) ** 0.3
    rprint(f"  人力资本代理: 简化 (GDP_pc^0.3)")

# 城镇人口代理
df['pop_urban_proxy'] = df['pop_10k']

# --- Between 截面标定 theta ---
reg_df = df[['year', 'city', 'K_100m', 'pop_urban_proxy', 'hc_city',
             'gdp_100m']].dropna()
reg_df = reg_df[(reg_df['K_100m'] > 0) & (reg_df['pop_urban_proxy'] > 0) &
                (reg_df['hc_city'] > 0) & (reg_df['gdp_100m'] > 0)]

between_df = reg_df.groupby('city')[['K_100m', 'pop_urban_proxy',
                                      'hc_city', 'gdp_100m']].mean()
for col in ['K_100m', 'pop_urban_proxy', 'hc_city', 'gdp_100m']:
    between_df[f'ln_{col}'] = np.log(between_df[col])

between_df['ln_Kstar_struct'] = (alpha_P_global * between_df['ln_pop_urban_proxy']
                                  + alpha_H_global * between_df['ln_hc_city']
                                  + alpha_G_global * between_df['ln_gdp_100m'])
residuals = between_df['ln_K_100m'] - between_df['ln_Kstar_struct']
ln_theta = residuals.median()
theta_china = np.exp(ln_theta)

# 截面 R2
fitted = ln_theta + between_df['ln_Kstar_struct']
ss_res = ((between_df['ln_K_100m'] - fitted) ** 2).sum()
ss_tot = ((between_df['ln_K_100m'] - between_df['ln_K_100m'].mean()) ** 2).sum()
r2_hybrid = 1 - ss_res / ss_tot

rprint(f"  theta_china = {theta_china:.6f} (ln_theta = {ln_theta:.4f})")
rprint(f"  截面拟合 R2 = {r2_hybrid:.4f}")

# --- 计算 K* ---
valid_calc = (df['pop_urban_proxy'].notna() & (df['pop_urban_proxy'] > 0) &
              df['hc_city'].notna() & (df['hc_city'] > 0) &
              df['gdp_100m'].notna() & (df['gdp_100m'] > 0))

df['ln_Kstar'] = np.nan
df.loc[valid_calc, 'ln_Kstar'] = (ln_theta
                                   + alpha_P_global * np.log(df.loc[valid_calc, 'pop_urban_proxy'])
                                   + alpha_H_global * np.log(df.loc[valid_calc, 'hc_city'])
                                   + alpha_G_global * np.log(df.loc[valid_calc, 'gdp_100m']))

# 二次标定: 使 2015 年全国中位数 OCR ~= 1.15
calibration_year = 2015
target_ocr_median = 1.15
cal_mask = ((df['year'] == calibration_year) & df['K_100m'].notna() &
            df['ln_Kstar'].notna() & (df['K_100m'] > 0))

if cal_mask.sum() > 0:
    cal_data = df.loc[cal_mask].copy()
    cal_data['ln_K_actual'] = np.log(cal_data['K_100m'])
    current_ln_ocr_med = (cal_data['ln_K_actual'] - cal_data['ln_Kstar']).median()
    delta_cal = current_ln_ocr_med - np.log(target_ocr_median)
    df.loc[df['ln_Kstar'].notna(), 'ln_Kstar'] += delta_cal
    rprint(f"  二次标定: delta={delta_cal:.4f}, "
           f"当前中位数OCR={np.exp(current_ln_ocr_med):.3f} -> 目标 {target_ocr_median}")
else:
    delta_cal = 0.0
    rprint("  警告: 标定失败")

df['Kstar_100m'] = np.exp(df['ln_Kstar'])

# --- 计算 OCR ---
valid_ocr = df['K_100m'].notna() & df['Kstar_100m'].notna() & (df['Kstar_100m'] > 0)
df.loc[valid_ocr, 'OCR'] = df.loc[valid_ocr, 'K_100m'] / df.loc[valid_ocr, 'Kstar_100m']

# --- 窗口 1 城市 OCR ---
w1_ocr = df[w1_mask & df['OCR'].notna()].copy()
w1_city_ocr = w1_ocr.groupby('city').agg({
    'OCR': 'mean',
    'Kstar_100m': 'mean',
    'K_100m': 'mean',
    'urban_q': 'mean',
    'city_tier': 'first',
    'region4': 'first',
    'gdp_per_capita': 'mean',
}).reset_index()

rprint(f"\n--- OCR 统计 (窗口 1, {len(w1_city_ocr)} 城市) ---")

# 按等级统计
rprint(f"\n{'等级':<10} {'N':>4} {'OCR_mean':>9} {'OCR_med':>9} {'OCR_p25':>9} "
       f"{'OCR_p75':>9} {'OCR>1%':>8}")
rprint("-" * 70)
for t in tier_order:
    sub = w1_city_ocr[w1_city_ocr['city_tier'] == t]['OCR']
    if len(sub) == 0:
        continue
    rprint(f"{t:<10} {len(sub):>4} {sub.mean():>9.3f} {sub.median():>9.3f} "
           f"{sub.quantile(0.25):>9.3f} {sub.quantile(0.75):>9.3f} "
           f"{(sub>1).sum()/len(sub)*100:>7.1f}%")

# 按区域统计
rprint(f"\n{'区域':<10} {'N':>4} {'OCR_mean':>9} {'OCR_med':>9} {'OCR_p25':>9} "
       f"{'OCR_p75':>9} {'OCR>1%':>8}")
rprint("-" * 70)
for r in ['东部', '中部', '西部', '东北']:
    sub = w1_city_ocr[w1_city_ocr['region4'] == r]['OCR']
    if len(sub) == 0:
        continue
    rprint(f"{r:<10} {len(sub):>4} {sub.mean():>9.3f} {sub.median():>9.3f} "
           f"{sub.quantile(0.25):>9.3f} {sub.quantile(0.75):>9.3f} "
           f"{(sub>1).sum()/len(sub)*100:>7.1f}%")

# --- C.4: 四色分级 (K-means 数据驱动阈值) ---
rprint("\n--- 四色分级 (K-means 数据驱动) ---")

ocr_vals = w1_city_ocr['OCR'].values.reshape(-1, 1)
kmeans = KMeans(n_clusters=4, random_state=42, n_init=20)
labels = kmeans.fit_predict(ocr_vals)

# 按 OCR 均值排序 cluster
cluster_means = pd.DataFrame({
    'cluster': range(4),
    'mean_ocr': [ocr_vals[labels == i].mean() for i in range(4)]
}).sort_values('mean_ocr')

# 从低到高映射颜色
color_map_names = ['绿色(适度)', '黄色(轻度过度)', '橙色(中度过度)', '红色(严重过度)']
color_hex = ['#2ca02c', '#ffc107', '#ff9800', '#d32f2f']

cluster_to_rank = {row['cluster']: i for i, (_, row) in enumerate(cluster_means.iterrows())}
w1_city_ocr['ocr_cluster'] = [cluster_to_rank[l] for l in labels]
w1_city_ocr['ocr_color'] = [color_map_names[cluster_to_rank[l]] for l in labels]

# 确定阈值 (cluster 边界)
thresholds = []
sorted_clusters = cluster_means['cluster'].values
for i in range(len(sorted_clusters) - 1):
    c1_vals = ocr_vals[labels == sorted_clusters[i]]
    c2_vals = ocr_vals[labels == sorted_clusters[i+1]]
    threshold = (c1_vals.max() + c2_vals.min()) / 2
    thresholds.append(threshold)

rprint(f"K-means 阈值 (数据驱动):")
for i, th in enumerate(thresholds):
    rprint(f"  {color_map_names[i]} | {th:.3f} | {color_map_names[i+1]}")

rprint(f"\n四色分级分布:")
for i, name in enumerate(color_map_names):
    n = (w1_city_ocr['ocr_cluster'] == i).sum()
    sub = w1_city_ocr[w1_city_ocr['ocr_cluster'] == i]['OCR']
    if len(sub) > 0:
        rprint(f"  {name}: {n} 城市 ({100*n/len(w1_city_ocr):.1f}%), "
               f"OCR range [{sub.min():.3f}, {sub.max():.3f}]")

# OCR 最高 / 最低城市
rprint("\nOCR 最高 10 个城市:")
top_ocr = w1_city_ocr.nlargest(10, 'OCR')[['city', 'city_tier', 'region4',
                                             'OCR', 'urban_q', 'ocr_color']]
for _, row in top_ocr.iterrows():
    rprint(f"  {row['city']:<10} {row['city_tier']:<8} {row['region4']:<4} "
           f"OCR={row['OCR']:.3f}  Q={row['urban_q']:.3f}  {row['ocr_color']}")

rprint("\nOCR 最低 10 个城市:")
bot_ocr = w1_city_ocr.nsmallest(10, 'OCR')[['city', 'city_tier', 'region4',
                                              'OCR', 'urban_q', 'ocr_color']]
for _, row in bot_ocr.iterrows():
    rprint(f"  {row['city']:<10} {row['city_tier']:<8} {row['region4']:<4} "
           f"OCR={row['OCR']:.3f}  Q={row['urban_q']:.3f}  {row['ocr_color']}")

# ############################################################
# PART D: 窗口 1 vs 窗口 2 稳健性比较
# ############################################################
rprint("\n" + "#" * 70)
rprint("# PART D: 窗口 1 vs 窗口 2 稳健性比较")
rprint("#" * 70)

# 窗口 2 城市 Q (2015-2016 子集, 用于直接比较)
# 以及全时段均值
w2_1516 = df[(df['year'].isin([2015, 2016])) & df['urban_q'].notna()].copy()
w2_city_1516 = w2_1516.groupby('city').agg({
    'urban_q': 'mean',
    'fai_imputed': lambda x: x.any(),
}).reset_index().rename(columns={'urban_q': 'Q_w2_1516',
                                  'fai_imputed': 'has_imputed_fai'})

# 对 2017-2023, 计算每个城市的最新 Q
w2_later = df[(df['year'].between(2017, 2023)) & df['urban_q'].notna()].copy()
w2_city_later = w2_later.groupby('city').agg({
    'urban_q': 'mean',
    'OCR': 'mean',
}).reset_index().rename(columns={'urban_q': 'Q_w2_extended',
                                  'OCR': 'OCR_w2_extended'})

# 合并窗口 1 和窗口 2
compare = w1_city[['city', 'urban_q', 'city_tier', 'region4']].rename(
    columns={'urban_q': 'Q_w1'})
compare = compare.merge(w2_city_1516[['city', 'Q_w2_1516', 'has_imputed_fai']],
                        on='city', how='left')
compare = compare.merge(w2_city_later[['city', 'Q_w2_extended']], on='city', how='left')

# 窗口 1 OCR
compare = compare.merge(w1_city_ocr[['city', 'OCR']].rename(columns={'OCR': 'OCR_w1'}),
                        on='city', how='left')

# 窗口 2 extended OCR
w2_ocr_ext = df[(df['year'].between(2017, 2023)) & df['OCR'].notna()].groupby('city')['OCR'].mean()
compare = compare.merge(w2_ocr_ext.rename('OCR_w2_extended').reset_index(),
                        on='city', how='left')

# --- D.1: Q 分布比较 (2015-2016 窗口 1 vs 窗口 2 — 应相同因为全部 FAI 真实) ---
rprint("\n--- D.1: 2015-2016 Q 分布 (窗口1 vs 窗口2) ---")
rprint("注: 2015-2016 年 FAI 全部为真实数据, 窗口 1 和 2 应完全一致")

w1_q = compare['Q_w1'].dropna()
w2_q = compare['Q_w2_1516'].dropna()
rprint(f"  窗口 1 Q: mean={w1_q.mean():.3f}, median={w1_q.median():.3f}, N={len(w1_q)}")
rprint(f"  窗口 2 Q (1516): mean={w2_q.mean():.3f}, median={w2_q.median():.3f}, N={len(w2_q)}")

# KS 检验
ks_stat, ks_p = stats.ks_2samp(w1_q, w2_q)
rprint(f"  KS 检验: stat={ks_stat:.4f}, p={ks_p:.4f}")

# --- D.2: 窗口 1 (2015-2016) vs 窗口 2 Extended (2017-2023) ---
rprint("\n--- D.2: 窗口 1 Q (2015-2016) vs 窗口 2 Extended Q (2017-2023) ---")
both = compare.dropna(subset=['Q_w1', 'Q_w2_extended'])
rprint(f"  匹配城市: {len(both)}")
if len(both) > 10:
    rprint(f"  窗口 1 Q: mean={both['Q_w1'].mean():.3f}, median={both['Q_w1'].median():.3f}")
    rprint(f"  窗口 2 ext Q: mean={both['Q_w2_extended'].mean():.3f}, "
           f"median={both['Q_w2_extended'].median():.3f}")

    # Q 变化
    both['Q_change'] = both['Q_w2_extended'] - both['Q_w1']
    both['Q_change_pct'] = (both['Q_w2_extended'] / both['Q_w1'] - 1) * 100
    rprint(f"  Q 变化: mean={both['Q_change'].mean():.3f}, "
           f"median={both['Q_change'].median():.3f}")
    rprint(f"  Q 变化%: mean={both['Q_change_pct'].mean():.1f}%, "
           f"median={both['Q_change_pct'].median():.1f}%")

    # Spearman 相关
    rho_q, p_q = stats.spearmanr(both['Q_w1'], both['Q_w2_extended'])
    rprint(f"  Q 排名 Spearman rho={rho_q:.4f}, p={p_q:.2e}")

    # Pearson 相关
    r_q, pr_q = stats.pearsonr(both['Q_w1'], both['Q_w2_extended'])
    rprint(f"  Q Pearson r={r_q:.4f}, p={pr_q:.2e}")

# --- D.3: OCR Spearman 相关性 ---
rprint("\n--- D.3: OCR 排名稳健性 ---")
both_ocr = compare.dropna(subset=['OCR_w1', 'OCR_w2_extended'])
rprint(f"  匹配城市 (有OCR): {len(both_ocr)}")
if len(both_ocr) > 10:
    rho_ocr, p_ocr = stats.spearmanr(both_ocr['OCR_w1'], both_ocr['OCR_w2_extended'])
    rprint(f"  OCR 排名 Spearman rho={rho_ocr:.4f}, p={p_ocr:.2e}")
    r_ocr, pr_ocr = stats.pearsonr(both_ocr['OCR_w1'], both_ocr['OCR_w2_extended'])
    rprint(f"  OCR Pearson r={r_ocr:.4f}, p={pr_ocr:.2e}")

    # OCR 变化
    both_ocr_sub = both_ocr.copy()
    both_ocr_sub['OCR_change'] = both_ocr_sub['OCR_w2_extended'] - both_ocr_sub['OCR_w1']
    rprint(f"  OCR 变化: mean={both_ocr_sub['OCR_change'].mean():.3f}, "
           f"median={both_ocr_sub['OCR_change'].median():.3f}")

# --- D.4: FAI 估算对 Q 和 OCR 的影响 ---
rprint("\n--- D.4: FAI 估算对 Q 和 OCR 的影响方向与幅度 ---")
rprint("2017+ 年 FAI 为 ratio 估算 (MAPE ~48%), 对 K 的影响:")

if len(both) > 10:
    # Q 变化按等级
    rprint("\n按城市等级的 Q 变化 (窗口 1 -> 窗口 2 Extended):")
    for t in tier_order:
        sub = both[both['city_tier'] == t]
        if len(sub) > 0:
            rprint(f"  {t} (N={len(sub)}): Q变化 mean={sub['Q_change'].mean():.3f}, "
                   f"median={sub['Q_change'].median():.3f}")

    # Q 变化按区域
    rprint("\n按区域的 Q 变化:")
    for r in ['东部', '中部', '西部', '东北']:
        sub = both[both['region4'] == r]
        if len(sub) > 0:
            rprint(f"  {r} (N={len(sub)}): Q变化 mean={sub['Q_change'].mean():.3f}, "
                   f"median={sub['Q_change'].median():.3f}")

rprint("\n结论:")
rprint("  FAI 估算 (2017+) 存在较大误差 (MAPE ~48%), 导致:")
rprint("  1. K 累积存量在 2017+ 逐年偏移, 但因 PIM 累积效应, 对总存量影响有限")
rprint("  2. 窗口 1 (2015-2016) 为唯一严格可靠窗口")
rprint("  3. 城市排名在两个窗口间的相关性反映了结构性差异的持久性")

# ############################################################
# PART E: 图表
# ############################################################
rprint("\n" + "#" * 70)
rprint("# PART E: 生成图表")
rprint("#" * 70)

fig = plt.figure(figsize=(20, 16))
gs = gridspec.GridSpec(2, 2, hspace=0.35, wspace=0.3)

# --- E.1: 城市 Q 箱线图（按等级）---
ax1 = fig.add_subplot(gs[0, 0])
tier_data = [w1_city[w1_city['city_tier'] == t]['urban_q'].values for t in tier_order]
bp = ax1.boxplot(tier_data, labels=tier_order, patch_artist=True,
                  showfliers=True, flierprops=dict(markersize=3, alpha=0.5))
colors_box = ['#e74c3c', '#f39c12', '#3498db', '#95a5a6']
for patch, color in zip(bp['boxes'], colors_box):
    patch.set_facecolor(color)
    patch.set_alpha(0.6)
ax1.axhline(y=1, color='black', linestyle='--', alpha=0.7, linewidth=1)
ax1.set_ylabel('Urban Q (V/K)', fontsize=12)
ax1.set_title('(a) 城市 Urban Q 分布 (2015-2016, Gold Standard)', fontsize=12)
ax1.text(0.02, 0.98, f'N={len(w1_city)}', transform=ax1.transAxes,
         va='top', fontsize=10, color='gray')

# 添加 N 标注
for i, t in enumerate(tier_order):
    n = len(w1_city[w1_city['city_tier'] == t])
    ax1.text(i+1, ax1.get_ylim()[0], f'n={n}', ha='center', va='bottom',
             fontsize=9, color='gray')

# --- E.2: 城市 OCR 分布直方图 ---
ax2 = fig.add_subplot(gs[0, 1])
ocr_data = w1_city_ocr['OCR'].dropna()
ax2.hist(ocr_data, bins=30, color='#3498db', alpha=0.6, edgecolor='white')
ax2.axvline(x=1.0, color='red', linestyle='--', linewidth=1.5, label='OCR=1 (均衡)')
ax2.axvline(x=ocr_data.median(), color='green', linestyle='-.',
            linewidth=1.5, label=f'中位数={ocr_data.median():.2f}')

# 标注四色阈值
for i, th in enumerate(thresholds):
    ax2.axvline(x=th, color=color_hex[i+1], linestyle=':', alpha=0.7)

ax2.set_xlabel('OCR (K/K*)', fontsize=12)
ax2.set_ylabel('城市数', fontsize=12)
ax2.set_title('(b) 城市 OCR 分布 (2015-2016)', fontsize=12)
ax2.legend(fontsize=9)
ax2.text(0.02, 0.98, f'N={len(ocr_data)}, K-means 4色分级',
         transform=ax2.transAxes, va='top', fontsize=10, color='gray')

# --- E.3: Q vs OCR 散点图 ---
ax3 = fig.add_subplot(gs[1, 0])
scatter_data = w1_city_ocr.dropna(subset=['OCR', 'urban_q'])

# 按等级着色
tier_colors = {'一线': '#e74c3c', '新一线': '#f39c12', '二线': '#3498db',
               '三线及以下': '#95a5a6'}
for t in tier_order:
    sub = scatter_data[scatter_data['city_tier'] == t]
    ax3.scatter(sub['OCR'], sub['urban_q'], c=tier_colors[t], label=t,
                alpha=0.6, s=30, edgecolors='white', linewidth=0.3)

# 标注典型城市
label_cities = ['北京市', '上海市', '深圳市', '广州市', '杭州市', '成都市',
                '天津市', '重庆市', '沈阳市', '哈尔滨市']
for _, row in scatter_data.iterrows():
    if row['city'] in label_cities:
        ax3.annotate(row['city'].replace('市', ''),
                     (row['OCR'], row['urban_q']),
                     fontsize=7, alpha=0.8,
                     xytext=(5, 5), textcoords='offset points')

ax3.axhline(y=1, color='gray', linestyle='--', alpha=0.5)
ax3.axvline(x=1, color='gray', linestyle='--', alpha=0.5)
ax3.set_xlabel('OCR (K/K*)', fontsize=12)
ax3.set_ylabel('Urban Q (V/K)', fontsize=12)
ax3.set_title('(c) Q vs OCR 散点图 (2015-2016)', fontsize=12)
ax3.legend(fontsize=9, loc='upper right')

# 象限标注
xlim = ax3.get_xlim()
ylim = ax3.get_ylim()
ax3.text(0.7 * 1 + 0.3 * xlim[0], ylim[1] * 0.9, 'Q>1, OCR<1\n(供不应求)',
         fontsize=8, ha='center', color='green', alpha=0.7)
ax3.text(xlim[1] * 0.85, ylim[1] * 0.9, 'Q>1, OCR>1\n(泡沫+过度建设)',
         fontsize=8, ha='center', color='red', alpha=0.7)
ax3.text(0.7 * 1 + 0.3 * xlim[0], ylim[0] + 0.05 * (ylim[1]-ylim[0]),
         'Q<1, OCR<1\n(低估值)',
         fontsize=8, ha='center', color='blue', alpha=0.7)
ax3.text(xlim[1] * 0.85, ylim[0] + 0.05 * (ylim[1]-ylim[0]),
         'Q<1, OCR>1\n(过度建设+低估值)',
         fontsize=8, ha='center', color='orange', alpha=0.7)

# --- E.4: 窗口 1 vs 窗口 2 Q 对比 ---
ax4 = fig.add_subplot(gs[1, 1])

if len(both) > 10:
    for t in tier_order:
        sub = both[both['city_tier'] == t]
        ax4.scatter(sub['Q_w1'], sub['Q_w2_extended'], c=tier_colors[t],
                    label=t, alpha=0.5, s=25, edgecolors='white', linewidth=0.3)

    # 45度线
    q_range = [min(both['Q_w1'].min(), both['Q_w2_extended'].min()),
               max(both['Q_w1'].max(), both['Q_w2_extended'].max())]
    ax4.plot(q_range, q_range, 'k--', alpha=0.5, linewidth=1)

    ax4.set_xlabel('Q (窗口 1: 2015-2016, FAI 真实)', fontsize=11)
    ax4.set_ylabel('Q (窗口 2: 2017-2023, FAI 含估算)', fontsize=11)
    ax4.set_title('(d) 窗口 1 vs 窗口 2 Q 对比', fontsize=12)
    ax4.legend(fontsize=9)

    # 添加相关系数
    rho_txt = f"Spearman rho={rho_q:.3f}\nPearson r={r_q:.3f}"
    ax4.text(0.02, 0.98, rho_txt, transform=ax4.transAxes, va='top',
             fontsize=10, color='gray',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
else:
    ax4.text(0.5, 0.5, '数据不足', transform=ax4.transAxes,
             ha='center', va='center', fontsize=14, color='gray')

plt.suptitle('中国城市 Urban Q 与 OCR 分析 -- 严格真实 FAI 窗口',
             fontsize=14, fontweight='bold', y=0.98)

plt.savefig(f"{FIGS}/fig_city_real_window.png", dpi=200, bbox_inches='tight',
            facecolor='white')
rprint(f"\n图表已保存: {FIGS}/fig_city_real_window.png")
plt.close()

# ############################################################
# 输出数据
# ############################################################
rprint("\n" + "#" * 70)
rprint("# 输出数据")
rprint("#" * 70)

# 合并输出: 窗口 1 城市截面 + OCR + 四色分级
output = w1_city[['city', 'urban_q', 'K_100m', 'V_100m', 'house_price',
                   'gdp_per_capita', 'gdp_100m', 'pop_10k', 'per_capita_area_m2',
                   'fai_100m', 'city_tier', 'region4', 'province', 'fai_gdp_ratio']].copy()
output = output.rename(columns={'urban_q': 'Q_w1'})

# 合并 OCR 和四色分级
ocr_cols = w1_city_ocr[['city', 'OCR', 'Kstar_100m', 'ocr_cluster', 'ocr_color']].copy()
ocr_cols = ocr_cols.rename(columns={'OCR': 'OCR_w1'})
output = output.merge(ocr_cols, on='city', how='left')

# 合并窗口 2 extended
if 'Q_w2_extended' in compare.columns:
    output = output.merge(compare[['city', 'Q_w2_extended', 'OCR_w2_extended']],
                          on='city', how='left')

output = output.sort_values('Q_w1', ascending=False)

output.to_csv(f"{DATA_PROC}/china_city_real_window.csv", index=False)
rprint(f"数据已保存: {DATA_PROC}/china_city_real_window.csv")
rprint(f"  行数: {len(output)}, 列数: {len(output.columns)}")

# ############################################################
# 保存报告
# ############################################################
with open(f"{MODELS}/city_real_window_report.txt", 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

print(f"\n报告已保存: {MODELS}/city_real_window_report.txt")
print("\n完成!")
