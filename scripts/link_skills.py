#!/usr/bin/env python3
"""
LINK SKILLS (Cross-Platform: macOS, Linux, Windows)
Tạo liên kết symlink/junction từ kho skills vào thư mục Agent harness:
  - ~/.agents/skills (Codex, Antigravity IDE, Agent harnesses)
  - ~/.claude/skills (Claude Code)

Tự động xử lý tương thích Windows:
  1. Thử tạo Symlink (nếu bật Developer Mode)
  2. Fallback sang Directory Junction (mklink /J - không cần quyền Admin)
  3. Fallback sang Copy nếu filesystem không hỗ trợ link
"""

import os
import sys
import shutil
import platform
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
HOME = Path.home()

DESTINATIONS = [
    HOME / ".claude" / "skills",
    HOME / ".agents" / "skills",
]

EXCLUDE_DIRS = {"node_modules", "deprecated", "misc"}


def find_skills():
    """Tìm tất cả các thư mục chứa SKILL.md hợp lệ."""
    skills = []
    for root, dirs, files in os.walk(SKILLS_DIR):
        # Bỏ qua thư mục loại trừ
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        if "SKILL.md" in files:
            skill_dir = Path(root)
            skills.append((skill_dir.name, skill_dir))
    return sorted(skills, key=lambda x: x[0])


def link_directory(src: Path, dst: Path):
    """Tạo liên kết xuyên nền tảng (Symlink -> Junction -> Copy)."""
    # Xoá liên kết hoặc thư mục cũ nếu đã tồn tại
    if dst.is_symlink() or os.path.islink(dst):
        try:
            dst.unlink()
        except OSError:
            pass
    elif dst.exists():
        if dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()

    # Thử tạo Symlink
    try:
        dst.symlink_to(src, target_is_directory=True)
        return "symlink"
    except (OSError, NotImplementedError):
        pass

    # Trên Windows: Thử tạo Directory Junction (mklink /J)
    if platform.system() == "Windows":
        try:
            import subprocess
            res = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(dst), str(src)],
                capture_output=True,
                text=True
            )
            if res.returncode == 0:
                return "junction"
        except Exception:
            pass

    # Fallback cuối cùng: Copy thư mục
    shutil.copytree(src, dst)
    return "copied"


def main():
    print(f"🔗 SKILLS LINKER — Nền tảng: {platform.system()} ({platform.machine()})")
    print(f"   Kho skills gốc: {SKILLS_DIR}")

    skills = find_skills()
    print(f"   Tìm thấy: {len(skills)} skills hợp lệ")

    for dest in DESTINATIONS:
        dest.mkdir(parents=True, exist_ok=True)
        print(f"\n📂 Đang liên kết vào: {dest}")

        linked_count = 0
        method_used = "symlink"
        for name, src in skills:
            target = dest / name
            method = link_directory(src, target)
            method_used = method
            linked_count += 1

        print(f"   ✅ Hoàn tất {linked_count} skills [chế độ: {method_used}]")

    print("\n🎉 Toàn bộ skills đã sẵn sàng! Mở Agent và gõ /dsg để bắt đầu.")


if __name__ == "__main__":
    main()
