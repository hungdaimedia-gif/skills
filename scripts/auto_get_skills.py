#!/usr/bin/env python3
"""
AUTO SKILL PIPELINE — Tự động nạp skills từ nhiều GitHub repos.

Cách dùng:
  python3 scripts/auto_get_skills.py                    # Nạp tất cả từ sources.yml
  python3 scripts/auto_get_skills.py --dry-run          # Preview, không thay đổi
  python3 scripts/auto_get_skills.py --repo owner/repo  # Chỉ 1 repo
  python3 scripts/auto_get_skills.py --conflict override # Ghi đè khi xung đột
"""

import os
import sys
import shutil
import re
import argparse
import subprocess
import tempfile
import difflib

try:
    import yaml
except ImportError:
    print("⚙️  Cài PyYAML: pip3 install pyyaml")
    sys.exit(1)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")
SOURCES_FILE = os.path.join(REPO_ROOT, "sources.yml")
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
CACHE_DIR = os.path.join(REPO_ROOT, ".skill-cache")

DOMAIN_MAP = {
    "engineering": "engineering",
    "writing": "writing",
    "art": "art",
    "finance": "finance",
    "productivity": "productivity",
    "misc": "misc",
}

BRANCH_KEYWORDS = {
    "💡 Ý tưởng & Đặc tả": ["spec", "ticket", "grill", "idea", "question", "domain", "plan", "wayfinder"],
    "🏗️ Kiến trúc & Thiết kế": ["architecture", "design", "module", "canvas", "flow", "boilerplate", "prototype"],
    "⚡ Viết Code & TDD": ["tdd", "test", "implement", "coding", "task", "runner"],
    "🛡️ Kiểm soát & Review": ["review", "budget", "guard", "conflict", "merge", "commit", "handoff"],
    "🩺 Cứu hộ & Gỡ lỗi": ["bug", "debug", "diagnos", "recovery", "disorientation", "error", "log"],
    "🚀 Nền tảng & Vận hành": ["setup", "install", "platform", "store", "wizard", "deploy", "m1"],
    "📖 Cốt truyện & Thế giới": ["world", "story", "novel", "character", "arc", "plot", "beat"],
    "🎨 Prompt & Bố cục Thị giác": ["midjourney", "prompt", "image", "art", "visual", "flux"],
    "📊 Phân tích BCTC & Dòng tiền": ["finance", "statement", "cash", "invest", "balance", "income"],
}


def detect_branch(name, content):
    text = (name + " " + content).lower()
    for branch, keywords in BRANCH_KEYWORDS.items():
        if any(k in text for k in keywords):
            return branch
    return "⚡ Viết Code & TDD"


def detect_domain(name, content, hint=None):
    if hint and hint in DOMAIN_MAP:
        return hint
    text = (name + " " + content).lower()
    if any(k in text for k in ["story", "novel", "character", "arc", "world", "beat"]):
        return "writing"
    if any(k in text for k in ["midjourney", "flux", "stable diffusion", "prompt art"]):
        return "art"
    if any(k in text for k in ["finance", "bctc", "balance sheet", "cash flow", "invest"]):
        return "finance"
    if any(k in text for k in ["grill", "handoff", "teach", "questionnaire", "wait-what"]):
        return "productivity"
    return "engineering"


# ===== QUALITY GATE CONSTANTS =====
DANGER_PATTERNS = [
    r"skip\s+(tests?|tdd)",
    r"git push\s+--force",
    r"no need\s+(for\s+)?(human|review|test)",
    r"always correct",
    r"bỏ qua test",
]
WHEN_KEYWORDS = ["when", "use when", "trigger", "activate", "khi nào"]
WHAT_KEYWORDS = ["what", "purpose", "goal", "how to", "làm gì", "mục đích"]
STEP_KEYWORDS = ["step", "phase", "bước", "process", "workflow", "protocol", "## "]


