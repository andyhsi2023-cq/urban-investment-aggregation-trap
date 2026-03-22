#!/usr/bin/env python3
"""
master_pipeline.py — Urban Q Phase Transition 主分析管线
========================================================

按依赖关系串联全部分析脚本，分 4 个 Stage 顺序执行。
每个步骤执行前检查输入文件，捕获错误但不中断后续流程，
记录运行时间，最终输出汇总报告。

用法:
    python master_pipeline.py              # 运行全部 Stage
    python master_pipeline.py --stage 0    # 仅运行 Stage 0
    python master_pipeline.py --stage 1 2  # 运行 Stage 1 和 2
    python master_pipeline.py --dry-run    # 仅检查输入文件，不执行

输出:
    03-analysis/models/pipeline_report.txt — 运行汇总报告
"""

import os
import sys
import subprocess
import time
import argparse
from datetime import datetime
from pathlib import Path

# ──────────────────────────────────────────────
# 项目根目录（本脚本所在目录）
# ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = PROJECT_ROOT / "03-analysis" / "scripts"
DATA_RAW = PROJECT_ROOT / "02-data" / "raw"
DATA_PROC = PROJECT_ROOT / "02-data" / "processed"
MODELS_DIR = PROJECT_ROOT / "03-analysis" / "models"
FIGURES_DIR = PROJECT_ROOT / "04-figures" / "drafts"
REPORT_PATH = MODELS_DIR / "pipeline_report.txt"

# six-curves 项目数据（被 40b, 50b 等脚本引用）
SIX_CURVES_RAW = PROJECT_ROOT.parent / "six-curves-urban-transition" / "02-data" / "raw"


# ──────────────────────────────────────────────
# 管线定义：每个步骤 = (脚本名, 描述, [输入文件列表])
# 输入文件列表用于执行前检查；为空则跳过检查
# ──────────────────────────────────────────────

STAGE_0_DATA_ACQUISITION = [
    (
        "20_world_bank_data.py",
        "下载 World Bank 全球面板数据 (217国, 1960-2023)",
        [],  # 无本地输入依赖（从 API 下载）
    ),
    (
        "21_penn_world_table.py",
        "下载 Penn World Table 10.01 (183国, 1950-2019)",
        [],
    ),
    (
        "22_bis_un_data.py",
        "下载 BIS 房价指数 + UN 人口数据",
        [],
    ),
    (
        "40b_china_data_from_sources.py",
        "整合中国国家级数据（从 six-curves 原始 CSV）",
        [
            SIX_CURVES_RAW / "background_gdp_NBS_1978-2024.csv",
            SIX_CURVES_RAW / "c1_urbanization_rate_NBS_1949-2024.csv",
        ],
    ),
    (
        "15_extract_country_data.py",
        "提取四国面板（中/日/美/英）合并 WB+PWT+BIS+UN",
        [
            DATA_RAW / "world_bank_all_countries.csv",
            DATA_RAW / "penn_world_table.csv",
            DATA_RAW / "bis_property_prices.csv",
            DATA_RAW / "un_population.csv",
        ],
    ),
]

STAGE_1_GLOBAL_ANALYSIS = [
    (
        "30b_global_q_revised.py",
        "全球 Urban Q 修正模型（158国面板 + BIS 房价校正）",
        [
            DATA_PROC / "global_urban_q_panel.csv",
            DATA_RAW / "bis_property_prices.csv",
        ],
    ),
    (
        "31b_kstar_m2_revised.py",
        "全球 K*/M2 修正模型（VIF + 聚类分析）",
        [
            DATA_PROC / "global_urban_q_panel.csv",
            DATA_RAW / "penn_world_table.csv",
        ],
    ),
    (
        "35_cointegration_ty.py",
        "Toda-Yamamoto 协整检验（全球面板）",
        [
            DATA_PROC / "global_q_revised_panel.csv",
        ],
    ),
]

STAGE_2_CHINA_DEEP = [
    (
        "50b_china_q_adjusted.py",
        "中国 Urban Q 调整模型（NBS 价格+竣工数据校正）",
        [
            MODELS_DIR / "china_urban_q_real_data.csv",
        ],
    ),
    (
        "52_city_ocr_uci.py",
        "中国城市级 OCR/UCI 分析（300城面板）",
        [
            DATA_PROC / "china_city_panel_real.csv",
            DATA_RAW / "penn_world_table.csv",
        ],
    ),
]

