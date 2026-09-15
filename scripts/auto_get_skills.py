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
import json
import argparse
import subprocess
import tempfile
import difflib
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone

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
LOGS_DIR = os.path.join(REPO_ROOT, "logs")
INGESTION_HISTORY_FILE = os.path.join(LOGS_DIR, "ingestion_history.jsonl")

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

# Các mẫu mã độc thực thi trong file .sh, .py, .js bên trong thư mục scripts/
SCRIPT_DANGER_PATTERNS = [
    (r"\b(OPENROUTER|ANTHROPIC|OPENAI|GITHUB|AWS|GEMINI)_[A-Z_]*KEY\b", "Đọc biến môi trường chứa API Key"),
    (r"\bcurl\s+[^|\n]*(-d|--data|-F|--form)\b", "Gửi dữ liệu ngầm ra mạng qua curl"),
    (r"\bwget\s+[^|\n]*--post-data\b", "Gửi dữ liệu ngầm ra mạng qua wget"),
    (r"\b(nc|ncat|netcat)\s+.*-e\b", "Mở reverse shell ngầm"),
    (r"/dev/tcp/\d+", "Mở kết nối socket ngầm qua /dev/tcp"),
    (r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+(/|~|\$HOME|\.\.)(\s|$)", "Lệnh xoá huỷ diệt root hoặc home directory"),
    (r"\bbase64\s+(-d|--decode)\s*\|\s*(ba)?sh\b", "Thực thi mã hoá base64 qua shell"),
    (r"\beval\s*\(\s*base64", "Hàm eval giải mã chuỗi base64"),
    (r"\b(curl|wget)\s+[^|\n]+\|\s*(ba)?sh\b", "Tải và thực thi script trực tiếp qua pipe shell"),
    (r"\.ssh/id_", "Cố tình truy cập private SSH key"),
]


def scan_script_safety(skill_dir_path):
    """Quét đệ quy toàn bộ thư mục skill tìm mã độc trong file thực thi (.sh, .py, .js...).
    Trả về (is_safe: bool, violations: list[str]).
    """
    if not skill_dir_path or not os.path.isdir(skill_dir_path):
        return True, []

    script_exts = {".sh", ".bash", ".py", ".js", ".mjs", ".zsh"}
    violations = []

    for root, _, files in os.walk(skill_dir_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in script_exts:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, skill_dir_path)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()
                    for pattern, desc in SCRIPT_DANGER_PATTERNS:
                        m = re.search(pattern, code, re.IGNORECASE)
                        if m:
                            violations.append(f"{rel_path}: {desc} ('{m.group(0)}')")
                except Exception as e:
                    violations.append(f"{rel_path}: Không thể đọc file ({e})")

    return (len(violations) == 0), violations


def validate_skill(skill_name, content, domain, skill_dir_path=None):
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

    # Gate 3: Novelty — cross-check description vs ALL existing skills
    desc_m = re.search(r"^description:\s*(.+)", content, re.MULTILINE)
    new_desc = desc_m.group(1).strip() if desc_m else ""
    max_cross_sim = 0.0
    if new_desc and len(new_desc) > 10:
        for walk_root, walk_dirs, walk_files in os.walk(SKILLS_DIR):
            walk_dirs[:] = [d for d in walk_dirs if d != "deprecated"]
            if "SKILL.md" in walk_files:
                try:
                    with open(os.path.join(walk_root, "SKILL.md"), "r", encoding="utf-8", errors="ignore") as ef:
                        ex_content = ef.read()
                    ex_desc_m = re.search(r"^description:\s*(.+)", ex_content, re.MULTILINE)
                    if ex_desc_m:
                        sim = similarity_score(new_desc, ex_desc_m.group(1).strip())
                        max_cross_sim = max(max_cross_sim, sim)
                except Exception:
                    pass
    cross_pct = int(max_cross_sim * 100)
    if max_cross_sim >= 0.80:
        g3 = 0   # Quá giống description của skill đã có
    elif max_cross_sim >= 0.60:
        g3 = 10  # Cảnh báo có thể chồng chéo
    else:
        g3 = 20  # Thực sự mới
    report["gate3_novelty"] = {"score": g3, "max": 20,
                                "details": f"max_desc_similarity={cross_pct}% vs existing skills"}
    score += g3

    # Gate 4: Domain fit (15đ)
    g4 = 15 if domain in DOMAIN_MAP else 0
    report["gate4_domain"] = {"score": g4, "max": 15, "details": f"domain={domain}"}
    score += g4

    # Gate 5: Safety (15đ) — Quét cả Markdown và thư mục scripts/
    danger_hits = [p for p in DANGER_PATTERNS if re.search(p, text_lower)]
    script_safe, script_violations = scan_script_safety(skill_dir_path) if skill_dir_path else (True, [])

    if danger_hits or not script_safe:
        g5 = 0
        details_list = []
        if danger_hits:
            details_list.append(f"md_violations={danger_hits}")
        if script_violations:
            details_list.append(f"script_violations={script_violations}")
        report["gate5_safety"] = {"score": 0, "max": 15, "details": "; ".join(details_list)}
    else:
        g5 = 15
        report["gate5_safety"] = {"score": 15, "max": 15, "details": "violations=none"}
    score += g5

    return score, report


def generate_fix_instructions(report, skill_name, content):
    """Tạo hướng dẫn sửa cụ thể cho từng Gate bị lỗi."""
    fixes = []

    g1 = report.get("gate1_structure", {})
    if g1.get("score", 20) < 20:
        details = g1.get("details", "")
        if "name_valid=False" in details:
            fixes.append(
                f"  🔧 [Gate 1] Tên skill không hợp lệ: '{skill_name}'\n"
                f"     → Chỉ dùng chữ thường, số và dấu gạch ngang: [a-z0-9-]\n"
                f"     → Sửa thành: '{skill_name.lower().replace(' ', '-').replace('_', '-')}'"
            )
        if "desc=False" in details:
            fixes.append(
                "  🔧 [Gate 1] Description quá ngắn hoặc thiếu trong frontmatter\n"
                "     → Thêm vào SKILL.md:\n"
                "       description: \"Mô tả rõ ràng ít nhất 20 ký tự, tối đa 200 ký tự.\""
            )
        if "name=False" in details:
            fixes.append(
                "  🔧 [Gate 1] Thiếu field 'name' trong frontmatter YAML\n"
                "     → Thêm vào đầu SKILL.md:\n"
                "       ---\n"
                "       name: ten-skill-cua-ban\n"
                "       description: \"...\"\n"
                "       ---"
            )

    g2 = report.get("gate2_substance", {})
    if g2.get("score", 30) < 30:
        details = g2.get("details", "")
        word_m = __import__("re").search(r"words=(\d+)", details)
        word_count = int(word_m.group(1)) if word_m else 0
        missing = []
        if "when=False" in details:
            missing.append("'khi nào dùng' (thêm: 'Use when: ...' hoặc 'Khi nào: ...')")
        if "what=False" in details:
            missing.append("'làm gì' (thêm: 'What it does: ...' hoặc '## Mục đích')")
        if "steps=False" in details:
            missing.append("'các bước' (thêm: '## Steps' hoặc '## Quy trình' với danh sách bước)")
        if word_count < 150:
            fixes.append(
                f"  🔧 [Gate 2] Nội dung quá ngắn: {word_count} từ (cần ≥ 150 từ)\n"
                f"     → Cần viết thêm khoảng {150 - word_count} từ nữa"
            )
        if missing:
            fixes.append(
                f"  🔧 [Gate 2] Thiếu các phần bắt buộc:\n"
                + "\n".join(f"     → {m}" for m in missing)
            )

    g3 = report.get("gate3_novelty", {})
    if g3.get("score", 20) < 20:
        details = g3.get("details", "")
        sim_m = __import__("re").search(r"max_desc_similarity=(\d+)%", details)
        sim_pct = int(sim_m.group(1)) if sim_m else 0
        fixes.append(
            f"  🔧 [Gate 3] Description quá giống skill đã có ({sim_pct}% tương đồng)\n"
            f"     → Kiểm tra: python3 scripts/auto_get_skills.py --dry-run\n"
            f"     → Làm rõ điểm khác biệt của skill này so với skill tương tự\n"
            f"     → Hoặc xem xét mở rộng skill đã có thay vì tạo mới"
        )

    g5 = report.get("gate5_safety", {})
    if g5.get("score", 15) < 15:
        details = g5.get("details", "")
        fixes.append(
            f"  🔧 [Gate 5] Skill vi phạm nguyên tắc an toàn\n"
            f"     → Vi phạm phát hiện: {details}\n"
            f"     → Xem quy tắc tại: SKILL_STANDARDS.md#gate-5-an-toàn--triết-lý"
        )

    return fixes


def print_quality_report(score, report, skill_name="", content=""):
    """In báo cáo chất lượng đầy đủ với hướng dẫn sửa cụ thể."""
    status = "✅ PASS" if score >= 70 else "❌ REJECT"
    print(f"     🔬 Quality Gate [{status}] — {score}/100 điểm")
    for gate, data in report.items():
        icon = "✅" if data["score"] == data["max"] else ("⚠️ " if data["score"] > 0 else "❌")
        print(f"        {icon} {gate}: {data['score']}/{data['max']} — {data['details']}")

    if score < 70 and skill_name:
        fixes = generate_fix_instructions(report, skill_name, content)
        if fixes:
            print(f"\n     📋 HƯỚNG DẪN SỬA ({len(fixes)} vấn đề):")
            for fix in fixes:
                print(fix)
            print(f"\n     💡 Sau khi sửa, chạy lại:")
            print(f"        python3 scripts/auto_get_skills.py /đường_dẫn/skill")


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
    """Tính độ tương đồng nội dung 0.0 → 1.0.
    BUG FIX: Dùng toàn bộ nội dung thay vì chỉ 500 ký tự đầu.
    Để tránh O(n^2) với file rất lớn, giới hạn 3000 ký tự.
    """
    limit = 3000
    return difflib.SequenceMatcher(None, text_a[:limit], text_b[:limit]).ratio()


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
def parse_frontmatter(content):
    """Tách frontmatter và body từ Markdown."""
    if not content.startswith("---"):
        return False, {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return False, {}, content
    try:
        fm = yaml.safe_load(parts[1])
        if isinstance(fm, dict):
            return True, fm, parts[2]
    except Exception:
        pass
    return False, {}, content


def inject_provenance_to_skill_md(file_path, repo_meta):
    """Gắn thông tin nguồn gốc GitHub vào YAML frontmatter của SKILL.md."""
    if not repo_meta or not os.path.exists(file_path):
        return
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        has_fm, fm, body = parse_frontmatter(content)
        if not has_fm or not isinstance(fm, dict):
            return

        fm["provenance"] = {
            "source_repo": repo_meta.get("repo", ""),
            "source_url": repo_meta.get("url", ""),
            "source_commit": repo_meta.get("commit", ""),
            "imported_at": repo_meta.get("imported_at", ""),
            "stars_at_import": repo_meta.get("stars", 0),
            "forks_at_import": repo_meta.get("forks", 0),
        }

        new_fm_str = yaml.dump(fm, allow_unicode=True, sort_keys=False).strip()
        new_content = f"---\n{new_fm_str}\n---\n{body}"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
    except Exception as e:
        print(f"     ⚠️  Không thể gắn provenance metadata: {e}")


def log_ingestion_event(repo_meta, added_skills, rejected_skills, skipped_skills):
    """Ghi nhật ký lịch sử nạp repo vào file JSON Lines."""
    if not repo_meta:
        return
    try:
        os.makedirs(LOGS_DIR, exist_ok=True)
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "repo": repo_meta.get("repo", ""),
            "url": repo_meta.get("url", ""),
            "commit": repo_meta.get("commit", ""),
            "stars": repo_meta.get("stars", 0),
            "forks": repo_meta.get("forks", 0),
            "added_count": len(added_skills),
            "added_skills": added_skills,
            "rejected_count": len(rejected_skills),
            "rejected_skills": rejected_skills,
            "skipped_count": len(skipped_skills),
            "skipped_skills": skipped_skills,
        }
        with open(INGESTION_HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"⚠️  Không thể ghi nhật ký lịch sử nạp: {e}")


def print_ingestion_history(limit=20):
    """In bảng lịch sử các lần nạp skill từ GitHub."""
    if not os.path.exists(INGESTION_HISTORY_FILE):
        print("📭 Chưa có lịch sử nạp nào được ghi nhận.")
        return

    events = []
    with open(INGESTION_HISTORY_FILE, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except Exception:
                    pass

    if not events:
        print("📭 Chưa có lịch sử nạp nào được ghi nhận.")
        return

    events.reverse()  # Hiện gần nhất trước
    events = events[:limit]

    print(f"\n{'='*75}")
    print(f"📜 LỊCH SỬ NẠP SKILLS TỪ GITHUB (Gần nhất {len(events)} lượt)")
    print(f"{'='*75}")
    print(f"{'Thời gian':<20} | {'Repo':<30} | {'Commit':<8} | {'Nạp':<5} | {'Loại':<5}")
    print(f"{'-'*20}-+-{'-'*30}-+-{'-'*8}-+-{'-'*5}-+-{'-'*5}")

    for ev in events:
        ts = ev.get("timestamp", "")[:19].replace("T", " ")
        repo = ev.get("repo", "")[:30]
        commit = str(ev.get("commit", ""))[:7]
        added = str(ev.get("added_count", 0))
        rejected = str(ev.get("rejected_count", 0))
        print(f"{ts:<20} | {repo:<30} | {commit:<8} | {added:<5} | {rejected:<5}")

        added_list = ev.get("added_skills", [])
        if added_list:
            print(f"   └─ ✅ Skills đã nạp: {', '.join(added_list)}")
        rej_list = ev.get("rejected_skills", [])
        if rej_list:
            print(f"   └─ 🚫 Skills bị loại: {', '.join([r.get('name', '') for r in rej_list if isinstance(r, dict)]) or ', '.join(map(str, rej_list))}")
    print(f"{'='*75}\n")


def ingest_one_skill(skill_path, domain_hint, conflict_policy, dry_run,
                     profile=None, quality_threshold=70, repo_meta=None):
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

    # ===== PROFILE FILTER CHECK =====
    if profile:
        dest_mock = os.path.join(SKILLS_DIR, domain, skill_name)
        if not apply_profile_filter(dest_mock, profile):
            print(f"  ⏭️  Profile filter: bỏ qua '{skill_name}' (không thuộc active_domains hoặc trong exclude_skills)")
            return "skipped"

    print(f"\n  📦 Skill: '{skill_name}'")
    print(f"     Domain: {domain} | Branch: {branch}")

    # ===== QUALITY GATE CHECK (5 Gates + Deep Script Security) =====
    score, report = validate_skill(skill_name, content, domain, skill_dir_path=skill_path)
    print_quality_report(score, report, skill_name=skill_name, content=content)
    if score < quality_threshold:
        print(f"  🚫 REJECTED: Điểm {score}/100 thấp hơn ngưỡng {quality_threshold} — Xem SKILL_STANDARDS.md để biết thêm.")
        return "rejected"

    # Kiểm tra xung đột
    existing = check_collision(skill_name)
    if existing:
        print(f"  ⚠️  Xung đột: đã tồn tại tại {existing}")
        conflict_result = resolve_conflict(skill_name, existing, skill_path, conflict_policy, dry_run)
        if conflict_result == "skipped":
            return "skipped"
        if conflict_result == "merged":
            return "skipped"  # Merged = không thêm mới, chỉ ghi chú

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

        # Gắn provenance metadata vào SKILL.md
        if repo_meta:
            inject_provenance_to_skill_md(os.path.join(dest_dir, "SKILL.md"), repo_meta)

        print(f"     ✅ Đã lưu: {dest_dir}")
    else:
        print(f"     [DRY-RUN] Sẽ lưu tại: {dest_dir}")
    return "added"


REPO_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$")


def verify_repo_social_proof(repo_name, min_stars=10000, min_forks=500, max_stale_days=180):
    """Kiểm tra uy tín cộng đồng của GitHub repo qua API trước khi nạp (Social Proof Gate).
    Trả về (passed: bool, reason: str, metadata: dict).
    """
    url = f"https://api.github.com/repos/{repo_name}"
    headers = {
        "User-Agent": "Skills-Auto-Pipeline/2.0",
        "Accept": "application/vnd.github.v3+json"
    }
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, f"Repo '{repo_name}' không tồn tại trên GitHub", {}
        elif e.code == 403:
            # Rate limited -> Bỏ qua kiểm tra mạng để không chặn pipeline offline
            return True, f"GitHub API rate limit (HTTP 403), bỏ qua bước kiểm tra mạng", {}
        return False, f"Lỗi GitHub API HTTP {e.code}: {e.reason}", {}
    except Exception as e:
        return True, f"Không thể kết nối GitHub API ({e}), bỏ qua bước kiểm tra mạng", {}

    stars = data.get("stargazers_count", 0)
    forks = data.get("forks_count", 0)
    archived = data.get("archived", False)
    disabled = data.get("disabled", False)
    pushed_at_str = data.get("pushed_at", "")

    metadata = {
        "stars": stars,
        "forks": forks,
        "archived": archived,
        "pushed_at": pushed_at_str,
        "description": data.get("description", ""),
    }

    if archived:
        return False, f"Repo đã bị đóng băng/ngừng phát triển (archived)", metadata
    if disabled:
        return False, f"Repo đã bị vô hiệu hóa (disabled)", metadata

    if stars < min_stars:
        return False, f"Số sao không đạt: {stars} ⭐ (yêu cầu tối thiểu ≥ {min_stars} ⭐)", metadata

    if forks < min_forks:
        return False, f"Số lượt fork không đạt: {forks} 🍴 (yêu cầu tối thiểu ≥ {min_forks} 🍴)", metadata

    # Kiểm tra ngày commit/push gần nhất
    if pushed_at_str:
        try:
            pushed_dt = datetime.fromisoformat(pushed_at_str.replace("Z", "+00:00"))
            now_dt = datetime.now(timezone.utc)
            days_ago = (now_dt - pushed_dt).days
            metadata["days_since_push"] = days_ago
            if days_ago > max_stale_days:
                return False, f"Repo bị bỏ hoang: commit gần nhất cách đây {days_ago} ngày (> {max_stale_days} ngày)", metadata
        except Exception:
            pass

    return True, f"Đạt chuẩn uy tín cộng đồng ({stars} ⭐, {forks} 🍴)", metadata


def discover_github_skills(query, min_stars=10000, min_forks=500, max_results=5):
    """Tìm kiếm tự động các repo skill chất lượng cao trên GitHub.
    Trả về danh sách các repo dict phù hợp.
    """
    encoded_query = urllib.parse.quote_plus(f"{query} stars:>={min_stars} forks:>={min_forks} archived:false")
    url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars&order=desc&per_page={max_results}"
    headers = {
        "User-Agent": "Skills-Auto-Pipeline/2.0",
        "Accept": "application/vnd.github.v3+json"
    }
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"❌ Lỗi tìm kiếm GitHub API: {e}")
        return []

    items = data.get("items", [])
    results = []
    for item in items:
        full_name = item.get("full_name", "")
        if REPO_PATTERN.match(full_name):
            results.append({
                "repo": full_name,
                "stars": item.get("stargazers_count", 0),
                "forks": item.get("forks_count", 0),
                "description": item.get("description", "") or "",
                "url": item.get("html_url", ""),
                "pushed_at": item.get("pushed_at", ""),
            })

    return results


def process_repo(source, global_conflict, dry_run, profile=None, quality_threshold=70,
                 social_check=True, min_stars=10000, min_forks=500, max_stale_days=180):
    """Clone 1 repo và nạp tất cả skills từ đó."""
    repo = source.get("repo", "")

    # === SECURITY: Validate repo name format trước khi dùng trong bất kỳ path/command nào ===
    if not REPO_PATTERN.match(repo):
        print(f"\n❌ SECURITY REJECT: repo name không hợp lệ: {repo!r}")
        print("   Chỉ cho phép format: 'owner/repo' (chữ cái, số, dấu gạch, chấm)")
        return 0, 0, 0

    # === GATE 0: SOCIAL PROOF & REPUTATION CHECK ===
    if social_check:
        passed, reason, meta = verify_repo_social_proof(
            repo, min_stars=min_stars, min_forks=min_forks, max_stale_days=max_stale_days
        )
        if not passed:
            print(f"\n🚫 SOCIAL PROOF REJECT: {reason}")
            print(f"   Bỏ qua repo '{repo}' vì không đạt chuẩn uy tín cộng đồng.")
            return 0, 0, 0
        elif meta.get("stars") is not None:
            days = meta.get("days_since_push", "?")
            print(f"  ⭐ Social Proof PASS: {meta['stars']} stars, {meta['forks']} forks (commit gần nhất: {days} ngày trước)")

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
        return 0, 0, 0

    # Lấy commit SHA của repo cache
    ret = subprocess.run(["git", "-C", cache_path, "rev-parse", "--short", "HEAD"],
                         capture_output=True, text=True, check=False)
    commit_sha = ret.stdout.strip() if ret.returncode == 0 else "head"

    repo_meta = {
        "repo": repo,
        "url": f"https://github.com/{repo}",
        "branch": branch,
        "commit": commit_sha,
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "stars": meta.get("stars", 0) if isinstance(meta, dict) else 0,
        "forks": meta.get("forks", 0) if isinstance(meta, dict) else 0,
    }

    # Tìm và nạp tất cả skills
    skill_paths = find_all_skills(cache_path, skills_dir)
    print(f"  🔍 Tìm thấy {len(skill_paths)} skills trong repo (commit: {commit_sha})")

    added = 0
    skipped = 0
    rejected = 0
    added_list = []
    rejected_list = []
    skipped_list = []

    for sp in skill_paths:
        sk_name = os.path.basename(sp)
        result = ingest_one_skill(sp, domain_hint, conflict_policy, dry_run,
                                 profile=profile, quality_threshold=quality_threshold,
                                 repo_meta=repo_meta)
        if result == "added":
            added += 1
            added_list.append(sk_name)
        elif result == "rejected":
            rejected += 1
            rejected_list.append(sk_name)
        else:
            skipped += 1
            skipped_list.append(sk_name)

    # Ghi lại lịch sử nạp vào logs/ingestion_history.jsonl
    log_ingestion_event(repo_meta, added_list, rejected_list, skipped_list)

    return added, skipped, rejected


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


PROFILES_DIR = os.path.join(REPO_ROOT, "profiles")


def load_profile(profile_name):
    """Tải profile YAML cho dự án. Trả về dict hoặc None nếu không có."""
    profile_path = os.path.join(PROFILES_DIR, f"{profile_name}.yml")
    if not os.path.exists(profile_path):
        print(f"❌ Không tìm thấy profile: {profile_path}")
        print(f"   Tạo profile mới: cp profiles/template.yml profiles/{profile_name}.yml")
        sys.exit(1)
    with open(profile_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def list_profiles():
    """Liệt kê tất cả profiles có sẵn."""
    if not os.path.isdir(PROFILES_DIR):
        return []
    return [
        f.replace(".yml", "")
        for f in os.listdir(PROFILES_DIR)
        if f.endswith(".yml") and f != "template.yml"
    ]


def apply_profile_filter(skills_dir_path, profile):
    """Kiểm tra skill có được phép trong profile này không."""
    if not profile:
        return True
    active_domains = set(profile.get("active_domains", list(DOMAIN_MAP.keys())))
    exclude_skills = set(profile.get("exclude_skills", []))
    include_tags = profile.get("include_tags", [])

    # Lấy domain từ đường dẫn: skills/<domain>/<skill-name>
    rel = os.path.relpath(skills_dir_path, SKILLS_DIR)
    parts = rel.split(os.sep)
    skill_domain = parts[0] if parts else "engineering"
    skill_name = parts[-1] if len(parts) > 1 else ""

    if skill_domain not in active_domains:
        return False
    if skill_name in exclude_skills:
        return False
    # include_tags filtering sẽ mở rộng sau khi có tag metadata
    return True


def main():
    parser = argparse.ArgumentParser(description="Auto Skill Pipeline — Săn tìm và nạp skills từ GitHub repos")
    parser.add_argument("--dry-run", action="store_true", help="Preview, không thay đổi gì")
    parser.add_argument("--repo", help="Chỉ xử lý repo cụ thể (format: owner/repo)")
    parser.add_argument("--conflict", choices=["skip", "override", "merge"],
                        help="Ghi đè policy xung đột toàn cục")
    parser.add_argument("--profile", help="Tên project profile (vd: hungdaitool, my-project)")
    parser.add_argument("--list-profiles", action="store_true", help="Liệt kê tất cả profiles có sẵn")
    parser.add_argument("--discover", help="Tự động tìm kiếm repo skill trên GitHub theo từ khóa")
    parser.add_argument("--min-stars", type=int, default=10000, help="Số sao tối thiểu cho Social Proof Gate (mặc định: 10000)")
    parser.add_argument("--min-forks", type=int, default=500, help="Số lượt fork tối thiểu (mặc định: 500)")
    parser.add_argument("--max-results", type=int, default=5, help="Số repo tối đa khi tìm kiếm --discover (mặc định: 5)")
    parser.add_argument("--no-social-check", action="store_true", help="Bỏ qua bước kiểm tra uy tín Social Proof Gate")
    parser.add_argument("--history", action="store_true", help="Hiển thị lịch sử các lần nạp skill từ GitHub")
    args = parser.parse_args()

    # === SHOW INGESTION HISTORY ===
    if args.history:
        print_ingestion_history()
        sys.exit(0)

    # === LIST PROFILES ===
    if args.list_profiles:
        profiles = list_profiles()
        print("📂 Profiles có sẵn:")
        for p in profiles:
            profile_path = os.path.join(PROFILES_DIR, f"{p}.yml")
            data = yaml.safe_load(open(profile_path))
            desc = data.get("profile", {}).get("description", "")
            print(f"   • {p:20s} — {desc}")
        print("\nDùng: python3 scripts/auto_get_skills.py --profile <tên>")
        sys.exit(0)

    # === AUTO-DISCOVER REPOS VIA GITHUB API ===
    if args.discover:
        print(f"\n🔎 Đang săn tìm kỹ năng trên GitHub: '{args.discover}' (yêu cầu ≥ {args.min_stars} ⭐, ≥ {args.min_forks} 🍴)...")
        found_repos = discover_github_skills(
            args.discover,
            min_stars=args.min_stars,
            min_forks=args.min_forks,
            max_results=args.max_results
        )
        if not found_repos:
            print(f"⚠️  Không tìm thấy repo nào đạt chuẩn uy tín (≥ {args.min_stars} ⭐, ≥ {args.min_forks} 🍴) cho: '{args.discover}'.")
            sys.exit(0)

        print(f"🎉 Tìm thấy {len(found_repos)} repo uy tín đạt chuẩn cộng đồng:")
        sources = []
        for r in found_repos:
            print(f"   • {r['repo']:35s} ⭐ {r['stars']:<6d} 🍴 {r['forks']:<5d} — {r['description'][:55]}...")
            sources.append({"repo": r["repo"], "conflict": args.conflict or "skip"})

        # Khi discover, mặc định bỏ qua kiểm tra lại social proof trong loop vì đã lọc sẵn
        args.no_social_check = True

    else:
        # === LOAD PROFILE ===
        profile = None
        quality_threshold = 70  # default
        if args.profile:
            profile = load_profile(args.profile)
            quality_threshold = profile.get("quality_threshold", 70)
            prof_meta = profile.get("profile", {})
            print(f"🎯 PROFILE: {prof_meta.get('name', args.profile)}")
            print(f"   {prof_meta.get('description', '')}")
            print(f"   Domains: {', '.join(profile.get('active_domains', ['all']))}")
            print(f"   Quality threshold: {quality_threshold}/100")

        # === LOAD SOURCES ===
        if profile and profile.get("sources"):
            sources = profile["sources"]
            print(f"   Sources: từ profile ({len(sources)} repos)")
        elif os.path.exists(SOURCES_FILE):
            with open(SOURCES_FILE, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            sources = config.get("sources", [])
            print(f"   Sources: từ sources.yml ({len(sources)} repos)")
        else:
            print(f"❌ Không tìm thấy sources.yml và profile không có sources riêng")
            sys.exit(1)

        if args.repo:
            sources = [s for s in sources if s.get("repo") == args.repo]
            if not sources:
                print(f"❌ Không tìm thấy repo '{args.repo}'")
                sys.exit(1)

    print(f"\n🚀 AUTO SKILL PIPELINE")
    print(f"   Repos: {len(sources)}")
    if args.dry_run:
        print("   [CHẾ ĐỘ DRY-RUN — Không thay đổi thực tế]")

    total_added = 0
    total_skipped = 0
    total_rejected = 0

    for source in sources:
        added, skipped, rejected = process_repo(
            source, args.conflict, args.dry_run,
            profile=(profile if not args.discover else None),
            quality_threshold=(quality_threshold if not args.discover else 70),
            social_check=(not args.no_social_check),
            min_stars=args.min_stars,
            min_forks=args.min_forks
        )
        total_added += added
        total_skipped += skipped
        total_rejected += rejected

    print(f"\n{'='*60}")
    print(f"📊 KẾT QUẢ PIPELINE:")
    print(f"   ✅ Đã thêm:    {total_added} skills mới")
    print(f"   ⏭️  Bỏ qua:    {total_skipped} skills (đã có hoặc quá giống)")
    print(f"   🚫 Từ chối:   {total_rejected} skills (không đạt Quality Gate / Social Proof)")
    print(f"{'='*60}")

    if not args.dry_run and total_added > 0:
        rebuild_hub()
    elif args.dry_run:
        print("\n[DRY-RUN] Chạy lại không có --dry-run để thực sự nạp.")


if __name__ == "__main__":
    main()
