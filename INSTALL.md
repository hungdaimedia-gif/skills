# INSTALL — Hướng Dẫn Cài Đặt Trên Máy Mới

> Kho skills này được thiết kế để **dùng được ở mọi dự án** trên máy của bạn,
> không phụ thuộc vào ngôn ngữ lập trình hay framework.

---

## Yêu Cầu Tối Thiểu

| Công cụ | Phiên bản | Mục đích |
| :--- | :--- | :--- |
| `git` | >= 2.x | Clone repo và pull cập nhật |
| `python3` | >= 3.9 | Build Web Hub và ingest skill mới |
| `bash` | >= 5.x | Chạy script link-skills |
| AI Agent | Claude Code / Codex / Antigravity IDE | Đọc và thực thi skills |

---

## Bước 1: Clone Repo Về Máy

```bash
git clone git@github.com:hungdaimedia-gif/skills.git ~/Projects/skills
cd ~/Projects/skills
```

---

## Bước 2: Cài Vào Toàn Máy (Recommended)

Chạy 1 lần duy nhất. Script sẽ tạo symlink từ repo vào 2 thư mục harness toàn máy:
- `~/.agents/skills/` (Codex, Antigravity IDE, các agent khác)
- `~/.claude/skills/` (Claude Code)

### 🍎 Trên macOS / Linux:
```bash
bash scripts/link-skills.sh
# Hoặc: python3 scripts/link_skills.py
```

### 🪟 Trên Windows:
Mở PowerShell hoặc Git Bash và chạy:
```powershell
python scripts/link_skills.py
```
*(Script tự động tạo Junction/Symlink vào `%USERPROFILE%\.agents\skills` và `%USERPROFILE%\.claude\skills`, tự động fallback sang copy nếu không có quyền admin).*

Kết quả: **Mọi dự án trên máy bạn** đều có thể gọi `/dsg`, `/tdd`, `/code-review`... ngay lập tức, không cần cấu hình thêm gì.

> **Cập nhật sau này**: Chỉ cần `git pull` trong thư mục repo. Toàn bộ skills được tự động cập nhật ngay lập tức.

---

## Bước 3: Khởi Động Web Hub (Skills Browser)

Web Hub là giao diện trực quan để tra cứu 53+ skills, lọc theo lĩnh vực và sao chép lệnh kích hoạt.

```bash
# Bước 3a: Build dữ liệu (chạy 1 lần, hoặc sau mỗi lần thêm skill mới)
python3 scripts/build_web_data.py

# Bước 3b: Khởi động server (chạy ngầm ở port 3333)
python3 -m http.server 3333 --directory web &

# Bước 3c: Mở trình duyệt
open http://localhost:3333
```

---

## Bước 4: Cài Per-Project (Tùy Chọn)

Nếu muốn skills riêng cho 1 dự án cụ thể (không chia sẻ toàn máy):

```bash
# Trong thư mục dự án của bạn:
mkdir -p .agents/skills

# Copy toàn bộ hoặc từng skill bạn cần:
cp -r ~/Projects/skills/skills/engineering/dsg .agents/skills/
cp -r ~/Projects/skills/skills/engineering/tdd .agents/skills/
# ...
```

---

## Nạp Skill Mới Từ GitHub Khác

Khi bạn tìm thấy skill hay từ một repo GitHub khác và muốn đưa vào kho:

```bash
# Clone skill đó về thư mục tạm:
git clone https://github.com/<author>/<repo>.git /tmp/new-skill-repo

# Chạy công cụ thẩm định (tự kiểm tra xung đột + phân nhánh):
python3 scripts/ingest_skill.py /tmp/new-skill-repo/skills/<skill-name>

# Xây lại dữ liệu Web Hub:
python3 scripts/build_web_data.py
```

---

## Cấu Trúc Thư Mục Sau Khi Cài

```
~/Projects/skills/              ← Repo nguồn, git pull để cập nhật
├── skills/
│   ├── engineering/            ← 31 skills kỹ thuật phần mềm
│   ├── productivity/           ← 7 skills năng suất cá nhân
│   ├── writing/                ← 2 skills sáng tác truyện
│   ├── art/                    ← 1 skill tranh AI (Midjourney)
│   ├── finance/                ← 1 skill phân tích tài chính
│   ├── misc/                   ← Skills tiện ích (không symlink toàn máy)
│   └── in-progress/            ← Skills đang thử nghiệm
├── web/                        ← Web Hub (http://localhost:3333)
├── scripts/
│   ├── link-skills.sh          ← Cài toàn máy (symlink)
│   ├── build_web_data.py       ← Build dữ liệu Web Hub
│   └── ingest_skill.py         ← Nạp skill mới từ GitHub
└── INSTALL.md                  ← File này

~/.agents/skills/               ← Symlinks → ~/Projects/skills/skills/*
~/.claude/skills/               ← Symlinks → ~/Projects/skills/skills/*
```

---

## Kiểm Tra Cài Đặt Thành Công

```bash
# Kiểm tra số skills đã link:
ls ~/.agents/skills/ | wc -l
# Kỳ vọng: >= 49

# Kiểm tra Web Hub đang chạy:
curl -sI http://localhost:3333/ | head -n 1
# Kỳ vọng: HTTP/1.0 200 OK

# Trong AI Agent, thử gọi:
# /dsg
# Kỳ vọng: Agent tự scan dự án và báo cáo chẩn đoán
```

---

## Gỡ Cài Đặt

```bash
# Xóa symlinks toàn máy:
rm -rf ~/.agents/skills
rm -rf ~/.claude/skills

# Xóa repo (nếu muốn):
rm -rf ~/Projects/skills
```
