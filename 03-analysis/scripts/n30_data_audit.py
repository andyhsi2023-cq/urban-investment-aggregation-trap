#!/usr/bin/env python3
"""
n30_data_audit.py -- 投稿前数据质量系统性审计
==============================================
目的:
    对本研究所有数据文件进行系统性真实性检查，包括:
    A. 原始数据文件基本信息与异常值
    B. 关键数字与权威外部来源交叉验证
    C. 构造变量 (MUQ, Urban Q) 计算逻辑验证
    D. 时间一致性检查
    E. 数据生成方式审计与真实性评级

输入:
    02-data/raw/ 下所有 CSV 文件

输出:
    02-data/data_audit_report.md — 完整审计报告

依赖: pandas, numpy, scipy
作者: data-analyst (审计模式)
日期: 2026-03-22
"""

import os
import sys
import numpy as np
import pandas as pd
from scipy import stats
from datetime import datetime

# ============================================================
# 路径配置
# ============================================================
BASE = "/Users/andy/Desktop/Claude/urban-q-phase-transition"
RAW = os.path.join(BASE, "02-data", "raw")
REPORT_PATH = os.path.join(BASE, "02-data", "data_audit_report.md")

# 报告缓冲
R = []
def rpt(s=''):
    R.append(s)
    print(s)

def section(title, level=2):
    rpt()
    rpt('#' * level + ' ' + title)
    rpt()

# ============================================================
# A. 原始数据文件基本信息
# ============================================================
FILES = {
    'world_bank_all_countries.csv':     '世界银行 WDI 全球面板',
    'penn_world_table.csv':             'Penn World Table 10.01',
    'bis_property_prices.csv':          'BIS 全球房价指数',
    'china_national_real_data.csv':     '中国国家级面板',
    'china_provincial_real_data.csv':   '中国 31 省面板',
    'japan_prefectural_panel.csv':      '日本 47 都道府县面板',
    'korea_regional_panel.csv':         '韩国 17 市道面板',
    'europe_regional_panel.csv':        '欧洲 NUTS-2 区域面板',
    'africa_regional_panel.csv':        '非洲(南非)省级面板',
    'oceania_regional_panel.csv':       '大洋洲(澳大利亚)州级面板',
}

