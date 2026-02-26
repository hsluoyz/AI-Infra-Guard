"""
攻击报告：根据编排器运行结果生成可读的 Markdown 报告。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime


def _escape_md(s: str) -> str:
    if not s:
        return ""
    return s.replace("|", "\\|").replace("\n", " ")[:200]


def _format_crescendo(result: dict) -> str:
    lines = [
        "# 红队攻击报告 (Crescendo)",
        "",
        f"- **攻击目标**: {result.get('attack_target', '')}",
        f"- **是否达成**: {'是' if result.get('success') else '否'}",
        f"- **最高得分**: {result.get('best_score', 0)}",
        f"- **总轮数**: {result.get('total_rounds', 0)}",
        "",
        "## 各轮详情",
        "",
        "| 轮次 | 阶段 | 得分 | 成功 | 攻击技术 | 攻击消息摘要 |",
        "|------|------|------|------|----------|--------------|",
    ]
    for r in result.get("rounds", []):
        turn = r.get("turn", {})
        eval_ = r.get("eval", {})
        lines.append(
            "| {} | {} | {} | {} | {} | {} |".format(
                r.get("round", ""),
                r.get("phase", ""),
                r.get("score", ""),
                "是" if eval_.get("is_successful") else "否",
                _escape_md(turn.get("attack_technique", "")),
                _escape_md(turn.get("attack_message", "")),
            )
        )
    lines.append("")
    return "\n".join(lines)


def _format_tap(result: dict) -> str:
    lines = [
        "# 红队攻击报告 (TAP)",
        "",
        f"- **攻击目标**: {result.get('attack_target', '')}",
        f"- **最高得分**: {result.get('best_score', 0)}",
        f"- **成功节点数**: {len(result.get('success_nodes', []))}",
        f"- **叶节点数**: {len(result.get('leaves', []))}",
        "",
        "## 成功节点",
        "",
    ]
    for n in result.get("success_nodes", []):
        t = n.turn
        lines.append(f"- **{n.node_id}** (depth={n.depth}, score={n.score})")
        lines.append(f"  - 攻击: {_escape_md(t.attack_message)}")
        lines.append(f"  - 技术: {t.attack_technique or '-'}")
        lines.append("")
    lines.append("## 叶节点得分摘要")
    lines.append("")
    for n in result.get("leaves", []):
        lines.append(f"- {n.node_id}: score={n.score}, on_topic={n.on_topic}, success={n.is_successful}")
    lines.append("")
    return "\n".join(lines)


def generate_report(
    result: dict,
    strategy: Optional[str] = None,
    title: Optional[str] = None,
) -> str:
    """
    根据 run_crescendo / run_tap 的返回结果生成 Markdown 报告。

    Args:
        result: 编排器返回的字典（需包含 strategy / rounds 或 root 等）
        strategy: 若 result 中无 strategy 键，可显式传入 "crescendo" 或 "tap"
        title: 报告主标题，可选

    Returns:
        Markdown 字符串
    """
    strategy = strategy or result.get("strategy", "")
    parts = []
    if title:
        parts.append(f"# {title}")
        parts.append("")
    parts.append(f"生成时间: {datetime.now().isoformat()}")
    parts.append("")
    if strategy == "crescendo":
        parts.append(_format_crescendo(result))
    elif strategy == "tap":
        parts.append(_format_tap(result))
    else:
        parts.append("未知策略，原始结果键: " + ", ".join(result.keys()))
    return "\n".join(parts)
