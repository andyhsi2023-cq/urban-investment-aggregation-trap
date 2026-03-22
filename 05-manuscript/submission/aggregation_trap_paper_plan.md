# Aggregation Trap Paper: Independent Publication Plan

**Date**: 2026-03-22
**Status**: Planning stage

---

## 1. Candidate Titles

1. **The Aggregation Trap: When Simpson's Paradox Becomes a Mathematical Necessity**
2. **Necessary Paradoxes: A Theorem on When Pooled Statistics Must Conceal Within-Group Decline**
3. **When Averages Lie by Construction: The Aggregation Trap in Stratified Measurement Systems**

Recommended: Title 1. It is direct, names the concept, and connects to the well-known Simpson's Paradox -- maximising discoverability while signalling theoretical novelty.

---

## 2. Positioning

This is a paper at the intersection of **statistical methodology**, **measurement theory**, and **complex systems**. It is not a paper about cities, medicine, or education per se -- it is about a structural failure mode in pooled statistics that affects all these domains. The urban investment application serves as the primary empirical validation, but the theorem's value lies in its generality.

The paper belongs to the tradition of methodological contributions that formalise well-known empirical phenomena: Simpson (1951) identified the paradox; Bickel, Hammel & O'Connell (1975) provided the Berkeley admissions case study; Pearl (2014) offered a causal-inference interpretation. This paper answers the question none of them posed: **under what conditions is Simpson's Paradox not merely possible but mathematically guaranteed?**

---

## 3. Core Contribution

**The Aggregation Trap Theorem.** Under three conditions -- (A1) within-group decline, (A2) systematic compositional shift (endogenous graduation), and (A3) compositional dominance -- Simpson's Paradox is a mathematical necessity, not a statistical curiosity. The aggregate trend must be non-negative even though every within-group trend is non-positive.

Key theoretical advances over existing literature:
- **Sufficiency conditions for necessity**: Prior work shows Simpson's Paradox *can* occur; we show when it *must* occur
- **Two-group closed form**: With two groups sharing decline rate gamma and baseline gap Delta-alpha, the paradox arises iff Delta-alpha >= gamma -- a single interpretable inequality
- **Boundary condition**: The theorem predicts where the paradox should *not* appear (within single countries), confirmed empirically in 7/7 cases
- **Constructive implications**: The theorem identifies which measurement systems are structurally vulnerable and suggests design principles to avoid the trap

---

## 4. Structure Outline

### Introduction (~800 words)
- **Hook**: "Simpson's Paradox has been known for 75 years. Yet a basic question remains unanswered: when must it occur?"
- Historical arc: Simpson (1951) -> Berkeley admissions (1975) -> Pearl's causal interpretation (2014) -> ecological fallacy (Robinson 1950)
- The gap: existing literature treats the paradox as a possibility to be checked post hoc, never as a predictable structural feature of measurement systems
- Contribution statement: We prove three sufficient conditions under which the paradox is guaranteed and demonstrate cross-domain applicability

### The Theorem (~1,200 words)
- **Setup**: K groups with linear efficiency functions E_k(u), weight functions w_k(u)
- **Statement**: Full theorem with three conditions (A1, A2, A3)
- **Proof**: Formal derivation (concise)
- **Two-group simplification**: Closed-form condition Delta-alpha >= gamma, with geometric interpretation ("the escalator outpaces the treadmill")
- **Corollaries**: (i) The paradox is stronger when the between-group gap is larger relative to within-group decline; (ii) The paradox disappears when compositional shift is absent or when within-group heterogeneity is small
- **Extensions**: Nonlinear E_k(u), continuous group transitions, stochastic formulation

### Empirical Validation: Urban Investment (~1,000 words)
- Brief description of MUQ framework (referencing the Nature Cities paper for full details)
- Cross-national verification: A1, A2, A3 all satisfied across 157 countries
- Boundary condition test: 0/7 countries satisfy all three conditions at the subnational level
- Monte Carlo: simulated data with and without the three conditions to confirm the theorem's predictions
- This section establishes that the theorem is not merely abstract but empirically operative at global scale

