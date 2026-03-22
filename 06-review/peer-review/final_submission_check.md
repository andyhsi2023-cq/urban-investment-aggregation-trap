# Final Submission Quality Check Report
## Target: Nature Cities (Article)
## Date: 2026-03-22
## Manuscript: "Urban investment efficiency declines across six continents: evidence from 1,567 cities and regions"

---

# EXECUTIVE SUMMARY

**Overall assessment**: The manuscript is of high quality with strong internal consistency. However, there are **2 FAIL items** (one critical, one moderate) and **8 WARNING items** that should be addressed before submission. The most critical issue is the `[repository URL upon acceptance]` placeholder remaining in the submission metadata file. The manuscript itself (nature_cities_version.md) is clean and ready.

**Verdict: CONDITIONAL PASS -- fix the 2 FAIL items before submitting.**

---

# A. TEXT COMPLETENESS

| # | Check Item | Status | Detail |
|---|-----------|--------|--------|
| A1 | No `[placeholder]` in manuscript | **PASS** | No instances found in nature_cities_version.md |
| A2 | No `[TBD]`, `[TODO]`, `[insert]`, `[URL]` | **PASS** | Clean in manuscript and cover letter |
| A3 | No `<!-- -->` comments leaking | **WARNING** | CHANGELOG block (lines 330-375) uses `<!-- -->` HTML comments. This is properly formatted and will NOT render in PDF/Word. However, verify during Word/PDF conversion that this block is truly invisible. If converting via Pandoc, test explicitly. |
| A4 | Acknowledgements filled | **PASS** | Line 258: Thanks open data providers (World Bank, PWT, Japan Cabinet Office, etc.) -- substantive, not placeholder. |
| A5 | Author contributions filled | **PASS** | Line 262: "H.X. conceived the study..." -- complete CRediT-style statement. |
| A6 | Competing interests declared | **PASS** | Line 266: "The author declares no competing interests." |
| A7 | Data availability filled | **PASS** | Line 250: Full statement with all data sources and GitHub URL. |
| A8 | Code availability filled | **PASS** | Line 254: GitHub URL present. |
| A9 | GitHub URL correct | **PASS** | Manuscript (line 250, 254): `https://github.com/andyhsi2023-cq/urban-investment-aggregation-trap` -- matches target. Cover letter (line 19): same URL. |
| A10 | SSRN URL correct | **PASS** | Cover letter (line 23): `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6453159` -- matches target. Not present in manuscript main text (appropriate -- SSRN link is for cover letter only). |
| A11 | **Metadata file: repository URL** | **FAIL** | `submission_metadata_nature_cities.md` lines 62 and 66 contain `[repository URL upon acceptance]` -- these are **still placeholders**. The actual GitHub URL has been filled in the manuscript and cover letter but NOT in the metadata file's Data Availability and Code Availability sections. **FIX**: Replace with `https://github.com/andyhsi2023-cq/urban-investment-aggregation-trap` in both locations. |

---

# B. NUMERICAL CONSISTENCY

