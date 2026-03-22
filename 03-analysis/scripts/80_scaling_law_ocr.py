#!/usr/bin/env python3
"""
80_scaling_law_ocr.py — OCR 标度律检验 (Scaling Law Analysis)
=============================================================
目的: 验证城市过度建设率 (OCR) 是否遵循标度律 OCR ~ Pop^(-alpha)
输入: china_city_real_window.csv, china_275_city_panel.csv, global_kstar_m2_panel.csv
输出: scaling_law_ocr_report.txt, fig_scaling_law.png, fig_scaling_source.csv
依赖: numpy, pandas, scipy, statsmodels, matplotlib, sklearn
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 路径配置
# ============================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
DATA_DIR = f'{BASE}/02-data/processed'
SCRIPT_OUT = f'{BASE}/03-analysis/models/scaling_law_ocr_report.txt'
FIG_OUT = f'{BASE}/04-figures/drafts/fig_scaling_law.png'
SOURCE_OUT = f'{BASE}/04-figures/source-data/fig_scaling_source.csv'

# ============================================================
# Nature 级配色 (色盲安全)
# ============================================================
REGION_COLORS = {
    '东部': '#0072B2',   # 蓝
    '中部': '#D55E00',   # 橙红
    '西部': '#009E73',   # 绿
    '东北': '#CC79A7',   # 粉紫
}
REGION_ORDER = ['东部', '中部', '西部', '东北']

report_lines = []
def rpt(s=''):
    report_lines.append(s)
    print(s)

# ============================================================
# 数据加载
# ============================================================
rpt('=' * 72)
rpt('OCR 标度律检验 (Scaling Law: OCR ~ Pop^(-alpha))')
rpt('=' * 72)
rpt()

df = pd.read_csv(f'{DATA_DIR}/china_city_real_window.csv')
rpt(f'数据: china_city_real_window.csv, N = {len(df)} 城市')
rpt(f'时期: 2015-2016 黄金窗口均值')
rpt()

# 加载城市面板以获取三产占比和城区人口
city_panel = pd.read_csv(f'{DATA_DIR}/china_275_city_panel.csv')
cp_1516 = city_panel[city_panel['year'].isin([2015, 2016])].groupby('city').agg({
    'ter_share': 'mean',
    'urban_pop_10k': 'mean'
}).reset_index()
df = df.merge(cp_1516, on='city', how='left')

# 计算关键比率
df['K_GDP'] = df['K_100m'] / df['gdp_100m']
df['V_GDP'] = df['V_100m'] / df['gdp_100m']

# 对数变换
df['ln_OCR'] = np.log(df['OCR_w1'])
df['ln_Pop'] = np.log(df['pop_10k'])
df['ln_Q'] = np.log(df['Q_w1'])
df['ln_GDP'] = np.log(df['gdp_100m'])
df['ln_K'] = np.log(df['K_100m'])
df['ln_V'] = np.log(df['V_100m'])
df['ln_GDP_pc'] = np.log(df['gdp_per_capita'])
df['ln_K_GDP'] = np.log(df['K_GDP'])
df['ln_V_GDP'] = np.log(df['V_GDP'])
df['ln_FAI_GDP'] = np.log(df['fai_gdp_ratio'])

# 城区人口对数（如可得）
if df['urban_pop_10k'].notna().sum() > 100:
    df['ln_UrbanPop'] = np.log(df['urban_pop_10k'].clip(lower=1))

# ============================================================
# 辅助函数
# ============================================================
def ols_report(y, X, label='', df_data=None):
    """运行 OLS 并返回结果摘要"""
    X_const = sm.add_constant(X)
    model = sm.OLS(y, X_const).fit(cov_type='HC1')
    return model

def format_coef(model, var_idx=1):
    """格式化系数报告"""
    b = model.params.iloc[var_idx]
    se = model.bse.iloc[var_idx]
    p = model.pvalues.iloc[var_idx]
    ci = model.conf_int().iloc[var_idx]
    return f'beta = {b:.4f}, SE = {se:.4f}, p = {p:.2e}, 95% CI [{ci[0]:.4f}, {ci[1]:.4f}]'


# ############################################################
# PART A: 基础标度律检验
# ############################################################
rpt('=' * 72)
rpt('PART A: 基础标度律检验')
rpt('=' * 72)
rpt()

# --- A1: ln(OCR) = a - alpha * ln(Pop) ---
rpt('--- A1: ln(OCR) = a - alpha * ln(Pop) + epsilon ---')
mask_a1 = df['OCR_w1'].notna() & df['pop_10k'].notna() & (df['OCR_w1'] > 0) & (df['pop_10k'] > 0)
df_a1 = df[mask_a1].copy()
model_a1 = ols_report(df_a1['ln_OCR'], df_a1['ln_Pop'])
alpha = -model_a1.params.iloc[1]  # 取负号使 alpha > 0 (如果关系为负)
rpt(f'N = {model_a1.nobs:.0f}')
rpt(f'ln(Pop) 系数: {model_a1.params.iloc[1]:.4f}  => alpha = {alpha:.4f}')
rpt(f'  {format_coef(model_a1)}')
rpt(f'  R-squared = {model_a1.rsquared:.4f}')
rpt(f'  Adj. R-squared = {model_a1.rsquared_adj:.4f}')
rpt(f'  F-statistic = {model_a1.fvalue:.2f}, p = {model_a1.f_pvalue:.2e}')
rpt()

# Breusch-Pagan 异方差检验
bp_stat, bp_p, _, _ = het_breuschpagan(model_a1.resid, model_a1.model.exog)
rpt(f'  Breusch-Pagan 异方差检验: stat = {bp_stat:.2f}, p = {bp_p:.4f}')
rpt(f'  (已使用 HC1 稳健标准误)')
rpt()

# --- A2: ln(Q) = a + beta * ln(Pop) ---
rpt('--- A2: ln(Q) = a + beta * ln(Pop) + epsilon ---')
mask_a2 = df['Q_w1'].notna() & df['pop_10k'].notna() & (df['Q_w1'] > 0) & (df['pop_10k'] > 0)
df_a2 = df[mask_a2].copy()
model_a2 = ols_report(df_a2['ln_Q'], df_a2['ln_Pop'])
beta_Q = model_a2.params.iloc[1]
rpt(f'N = {model_a2.nobs:.0f}')
rpt(f'ln(Pop) 系数 (beta_Q): {format_coef(model_a2)}')
rpt(f'  R-squared = {model_a2.rsquared:.4f}')
rpt(f'  Bettencourt 参考值: GDP 产出标度 ~1.15 (超线性)')
rpt(f'  本研究 Q 标度: beta = {beta_Q:.4f}')
rpt()

# --- A3: K/GDP 和 V/GDP 的标度 ---
rpt('--- A3: 分解 OCR 驱动力 --- ')
rpt('  ln(K/GDP) = a + beta_KGDP * ln(Pop)')
model_kgdp = ols_report(df_a1['ln_K_GDP'], df_a1['ln_Pop'])
rpt(f'  beta_K/GDP: {format_coef(model_kgdp)}  R2={model_kgdp.rsquared:.4f}')

rpt('  ln(V/GDP) = a + beta_VGDP * ln(Pop)')
model_vgdp = ols_report(df_a1['ln_V_GDP'], df_a1['ln_Pop'])
rpt(f'  beta_V/GDP: {format_coef(model_vgdp)}  R2={model_vgdp.rsquared:.4f}')
rpt()
rpt(f'  解读: K/GDP 标度指数 = {model_kgdp.params.iloc[1]:.4f}, V/GDP 标度指数 = {model_vgdp.params.iloc[1]:.4f}')
if model_kgdp.params.iloc[1] > model_vgdp.params.iloc[1]:
    rpt('  => K 增速快于 V，过度建设主要由资本过度积累驱动')
else:
    rpt('  => V 增速快于 K，资产价值对人口更敏感')
rpt()


# ############################################################
# PART B: 稳健性检验
# ############################################################
rpt('=' * 72)
rpt('PART B: 稳健性检验')
rpt('=' * 72)
rpt()

# --- B1: 分区域 ---
rpt('--- B1: 分区域标度律 ---')
alphas_region = {}
for reg in REGION_ORDER:
    sub = df_a1[df_a1['region4'] == reg]
    if len(sub) >= 10:
        m = ols_report(sub['ln_OCR'], sub['ln_Pop'])
        a_reg = -m.params.iloc[1]
        alphas_region[reg] = {'alpha': a_reg, 'se': m.bse.iloc[1], 'p': m.pvalues.iloc[1],
                              'r2': m.rsquared, 'n': len(sub)}
        rpt(f'  {reg} (n={len(sub)}): alpha = {a_reg:.4f}, SE = {m.bse.iloc[1]:.4f}, '
            f'p = {m.pvalues.iloc[1]:.2e}, R2 = {m.rsquared:.4f}')

# 区域交互项 F 检验
rpt()
rpt('  区域交互项 F 检验:')
df_a1_dummy = df_a1.copy()
for reg in REGION_ORDER[1:]:
    df_a1_dummy[f'd_{reg}'] = (df_a1_dummy['region4'] == reg).astype(int)
    df_a1_dummy[f'int_{reg}'] = df_a1_dummy[f'd_{reg}'] * df_a1_dummy['ln_Pop']

# 受限模型（无交互项）
X_r = sm.add_constant(df_a1_dummy['ln_Pop'])
model_r = sm.OLS(df_a1_dummy['ln_OCR'], X_r).fit()
# 非受限模型（含交互项）
int_cols = [f'd_{r}' for r in REGION_ORDER[1:]] + [f'int_{r}' for r in REGION_ORDER[1:]]
X_ur = sm.add_constant(df_a1_dummy[['ln_Pop'] + int_cols])
model_ur = sm.OLS(df_a1_dummy['ln_OCR'], X_ur).fit()
f_test = model_ur.compare_f_test(model_r)
rpt(f'  F = {f_test[0]:.2f}, p = {f_test[1]:.4f}')
if f_test[1] < 0.05:
    rpt('  => 区域间 alpha 存在显著差异')
else:
    rpt('  => 区域间 alpha 无显著差异 (标度律具有一致性)')

# alpha 变化幅度
if alphas_region:
    all_alphas = [v['alpha'] for v in alphas_region.values()]
    mean_alpha = np.mean(all_alphas)
    max_dev = max(abs(a - mean_alpha) / abs(mean_alpha) for a in all_alphas) * 100
    rpt(f'  alpha 均值 = {mean_alpha:.4f}, 最大偏差 = {max_dev:.1f}%')
rpt()

# --- B2: 控制变量 ---
rpt('--- B2: 控制变量后的标度律 ---')
df_b2 = df_a1.copy()
# 基本控制: ln(GDP_pc) + FAI/GDP
ctrl_cols_1 = ['ln_GDP_pc', 'ln_FAI_GDP']
valid_b2 = df_b2[['ln_OCR', 'ln_Pop'] + ctrl_cols_1].dropna()
X_b2 = valid_b2[['ln_Pop'] + ctrl_cols_1]
model_b2 = ols_report(valid_b2['ln_OCR'], X_b2)
rpt(f'  模型: ln(OCR) ~ ln(Pop) + ln(GDP_pc) + ln(FAI/GDP)')
rpt(f'  N = {model_b2.nobs:.0f}')
rpt(f'  ln(Pop): {format_coef(model_b2, 1)}')
rpt(f'  ln(GDP_pc): {format_coef(model_b2, 2)}')
rpt(f'  ln(FAI/GDP): {format_coef(model_b2, 3)}')
rpt(f'  R2 = {model_b2.rsquared:.4f}')
alpha_b2 = -model_b2.params.iloc[1]
rpt(f'  控制后 alpha = {alpha_b2:.4f} (基础 alpha = {alpha:.4f})')
rpt()

# 加入三产占比（如可得）
if 'ter_share' in df_b2.columns and df_b2['ter_share'].notna().sum() > 100:
    df_b2['ln_ter'] = np.log(df_b2['ter_share'].clip(lower=0.01))
    ctrl_cols_2 = ['ln_GDP_pc', 'ln_FAI_GDP', 'ln_ter']
    valid_b2b = df_b2[['ln_OCR', 'ln_Pop'] + ctrl_cols_2].dropna()
    X_b2b = valid_b2b[['ln_Pop'] + ctrl_cols_2]
    model_b2b = ols_report(valid_b2b['ln_OCR'], X_b2b)
    rpt(f'  扩展模型 (加入三产占比): N = {model_b2b.nobs:.0f}')
    rpt(f'  ln(Pop): {format_coef(model_b2b, 1)}')
    rpt(f'  R2 = {model_b2b.rsquared:.4f}')
    rpt()

# --- B3: 非参验证 (LOESS) ---
rpt('--- B3: 非参验证 (LOESS 线性检验) ---')
from statsmodels.nonparametric.smoothers_lowess import lowess
loess_fit = lowess(df_a1['ln_OCR'].values, df_a1['ln_Pop'].values, frac=0.5, return_sorted=True)
# 比较 LOESS 残差与 OLS 残差
ols_pred = model_a1.predict(sm.add_constant(df_a1['ln_Pop']))
ols_resid_ss = np.sum((df_a1['ln_OCR'].values - ols_pred.values) ** 2)
# LOESS 残差 (近似)
from scipy.interpolate import interp1d
loess_interp = interp1d(loess_fit[:, 0], loess_fit[:, 1], fill_value='extrapolate')
loess_pred = loess_interp(df_a1['ln_Pop'].values)
loess_resid_ss = np.sum((df_a1['ln_OCR'].values - loess_pred) ** 2)
improvement = (ols_resid_ss - loess_resid_ss) / ols_resid_ss * 100
rpt(f'  OLS RSS = {ols_resid_ss:.2f}, LOESS RSS = {loess_resid_ss:.2f}')
rpt(f'  LOESS 改善 = {improvement:.1f}%')
if improvement < 10:
    rpt('  => LOESS 改善 < 10%，线性（幂律）假设合理')
else:
    rpt('  => LOESS 改善 >= 10%，幂律关系可能存在非线性偏差，需谨慎')
rpt()

# Ramsey RESET 检验
rpt('  Ramsey RESET 检验 (非线性遗漏变量):')
fitted = model_a1.fittedvalues
X_reset = sm.add_constant(pd.DataFrame({'ln_Pop': df_a1['ln_Pop'], 'fitted2': fitted**2, 'fitted3': fitted**3}))
model_reset = sm.OLS(df_a1['ln_OCR'], X_reset).fit()
# F-test for fitted2, fitted3
r_matrix = np.zeros((2, 4))
r_matrix[0, 2] = 1  # fitted2
r_matrix[1, 3] = 1  # fitted3
f_test_reset = model_reset.f_test(r_matrix)
f_val = float(np.squeeze(f_test_reset.fvalue))
p_val = float(np.squeeze(f_test_reset.pvalue))
rpt(f'  F = {f_val:.2f}, p = {p_val:.4f}')
if p_val > 0.05:
    rpt('  => 未检测到显著非线性 (幂律假设成立)')
else:
    rpt('  => 检测到显著非线性，幂律关系近似但非完美')
rpt()

# --- B4: 异常值 (剔除一线城市) ---
rpt('--- B4: 剔除一线城市后的标度律 ---')
df_b4 = df_a1[df_a1['city_tier'] != '一线'].copy()
model_b4 = ols_report(df_b4['ln_OCR'], df_b4['ln_Pop'])
alpha_b4 = -model_b4.params.iloc[1]
rpt(f'  N = {model_b4.nobs:.0f} (剔除 {len(df_a1) - len(df_b4)} 个一线城市)')
rpt(f'  alpha = {alpha_b4:.4f} (原始 alpha = {alpha:.4f})')
rpt(f'  {format_coef(model_b4)}')
rpt(f'  R2 = {model_b4.rsquared:.4f}')
change_pct = abs(alpha_b4 - alpha) / abs(alpha) * 100
rpt(f'  alpha 变化: {change_pct:.1f}%')
rpt()

# Cook's distance 异常值分析
from statsmodels.stats.outliers_influence import OLSInfluence
influence = OLSInfluence(model_a1)
cooks_d = influence.cooks_distance[0]
threshold = 4 / len(df_a1)
outlier_cities = df_a1[cooks_d > threshold]['city'].tolist()
rpt(f"  Cook's D 异常值 (>{threshold:.4f}): {len(outlier_cities)} 城市")
if outlier_cities:
    rpt(f'  {outlier_cities[:10]}')
rpt()

# --- B5: 分年份 (2015 vs 2016) ---
rpt('--- B5: 分年份稳定性 ---')
# 需要从面板数据获取分年份数据
cp_2015 = city_panel[city_panel['year'] == 2015].copy()
cp_2016 = city_panel[city_panel['year'] == 2016].copy()
for yr, cp_yr in [(2015, cp_2015), (2016, cp_2016)]:
    # 需要面板中有 OCR 或可以计算
    # 面板中有 K_pim_100m 和相关数据，尝试用 window 数据中的 mapping
    # 由于 window 数据已是均值，改用面板中的 urban_q 作为替代检验
    if 'urban_q' in cp_yr.columns and 'urban_pop_10k' in cp_yr.columns:
        valid = cp_yr.dropna(subset=['urban_q', 'urban_pop_10k'])
        valid = valid[(valid['urban_q'] > 0) & (valid['urban_pop_10k'] > 0)]
        if len(valid) > 30:
            valid['ln_Q_yr'] = np.log(valid['urban_q'])
            valid['ln_Pop_yr'] = np.log(valid['urban_pop_10k'])
            m_yr = ols_report(valid['ln_Q_yr'], valid['ln_Pop_yr'])
            rpt(f'  {yr}: ln(Q) ~ ln(Pop), beta = {m_yr.params.iloc[1]:.4f}, '
                f'p = {m_yr.pvalues.iloc[1]:.2e}, R2 = {m_yr.rsquared:.4f}, N = {len(valid)}')

# 用 window 数据做伪分年份（OCR_w1 vs OCR_w2_extended）
rpt()
rpt('  使用 W1 vs W2 窗口对比:')
for col, label in [('OCR_w1', 'W1 (2015-16)'), ('OCR_w2_extended', 'W2 (扩展)')]:
    valid = df[(df[col] > 0) & (df['pop_10k'] > 0)].copy()
    valid['ln_y'] = np.log(valid[col])
    m_w = ols_report(valid['ln_y'], valid['ln_Pop'])
    rpt(f'  {label}: alpha = {-m_w.params.iloc[1]:.4f}, p = {m_w.pvalues.iloc[1]:.2e}, '
        f'R2 = {m_w.rsquared:.4f}')
rpt()

# --- B6: 替代人口指标 ---
rpt('--- B6: 替代人口指标 (城区人口) ---')
if 'ln_UrbanPop' in df.columns:
    valid_b6 = df_a1.dropna(subset=['ln_UrbanPop'])
    if len(valid_b6) > 50:
        model_b6 = ols_report(valid_b6['ln_OCR'], valid_b6['ln_UrbanPop'])
        alpha_b6 = -model_b6.params.iloc[1]
        rpt(f'  N = {model_b6.nobs:.0f}')
        rpt(f'  alpha (城区人口) = {alpha_b6:.4f}')
        rpt(f'  {format_coef(model_b6)}')
        rpt(f'  R2 = {model_b6.rsquared:.4f}')
        rpt(f'  对比: alpha (总人口) = {alpha:.4f}')
    else:
        rpt('  城区人口数据不足，跳过')
else:
    rpt('  城区人口数据不可用，跳过')
rpt()

# 稳健性汇总表
rpt('--- 稳健性汇总 ---')
rpt(f'{"检验":<30} {"alpha":<10} {"p":<12} {"R2":<8} {"判定":<6}')
rpt('-' * 66)
tests = [
    ('基础模型', alpha, model_a1.pvalues.iloc[1], model_a1.rsquared),
    ('控制GDP_pc+FAI/GDP', alpha_b2, model_b2.pvalues.iloc[1], model_b2.rsquared),
    ('剔除一线城市', alpha_b4, model_b4.pvalues.iloc[1], model_b4.rsquared),
]
for name, a, p, r2 in tests:
    sig = 'PASS' if p < 0.01 else ('PASS*' if p < 0.05 else 'FAIL')
    rpt(f'{name:<30} {a:<10.4f} {p:<12.2e} {r2:<8.4f} {sig}')
for reg, info in alphas_region.items():
    sig = 'PASS' if info['p'] < 0.01 else ('PASS*' if info['p'] < 0.05 else 'FAIL')
    rpt(f'{"区域: " + reg:<30} {info["alpha"]:<10.4f} {info["p"]:<12.2e} {info["r2"]:<8.4f} {sig}')
rpt()


# ############################################################
# PART C: 与 Bettencourt 标度律的对话
# ############################################################
rpt('=' * 72)
rpt('PART C: 标度指数对比 (Bettencourt Framework)')
rpt('=' * 72)
rpt()

# C1: GDP ~ Pop^beta_GDP
model_gdp = ols_report(df_a1['ln_GDP'], df_a1['ln_Pop'])
beta_GDP = model_gdp.params.iloc[1]
rpt(f'C1. GDP ~ Pop^beta_GDP')
rpt(f'  beta_GDP = {beta_GDP:.4f}, {format_coef(model_gdp)}')
rpt(f'  R2 = {model_gdp.rsquared:.4f}')
rpt(f'  Bettencourt 参考: beta_GDP ~ 1.15 (超线性)')
rpt()

# C2: K ~ Pop^beta_K
model_k = ols_report(df_a1['ln_K'], df_a1['ln_Pop'])
beta_K = model_k.params.iloc[1]
rpt(f'C2. K ~ Pop^beta_K')
rpt(f'  beta_K = {beta_K:.4f}, {format_coef(model_k)}')
rpt(f'  R2 = {model_k.rsquared:.4f}')
rpt()

# C3: V ~ Pop^beta_V
model_v = ols_report(df_a1['ln_V'], df_a1['ln_Pop'])
beta_V = model_v.params.iloc[1]
rpt(f'C3. V ~ Pop^beta_V')
rpt(f'  beta_V = {beta_V:.4f}, {format_coef(model_v)}')
rpt(f'  R2 = {model_v.rsquared:.4f}')
rpt()

# C4: 理论关系
rpt(f'C4. 理论关系:')
rpt(f'  OCR = K / K* = K / V')
rpt(f'  标度关系: OCR ~ Pop^(beta_K - beta_V)')
rpt(f'  实际: beta_K - beta_V = {beta_K:.4f} - {beta_V:.4f} = {beta_K - beta_V:.4f}')
rpt(f'  直接估计: alpha_OCR = {-model_a1.params.iloc[1]:.4f} (取负号)')
rpt(f'  差异: {abs((beta_K - beta_V) - model_a1.params.iloc[1]):.4f}')
rpt(f'  (OCR 标度指数应近似等于 beta_K - beta_V，因为 ln(OCR) = ln(K/V) = (beta_K - beta_V)*ln(Pop))')
rpt()

# C5: 标度指数对比表
rpt(f'C5. 标度指数汇总表:')
rpt(f'{"指标":<20} {"标度指数":<12} {"SE":<10} {"p":<12} {"R2":<8} {"Bettencourt参考":<15}')
rpt('-' * 77)
scaling_table = [
    ('GDP ~ Pop', beta_GDP, model_gdp.bse.iloc[1], model_gdp.pvalues.iloc[1], model_gdp.rsquared, '~1.15'),
    ('K ~ Pop', beta_K, model_k.bse.iloc[1], model_k.pvalues.iloc[1], model_k.rsquared, 'infra ~0.8'),
    ('V ~ Pop', beta_V, model_v.bse.iloc[1], model_v.pvalues.iloc[1], model_v.rsquared, 'N/A'),
    ('Q ~ Pop', beta_Q, model_a2.bse.iloc[1], model_a2.pvalues.iloc[1], model_a2.rsquared, 'N/A'),
    ('OCR ~ Pop', model_a1.params.iloc[1], model_a1.bse.iloc[1], model_a1.pvalues.iloc[1], model_a1.rsquared, 'N/A'),
    ('K/GDP ~ Pop', model_kgdp.params.iloc[1], model_kgdp.bse.iloc[1], model_kgdp.pvalues.iloc[1], model_kgdp.rsquared, 'infra: ~-0.35'),
    ('V/GDP ~ Pop', model_vgdp.params.iloc[1], model_vgdp.bse.iloc[1], model_vgdp.pvalues.iloc[1], model_vgdp.rsquared, 'N/A'),
]
for name, b, se, p, r2, ref in scaling_table:
    rpt(f'{name:<20} {b:<12.4f} {se:<10.4f} {p:<12.2e} {r2:<8.4f} {ref}')
rpt()


# ############################################################
# PART D: 跨国初步验证
# ############################################################
rpt('=' * 72)
rpt('PART D: 跨国初步验证')
rpt('=' * 72)
rpt()

gp = pd.read_csv(f'{DATA_DIR}/global_kstar_m2_panel.csv')
# 使用 2015 年数据
gp_2015 = gp[gp['year'] == 2015].dropna(subset=['OCR_m2', 'Pu']).copy()
gp_2015 = gp_2015[(gp_2015['OCR_m2'] > 0) & (gp_2015['Pu'] > 0)]
rpt(f'跨国数据: 2015 年, N = {len(gp_2015)} 国家')

if len(gp_2015) >= 20:
    gp_2015['ln_OCR_m2'] = np.log(gp_2015['OCR_m2'])
    gp_2015['ln_Pu'] = np.log(gp_2015['Pu'])

    model_d1 = ols_report(gp_2015['ln_OCR_m2'], gp_2015['ln_Pu'])
    rpt(f'ln(OCR_m2) ~ ln(Urban_Pop):')
    rpt(f'  {format_coef(model_d1)}')
    rpt(f'  R2 = {model_d1.rsquared:.4f}')
    rpt()

    # 按人口五分位
    gp_2015['pop_q'] = pd.qcut(gp_2015['Pu'], 5, labels=['Q1(小)', 'Q2', 'Q3', 'Q4', 'Q5(大)'])
    rpt('  按城镇人口五分位的 OCR_m2 均值:')
    for q in ['Q1(小)', 'Q2', 'Q3', 'Q4', 'Q5(大)']:
        sub = gp_2015[gp_2015['pop_q'] == q]
        rpt(f'    {q}: OCR_m2 均值 = {sub["OCR_m2"].mean():.3f}, '
            f'中位数 = {sub["OCR_m2"].median():.3f}, N = {len(sub)}')

    # Spearman 秩相关
    rho, p_rho = stats.spearmanr(gp_2015['Pu'], gp_2015['OCR_m2'])
    rpt(f'\n  Spearman 秩相关: rho = {rho:.4f}, p = {p_rho:.4f}')
    if p_rho < 0.05 and rho < 0:
        rpt('  => 跨国数据支持 OCR 与人口规模的负相关')
    elif p_rho < 0.05 and rho > 0:
        rpt('  => 跨国数据显示正相关，与城市级结论相反，需进一步解释')
    else:
        rpt('  => 跨国数据未发现显著相关')
else:
    rpt('  跨国数据不足，跳过')
rpt()


# ############################################################
# PART E: Nature 级可视化
# ############################################################
rpt('=' * 72)
rpt('PART E: 可视化')
rpt('=' * 72)
rpt()

fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.5), dpi=300)
plt.rcParams.update({
    'font.size': 7,
    'axes.labelsize': 8,
    'axes.titlesize': 8,
    'xtick.labelsize': 6.5,
    'ytick.labelsize': 6.5,
    'legend.fontsize': 6,
    'font.family': 'Arial',
})

# --- Panel a: 旗舰散点图 ---
ax = axes[0]

# 标注的典型城市
annotate_cities = {
    '深圳市': '深圳', '上海市': '上海', '北京市': '北京',
    '鄂尔多斯市': '鄂尔多斯', '广州市': '广州',
}

# GDP 归一化用于点大小
gdp_norm = df_a1['gdp_100m'] / df_a1['gdp_100m'].max()
sizes = 8 + gdp_norm * 60

for reg in REGION_ORDER:
    mask = df_a1['region4'] == reg
    sub = df_a1[mask]
    s = sizes[mask]
    ax.scatter(sub['ln_Pop'], sub['ln_OCR'],
               c=REGION_COLORS[reg], s=s, alpha=0.7, edgecolors='white',
               linewidth=0.3, label=reg, zorder=3)

# 拟合线 + 95% CI
x_line = np.linspace(df_a1['ln_Pop'].min() - 0.2, df_a1['ln_Pop'].max() + 0.2, 200)
X_line = sm.add_constant(x_line)
pred = model_a1.get_prediction(X_line)
pred_summary = pred.summary_frame(alpha=0.05)
ax.plot(x_line, pred_summary['mean'], color='#333333', linewidth=1.2, zorder=4)
ax.fill_between(x_line, pred_summary['obs_ci_lower'], pred_summary['obs_ci_upper'],
                alpha=0.08, color='gray', zorder=1)
ax.fill_between(x_line, pred_summary['mean_ci_lower'], pred_summary['mean_ci_upper'],
                alpha=0.2, color='#333333', zorder=2)

# OCR = 1 参考线 (ln(1) = 0)
ax.axhline(y=0, color='#999999', linewidth=0.8, linestyle='--', zorder=2, label='OCR = 1')

# 标注城市
for city_full, city_short in annotate_cities.items():
    row = df_a1[df_a1['city'] == city_full]
    if len(row) == 1:
        x_pt = row['ln_Pop'].values[0]
        y_pt = row['ln_OCR'].values[0]
        ax.annotate(city_short, (x_pt, y_pt), fontsize=5.5,
                    fontfamily='Heiti TC',
                    xytext=(5, 4), textcoords='offset points',
                    color='#333333', zorder=5)

# 图例
legend_handles = [Line2D([0], [0], marker='o', color='w',
                         markerfacecolor=REGION_COLORS[r], markersize=4.5, label=r)
                  for r in REGION_ORDER]
legend_handles.append(Line2D([0], [0], color='#999999', linestyle='--', linewidth=0.8, label='OCR = 1'))

ax.legend(handles=legend_handles, loc='upper right', frameon=True,
          framealpha=0.9, edgecolor='#cccccc', prop={'family': 'Heiti TC', 'size': 5.5})

ax.set_xlabel('ln(Population / 10k)', fontsize=7)
ax.set_ylabel('ln(OCR)', fontsize=7)
ax.set_title(f'a  Scaling law: OCR ~ Pop$^{{-\\alpha}}$\n'
             f'($\\alpha$ = {alpha:.3f}, R$^2$ = {model_a1.rsquared:.3f}, '
             f'p = {model_a1.pvalues.iloc[1]:.1e})',
             fontsize=7, loc='left', fontweight='bold')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(width=0.5)
for spine in ax.spines.values():
    spine.set_linewidth(0.5)

# --- Panel b: 标度指数对比 ---
ax2 = axes[1]
scaling_names = ['$\\beta_{GDP}$', '$\\beta_K$', '$\\beta_V$', '$\\beta_Q$', '$\\beta_{OCR}$']
scaling_vals = [beta_GDP, beta_K, beta_V, beta_Q, model_a1.params.iloc[1]]
scaling_ses = [model_gdp.bse.iloc[1], model_k.bse.iloc[1], model_v.bse.iloc[1],
               model_a2.bse.iloc[1], model_a1.bse.iloc[1]]
bar_colors = ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#E69F00']

x_pos = np.arange(len(scaling_names))
bars = ax2.bar(x_pos, scaling_vals, yerr=[1.96*s for s in scaling_ses],
               color=bar_colors, width=0.6, edgecolor='white', linewidth=0.5,
               capsize=2, error_kw={'linewidth': 0.8})

# 参考线
ax2.axhline(y=1.0, color='#999999', linewidth=0.6, linestyle=':', label='Linear scaling')
ax2.axhline(y=0.0, color='#333333', linewidth=0.4)

# Bettencourt GDP 参考
ax2.axhline(y=1.15, color='#0072B2', linewidth=0.6, linestyle='--', alpha=0.5)
ax2.annotate('Bettencourt\nGDP~1.15', xy=(0, 1.15), fontsize=4.5, color='#0072B2',
             xytext=(-0.4, 1.25), alpha=0.7)

ax2.set_xticks(x_pos)
ax2.set_xticklabels(scaling_names, fontsize=6.5)
ax2.set_ylabel('Scaling exponent ($\\beta$)', fontsize=7)
ax2.set_title('b  Scaling exponents comparison', fontsize=7, loc='left', fontweight='bold')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.tick_params(width=0.5)
for spine in ax2.spines.values():
    spine.set_linewidth(0.5)

# 数值标注
for i, (v, s) in enumerate(zip(scaling_vals, scaling_ses)):
    ax2.text(i, v + 1.96*s + 0.03, f'{v:.2f}', ha='center', va='bottom', fontsize=5.5, color='#333333')

plt.tight_layout(w_pad=2)
plt.savefig(FIG_OUT, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
rpt(f'图表已保存: {FIG_OUT}')

# ============================================================
# Source Data 输出
# ============================================================
source_df = df_a1[['city', 'region4', 'city_tier', 'pop_10k', 'gdp_100m',
                    'OCR_w1', 'Q_w1', 'K_100m', 'V_100m', 'ln_Pop', 'ln_OCR',
                    'ln_Q', 'ln_GDP', 'ln_K', 'ln_V']].copy()
source_df.to_csv(SOURCE_OUT, index=False, encoding='utf-8-sig')
rpt(f'Source data 已保存: {SOURCE_OUT}')
rpt()


# ############################################################
# GO / NO-GO 判定
# ############################################################
rpt('=' * 72)
rpt('GO / NO-GO 判定')
rpt('=' * 72)
rpt()

criteria = []
# 1. alpha 显著性 p < 0.01
p_alpha = model_a1.pvalues.iloc[1]
c1 = p_alpha < 0.01
criteria.append(('alpha 显著性 (p < 0.01)', c1, f'p = {p_alpha:.2e}', '必须'))

# 2. R2 > 0.3
r2_main = model_a1.rsquared
c2 = r2_main > 0.3
criteria.append(('R-squared > 0.3', c2, f'R2 = {r2_main:.4f}', '期望'))

# 3. 分区域 alpha 稳定性 < 30%
if alphas_region:
    all_a = [v['alpha'] for v in alphas_region.values()]
    mean_a = np.mean(all_a)
    max_dev_pct = max(abs(a - mean_a) / abs(mean_a) for a in all_a) * 100
    c3 = max_dev_pct < 30
    criteria.append(('区域 alpha 稳定 (变化<30%)', c3, f'最大偏差 = {max_dev_pct:.1f}%', '期望'))

# 4. 控制变量后 alpha 仍显著
p_ctrl = model_b2.pvalues.iloc[1]
c4 = p_ctrl < 0.01
criteria.append(('控制变量后 alpha 显著', c4, f'p = {p_ctrl:.2e}', '必须'))

rpt(f'{"条件":<35} {"结果":<20} {"判定":<8} {"级别":<6}')
rpt('-' * 69)
must_pass = True
for name, passed, detail, level in criteria:
    status = 'PASS' if passed else 'FAIL'
    rpt(f'{name:<35} {detail:<20} {status:<8} {level}')
    if level == '必须' and not passed:
        must_pass = False

rpt()
must_criteria = sum(1 for _, p, _, l in criteria if l == '必须' and p)
must_total = sum(1 for _, _, _, l in criteria if l == '必须')
expect_criteria = sum(1 for _, p, _, l in criteria if l == '期望' and p)
expect_total = sum(1 for _, _, _, l in criteria if l == '期望')

rpt(f'必须条件: {must_criteria}/{must_total} 通过')
rpt(f'期望条件: {expect_criteria}/{expect_total} 通过')
rpt()

if must_pass and expect_criteria >= expect_total * 0.5:
    verdict = 'GO'
    rpt(f'>>> 最终判定: **{verdict}** <<<')
    rpt(f'OCR 标度律成立，alpha = {alpha:.4f}，可作为 Nature 正刊论文的核心发现。')
elif must_pass:
    verdict = 'CONDITIONAL GO'
    rpt(f'>>> 最终判定: **{verdict}** <<<')
    rpt(f'OCR 标度律基本成立 (alpha = {alpha:.4f})，但部分期望条件未满足，需补充论证。')
else:
    verdict = 'NO-GO'
    rpt(f'>>> 最终判定: **{verdict}** <<<')
    rpt(f'OCR 标度律检验未通过必须条件，不建议作为核心突破口。')

rpt()
rpt(f'理论意义: 大城市人口聚集带来更高效的资本利用 (alpha = {alpha:.4f})，')
rpt(f'小城市因人口不足而出现系统性过度建设，这一标度律为城市更新')
rpt(f'政策提供了定量基准。')

# 保存报告
with open(SCRIPT_OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
rpt()
rpt(f'报告已保存: {SCRIPT_OUT}')
rpt('分析完成。')
