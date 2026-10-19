# PM-AutoTracker · 项目进度自动化汇总工具

一个读进度表、算逾期和进度偏差、再生成 Markdown 周报加风险清单的轻量工具，零第三方依赖，开箱即用。

做它的起因很实际：人工每周汇总各模块进度、催办、写周报，大概要两小时，而且每个人口径还不一致。我把这套活拆成三层，再用脚本把输出层自动化掉。采集层收各模块交上来的结构化进度（CSV，以后能接 Excel）；逻辑层定风险判定规则，进度偏差超过 20% 或者关键路径延期就标红预警；输出层出周报模板、风险清单和看板。这个仓库把第三层实现了，顺手把第二层的规则固化了下来。

## 使用方式

```bash
# 默认读 sample_progress.csv，输出 weekly_report_output.md
python weekly_report.py

# 指定基准日，复盘历史周报
python weekly_report.py --today 2026-10-15

# 指定输入和输出文件
python weekly_report.py --input 我的进度表.csv --output 本周周报.md
```

Python 3.8 以上即可，不用装任何第三方库。

## 进度表字段（CSV 表头）

| 字段 | 含义 | 示例 |
|---|---|---|
| `module` | 模块名 | 用户中心重构 |
| `owner` | 负责人 | 张三 |
| `plan_date` | 计划开始日期 | 2026-10-10 |
| `expected_date` | 预计完成日期 | 2026-10-14 |
| `progress_pct` | 当前进度(%) | 70 |
| `status` | 状态 | 进行中 / 已完成 / 未开始 |
| `critical` | 是否关键路径(是/否) | 是 |
| `note` | 备注 | 接口联调延期 |

## 风险判定逻辑

逾期看预计完成日期是不是已经过了今天而且进度没到 100%。进度落后按时间推算出应完成进度，实际落后超过 20% 这个阈值就预警。关键路径上的模块只要没做到 100% 且存在偏差，优先预警。

脚本只负责把异常项列出来，真假的判断留给人——这正是人机协同的关键，比如区分真风险和口径差异。

## 仓库结构

```
pm-autotracker/
├── README.md                     # 本说明
├── weekly_report.py              # 核心脚本（零依赖）
├── sample_progress.csv           # 脱敏样例数据
├── weekly_report_output.md       # 脚本生成的样例周报
└── 需求拆解三层框架.md            # AI 辅助拆解方法论
```

## 注意

仓库里都是脱敏后的样例数据，真实公司项目信息别往里放。想接真实 Excel，把 csv 换成 pandas.read_excel 就行（需要 pip install pandas openpyxl）。