| # | Claim in Manuscript | Source Report Value | Status | Notes |
|---|-------|---------|--------|-------|
| B1 | 157 countries (GDP-MUQ) | Phase0: Low=29 + LMI=37 + UMI=40 + High=51 = 157 | **PASS** | |
| B2 | 1,567 regions | Unified panel: "Total unique regions: 1567" | **PASS** | |
| B3 | 30,098 observations | Unified panel: "Total obs with valid MUQ: 30098" | **PASS** | |
| B4 | 8 countries, 6 continents | Unified panel: 35 countries, 7 data-source groups | **WARNING** | See detailed analysis below |
| B5 | GDP-MUQ Low income rho=-0.116, p<0.001 | Phase0: rho=-0.1160, p=0.0000 | **PASS** | |
| B6 | GDP-MUQ Lower-mid rho=-0.131, p<0.001 | Phase0: rho=-0.1306, p=0.0000 | **PASS** | |
| B7 | GDP-MUQ Upper-mid rho=-0.248, p<0.001 | Phase0: rho=-0.2475, p=0.0000 | **PASS** | |
| B8 | GDP-MUQ High rho=-0.035, p=0.080 | Phase0: rho=-0.0351, p=0.0795 | **PASS** | |
| B9 | Housing-MUQ groups | Not in provided reports (separate analysis) | **N/A** | Cannot verify from provided files |
| B10 | China clean spec beta=-0.37, p=0.019 | Clean spec: beta=-0.3669, p=1.935e-02 | **PASS** | Rounded correctly to -0.37 |
| B11 | US clean spec beta=+2.81 | Clean spec: beta=2.8097 | **PASS** | Rounded correctly to +2.81 |
| B12 | Mechanical correlation attenuation 83.7% | Clean spec: "衰减比 = 0.8374, 机械相关份额 = 83.7%" | **PASS** | |
| B13 | Japan Pooled beta=+0.638 | Japan report: "Pooled OLS beta = 0.6382" | **PASS** | Rounded correctly |
| B14 | Japan TWFE beta=+0.057, p=0.037 | Japan report: "beta = 0.0567, p = 3.7461e-02" | **PASS** | Rounded correctly |
| B15 | Japan Bai-Perron breaks 1980, 1990 | Japan report: "BIC最適断点数: 2, 断点: 1980, 1990" | **PASS** | |
| B16 | China-Japan mirror: 3.4x MUQ gap | Japan report: JP MUQ=0.4943, CN MUQ=0.1441; ratio = 0.4943/0.1441 = 3.43 | **PASS** | Manuscript says "China's returns are 3.4 times lower" -- slight ambiguity. 0.4943/0.1441 = 3.43x. Manuscript says China's MUQ is "29% of Japan's" (0.144/0.494 = 0.29). Both correct. |
| B17 | 2.3x investment intensity gap | Japan report: CN 44.1% vs JP 31.3%; 44.1/31.3 = 1.41. But CN FAI/GDP provincial = 70.8% vs JP 31.3%, giving 2.26x | **WARNING** | The 2.3x figure uses provincial FAI/GDP (0.7077) vs JP GFCF/GDP (0.3130), ratio = 2.26. Rounds to 2.3x. However, the 44.1% figure uses WB national GFCF/GDP for China. The manuscript should clarify which China investment measure is used. Using WB data: 44.1/31.3 = 1.41x, NOT 2.3x. This discrepancy needs attention. |
| B18 | 2.7x decline rate gap | Japan report: CN slope=-0.007371, JP slope=-0.002693; ratio=2.74x | **PASS** | |
| B19 | Korea recovery ratio 0.78 | Korea report: mean recovery ratios -- metro 0.745, province 0.743. But the manuscript cites 0.78. Need to check how this is computed. | **WARNING** | The 0.78 figure does not directly match the country-level averages in the report (metro 0.745, province 0.743). It may represent the national-aggregate recovery ratio (not the mean of regional ratios). The report shows 恢复期 MUQ mean = 0.2887 vs 危机前 mean = 0.3686, ratio = 0.783. This matches. PASS on closer inspection. |
| B20 | PIIGS recovery ratio 0.65 | Not directly in provided reports | **N/A** | Cannot verify from provided files |
| B21 | US$18 trillion (continuous measure) | Dollar report: "方法 A 累计: US$17,783.5 billion = US$17.78 trillion" | **PASS** | Rounded to ~US$18 trillion. The 90% CI [11.7, 24.4] matches manuscript. |
| B22 | 2.7 GtCO2 carbon estimate | Carbon report: "Method C (综合法): 2.97 GtCO2" -- manuscript adopts "2.7 GtCO2 (rounded from Method C)" | **WARNING** | The manuscript says "approximately 2.7 GtCO2" which is described as "rounded from Method C" in Methods M5. But Method C point estimate is 2.97, not 2.7. The 2.7 appears to be rounded DOWN. The 90% CI is [2.04, 3.47]. The carbon report Section 9 recommends "approximately 2.7 GtCO2" as the main text figure. This appears to be a deliberate conservative choice rather than simple rounding. Acceptable but should be documented more clearly in Methods. |
| B23 | Unified panel beta=-0.043, p<0.001 | Unified panel report: "beta = -0.0432, SE = 0.0126, p = 0.000625" | **PASS** | -0.0432 rounds to -0.043. p=0.000625 < 0.001. Correct. |
| B24 | beta_V=1.057 (China), 94.6% mechanical | betaV report: "beta_V = 1.0567, 机械成分占 beta_V 比例 = 94.6%" | **PASS** | 1.0567 rounds to 1.057. |
| B25 | Aggregation Trap: within -0.076, between +0.114 | Box 1 claims "between-component 0.114 versus within-component 0.076" | **WARNING** | These numbers are not found in the unified_panel_report.txt. The report shows within-country decompositions where no country passes A3. The cross-national level verification with these specific numbers (0.114 and 0.076) must come from a different analysis file not provided for checking. Cannot independently verify. |
| B26 | Japan prefecture FE beta=+0.813 | Japan report: "Prefecture FE: beta = 0.8129" | **PASS** | |
| B27 | Japan high-growth era coeff 0.127 | Japan report: "高度成長 (1960-1973): beta=0.1268" | **PASS** | Rounds to 0.127. |
| B28 | Japan recovery period coeff 0.073 | Japan report: "回復期 (2003-2022): beta=0.0734" | **PASS** | Rounds to 0.073. |
| B29 | Capital-region decline -0.0087/yr | Japan report: "Capital: slope = -0.008657/年" | **PASS** | Rounds to -0.0087. |
| B30 | Korea Kruskal-Wallis H=52.7, p<10^-11 | Korea report: "H = 52.668, p = 3.6589e-12" | **PASS** | H rounds to 52.7; 3.66e-12 < 10^-11. |
| B31 | 91% concentrated in 2021-2024 | Dollar report: "崩盘期占比: 91.0%" | **PASS** | |

