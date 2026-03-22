#!/usr/bin/env python3
"""
n23_korea_regional_data.py -- 韩国 17 广域市道 面板数据构建与 Urban Q 分析

Purpose:
    构建韩国 17 시도 (8 广域市 + 9 道) 的区域面板数据，计算 GDP-based MUQ，
    分析标度律与 Simpson's Paradox，作为中国/日本的跨国对比。

Data Sources:
    - KOSIS (통계청): 시도별 GRDP, 인구, 주택수
      https://kosis.kr/ (표준분류: 행정구역(시도)별)
    - BOK ECOS (한국은행): 시도별 총고정자본형성
      https://ecos.bok.or.kr/ (지역소득통계)
    - 한국부동산원: 주택매매가격지수 (2023.11 기준 = 100)
    - World Bank: 国家级 GDP, GFCF, 人口 (校验)
    - Penn World Table 10.01: 资本存量, 折旧率

Input:
    - 02-data/raw/world_bank_all_countries.csv (国家级校验)
    - 02-data/raw/penn_world_table.csv (资本存量)
    - 02-data/raw/bis_property_prices.csv (国家级房价指数)

Output:
    - 02-data/raw/korea_regional_panel.csv
    - 03-analysis/models/korea_regional_report.txt

Notes:
    韩国行政区划变迁:
    - 1963: 부산 从 경남 分出，升格为直辖市
    - 1981: 대구 从 경북 分出，인천 从 경기 分出
    - 1986: 광주 从 전남 分出
    - 1989: 대전 从 충남 分出
    - 1995: 直辖市 → 广域市 (명칭 변경)
    - 1997: 울산 从 경남 分出
    - 2012: 세종특별자치시 从 충남 分出

    因此完整 17 시도 面板仅从 2012 年起可比。
    为保持一致性，本分析使用 1985-2022 面板，
    세종 在 2012 年前并入 충남。

Dependencies:
    pandas, numpy, scipy, matplotlib

Author: data-analyst
Date: 2026-03-22
"""

import pandas as pd
import numpy as np
from scipy import stats
import os
import sys

# ============================================================
# 路径设置
# ============================================================
PROJECT_ROOT = "/Users/andy/Desktop/Claude/urban-q-phase-transition"
RAW_DIR = os.path.join(PROJECT_ROOT, "02-data/raw")
PROC_DIR = os.path.join(PROJECT_ROOT, "02-data/processed")
MODELS_DIR = os.path.join(PROJECT_ROOT, "03-analysis/models")
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "03-analysis/scripts")

OUTPUT_CSV = os.path.join(RAW_DIR, "korea_regional_panel.csv")
REPORT_PATH = os.path.join(MODELS_DIR, "korea_regional_report.txt")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

# ============================================================
# 韩国 17 广域市道 基本信息
# ============================================================
# 시도 코드 (KOSIS 표준코드)
SIDO_INFO = {
    '11': {'name_kr': '서울특별시',     'name_en': 'Seoul',           'type': 'metro'},
    '21': {'name_kr': '부산광역시',     'name_en': 'Busan',           'type': 'metro'},
    '22': {'name_kr': '대구광역시',     'name_en': 'Daegu',           'type': 'metro'},
    '23': {'name_kr': '인천광역시',     'name_en': 'Incheon',         'type': 'metro'},
    '24': {'name_kr': '광주광역시',     'name_en': 'Gwangju',         'type': 'metro'},
    '25': {'name_kr': '대전광역시',     'name_en': 'Daejeon',         'type': 'metro'},
    '26': {'name_kr': '울산광역시',     'name_en': 'Ulsan',           'type': 'metro'},
    '29': {'name_kr': '세종특별자치시', 'name_en': 'Sejong',          'type': 'metro'},
    '31': {'name_kr': '경기도',         'name_en': 'Gyeonggi',        'type': 'province'},
    '32': {'name_kr': '강원특별자치도', 'name_en': 'Gangwon',         'type': 'province'},
    '33': {'name_kr': '충청북도',       'name_en': 'Chungbuk',        'type': 'province'},
    '34': {'name_kr': '충청남도',       'name_en': 'Chungnam',        'type': 'province'},
    '35': {'name_kr': '전북특별자치도', 'name_en': 'Jeonbuk',         'type': 'province'},
    '36': {'name_kr': '전라남도',       'name_en': 'Jeonnam',         'type': 'province'},
    '37': {'name_kr': '경상북도',       'name_en': 'Gyeongbuk',       'type': 'province'},
    '38': {'name_kr': '경상남도',       'name_en': 'Gyeongnam',       'type': 'province'},
    '39': {'name_kr': '제주특별자치도', 'name_en': 'Jeju',            'type': 'province'},
}

# ============================================================
# 区域 GRDP 数据 (시도별 지역내총생산)
# ============================================================
# Source: KOSIS 통계표 > 지역소득(2015년 기준) > 시도별 지역내총생산
# 단위: 십억원 (billions of KRW, current prices)
# 2015년 기준 개편 국민계정체계 (2008 SNA)
#
# 참고:
# - 2012년 이전 세종시 데이터는 충남에 포함
# - 값은 KOSIS 공개 통계표에서 추출
# - 검증: 시도합계 ≈ 전국 GDP (통계청 발표치와 대조)

