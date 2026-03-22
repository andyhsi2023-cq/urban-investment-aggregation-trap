#!/usr/bin/env python3
"""
n24_europe_regional_data.py -- 欧洲区域级面板数据获取与 MUQ 构建
=================================================================
目的:
    获取欧洲 NUTS-2 区域级 GDP + 人口多年面板数据 (2000-2022),
    结合国家级 GFCF (来自 World Bank), 构建区域 MUQ 估计,
    并进行标度律分析, 为论文提供亚洲和美国以外的数据支撑。

数据来源:
    A. Eurostat REST API / Bulk Download:
       - nama_10r_2gdp: NUTS-2 GDP (百万欧元, 2000-2022)
       - demo_r_pjangroup: NUTS-2 人口
    B. World Bank (已有): 国家级 GFCF (current USD)
       - 02-data/raw/world_bank_all_countries.csv
    C. BIS Property Prices (已有): 国家级房价指数
       - 02-data/raw/bis_property_prices.csv

输入:
    - 从 Eurostat API 直接下载 (网络)
    - 02-data/raw/world_bank_all_countries.csv (已有)
    - 02-data/raw/bis_property_prices.csv (已有)

输出:
    - 02-data/raw/europe_regional_panel.csv          (NUTS-2 面板)
    - 03-analysis/models/europe_regional_report.txt   (分析报告)

依赖: pandas, numpy, requests, gzip, statsmodels, scipy, matplotlib
"""

import os
import sys
import io
import gzip
import time
import numpy as np
import pandas as pd
import requests
import statsmodels.api as sm
from scipy import stats

# 随机种子
np.random.seed(42)

# ============================================================
# 路径配置
# ============================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
DATA_RAW = os.path.join(BASE, '02-data', 'raw')
DATA_PROC = os.path.join(BASE, '02-data', 'processed')
MODELS = os.path.join(BASE, '03-analysis', 'models')
FIGS = os.path.join(BASE, '04-figures', 'drafts')
SOURCE_DIR = os.path.join(BASE, '04-figures', 'source-data')

for d in [DATA_RAW, DATA_PROC, MODELS, FIGS, SOURCE_DIR]:
    os.makedirs(d, exist_ok=True)

report_lines = []
def rpt(s=''):
    report_lines.append(str(s))
    print(s)