def validate_skill(skill_name, content, domain):
    """Chấm điểm skill theo 5 Quality Gates (0-100). Trả về (score, report)."""
    report = {}
    score = 0

    # Gate 1: Cấu trúc (20đ)
    has_name = bool(re.search(r"^name:\s*\S+", content, re.MULTILINE))
    has_desc = bool(re.search(r"^description:\s*.{20,200}", content, re.MULTILINE))
    name_valid = bool(re.match(r"^[a-z0-9\-]+$", skill_name))
    g1 = 20 if (has_name and has_desc and name_valid) else (10 if (has_name or has_desc) else 0)
    report["gate1_structure"] = {"score": g1, "max": 20,
                                  "details": f"name={has_name} desc={has_desc} name_valid={name_valid}"}
    score += g1

    # Gate 2: Nội dung tối thiểu (30đ)
    word_count = len(content.split())
    text_lower = content.lower()
    has_when = any(k in text_lower for k in WHEN_KEYWORDS)
    has_what = any(k in text_lower for k in WHAT_KEYWORDS)
    has_steps = any(k in text_lower for k in STEP_KEYWORDS)
    answered = sum([has_when, has_what, has_steps])
    if word_count >= 150 and answered >= 2:
        g2 = 30
    elif word_count >= 80 and answered >= 1:
        g2 = 15
    else:
        g2 = 0
    report["gate2_substance"] = {"score": g2, "max": 30,
                                  "details": f"words={word_count} when={has_when} what={has_what} steps={has_steps}"}
    score += g2

    # Gate 3: Novelty — checked by collision detector, assume pass
    report["gate3_novelty"] = {"score": 20, "max": 20, "details": "checked separately"}
    score += 20

    # Gate 4: Domain fit (15đ)
    g4 = 15 if domain in DOMAIN_MAP else 0
    report["gate4_domain"] = {"score": g4, "max": 15, "details": f"domain={domain}"}
    score += g4

    # Gate 5: Safety (15đ)
    danger_hits = [p for p in DANGER_PATTERNS if re.search(p, text_lower)]
    g5 = 0 if danger_hits else 15
    report["gate5_safety"] = {"score": g5, "max": 15,
                               "details": f"violations={'none' if not danger_hits else danger_hits}"}
    score += g5

    return score, report


def print_quality_report(score, report):
    status = "✅ PASS" if score >= 70 else "❌ REJECT"
    print(f"     🔬 Quality Gate [{status}] — {score}/100 điểm")
    for gate, data in report.items():
        icon = "✅" if data["score"] == data["max"] else ("⚠️ " if data["score"] > 0 else "❌")
        print(f"        {icon} {gate}: {data['score']}/{data['max']} — {data['details']}")


def find_all_skills(repo_local_path, skills_dir_hint="skills"):
    """Quét repo và tìm tất cả thư mục chứa SKILL.md."""
    found = []
    search_root = os.path.join(repo_local_path, skills_dir_hint)
    if not os.path.isdir(search_root):
        search_root = repo_local_path

    for root, dirs, files in os.walk(search_root):
        # Bỏ qua deprecated và node_modules
        dirs[:] = [d for d in dirs if d not in ("deprecated", "node_modules", ".git")]
        if "SKILL.md" in files:
            found.append(root)
    return found


def check_collision(skill_name):
    """Kiểm tra skill trùng tên trong kho."""
    for root, dirs, files in os.walk(SKILLS_DIR):
        if os.path.basename(root) == skill_name and "SKILL.md" in files:
            return root
    return None


def similarity_score(text_a, text_b):
    """Tính độ tương đồng nội dung 0.0 → 1.0."""
    return difflib.SequenceMatcher(None, text_a[:500], text_b[:500]).ratio()