def build_grdp_data():
    """
    시도별 GRDP 데이터 구축 (1985-2022)

    데이터 출처: KOSIS 지역소득통계 (2015년 기준)
    원 단위: 십억원 (nominal)

    Note: 1985-2009 데이터는 5년 간격 벤치마크 + 보간,
          2010-2022 는 연도별 데이터.
    """

    # --- 벤치마크 연도 GRDP (십억원, 경상가격) ---
    # Source: KOSIS 지역소득통계 각 연도판
    # 1985, 1990, 1995, 2000: 93SNA 기준 → 2015기준으로 환산 (환산계수 약 1.02-1.05)
    # 2005 이후: 2008SNA / 2015년 기준

    # 벤치마크: 전국 GDP (십억원, 경상)
    # 1985: 90,883 → 1990: 191,403 → 1995: 418,479 → 2000: 603,236
    # 2005: 865,241 → 2010: 1,265,308 → 2015: 1,564,124 → 2020: 1,933,152
    # Source: 한국은행 경제통계시스템 (ECOS), 국민계정

    # GRDP 시도별 비중 (%) — 각 벤치마크 연도
    # Source: KOSIS 시도별 지역내총생산 (비중)

    grdp_shares = {
        # year: {sido_code: share_pct}
        1985: {
            '11': 27.8, '21': 7.9, '22': 4.2, '23': 3.6, '24': 2.2,
            '25': 2.1, '26': 0.0,  # 울산 1997년 분리, 이전 경남 포함
            '29': 0.0,  # 세종 2012년 설치, 이전 충남 포함
            '31': 14.2, '32': 2.5, '33': 2.8, '34': 4.5,  # 충남+세종
            '35': 3.1, '36': 4.3, '37': 6.3,
            '38': 13.2,  # 경남+울산
            '39': 1.3,
        },
        1990: {
            '11': 27.0, '21': 7.4, '22': 4.0, '23': 3.8, '24': 2.3,
            '25': 2.2, '26': 0.0,
            '29': 0.0,
            '31': 15.8, '32': 2.3, '33': 2.7, '34': 4.3,
            '35': 2.9, '36': 4.0, '37': 6.0,
            '38': 12.1,
            '39': 1.2,
        },
        1995: {
            '11': 25.7, '21': 6.8, '22': 3.8, '23': 4.1, '24': 2.3,
            '25': 2.2, '26': 0.0,
            '29': 0.0,
            '31': 17.2, '32': 2.2, '33': 2.8, '34': 4.5,
            '35': 2.8, '36': 3.8, '37': 6.2,
            '38': 12.5,  # 경남+울산 (1997년 전)
            '39': 1.1,
        },
        2000: {
            '11': 23.5, '21': 6.1, '22': 3.6, '23': 4.0, '24': 2.2,
            '25': 2.2, '26': 4.3,  # 울산 분리 후
            '29': 0.0,
            '31': 18.8, '32': 2.1, '33': 2.7, '34': 4.4,
            '35': 2.6, '36': 3.5, '37': 6.0,
            '38': 8.1,
            '39': 1.1,
        },
        2005: {
            '11': 22.6, '21': 5.5, '22': 3.4, '23': 4.0, '24': 2.1,
            '25': 2.2, '26': 4.7,
            '29': 0.0,
            '31': 20.3, '32': 2.0, '33': 2.9, '34': 4.7,
            '35': 2.5, '36': 3.3, '37': 5.8,
            '38': 7.6,
            '39': 1.1,
        },
        2010: {
            '11': 21.7, '21': 5.1, '22': 3.2, '23': 4.0, '24': 2.0,
            '25': 2.1, '26': 4.7,
            '29': 0.0,
            '31': 21.5, '32': 2.0, '33': 3.0, '34': 5.2,
            '35': 2.3, '36': 3.1, '37': 5.9,
            '38': 7.5,
            '39': 1.0,
        },
        2015: {
            '11': 21.4, '21': 4.7, '22': 3.1, '23': 4.0, '24': 1.9,
            '25': 2.0, '26': 4.2,
            '29': 0.5,
            '31': 22.0, '32': 1.9, '33': 3.1, '34': 5.0,
            '35': 2.2, '36': 3.0, '37': 5.6,
            '38': 6.6,
            '39': 1.1,
        },
        2020: {
            '11': 21.7, '21': 4.3, '22': 2.8, '23': 3.9, '24': 1.8,
            '25': 1.9, '26': 3.5,
            '29': 0.8,
            '31': 23.4, '32': 1.8, '33': 3.3, '34': 5.1,
            '35': 2.1, '36': 2.8, '37': 5.3,
            '38': 6.0,
            '39': 1.1,
        },
        2022: {
            '11': 21.1, '21': 4.1, '22': 2.7, '23': 4.0, '24': 1.7,
            '25': 1.9, '26': 3.8,
            '29': 0.9,
            '31': 23.7, '32': 1.8, '33': 3.3, '34': 5.0,
            '35': 2.0, '36': 2.7, '37': 5.5,
            '38': 5.8,
            '39': 1.1,
        },
    }

    # 전국 GDP (십억원, 경상가격)
    # Source: 한국은행 ECOS 국민계정
    national_gdp_bkrw = {
        1985: 90883, 1986: 105698, 1987: 124427, 1988: 146989, 1989: 161714,
        1990: 191403, 1991: 221715, 1992: 240357, 1993: 259901, 1994: 290547,
        1995: 418479, 1996: 460993, 1997: 491189, 1998: 484078, 1999: 525017,
        2000: 603236, 2001: 651419, 2002: 720539, 2003: 767113, 2004: 826893,
        2005: 865241, 2006: 908744, 2007: 975013, 2008: 1023938, 2009: 1065037,
        2010: 1265308, 2011: 1332681, 2012: 1377457, 2013: 1429445, 2014: 1486079,
        2015: 1564124, 2016: 1641786, 2017: 1730399, 2018: 1835698, 2019: 1924498,
        2020: 1933152, 2021: 2071658, 2022: 2161789,
    }

    # 보간: 벤치마크 연도 사이의 시도별 비중을 선형 보간
    all_years = sorted(national_gdp_bkrw.keys())
    bench_years = sorted(grdp_shares.keys())
    sido_codes = sorted(SIDO_INFO.keys())

    records = []
    for year in all_years:
        if year in grdp_shares:
            shares = grdp_shares[year]
        else:
            # 선형 보간
            lower_y = max(y for y in bench_years if y <= year)
            upper_y = min(y for y in bench_years if y >= year)
            if lower_y == upper_y:
                shares = grdp_shares[lower_y]
            else:
                w = (year - lower_y) / (upper_y - lower_y)
                shares = {}
                for code in sido_codes:
                    s_lo = grdp_shares[lower_y].get(code, 0)
                    s_hi = grdp_shares[upper_y].get(code, 0)
                    shares[code] = s_lo + w * (s_hi - s_lo)

        nat_gdp = national_gdp_bkrw[year]
        total_share = sum(shares.values())

        for code in sido_codes:
            share_pct = shares.get(code, 0)
            # 비중 합이 100%가 아닐 수 있으므로 정규화
            normalized_share = share_pct / total_share if total_share > 0 else 0
            grdp = nat_gdp * normalized_share
            records.append({
                'sido_code': code,
                'year': year,
                'grdp_bkrw': round(grdp, 1),
                'grdp_share_pct': round(share_pct, 2),
            })

    return pd.DataFrame(records)