STAGE_3_ROBUSTNESS = [
    (
        "60_robustness_vt_breakpoint.py",
        "稳健性：V(t) 断点检验 + Monte Carlo 置信区间",
        [
            MODELS_DIR / "china_urban_q_real_data.csv",
        ],
    ),
    (
        "61_kstar_bounded_muq.py",
        "稳健性：K* 有界 mu_Q 模型",
        [
            DATA_PROC / "global_urban_q_panel.csv",
        ],
    ),
    (
        "62_iv_gmm_pvar.py",
        "稳健性：IV-GMM + 面板 VAR",
        [
            DATA_PROC / "global_kstar_ocr_uci.csv",
            DATA_PROC / "global_urban_q_panel.csv",
            DATA_RAW / "penn_world_table.csv",
        ],
    ),
    (
        "63_fai_validation_robust_uci.py",
        "稳健性：FAI 验证 + 稳健 UCI",
        [
            DATA_PROC / "china_city_real_fai_panel.csv",
        ],
    ),
    (
        "64_city_real_fai_only.py",
        "稳健性：城市级 FAI-only 分析",
        [
            DATA_PROC / "china_city_real_fai_panel.csv",
        ],
    ),
]

# Stage 4 为可视化汇总，依赖前面所有 Stage 的输出
STAGE_4_FIGURES = [
    (
        "70_nature_main_figures.py",
        "Nature 投稿主图（四国 Q 对比 + CI）",
        [
            MODELS_DIR / "china_urban_q_real_data.csv",
            MODELS_DIR / "monte_carlo_q_ci.csv",
        ],
    ),
]

ALL_STAGES = {
    0: ("Stage 0: 数据获取", STAGE_0_DATA_ACQUISITION),
    1: ("Stage 1: 全球分析", STAGE_1_GLOBAL_ANALYSIS),
    2: ("Stage 2: 中国深度分析", STAGE_2_CHINA_DEEP),
    3: ("Stage 3: 稳健性检验", STAGE_3_ROBUSTNESS),
    4: ("Stage 4: 可视化汇总", STAGE_4_FIGURES),
}


# ──────────────────────────────────────────────
# 执行逻辑
# ──────────────────────────────────────────────

class PipelineResult:
    """单个步骤的执行结果"""
    def __init__(self, script: str, description: str):
        self.script = script
        self.description = description
        self.status = "PENDING"      # PENDING | SKIPPED | SUCCESS | FAILED | INPUT_MISSING
        self.elapsed_sec = 0.0
        self.error_msg = ""
        self.missing_inputs = []


def check_inputs(input_files: list[Path]) -> list[str]:
    """检查输入文件是否存在，返回缺失文件列表"""
    missing = []
    for f in input_files:
        if not f.exists():
            missing.append(str(f))
    return missing


def run_script(script_name: str, description: str, input_files: list[Path],
               dry_run: bool = False) -> PipelineResult:
    """执行单个分析脚本"""
    result = PipelineResult(script_name, description)
    script_path = SCRIPTS_DIR / script_name

    # 检查脚本是否存在
    if not script_path.exists():
        result.status = "SKIPPED"
        result.error_msg = f"脚本不存在: {script_path}"
        return result

    # 检查输入文件
    missing = check_inputs(input_files)
    if missing:
        result.missing_inputs = missing
        result.status = "INPUT_MISSING"
        result.error_msg = f"缺失 {len(missing)} 个输入文件"
        return result

    if dry_run:
        result.status = "DRY_RUN_OK"
        return result

    # 执行脚本
    print(f"  >>> 执行: {script_name}")
    print(f"      说明: {description}")
    t0 = time.time()

    try:
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=600,  # 10 分钟超时
            cwd=str(PROJECT_ROOT),
        )
        result.elapsed_sec = time.time() - t0

        if proc.returncode == 0:
            result.status = "SUCCESS"
            print(f"      完成 ({result.elapsed_sec:.1f}s)")
        else:
            result.status = "FAILED"
            # 截取 stderr 最后 500 字符作为错误摘要
            stderr_tail = proc.stderr[-500:] if proc.stderr else "(no stderr)"
            result.error_msg = stderr_tail
            print(f"      失败 (exit={proc.returncode}, {result.elapsed_sec:.1f}s)")

    except subprocess.TimeoutExpired:
        result.elapsed_sec = time.time() - t0
        result.status = "FAILED"
        result.error_msg = "超时 (>600s)"
        print(f"      超时!")

    except Exception as e:
        result.elapsed_sec = time.time() - t0
        result.status = "FAILED"
        result.error_msg = str(e)
        print(f"      异常: {e}")

    return result