### Cross-Domain Applications (~1,200 words)
Four worked examples demonstrating the theorem's applicability:

**Medicine.** Treatment effectiveness declining within age strata but appearing stable in pooled clinical trials -- when patients systematically shift between risk groups (e.g., improved diagnosis moves patients from "undetected" to "detected" categories). The theorem predicts when aggregate treatment statistics must mask within-stratum deterioration.

**Education.** School quality declining within school types (public, charter, private) but pooled test scores rising as students migrate toward higher-performing types. The theorem identifies conditions under which league tables structurally conceal quality erosion.

**Finance / Credit rating.** Portfolio quality declining within rating categories but appearing stable in aggregate because firms systematically upgrade through categories. This connects to the credit-rating inflation literature and explains why aggregate default rates can appear stable even as within-category risk rises.

**Infrastructure gap estimation.** The World Bank's infrastructure-gap methodology assumes constant marginal returns to investment -- precisely the aggregation trap. The theorem provides a formal proof that this assumption must produce overestimates when countries graduate between income groups.

Each example: (i) maps the three conditions to the specific domain; (ii) identifies the measurement system at risk; (iii) proposes a diagnostic test.

### Discussion (~800 words)
- **Measurement system design**: The theorem implies that any system measuring heterogeneous units on pooled metrics, where units can graduate between strata, is vulnerable. Design principles: always report within-stratum trends; test A1-A3 before pooling; use the two-group inequality as a screening diagnostic.
- **Relationship to causal inference**: Pearl's (2014) causal interpretation of Simpson's Paradox focuses on when to condition on a covariate. Our theorem addresses a different question: when must the paradox arise regardless of the analyst's conditioning choices? The two perspectives are complementary.
- **Relationship to ecological fallacy**: Robinson (1950) showed that group-level correlations need not reflect individual-level relationships. The aggregation trap is a specific, provable instance where they must diverge.
- **Limitations**: The theorem assumes linear within-group trends and parametric weight functions. Extensions to nonlinear and nonparametric settings are sketched but not fully proved.
- **Closing**: "Measurement systems that pool across developmental stages are not merely at risk of missing within-group decline -- they are mathematically guaranteed to miss it."

---

## 5. Relationship to Nature Cities Paper

The two papers are designed to be **mutually reinforcing but independently readable**:

| Dimension | Nature Cities paper | Aggregation Trap paper |
|-----------|-------------------|----------------------|
| Focus | Urban investment efficiency globally | Statistical methodology + cross-domain theory |
| Theorem role | Tool (Box 1, ~470 words) | Central contribution (~1,200 words) |
| Empirical content | Full MUQ analysis (8 countries, 1,567 regions) | Brief validation (referencing NC paper for details) |
| Cross-domain examples | One paragraph in Discussion | Four worked examples (~1,200 words) |
| Proof | Concise statement | Full formal proof + extensions |

**Citation strategy**: The Nature Cities paper cites the AT paper as "the formal treatment of the theorem and its cross-domain generality is developed in [ref]." The AT paper cites the Nature Cities paper as "the first large-scale empirical validation of the theorem is reported in [ref]." Neither paper is a prerequisite for understanding the other.

---

## 6. Estimated Word Count and Work

| Section | Words |
|---------|:-----:|
| Abstract | ~200 |
| Introduction | ~800 |
| Theorem + proof | ~1,200 |
| Empirical validation | ~1,000 |
| Cross-domain applications | ~1,200 |
| Discussion | ~800 |
| **Total main text** | **~5,200** |
| Methods/Appendix | ~500 |
| **Total** | **~5,700** |

### Estimated workload

| Task | Time |
|------|:----:|
| Formal proof polishing + extensions (nonlinear, stochastic) | 2 weeks |
| Cross-domain literature review (medicine, education, finance, infrastructure) | 1 week |
| Four worked examples with real or simulated data | 2 weeks |
| Monte Carlo validation suite | 1 week |
| Writing first draft | 2 weeks |
| Revision and polishing | 1 week |
| **Total** | **~9 weeks** |