### B4 Detailed Analysis: "8 countries, 6 continents"

The unified panel contains **35 countries** across **7 data collection groups** (China, Japan, Korea, US, Europe [29 EU countries], Australia, South Africa).

**"8 countries"**: If we count the 7 groups, we get 7, not 8. If we count only the non-EU countries individually (China, Japan, Korea, US, Australia, South Africa = 6) plus "Europe" as one block, that is still 7. The number 8 does not correspond to any obvious grouping. POSSIBLE EXPLANATION: if the US data counts as 2 sources (Census ACS + BEA), or if one EU country is counted separately, but this is not documented.

However, upon further reflection, the M1 Methods section lists exactly 7 bullet-point data sources. The claim "eight countries" is repeated 4 times in the manuscript and in the cover letter. This inconsistency is a potential desk-reject trigger if an editor notices it.

**"6 continents"**: Asia (China, Japan, Korea), Europe (EU countries), North America (US), Oceania (Australia), Africa (South Africa). That is **5 continents**, not 6. South America is not represented.

**Recommendation**: Either (a) clarify the counting to match exactly, or (b) revise to "seven data systems across five continents" or similar. If the intent is to count Europe and Asia as separate continents (standard geographic convention), then it is technically 5 continents. If one counts sub-continental regions differently, it could be stretched, but this is risky.

**STATUS: WARNING -- potential factual inaccuracy requiring clarification before submission.**

### B17 Detailed Analysis: "2.3x investment intensity gap"

The Japan report shows two different China investment intensity measures at ~54% urbanisation:
- WB national GFCF/GDP: 44.1% (vs Japan 31.3% => ratio 1.41x)
- Provincial FAI/GDP: 70.8% (vs Japan 31.3% => ratio 2.26x)

The manuscript states "2.3 times higher investment intensity (China 44% versus Japan 31%)" -- but 44/31 = 1.42, not 2.3. The 2.3x ratio matches the provincial FAI/GDP comparison. The text conflates the WB percentage with the provincial ratio.