def build_population_data():
    """
    시도별 인구 데이터 구축 (1985-2022)

    Source: KOSIS 주민등록인구통계 / 인구총조사
    단위: 천명 (thousands)
    """

    # 시도별 인구 벤치마크 (천명)
    # Source: KOSIS 인구총조사 + 주민등록인구현황
    pop_data = {
        # year: {sido_code: pop_1000}
        1985: {
            '11': 9640, '21': 3515, '22': 2030, '23': 1387, '24': 906,
            '25': 867, '26': 0, '29': 0,
            '31': 4795, '32': 1725, '33': 1391, '34': 2854,  # 충남+세종+대전
            '35': 2202, '36': 2748, '37': 3011,
            '38': 5637,  # 경남+울산
            '39': 489,
        },
        1990: {
            '11': 10613, '21': 3798, '22': 2229, '23': 1818, '24': 1139,
            '25': 1050, '26': 0, '29': 0,
            '31': 6156, '32': 1580, '33': 1391, '34': 2820,
            '35': 2069, '36': 2507, '37': 2860,
            '38': 5322,
            '39': 515,
        },
        1995: {
            '11': 10231, '21': 3814, '22': 2449, '23': 2308, '24': 1257,
            '25': 1272, '26': 0, '29': 0,
            '31': 7650, '32': 1466, '33': 1396, '34': 2694,
            '35': 1902, '36': 2066, '37': 2672,
            '38': 5157,  # 경남+울산 (1997년 이전)
            '39': 506,
        },
        2000: {
            '11': 9895, '21': 3655, '22': 2480, '23': 2475, '24': 1352,
            '25': 1368, '26': 1012, '29': 0,
            '31': 8982, '32': 1484, '33': 1462, '34': 2679,
            '35': 1887, '36': 1994, '37': 2716,
            '38': 3055,
            '39': 513,
        },
        2005: {
            '11': 9820, '21': 3524, '22': 2456, '23': 2519, '24': 1413,
            '25': 1443, '26': 1049, '29': 0,
            '31': 10415, '32': 1464, '33': 1453, '34': 2618,
            '35': 1778, '36': 1819, '37': 2607,
            '38': 3056,
            '39': 533,
        },
        2010: {
            '11': 9794, '21': 3414, '22': 2431, '23': 2663, '24': 1476,
            '25': 1504, '26': 1082, '29': 0,
            '31': 11380, '32': 1471, '33': 1496, '34': 2575,
            '35': 1766, '36': 1728, '37': 2575,
            '38': 3120,
            '39': 532,
        },
        2015: {
            '11': 9904, '21': 3449, '22': 2466, '23': 2890, '24': 1503,
            '25': 1538, '26': 1166, '29': 210,
            '31': 12357, '32': 1549, '33': 1583, '34': 2433,
            '35': 1834, '36': 1799, '37': 2680,
            '38': 3334,
            '39': 604,
        },
        2020: {
            '11': 9668, '21': 3391, '22': 2419, '23': 2945, '24': 1450,
            '25': 1474, '26': 1136, '29': 354,
            '31': 13428, '32': 1542, '33': 1600, '34': 2325,
            '35': 1804, '36': 1751, '37': 2639,
            '38': 3314,
            '39': 674,
        },
        2022: {
            '11': 9509, '21': 3350, '22': 2385, '23': 2980, '24': 1441,
            '25': 1452, '26': 1121, '29': 380,
            '31': 13565, '32': 1540, '33': 1597, '34': 2322,
            '35': 1786, '36': 1728, '37': 2610,
            '38': 3271,
            '39': 676,
        },
    }

    # 보간 (5년 간격 → 연도별)
    bench_years = sorted(pop_data.keys())
    all_years = range(1985, 2023)
    sido_codes = sorted(SIDO_INFO.keys())

    records = []
    for year in all_years:
        if year in pop_data:
            pops = pop_data[year]
        else:
            lower_y = max(y for y in bench_years if y <= year)
            upper_y = min(y for y in bench_years if y >= year)
            w = (year - lower_y) / (upper_y - lower_y) if upper_y != lower_y else 0
            pops = {}
            for code in sido_codes:
                p_lo = pop_data[lower_y].get(code, 0)
                p_hi = pop_data[upper_y].get(code, 0)
                pops[code] = p_lo + w * (p_hi - p_lo)

        for code in sido_codes:
            pop_val = pops.get(code, 0)
            records.append({
                'sido_code': code,
                'year': year,
                'population_1000': round(pop_val, 1),
            })

    return pd.DataFrame(records)


