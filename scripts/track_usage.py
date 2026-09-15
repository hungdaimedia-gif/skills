#!/usr/bin/env python3
"""
SKILL USAGE TRACKER — Theo dõi và thống kê lịch sử sử dụng skills trong dự án.

Cách dùng:
  python3 scripts/track_usage.py log <skill-name> [--agent <tên-agent>] [--goal "mô tả việc"]
  python3 scripts/track_usage.py stats
  python3 scripts/track_usage.py list [--limit 20]
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from collections import Counter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(REPO_ROOT, "logs")
USAGE_LOG_FILE = os.path.join(LOGS_DIR, "usage_history.jsonl")


def log_usage(skill_name, agent="antigravity", goal="", status="success"):
    """Ghi nhận 1 sự kiện sử dụng skill."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "skill": skill_name,
        "agent": agent,
        "goal": goal,
        "status": status,
    }
    with open(USAGE_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(f"📝 Đã ghi nhận sử dụng skill: '{skill_name}' (Agent: {agent})")


def show_stats():
    """Thống kê tần suất sử dụng các skill."""
    if not os.path.exists(USAGE_LOG_FILE):
        print("📭 Chưa có dữ liệu lịch sử sử dụng skills.")
        return

    counts = Counter()
    agent_counts = Counter()
    last_used = {}

    with open(USAGE_LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                    sk = data.get("skill", "unknown")
                    ag = data.get("agent", "unknown")
                    ts = data.get("timestamp", "")
                    counts[sk] += 1
                    agent_counts[ag] += 1
                    last_used[sk] = ts
                except Exception:
                    pass

    if not counts:
        print("📭 Chưa có dữ liệu lịch sử sử dụng skills.")
        return

    print(f"\n{'='*65}")
    print("📊 BÁO CÁO THỐNG KÊ SỬ DỤNG SKILLS (USAGE TELEMETRY)")
    print(f"{'='*65}")
    print(f"Tổng số lượt gọi: {sum(counts.values())} lượt | Tổng số skills đã kích hoạt: {len(counts)}")
    print(f"\n🤖 Phân bổ theo AI Agent:")
    for ag, c in agent_counts.most_common():
        print(f"   • {ag:<15}: {c} lượt")

    print(f"\n🔥 Top Skills Được Dùng Nhiều Nhất:")
    print(f"{'Skill Name':<35} | {'Lượt dùng':<10} | {'Dùng gần nhất':<20}")
    print(f"{'-'*35}-+-{'-'*10}-+-{'-'*20}")
    for sk, c in counts.most_common(15):
        lu = last_used.get(sk, "")[:19].replace("T", " ")
        print(f"{sk:<35} | {c:<10} | {lu:<20}")
    print(f"{'='*65}\n")


def show_list(limit=20):
    """Hiển thị nhật ký gọi skill gần nhất."""
    if not os.path.exists(USAGE_LOG_FILE):
        print("📭 Chưa có nhật ký sử dụng nào.")
        return

    events = []
    with open(USAGE_LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except Exception:
                    pass

    if not events:
        print("📭 Chưa có nhật ký sử dụng nào.")
        return

    events.reverse()
    events = events[:limit]

    print(f"\n{'='*75}")
    print(f"📋 NHẬT KÝ SỬ DỤNG SKILLS ({len(events)} lượt gần nhất)")
    print(f"{'='*75}")
    print(f"{'Thời gian':<20} | {'Skill':<30} | {'Agent':<12} | {'Trạng thái':<8}")
    print(f"{'-'*20}-+-{'-'*30}-+-{'-'*12}-+-{'-'*8}")
    for ev in events:
        ts = ev.get("timestamp", "")[:19].replace("T", " ")
        sk = ev.get("skill", "")[:30]
        ag = ev.get("agent", "")[:12]
        st = ev.get("status", "ok")[:8]
        print(f"{ts:<20} | {sk:<30} | {ag:<12} | {st:<8}")
        goal = ev.get("goal", "")
        if goal:
            print(f"   └─ 🎯 Mục tiêu: {goal}")
    print(f"{'='*75}\n")


def main():
    parser = argparse.ArgumentParser(description="Skill Usage Tracker")
    subparsers = parser.add_subparsers(dest="command")

    # log
    log_parser = subparsers.add_parser("log", help="Ghi nhận 1 lần kích hoạt skill")
    log_parser.add_argument("skill", help="Tên skill được sử dụng")
    log_parser.add_argument("--agent", default="antigravity", help="Tên AI Agent kích hoạt (mặc định: antigravity)")
    log_parser.add_argument("--goal", default="", help="Mô tả mục đích sử dụng")
    log_parser.add_argument("--status", default="success", choices=["success", "failed"], help="Trạng thái thực thi")

    # stats
    subparsers.add_parser("stats", help="Xem báo cáo thống kê sử dụng")

    # list
    list_parser = subparsers.add_parser("list", help="Xem danh sách các lần gọi gần nhất")
    list_parser.add_argument("--limit", type=int, default=20, help="Số dòng hiển thị (mặc định: 20)")

    args = parser.parse_args()

    if args.command == "log":
        log_usage(args.skill, agent=args.agent, goal=args.goal, status=args.status)
    elif args.command == "stats":
        show_stats()
    elif args.command == "list":
        show_list(limit=args.limit)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
