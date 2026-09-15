#!/usr/bin/env python3
"""
SKILL INGESTION & CONFLICT ARBITRATION TOOL
Tự động thẩm định, kiểm tra xung đột và nạp skill mới từ GitHub vào hệ thống DSG.
"""

import os
import sys
import shutil
import re
import argparse
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")

BRANCHES = [
    "💡 Ý tưởng & Đặc tả",
    "🏗️ Kiến trúc & Thiết kế",
    "⚡ Viết Code & TDD",
    "🛡️ Kiểm soát & Review",
    "🩺 Cứu hộ & Gỡ lỗi",
    "🚀 Nền tảng & Vận hành"
]

def analyze_branch_heuristic(name, content):
    text = (name + " " + content).lower()
    if any(k in text for k in ["spec", "ticket", "grill", "idea", "question", "domain", "plan"]):
        return "💡 Ý tưởng & Đặc tả"
    if any(k in text for k in ["architecture", "design", "module", "canvas", "flow", "boilerplate", "prototype"]):
        return "🏗️ Kiến trúc & Thiết kế"
    if any(k in text for k in ["tdd", "test", "implement", "coding", "task", "runner", "write"]):
        return "⚡ Viết Code & TDD"
    if any(k in text for k in ["review", "budget", "line", "guard", "conflict", "merge", "commit", "handoff"]):
        return "🛡️ Kiểm soát & Review"
    if any(k in text for k in ["bug", "debug", "diagnos", "recovery", "disorientation", "error", "log"]):
        return "🩺 Cứu hộ & Gỡ lỗi"
    if any(k in text for k in ["setup", "install", "m1", "platform", "store", "wizard", "deploy"]):
        return "🚀 Nền tảng & Vận hành"
    return "⚡ Viết Code & TDD"

def check_existing_collision(skill_name):
    for root, dirs, files in os.walk(SKILLS_DIR):
        if os.path.basename(root) == skill_name and "SKILL.md" in files:
            return root
    return None

def ingest_skill(source_path, target_branch=None, force=False):
    print("=" * 60)
    print("🛡️  DSG SKILL INGESTION & CONFLICT ARBITRATION")
    print("=" * 60)

    if not os.path.exists(source_path):
        print(f"❌ Lỗi: Không tìm thấy đường dẫn nguồn: {source_path}")
        sys.exit(1)

    skill_name = os.path.basename(source_path.rstrip("/\\"))
    skill_md_path = os.path.join(source_path, "SKILL.md") if os.path.isdir(source_path) else source_path

    if not os.path.exists(skill_md_path):
        print(f"❌ Lỗi: Thư mục nguồn không chứa file SKILL.md hợp lệ!")
        sys.exit(1)

    with open(skill_md_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Parse frontmatter name if present
    name_m = re.search(r"^name:\s*([^\n\r]+)", content, re.MULTILINE)
    if name_m:
        skill_name = name_m.group(1).strip().strip("\"'")

    print(f"📦 Đang thẩm định Skill: '{skill_name}'")

    # 1. Kiểm tra va chạm (Collision Check)
    existing_path = check_existing_collision(skill_name)
    if existing_path:
        print(f"⚠️  CẢNH BÁO XUNG ĐỘT: Skill '{skill_name}' đã tồn tại trong kho tại:")
        print(f"   👉 {existing_path}")
        if not force:
            print("   Để ghi đè và lưu bản cũ vào 'deprecated', hãy chạy lại với cờ --force")
            return
        else:
            dep_dir = os.path.join(SKILLS_DIR, "deprecated", f"{skill_name}_backup")
            os.makedirs(dep_dir, exist_ok=True)
            print(f"   🔄 Đang sao lưu bản cũ sang: {dep_dir}")
            shutil.move(existing_path, dep_dir)

    # 2. Xác định phân nhánh
    branch = target_branch if target_branch else analyze_branch_heuristic(skill_name, content)
    print(f"📂 Phân nhánh đề xuất: {branch}")

    # 3. Sao chép vào thư mục đích
    dest_category = "engineering"
    dest_skill_dir = os.path.join(SKILLS_DIR, dest_category, skill_name)
    os.makedirs(dest_skill_dir, exist_ok=True)

    if os.path.isdir(source_path):
        for item in os.listdir(source_path):
            s = os.path.join(source_path, item)
            d = os.path.join(dest_skill_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
    else:
        shutil.copy2(source_path, os.path.join(dest_skill_dir, "SKILL.md"))

    print(f"✅ Đã lưu skill vào: {dest_skill_dir}")

    # 4. Tự động cập nhật Web Data và Symlink
    print("🔄 Đang đồng bộ hóa dữ liệu Web Hub & Symlink hệ thống...")
    try:
        subprocess.run(["python3", os.path.join(SCRIPTS_DIR, "build_web_data.py")], check=True)
        subprocess.run(["bash", os.path.join(SCRIPTS_DIR, "link-skills.sh")], check=True)
        print("🎉 THÀNH CÔNG: Skill đã được nạp, giải quyết xung đột và sẵn sàng sử dụng qua /dsg!")
        print(f"🌐 Xem trực tiếp trên Web Hub: http://localhost:3333")
    except Exception as e:
        print(f"⚠️ Cảnh báo khi chạy script đồng bộ: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DSG Skill Ingestion Tool")
    parser.add_argument("source", help="Đường dẫn tới thư mục hoặc file SKILL.md cần nạp")
    parser.add_argument("--branch", choices=BRANCHES, help="Chỉ định phân nhánh cụ thể")
    parser.add_argument("--force", action="store_true", help="Ghi đè nếu đã tồn tại")
    args = parser.parse_args()

    ingest_skill(args.source, target_branch=args.branch, force=args.force)