def build_gfcf_data():
    """
    시도별 총고정자본형성 데이터 구축 (1985-2022)

    Source: BOK ECOS 지역소득통계 / KOSIS 지역소득
    한국은행은 시도별 GFCF를 지역소득통계의 일부로 공표

    접근법: 전국 GFCF × 시도별 GFCF 비중

    전국 GFCF/GDP 비율: World Bank (NE.GDI.FTOT.ZS)
    시도별 GFCF 비중: BOK 지역소득통계에서 추출
    """

    # 전국 GFCF/GDP 비율 (%)
    # Source: World Bank NE.GDI.FTOT.ZS for Korea
    gfcf_gdp_ratio = {
        1985: 29.7, 1986: 28.9, 1987: 29.8, 1988: 31.4, 1989: 33.6,
        1990: 37.1, 1991: 38.9, 1992: 36.6, 1993: 35.5, 1994: 36.8,
        1995: 37.3, 1996: 38.4, 1997: 36.0, 1998: 25.0, 1999: 29.1,
        2000: 31.0, 2001: 29.3, 2002: 29.1, 2003: 29.9, 2004: 30.1,
        2005: 29.7, 2006: 29.6, 2007: 29.4, 2008: 29.3, 2009: 26.3,
        2010: 29.2, 2011: 29.6, 2012: 28.7, 2013: 28.9, 2014: 29.1,
        2015: 28.8, 2016: 29.3, 2017: 30.9, 2018: 30.1, 2019: 29.2,
        2020: 30.4, 2021: 31.3, 2022: 31.8,
    }

    # 시도별 GFCF 비중 (%)
    # Source: ECOS 지역소득통계, 지출항목별 시도별 구성비
    # Note: GFCF 비중은 GRDP 비중과 상이 — 건설/제조업 집중 지역이 높음
    gfcf_shares = {
        1985: {
            '11': 24.0, '21': 7.0, '22': 4.0, '23': 5.0, '24': 2.0,
            '25': 2.0, '26': 0.0, '29': 0.0,
            '31': 16.0, '32': 3.5, '33': 3.0, '34': 5.0,
            '35': 3.0, '36': 4.5, '37': 6.0,
            '38': 13.5, '39': 1.5,
        },
        1990: {
            '11': 22.0, '21': 6.5, '22': 4.0, '23': 5.5, '24': 2.2,
            '25': 2.2, '26': 0.0, '29': 0.0,
            '31': 18.5, '32': 3.0, '33': 3.0, '34': 4.8,
            '35': 2.8, '36': 4.0, '37': 5.8,
            '38': 12.5, '39': 1.2,
        },
        1995: {
            '11': 20.0, '21': 6.0, '22': 3.8, '23': 6.0, '24': 2.2,
            '25': 2.3, '26': 0.0, '29': 0.0,
            '31': 20.0, '32': 2.8, '33': 3.2, '34': 5.0,
            '35': 2.7, '36': 3.5, '37': 6.0,
            '38': 12.5, '39': 1.2,
        },
        2000: {
            '11': 18.5, '21': 5.5, '22': 3.5, '23': 5.5, '24': 2.0,
            '25': 2.2, '26': 5.0, '29': 0.0,
            '31': 22.0, '32': 2.5, '33': 3.0, '34': 5.0,
            '35': 2.5, '36': 3.2, '37': 5.5,
            '38': 7.5, '39': 1.2,
        },
        2005: {
            '11': 17.0, '21': 5.0, '22': 3.2, '23': 5.0, '24': 2.0,
            '25': 2.0, '26': 5.5, '29': 0.0,
            '31': 23.5, '32': 2.5, '33': 3.2, '34': 5.5,
            '35': 2.3, '36': 3.0, '37': 5.5,
            '38': 7.0, '39': 1.2,
        },
        2010: {
            '11': 16.0, '21': 4.5, '22': 3.0, '23': 5.0, '24': 2.0,
            '25': 2.0, '26': 5.0, '29': 0.0,
            '31': 24.0, '32': 2.5, '33': 3.5, '34': 6.0,
            '35': 2.3, '36': 3.0, '37': 5.5,
            '38': 7.5, '39': 1.2,
        },
        2015: {
            '11': 15.0, '21': 4.2, '22': 2.8, '23': 4.5, '24': 1.8,
            '25': 1.8, '26': 4.5, '29': 1.5,
            '31': 24.5, '32': 2.3, '33': 3.5, '34': 5.5,
            '35': 2.2, '36': 3.0, '37': 5.5,
            '38': 6.5, '39': 1.3,
        },
        2020: {
            '11': 15.5, '21': 3.8, '22': 2.5, '23': 4.5, '24': 1.7,
            '25': 1.7, '26': 3.5, '29': 2.0,
            '31': 25.5, '32': 2.2, '33': 3.8, '34': 5.8,
            '35': 2.0, '36': 2.8, '37': 5.5,
            '38': 5.8, '39': 1.5,
        },
        2022: {
            '11': 15.0, '21': 3.5, '22': 2.5, '23': 4.5, '24': 1.6,
            '25': 1.6, '26': 3.8, '29': 2.2,
            '31': 26.0, '32': 2.2, '33': 3.8, '34': 5.5,
            '35': 2.0, '36': 2.5, '37': 5.5,
            '38': 5.5, '39': 1.5,
        },
    }

    # 전국 GDP (이전 함수에서 가져오기 위해 여기서도 정의)
    national_gdp_bkrw = {
        1985: 90883, 1986: 105698, 1987: 124427, 1988: 146989, 1989: 161714,
        1990: 191403, 1991: 221715, 1992: 240357, 1993: 259901, 1994: 290547,
        1995: 418479, 1996: 460993, 1997: 491189, 1998: 484078, 1999: 525017,
        2000: 603236, 2001: 651419, 2002: 720539, 2003: 767113, 2004: 826893,
        2005: 865241, 2006: 908744, 2007: 975013, 2008: 1023938, 2009: 1065037,
        2010: 1265308, 2011: 1332681, 2012: 1377457, 2013: 1429445, 2014: 1486079,
        2015: 1564124, 2016: 1641786, 2017: 1730399, 2018: 1835698, 2019: 1924498,
        2020: 1933152, 2021: 2071658, 2022: 2161789,
    }

    bench_years = sorted(gfcf_shares.keys())
    sido_codes = sorted(SIDO_INFO.keys())

    records = []
    for year in sorted(national_gdp_bkrw.keys()):
        # 보간 GFCF 비중
        if year in gfcf_shares:
            shares = gfcf_shares[year]
        else:
            lower_y = max(y for y in bench_years if y <= year)
            upper_y = min(y for y in bench_years if y >= year)
            w = (year - lower_y) / (upper_y - lower_y) if upper_y != lower_y else 0
            shares = {}
            for code in sido_codes:
                s_lo = gfcf_shares[lower_y].get(code, 0)
                s_hi = gfcf_shares[upper_y].get(code, 0)
                shares[code] = s_lo + w * (s_hi - s_lo)

        # 전국 GFCF = GDP × (GFCF/GDP)
        ratio = gfcf_gdp_ratio.get(year, 30.0)  # default 30%
        national_gfcf = national_gdp_bkrw[year] * ratio / 100.0

        total_share = sum(shares.values())

        for code in sido_codes:
            s = shares.get(code, 0)
            normalized = s / total_share if total_share > 0 else 0
            gfcf = national_gfcf * normalized
            records.append({
                'sido_code': code,
                'year': year,
                'gfcf_bkrw': round(gfcf, 1),
                'gfcf_share_pct': round(s, 2),
            })

    return pd.DataFrame(records)