def resolve_conflict(skill_name, existing_path, new_skill_path, policy, dry_run):
    """Xử lý xung đột theo policy: skip | override | merge (giữ bản cũ, bổ sung)."""
    existing_md = os.path.join(existing_path, "SKILL.md")
    new_md = os.path.join(new_skill_path, "SKILL.md")

    with open(existing_md, "r", encoding="utf-8", errors="ignore") as f:
        existing_content = f.read()
    with open(new_md, "r", encoding="utf-8", errors="ignore") as f:
        new_content = f.read()

    score = similarity_score(existing_content, new_content)
    similarity_pct = int(score * 100)

    print(f"   📊 Độ tương đồng nội dung: {similarity_pct}%")

    if score >= 0.85:
        print(f"   ✅ Rất giống nhau ({similarity_pct}%) — Bỏ qua, giữ bản hiện tại.")
        return "skipped"

    if policy == "skip":
        print(f"   ⏭️  Policy=skip — Bỏ qua bản mới, giữ bản hiện tại.")
        return "skipped"

    if policy == "override":
        print(f"   🔄 Policy=override — Sao lưu bản cũ vào deprecated/ rồi ghi đè.")
        if not dry_run:
            backup = os.path.join(SKILLS_DIR, "deprecated", f"{skill_name}_backup")
            os.makedirs(backup, exist_ok=True)
            shutil.move(existing_path, backup)
        return "override"

    # policy == "merge": Giữ bản cũ, chỉ ghi chú trong SKILL.md
    print(f"   🔀 Policy=merge — Khác nhau ({similarity_pct}%), giữ bản gốc, thêm ghi chú nguồn.")
    if not dry_run:
        note = f"\n\n<!-- SOURCE: Imported from pipeline, similarity={similarity_pct}% -->\n"
        with open(existing_md, "a", encoding="utf-8") as f:
            f.write(note)
    return "merged"