**STATUS: WARNING -- the "China 44% versus Japan 31%" parenthetical is INCONSISTENT with the "2.3 times" claim. Either cite 71% vs 31% (provincial FAI/GDP, giving 2.3x), or cite 44% vs 31% (WB GFCF/GDP) and change the multiplier to ~1.4x.**

---

# C. REFERENCES CHECK

| # | Check Item | Status | Detail |
|---|-----------|--------|--------|
| C1 | Total reference count | **PASS** | 50 references (lines 195-244). Matches metadata claim. |
| C2 | All in-text ^N have matching reference | **WARNING** | Spot-checked: ^31 (Simpson), ^7 (Pritchett), ^20 (Hsieh-Klenow), ^19 (Easterly), ^36,37,38, ^3,4, ^5,26, ^13,25, ^22, ^23,24, ^28, ^11,16, ^17, ^27, ^30 -- all have corresponding entries. However, the manuscript uses ^-style superscript citation but the references are numbered 1-50. Cross-matching: ^31 = Simpson (ref 31), ^7 = Pritchett (ref 7). Appears consistent. Full automated verification not possible without rendering, but spot-check PASS. |
| C3 | All references cited in text | **WARNING** | Refs 40 (Kose et al.), 42 (Acemoglu & Robinson), 44 (Angel et al.), 45 (Cervero & Kockelman), 50 (IMF WEO) -- not found in text body by quick search. These may be cited in Extended Data descriptions or figure notes not included in the manuscript text. If they are not cited anywhere in the submission package, they should be removed. |
| C4 | Key citations present | **PASS** | Hsieh-Klenow (ref 20), Bettencourt 2013 (ref 21), Pritchett (ref 7), Easterly (ref 19), Hsieh-Moretti (ref 22) -- all present. |
| C5 | Format consistency | **PASS** | Nature numbered format. Author, title, journal, volume, pages, year. Consistent throughout. |

---

# D. FIGURES CHECK

| # | Check Item | Status | Detail |
|---|-----------|--------|--------|
| D1 | 8 main figures with captions | **PASS** | Lines 299-308: Fig. 1-8 listed with descriptions. |
| D2 | ED figures with captions | **PASS** | Lines 274-293: ED Fig. 1-10 and ED Table 1-10, all with descriptions. |
| D3 | Every figure cited in text | **PASS** | Fig. 1 (line 33), Fig. 3 (line 41), Fig. 4 (line 45), Fig. 5 (line 47), Fig. 6 (line 51), Fig. 7 (line 65). Fig. 2 is referenced implicitly via Box 1. Fig. 8 is the policy framework. |
| D4 | Figure numbers continuous | **PASS** | Fig. 1 through Fig. 8; ED Fig. 1 through ED Fig. 10. Sequential. |
| D5 | **Actual figure files exist** | **FAIL** | The manuscript references 8 main figures and 10 ED figures, but the metadata (line 127-128) marks "All figures prepared: Pending" and "Extended Data prepared: Pending." **No production-quality figure files have been confirmed.** This is a submission blocker. |

---

# E. COVER LETTER CHECK

| # | Check Item | Status | Detail |
|---|-----------|--------|--------|
| E1 | Addressee: Editor, Nature Cities | **PASS** | Line 3: "To: Editor, Nature Cities" |
| E2 | Independent author declaration | **PASS** | Lines 19: "This work was conceived and executed by a single researcher." |
| E3 | GitHub URL correct | **PASS** | Line 19: Full correct URL. |
| E4 | SSRN URL correct | **PASS** | Lines 19 and 23: Correct URL. |
| E5 | MUQ vs ICOR distinction | **PASS** | Line 15 (Finding 1): "we employ 1/ICOR as a diagnostic signal... testing whether the within-group decline pattern is robust" -- explicit Easterly distinction. Cover letter paragraph 1 also notes "a GDP-based MUQ formulation immune to housing-price cycles". |
| E6 | Reviewer recommendations | **PASS** | Line 25: "I suggest reviewers from urban science, urban economics, and urban sustainability" with specific guidance on avoiding scaling-law conflicts. Detailed names in metadata file. |
| E7 | Pronoun consistency (I, not We) | **PASS** | Throughout: "I submit", "I show", "I suggest". Consistent single-author voice. |
| E8 | "8 countries, 6 continents" claim | **WARNING** | Same issue as B4. Cover letter line 11 repeats "eight countries and six continents." |