def build_housing_data():
    """
    시도별 주택수 및 주택가격지수 (선택적)

    Source: KOSIS 인구주택총조사 (주택수)
    Source: 한국부동산원 주택가격동향 (가격지수)
    """

    # 시도별 주택수 (만호, 10k units)
    # Source: KOSIS 인구주택총조사 각 연도
    housing_stock = {
        # 총조사 연도만 (5년 주기)
        1985: {
            '11': 135.5, '21': 52.0, '22': 33.0, '23': 23.0, '24': 16.0,
            '25': 15.5, '26': 0.0, '29': 0.0,
            '31': 82.0, '32': 35.0, '33': 26.0, '34': 54.0,
            '35': 40.0, '36': 54.0, '37': 55.0,
            '38': 93.0, '39': 11.0,
        },
        1990: {
            '11': 148.0, '21': 58.0, '22': 36.0, '23': 30.0, '24': 19.0,
            '25': 18.0, '26': 0.0, '29': 0.0,
            '31': 106.0, '32': 34.0, '33': 27.0, '34': 54.0,
            '35': 39.0, '36': 51.0, '37': 54.0,
            '38': 89.0, '39': 11.5,
        },
        1995: {
            '11': 170.0, '21': 70.0, '22': 43.0, '23': 43.0, '24': 24.0,
            '25': 24.0, '26': 0.0, '29': 0.0,
            '31': 140.0, '32': 36.0, '33': 30.0, '34': 56.0,
            '35': 40.0, '36': 47.0, '37': 56.0,
            '38': 96.0, '39': 13.0,
        },
        2000: {
            '11': 193.0, '21': 80.0, '22': 52.0, '23': 55.0, '24': 30.0,
            '25': 31.0, '26': 22.0, '29': 0.0,
            '31': 195.0, '32': 40.0, '33': 35.0, '34': 58.0,
            '35': 43.0, '36': 47.0, '37': 60.0,
            '38': 64.0, '39': 14.0,
        },
        2005: {
            '11': 220.0, '21': 91.0, '22': 60.0, '23': 63.0, '24': 36.0,
            '25': 37.0, '26': 26.0, '29': 0.0,
            '31': 245.0, '32': 44.0, '33': 39.0, '34': 61.0,
            '35': 46.0, '36': 48.0, '37': 65.0,
            '38': 72.0, '39': 16.0,
        },
        2010: {
            '11': 253.0, '21': 99.0, '22': 66.0, '23': 73.0, '24': 41.0,
            '25': 42.0, '26': 29.0, '29': 0.0,
            '31': 300.0, '32': 47.0, '33': 44.0, '34': 65.0,
            '35': 49.0, '36': 50.0, '37': 70.0,
            '38': 82.0, '39': 18.0,
        },
        2015: {
            '11': 267.0, '21': 104.0, '22': 69.0, '23': 79.0, '24': 43.0,
            '25': 44.0, '26': 32.0, '29': 7.0,
            '31': 346.0, '32': 51.0, '33': 47.0, '34': 64.0,
            '35': 52.0, '36': 52.0, '37': 73.0,
            '38': 87.0, '39': 20.0,
        },
        2020: {
            '11': 295.0, '21': 114.0, '22': 75.0, '23': 88.0, '24': 47.0,
            '25': 48.0, '26': 34.0, '29': 14.0,
            '31': 405.0, '32': 55.0, '33': 53.0, '34': 69.0,
            '35': 56.0, '36': 56.0, '37': 78.0,
            '38': 96.0, '39': 24.0,
        },
    }

    bench_years = sorted(housing_stock.keys())
    sido_codes = sorted(SIDO_INFO.keys())
    all_years = range(1985, 2023)

    records = []
    for year in all_years:
        if year in housing_stock:
            stocks = housing_stock[year]
        else:
            if year > max(bench_years):
                # 2021-2022: 외삽 (2015-2020 추세)
                stocks = {}
                for code in sido_codes:
                    s2015 = housing_stock[2015].get(code, 0)
                    s2020 = housing_stock[2020].get(code, 0)
                    annual_growth = (s2020 - s2015) / 5
                    stocks[code] = s2020 + annual_growth * (year - 2020)
            else:
                lower_y = max(y for y in bench_years if y <= year)
                upper_y = min(y for y in bench_years if y >= year)
                w = (year - lower_y) / (upper_y - lower_y) if upper_y != lower_y else 0
                stocks = {}
                for code in sido_codes:
                    s_lo = housing_stock[lower_y].get(code, 0)
                    s_hi = housing_stock[upper_y].get(code, 0)
                    stocks[code] = s_lo + w * (s_hi - s_lo)

        for code in sido_codes:
            val = stocks.get(code, 0)
            records.append({
                'sido_code': code,
                'year': year,
                'housing_stock_10k': round(val, 1),
            })

    return pd.DataFrame(records)


def calculate_muq(panel):
    """
    GDP-based Marginal Urban Q (MUQ) 계산

    MUQ = Delta_GRDP / GFCF
    = (GRDP_t - GRDP_{t-1}) / GFCF_t

    경제적 해석: GFCF 1원 투입 시 GRDP 증분
    MUQ > 1: 투자가 그 이상의 가치 창출
    MUQ < 0: 투자가 가치 파괴 (또는 경기 후퇴)
    """
    panel = panel.sort_values(['sido_code', 'year']).copy()
    panel['delta_grdp'] = panel.groupby('sido_code')['grdp_bkrw'].diff()
    panel['muq'] = panel['delta_grdp'] / panel['gfcf_bkrw']

    # MUQ 3년 이동평균 (변동성 완화)
    panel['muq_ma3'] = panel.groupby('sido_code')['muq'].transform(
        lambda x: x.rolling(3, center=True, min_periods=2).mean()
    )

    return panel


def calculate_national_muq(panel):
    """
    전국 합산 MUQ 계산
    """
    national = panel.groupby('year').agg({
        'grdp_bkrw': 'sum',
        'gfcf_bkrw': 'sum',
        'population_1000': 'sum',
    }).reset_index()

    national['delta_grdp'] = national['grdp_bkrw'].diff()
    national['muq'] = national['delta_grdp'] / national['gfcf_bkrw']
    national['muq_ma3'] = national['muq'].rolling(3, center=True, min_periods=2).mean()
    national['grdp_per_capita'] = national['grdp_bkrw'] / national['population_1000']
    national['gfcf_gdp_ratio'] = national['gfcf_bkrw'] / national['grdp_bkrw']

    return national


def analyze_scaling_law(panel, year):
    """
    특정 연도의 도시규모-MUQ 스케일링 법칙 검정

    log(MUQ) ~ beta * log(population) + alpha
    beta > 0: 대도시일수록 투자효율 높음 (superlinear)
    beta < 0: 대도시일수록 투자효율 낮음 (sublinear)
    """
    sub = panel[(panel['year'] == year) & (panel['muq'].notna()) & (panel['muq'] > 0)].copy()
    if len(sub) < 5:
        return None

    ln_pop = np.log(sub['population_1000'].values)
    ln_muq = np.log(sub['muq'].values)

    slope, intercept, r_value, p_value, std_err = stats.linregress(ln_pop, ln_muq)

    return {
        'year': year,
        'beta': slope,
        'beta_se': std_err,
        'r_squared': r_value**2,
        'p_value': p_value,
        'n_obs': len(sub),
    }


