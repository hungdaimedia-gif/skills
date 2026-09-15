# 📜 BẢN GHI NHẬN THAY ĐỔI TOÀN DIỆN VỀ SKILLS (SKILLS CHANGELOG)
*Thời gian cập nhật: 15/09/2026 • Quản trị bởi: DSG (Dynamic Skill Dispatcher)*

---

## 🎯 TỔNG QUAN THAY ĐỔI CỐT LÕI
Hệ thống skills đã được nâng cấp toàn diện từ trạng thái **rời rạc, thủ công** thành **một cỗ máy tự vận hành 49 skills đồng bộ 2 chiều**, có giao diện Web trực quan và trạm điều phối tự động `/dsg`.

---

## 1. ĐỒNG BỘ 2 CHIỀU GIỮA 2 KHO DỰ ÁN
* **Kho nguồn 1**: `git@github.com:hungdaimedia-gif/idea-agent-loop-blueprint.git`
* **Kho nguồn 2**: `git@github.com:hungdaimedia-gif/skills.git` (đã clone về `~/Projects/skills`)

### Chiều đi (Từ Blueprint sang Skills Repo):
Đã chuyển thành công **11 skills thực chiến** vào thư mục `skills/engineering/`:
1. `agent-disorientation-recovery`: Cứu hộ khi agent mất phương hướng, looping.
2. `chrome-web-store-prep`: Chuẩn hóa manifest, asset và policy nộp Chrome Web Store.
3. `claude-task-runner`: Điều phối và chạy task tự động tuân thủ ranh giới.
4. `code-bug-inspector`: Thanh tra mã lỗi tĩnh bằng AST Python (`bug_inspector.py`).
5. `codebase-line-budget-guard`: Giám sát giới hạn dòng code (< 300-500 dòng/file).
6. `fullstack-boilerplate-architect`: Dựng khung kiến trúc chuẩn mực fullstack.
7. `macos-m1-multiagent-setup`: Cài đặt Multi-Agent tối ưu cho Mac Apple Silicon.
8. `multiagent-setup-crossplatform`: Cài đặt Multi-Agent tương thích macOS, Linux, Windows.
9. `project-blueprint-loop-architect`: Bản vẽ kiến trúc vòng lặp agent loop.
10. `system-logs-and-diagnostics`: Nhật ký hệ thống & Chẩn đoán từ xa.
11. `workflow-node-studio`: Thiết kế Custom Node canvas với React Flow (@xyflow/react).

### Chiều về (Từ Skills Repo sang Blueprint & Toàn hệ thống):
Đã sao chép toàn bộ các skills từ `skills.git` về dự án `idea-agent-loop-blueprint` (nâng tổng số lên **49 skills** trong `.agents/skills/`), đồng thời chạy `link-skills.sh` symlink tự động tới:
- `~/.claude/skills` (Claude Code)
- `~/.agents/skills` (Codex / Antigravity / Agent CLI)

---

## 2. RA ĐỜI SIÊU KỸ NĂNG ĐIỀU PHỐI: `/dsg`
* **Tên**: `dsg` (Dynamic Skill Dispatcher & Autonomous Deep Analyzer).
* **Vị trí**: `skills/engineering/dsg/SKILL.md`.
* **Mục tiêu**: Người dùng **không cần nhớ bất kỳ tên tiếng Anh nào** của 49 skills. Chỉ cần gõ `/dsg`.
* **Cơ chế hoạt động**:
  1. **Tự quét sự thật ngầm**: Đọc `git status`, `git diff`, file đang mở, log terminal.
  2. **Bắt đúng bệnh**: Tự phát hiện vấn đề (Ý tưởng mờ mịt, file quá dài, lỗi logic, agent ngáo).
  3. **Tự động xâu chuỗi (Chaining)**: Gọi nối tiếp các skill liên quan (ví dụ: `diagnosing-bugs` ➔ `code-bug-inspector` ➔ `tdd`).
  4. **Triệt tiêu câu hỏi thừa**: Báo cáo phân tích kỹ lý do bằng tiếng Việt và hành động dứt điểm.
  5. **Cơ chế Trọng tài phân xử xung đột**:
     - *Cô lập ngữ cảnh*: Chỉ bốc 1-2 skill cần thiết, không nạp cả đống làm loãng não AI.
     - *Thứ bậc ưu tiên*: Luật an toàn dự án luôn đứng trên các skill xúi code ẩu.
     - *Minh bạch đánh đổi*: Nêu rõ ưu/nhược điểm khi có 2 cách giải quyết.