def ingest_one_skill(skill_path, domain_hint, conflict_policy, dry_run):
    """Nạp 1 skill vào kho."""
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md):
        return False

    with open(skill_md, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Lấy tên từ frontmatter hoặc tên thư mục
    name_m = re.search(r"^name:\s*([^\n\r]+)", content, re.MULTILINE)
    skill_name = name_m.group(1).strip().strip("\"'") if name_m else os.path.basename(skill_path)

    domain = detect_domain(skill_name, content, hint=domain_hint)
    branch = detect_branch(skill_name, content)

    print(f"\n  📦 Skill: '{skill_name}'")
    print(f"     Domain: {domain} | Branch: {branch}")

    # ===== QUALITY GATE CHECK =====
    score, report = validate_skill(skill_name, content, domain)
    print_quality_report(score, report)
    if score < 70:
        print(f"  🚫 REJECTED: Điểm {score}/100 thấp hơn ngưỡng 70 — Xem SKILL_STANDARDS.md để biết thêm.")
        return False

    # Kiểm tra xung đột
    existing = check_collision(skill_name)
    if existing:
        print(f"  ⚠️  Xung đột: đã tồn tại tại {existing}")
        result = resolve_conflict(skill_name, existing, skill_path, conflict_policy, dry_run)
        if result == "skipped":
            return False
        if result == "merged":
            return True


    # Sao chép vào thư mục đích
    dest_dir = os.path.join(SKILLS_DIR, domain, skill_name)
    if not dry_run:
        os.makedirs(dest_dir, exist_ok=True)
        for item in os.listdir(skill_path):
            s = os.path.join(skill_path, item)
            d = os.path.join(dest_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        print(f"     ✅ Đã lưu: {dest_dir}")
    else:
        print(f"     [DRY-RUN] Sẽ lưu tại: {dest_dir}")
    return True


def process_repo(source, global_conflict, dry_run):
    """Clone 1 repo và nạp tất cả skills từ đó."""
    repo = source.get("repo")
    branch = source.get("branch", "main")
    skills_dir = source.get("skills_dir", "skills")
    domain_hint = source.get("domain", None)
    conflict_policy = source.get("conflict", global_conflict or "skip")

    print(f"\n{'='*60}")
    print(f"📥 REPO: {repo} (branch: {branch})")
    print(f"{'='*60}")

    # Clone vào cache tạm
    cache_path = os.path.join(CACHE_DIR, repo.replace("/", "__"))
    if os.path.exists(cache_path):
        print(f"  🔄 Đang cập nhật cache...")
        if not dry_run:
            subprocess.run(["git", "-C", cache_path, "pull", "--quiet"], check=False)
    else:
        print(f"  📡 Đang clone {repo}...")
        if not dry_run:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            ret = subprocess.run(
                ["git", "clone", "--depth=1", "--branch", branch,
                 f"https://github.com/{repo}.git", cache_path],
                capture_output=True, text=True
            )
            if ret.returncode != 0:
                print(f"  ❌ Clone thất bại: {ret.stderr.strip()}")
                return 0, 0

    if dry_run:
        print(f"  [DRY-RUN] Sẽ clone từ: https://github.com/{repo}.git")
        return 0, 0

    # Tìm và nạp tất cả skills
    skill_paths = find_all_skills(cache_path, skills_dir)
    print(f"  🔍 Tìm thấy {len(skill_paths)} skills trong repo")

    added = 0
    skipped = 0
    for sp in skill_paths:
        ok = ingest_one_skill(sp, domain_hint, conflict_policy, dry_run)
        if ok:
            added += 1
        else:
            skipped += 1

    return added, skipped


def rebuild_hub():
    """Tái tạo Web Hub và symlink sau khi nạp xong."""
    print(f"\n{'='*60}")
    print("🔄 Đang rebuild Web Hub & Symlinks...")
    try:
        subprocess.run(["python3", os.path.join(SCRIPTS_DIR, "build_web_data.py")], check=True)
        subprocess.run(["bash", os.path.join(SCRIPTS_DIR, "link-skills.sh")], check=True)
        print("🎉 Hoàn tất! Mở http://localhost:3333 để xem skills mới.")
    except Exception as e:
        print(f"⚠️  Lỗi khi rebuild: {e}")


def main():
    parser = argparse.ArgumentParser(description="Auto Skill Pipeline — Nạp skills từ nhiều GitHub repos")
    parser.add_argument("--dry-run", action="store_true", help="Preview, không thay đổi gì")
    parser.add_argument("--repo", help="Chỉ xử lý repo cụ thể (format: owner/repo)")
    parser.add_argument("--conflict", choices=["skip", "override", "merge"],
                        help="Ghi đè policy xung đột toàn cục")
    args = parser.parse_args()

    if not os.path.exists(SOURCES_FILE):
        print(f"❌ Không tìm thấy {SOURCES_FILE}")
        print("Chạy script từ thư mục gốc của repo.")
        sys.exit(1)

    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    sources = config.get("sources", [])
    if args.repo:
        sources = [s for s in sources if s.get("repo") == args.repo]
        if not sources:
            print(f"❌ Không tìm thấy repo '{args.repo}' trong sources.yml")
            sys.exit(1)

    print("🚀 AUTO SKILL PIPELINE")
    print(f"   Nguồn: {SOURCES_FILE}")
    print(f"   Repos: {len(sources)}")
    if args.dry_run:
        print("   [CHẾ ĐỘ DRY-RUN — Không thay đổi thực tế]")

    total_added = 0
    total_skipped = 0

    for source in sources:
        added, skipped = process_repo(source, args.conflict, args.dry_run)
        total_added += added
        total_skipped += skipped

    print(f"\n{'='*60}")
    print(f"📊 KẾT QUẢ PIPELINE:")
    print(f"   ✅ Đã thêm:    {total_added} skills mới")
    print(f"   ⏭️  Bỏ qua:    {total_skipped} skills (đã có hoặc quá giống)")
    print(f"{'='*60}")

    if not args.dry_run and total_added > 0:
        rebuild_hub()
    elif args.dry_run:
        print("\n[DRY-RUN] Chạy lại không có --dry-run để thực sự nạp.")


if __name__ == "__main__":
    main()