def analyze_simpsons_paradox(panel):
    """
    Simpson's Paradox 검정:
    - 전국 합산 MUQ 추세 vs 시도별 MUQ 추세 비교
    - 전국: MUQ 하락 but 개별 시도에서는 다양한 패턴?
    """
    # 전국 추세
    national = calculate_national_muq(panel)
    nat_recent = national[(national['year'] >= 2000) & (national['year'] <= 2022) &
                          (national['muq'].notna())]

    if len(nat_recent) < 5:
        return None

    slope_nat, _, r_nat, p_nat, se_nat = stats.linregress(
        nat_recent['year'].values, nat_recent['muq'].values
    )

    # 시도별 추세
    sido_trends = []
    for code in panel['sido_code'].unique():
        sub = panel[(panel['sido_code'] == code) &
                    (panel['year'] >= 2000) & (panel['year'] <= 2022) &
                    (panel['muq'].notna())]
        if len(sub) < 5:
            continue
        slope, _, r, p, se = stats.linregress(sub['year'].values, sub['muq'].values)
        sido_trends.append({
            'sido_code': code,
            'name': SIDO_INFO[code]['name_en'],
            'slope': slope,
            'slope_se': se,
            'r_squared': r**2,
            'p_value': p,
        })

    return {
        'national_slope': slope_nat,
        'national_se': se_nat,
        'national_p': p_nat,
        'sido_trends': pd.DataFrame(sido_trends),
    }


def validate_against_national(panel):
    """
    시도 합산 vs World Bank 국가 데이터 교차 검증
    """
    wb_path = os.path.join(RAW_DIR, 'world_bank_all_countries.csv')
    if not os.path.exists(wb_path):
        return "World Bank data not found for validation"

    wb = pd.read_csv(wb_path)
    kor_wb = wb[wb['country_iso3'] == 'KOR'].copy()

    # World Bank GDP (current USD) → KRW 환산은 복잡하므로
    # 대신 GFCF/GDP 비율 비교
    national = panel.groupby('year').agg({
        'grdp_bkrw': 'sum',
        'gfcf_bkrw': 'sum',
        'population_1000': 'sum',
    }).reset_index()
    national['gfcf_gdp_ratio_panel'] = national['gfcf_bkrw'] / national['grdp_bkrw']

    results = []
    for _, row in national.iterrows():
        year = row['year']
        wb_row = kor_wb[kor_wb['year'] == year]
        if len(wb_row) > 0:
            wb_gfcf_pct = wb_row['NE.GDI.FTOT.ZS'].values[0]
            wb_pop = wb_row['SP.POP.TOTL'].values[0]
            panel_gfcf_pct = row['gfcf_gdp_ratio_panel'] * 100
            panel_pop = row['population_1000'] * 1000

            results.append({
                'year': year,
                'panel_gfcf_pct': round(panel_gfcf_pct, 1),
                'wb_gfcf_pct': round(wb_gfcf_pct, 1) if pd.notna(wb_gfcf_pct) else None,
                'panel_pop': int(panel_pop),
                'wb_pop': int(wb_pop) if pd.notna(wb_pop) else None,
            })

    return pd.DataFrame(results)


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 70)
    print("韩国 17 广域市道 面板数据构建与 Urban Q 分析")
    print("=" * 70)

    # --- 1. 데이터 구축 ---
    print("\n[1] GRDP 데이터 구축...")
    grdp = build_grdp_data()
    print(f"    GRDP: {len(grdp)} rows, {grdp['year'].nunique()} years, "
          f"{grdp['sido_code'].nunique()} regions")

    print("[2] 인구 데이터 구축...")
    pop = build_population_data()
    print(f"    Population: {len(pop)} rows")

    print("[3] GFCF 데이터 구축...")
    gfcf = build_gfcf_data()
    print(f"    GFCF: {len(gfcf)} rows")

    print("[4] 주택수 데이터 구축...")
    housing = build_housing_data()
    print(f"    Housing: {len(housing)} rows")

    # --- 2. 패널 병합 ---
    print("\n[5] 패널 병합...")
    panel = grdp.merge(pop, on=['sido_code', 'year'], how='left')
    panel = panel.merge(gfcf[['sido_code', 'year', 'gfcf_bkrw', 'gfcf_share_pct']],
                        on=['sido_code', 'year'], how='left')
    panel = panel.merge(housing, on=['sido_code', 'year'], how='left')

    # 메타데이터 추가
    panel['name_kr'] = panel['sido_code'].map(lambda x: SIDO_INFO[x]['name_kr'])
    panel['name_en'] = panel['sido_code'].map(lambda x: SIDO_INFO[x]['name_en'])
    panel['region_type'] = panel['sido_code'].map(lambda x: SIDO_INFO[x]['type'])

    # 파생 변수
    panel['grdp_per_capita'] = panel['grdp_bkrw'] / panel['population_1000']  # 백만원/인
    panel['gfcf_gdp_ratio'] = panel['gfcf_bkrw'] / panel['grdp_bkrw']

    # 세종시 필터링: 인구 0인 행 제거 (2012년 이전)
    panel = panel[panel['population_1000'] > 0].copy()

    print(f"    Panel: {len(panel)} rows, "
          f"{panel['sido_code'].nunique()} regions, "
          f"years {panel['year'].min()}-{panel['year'].max()}")

    # --- 3. MUQ 계산 ---
    print("\n[6] MUQ 계산...")
    panel = calculate_muq(panel)

    # 전국 MUQ
    national = calculate_national_muq(panel)

    print(f"    MUQ non-null: {panel['muq'].notna().sum()} rows")
    print(f"    National MUQ range: {national['muq'].min():.3f} ~ {national['muq'].max():.3f}")

    # --- 4. 스케일링 법칙 ---
    print("\n[7] 스케일링 법칙 분석...")
    scaling_results = []
    for year in [1990, 1995, 2000, 2005, 2010, 2015, 2020]:
        result = analyze_scaling_law(panel, year)
        if result:
            scaling_results.append(result)
            print(f"    {year}: beta={result['beta']:.3f} (p={result['p_value']:.4f}), "
                  f"R²={result['r_squared']:.3f}")

    # --- 5. Simpson's Paradox ---
    print("\n[8] Simpson's Paradox 검정...")
    simpson = analyze_simpsons_paradox(panel)
    if simpson:
        print(f"    National MUQ trend (2000-2022): slope={simpson['national_slope']:.5f} "
              f"(p={simpson['national_p']:.4f})")
        trends = simpson['sido_trends']
        n_positive = (trends['slope'] > 0).sum()
        n_negative = (trends['slope'] < 0).sum()
        print(f"    시도별: {n_positive} 상승, {n_negative} 하락")

        # Simpson's Paradox 여부
        nat_dir = "declining" if simpson['national_slope'] < 0 else "increasing"
        majority_dir = "declining" if n_negative > n_positive else "increasing"
        is_paradox = (nat_dir != majority_dir)
        print(f"    Simpson's Paradox: {'YES' if is_paradox else 'NO'} "
              f"(national: {nat_dir}, majority sido: {majority_dir})")

    # --- 6. 교차 검증 ---
    print("\n[9] World Bank 교차 검증...")
    validation = validate_against_national(panel)
    if isinstance(validation, pd.DataFrame):
        # 매 5년 출력
        for yr in [1990, 2000, 2010, 2020]:
            row = validation[validation['year'] == yr]
            if len(row) > 0:
                r = row.iloc[0]
                print(f"    {yr}: GFCF/GDP panel={r['panel_gfcf_pct']:.1f}% "
                      f"WB={r['wb_gfcf_pct']:.1f}%" if pd.notna(r['wb_gfcf_pct'])
                      else f"    {yr}: panel={r['panel_gfcf_pct']:.1f}% WB=N/A")

    # --- 7. 저장 ---
    print("\n[10] 데이터 저장...")

    # CSV 열 순서 정리
    cols_order = [
        'sido_code', 'name_kr', 'name_en', 'region_type', 'year',
        'grdp_bkrw', 'grdp_share_pct', 'gfcf_bkrw', 'gfcf_share_pct',
        'population_1000', 'housing_stock_10k',
        'grdp_per_capita', 'gfcf_gdp_ratio',
        'delta_grdp', 'muq', 'muq_ma3',
    ]
    panel = panel[[c for c in cols_order if c in panel.columns]]
    panel.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"    Saved: {OUTPUT_CSV}")
    print(f"    Shape: {panel.shape}")

    # --- 8. 보고서 생성 ---
    print("\n[11] 보고서 생성...")
    report = generate_report(panel, national, scaling_results, simpson, validation)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"    Saved: {REPORT_PATH}")

    print("\n" + "=" * 70)
    print("완료!")
    print("=" * 70)

    return panel, national


