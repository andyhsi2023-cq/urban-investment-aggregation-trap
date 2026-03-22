# SSRN 预印本提交操作指南

## 准备工作

### 1. 转换 PDF
将 Nature Cities 版论文转为 PDF：
```bash
# 方法 A: 使用 pandoc (如已安装)
cd /Users/andy/Desktop/Claude/urban-q-phase-transition
pandoc 05-manuscript/drafts/nature_cities_version.md -o 05-manuscript/submission/preprint.pdf

# 方法 B: 使用在线工具
# 访问 https://www.markdowntopdf.com/ 上传 nature_cities_version.md
```

### 2. PDF 文件位置
`05-manuscript/submission/preprint.pdf`

---

## SSRN 提交步骤 (已登录 https://hq.ssrn.com/submission.cfm)

### Step 1: Upload Submission
- **Upload PDF**: 点击 "browse" 上传 preprint.pdf
- **Are you the author**: 选 "I am the Author" (已默认选中)
- **Content Format**: 选 "Paper"
- **Content Type**: 选 "Preprint"
- 点击 "Next Step"

### Step 2: Confirm Key Submission Details
SSRN 会从 PDF 自动提取标题和摘要，请核实：

**Title**:
Urban investment efficiency declines across six continents: evidence from 1,567 cities and regions

**Abstract** (Nature Cities 版 ~220 词):
从 nature_cities_version.md 的 Abstract 部分复制

**Keywords** (用逗号分隔):
urban investment efficiency, Simpson's paradox, aggregation trap, marginal Urban Q, city-level comparative analysis, scaling laws, urban sustainability, crisis-recovery archetypes

### Step 3: Author Information
- **Author**: Hongyang Xi
- **Email**: 26708155@alu.cqu.edu.cn
- **Affiliation**: Chongqing Survey Institute Co., Ltd., Chongqing, China
- **ORCID**: 0009-0007-6911-2309

### Step 4: Classify Your Submission
选择学科分类：
- **Primary**: Economics > Urban Economics
- **Secondary**: Environmental Economics, Development Economics
- 或搜索 "Urban Economics" 选择

### Step 5: Research Integrity
- 确认原创性声明
- 勾选相关选项

### Step 6: Review and Submit
- 检查所有信息
- 点击 "Submit"

---

## 提交后
- SSRN 通常在 24-48 小时内审核并发布
- 发布后会获得 SSRN DOI 和论文 URL
- 将 URL 更新到论文和 Cover Letter 中的 [preprint URL] 占位符

## 仓库 URL (已创建)
https://github.com/andyhsi2023-cq/urban-investment-aggregation-trap