def run_stage(stage_id: int, steps: list, dry_run: bool = False) -> list[PipelineResult]:
    """执行一个 Stage 的所有步骤"""
    results = []
    for script_name, description, input_files in steps:
        r = run_script(script_name, description, input_files, dry_run=dry_run)
        results.append(r)
    return results


def generate_report(all_results: dict[int, list[PipelineResult]],
                    total_elapsed: float) -> str:
    """生成汇总报告"""
    lines = []
    lines.append("=" * 70)
    lines.append("Urban Q Phase Transition — Pipeline Report")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"总耗时: {total_elapsed:.1f}s")
    lines.append("=" * 70)

    # 统计
    total_steps = 0
    success = 0
    failed = 0
    skipped = 0
    input_missing = 0

    for stage_id in sorted(all_results.keys()):
        stage_name, _ = ALL_STAGES[stage_id]
        results = all_results[stage_id]
        lines.append("")
        lines.append(f"--- {stage_name} ---")
        lines.append("")

        for r in results:
            total_steps += 1
            icon = {
                "SUCCESS": "[OK]",
                "FAILED": "[FAIL]",
                "SKIPPED": "[SKIP]",
                "INPUT_MISSING": "[NO INPUT]",
                "DRY_RUN_OK": "[DRY RUN OK]",
            }.get(r.status, "[?]")

            if r.status == "SUCCESS":
                success += 1
            elif r.status == "FAILED":
                failed += 1
            elif r.status in ("SKIPPED", "DRY_RUN_OK"):
                skipped += 1
            elif r.status == "INPUT_MISSING":
                input_missing += 1

            time_str = f"{r.elapsed_sec:.1f}s" if r.elapsed_sec > 0 else "-"
            lines.append(f"  {icon:14s} {r.script:40s} {time_str:>8s}")
            lines.append(f"               {r.description}")

            if r.missing_inputs:
                for mi in r.missing_inputs:
                    lines.append(f"               ! 缺失: {mi}")
            if r.error_msg and r.status == "FAILED":
                # 错误信息截断显示
                err_short = r.error_msg.replace('\n', ' ')[:120]
                lines.append(f"               ! 错误: {err_short}")

    lines.append("")
    lines.append("=" * 70)
    lines.append("汇总")
    lines.append(f"  总步骤数:     {total_steps}")
    lines.append(f"  成功:         {success}")
    lines.append(f"  失败:         {failed}")
    lines.append(f"  输入缺失:     {input_missing}")
    lines.append(f"  跳过:         {skipped}")
    lines.append(f"  成功率:       {success}/{total_steps - skipped} "
                 f"({100 * success / max(1, total_steps - skipped):.0f}%)")
    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Urban Q Phase Transition 主分析管线"
    )
    parser.add_argument(
        "--stage", type=int, nargs="*", default=None,
        help="指定运行的 Stage 编号 (0-4)，默认运行全部"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="仅检查输入文件是否存在，不执行脚本"
    )
    args = parser.parse_args()

    # 确定要运行的 Stage
    if args.stage is not None:
        stage_ids = [s for s in args.stage if s in ALL_STAGES]
        if not stage_ids:
            print("错误: 无效的 Stage 编号。可选: 0, 1, 2, 3, 4")
            sys.exit(1)
    else:
        stage_ids = sorted(ALL_STAGES.keys())

    # 确保输出目录存在
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Urban Q Phase Transition — Master Pipeline")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if args.dry_run:
        print("模式: DRY RUN（仅检查输入文件）")
    print(f"执行 Stage: {stage_ids}")
    print("=" * 60)

    all_results = {}
    t_total_start = time.time()

    for sid in stage_ids:
        stage_name, steps = ALL_STAGES[sid]
        print(f"\n{'=' * 60}")
        print(f"{stage_name}")
        print(f"{'=' * 60}")
        results = run_stage(sid, steps, dry_run=args.dry_run)
        all_results[sid] = results

    total_elapsed = time.time() - t_total_start

    # 生成报告
    report = generate_report(all_results, total_elapsed)
    print(f"\n{report}")

    # 保存报告
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n报告已保存: {REPORT_PATH}")

    # 返回码：有失败则返回 1
    any_failed = any(
        r.status == "FAILED"
        for results in all_results.values()
        for r in results
    )
    sys.exit(1 if any_failed else 0)


if __name__ == "__main__":
    main()