---

## 3. TÁI CẤU TRÚC DANH MỤC: CÂY PHÂN NHÁNH 6 NHÁNH THỰC CHIẾN
Thay thế cách phân loại thư mục phẳng cũ (`engineering`, `productivity`...) bằng 6 nhánh theo tâm lý làm việc thực tế:

| Nhánh | Số lượng | Các skills tiêu biểu |
| :--- | :---: | :--- |
| 💡 **1. Ý tưởng & Đặc tả** | 12 skills | `dsg`, `ask-matt`, `grill-with-docs`, `to-spec`, `to-tickets`, `wayfinder`, `domain-modeling`... |
| 🏗️ **2. Kiến trúc & Thiết kế** | 6 skills | `codebase-design`, `fullstack-boilerplate-architect`, `workflow-node-studio`, `prototype`... |
| ⚡ **3. Viết Code & TDD** | 10 skills | `implement`, `tdd`, `claude-task-runner`, `loop-me`, `teach`, `writing-for-agents`... |
| 🛡️ **4. Kiểm soát & Review** | 8 skills | `codebase-line-budget-guard`, `code-review`, `resolving-merge-conflicts`, `git-guardrails`... |
| 🩺 **5. Cứu hộ & Gỡ lỗi** | 6 skills | `agent-disorientation-recovery`, `code-bug-inspector`, `diagnosing-bugs`, `system-logs`... |
| 🚀 **6. Nền tảng & Vận hành** | 7 skills | `macos-m1-multiagent-setup`, `multiagent-setup-crossplatform`, `chrome-web-store-prep`, `wizard`... |

---

## 4. ỨNG DỤNG WEB HUB TƯƠNG TÁC (SKILLS HUB)
* **Đường dẫn**: Thư mục `web/` (đang host tại `http://localhost:3333`).
* **Đặc điểm nổi bật**:
  - **Giữ nguyên 100% tiếng Anh gốc**: Không phá vỡ quy chuẩn kỹ thuật của tác giả gốc.
  - **Bổ sung Giải Thích Tiếng Việt Thực Chiến**: Mỗi thẻ skill và bảng chi tiết (drawer) đều có khối `Bản chất là gì`, `Khi nào nên dùng`, `Lợi ích mang lại`.
  - **Bản đồ quy trình tương tác**: Click vào từng bước để xem combo skill khuyên dùng.
  - **Bộ trắc nghiệm tình huống**: Click tình huống hay gặp để nhận ngay prompt chuẩn.
  - **Bộ lọc theo 6 nhánh**: Lọc nhanh chóng theo từng nhánh nghiệp vụ.

---

## 5. HỆ THỐNG CÔNG CỤ TỰ ĐỘNG HÓA (SCRIPTS)
1. [`scripts/build_web_data.py`](file:///Users/macos/Projects/skills/scripts/build_web_data.py): Tự động quét toàn bộ kho skills, phân nhánh và tạo file dữ liệu `web/skills-data.js` kèm từ điển tiếng Việt.
2. [`scripts/ingest_skill.py`](file:///Users/macos/Projects/skills/scripts/ingest_skill.py): Động cơ nạp skill mới từ GitHub về, tự động kiểm tra xung đột va chạm và xếp nhánh.
3. [`scripts/link-skills.sh`](file:///Users/macos/Projects/skills/scripts/link-skills.sh): Tự động tạo symlink vào hệ thống máy.

---

## 📌 HƯỚNG DẪN SỬ DỤNG NHANH CHO BẠN
1. **Khi làm việc hàng ngày**: Chỉ cần gõ `/dsg` hoặc `/dsg [vấn đề]` để AI tự chẩn đoán và chạy skill thích hợp.
2. **Khi muốn nạp thêm skill từ GitHub**: Gõ `/dsg phân tích skill của git [link/thư mục] và mang về`.
3. **Khi muốn tra cứu trực quan**: Mở trình duyệt tại `http://localhost:3333`.
