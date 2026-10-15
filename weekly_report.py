#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PM-AutoTracker: 项目进度自动汇总 + 风险预警 + 周报生成

读取进度表(CSV) -> 计算逾期 / 进度偏差 -> 输出 Markdown 周报 + 风险清单。
零第三方依赖，开箱即用。

用法:
    python weekly_report.py
    python weekly_report.py --today 2026-10-15
    python weekly_report.py --input 我的进度表.csv --output 本周周报.md
"""

import argparse
import csv
from datetime import date, datetime

RISK_DEVIATION = 20  # 进度偏差预警阈值(%)


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def parse_date(s):
    return datetime.strptime(s.strip(), "%Y-%m-%d").date()


def main():
    ap = argparse.ArgumentParser(description="项目进度自动汇总 + 风险预警")
    ap.add_argument("--input", default="sample_progress.csv", help="进度表 CSV 路径")
    ap.add_argument("--output", default="weekly_report_output.md", help="输出 Markdown 路径")
    ap.add_argument("--today", default=None, help="基准日期 YYYY-MM-DD（默认今天）")
    ap.add_argument("--deviation", type=float, default=RISK_DEVIATION, help="进度偏差阈值(%)")
    args = ap.parse_args()

    today = parse_date(args.today) if args.today else date.today()

    rows = []
    with open(args.input, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    if not rows:
        print("⚠️ 进度表为空，请检查输入文件。")
        return

    total = len(rows)
    done = 0
    risks = []

    for r in rows:
        plan = parse_date(r["plan_date"])
        exp = parse_date(r["expected_date"])
        prog = int(r["progress_pct"])
        span = max((exp - plan).days, 1)
        elapsed = (today - plan).days
        scheduled = clamp(elapsed / span * 100, 0, 100)  # 按时间应完成进度
        deviation = round(scheduled - prog, 1)
        overdue = (exp < today) and prog < 100
        critical = str(r.get("critical", "")).strip() in ("是", "Y", "y", "1", "true")
        is_risk = overdue or deviation > args.deviation or (critical and deviation > 0 and prog < 100)

        r["_scheduled"] = round(scheduled, 1)
        r["_deviation"] = deviation
        r["_overdue"] = overdue
        r["_critical"] = critical
        r["_risk"] = is_risk

        if prog >= 100 or str(r.get("status", "")).strip() == "已完成":
            done += 1

        if is_risk:
            reasons = []
            if overdue:
                reasons.append("已逾期")
            if deviation > args.deviation:
                reasons.append(f"进度落后 {deviation}%")
            if critical and prog < 100:
                reasons.append("关键路径")
            r["_reason"] = "、".join(reasons)
            risks.append(r)

    in_progress = total - done
    risk_count = len(risks)

    # ---------- 生成 Markdown ----------
    lines = []
    lines.append(f"# 项目周报（自动生成）")
    lines.append("")
    lines.append(f"> 生成基准日：{today.isoformat()} ｜ 数据来源：`{args.input}`")
    lines.append("")
    lines.append("## 一、总体概览")
    lines.append("")
    lines.append(f"- 模块总数：**{total}**")
    lines.append(f"- 已完成：{done} ｜ 进行中：{in_progress}")
    lines.append(f"- ⚠️ 风险项：**{risk_count}**")
    lines.append("")
    lines.append("## 二、风险清单（需优先跟进）")
    lines.append("")
    if risks:
        lines.append("| 模块 | 负责人 | 进度 | 应完成 | 偏差 | 关键 | 风险原因 | 备注 |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for r in sorted(risks, key=lambda x: (not x["_critical"], -x["_deviation"])):
            lines.append(
                f"| {r['module']} | {r['owner']} | {r['progress_pct']}% | "
                f"{r['_scheduled']}% | {r['_deviation']}% | "
                f"{'🔴' if r['_critical'] else '—'} | {r['_reason']} | {r.get('note','')} |"
            )
    else:
        lines.append("✅ 本周暂无风险项。")
    lines.append("")
    lines.append("## 三、各模块进度")
    lines.append("")
    lines.append("| 模块 | 负责人 | 进度 | 状态 | 计划日 | 预计完成 | 关键 |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in rows:
        flag = "🔴" if r["_risk"] else ("🟢" if int(r["progress_pct"]) >= 100 else "🟡")
        lines.append(
            f"| {flag} {r['module']} | {r['owner']} | {r['progress_pct']}% | "
            f"{r['status']} | {r['plan_date']} | {r['expected_date']} | "
            f"{'是' if r['_critical'] else '否'} |"
        )
    lines.append("")
    lines.append("## 四、下周计划（待填写）")
    lines.append("")
    lines.append("- [ ] ")
    lines.append("- [ ] ")
    lines.append("")
    lines.append("---")
    lines.append("*本文档由 PM-AutoTracker 自动生成，风险项请人工复核后进入正式周报。*")
    lines.append("")

    md = "\n".join(lines)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(md)

    # 控制台摘要
    print(f"✅ 已生成周报：{args.output}")
    print(f"   模块 {total} 个 ｜ 完成 {done} ｜ 风险 {risk_count} 个")
    for r in risks:
        print(f"   ⚠️ {r['module']}（{r['owner']}）：{r['_reason']}")


if __name__ == "__main__":
    main()