---

## 7. Target Journal Assessment and Recommendation

### Detailed evaluation

| Journal | Fit | Strengths | Weaknesses | Probability |
|---------|:---:|-----------|------------|:-----------:|
| **PNAS** | A | Cross-disciplinary; accepts short articles; high impact (IF ~12); "Brief Report" format (~3,500 words) fits a tight version | Extremely competitive; may want more mathematical depth for a theorem paper | 15-25% |
| **Science Advances** | A- | Broadly cross-disciplinary; accepts longer articles (~6,000 words); good for methods papers with empirical validation; open access | Perceived as second-tier to Science; less prestige for a theorem | 25-35% |
| **Nature Human Behaviour** | B+ | Social science methodology; high impact (IF ~25); visibility | "Behaviour" framing may not fit a measurement/statistics paper; editors may see it as too mathematical | 10-20% |
| **PNAS Nexus** | B+ | Cross-disciplinary; open access; growing reputation; lower bar than PNAS; accepts methodology papers | Young journal; less prestige; unclear long-term positioning | 35-45% |
| **Proc. Royal Society A** | B | Strong tradition of mathematical methodology; appropriate for theorem papers; respected | Lower impact (IF ~3.5); narrower readership; may not reach social scientists | 30-40% |
| **JASA** | B- | Top statistics journal; theorem papers welcome; highly prestigious within statistics | Requires deeper mathematical contribution (extensions, optimality results); narrow audience; long review times | 15-25% |
| **Statistical Science** | B- | Review/methodology journal; excellent for "big idea" papers; readable style | Very narrow audience; low publication frequency; IF ~3.7 | 20-30% |

### Recommendation

**Primary target: PNAS (Brief Report)**

Rationale:
1. The theorem's cross-domain applicability (medicine, education, finance, urban science) maps perfectly to PNAS's multi-disciplinary mandate
2. The "Brief Report" format (~3,500 words) forces the paper into its most powerful form -- tight theorem + one primary empirical validation + brief cross-domain sketches
3. PNAS has a strong tradition of publishing foundational results in applied statistics/social methodology (e.g., Ioannidis 2005 on false findings; Simmons et al. 2011 on false positives)
4. The urban investment validation, already published (or under review) in Nature Cities, provides strong credibility for the empirical grounding
5. A PNAS companion to a Nature Cities paper creates a high-visibility pair

**Backup target: Science Advances**

Rationale:
1. Allows the full ~5,200-word version with all four cross-domain examples
2. Open access maximises reach across domains
3. More receptive to papers that combine formal theory with empirical demonstration
4. Shorter review times than PNAS

**Alternative path: JASA (if mathematical extensions are developed)**

If the proof is extended to nonlinear, nonparametric, and stochastic settings with optimality results (i.e., the conditions are not only sufficient but necessary under regularity assumptions), the paper would merit JASA. This requires an additional 4-6 weeks of mathematical work. The trade-off is narrower audience but higher prestige within statistics.

### Strategic sequencing

1. Submit Nature Cities paper first (target: 2026-05-10)
2. Begin AT paper immediately after NC submission
3. AT paper first draft complete by 2026-07-15
4. Submit AT paper to PNAS by 2026-08-01
5. If PNAS desk rejects, reformat for Science Advances within one week

---

## 8. Open Questions for PI

1. **Depth of mathematical extensions**: Should we pursue the nonlinear/stochastic extensions (needed for JASA, optional for PNAS)? This adds 4-6 weeks but strengthens the contribution.
2. **Cross-domain examples**: Should all four examples use real data, or are two real + two simulated acceptable? Real data for medicine and education requires literature review and potentially data acquisition.
3. **Timing**: Should the AT paper wait until Nature Cities is accepted (to cite it as published), or proceed in parallel (citing it as "under review" or as a preprint)?
4. **Co-authorship**: If a statistician or mathematician is brought in for the proof extensions, this would strengthen credibility at JASA but delay the timeline.

---

*Document prepared 2026-03-22. To be updated as Nature Cities submission progresses.*