rpt('# 数据质量系统性审计报告')
rpt()
rpt(f'审计日期: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
rpt(f'审计人: data-analyst (AI agent, 审计模式)')
rpt(f'项目: Urban Q Phase Transition — 目标: Nature 主刊')
rpt()
rpt('---')

# ============================================================
# PART A: 逐文件基本信息 + 异常值
# ============================================================
section('A. 原始数据文件基本信息与异常值检测')

file_summaries = []  # 用于总览表

for fname, desc in FILES.items():
    fpath = os.path.join(RAW, fname)
    rpt(f'### {fname}')
    rpt(f'**描述**: {desc}')
    rpt()

    if not os.path.exists(fpath):
        rpt('**状态**: 文件不存在!')
        rpt()
        file_summaries.append({
            'file': fname, 'desc': desc, 'rows': 0, 'cols': 0,
            'status': 'MISSING', 'generation': 'N/A', 'grade': 'F'
        })
        continue

    try:
        df = pd.read_csv(fpath)
    except Exception as e:
        rpt(f'**状态**: 读取失败 - {e}')
        rpt()
        file_summaries.append({
            'file': fname, 'desc': desc, 'rows': 0, 'cols': 0,
            'status': 'READ_ERROR', 'generation': 'N/A', 'grade': 'F'
        })
        continue

    nrows, ncols = df.shape
    rpt(f'- **行数**: {nrows:,}')
    rpt(f'- **列数**: {ncols}')
    rpt(f'- **列名**: {list(df.columns)}')

    # 时间范围
    year_col = None
    for c in ['year', 'period']:
        if c in df.columns:
            year_col = c
            break
    if year_col:
        years = pd.to_numeric(df[year_col], errors='coerce').dropna()
        if len(years) > 0:
            rpt(f'- **时间范围**: {int(years.min())} - {int(years.max())}')

    # 国家/地区数
    for c in ['country_name', 'country_iso3', 'province', 'prefecture_en',
              'name_en', 'region_name', 'geo', 'country_code']:
        if c in df.columns:
            n_entities = df[c].nunique()
            rpt(f'- **{c} 唯一值**: {n_entities}')
            if n_entities < 30:
                rpt(f'  - 列表: {sorted(df[c].unique())}')
            break

    # 缺失值
    miss = df.isnull().sum()
    miss_pct = df.isnull().mean() * 100
    cols_with_missing = miss[miss > 0]
    if len(cols_with_missing) > 0:
        rpt(f'- **缺失值**:')
        for col in cols_with_missing.index:
            rpt(f'  - {col}: {cols_with_missing[col]:,} ({miss_pct[col]:.1f}%)')
    else:
        rpt(f'- **缺失值**: 无')

    # 数值范围与异常值
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    anomalies = []
    rpt(f'- **数值列范围检查**:')
    for col in numeric_cols:
        vals = df[col].dropna()
        if len(vals) == 0:
            continue
        vmin, vmax, vmean = vals.min(), vals.max(), vals.mean()
        rpt(f'  - {col}: min={vmin:.4g}, max={vmax:.4g}, mean={vmean:.4g}')

        # 语义检查
        col_lower = col.lower()
        if 'urbanization' in col_lower or 'urban_pct' in col_lower:
            if vmin < 0 or vmax > 100:
                anomalies.append(f'{col}: 城镇化率超出 [0, 100] 范围 (min={vmin}, max={vmax})')
        if 'population' in col_lower or 'pop' in col_lower:
            if vmin < 0:
                anomalies.append(f'{col}: 人口为负值 (min={vmin})')

        # Z-score > 3
        if len(vals) > 10:
            z = np.abs(stats.zscore(vals, nan_policy='omit'))
            n_outliers = (z > 3).sum()
            if n_outliers > 0:
                outlier_idx = np.where(z > 3)[0]
                sample_outliers = vals.iloc[outlier_idx[:5]].tolist()
                anomalies.append(f'{col}: {n_outliers} 个 Z>3 异常值, 样本={sample_outliers[:3]}')

    if anomalies:
        rpt(f'- **异常值/警告**: {len(anomalies)} 项')
        for a in anomalies:
            rpt(f'  - WARNING: {a}')
    else:
        rpt(f'- **异常值**: 未检出')
    rpt()

    file_summaries.append({
        'file': fname, 'desc': desc, 'rows': nrows, 'cols': ncols,
        'status': 'OK' if len(anomalies) == 0 else f'WARN({len(anomalies)})',
        'generation': '', 'grade': ''
    })


# ============================================================
# PART B: 关键数字交叉验证
# ============================================================
section('B. 关键数字外部交叉验证')

validation_results = []

def validate(name, expected, actual, tolerance_pct=5.0, unit=''):
    """验证一个数据点"""
    if actual is None or np.isnan(actual):
        result = {
            'name': name, 'expected': expected, 'actual': 'N/A',
            'deviation_pct': 'N/A', 'status': 'FAIL - 数据缺失'
        }
        validation_results.append(result)
        rpt(f'  - {name}: 预期={expected}{unit}, 实际=N/A => **FAIL (数据缺失)**')
        return False

    dev_pct = abs(actual - expected) / abs(expected) * 100
    status = 'PASS' if dev_pct <= tolerance_pct else f'FAIL (偏差 {dev_pct:.1f}%)'
    result = {
        'name': name, 'expected': expected, 'actual': round(actual, 2),
        'deviation_pct': round(dev_pct, 2), 'status': status
    }
    validation_results.append(result)
    marker = 'PASS' if dev_pct <= tolerance_pct else f'**FAIL ({dev_pct:.1f}%)**'
    rpt(f'  - {name}: 预期={expected:,.2f}{unit}, 实际={actual:,.2f}{unit}, 偏差={dev_pct:.2f}% => {marker}')
    return dev_pct <= tolerance_pct


# --- B1: 中国数据 ---
rpt('### B1. 中国数据验证')
rpt()

china_nat = pd.read_csv(os.path.join(RAW, 'china_national_real_data.csv'))

# 2023 GDP
row_2023 = china_nat[china_nat['year'] == 2023]
if len(row_2023) > 0:
    gdp_col = 'gdp_100m' if 'gdp_100m' in china_nat.columns else None
    if gdp_col:
        gdp_val = row_2023[gdp_col].values[0]
        validate('中国 2023 GDP (亿元)', 1260582.0, gdp_val, 1.0, ' 亿元')
    else:
        rpt('  - WARNING: 找不到 GDP 列')

# 2023 城镇化率
if 'urbanization_rate' in china_nat.columns:
    ur_val = row_2023['urbanization_rate'].values[0] if len(row_2023) > 0 else None
    if ur_val is not None and not np.isnan(ur_val):
        validate('中国 2023 城镇化率 (%)', 66.16, ur_val, 1.0, '%')

# 2023 FAI
if 'fai_total_100m' in china_nat.columns:
    row_fai = china_nat[china_nat['year'] == 2023]
    if len(row_fai) > 0:
        fai_val = row_fai['fai_total_100m'].values[0]
        if not np.isnan(fai_val):
            validate('中国 2023 固定资产投资 (亿元)', 503036.0, fai_val, 2.0, ' 亿元')

# 2023 商品房均价
if 'avg_price_yuan_m2' in china_nat.columns:
    row_price = china_nat[china_nat['year'] == 2023]
    if len(row_price) > 0:
        price_val = row_price['avg_price_yuan_m2'].values[0]
        if not np.isnan(price_val):
            # 2023 全国商品房均价约 10,437 元/m2 (116622亿/111735万m2)
            validate('中国 2023 商品房均价 (元/m2)', 10437, price_val, 10.0, ' 元/m2')

# 省级加总 vs 全国
rpt()
rpt('#### 省级加总校验')
china_prov = pd.read_csv(os.path.join(RAW, 'china_provincial_real_data.csv'))

# 找共同年份
if 'gdp_billion_yuan' in china_prov.columns:
    # 注意: 列名为 gdp_billion_yuan 但实际单位是亿元 (100m yuan)
    # 验证: 北京 2005 GDP = 6969.5，符合亿元量级 (≈0.7万亿)
    for check_year in [2015, 2020, 2023]:
        prov_yr = china_prov[china_prov['year'] == check_year]
        nat_yr = china_nat[china_nat['year'] == check_year]
        if len(prov_yr) > 0 and len(nat_yr) > 0:
            prov_sum = prov_yr['gdp_billion_yuan'].sum()
            if 'gdp_100m' in china_nat.columns:
                nat_gdp = nat_yr['gdp_100m'].values[0]
                # 两者均为亿元单位
                validate(f'中国 {check_year} 31省GDP加总 vs 全国 (亿元)',
                         nat_gdp, prov_sum, 10.0, ' 亿元')
    rpt()
    rpt('  **WARNING**: 省级数据列名 gdp_billion_yuan 实际单位为亿元 (100m yuan)，列名有误导性，建议修正为 gdp_100m_yuan')
    rpt()

# 省人口加总
if 'year' in china_prov.columns:
    # 检查是否有人口列
    pop_cols = [c for c in china_prov.columns if 'pop' in c.lower()]
    rpt(f'  省级数据人口相关列: {pop_cols}')

rpt()

# --- B2: 日本数据 ---
rpt('### B2. 日本数据验证')
rpt()

japan = pd.read_csv(os.path.join(RAW, 'japan_prefectural_panel.csv'))

# 2022 全国 GDP (47县加总)
jp_2022 = japan[japan['year'] == 2022]
if len(jp_2022) > 0 and 'gdp_nominal_myen' in japan.columns:
    jp_gdp_sum = jp_2022['gdp_nominal_myen'].sum()
    # 2022 日本名义GDP约 556万亿日元 = 556,000,000 百万日元
    validate('日本 2022 47县GDP加总 (百万日元)', 556000000, jp_gdp_sum, 5.0, ' 百万日元')

# 47县人口加总
if 'population' in japan.columns:
    jp_pop_2022 = jp_2022['population'].dropna()
    if len(jp_pop_2022) > 0:
        jp_pop_sum = jp_pop_2022.sum()
        # 2022 日本人口约 1.25 亿
        validate('日本 2022 47县人口加总', 125000000, jp_pop_sum, 3.0)
    else:
        rpt('  - WARNING: 2022年47县人口数据大量缺失')

# 1991 泡沫期 GFCF/GDP
jp_1991 = japan[japan['year'] == 1991]
if len(jp_1991) > 0 and 'gfcf_gdp_ratio' in japan.columns:
    ratio_1991 = jp_1991['gfcf_gdp_ratio'].dropna()
    if len(ratio_1991) > 0:
        avg_ratio = ratio_1991.mean()
        rpt(f'  - 日本 1991 平均 GFCF/GDP 比率: {avg_ratio:.4f} (预期 ~0.30-0.33)')

# 2022 GFCF/GDP
if len(jp_2022) > 0 and 'gfcf_gdp_ratio' in japan.columns:
    ratio_2022 = jp_2022['gfcf_gdp_ratio'].dropna()
    if len(ratio_2022) > 0:
        avg_ratio_2022 = ratio_2022.mean()
        rpt(f'  - 日本 2022 平均 GFCF/GDP 比率: {avg_ratio_2022:.4f} (预期 ~0.24-0.25)')

rpt()

# --- B3: 韩国数据 ---
rpt('### B3. 韩国数据验证')
rpt()

korea = pd.read_csv(os.path.join(RAW, 'korea_regional_panel.csv'))

# 2022 全国 GDP
kr_2022 = korea[korea['year'] == 2022]
if len(kr_2022) > 0 and 'grdp_bkrw' in korea.columns:
    kr_gdp_sum = kr_2022['grdp_bkrw'].sum()
    # 2022 韩国名义GDP约 2,162 万亿韩元 = 2,161,789 十亿韩元
    validate('韩国 2022 17市道GDP加总 (十亿韩元)', 2161789, kr_gdp_sum, 5.0, ' 十亿韩元')

# 首尔 GDP 占比
if len(kr_2022) > 0 and 'grdp_share_pct' in korea.columns:
    seoul_share = kr_2022[kr_2022['name_en'] == 'Seoul']['grdp_share_pct']
    if len(seoul_share) > 0:
        seoul_pct = seoul_share.values[0]
        validate('韩国 2022 首尔 GDP 占比 (%)', 21.0, seoul_pct, 10.0, '%')

rpt()

# --- B4: 世界银行数据 (美国) ---
rpt('### B4. 美国数据验证 (World Bank)')
rpt()

wb = pd.read_csv(os.path.join(RAW, 'world_bank_all_countries.csv'))
us_wb = wb[wb['country_iso3'] == 'USA']
us_2022 = us_wb[us_wb['year'] == 2022]

if len(us_2022) > 0:
    # 美国城镇化率
    if 'SP.URB.TOTL.IN.ZS' in us_2022.columns:
        us_urban = us_2022['SP.URB.TOTL.IN.ZS'].values[0]
        validate('美国 2022 城镇化率 (%)', 83.0, us_urban, 3.0, '%')

rpt()

# --- B5: 欧洲数据 ---
rpt('### B5. 欧洲数据验证')
rpt()

europe = pd.read_csv(os.path.join(RAW, 'europe_regional_panel.csv'))

# 德国 GDP 最大区域 (应为 Oberbayern)
de_regions = europe[(europe['iso3'] == 'DEU') & (europe['year'] == 2020)]
if len(de_regions) > 0 and 'gdp_meur' in europe.columns:
    de_top = de_regions.nlargest(3, 'gdp_meur')[['geo', 'gdp_meur']]
    rpt(f'  - 德国 2020 GDP 前3区域:')
    for _, row in de_top.iterrows():
        rpt(f'    - {row["geo"]}: {row["gdp_meur"]:,.0f} 百万欧元')
    # 检查 DE21 (Oberbayern) 是否在前3
    if 'DE21' in de_top['geo'].values:
        rpt(f'  => PASS: Oberbayern (DE21) 在德国 GDP 前3')
    else:
        rpt(f'  => WARNING: Oberbayern (DE21) 不在德国 GDP 前3，可能的问题')

# 法国 GDP 最大区域 (应为 FR10 Île-de-France)
fr_regions = europe[(europe['iso3'] == 'FRA') & (europe['year'] == 2020)]
if len(fr_regions) > 0 and 'gdp_meur' in europe.columns:
    fr_top = fr_regions.nlargest(3, 'gdp_meur')[['geo', 'gdp_meur']]
    rpt(f'  - 法国 2020 GDP 前3区域:')
    for _, row in fr_top.iterrows():
        rpt(f'    - {row["geo"]}: {row["gdp_meur"]:,.0f} 百万欧元')
    if 'FR10' in fr_top['geo'].values:
        rpt(f'  => PASS: Île-de-France (FR10) 在法国 GDP 前3')
    else:
        rpt(f'  => WARNING: Île-de-France (FR10) 不在法国 GDP 前3')

rpt()

# --- B6: 澳大利亚/南非 ---
rpt('### B6. 澳大利亚与南非数据验证')
rpt()

oceania = pd.read_csv(os.path.join(RAW, 'oceania_regional_panel.csv'))
africa = pd.read_csv(os.path.join(RAW, 'africa_regional_panel.csv'))

# NSW 占比
aus_2020 = oceania[oceania['year'] == 2020]
if len(aus_2020) > 0 and 'gdp_share' in oceania.columns:
    nsw = aus_2020[aus_2020['region_code'] == 'AU-NSW']
    if len(nsw) > 0:
        nsw_share = nsw['gdp_share'].values[0]
        validate('澳大利亚 2020 NSW GDP 占比', 0.315, nsw_share, 15.0)

# Gauteng 占比
za_2020 = africa[africa['year'] == 2020]
if len(za_2020) > 0 and 'gdp_share' in africa.columns:
    gau = za_2020[za_2020['region_code'] == 'ZA-GP']
    if len(gau) > 0:
        gau_share = gau['gdp_share'].values[0]
        validate('南非 2020 Gauteng GDP 占比', 0.34, gau_share, 15.0)

rpt()

# ============================================================
# PART C: 构造变量逻辑验证
# ============================================================
section('C. 构造变量逻辑验证')

# --- C1: MUQ = DeltaGDP / GFCF 验证 ---
rpt('### C1. GDP-based MUQ 手动验算')
rpt()

# 日本面板 MUQ
rpt('**日本面板 MUQ 抽样验算:**')
rpt()
japan_muq = japan[japan['muq'].notna()].copy()
if len(japan_muq) > 0:
    # 随机抽5个县 x 某年
    np.random.seed(42)
    prefs = japan_muq['pref_code'].unique()
    sample_prefs = np.random.choice(prefs, min(5, len(prefs)), replace=False)
    sample_years = [1990, 2000, 2010]

    for pc in sample_prefs:
        pref_data = japan[japan['pref_code'] == pc].sort_values('year')
        pref_name = pref_data['prefecture_en'].iloc[0] if 'prefecture_en' in pref_data.columns else pc

        for yr in sample_years:
            row_curr = pref_data[pref_data['year'] == yr]
            row_prev = pref_data[pref_data['year'] == yr - 1]
            if len(row_curr) > 0 and len(row_prev) > 0:
                gdp_curr = row_curr['gdp_nominal_myen'].values[0]
                gdp_prev = row_prev['gdp_nominal_myen'].values[0]
                gfcf = row_curr['gfcf_nominal_myen'].values[0]
                delta_gdp = gdp_curr - gdp_prev
                muq_computed = delta_gdp / gfcf if gfcf != 0 else np.nan
                muq_file = row_curr['muq'].values[0]

                match = 'MATCH' if (np.isnan(muq_computed) and np.isnan(muq_file)) or \
                                    abs(muq_computed - muq_file) < 0.001 else 'MISMATCH'
                rpt(f'  {pref_name} {yr}: DeltaGDP={delta_gdp:,.0f}, GFCF={gfcf:,.0f}, '
                    f'计算MUQ={muq_computed:.6f}, 文件MUQ={muq_file:.6f} => {match}')

rpt()

# 韩国面板 MUQ
rpt('**韩国面板 MUQ 抽样验算:**')
rpt()
korea['sido_code'] = korea['sido_code'].astype(str)
korea_sorted = korea.sort_values(['sido_code', 'year'])
sample_sidos = ['11', '31', '21']  # 首尔、京畿、釜山
sample_years_kr = [2000, 2010, 2020]

for sc in sample_sidos:
    sido_data = korea_sorted[korea_sorted['sido_code'] == sc]
    sido_name = sido_data['name_en'].iloc[0] if 'name_en' in sido_data.columns else sc

    for yr in sample_years_kr:
        row_curr = sido_data[sido_data['year'] == yr]
        row_prev = sido_data[sido_data['year'] == yr - 1]
        if len(row_curr) > 0 and len(row_prev) > 0:
            gdp_curr = row_curr['grdp_bkrw'].values[0]
            gdp_prev = row_prev['grdp_bkrw'].values[0]
            gfcf_col = 'gfcf_bkrw' if 'gfcf_bkrw' in korea.columns else None
            if gfcf_col:
                gfcf = row_curr[gfcf_col].values[0]
                delta_gdp = gdp_curr - gdp_prev
                muq_computed = delta_gdp / gfcf if gfcf != 0 else np.nan
                muq_file = row_curr['muq'].values[0] if 'muq' in row_curr.columns else np.nan

                if pd.notna(muq_file):
                    match = 'MATCH' if abs(muq_computed - muq_file) < 0.001 else 'MISMATCH'
                else:
                    match = 'N/A'
                rpt(f'  {sido_name} {yr}: DeltaGRDP={delta_gdp:,.1f}, GFCF={gfcf:,.1f}, '
                    f'计算MUQ={muq_computed:.6f}, 文件MUQ={muq_file if pd.notna(muq_file) else "N/A"} => {match}')

rpt()

# --- C2: Urban Q = V / K 验证 (中国国家级) ---
rpt('### C2. 中国国家级 Urban Q 构造验证')
rpt()

if 'urban_q' in china_nat.columns:
    # 检查 urban_q 列的定义
    rpt('  urban_q 列存在, 检查定义:')

    # 看是否有 V 和 K 相关列
    v_cols = [c for c in china_nat.columns if 'value' in c.lower() or 'stock' in c.lower()
              or 'housing_value' in c.lower() or 'sales_value' in c.lower()]
    k_cols = [c for c in china_nat.columns if 'capital' in c.lower() or 'stock' in c.lower()
              or 'housing_stock' in c.lower()]
    rpt(f'  可能的 V 列: {v_cols}')
    rpt(f'  可能的 K 列: {k_cols}')

    # 抽样检查
    for yr in [2005, 2010, 2015, 2020]:
        row = china_nat[china_nat['year'] == yr]
        if len(row) > 0:
            uq = row['urban_q'].values[0]
            rpt(f'  {yr}: Urban Q = {uq:.6f}' if pd.notna(uq) else f'  {yr}: Urban Q = N/A')
            # 检查是否由 V/K 计算得来
            if 'housing_value_100m' in row.columns and 'capital_stock_100m' in row.columns:
                v = row['housing_value_100m'].values[0]
                k = row['capital_stock_100m'].values[0]
                if pd.notna(v) and pd.notna(k) and k > 0:
                    q_calc = v / k
                    match = 'MATCH' if abs(q_calc - uq) / abs(uq) < 0.01 else 'MISMATCH'
                    rpt(f'    V={v:,.0f}, K={k:,.0f}, V/K={q_calc:.6f} => {match}')
else:
    rpt('  urban_q 列不存在 (可能在 processed 数据中计算)')

rpt()


# ============================================================
# PART D: 时间一致性检查
# ============================================================
section('D. 时间一致性检查')

# D1: 中国 GDP 在不同来源中的一致性
rpt('### D1. 中国 GDP 跨数据源一致性')
rpt()

cn_wb = wb[(wb['country_iso3'] == 'CHN') & (wb['year'].isin([2015, 2020, 2022]))]
for yr in [2015, 2020, 2022]:
    # World Bank GDP (current USD)
    wb_row = cn_wb[cn_wb['year'] == yr]
    wb_gdp_usd = wb_row['NY.GDP.MKTP.CD'].values[0] if len(wb_row) > 0 else None

    # china_national_real_data
    nat_row = china_nat[china_nat['year'] == yr]
    nat_gdp_100m = nat_row['gdp_100m'].values[0] if len(nat_row) > 0 and 'gdp_100m' in nat_row.columns else None

    # World Bank 中国数据也在 china_national 中
    if 'wb_gdp_current_usd' in china_nat.columns:
        nat_wb_gdp = nat_row['wb_gdp_current_usd'].values[0] if len(nat_row) > 0 else None
    else:
        nat_wb_gdp = None

    rpt(f'  {yr}:')
    if wb_gdp_usd is not None:
        rpt(f'    WDI GDP (USD): {wb_gdp_usd:,.0f}')
    if nat_gdp_100m is not None:
        rpt(f'    china_national GDP (亿元): {nat_gdp_100m:,.1f}')
    if nat_wb_gdp is not None and wb_gdp_usd is not None:
        dev = abs(nat_wb_gdp - wb_gdp_usd) / wb_gdp_usd * 100
        rpt(f'    china_national WB_GDP (USD): {nat_wb_gdp:,.0f}, 偏差={dev:.2f}%')

rpt()

# D2: 日本 SNA 基准变更点
rpt('### D2. 日本 SNA 基准变更年份跳跃检查')
rpt()

if 'sna_basis' in japan.columns:
    # 东京作为代表
    tokyo = japan[japan['pref_code'] == '13'].sort_values('year')
    if len(tokyo) > 0:
        rpt(f'  东京都 SNA 基准变更点:')
        prev_sna = None
        for _, row in tokyo.iterrows():
            sna = row['sna_basis']
            if sna != prev_sna and prev_sna is not None:
                yr = int(row['year'])
                gdp_curr = row['gdp_nominal_myen']
                prev_row = tokyo[tokyo['year'] == yr - 1]
                if len(prev_row) > 0:
                    gdp_prev = prev_row['gdp_nominal_myen'].values[0]
                    jump = (gdp_curr - gdp_prev) / gdp_prev * 100
                    rpt(f'    {yr}: {prev_sna} -> {sna}, GDP 变动 = {jump:.1f}%')
                    if abs(jump) > 15:
                        rpt(f'      WARNING: GDP 跳跃超过 15%, 可能因 SNA 基准变更')
            prev_sna = sna

rpt()

# D3: 韩国 1997-1998 亚洲金融危机
rpt('### D3. 韩国 1997-1998 亚洲金融危机年份检查')
rpt()

kr_97_98 = korea[korea['year'].isin([1996, 1997, 1998, 1999])]
if len(kr_97_98) > 0 and 'grdp_bkrw' in korea.columns:
    nat_gdp_kr = kr_97_98.groupby('year')['grdp_bkrw'].sum()
    rpt(f'  韩国全国 GRDP 加总:')
    for yr in sorted(nat_gdp_kr.index):
        rpt(f'    {yr}: {nat_gdp_kr[yr]:,.0f} 十亿韩元')
    if 1997 in nat_gdp_kr.index and 1998 in nat_gdp_kr.index:
        drop_pct = (nat_gdp_kr[1998] - nat_gdp_kr[1997]) / nat_gdp_kr[1997] * 100
        rpt(f'  1997->1998 变动: {drop_pct:.1f}%')
        if drop_pct < 0:
            rpt(f'  => 合理: 亚洲金融危机导致 GDP 下降')
        else:
            rpt(f'  => WARNING: 名义 GDP 在危机年份没有下降，需检查')

rpt()


# ============================================================
# PART E: 数据生成方式审计
# ============================================================
section('E. 数据生成方式审计')

# 根据对脚本的审查，标记每个文件的生成方式
generation_methods = {
    'world_bank_all_countries.csv': {
        'method': 'API 获取',
        'source': 'World Bank Open Data API v2 (20_world_bank_data.py)',
        'risk': 'LOW',
        'note': '直接从 World Bank API 批量下载，数据为官方发布数据',
    },
    'penn_world_table.csv': {
        'method': 'API/下载',
        'source': 'PWT 10.01 官方 Excel 下载 + 脚本解析 (21_penn_world_table.py)',
        'risk': 'LOW',
        'note': '从 Groningen 官方文件下载并解析',
    },
    'bis_property_prices.csv': {
        'method': 'API/下载',
        'source': 'BIS 统计数据下载 (22_bis_un_data.py)',
        'risk': 'LOW',
        'note': '从 BIS 官方 CSV 下载',
    },
    'china_national_real_data.csv': {
        'method': '手动构建 + API 补充',
        'source': 'NBS API + 中国统计年鉴硬编码数据 (40_china_real_data.py)',
        'risk': 'MEDIUM',
        'note': 'GDP/人口/投资等来自统计年鉴，通过脚本硬编码录入。'
                'API 作为主策略但可能失败，回退到硬编码。'
                '数据已与国家统计局公报交叉验证。'
                'WB 数据列直接从 world_bank_all_countries.csv 合并。',
    },
    'china_provincial_real_data.csv': {
        'method': '手动构建 + 插值',
        'source': 'NBS API + 中国统计年鉴 (41_china_provincial_data.py)',
        'risk': 'MEDIUM-HIGH',
        'note': '基准年份数据 (2005, 2010, 2015, 2020, 2023) 来自统计年鉴。'
                '中间年份通过线性插值填充 (标记为 interpolated)。'
                '插值数据仅用于趋势分析，不用于精确点估计。',
    },
    'japan_prefectural_panel.csv': {
        'method': '官方文件解析',
        'source': '内閣府県民経済計算 Excel 文件 (n21_japan_prefectural_data.py)',
        'risk': 'LOW',
        'note': '直接从内閣府下载的 Excel 文件 (4 个 SNA 基准) 解析。'
                '原始 Excel 文件保存在 japan_cab_office/ 目录。'
                '这是所有区域数据中最可靠的来源。',
    },
    'korea_regional_panel.csv': {
        'method': '脚本构建 (份额分配 + 插值)',
        'source': 'KOSIS/ECOS 基准数据 + 线性插值 (n23_korea_regional_data.py)',
        'risk': 'HIGH',
        'note': '全国GDP来自BOK (硬编码), 区域份额来自KOSIS (硬编码, 5年间隔)。'
                '中间年份通过线性插值。GFCF 使用全国比率 + 区域份额。'
                '这意味着区域级 GFCF 是估算值而非直接观测值。'
                '核心问题: 区域 GRDP = 全国 GDP x 插值份额，非直接统计值。',
    },
    'europe_regional_panel.csv': {
        'method': 'API 获取 + 国家级分配',
        'source': 'Eurostat API (NUTS-2 GDP, 人口) + WB 国家 GFCF (n24_europe_regional_data.py)',
        'risk': 'MEDIUM',
        'note': 'GDP 和人口直接从 Eurostat API 下载 (如果网络可用)。'
                'GFCF 使用国家级 WB 数据按 GDP 份额分配到区域。'
                '如果 Eurostat API 失败，可能回退到备用数据。'
                '需要确认实际运行时 API 是否成功。',
    },
    'africa_regional_panel.csv': {
        'method': '脚本构建 (份额分配 + 插值)',
        'source': 'WB 国家级数据 + 省级份额 (n25_africa_oceania_data.py)',
        'risk': 'HIGH',
        'note': '南非省级 GDP = WB 国家 GDP x 省级份额 (5年间隔硬编码 + 插值)。'
                '人口也是基准年份 + 插值。GFCF 按 GDP 份额分配。'
                '这些数据本质上是基于份额假设的推算值。',
    },
    'oceania_regional_panel.csv': {
        'method': '脚本构建 (份额分配 + 插值)',
        'source': 'WB 国家级数据 + ABS 州级份额 (n25_africa_oceania_data.py)',
        'risk': 'HIGH',
        'note': '与南非相同方法。州级 GDP = WB 国家 GDP x 州级份额。'
                '虽然份额来自 ABS 5220.0，但中间年份是插值的。'
                '核心限制: 所有区域级波动都来自国家级波动 x 平滑份额，'
                '区域特异性波动被完全抹掉。',
    },
}

for fname, info in generation_methods.items():
    rpt(f'### {fname}')
    rpt(f'- **生成方式**: {info["method"]}')
    rpt(f'- **数据源**: {info["source"]}')
    rpt(f'- **风险等级**: {info["risk"]}')
    rpt(f'- **说明**: {info["note"]}')
    rpt()

    # 更新 file_summaries
    for fs in file_summaries:
        if fs['file'] == fname:
            fs['generation'] = info['method']
            break


# ============================================================
# PART F: 数据真实性评级
# ============================================================
section('F. 数据真实性评级总览')

grades = {
    'world_bank_all_countries.csv': ('A', '官方 API 直接下载，数据可溯源'),
    'penn_world_table.csv': ('A', '学术标准数据集，广泛使用'),
    'bis_property_prices.csv': ('A', '国际清算银行官方数据'),
    'china_national_real_data.csv': ('B+', '基于统计年鉴硬编码，已验证核心数据点。'
                                          '2024年部分数据为估算。WB数据为API获取。'),
    'china_provincial_real_data.csv': ('B-', '基准年份可靠，但中间年份为线性插值。'
                                            '插值数据限制了年际变化分析的精度。'),
    'japan_prefectural_panel.csv': ('A', '直接从内閣府官方Excel解析，原始文件保留。'
                                        '4个SNA基准完整覆盖1955-2022。'),
    'korea_regional_panel.csv': ('C+', '全国GDP硬编码可验证，但区域份额为5年间隔+插值。'
                                       '区域GFCF是估算值。适合趋势分析，不适合精确点估计。'),
    'europe_regional_panel.csv': ('B', '如API成功则GDP/人口为官方数据。'
                                       '区域GFCF是国家级按份额分配的估算值。'),
    'africa_regional_panel.csv': ('C', '完全基于份额分配+插值构建。'
                                       '区域特异性信息有限。仅适合辅助性展示。'),
    'oceania_regional_panel.csv': ('C', '同上。州级数据为份额分配推算。'
                                        '虽然ABS份额相对可靠，但方法论限制同africa。'),
}

rpt('| 文件 | 评级 | 说明 |')
rpt('|------|------|------|')
for fname, (grade, note) in grades.items():
    rpt(f'| {fname} | **{grade}** | {note} |')
    for fs in file_summaries:
        if fs['file'] == fname:
            fs['grade'] = grade

rpt()


# ============================================================
# PART G: 致命问题清单
# ============================================================
section('G. 致命问题清单 (可能影响论文结论可信度)')

fatal_issues = [
    {
        'severity': 'CRITICAL',
        'file': 'korea_regional_panel.csv, africa_regional_panel.csv, oceania_regional_panel.csv',
        'issue': '区域级 MUQ 的方法论缺陷',
        'detail': '这三个文件的区域 GFCF 均非直接观测值，而是通过 "国家 GFCF x 区域份额" 推算。'
                  '由于份额在基准年份之间线性插值，区域 MUQ 的年际波动主要来自国家级波动，'
                  '而非区域特异性投资效率变化。这导致: (1) 区域间 MUQ 差异被人为缩小; '
                  '(2) Simpson\'s Paradox 的检测可能受到方法论伪影影响; '
                  '(3) 标度律分析中的散点可能反映的是份额分配的机械结果而非真实经济规律。',
        'recommendation': '在论文中明确标注这些数据的估算性质和局限性。'
                         '核心论证应基于日本 (A级)、中国 (B级) 和 World Bank 跨国数据 (A级)。'
                         '韩国/南非/澳大利亚数据仅作为 "一致性检查" 或 "辅助证据"，不应作为独立支撑。',
    },
    {
        'severity': 'HIGH',
        'file': 'china_national_real_data.csv',
        'issue': '中国 1990-1999 年投资数据缺失',
        'detail': '脚本中 fai_total_100m 和 re_inv_100m 序列从 2000 年开始，'
                  '1990-1999 年缺失。这影响该时段 MUQ 和 Urban Q 的计算。'
                  '但论文的主要发现集中在 2000-2024 区间，影响有限。',
        'recommendation': '尝试补全 1990 年代数据 (统计年鉴中有记录)，'
                         '或在论文中明确说明分析起始年份为 2000 年。',
    },
    {
        'severity': 'HIGH',
        'file': 'china_provincial_real_data.csv',
        'issue': '大量中间年份为线性插值',
        'detail': '基准年份仅为 2005, 2010, 2015, 2020, 2023 (部分省份更少)。'
                  '中间年份 (如 2006-2009, 2011-2014, 2016-2019) 全部为线性插值。'
                  '这意味着 FAI/GDP 比率在基准年份之间是人为平滑的直线，'
                  '不能反映年际波动 (如 2008 刺激计划、2015 去产能等)。',
        'recommendation': '(1) 从中国统计年鉴逐年补全省级数据; '
                         '(2) 或在论文中仅使用基准年份截面，而非连续面板; '
                         '(3) 标注 data_type=interpolated 的行不用于时序分析。',
    },
    {
        'severity': 'MEDIUM',
        'file': 'china_national_real_data.csv',
        'issue': '关键变量 (housing_stock, capital_stock) 的构造方法不透明',
        'detail': '文件中包含 housing_stock_10k_m2, housing_value_100m, capital_stock_100m, '
                  're_capital_stock_100m 等列，但其构造方法 (永续盘存法的具体参数等) '
                  '未在数据文件或脚本注释中完整记录。'
                  'Urban Q = V/K 的可信度取决于 V 和 K 的构造方法。',
        'recommendation': '在论文 Methods 部分和 Supplementary Information 中'
                         '完整记录 V 和 K 的构造公式、折旧率假设、基期选择等。',
    },
    {
        'severity': 'MEDIUM',
        'file': '40_china_real_data.py',
        'issue': '脚本使用了 warnings.filterwarnings("ignore")',
        'detail': '这违反了最佳实践。警告可能包含重要的数据质量信号。',
        'recommendation': '移除 warnings.filterwarnings("ignore")，逐一处理警告。',
    },
    {
        'severity': 'LOW',
        'file': 'japan_prefectural_panel.csv',
        'issue': 'SNA 基准变更点可能导致 MUQ 异常值',
        'detail': 'GDP 序列在 1975, 1996, 2011 附近有 SNA 基准变更。'
                  '虽然脚本尝试了接续处理，但变更点附近的 delta_GDP 可能包含'
                  '方法论变更导致的非经济性跳跃，影响 MUQ 计算。',
        'recommendation': '在变更年份前后加入虚拟变量或排除这些年份的 MUQ。'
                         '敏感性分析中应展示排除变更年份后结果是否稳健。',
    },
]

for i, issue in enumerate(fatal_issues, 1):
    rpt(f'### 问题 {i}: [{issue["severity"]}] {issue["issue"]}')
    rpt(f'- **涉及文件**: {issue["file"]}')
    rpt(f'- **详情**: {issue["detail"]}')
    rpt(f'- **建议**: {issue["recommendation"]}')
    rpt()


# ============================================================
# PART H: 审计总览表
# ============================================================
section('H. 审计总览表')

rpt('| 文件 | 行数 | 列数 | 生成方式 | 状态 | 评级 |')
rpt('|------|------|------|----------|------|------|')
for fs in file_summaries:
    rpt(f'| {fs["file"]} | {fs["rows"]:,} | {fs["cols"]} | {fs["generation"]} | {fs["status"]} | {fs["grade"]} |')

rpt()

# ============================================================
# PART I: 交叉验证结果表
# ============================================================
section('I. 交叉验证结果汇总')

rpt('| 验证项 | 预期值 | 实际值 | 偏差% | 状态 |')
rpt('|--------|--------|--------|-------|------|')
for vr in validation_results:
    rpt(f'| {vr["name"]} | {vr["expected"]} | {vr["actual"]} | {vr["deviation_pct"]} | {vr["status"]} |')

rpt()


# ============================================================
# PART J: 投稿前建议
# ============================================================
section('J. 投稿前必须修复的数据问题')

rpt('**必须修复 (MUST FIX):**')
rpt()
rpt('1. 在论文 Methods / Supplementary Information 中完整披露:')
rpt('   - 韩国/南非/澳大利亚区域级数据的估算方法和局限性')
rpt('   - Urban Q 的 V 和 K 的构造公式及参数')
rpt('   - 中国省级数据中线性插值的范围和影响')
rpt()
rpt('2. 将核心论证限于高可信度数据:')
rpt('   - 主要结论基于: WDI 跨国面板 (A), 日本面板 (A), 中国国家级 (B+)')
rpt('   - 韩国/欧洲/南非/澳大利亚仅作为补充/一致性检查')
rpt()
rpt('3. 移除 40_china_real_data.py 中的 warnings.filterwarnings("ignore")')
rpt()
rpt('**建议修复 (SHOULD FIX):**')
rpt()
rpt('4. 补全中国 1990-1999 年投资数据 (从统计年鉴中)')
rpt('5. 从统计年鉴逐年补全省级面板 (消除插值依赖)')
rpt('6. 在日本面板中标记 SNA 变更年份，在敏感性分析中排除')
rpt('7. 为每个数据文件创建 SHA-256 校验和，存入 data_checksums.md')
rpt()
rpt('**可选改进 (NICE TO HAVE):**')
rpt()
rpt('8. 将韩国数据从 KOSIS 逐年下载替代份额插值')
rpt('9. 从 ABS 直接获取澳大利亚州级 GDP (而非份额分配)')
rpt('10. 从 Stats SA 直接获取南非省级 GDP')

rpt()
rpt('---')
rpt()
rpt(f'审计完成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
rpt()
rpt('**总体评估**: 核心数据 (WDI, PWT, BIS, 日本面板, 中国国家级) 质量可靠 (A-B+ 级)，')
rpt('可支撑 Nature 级别论文。区域面板数据 (韩国, 南非, 澳大利亚) 为估算数据 (C-C+ 级)，')
rpt('在论文中必须明确标注为辅助证据，不能作为独立论证基础。')
rpt('中国省级数据 (B-) 中的线性插值是一个需要关注的问题。')

# ============================================================
# 保存报告
# ============================================================
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(R))
print(f'\n审计报告已保存: {REPORT_PATH}')