def save_report():
    """保存报告到文件"""
    report_path = os.path.join(MODELS, 'europe_regional_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    print(f'\n报告已保存: {report_path}')

# ============================================================
# 国家代码映射
# ============================================================
# NUTS-2 前两位 -> ISO2 -> ISO3 (用于匹配 World Bank)
NUTS_TO_ISO2 = {
    'AT': 'AT', 'BE': 'BE', 'BG': 'BG', 'CY': 'CY', 'CZ': 'CZ',
    'DE': 'DE', 'DK': 'DK', 'EE': 'EE', 'EL': 'GR', 'ES': 'ES',
    'FI': 'FI', 'FR': 'FR', 'HR': 'HR', 'HU': 'HU', 'IE': 'IE',
    'IT': 'IT', 'LT': 'LT', 'LU': 'LU', 'LV': 'LV', 'MT': 'MT',
    'NL': 'NL', 'PL': 'PL', 'PT': 'PT', 'RO': 'RO', 'SE': 'SE',
    'SI': 'SI', 'SK': 'SK', 'NO': 'NO', 'CH': 'CH', 'UK': 'GB',
}

ISO2_TO_ISO3 = {
    'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'CY': 'CYP', 'CZ': 'CZE',
    'DE': 'DEU', 'DK': 'DNK', 'EE': 'EST', 'GR': 'GRC', 'ES': 'ESP',
    'FI': 'FIN', 'FR': 'FRA', 'HR': 'HRV', 'HU': 'HUN', 'IE': 'IRL',
    'IT': 'ITA', 'LT': 'LTU', 'LU': 'LUX', 'LV': 'LVA', 'MT': 'MLT',
    'NL': 'NLD', 'PL': 'POL', 'PT': 'PRT', 'RO': 'ROU', 'SE': 'SWE',
    'SI': 'SVN', 'SK': 'SVK', 'NO': 'NOR', 'CH': 'CHE', 'GB': 'GBR',
}

COUNTRY_NAMES = {
    'AT': 'Austria', 'BE': 'Belgium', 'BG': 'Bulgaria', 'CY': 'Cyprus',
    'CZ': 'Czechia', 'DE': 'Germany', 'DK': 'Denmark', 'EE': 'Estonia',
    'GR': 'Greece', 'ES': 'Spain', 'FI': 'Finland', 'FR': 'France',
    'HR': 'Croatia', 'HU': 'Hungary', 'IE': 'Ireland', 'IT': 'Italy',
    'LT': 'Lithuania', 'LU': 'Luxembourg', 'LV': 'Latvia', 'MT': 'Malta',
    'NL': 'Netherlands', 'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania',
    'SE': 'Sweden', 'SI': 'Slovenia', 'SK': 'Slovakia', 'NO': 'Norway',
    'CH': 'Switzerland', 'GB': 'United Kingdom',
}

# 海外领地排除 (NUTS-2 前缀)
OVERSEAS_PREFIXES = ['FRY', 'PT2', 'PT3', 'ES7']

# ============================================================
# Part A: Eurostat 数据下载
# ============================================================
rpt('=' * 72)
rpt('n24_europe_regional_data.py')
rpt('欧洲 NUTS-2 区域面板数据获取与 MUQ 构建')
rpt('=' * 72)
rpt()
rpt(f'运行时间: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}')
rpt()

def parse_eurostat_to_long(content_bytes, value_col_name='value'):
    """
    将 Eurostat TSV 内容解析为长格式 DataFrame.
    返回 DataFrame: columns = [各meta字段..., year, value_col_name]
    """
    try:
        text = content_bytes.decode('utf-8')
    except Exception:
        text = content_bytes.decode('latin-1')

    lines = text.strip().split('\n')
    header_line = lines[0]
    header_parts = header_line.split('\t')

    # 解析 meta 列名和年份
    meta_header = header_parts[0]
    for sep in ['\\TIME_PERIOD', '\\time', '\\TIME']:
        if sep in meta_header:
            meta_header = meta_header.split(sep)[0]
            break
    meta_col_names = [c.strip() for c in meta_header.split(',')]

    years = [y.strip() for y in header_parts[1:]]

    records = []
    for line in lines[1:]:
        parts = line.split('\t')
        if len(parts) < 2:
            continue

        meta_str = parts[0].strip()
        meta_vals = [m.strip() for m in meta_str.split(',')]

        while len(meta_vals) < len(meta_col_names):
            meta_vals.append('')

        meta_dict = {}
        for i, col_name in enumerate(meta_col_names):
            meta_dict[col_name] = meta_vals[i] if i < len(meta_vals) else ''

        for j, yr in enumerate(years):
            if j + 1 < len(parts):
                val_str = parts[j + 1].strip()
                val_clean = ''
                for ch in val_str:
                    if ch in '0123456789.-':
                        val_clean += ch
                try:
                    val = float(val_clean)
                except Exception:
                    val = np.nan

                rec = meta_dict.copy()
                rec['year'] = yr
                rec[value_col_name] = val
                records.append(rec)

    df = pd.DataFrame(records)
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    return df


def download_eurostat(dataset_code, timeout=180):
    """下载 Eurostat 数据 (TSV 格式), 返回 bytes 或 None"""
    urls = [
        f'https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{dataset_code}/?format=TSV',
        f'https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/{dataset_code}.tsv.gz',
    ]

    for url in urls:
        rpt(f'  尝试: {url[:90]}...')
        try:
            r = requests.get(url, timeout=timeout, headers={
                'User-Agent': 'Mozilla/5.0 (Research; Academic Use)',
                'Accept': '*/*'
            })
            if r.status_code == 200 and len(r.content) > 100:
                rpt(f'  => 成功, 大小 = {len(r.content):,} bytes')
                if r.content[:2] == b'\x1f\x8b':
                    content = gzip.decompress(r.content)
                else:
                    content = r.content
                return content
            else:
                rpt(f'  => HTTP {r.status_code}, 内容大小 {len(r.content)}')
        except Exception as e:
            rpt(f'  => 失败: {e}')
        time.sleep(2)

    return None


# --- A1: 下载 NUTS-2 GDP ---
rpt('PART A: 数据下载')
rpt('-' * 72)
rpt('\n--- A1: NUTS-2 GDP (nama_10r_2gdp) ---')

gdp_raw = pd.DataFrame()
gdp_content = download_eurostat('nama_10r_2gdp')

if gdp_content is not None:
    gdp_raw = parse_eurostat_to_long(gdp_content, 'gdp_meur')
    rpt(f'  GDP 原始记录数: {len(gdp_raw):,}')
    rpt(f'  列: {list(gdp_raw.columns)}')
    if len(gdp_raw) > 0:
        rpt(f'  年份范围: {gdp_raw["year"].min():.0f} - {gdp_raw["year"].max():.0f}')
        for col in gdp_raw.columns:
            if col not in ['year', 'gdp_meur', 'geo']:
                uvals = gdp_raw[col].unique()
                if len(uvals) < 20:
                    rpt(f'  {col}: {sorted(uvals)}')
else:
    rpt('[WARNING] NUTS-2 GDP 下载失败, 尝试 NUTS-3...')
    gdp_content = download_eurostat('nama_10r_3gdp')
    if gdp_content is not None:
        gdp_raw = parse_eurostat_to_long(gdp_content, 'gdp_meur')
        rpt(f'  NUTS-3 GDP 原始记录数: {len(gdp_raw):,}')

# --- A2: 下载 NUTS-2 人口 ---
rpt('\n--- A2: NUTS-2 人口 (demo_r_pjangroup) ---')
pop_raw = pd.DataFrame()

for pop_dataset in ['demo_r_pjangroup', 'demo_r_pjanaggr3', 'demo_r_d2jan']:
    rpt(f'\n  尝试数据集: {pop_dataset}')
    pop_content = download_eurostat(pop_dataset)
    if pop_content is not None:
        pop_raw = parse_eurostat_to_long(pop_content, 'population')
        rpt(f'  人口原始记录数: {len(pop_raw):,}')
        if len(pop_raw) > 0:
            rpt(f'  列: {list(pop_raw.columns)}')
            rpt(f'  年份范围: {pop_raw["year"].min():.0f} - {pop_raw["year"].max():.0f}')
            for col in pop_raw.columns:
                if col not in ['year', 'population', 'geo']:
                    uvals = pop_raw[col].unique()
                    if len(uvals) < 20:
                        rpt(f'  {col}: {sorted(uvals)}')
            break
    time.sleep(2)

# ============================================================
# Part B: 数据处理 — 筛选与合并
# ============================================================
rpt()
rpt('PART B: 数据筛选与合并')
rpt('-' * 72)

# --- B1: GDP 筛选 ---
if len(gdp_raw) == 0:
    rpt('[FATAL] GDP 数据不可用, 使用已有截面数据作为后备')
    # 加载已有截面数据 (来自 85_eu_nuts3_scaling.py)
    eu_cross = pd.read_csv(os.path.join(DATA_RAW, 'eu_nuts3_data.csv'))
    rpt(f'  后备截面数据: {len(eu_cross)} 行, {eu_cross["country"].nunique()} 个国家')
    USE_PANEL = False
else:
    USE_PANEL = True
    rpt('\n  GDP 数据筛选:')

    # 筛选: MIO_EUR (百万欧元), NUTS-2 (代码长度=4)
    if 'unit' in gdp_raw.columns:
        gdp_filt = gdp_raw[gdp_raw['unit'] == 'MIO_EUR'].copy()
    else:
        gdp_filt = gdp_raw.copy()

    if 'na_item' in gdp_filt.columns:
        gdp_filt = gdp_filt[gdp_filt['na_item'] == 'B1GQ'].copy()

    # 同时保留 NUTS-2 (len=4) 和 NUTS-0 (len=2, 用于校验)
    gdp_nuts2 = gdp_filt[gdp_filt['geo'].str.len() == 4].copy()
    gdp_nuts0 = gdp_filt[gdp_filt['geo'].str.len() == 2].copy()

    rpt(f'  NUTS-2 GDP 记录: {len(gdp_nuts2):,}')
    rpt(f'  NUTS-0 GDP 记录: {len(gdp_nuts0):,}')

    # 排除海外领地
    for prefix in OVERSEAS_PREFIXES:
        gdp_nuts2 = gdp_nuts2[~gdp_nuts2['geo'].str.startswith(prefix)]
    rpt(f'  排除海外领地后: {len(gdp_nuts2):,}')

    # 添加国家代码
    gdp_nuts2['nuts_prefix'] = gdp_nuts2['geo'].str[:2]
    gdp_nuts2['iso2'] = gdp_nuts2['nuts_prefix'].map(NUTS_TO_ISO2)
    gdp_nuts2['iso3'] = gdp_nuts2['iso2'].map(ISO2_TO_ISO3)
    gdp_nuts2['country_name'] = gdp_nuts2['iso2'].map(COUNTRY_NAMES)

    # 移除无法映射的
    gdp_nuts2 = gdp_nuts2[gdp_nuts2['iso2'].notna()].copy()
    rpt(f'  可映射国家后: {len(gdp_nuts2):,}')

    # 有效年份诊断
    gdp_valid = gdp_nuts2[gdp_nuts2['gdp_meur'].notna()]
    yr_counts = gdp_valid.groupby('year')['geo'].nunique()
    rpt(f'\n  各年份有效 NUTS-2 区域数:')
    for yr in sorted(yr_counts.index, reverse=True)[:10]:
        rpt(f'    {int(yr)}: {yr_counts[yr]} 区域')

    rpt(f'\n  覆盖国家 ({gdp_nuts2["country_name"].nunique()}):')
    for c in sorted(gdp_nuts2['country_name'].dropna().unique()):
        n_reg = gdp_nuts2[gdp_nuts2['country_name'] == c]['geo'].nunique()
        rpt(f'    {c}: {n_reg} 个 NUTS-2 区域')

# --- B2: 人口筛选 ---
if len(pop_raw) > 0 and USE_PANEL:
    rpt('\n  人口数据筛选:')

    # 筛选: TOTAL 或 T (性别合计), NUTS-2
    pop_filt = pop_raw.copy()

    # 根据列结构筛选
    if 'sex' in pop_filt.columns:
        pop_filt = pop_filt[pop_filt['sex'] == 'T'].copy()
    if 'age' in pop_filt.columns:
        pop_filt = pop_filt[pop_filt['age'] == 'TOTAL'].copy()
    if 'unit' in pop_filt.columns:
        pop_filt = pop_filt[pop_filt['unit'] == 'NR'].copy()

    pop_nuts2 = pop_filt[pop_filt['geo'].str.len() == 4].copy()

    # 排除海外领地
    for prefix in OVERSEAS_PREFIXES:
        pop_nuts2 = pop_nuts2[~pop_nuts2['geo'].str.startswith(prefix)]

    pop_nuts2['nuts_prefix'] = pop_nuts2['geo'].str[:2]
    pop_nuts2['iso2'] = pop_nuts2['nuts_prefix'].map(NUTS_TO_ISO2)
    pop_nuts2 = pop_nuts2[pop_nuts2['iso2'].notna()].copy()

    rpt(f'  NUTS-2 人口记录: {len(pop_nuts2):,}')
    pop_valid = pop_nuts2[pop_nuts2['population'].notna()]
    rpt(f'  有效记录: {len(pop_valid):,}')

    # 合并 GDP + 人口
    rpt('\n  合并 GDP + 人口...')

    # 保留关键列
    gdp_panel = gdp_nuts2[['geo', 'year', 'gdp_meur', 'nuts_prefix', 'iso2', 'iso3', 'country_name']].copy()
    pop_panel = pop_nuts2[['geo', 'year', 'population']].copy()

    # 去重 (可能有多条记录由于不同 freq 或其他维度)
    gdp_panel = gdp_panel.groupby(['geo', 'year']).agg({
        'gdp_meur': 'first',
        'nuts_prefix': 'first',
        'iso2': 'first',
        'iso3': 'first',
        'country_name': 'first'
    }).reset_index()

    pop_panel = pop_panel.groupby(['geo', 'year']).agg({
        'population': 'first'
    }).reset_index()

    panel = pd.merge(gdp_panel, pop_panel, on=['geo', 'year'], how='outer')
    rpt(f'  合并后: {len(panel):,} 行, {panel["geo"].nunique()} 区域')

    # 补充元数据列 (对于只有人口没有 GDP 的行)
    panel['nuts_prefix'] = panel['geo'].str[:2]
    panel['iso2'] = panel['nuts_prefix'].map(NUTS_TO_ISO2)
    panel['iso3'] = panel['iso2'].map(ISO2_TO_ISO3)
    panel['country_name'] = panel['iso2'].map(COUNTRY_NAMES)
    panel = panel[panel['iso2'].notna()].copy()

else:
    if USE_PANEL:
        rpt('[WARNING] 人口数据不可用, 仅使用 GDP')
        panel = gdp_nuts2[['geo', 'year', 'gdp_meur', 'nuts_prefix', 'iso2', 'iso3', 'country_name']].copy()
        panel['population'] = np.nan

# ============================================================
# Part C: 加载国家级 GFCF (World Bank)
# ============================================================
rpt()
rpt('PART C: 加载国家级 GFCF')
rpt('-' * 72)

wb_path = os.path.join(DATA_RAW, 'world_bank_all_countries.csv')
wb = pd.read_csv(wb_path)
rpt(f'  World Bank 数据: {len(wb)} 行, {wb["country_iso3"].nunique()} 个国家')

# 欧洲国家 GFCF (current USD)
euro_iso3 = list(ISO2_TO_ISO3.values())
wb_euro = wb[wb['country_iso3'].isin(euro_iso3)][
    ['country_iso3', 'country_iso2', 'year', 'NY.GDP.MKTP.CD', 'NE.GDI.FTOT.CD', 'NE.GDI.FTOT.ZS']
].copy()
wb_euro.columns = ['iso3', 'iso2', 'year', 'gdp_usd', 'gfcf_usd', 'gfcf_pct_gdp']
wb_euro = wb_euro.dropna(subset=['gfcf_usd'])

rpt(f'  欧洲国家 GFCF 记录: {len(wb_euro)}')
rpt(f'  国家: {sorted(wb_euro["iso3"].unique())}')
rpt(f'  年份范围: {wb_euro["year"].min():.0f} - {wb_euro["year"].max():.0f}')

# ============================================================
# Part D: 构建区域 GFCF 估计 (按 GDP 份额分配)
# ============================================================
rpt()
rpt('PART D: 区域 GFCF 估计与 MUQ 构建')
rpt('-' * 72)

if USE_PANEL:
    # 筛选有效面板: GDP 非缺失
    panel_valid = panel[panel['gdp_meur'].notna()].copy()
    rpt(f'  有效 GDP 面板: {len(panel_valid)} 行')

    # 步骤 1: 计算各区域 GDP 占国家总 GDP 的比例
    # 需要国家级 GDP (来自 NUTS-0 或汇总 NUTS-2)
    country_gdp_from_nuts2 = panel_valid.groupby(['iso3', 'year'])['gdp_meur'].sum().reset_index()
    country_gdp_from_nuts2.columns = ['iso3', 'year', 'country_gdp_meur']

    panel_valid = panel_valid.merge(country_gdp_from_nuts2, on=['iso3', 'year'], how='left')
    panel_valid['gdp_share'] = panel_valid['gdp_meur'] / panel_valid['country_gdp_meur']

    # 步骤 2: 国家 GFCF 按 GDP 份额分配到区域
    # 注意: World Bank GFCF 是 current USD, Eurostat GDP 是 百万 EUR
    # 我们使用 GFCF/GDP 比率来避免汇率问题:
    #   regional_GFCF_meur = gdp_share * national_GFCF_pct_GDP * national_GDP_from_nuts2
    # 等价于: regional_GFCF_meur = regional_GDP_meur * national_GFCF_pct_GDP / 100

    wb_gfcf_ratio = wb_euro[['iso3', 'year', 'gfcf_pct_gdp']].drop_duplicates()
    panel_valid = panel_valid.merge(wb_gfcf_ratio, on=['iso3', 'year'], how='left')

    # 区域 GFCF 估计 (百万 EUR)
    panel_valid['gfcf_est_meur'] = panel_valid['gdp_meur'] * panel_valid['gfcf_pct_gdp'] / 100.0

    n_with_gfcf = panel_valid['gfcf_est_meur'].notna().sum()
    rpt(f'  有 GFCF 估计的记录: {n_with_gfcf} / {len(panel_valid)}')

    # 步骤 3: 构建 MUQ = DeltaGDP / GFCF
    panel_valid = panel_valid.sort_values(['geo', 'year'])
    panel_valid['delta_gdp'] = panel_valid.groupby('geo')['gdp_meur'].diff()
    panel_valid['muq'] = panel_valid['delta_gdp'] / panel_valid['gfcf_est_meur']

    # MUQ 3 年移动平均 (更稳定)
    panel_valid['muq_ma3'] = panel_valid.groupby('geo')['muq'].transform(
        lambda x: x.rolling(3, min_periods=2, center=True).mean()
    )

    # GDP per capita
    panel_valid['gdp_per_capita'] = np.where(
        panel_valid['population'] > 0,
        panel_valid['gdp_meur'] * 1e6 / panel_valid['population'],
        np.nan
    )

    # 对数变量
    panel_valid['ln_gdp'] = np.log(panel_valid['gdp_meur'].clip(lower=1e-6))
    panel_valid['ln_pop'] = np.log(panel_valid['population'].clip(lower=1))
    panel_valid['ln_gdp_pc'] = np.log(panel_valid['gdp_per_capita'].clip(lower=1e-6))

    # GDP 增长率
    panel_valid['gdp_growth'] = panel_valid.groupby('geo')['gdp_meur'].pct_change()

    # 投资强度
    panel_valid['invest_intensity'] = panel_valid['gfcf_est_meur'] / panel_valid['gdp_meur']

    # 人口增长
    panel_valid['pop_growth'] = panel_valid.groupby('geo')['population'].pct_change(fill_method=None)

    rpt(f'\n  面板统计:')
    rpt(f'  总行数: {len(panel_valid)}')
    rpt(f'  区域数: {panel_valid["geo"].nunique()}')
    rpt(f'  国家数: {panel_valid["country_name"].nunique()}')
    rpt(f'  年份范围: {panel_valid["year"].min():.0f} - {panel_valid["year"].max():.0f}')

    # MUQ 分布
    muq_vals = panel_valid['muq'].dropna()
    muq_vals_clean = muq_vals[np.isfinite(muq_vals)]
    if len(muq_vals_clean) > 10:
        # Winsorize 1%/99%
        q01, q99 = muq_vals_clean.quantile([0.01, 0.99])
        muq_w = muq_vals_clean.clip(q01, q99)
        rpt(f'\n  MUQ 分布 (winsorized 1%/99%):')
        rpt(f'    N = {len(muq_w)}')
        rpt(f'    Mean = {muq_w.mean():.4f}')
        rpt(f'    Median = {muq_w.median():.4f}')
        rpt(f'    SD = {muq_w.std():.4f}')
        rpt(f'    [Q25, Q75] = [{muq_w.quantile(0.25):.4f}, {muq_w.quantile(0.75):.4f}]')
        rpt(f'    Range = [{muq_w.min():.4f}, {muq_w.max():.4f}]')

    # 保存面板
    output_path = os.path.join(DATA_RAW, 'europe_regional_panel.csv')
    panel_valid.to_csv(output_path, index=False)
    rpt(f'\n  面板已保存: {output_path}')
    rpt(f'  列: {list(panel_valid.columns)}')

    panel = panel_valid  # 后续分析使用

else:
    rpt('[NOTE] 无面板数据, 使用截面模式')
    panel = eu_cross.copy()
    panel['muq'] = np.nan
    panel['muq_ma3'] = np.nan
    panel['ln_gdp'] = np.log(panel['gdp_value'].clip(lower=1e-6))
    panel['ln_pop'] = np.log(panel['population'].clip(lower=1))
    panel['ln_gdp_pc'] = np.log(panel['gdp_per_capita'].clip(lower=1e-6))

# ============================================================
# Part E: 标度律分析
# ============================================================
rpt()
rpt('PART E: 标度律分析 — ln(GDP) ~ ln(Pop)')
rpt('-' * 72)

def run_scaling_ols(data, y_col, x_col, label):
    """运行标度律 OLS, 报告结果"""
    mask = data[y_col].notna() & data[x_col].notna() & np.isfinite(data[y_col]) & np.isfinite(data[x_col])
    d = data[mask]
    if len(d) < 10:
        rpt(f'\n  [{label}] 样本不足 (N={len(d)}), 跳过')
        return None
    Y = d[y_col]
    X = sm.add_constant(d[x_col])
    model = sm.OLS(Y, X).fit(cov_type='HC1')
    b = model.params.iloc[1]
    se = model.bse.iloc[1]
    ci = model.conf_int().iloc[1]
    rpt(f'\n  [{label}]')
    rpt(f'  {y_col} = a + b * {x_col}')
    rpt(f'  N = {len(d)}')
    rpt(f'  b (scaling exponent) = {b:.4f} (SE = {se:.4f})')
    rpt(f'  95% CI = [{ci[0]:.4f}, {ci[1]:.4f}]')
    rpt(f'  t = {model.tvalues.iloc[1]:.3f}, p = {model.pvalues.iloc[1]:.2e}')
    rpt(f'  R-squared = {model.rsquared:.4f}')

    # 超线性/亚线性判断
    if ci[0] > 1.0:
        rpt(f'  => 超线性 (b > 1): 大区域 GDP per capita 更高 (集聚效应)')
    elif ci[1] < 1.0:
        rpt(f'  => 亚线性 (b < 1): 大区域 GDP per capita 更低')
    else:
        rpt(f'  => 无法拒绝线性 (b = 1): 95% CI 跨越 1.0')

    return model

# --- E1: 全欧洲截面 (最新年份) ---
if USE_PANEL:
    # 找到观测最多的近年
    recent_years = sorted(panel['year'].dropna().unique(), reverse=True)
    best_year = None
    for yr in recent_years[:5]:
        n_obs = panel[(panel['year'] == yr) & panel['gdp_meur'].notna() & panel['population'].notna()].shape[0]
        if n_obs > 100:
            best_year = yr
            break
    if best_year is None and len(recent_years) > 0:
        best_year = recent_years[0]

    if best_year is not None:
        rpt(f'\n--- E1: 全欧洲截面标度律 (year = {int(best_year)}) ---')
        cross = panel[(panel['year'] == best_year) & panel['gdp_meur'].notna() & panel['population'].notna()].copy()
        cross = cross[(cross['population'] > 10000) & (cross['gdp_meur'] > 10)]
        rpt(f'  样本: {len(cross)} 区域 (人口>10000, GDP>10M EUR)')

        m_all = run_scaling_ols(cross, 'ln_gdp', 'ln_pop', f'EU-wide {int(best_year)}')

    # --- E2: 分国家标度律 ---
    rpt(f'\n--- E2: 分国家截面标度律 (year = {int(best_year)}) ---')
    country_scaling = []
    for cname in sorted(cross['country_name'].dropna().unique()):
        csub = cross[cross['country_name'] == cname]
        if len(csub) >= 5:
            mask = csub['ln_gdp'].notna() & csub['ln_pop'].notna()
            csub_v = csub[mask]
            if len(csub_v) >= 5:
                Y = csub_v['ln_gdp']
                X = sm.add_constant(csub_v['ln_pop'])
                try:
                    m = sm.OLS(Y, X).fit(cov_type='HC1')
                    b = m.params.iloc[1]
                    se = m.bse.iloc[1]
                    ci = m.conf_int().iloc[1]
                    country_scaling.append({
                        'country': cname,
                        'n_regions': len(csub_v),
                        'beta': b,
                        'se': se,
                        'ci_lo': ci[0],
                        'ci_hi': ci[1],
                        'r2': m.rsquared,
                        'p': m.pvalues.iloc[1]
                    })
                except Exception:
                    pass

    if country_scaling:
        cs_df = pd.DataFrame(country_scaling).sort_values('beta', ascending=False)
        rpt(f'\n  国家标度指数排名 (N >= 5 区域):')
        rpt(f'  {"Country":<20s} {"N":>4s} {"beta":>7s} {"SE":>7s} {"95% CI":>18s} {"R2":>6s}')
        rpt(f'  {"-"*20} {"---":>4s} {"-----":>7s} {"-----":>7s} {"----------------":>18s} {"----":>6s}')
        for _, row in cs_df.iterrows():
            rpt(f'  {row["country"]:<20s} {row["n_regions"]:4.0f} {row["beta"]:7.4f} {row["se"]:7.4f} '
                f'[{row["ci_lo"]:7.4f}, {row["ci_hi"]:7.4f}] {row["r2"]:6.4f}')

        # 保存 source data
        cs_df.to_csv(os.path.join(SOURCE_DIR, 'eu_country_scaling.csv'), index=False)

    # --- E3: 面板 FE 标度律 ---
    rpt(f'\n--- E3: 面板固定效应标度律 ---')
    panel_fe = panel[
        (panel['year'] >= 2000) &
        panel['ln_gdp'].notna() &
        panel['ln_pop'].notna() &
        np.isfinite(panel['ln_gdp']) &
        np.isfinite(panel['ln_pop'])
    ].copy()

    if len(panel_fe) > 100:
        # Year FE
        panel_fe['year_int'] = panel_fe['year'].astype(int)
        year_dummies = pd.get_dummies(panel_fe['year_int'], prefix='yr', drop_first=True, dtype=float)
        X_fe = pd.concat([sm.add_constant(panel_fe[['ln_pop']].reset_index(drop=True)),
                          year_dummies.reset_index(drop=True)], axis=1)
        Y_fe = panel_fe['ln_gdp'].reset_index(drop=True)

        # 去除缺失
        mask_fe = X_fe.notna().all(axis=1) & Y_fe.notna()
        X_fe = X_fe[mask_fe]
        Y_fe = Y_fe[mask_fe]

        if len(Y_fe) > 50:
            m_fe = sm.OLS(Y_fe, X_fe).fit(cov_type='cluster', cov_kwds={'groups': panel_fe[mask_fe.values]['geo'].values})
            b_fe = m_fe.params['ln_pop']
            se_fe = m_fe.bse['ln_pop']
            ci_fe = m_fe.conf_int().loc['ln_pop']
            rpt(f'  Pooled OLS + Year FE + Clustered SE (by region):')
            rpt(f'  N = {len(Y_fe)}, Regions = {panel_fe[mask_fe.values]["geo"].nunique()}')
            rpt(f'  beta = {b_fe:.4f} (SE = {se_fe:.4f})')
            rpt(f'  95% CI = [{ci_fe[0]:.4f}, {ci_fe[1]:.4f}]')
            rpt(f'  R-squared = {m_fe.rsquared:.4f}')

else:
    # 截面模式
    rpt('\n--- 截面标度律 (已有数据) ---')
    cross = panel[(panel['population'] > 10000) & (panel['gdp_value'] > 10)].copy()
    run_scaling_ols(cross, 'ln_gdp', 'ln_pop', 'EU cross-section (existing)')


# ============================================================
# Part F: MUQ 分析 (面板模式)
# ============================================================
rpt()
rpt('PART F: MUQ 区域分析')
rpt('-' * 72)

if USE_PANEL:
    muq_data = panel[panel['muq'].notna() & np.isfinite(panel['muq'])].copy()
    rpt(f'  有效 MUQ 观测: {len(muq_data)}')

    if len(muq_data) > 100:
        # Winsorize
        q01, q99 = muq_data['muq'].quantile([0.01, 0.99])
        muq_data['muq_w'] = muq_data['muq'].clip(q01, q99)

        # --- F1: 分国家 MUQ 统计 ---
        rpt(f'\n--- F1: 分国家 MUQ 中位数 ---')
        country_muq = muq_data.groupby('country_name')['muq_w'].agg(['median', 'mean', 'std', 'count'])
        country_muq = country_muq[country_muq['count'] >= 20].sort_values('median', ascending=False)
        rpt(f'  {"Country":<20s} {"N":>5s} {"Median":>8s} {"Mean":>8s} {"SD":>8s}')
        rpt(f'  {"-"*20} {"---":>5s} {"------":>8s} {"------":>8s} {"------":>8s}')
        for cname, row in country_muq.iterrows():
            rpt(f'  {cname:<20s} {row["count"]:5.0f} {row["median"]:8.4f} {row["mean"]:8.4f} {row["std"]:8.4f}')

        # --- F2: 时期对比 (2000s vs 2010s) ---
        rpt(f'\n--- F2: 时期对比 ---')
        for period_name, yr_range in [('2001-2007', (2001, 2007)), ('2010-2019', (2010, 2019)), ('2020-2022', (2020, 2022))]:
            p_sub = muq_data[(muq_data['year'] >= yr_range[0]) & (muq_data['year'] <= yr_range[1])]
            if len(p_sub) > 10:
                rpt(f'  {period_name}: N={len(p_sub)}, MUQ median={p_sub["muq_w"].median():.4f}, '
                    f'mean={p_sub["muq_w"].mean():.4f}')

        # --- F3: MUQ vs 投资强度 (核心检验) ---
        rpt(f'\n--- F3: MUQ vs 投资强度 (核心负相关检验) ---')
        mi_data = muq_data[muq_data['invest_intensity'].notna() & np.isfinite(muq_data['invest_intensity'])].copy()
        mi_data = mi_data[(mi_data['invest_intensity'] > 0) & (mi_data['invest_intensity'] < 1)]

        if len(mi_data) > 50:
            # 注意: 当 GFCF 是用 GFCF/GDP 比率分配时, MUQ = DeltaGDP/GFCF = DeltaGDP/(GDP*r)
            # invest_intensity = GFCF/GDP = r (常数, 来自国家级)
            # 所以 MUQ 和 invest_intensity 的跨区域变异完全来自 DeltaGDP/GDP 和国家级 r
            # 这意味着 MUQ vs invest_intensity 的关系主要是跨国差异
            rpt('  [注意] 区域 GFCF 按国家 GFCF/GDP 比率分配,')
            rpt('  故 MUQ vs invest_intensity 的变异主要反映跨国差异')
            rpt('  (同一国家内各区域的 invest_intensity 相同)')

            # 跨国: 国家级 MUQ vs 投资强度
            country_agg = mi_data.groupby(['country_name', 'year']).agg({
                'muq_w': 'median',
                'invest_intensity': 'mean',
                'gdp_meur': 'sum'
            }).reset_index()

            if len(country_agg) > 20:
                mask_ca = country_agg['muq_w'].notna() & country_agg['invest_intensity'].notna()
                ca = country_agg[mask_ca]
                Y_ca = ca['muq_w']
                X_ca = sm.add_constant(ca['invest_intensity'])
                m_ca = sm.OLS(Y_ca, X_ca).fit(cov_type='HC1')
                b_ca = m_ca.params.iloc[1]
                ci_ca = m_ca.conf_int().iloc[1]
                rpt(f'\n  跨国 MUQ ~ invest_intensity:')
                rpt(f'  N = {len(ca)}, b = {b_ca:.4f}, 95% CI = [{ci_ca[0]:.4f}, {ci_ca[1]:.4f}]')
                rpt(f'  p = {m_ca.pvalues.iloc[1]:.4e}, R2 = {m_ca.rsquared:.4f}')
                if b_ca < 0:
                    rpt(f'  => 负相关: 投资强度越高, MUQ 越低 (与中日美一致)')
                else:
                    rpt(f'  => 正相关或不显著: 与预期不一致, 需进一步检查')

        # --- F4: MUQ 与 GDP per capita 的关系 ---
        rpt(f'\n--- F4: MUQ vs GDP per capita ---')
        mg_data = muq_data[muq_data['gdp_per_capita'].notna() & (muq_data['gdp_per_capita'] > 0)].copy()
        mg_data['ln_gdp_pc'] = np.log(mg_data['gdp_per_capita'])

        if len(mg_data) > 50:
            Y_mg = mg_data['muq_w']
            X_mg = sm.add_constant(mg_data['ln_gdp_pc'])
            m_mg = sm.OLS(Y_mg, X_mg).fit(cov_type='HC1')
            b_mg = m_mg.params.iloc[1]
            ci_mg = m_mg.conf_int().iloc[1]
            rpt(f'  MUQ ~ ln(GDP_pc):')
            rpt(f'  N = {len(mg_data)}, b = {b_mg:.4f}, 95% CI = [{ci_mg[0]:.4f}, {ci_mg[1]:.4f}]')
            rpt(f'  p = {m_mg.pvalues.iloc[1]:.4e}, R2 = {m_mg.rsquared:.4f}')

else:
    rpt('  [SKIP] 无面板数据, MUQ 分析跳过')

# ============================================================
# Part G: 跨国对比摘要
# ============================================================
rpt()
rpt('PART G: 跨国对比摘要')
rpt('-' * 72)

if USE_PANEL:
    # 选取主要国家最近 5 年数据
    key_countries = ['Germany', 'France', 'Italy', 'Spain', 'United Kingdom',
                     'Netherlands', 'Poland', 'Sweden', 'Austria', 'Belgium']
    recent_5yr = panel['year'].max() - 4

    rpt(f'\n  主要欧洲国家 (最近5年 {int(recent_5yr)}-{int(panel["year"].max())}):')
    rpt(f'  {"Country":<20s} {"Regions":>8s} {"Tot GDP(BEUR)":>14s} {"Avg MUQ":>8s} {"Avg GFCF/GDP":>13s}')
    rpt(f'  {"-"*20} {"-------":>8s} {"-"*14:>14s} {"-------":>8s} {"-"*13:>13s}')

    for cname in key_countries:
        csub = panel[(panel['country_name'] == cname) & (panel['year'] >= recent_5yr)]
        if len(csub) == 0:
            continue
        n_reg = csub['geo'].nunique()
        tot_gdp = csub.groupby('year')['gdp_meur'].sum().mean() / 1000  # 十亿 EUR
        avg_muq = csub['muq'].dropna()
        avg_muq_val = avg_muq[np.isfinite(avg_muq)].median() if len(avg_muq) > 0 else np.nan
        avg_inv = csub['invest_intensity'].dropna().mean() if 'invest_intensity' in csub.columns else np.nan

        rpt(f'  {cname:<20s} {n_reg:8d} {tot_gdp:14.1f} {avg_muq_val:8.4f} {avg_inv:13.4f}')

# ============================================================
# Part H: 数据质量与限制
# ============================================================
rpt()
rpt('PART H: 数据质量与限制')
rpt('-' * 72)
rpt()
rpt('数据来源:')
rpt('  - GDP: Eurostat nama_10r_2gdp (NUTS-2, 百万 EUR, current prices)')
rpt('  - Population: Eurostat demo_r_pjangroup (NUTS-2)')
rpt('  - GFCF: World Bank NE.GDI.FTOT.CD (国家级, current USD)')
rpt()
rpt('关键假设:')
rpt('  1. 区域 GFCF 按 GDP 份额从国家 GFCF 分配 (与日本都道府県处理一致)')
rpt('     - 假设各区域 GFCF/GDP 比率相同 (实际上工业区可能更高)')
rpt('     - 这意味着跨区域 MUQ 变异完全来自 GDP 增长差异')
rpt('  2. 使用名义值 (未做通胀调整)')
rpt('     - 欧洲区域 CPI 数据可得性有限')
rpt('     - 名义 MUQ 在跨区域比较中仍有信息量')
rpt('  3. NUTS-2 而非 NUTS-3')
rpt('     - NUTS-2 GDP 数据更完整 (NUTS-3 有更多缺失)')
rpt('     - NUTS-2 平均人口 ~100-300 万, 与中国地级市可比')
rpt()
rpt('局限:')
rpt('  1. 区域 GFCF 为估计值, 非直接观测')
rpt('  2. 不含英国 (UK 于 2020 脱欧, Eurostat 数据截止 ~2019)')
rpt('  3. 房价数据仅有国家级 (BIS), 无法构建区域 housing-based MUQ')
rpt('  4. 少数东欧国家 2000 年代初数据缺失')

# ============================================================
# 保存报告
# ============================================================
rpt()
rpt('=' * 72)
rpt('脚本执行完成')
rpt('=' * 72)

save_report()

print('\n完成!')