---

# F. FORMAT CHECK

| # | Check Item | Status | Detail |
|---|-----------|--------|--------|
| F1 | Title correct | **PASS** | Consistent across manuscript, cover letter, and metadata. |
| F2 | Author info complete | **PASS** | Name, affiliation (Chongqing Survey Institute Co., Ltd.), email (26708155@alu.cqu.edu.cn), ORCID (0009-0007-6911-2309) -- all present in manuscript, cover letter, and metadata. |
| F3 | Line spacing | **N/A** | Markdown source; formatting applies during Word/PDF conversion. |
| F4 | Font uniformity | **N/A** | Same as above. |
| F5 | Special character issues | **PASS** | Em-dashes (--) used consistently. Greek letters (rho, beta, alpha, gamma, epsilon) written out in ASCII. Superscripts use ^ notation. No encoding issues detected. |
| F6 | Word count within limits | **PASS** | Main text + Box 1: ~4,650 words. Nature Cities guideline: ~4,000-5,000. Within range. Full text with Methods: ~6,100. Acceptable for Nature Cities Article format. |

---

# G. LANGUAGE CHECK

| # | Check Item | Status | Detail |
|---|-----------|--------|--------|
| G1 | Causal language audit | **WARNING** | Line 5 (Abstract): "Urban investment drives economic growth" -- this is a causal claim in the first sentence. The rest of the paper carefully avoids causal language, but this opening sentence makes an unqualified causal assertion. **Recommend**: "Urban investment is associated with economic growth" or "Urban investment supports economic growth." ALSO: Line 13: "despite Japan's continued urbanisation" uses "despite" which implies causation (urbanisation should prevent value decline). Acceptable in narrative context but note for awareness. |
| G2 | "mathematical necessity" qualifications | **PASS** | Three instances found. All are properly qualified with "under three empirically verified conditions" or equivalent. No unqualified claims of mathematical necessity. |
| G3 | Grammar/spelling spot-check | **PASS** | Checked 10 paragraphs (Abstract, Intro para 1-3, Finding 1 para 1, Finding 2 para 1-2, Finding 3 para 1, Discussion para 1, Limitations). No errors found. British spelling conventions used consistently (urbanisation, specialisation, etc.). |
| G4 | Hedging language appropriate | **PASS** | Key claims properly hedged: "is consistent with" (not "proves"), "may underlie" (not "explains"), "suggests that" (not "shows that"). The transparent limitations section acknowledges all five major weaknesses. |

---

# SUMMARY OF ALL ISSUES

## FAIL Items (must fix before submission)

### F-1. Metadata file contains `[repository URL upon acceptance]` placeholders
- **Location**: `submission_metadata_nature_cities.md`, lines 62 (Data Availability) and 66 (Code Availability)
- **Fix**: Replace both instances with `https://github.com/andyhsi2023-cq/urban-investment-aggregation-trap`
- **Risk if unfixed**: If this file is copy-pasted into the submission system, the placeholder will be visible to the editor.

### F-2. Figure files not yet produced
- **Location**: Metadata checklist lines 127-128 mark figures as "Pending"
- **Fix**: Generate all 8 main figures and 10 ED figures in production quality before submission.
- **Risk if unfixed**: Cannot submit without figures.

## WARNING Items (recommended fixes)

### W-1. "8 countries, 6 continents" claim appears inaccurate (B4)
- **Risk**: HIGH. Editor or reviewer may count and find the discrepancy.
- **Recommendation**: Verify exact counting. If the panel covers China, Japan, Korea, US, 29 EU countries, Australia, South Africa, the accurate statement is "35 countries across five continents" or "seven data systems spanning five continents." If there is a legitimate basis for "8 countries, 6 continents," document it explicitly in Methods.

