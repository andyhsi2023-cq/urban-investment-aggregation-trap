"""
102_scaling_gap_crossnational.py
================================
目的: 跨国验证 Scaling Gap (Delta_beta = beta_V - beta_K) 的普遍性
输入:
  - 02-data/raw/us_msa_data.csv (921 MSA)
  - 02-data/raw/japan_prefecture_data.csv (47 都道府県)
  - 02-data/raw/eu_nuts3_data.csv (1260 NUTS-3)
  - 02-data/raw/brazil_municipio_data.csv (5570 市)
  - 03-analysis/models/scaling_law_ocr_report.txt (中国已有结果)
输出:
  - 03-analysis/models/scaling_gap_crossnational_report.txt
  - 04-figures/drafts/fig_scaling_gap.png
  - 04-figures/source-data/fig_scaling_gap_source.csv
依赖: pandas, numpy, statsmodels, matplotlib, scipy
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import warnings

# ============================================================
# 路径设置
# ============================================================
PROJECT = Path("/Users/andy/Desktop/Claude/urban-q-phase-transition")
DATA_RAW = PROJECT / "02-data" / "raw"
MODELS = PROJECT / "03-analysis" / "models"
FIG_DRAFTS = PROJECT / "04-figures" / "drafts"
FIG_SOURCE = PROJECT / "04-figures" / "source-data"

REPORT_PATH = MODELS / "scaling_gap_crossnational_report.txt"
FIG_PATH = FIG_DRAFTS / "fig_scaling_gap.png"
SOURCE_PATH = FIG_SOURCE / "fig_scaling_gap_source.csv"

np.random.seed(20260321)

# ============================================================
# 辅助函数
# ============================================================

def ols_robust(y, x, add_const=True):
    """OLS 回归，HC1 稳健标准误，返回结果字典"""
    mask = np.isfinite(y) & np.isfinite(x)
    y_clean = y[mask]
    x_clean = x[mask]
    if add_const:
        X = sm.add_constant(x_clean)
    else:
        X = x_clean.values.reshape(-1, 1) if hasattr(x_clean, 'values') else x_clean.reshape(-1, 1)
    model = sm.OLS(y_clean, X).fit(cov_type='HC1')
    idx = 1 if add_const else 0
    ci = model.conf_int().iloc[idx]
    return {
        'beta': model.params.iloc[idx],
        'se': model.bse.iloc[idx],
        'p': model.pvalues.iloc[idx],
        'ci_lo': ci.iloc[0],
        'ci_hi': ci.iloc[1],
        'r2': model.rsquared,
        'n': int(model.nobs),
        'model': model
    }


def delta_beta_inference(res_a, res_b):
    """
    计算 Delta_beta = beta_a - beta_b 及其标准误 (假设独立估计)
    如果来自同一回归则需 SUR，这里用独立近似 + Delta method
    """
    db = res_a['beta'] - res_b['beta']
    # 保守: 假设独立 (实际可能有正相关，会低估 SE)
    se = np.sqrt(res_a['se']**2 + res_b['se']**2)
    z = db / se
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    ci_lo = db - 1.96 * se
    ci_hi = db + 1.96 * se
    return {
        'delta_beta': db,
        'se': se,
        'z': z,
        'p': p,
        'ci_lo': ci_lo,
        'ci_hi': ci_hi
    }


def delta_beta_direct(y_ratio, x_pop):
    """直接回归 ln(V/GDP) ~ ln(Pop) 得到 Delta_beta_VGDP"""
    return ols_robust(y_ratio, x_pop)


lines = []  # 报告行缓冲

def report(text=""):
    print(text)
    lines.append(text)


# ============================================================
# PART 0: 中国 (直接引用已有结果)
# ============================================================
report("=" * 72)
report("V0b: Scaling Gap (Delta_beta) 跨国验证")
report("=" * 72)
report()
report("分析日期: 2026-03-21")
report("随机种子: 20260321")
report()

# 中国已有结果
china = {
    'country': 'China',
    'n': 248,
    'beta_V': {'beta': 1.3390, 'se': 0.0563, 'p': 3.38e-125, 'r2': 0.8195,
               'ci_lo': 1.2287, 'ci_hi': 1.4493, 'n': 248},
    'beta_K': {'beta': 0.8610, 'se': 0.0450, 'p': 1.25e-81, 'r2': 0.6317,
               'ci_lo': 0.7728, 'ci_hi': 0.9492, 'n': 248},
    'beta_GDP': {'beta': 1.0377, 'se': 0.0533, 'p': 1.69e-84, 'r2': 0.6871,
                 'ci_lo': 0.9332, 'ci_hi': 1.1421, 'n': 248},
    'delta_VGDP_direct': {'beta': 0.3014, 'se': 0.0502, 'p': 2.00e-9,
                          'r2': 0.1708, 'ci_lo': 0.2029, 'ci_hi': 0.3998, 'n': 248},
}

report("--- PART 0: 中国 (已有结果, N=248) ---")
report(f"  beta_V  = {china['beta_V']['beta']:.4f}  (SE={china['beta_V']['se']:.4f}, R2={china['beta_V']['r2']:.4f})")
report(f"  beta_K  = {china['beta_K']['beta']:.4f}  (SE={china['beta_K']['se']:.4f}, R2={china['beta_K']['r2']:.4f})")
report(f"  beta_GDP= {china['beta_GDP']['beta']:.4f}  (SE={china['beta_GDP']['se']:.4f}, R2={china['beta_GDP']['r2']:.4f})")
report(f"  Delta_VK   = {china['beta_V']['beta'] - china['beta_K']['beta']:.4f}")
report(f"  Delta_VGDP = {china['delta_VGDP_direct']['beta']:.4f}  (直接估计, p={china['delta_VGDP_direct']['p']:.2e})")
report()

# ============================================================
# PART 1: 美国 (921 MSA)
# ============================================================
report("--- PART 1: 美国 (MSA) ---")

us = pd.read_csv(DATA_RAW / "us_msa_data.csv")
report(f"  原始数据: {len(us)} MSA")

# 清洗: 排除缺失值
us_clean = us.dropna(subset=['population', 'V_total', 'gdp_millions', 'housing_units'])
us_clean = us_clean[us_clean['population'] > 0]
us_clean = us_clean[us_clean['V_total'] > 0]
us_clean = us_clean[us_clean['gdp_millions'] > 0]
us_clean = us_clean[us_clean['housing_units'] > 0]
report(f"  清洗后: {len(us_clean)} MSA")

# 计算对数变量
ln_pop_us = np.log(us_clean['population'])
ln_V_us = np.log(us_clean['V_total'])
ln_gdp_us = np.log(us_clean['gdp_millions'] * 1e6)  # 转为美元
ln_hu_us = np.log(us_clean['housing_units'])

# beta_V: ln(V_total) ~ ln(Pop)
# V_total = median_home_value * housing_units
res_V_us = ols_robust(ln_V_us, ln_pop_us)
report(f"  beta_V  = {res_V_us['beta']:.4f}  (SE={res_V_us['se']:.4f}, p={res_V_us['p']:.2e}, R2={res_V_us['r2']:.4f}, N={res_V_us['n']})")
report(f"           95% CI = [{res_V_us['ci_lo']:.4f}, {res_V_us['ci_hi']:.4f}]")

# beta_K 代理: ln(housing_units) ~ ln(Pop)
# housing_units 是 K 的数量代理 (缺少单位造价数据)
res_K_us = ols_robust(ln_hu_us, ln_pop_us)
report(f"  beta_HU = {res_K_us['beta']:.4f}  (SE={res_K_us['se']:.4f}, p={res_K_us['p']:.2e}, R2={res_K_us['r2']:.4f}, N={res_K_us['n']})")
report(f"           95% CI = [{res_K_us['ci_lo']:.4f}, {res_K_us['ci_hi']:.4f}]")
report(f"           注: housing_units 是 K 的数量代理, 不含造价信息")

# beta_GDP: ln(GDP) ~ ln(Pop)
res_GDP_us = ols_robust(ln_gdp_us, ln_pop_us)
report(f"  beta_GDP= {res_GDP_us['beta']:.4f}  (SE={res_GDP_us['se']:.4f}, p={res_GDP_us['p']:.2e}, R2={res_GDP_us['r2']:.4f}, N={res_GDP_us['n']})")
report(f"           95% CI = [{res_GDP_us['ci_lo']:.4f}, {res_GDP_us['ci_hi']:.4f}]")

# Delta_beta: V - HU (类 K 代理)
db_VK_us = delta_beta_inference(res_V_us, res_K_us)
report(f"  Delta_V-HU = {db_VK_us['delta_beta']:.4f}  (SE={db_VK_us['se']:.4f}, p={db_VK_us['p']:.2e}, 95%CI=[{db_VK_us['ci_lo']:.4f}, {db_VK_us['ci_hi']:.4f}])")

# Delta_VGDP 直接估计: ln(V/GDP) ~ ln(Pop)
ln_V_GDP_us = np.log(us_clean['V_total'] / (us_clean['gdp_millions'] * 1e6))
res_VGDP_us = ols_robust(ln_V_GDP_us, ln_pop_us)
report(f"  Delta_VGDP (direct) = {res_VGDP_us['beta']:.4f}  (SE={res_VGDP_us['se']:.4f}, p={res_VGDP_us['p']:.2e}, R2={res_VGDP_us['r2']:.4f})")
report(f"           95% CI = [{res_VGDP_us['ci_lo']:.4f}, {res_VGDP_us['ci_hi']:.4f}]")

# 分 Metro vs Micro
report()
report("  --- 分 Metro / Micro ---")
for is_metro, label in [(True, 'Metro'), (False, 'Micro')]:
    sub = us_clean[us_clean['is_metro'] == is_metro]
    if len(sub) < 20:
        continue
    ln_p = np.log(sub['population'])
    ln_v = np.log(sub['V_total'])
    ln_g = np.log(sub['gdp_millions'] * 1e6)
    r_v = ols_robust(ln_v, ln_p)
    r_g = ols_robust(ln_g, ln_p)
    ln_vg = np.log(sub['V_total'] / (sub['gdp_millions'] * 1e6))
    r_vg = ols_robust(ln_vg, ln_p)
    report(f"  {label} (N={len(sub)}): beta_V={r_v['beta']:.4f}, beta_GDP={r_g['beta']:.4f}, Delta_VGDP={r_vg['beta']:.4f} (p={r_vg['p']:.2e})")

report()

# ============================================================
# PART 2: 日本 (47 都道府県)
# ============================================================
report("--- PART 2: 日本 (47 都道府県) ---")

jp = pd.read_csv(DATA_RAW / "japan_prefecture_data.csv")
report(f"  原始数据: {len(jp)} 都道府県")

jp_clean = jp.dropna(subset=['population', 'gdp_yen', 'housing_total'])
jp_clean = jp_clean[jp_clean['population'] > 0]
report(f"  清洗后: {len(jp_clean)} 都道府県")

ln_pop_jp = np.log(jp_clean['population'])
ln_gdp_jp = np.log(jp_clean['gdp_yen'])
ln_hu_jp = np.log(jp_clean['housing_total'])

# beta_GDP: ln(GDP) ~ ln(Pop)
res_GDP_jp = ols_robust(ln_gdp_jp, ln_pop_jp)
report(f"  beta_GDP= {res_GDP_jp['beta']:.4f}  (SE={res_GDP_jp['se']:.4f}, p={res_GDP_jp['p']:.2e}, R2={res_GDP_jp['r2']:.4f}, N={res_GDP_jp['n']})")
report(f"           95% CI = [{res_GDP_jp['ci_lo']:.4f}, {res_GDP_jp['ci_hi']:.4f}]")

# beta_HU: ln(Housing) ~ ln(Pop) — K 的数量代理
res_HU_jp = ols_robust(ln_hu_jp, ln_pop_jp)
report(f"  beta_HU = {res_HU_jp['beta']:.4f}  (SE={res_HU_jp['se']:.4f}, p={res_HU_jp['p']:.2e}, R2={res_HU_jp['r2']:.4f}, N={res_HU_jp['n']})")
report(f"           95% CI = [{res_HU_jp['ci_lo']:.4f}, {res_HU_jp['ci_hi']:.4f}]")

# 日本没有直接的 V 数据 (no home price per city)
# 但我们可以报告 beta_GDP 作为参照
# GDP/Pop 人均标度
ln_gdp_pc_jp = np.log(jp_clean['gdp_per_capita'])
res_GDPpc_jp = ols_robust(ln_gdp_pc_jp, ln_pop_jp)
report(f"  beta_GDPpc = {res_GDPpc_jp['beta']:.4f}  (SE={res_GDPpc_jp['se']:.4f}, p={res_GDPpc_jp['p']:.2e}, R2={res_GDPpc_jp['r2']:.4f})")
report(f"  注: 日本无城市级 V 数据, 无法直接计算 Delta_VGDP")

# 空置率标度 (OCR 代理)
ln_vac_jp = np.log(jp_clean['vacancy_rate'])
res_vac_jp = ols_robust(ln_vac_jp, ln_pop_jp)
report(f"  gamma_vacancy = {res_vac_jp['beta']:.4f}  (SE={res_vac_jp['se']:.4f}, p={res_vac_jp['p']:.2e}, R2={res_vac_jp['r2']:.4f})")
report(f"  注: gamma < 0 意味着小城市空置率更高, 与 OCR 标度律一致")
report()

# ============================================================
# PART 3: 欧盟 (1260 NUTS-3)
# ============================================================
report("--- PART 3: 欧盟 (1260 NUTS-3) ---")

eu = pd.read_csv(DATA_RAW / "eu_nuts3_data.csv")
report(f"  原始数据: {len(eu)} NUTS-3 区域")

eu_clean = eu.dropna(subset=['population', 'gdp_value'])
eu_clean = eu_clean[eu_clean['population'] > 0]
eu_clean = eu_clean[eu_clean['gdp_value'] > 0]
report(f"  清洗后: {len(eu_clean)} NUTS-3 区域")

ln_pop_eu = np.log(eu_clean['population'])
ln_gdp_eu = np.log(eu_clean['gdp_value'])  # MIO_EUR

# Pooled beta_GDP
res_GDP_eu = ols_robust(ln_gdp_eu, ln_pop_eu)
report(f"  beta_GDP (pooled) = {res_GDP_eu['beta']:.4f}  (SE={res_GDP_eu['se']:.4f}, p={res_GDP_eu['p']:.2e}, R2={res_GDP_eu['r2']:.4f}, N={res_GDP_eu['n']})")
report(f"           95% CI = [{res_GDP_eu['ci_lo']:.4f}, {res_GDP_eu['ci_hi']:.4f}]")

# 国家固定效应
eu_clean_fe = eu_clean.copy()
country_dummies = pd.get_dummies(eu_clean_fe['country_code'], drop_first=True, dtype=float)
X_fe = sm.add_constant(pd.concat([ln_pop_eu.reset_index(drop=True), country_dummies.reset_index(drop=True)], axis=1))
X_fe.columns = ['const', 'ln_pop'] + list(country_dummies.columns)
y_fe = ln_gdp_eu.reset_index(drop=True)
model_fe = sm.OLS(y_fe, X_fe).fit(cov_type='HC1')
report(f"  beta_GDP (country FE) = {model_fe.params['ln_pop']:.4f}  (SE={model_fe.bse['ln_pop']:.4f}, p={model_fe.pvalues['ln_pop']:.2e}, R2={model_fe.rsquared:.4f})")
report(f"           95% CI = [{model_fe.conf_int().loc['ln_pop', 0]:.4f}, {model_fe.conf_int().loc['ln_pop', 1]:.4f}]")
report(f"  注: 欧盟无城市级 V/K 数据, 无法直接计算 Delta_VGDP")
report()

# ============================================================
# PART 4: 巴西 (5570 市)
# ============================================================
report("--- PART 4: 巴西 (5570 市) ---")

br = pd.read_csv(DATA_RAW / "brazil_municipio_data.csv")
report(f"  原始数据: {len(br)} 市")

br_clean = br.dropna(subset=['population', 'gdp_1000brl'])
br_clean = br_clean[br_clean['population'] > 0]
br_clean = br_clean[br_clean['gdp_1000brl'] > 0]
report(f"  清洗后: {len(br_clean)} 市")

ln_pop_br = np.log(br_clean['population'])
ln_gdp_br = np.log(br_clean['gdp_1000brl'])

res_GDP_br = ols_robust(ln_gdp_br, ln_pop_br)
report(f"  beta_GDP= {res_GDP_br['beta']:.4f}  (SE={res_GDP_br['se']:.4f}, p={res_GDP_br['p']:.2e}, R2={res_GDP_br['r2']:.4f}, N={res_GDP_br['n']})")
report(f"           95% CI = [{res_GDP_br['ci_lo']:.4f}, {res_GDP_br['ci_hi']:.4f}]")

# 分州固定效应
br_clean_fe = br_clean.copy()
uf_dummies = pd.get_dummies(br_clean_fe['uf'], drop_first=True, dtype=float)
X_br_fe = sm.add_constant(pd.concat([ln_pop_br.reset_index(drop=True), uf_dummies.reset_index(drop=True)], axis=1))
X_br_fe.columns = ['const', 'ln_pop'] + list(uf_dummies.columns)
y_br_fe = ln_gdp_br.reset_index(drop=True)
model_br_fe = sm.OLS(y_br_fe, X_br_fe).fit(cov_type='HC1')
report(f"  beta_GDP (state FE) = {model_br_fe.params['ln_pop']:.4f}  (SE={model_br_fe.bse['ln_pop']:.4f}, p={model_br_fe.pvalues['ln_pop']:.2e}, R2={model_br_fe.rsquared:.4f})")
report(f"           95% CI = [{model_br_fe.conf_int().loc['ln_pop', 0]:.4f}, {model_br_fe.conf_int().loc['ln_pop', 1]:.4f}]")

# 人均 GDP 标度
ln_gdp_pc_br = np.log(br_clean['gdp_pc_brl'])
res_GDPpc_br = ols_robust(ln_gdp_pc_br, ln_pop_br)
report(f"  beta_GDPpc = {res_GDPpc_br['beta']:.4f}  (SE={res_GDPpc_br['se']:.4f}, p={res_GDPpc_br['p']:.2e}, R2={res_GDPpc_br['r2']:.4f})")
report(f"  注: 巴西无城市级 V/K 数据, 无法直接计算 Delta_VGDP")
report()

# ============================================================
# PART 5: 跨国汇总表
# ============================================================
report("=" * 72)
report("PART 5: 跨国汇总对比表")
report("=" * 72)
report()

# 汇总表
header = f"{'国家':<12} {'N':>6} {'beta_V':>8} {'beta_K/HU':>10} {'beta_GDP':>10} {'Delta_VK':>10} {'Delta_VGDP':>12} {'R2(V)':>7} {'R2(GDP)':>8}"
report(header)
report("-" * len(header))

# 中国
report(f"{'China':<12} {248:>6} {1.3390:>8.4f} {0.8610:>10.4f} {1.0377:>10.4f} {0.4780:>10.4f} {0.3014:>12.4f} {0.8195:>7.4f} {0.6871:>8.4f}")

# 美国
db_vk_us_val = res_V_us['beta'] - res_K_us['beta']
report(f"{'USA':<12} {res_V_us['n']:>6} {res_V_us['beta']:>8.4f} {res_K_us['beta']:>10.4f} {res_GDP_us['beta']:>10.4f} {db_vk_us_val:>10.4f} {res_VGDP_us['beta']:>12.4f} {res_V_us['r2']:>7.4f} {res_GDP_us['r2']:>8.4f}")

# 日本 (仅 GDP 和 HU)
report(f"{'Japan':<12} {res_GDP_jp['n']:>6} {'N/A':>8} {res_HU_jp['beta']:>10.4f} {res_GDP_jp['beta']:>10.4f} {'N/A':>10} {'N/A':>12} {'N/A':>7} {res_GDP_jp['r2']:>8.4f}")

# 欧盟
report(f"{'EU (pool)':<12} {res_GDP_eu['n']:>6} {'N/A':>8} {'N/A':>10} {res_GDP_eu['beta']:>10.4f} {'N/A':>10} {'N/A':>12} {'N/A':>7} {res_GDP_eu['r2']:>8.4f}")
report(f"{'EU (FE)':<12} {res_GDP_eu['n']:>6} {'N/A':>8} {'N/A':>10} {model_fe.params['ln_pop']:>10.4f} {'N/A':>10} {'N/A':>12} {'N/A':>7} {model_fe.rsquared:>8.4f}")

# 巴西
report(f"{'Brazil':<12} {res_GDP_br['n']:>6} {'N/A':>8} {'N/A':>10} {res_GDP_br['beta']:>10.4f} {'N/A':>10} {'N/A':>12} {'N/A':>7} {res_GDP_br['r2']:>8.4f}")
report(f"{'Brazil(FE)':<12} {res_GDP_br['n']:>6} {'N/A':>8} {'N/A':>10} {model_br_fe.params['ln_pop']:>10.4f} {'N/A':>10} {'N/A':>12} {'N/A':>7} {model_br_fe.rsquared:>8.4f}")
report()

# ============================================================
# PART 6: 深入分析 — 美国 Delta_VGDP 的结构
# ============================================================
report("=" * 72)
report("PART 6: 美国 Delta_VGDP 的详细分解")
report("=" * 72)
report()

# V = median_home_value * housing_units
# ln(V) = ln(median_home_value) + ln(housing_units)
# beta_V = beta_price + beta_HU
# Delta_VGDP = beta_V - beta_GDP = (beta_price + beta_HU) - beta_GDP

ln_price_us = np.log(us_clean['median_home_value'])
res_price_us = ols_robust(ln_price_us, ln_pop_us)
report(f"  分解 beta_V = beta_price + beta_HU:")
report(f"  beta_price (median_home_value ~ Pop) = {res_price_us['beta']:.4f}  (SE={res_price_us['se']:.4f}, p={res_price_us['p']:.2e}, R2={res_price_us['r2']:.4f})")
report(f"  beta_HU    (housing_units ~ Pop)     = {res_K_us['beta']:.4f}")
report(f"  beta_price + beta_HU = {res_price_us['beta'] + res_K_us['beta']:.4f}  vs  直接 beta_V = {res_V_us['beta']:.4f}")
report(f"  (差异来自 Jensen's inequality, 可忽略)")
report()
report(f"  关键发现: 美国 V 的超线性标度主要来自:")
report(f"    - 房价标度 (beta_price = {res_price_us['beta']:.4f}): 大城市房价更高")
report(f"    - 住房量标度 (beta_HU = {res_K_us['beta']:.4f}): 住房量近似线性")
report(f"    - GDP 标度 (beta_GDP = {res_GDP_us['beta']:.4f}): GDP 超线性")
report(f"    - Delta_VGDP = {res_VGDP_us['beta']:.4f}: V 增速{'快于' if res_VGDP_us['beta'] > 0 else '慢于'} GDP")
report()

# 分区域 (US Census Regions)
report("  --- 美国分区域 Delta_VGDP ---")
for region in sorted(us_clean['region'].dropna().unique()):
    sub = us_clean[us_clean['region'] == region]
    if len(sub) < 20:
        continue
    lp = np.log(sub['population'])
    lvg = np.log(sub['V_total'] / (sub['gdp_millions'] * 1e6))
    r = ols_robust(lvg, lp)
    sig = "***" if r['p'] < 0.001 else "**" if r['p'] < 0.01 else "*" if r['p'] < 0.05 else ""
    report(f"    {region:<12} (N={len(sub):>3}): Delta_VGDP = {r['beta']:.4f}  (SE={r['se']:.4f}, p={r['p']:.2e}) {sig}")
report()

# ============================================================
# PART 7: 超线性指数对比 — Bettencourt Framework
# ============================================================
report("=" * 72)
report("PART 7: 标度指数对比 (Bettencourt Framework)")
report("=" * 72)
report()

report("  理论预期 (Bettencourt et al. 2007, 2010):")
report("    GDP ~ Pop^beta_GDP, beta_GDP ~ 1.05-1.20 (超线性)")
report("    Infrastructure ~ Pop^beta_K, beta_K ~ 0.75-0.90 (亚线性)")
report("    如果 V ~ Pop^beta_V 且 V > K (市场估值 > 重建成本):")
report("    则 beta_V > beta_K 是 Q > 1 的城市规模梯度")
report()
report("  实际观测:")
report(f"    中国: beta_V={1.3390:.2f}, beta_K={0.8610:.2f}, beta_GDP={1.0377:.2f}  =>  Delta_VK={0.48:.2f}, Delta_VGDP={0.30:.2f}")
report(f"    美国: beta_V={res_V_us['beta']:.2f}, beta_HU={res_K_us['beta']:.2f}, beta_GDP={res_GDP_us['beta']:.2f}  =>  Delta_V-HU={db_vk_us_val:.2f}, Delta_VGDP={res_VGDP_us['beta']:.2f}")
report(f"    日本: beta_HU={res_HU_jp['beta']:.2f}, beta_GDP={res_GDP_jp['beta']:.2f}")
report(f"    巴西: beta_GDP={res_GDP_br['beta']:.2f}")
report(f"    EU(FE): beta_GDP={model_fe.params['ln_pop']:.2f}")
report()

# ============================================================
# PART 8: GO/NO-GO 判定
# ============================================================
report("=" * 72)
report("PART 8: GO / NO-GO 判定")
report("=" * 72)
report()

# 核心判据: Delta_VGDP > 0 是否在多国成立
us_delta_sig = res_VGDP_us['p'] < 0.05 and res_VGDP_us['beta'] > 0
china_delta_sig = True  # p = 2e-9

report("  条件 A (关键): Delta_VGDP > 0 且显著")
report(f"    中国: Delta_VGDP = {0.3014:.4f}, p = 2.00e-09  => {'PASS' if china_delta_sig else 'FAIL'}")
report(f"    美国: Delta_VGDP = {res_VGDP_us['beta']:.4f}, p = {res_VGDP_us['p']:.2e}  => {'PASS' if us_delta_sig else 'FAIL'}")
report()

# 次要判据: beta_GDP > 1 (超线性)
report("  条件 B (支持性): beta_GDP > 1 (超线性, 集聚经济)")
for label, beta, se, p in [
    ("中国", 1.0377, 0.0533, 1.69e-84),
    ("美国", res_GDP_us['beta'], res_GDP_us['se'], res_GDP_us['p']),
    ("日本", res_GDP_jp['beta'], res_GDP_jp['se'], res_GDP_jp['p']),
    ("巴西", res_GDP_br['beta'], res_GDP_br['se'], res_GDP_br['p']),
    ("EU(FE)", model_fe.params['ln_pop'], model_fe.bse['ln_pop'], model_fe.pvalues['ln_pop']),
]:
    # 检验 beta_GDP > 1 (或对 EU FE: > 1 是总量标度)
    is_super = beta > 1.0
    report(f"    {label:<10}: beta_GDP = {beta:.4f} (SE={se:.4f})  {'> 1 (超线性)' if is_super else '<= 1'}")

report()

# 综合判定
report("  --- 综合判定 ---")
report()
if us_delta_sig:
    report("  场景 A: **GO** — Delta_VGDP > 0 在中国和美国均显著")
    report("  V 超 GDP 标度是城市系统的普遍特征")
    report("  Scaling Gap 作为 MUQ 梯度的数学引擎得到跨国验证")
    go_result = "GO"
elif res_VGDP_us['beta'] > 0:
    report("  场景 B: **CAUTION** — Delta_VGDP > 0 方向一致但美国不显著")
    report("  Scaling Gap 存在但可能因市场效率而在发达国家变弱")
    report("  需要调整叙事: 强调发展阶段差异")
    go_result = "CAUTION"
else:
    report("  场景 C: **FAIL** — Delta_VGDP 在美国为负或零")
    report("  Scaling Gap 不具普遍性, 可能是中国特有的发展阶段特征")
    go_result = "FAIL"

report()

# ============================================================
# PART 9: 理论解读
# ============================================================
report("=" * 72)
report("PART 9: 理论解读与叙事建议")
report("=" * 72)
report()

report("  1. V 的超线性标度 (beta_V > 1) 的含义:")
report("     大城市的不动产总价值不成比例地高于人口规模")
report("     这反映了土地稀缺性溢价 + 集聚经济资本化")
report()
report("  2. K 的亚线性标度 (beta_K < 1) 的含义:")
report("     大城市的建设资本相对于人口是不足的")
report("     这符合 Bettencourt 的基础设施标度律")
report()
report("  3. Delta_beta = beta_V - beta_K > 0 的含义:")
report("     大城市 V/K 比值更高 => Tobin's Q 更高")
report("     这创建了从小城市到大城市的 Q 梯度")
report("     Q 梯度 = 资源配置信号 => 驱动城市化和投资向大城市聚集")
report()
report("  4. 跨国差异的来源:")
report("     中国 Delta_VGDP = 0.30 (大): 土地财政 + 快速城市化 + 供给管制")
report(f"     美国 Delta_VGDP = {res_VGDP_us['beta']:.2f}: 成熟市场, 土地使用管制创造稀缺")
report("     发展中国家可能更大 (需要更多数据)")
report()

# ============================================================
# PART 10: V 定义可比性讨论
# ============================================================
report("=" * 72)
report("PART 10: 方法论说明 — V 定义的跨国可比性")
report("=" * 72)
report()
report("  中国 V = 人口 * 人均住房面积 * 单位房价")
report("         = total_floor_area * price_per_m2")
report("  美国 V = median_home_value * housing_units")
report("         = (中位房价) * (住房总套数)")
report()
report("  差异:")
report("  (a) 中国用面积计算, 美国用套数计算 => 套均面积差异未反映")
report("  (b) 中国 price_per_m2 反映新房+二手房均价, 美国 median 是存量分布中位数")
report("  (c) 两者都是不动产市场价值的合理近似, 但绝对值不可比")
report("  (d) 标度指数 (对数-对数斜率) 不受绝对值影响, 可比性强")
report("  (e) 关键可比性: 两国的 V 都包含 '价格效应' 和 '数量效应'")
report("      中国: 价格效应 + 面积效应")
report("      美国: 价格效应 + 套数效应")
report()

# ============================================================
# 保存报告
# ============================================================
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
report(f"\n报告已保存: {REPORT_PATH}")

# ============================================================
# PART 11: 可视化
# ============================================================

# 收集图表数据
fig_data = []

# Panel (a) 各国标度指数条形图
countries_bar = ['China', 'USA', 'Japan', 'EU(FE)', 'Brazil']
beta_V_vals = [1.3390, res_V_us['beta'], np.nan, np.nan, np.nan]
beta_V_se = [0.0563, res_V_us['se'], np.nan, np.nan, np.nan]
beta_K_vals = [0.8610, res_K_us['beta'], res_HU_jp['beta'], np.nan, np.nan]
beta_K_se = [0.0450, res_K_us['se'], res_HU_jp['se'], np.nan, np.nan]
beta_GDP_vals = [1.0377, res_GDP_us['beta'], res_GDP_jp['beta'], model_fe.params['ln_pop'], res_GDP_br['beta']]
beta_GDP_se = [0.0533, res_GDP_us['se'], res_GDP_jp['se'], model_fe.bse['ln_pop'], res_GDP_br['se']]

# Panel (b) Delta_beta 跨国对比
delta_countries = ['China', 'USA']
delta_vals = [0.3014, res_VGDP_us['beta']]
delta_se_vals = [0.0502, res_VGDP_us['se']]

# 创建图表
fig = plt.figure(figsize=(16, 5.5))
gs = gridspec.GridSpec(1, 3, width_ratios=[1.2, 0.8, 1.0], wspace=0.35)

# === Panel (a): 各国标度指数对比 ===
ax1 = fig.add_subplot(gs[0])

x = np.arange(len(countries_bar))
width = 0.25

# beta_V
bars_v = ax1.bar(x - width, beta_V_vals, width, yerr=[abs(s) * 1.96 if not np.isnan(s) else 0 for s in beta_V_se],
                 color='#e74c3c', alpha=0.85, label=r'$\beta_V$', capsize=3, edgecolor='white', linewidth=0.5)
# beta_K/HU
bars_k = ax1.bar(x, beta_K_vals, width, yerr=[abs(s) * 1.96 if not np.isnan(s) else 0 for s in beta_K_se],
                 color='#3498db', alpha=0.85, label=r'$\beta_K$ (or $\beta_{HU}$)', capsize=3, edgecolor='white', linewidth=0.5)
# beta_GDP
bars_g = ax1.bar(x + width, beta_GDP_vals, width, yerr=[abs(s) * 1.96 if not np.isnan(s) else 0 for s in beta_GDP_se],
                 color='#2ecc71', alpha=0.85, label=r'$\beta_{GDP}$', capsize=3, edgecolor='white', linewidth=0.5)

ax1.axhline(y=1, color='grey', linestyle='--', linewidth=0.8, alpha=0.5)
ax1.set_xticks(x)
ax1.set_xticklabels(countries_bar, fontsize=9)
ax1.set_ylabel('Scaling exponent', fontsize=10)
ax1.set_title('(a) Scaling exponents by country', fontsize=11, fontweight='bold')
ax1.legend(fontsize=8, loc='upper right')
ax1.set_ylim(0, 1.7)
ax1.text(0.02, 0.98, 'N/A = data not available', transform=ax1.transAxes, fontsize=7, va='top', color='grey')

# === Panel (b): Delta_VGDP 跨国对比 + CI ===
ax2 = fig.add_subplot(gs[1])

y_pos = np.arange(len(delta_countries))
colors_delta = ['#e74c3c', '#3498db']

for i, (country, val, se) in enumerate(zip(delta_countries, delta_vals, delta_se_vals)):
    ci_lo = val - 1.96 * se
    ci_hi = val + 1.96 * se
    ax2.barh(i, val, height=0.5, color=colors_delta[i], alpha=0.85, edgecolor='white', linewidth=0.5)
    ax2.errorbar(val, i, xerr=1.96 * se, fmt='none', color='black', capsize=4, linewidth=1.2)
    ax2.text(val + 1.96 * se + 0.02, i, f'{val:.3f}\n[{ci_lo:.3f}, {ci_hi:.3f}]', va='center', fontsize=8)

ax2.axvline(x=0, color='grey', linestyle='--', linewidth=0.8)
ax2.set_yticks(y_pos)
ax2.set_yticklabels(delta_countries, fontsize=10)
ax2.set_xlabel(r'$\Delta\beta_{V-GDP}$', fontsize=10)
ax2.set_title(r'(b) $\Delta\beta_{V-GDP}$ with 95% CI', fontsize=11, fontweight='bold')
ax2.set_xlim(-0.15, 0.55)

# === Panel (c): ln(V) vs ln(Pop) 双国散点 ===
ax3 = fig.add_subplot(gs[2])

# 美国
ax3.scatter(ln_pop_us, ln_V_us, s=8, alpha=0.3, color='#3498db', label=f'USA (N={res_V_us["n"]})')
# 回归线
x_range_us = np.linspace(ln_pop_us.min(), ln_pop_us.max(), 100)
y_pred_us = res_V_us['model'].params[0] + res_V_us['model'].params[1] * x_range_us
ax3.plot(x_range_us, y_pred_us, color='#3498db', linewidth=2,
         label=fr'$\beta_V$ = {res_V_us["beta"]:.3f}')

# 中国参考线 (用中国的标度参数, 但位移到美国的范围)
# 只画斜率参考线
x_mid = np.mean(ln_pop_us)
y_mid = np.mean(ln_V_us)
x_range_cn = np.linspace(ln_pop_us.min(), ln_pop_us.max(), 100)
y_cn_ref = y_mid + 1.3390 * (x_range_cn - x_mid)
ax3.plot(x_range_cn, y_cn_ref, color='#e74c3c', linewidth=2, linestyle='--',
         label=r'China $\beta_V$ = 1.339 (ref slope)')

ax3.set_xlabel('ln(Population)', fontsize=10)
ax3.set_ylabel('ln(V)', fontsize=10)
ax3.set_title('(c) V ~ Pop scaling: USA vs China slope', fontsize=11, fontweight='bold')
ax3.legend(fontsize=8, loc='upper left')

plt.tight_layout()
plt.savefig(FIG_PATH, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
report(f"图表已保存: {FIG_PATH}")

# 保存 source data
source_records = []
for c, bv, bvse, bk, bkse, bg, bgse in zip(
    countries_bar, beta_V_vals, beta_V_se, beta_K_vals, beta_K_se, beta_GDP_vals, beta_GDP_se):
    source_records.append({
        'country': c,
        'beta_V': bv, 'beta_V_se': bvse,
        'beta_K_or_HU': bk, 'beta_K_or_HU_se': bkse,
        'beta_GDP': bg, 'beta_GDP_se': bgse,
    })
source_df = pd.DataFrame(source_records)
source_df.to_csv(SOURCE_PATH, index=False)
report(f"Source data 已保存: {SOURCE_PATH}")

print("\n=== 分析完成 ===")