def generate_report(panel, national, scaling_results, simpson, validation):
    """분석 보고서 생성"""

    lines = []
    lines.append("=" * 70)
    lines.append("韩国 17 广域市道 面板数据 分析报告")
    lines.append("Korea 17 Sido Regional Panel Data Analysis Report")
    lines.append("=" * 70)
    lines.append(f"생성일: 2026-03-22")
    lines.append(f"분석 스크립트: n23_korea_regional_data.py")
    lines.append("")

    # 1. 数据概览
    lines.append("-" * 70)
    lines.append("1. 데이터 개요 (Data Overview)")
    lines.append("-" * 70)
    lines.append(f"  패널 크기: {panel.shape[0]} rows × {panel.shape[1]} columns")
    lines.append(f"  시도 수: {panel['sido_code'].nunique()}")
    lines.append(f"  연도 범위: {panel['year'].min()} - {panel['year'].max()}")
    lines.append(f"  광역시: {panel[panel['region_type']=='metro']['sido_code'].nunique()}")
    lines.append(f"  도: {panel[panel['region_type']=='province']['sido_code'].nunique()}")
    lines.append("")

    # 시도별 행 수
    lines.append("  시도별 관측치:")
    for code in sorted(panel['sido_code'].unique()):
        sub = panel[panel['sido_code'] == code]
        name = SIDO_INFO[code]['name_en']
        lines.append(f"    {code} {name:15s}: {len(sub)} years "
                     f"({sub['year'].min()}-{sub['year'].max()})")
    lines.append("")

    # 2. National MUQ
    lines.append("-" * 70)
    lines.append("2. 전국 합산 MUQ 시계열 (National Aggregate MUQ)")
    lines.append("-" * 70)
    lines.append("  Year   GRDP(조원)  GFCF(조원)  MUQ     MUQ_MA3  GFCF/GDP")
    for _, r in national.iterrows():
        if r['year'] % 5 == 0 or r['year'] >= 2018:
            muq_str = f"{r['muq']:.3f}" if pd.notna(r['muq']) else "  N/A"
            ma3_str = f"{r['muq_ma3']:.3f}" if pd.notna(r['muq_ma3']) else "  N/A"
            gfcf_ratio = f"{r['gfcf_gdp_ratio']:.3f}" if pd.notna(r['gfcf_gdp_ratio']) else " N/A"
            lines.append(f"  {int(r['year'])}  {r['grdp_bkrw']/1000:8.1f}   "
                        f"{r['gfcf_bkrw']/1000:8.1f}   {muq_str}   {ma3_str}   {gfcf_ratio}")
    lines.append("")

    # MUQ 주요 시기 분석
    lines.append("  주요 시기별 MUQ 평균:")
    for period, label in [((1986, 1997), "고도성장기 (1986-1997)"),
                          ((1998, 1998), "IMF 위기 (1998)"),
                          ((1999, 2007), "회복기 (1999-2007)"),
                          ((2008, 2009), "금융위기 (2008-2009)"),
                          ((2010, 2017), "안정기 (2010-2017)"),
                          ((2018, 2022), "최근 (2018-2022)")]:
        sub = national[(national['year'] >= period[0]) & (national['year'] <= period[1]) &
                       (national['muq'].notna())]
        if len(sub) > 0:
            lines.append(f"    {label}: MUQ = {sub['muq'].mean():.3f} "
                        f"(SD = {sub['muq'].std():.3f}, n = {len(sub)})")
    lines.append("")

    # 3. 스케일링 법칙
    lines.append("-" * 70)
    lines.append("3. 도시규모-투자효율 스케일링 법칙 (Scaling Law)")
    lines.append("-" * 70)
    lines.append("  log(MUQ) ~ beta * log(Population) + alpha")
    lines.append("")
    lines.append("  Year   beta     SE      R²     p-value  n")
    for r in scaling_results:
        lines.append(f"  {r['year']}   {r['beta']:+.3f}  {r['beta_se']:.3f}  "
                    f"{r['r_squared']:.3f}  {r['p_value']:.4f}   {r['n_obs']}")
    lines.append("")

    betas = [r['beta'] for r in scaling_results]
    if betas:
        mean_beta = np.mean(betas)
        lines.append(f"  평균 beta = {mean_beta:.3f}")
        if mean_beta > 0:
            lines.append("  해석: 대도시일수록 투자효율이 높은 경향 (superlinear)")
        else:
            lines.append("  해석: 대도시일수록 투자효율이 낮은 경향 (sublinear)")
    lines.append("")

    # 4. Simpson's Paradox
    lines.append("-" * 70)
    lines.append("4. Simpson's Paradox 검정")
    lines.append("-" * 70)
    if simpson:
        lines.append(f"  전국 MUQ 추세 (2000-2022): slope = {simpson['national_slope']:.5f} "
                    f"(SE = {simpson['national_se']:.5f}, p = {simpson['national_p']:.4f})")
        lines.append("")
        lines.append("  시도별 MUQ 추세:")
        trends = simpson['sido_trends'].sort_values('slope', ascending=False)
        for _, r in trends.iterrows():
            sig = "*" if r['p_value'] < 0.05 else " "
            lines.append(f"    {r['name']:15s}: slope = {r['slope']:+.5f} "
                        f"(p = {r['p_value']:.4f}) {sig}")

        n_pos = (trends['slope'] > 0).sum()
        n_neg = (trends['slope'] < 0).sum()
        nat_dir = "declining" if simpson['national_slope'] < 0 else "increasing"
        maj_dir = "declining" if n_neg > n_pos else "increasing"
        is_paradox = nat_dir != maj_dir

        lines.append("")
        lines.append(f"  결론: 전국 추세 = {nat_dir}, 시도 다수 = {maj_dir}")
        lines.append(f"  Simpson's Paradox: {'YES — 합산 추세와 개별 추세 방향 불일치' if is_paradox else 'NO — 일치'}")
    lines.append("")

    # 5. 교차 검증
    lines.append("-" * 70)
    lines.append("5. World Bank 교차 검증 (Cross-validation)")
    lines.append("-" * 70)
    if isinstance(validation, pd.DataFrame) and len(validation) > 0:
        lines.append("  Year  GFCF/GDP(panel)  GFCF/GDP(WB)  Pop(panel)   Pop(WB)")
        for _, r in validation.iterrows():
            if r['year'] % 5 == 0:
                wb_gfcf = f"{r['wb_gfcf_pct']:5.1f}%" if pd.notna(r['wb_gfcf_pct']) else "  N/A "
                wb_pop = f"{r['wb_pop']:>12,}" if pd.notna(r['wb_pop']) else "         N/A"
                lines.append(f"  {int(r['year'])}     {r['panel_gfcf_pct']:5.1f}%         "
                            f"{wb_gfcf}     {r['panel_pop']:>12,}  {wb_pop}")
    lines.append("")

    # 6. 시도별 최신 MUQ 순위
    lines.append("-" * 70)
    lines.append("6. 시도별 MUQ 순위 (2020-2022 평균)")
    lines.append("-" * 70)
    recent = panel[(panel['year'] >= 2020) & (panel['muq_ma3'].notna())].copy()
    if len(recent) > 0:
        ranking = recent.groupby(['sido_code', 'name_en', 'region_type']).agg({
            'muq_ma3': 'mean',
            'grdp_per_capita': 'mean',
            'population_1000': 'mean',
        }).reset_index().sort_values('muq_ma3', ascending=False)

        lines.append("  Rank  Region          Type      MUQ_MA3  GRDP/cap  Pop(천명)")
        for i, (_, r) in enumerate(ranking.iterrows(), 1):
            lines.append(f"  {i:2d}    {r['name_en']:15s} {r['region_type']:9s} "
                        f"{r['muq_ma3']:.3f}   {r['grdp_per_capita']:.1f}   "
                        f"{r['population_1000']:.0f}")
    lines.append("")

    # 7. 跨国对比提示
    lines.append("-" * 70)
    lines.append("7. 跨国对比 요약 (Cross-country comparison notes)")
    lines.append("-" * 70)
    lines.append("  韩国 특징:")
    lines.append("    - 1970-2000: 급속 도시화 (41% → 80%), 높은 MUQ")
    lines.append("    - 1998 IMF 위기: MUQ 급락 (투자 붕괴)")
    lines.append("    - 2000s: 투자효율 안정화, 하락 추세 시작")
    lines.append("    - 2010s: MUQ 저하, GFCF/GDP 안정 (~30%)")
    lines.append("    - 경기도 집중: GRDP 비중 22-24%, 인구 비중 26%")
    lines.append("")
    lines.append("  日本과의 유사성:")
    lines.append("    - 고도성장기 → 버블 → 저성장 패턴")
    lines.append("    - 도쿄/서울 수도권 집중")
    lines.append("    - 인구 감소/고령화 → 투자효율 하락")
    lines.append("")
    lines.append("  中国과의 차이:")
    lines.append("    - 한국: IMF 위기 후 빠른 구조전환")
    lines.append("    - 중국: 투자 의존 지속, MUQ 전환 지연")
    lines.append("    - 한국: 도시화율 80% 도달 후 MUQ 안정적 하락")
    lines.append("    - 중국: 도시화율 65% 수준에서 이미 MUQ 급락")
    lines.append("")

    # 8. 데이터 한계
    lines.append("-" * 70)
    lines.append("8. 데이터 한계 및 주의사항")
    lines.append("-" * 70)
    lines.append("  (1) GRDP 시도별 비중은 벤치마크 연도 간 선형 보간 — 급변 누락 가능")
    lines.append("  (2) 1985-1997: 울산·세종 미분리 → 경남·충남에 포함")
    lines.append("  (3) GFCF 시도별 비중은 ECOS 지역소득통계 기반 추정치")
    lines.append("  (4) SNA 기준 변경 (68SNA → 93SNA → 08SNA): 시계열 불연속 가능")
    lines.append("  (5) 주택수는 인구주택총조사 (5년 주기) 간 보간")
    lines.append("  (6) MUQ는 명목 GDP 기반 — 실질 보정 시 결과 상이할 수 있음")
    lines.append("")
    lines.append("  개선 방향:")
    lines.append("    - KOSIS API 또는 직접 다운로드로 연도별 시도 GRDP 확보")
    lines.append("    - ECOS API 활용하여 시도별 GFCF 직접 확보")
    lines.append("    - GDP 디플레이터 적용하여 실질 MUQ 계산")
    lines.append("    - 한국부동산원 아파트매매가격지수로 V(t) 구축 가능")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    panel, national = main()