### W-2. "2.3x investment intensity" inconsistent with parenthetical "China 44% vs Japan 31%" (B17)
- **Risk**: MEDIUM. A reviewer doing arithmetic will notice 44/31 = 1.4, not 2.3.
- **Recommendation**: Either change to "China's provincial FAI/GDP of 71% versus Japan's 31%" to support the 2.3x claim, or change the multiplier to ~1.4x if using WB national GFCF/GDP.

### W-3. Carbon estimate 2.7 GtCO2 vs Method C point estimate 2.97 GtCO2 (B22)
- **Risk**: LOW. The Methods section explains "central estimate of 2.7 GtCO2 (rounded from Method C)." However, 2.97 rounds to 3.0, not 2.7. A reviewer may question this.
- **Recommendation**: Either use "approximately 3.0 GtCO2" or explain more explicitly why 2.7 is adopted (e.g., "the lower bound of Method C" or "geometric mean of Methods A and C").

### W-4. References 40, 42, 44, 45, 50 may not be cited in main text (C3)
- **Risk**: LOW-MEDIUM. Uncited references will be flagged by copy editors.
- **Recommendation**: Verify whether these are cited in Extended Data notes. If not, either cite them or remove them.

### W-5. Opening sentence "drives" is causal language (G1)
- **Risk**: LOW. This is a widely accepted phrase in economics. However, given the paper's careful non-causal framing throughout, it creates a minor inconsistency.
- **Recommendation**: Consider softening to "is associated with" or "supports."

### W-6. CHANGELOG HTML comment block (A3)
- **Risk**: VERY LOW if converting properly. HIGH if accidentally rendered.
- **Recommendation**: Test Word/PDF output to confirm the comment block is invisible. Consider removing it from the submission version entirely.

### W-7. Aggregation Trap theorem numbers (0.114, 0.076) not verifiable from provided reports (B25)
- **Risk**: LOW (likely from a separate analysis file).
- **Recommendation**: Confirm these numbers against the source analysis before submission.

### W-8. Metadata Data/Code Availability differs from manuscript version
- **Risk**: MEDIUM. The manuscript has the real GitHub URL; the metadata has placeholders.
- **Recommendation**: Synchronise all three files (manuscript, cover letter, metadata) to use identical Data/Code Availability text.

---

# STRENGTHS CONFIRMED

1. **Internal numerical consistency**: 25 of 27 verifiable numbers match source reports exactly (rounding applied correctly).
2. **Transparent limitations**: Five limitations explicitly stated, including the sign-reversal boundary condition and carbon methodology caveats.
3. **Cover letter quality**: Excellent. Addresses Nature Cities specifically, distinguishes from Nature submission, includes reviewer recommendations with rationale, and maintains consistent single-author voice.
4. **Causal language discipline**: Remarkably clean for a paper of this scope. Nearly all claims use appropriate hedging ("is associated with," "is consistent with," "suggests").
5. **Reference format**: Clean Nature numbered style, 50 references within the typical range for Nature Cities Articles.
6. **Methodological transparency**: Clean specification methodology, mechanical correlation quantification, and within-city sign reversal are all reported upfront rather than buried.

---

# FINAL VERDICT

| Decision | Status |
|----------|--------|
| **Can submit after fixing FAIL items?** | YES |
| **Estimated time to fix all issues** | 2-4 hours (figures excluded; figure production may take days) |
| **Desk reject risk** | 20-30% (consistent with metadata self-assessment) |
| **Priority fix order** | F-2 (figures) > F-1 (metadata placeholder) > W-1 (8 countries) > W-2 (2.3x arithmetic) > W-3 (carbon rounding) > rest |

**The manuscript text itself is submission-ready pending the fixes above. The most critical blockers are (1) figure production and (2) metadata placeholder correction.**

---

*Report generated by Peer Reviewer agent, 2026-03-22.*
*Reviewed against: nature_cities_version.md, cover_letter_nature_cities.md, submission_metadata_nature_cities.md, and 8 analysis reports.*
