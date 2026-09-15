#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║        Code Bug Inspector — Agent Loop Blueprint         ║
║  Phân tích lỗi phần mềm theo quy trình 4 bước chuẩn     ║
╚══════════════════════════════════════════════════════════╝
"""

import subprocess
import sys
import os
import re
import json
from pathlib import Path
from datetime import datetime


# ─── ANSI Colors ─────────────────────────────────────────
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def header(text):   print(f"\n{BOLD}{CYAN}{'═'*55}{RESET}\n{BOLD}{CYAN}  {text}{RESET}\n{BOLD}{CYAN}{'═'*55}{RESET}")
def ok(text):       print(f"  {GREEN}✅ {text}{RESET}")
def warn(text):     print(f"  {YELLOW}⚠️  {text}{RESET}")
def err(text):      print(f"  {RED}❌ {text}{RESET}")
def info(text):     print(f"  {BLUE}ℹ️  {text}{RESET}")
def step(n, text):  print(f"\n{BOLD}[Bước {n}]{RESET} {text}")


# ════════════════════════════════════════════════════════════
# BƯỚC 1: THU THẬP MÔI TRƯỜNG (Reconnaissance)
# ════════════════════════════════════════════════════════════
def step1_environment():
    step(1, "Thu thập thông tin môi trường...")

    env = {}

    # Python version
    env["python"] = sys.version.split()[0]
    ok(f"Python: {env['python']}")

    # Node.js version
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            env["node"] = result.stdout.strip()
            ok(f"Node.js: {env['node']}")
        else:
            warn("Node.js: không tìm thấy")
            env["node"] = None
    except FileNotFoundError:
        warn("Node.js: chưa có trong PATH (bỏ qua)")
        env["node"] = None

    # pip packages
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=json"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        packages = {p["name"].lower(): p["version"] for p in json.loads(result.stdout)}
        env["packages"] = packages
        ok(f"Đã tìm thấy {len(packages)} Python packages")
    else:
        env["packages"] = {}

    return env


# ════════════════════════════════════════════════════════════
# BƯỚC 2: KHOANH VÙNG LỖI (Isolation)
# ════════════════════════════════════════════════════════════
def step2_isolate(file_path: str):
    step(2, f"Khoanh vùng mã nguồn: {file_path}")

    if not Path(file_path).exists():
        err(f"File không tồn tại: {file_path}")
        return None

    ext = Path(file_path).suffix.lower()
    info(f"Loại file: {ext}")

    if ext == ".py":
        return _run_python_check(file_path)
    elif ext in [".js", ".mjs", ".ts"]:
        return _run_node_check(file_path)
    else:
        warn(f"Chưa hỗ trợ phân tích file {ext}. Thực hiện kiểm tra cơ bản...")
        return _basic_check(file_path)


def _run_python_check(file_path):
    errors = []

    # Syntax check
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", file_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        errors.append({"type": "SyntaxError", "detail": result.stderr.strip()})
        err(f"Lỗi cú pháp Python:\n    {result.stderr.strip()}")
    else:
        ok("Không có lỗi cú pháp Python")

    # Pyflakes static analysis (nếu có)
    result = subprocess.run(
        [sys.executable, "-m", "pyflakes", file_path],
        capture_output=True, text=True
    )
    if result.returncode != 0 and result.stdout:
        for line in result.stdout.strip().splitlines():
            errors.append({"type": "StaticAnalysis", "detail": line})
            warn(f"Pyflakes: {line}")
    elif result.returncode == 0:
        ok("Pyflakes: Không có vấn đề")

    # Thực thi thử và bắt runtime error
    result = subprocess.run(
        [sys.executable, file_path],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        errors.append({"type": "RuntimeError", "detail": result.stderr.strip()})
        err(f"Lỗi khi chạy file:\n    {result.stderr.strip()}")
    else:
        ok(f"Chạy thành công. Output:\n    {result.stdout.strip()[:200]}")

    return errors


def _run_node_check(file_path):
    errors = []

    result = subprocess.run(
        ["node", "--check", file_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        errors.append({"type": "SyntaxError", "detail": result.stderr.strip()})
        err(f"Lỗi cú pháp Node.js:\n    {result.stderr.strip()}")
    else:
        ok("Không có lỗi cú pháp Node.js")

    result = subprocess.run(
        ["node", file_path],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        errors.append({"type": "RuntimeError", "detail": result.stderr.strip()})
        err(f"Lỗi khi chạy file:\n    {result.stderr.strip()}")
    else:
        ok(f"Chạy thành công. Output:\n    {result.stdout.strip()[:200]}")

    return errors


def _basic_check(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    info(f"File có {len(lines)} dòng. Kiểm tra cơ bản hoàn tất.")
    return []


# ════════════════════════════════════════════════════════════
# BƯỚC 3: PHÂN LOẠI NGUYÊN NHÂN (Root Cause Analysis)
# ════════════════════════════════════════════════════════════
def step3_root_cause(errors: list):
    step(3, "Phân tích nguyên nhân cốt lõi...")

    if not errors:
        ok("Không phát hiện lỗi nào!")
        return []

    classified = []
    for e in errors:
        detail = e.get("detail", "")

        # Nhận diện loại lỗi
        if e["type"] == "SyntaxError" or "SyntaxError" in detail:
            cat = "🔴 Lỗi Cú pháp (Syntax)"
            tip = "Kiểm tra dấu ngoặc, dấu phẩy, thụt đầu dòng (indent), hoặc từ khóa sai."
        elif "NameError" in detail or "undefined" in detail.lower():
            cat = "🟠 Lỗi Biến chưa định nghĩa (NameError)"
            tip = "Biến hoặc hàm được gọi trước khi được khai báo. Kiểm tra import và phạm vi (scope)."
        elif "AttributeError" in detail:
            cat = "🟠 Lỗi Thuộc tính (AttributeError)"
            tip = "Đối tượng không có thuộc tính/phương thức này. Kiểm tra kiểu dữ liệu hoặc kiểm tra None trước khi truy cập."
        elif "TypeError" in detail:
            cat = "🟡 Lỗi Kiểu dữ liệu (TypeError)"
            tip = "Truyền sai kiểu tham số, hoặc thực hiện phép toán trên sai kiểu. Kiểm tra kiểu đầu vào."
        elif "ImportError" in detail or "ModuleNotFoundError" in detail:
            cat = "🟣 Lỗi Import (ModuleNotFoundError)"
            tip = "Thư viện chưa được cài. Chạy: pip install <tên_thư_viện>"
        elif "IndexError" in detail or "KeyError" in detail:
            cat = "🟡 Lỗi Truy cập dữ liệu (Index/KeyError)"
            tip = "Truy cập phần tử không tồn tại trong list/dict. Kiểm tra độ dài hoặc dùng .get()."
        elif "RecursionError" in detail or "maximum recursion" in detail.lower():
            cat = "🔴 Lỗi Đệ quy vô hạn (RecursionError)"
            tip = "Hàm gọi đệ quy không có điều kiện thoát (base case). Kiểm tra lại logic dừng."
        elif "timeout" in detail.lower():
            cat = "🔴 Lỗi Vòng lặp vô hạn / Timeout"
            tip = "Chương trình bị kẹt. Kiểm tra điều kiện thoát của vòng lặp while/for."
        elif e["type"] == "StaticAnalysis":
            cat = "🔵 Cảnh báo tĩnh (Static Analysis)"
            tip = "Biến được định nghĩa nhưng không dùng, hoặc import thừa. Dọn dẹp code."
        else:
            cat = "⚪ Lỗi khác (Runtime)"
            tip = "Xem lại StackTrace để tìm chính xác dòng gây lỗi."

        classified.append({**e, "category": cat, "tip": tip})
        print(f"\n  {BOLD}{cat}{RESET}")
        print(f"  Chi tiết: {YELLOW}{detail[:300]}{RESET}")
        print(f"  💡 Gợi ý: {GREEN}{tip}{RESET}")

    return classified


# ════════════════════════════════════════════════════════════
# BƯỚC 4: TẠO BÁO CÁO (Report & Prevention)
# ════════════════════════════════════════════════════════════
def step4_report(file_path: str, classified: list, env: dict):
    step(4, "Tạo báo cáo lỗi...")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_path = Path(file_path).parent / "bug_report.md"

    lines = [
        f"# 🐛 Báo cáo Lỗi — {Path(file_path).name}",
        f"> Được tạo lúc: {timestamp} bởi Code Bug Inspector",
        "",
        "## Môi trường",
        f"- Python: `{env.get('python', 'N/A')}`",
        f"- Node.js: `{env.get('node', 'N/A')}`",
        "",
        f"## File kiểm tra: `{file_path}`",
        "",
        "## Kết quả",
    ]

    if not classified:
        lines.append("✅ Không phát hiện lỗi nào. Code chạy bình thường.")
    else:
        lines.append(f"Phát hiện **{len(classified)} lỗi**:\n")
        for i, e in enumerate(classified, 1):
            lines += [
                f"### Lỗi #{i}: {e['category']}",
                f"```",
                e.get("detail", "")[:500],
                f"```",
                f"**💡 Gợi ý sửa:** {e['tip']}",
                "",
            ]

    lines += [
        "## Phòng ngừa tái diễn",
        "- Thêm Unit Test cho các hàm cốt lõi.",
        "- Dùng type hints (Python) hoặc TypeScript để bắt lỗi kiểu sớm hơn.",
        "- Tích hợp linter (flake8, pylint, eslint) vào CI/CD pipeline.",
        "",
        "---",
        "_Báo cáo này được tạo tự động bởi `code-bug-inspector` skill._",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")
    ok(f"Báo cáo đã lưu tại: {report_path}")
    return str(report_path)


# ════════════════════════════════════════════════════════════
# MAIN ENTRY
# ════════════════════════════════════════════════════════════
def main():
    header("Code Bug Inspector — Agent Loop Blueprint")

    if len(sys.argv) < 2:
        err("Cách dùng: python bug_inspector.py <đường_dẫn_file>")
        err("Ví dụ:     python bug_inspector.py ../hello_loop.py")
        sys.exit(1)

    file_path = sys.argv[1]

    env       = step1_environment()
    errors    = step2_isolate(file_path)
    if errors is None:
        sys.exit(1)
    classified = step3_root_cause(errors)
    report    = step4_report(file_path, classified, env)

    header("Hoàn tất Kiểm tra")
    if classified:
        err(f"Phát hiện {len(classified)} lỗi. Xem báo cáo: {report}")
        sys.exit(1)
    else:
        ok(f"Không có lỗi. Báo cáo: {report}")
        sys.exit(0)


if __name__ == "__main__":
    main()
