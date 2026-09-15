# 🧠 AI Skills Hub — Đa Lĩnh Vực & Tự Động Hóa Chất Lượng Cao

[![CI Tests](https://github.com/hungdaimedia-gif/skills/actions/workflows/test.yml/badge.svg)](https://github.com/hungdaimedia-gif/skills/actions/workflows/test.yml)
[![Skills Count](https://img.shields.io/badge/skills-53%2B-blue.svg)](https://github.com/hungdaimedia-gif/skills)
[![Quality Gate](https://img.shields.io/badge/Quality%20Gate-5%20Gates%20%7C%20%E2%89%A570pts-success.svg)](./SKILL_STANDARDS.md)
[![Profiles](https://img.shields.io/badge/Multi--Project-Profiles-orange.svg)](./profiles/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

Kho kỹ năng (Skills) toàn diện cho AI Coding Agent & Nhà sáng tạo nội dung — Bao gồm **53+ skills** qua 5 lĩnh vực (**Lập trình**, **Sáng tác**, **Tranh AI**, **Tài chính**, **Năng suất**), tích hợp **Dispatcher thông minh `/dsg`**, **Pipeline tự động nạp từ GitHub**, và **Hệ thống Profile đa dự án**.

> Tương thích hoàn hảo với: **Antigravity IDE**, **Claude Code**, **Cursor**, **Codex**, **OpenCode**, và các Agent theo chuẩn Markdown `SKILL.md`.

---

## ⚡ Cài Đặt Nhanh Trong 30 Giây

Xem tài liệu cài đặt chi tiết từng bước: [📖 Hướng Dẫn Cài Đặt (INSTALL.md)](./INSTALL.md)

### 1. Cài đặt toàn bộ máy (Dùng cho mọi dự án)
```bash
# Clone kho kỹ năng về máy
git clone git@github.com:hungdaimedia-gif/skills.git ~/Projects/skills

# Tạo liên kết symlink vào ~/.agents/skills (Agent tự động nhận diện)
bash ~/Projects/skills/scripts/link-skills.sh

# Mở Web Hub giao diện đồ họa tra cứu trực quan
python3 -m http.server 3333 --directory ~/Projects/skills/web &
open http://localhost:3333
```

### 2. Kích hoạt trong phiên trò chuyện của Agent
Sau khi cài đặt, bạn chỉ cần gõ lệnh trong bất kỳ thư mục dự án nào:
* **`/dsg`** — *Trạm điều phối thông minh*: Agent tự chẩn đoán ngữ cảnh dự án và tự chạy chuỗi skill tương ứng (không cần nhớ tên tiếng Anh).
* **`/tdd`** — Thực hiện chu trình Test-Driven Development (Đỏ → Xanh → Tối ưu).
* **`/code-review`** — Rà soát code 2 trục (Tiêu chuẩn repo + Yêu cầu bài toán) trước khi commit.
* **`/grill-with-docs`** — Phỏng vấn làm rõ ý tưởng, cập nhật `CONTEXT.md` và ADR kiến trúc.

---

## 🌟 Điểm Nhấn Công Nghệ

### 1. 🧠 Trạm Điều Phối Thông Minh `/dsg`
Không cần phải nhớ hàng chục lệnh tiếng Anh. Gõ `/dsg` hoặc `dsg`, hệ thống sẽ:
1. Quét cấu trúc dự án và lịch sử trao đổi.
2. Tự động xác định bạn đang ở giai đoạn nào (*Khởi tạo*, *Lập trình*, *Gỡ lỗi*, hay *Tái cấu trúc*).
3. Đề xuất và kích hoạt chuỗi kỹ năng tối ưu nhất.

### 2. 🔬 Pipeline Tự Động & 5 Cổng Kiểm Tra Chất Lượng (Quality Gates)
Tự động nạp skills từ các GitHub repo khác vào kho mà **không lo bị rác, trùng lặp hoặc phá hỏng repo**:

```
GitHub Repo ──► Clone Cache ──► Quét SKILL.md ──► 5 Quality Gates (≥70đ) ──► Phân loại Domain ──► Auto Rebuild Hub
```

| Cổng (Gate) | Tiêu chuẩn kiểm tra | Điểm tối đa |
|:---|:---|:---:|
| **Gate 1: Structure** | Frontmatter hợp lệ (`name:`, `description:` 20–200 ký tự), tên chuẩn slug `[a-z0-9-]` | 20đ |
| **Gate 2: Substance** | Dung lượng ≥ 150 từ, đầy đủ mục tiêu (*Khi nào dùng*, *Mục đích*, *Các bước*) | 30đ |
| **Gate 3: Novelty** | So khớp với tất cả skills hiện có; từ chối nếu mô tả trùng lặp > 80% | 20đ |
| **Gate 4: Domain Fit** | Phân loại chính xác vào domain: `engineering`, `writing`, `art`, `finance`, `productivity` | 15đ |
| **Gate 5: Safety** | Không chứa hành vi nguy hiểm (`git push --force`, `skip tests`, `bỏ qua review`...) | 15đ |

> 💡 **Actionable Feedback Loop**: Nếu skill bị từ chối (< 70đ), pipeline tự động in ra hướng dẫn chi tiết từng dòng cần sửa để bạn hoàn thiện ngay.  
> Chi tiết tiêu chuẩn: [SKILL_STANDARDS.md](./SKILL_STANDARDS.md)

### 3. 🎯 Hệ Thống Profile Đa Dự Án (`profiles/`)
Mỗi dự án có thể có nhu cầu sử dụng skill khác nhau. Bạn có thể định cấu hình riêng biệt:
```bash
# Liệt kê các profile có sẵn
python3 scripts/auto_get_skills.py --list-profiles

# Chạy nạp theo profile của hungdaitool
python3 scripts/auto_get_skills.py --profile hungdaitool

# Chạy thử nghiệm xem trước (không sửa file)
python3 scripts/auto_get_skills.py --dry-run
```
* [hungdaitool.yml](./profiles/hungdaitool.yml): Profile chính cho công việc lập trình, sáng tác và tài chính.
* [template.yml](./profiles/template.yml): Bản mẫu để bạn tự tạo profile cho dự án mới của riêng mình.

### 4. 🌐 Web Hub Tra Cứu Trực Quan (`localhost:3333`)
Giao diện Web Hub tích hợp sẵn giúp bạn:
- Tìm kiếm nhanh toàn văn theo tên, mục đích và nội dung skill.
- Lọc theo từng nhánh làm việc (*Ý tưởng*, *Kiến trúc*, *Viết Code*, *Gỡ lỗi*, *Vận hành*...).
- Xem nhanh cheatsheet và nút 1-click sao chép prompt cho Agent.

---

## 📚 Danh Mục Kỹ Năng (53+ Skills)

### 💻 1. Engineering (Lập Trình & Kỹ Thuật Hệ Thống)

| Kỹ năng | Cách gọi | Mục đích & Quy trình |
|:---|:---:|:---|
| **[dsg](./skills/engineering/dsg/SKILL.md)** | Model/User | **Trạm điều phối thông minh**: Tự chẩn đoán ngữ cảnh dự án & chạy chuỗi skill phù hợp |
| **[tdd](./skills/engineering/tdd/SKILL.md)** | Model/User | Phát triển hướng kiểm thử (Red → Green → Refactor) từng lát cắt tính năng |
| **[code-review](./skills/engineering/code-review/SKILL.md)** | Model/User | Rà soát diff 2 trục song song: Chuẩn mực code (Standards) & Đúng đặc tả (Spec) |
| **[diagnosing-bugs](./skills/engineering/diagnosing-bugs/SKILL.md)** | Model/User | Quy trình chẩn đoán bug khó: Tái hiện lỗi đỏ → Giảm thiểu → Giả thuyết → Sửa → Kiểm tra lại |
| **[agent-disorientation-recovery](./skills/engineering/agent-disorientation-recovery/SKILL.md)** | Model/User | Cứu hộ Agent khi bị quá tải, mất ngữ cảnh sau compaction hoặc lặp lỗi |
| **[claude-task-runner](./skills/engineering/claude-task-runner/SKILL.md)** | Model/User | Vòng lặp nhận và thực thi tự động các nhiệm vụ từ Tech Lead AI |
| **[workflow-node-studio](./skills/engineering/workflow-node-studio/SKILL.md)** | Model/User | Thiết kế giao diện Studio canvas và viết Custom Node React Flow (@xyflow/react) |
| **[chrome-web-store-prep](./skills/engineering/chrome-web-store-prep/SKILL.md)** | Model/User | Chuẩn hoá Chrome Extension MV3, rà soát quyền hạn và chuẩn bị hồ sơ upload Web Store |
| **[macos-m1-multiagent-setup](./skills/engineering/macos-m1-multiagent-setup/SKILL.md)** | Model/User | Thiết lập hệ thống Multi-Agent AI (CrewAI + OpenRouter) trên MacBook M1 macOS |
| **[multiagent-setup-crossplatform](./skills/engineering/multiagent-setup-crossplatform/SKILL.md)** | Model/User | Cài đặt và vận hành hệ thống Multi-Agent trên macOS, Linux và Windows |
| **[code-bug-inspector](./skills/engineering/code-bug-inspector/SKILL.md)** | Model/User | Tự động phân tích, phát hiện lỗi cú pháp, type, import và đề xuất giải pháp sửa chữa |
| **[codebase-design](./skills/engineering/codebase-design/SKILL.md)** | Model/User | Thiết kế module sâu (Deep Module): giao diện nhỏ gọn, xử lý mạnh mẽ bên dưới |
| **[domain-modeling](./skills/engineering/domain-modeling/SKILL.md)** | Model/User | Xây dựng và chuẩn hoá mô hình domain, cập nhật `CONTEXT.md` và Architecture Decision Records |
| **[grill-with-docs](./skills/engineering/grill-with-docs/SKILL.md)** | User | Phỏng vấn làm rõ yêu cầu kết hợp xây dựng từ vựng domain và ghi chép tài liệu kỹ thuật |
| **[implement](./skills/engineering/implement/SKILL.md)** | User | Hiện thực hoá công việc từ spec/tickets, kết hợp TDD và rà soát code trước commit |
| **[improve-codebase-architecture](./skills/engineering/improve-codebase-architecture/SKILL.md)** | User | Quét toàn bộ codebase tìm điểm nghẽn kiến trúc và xuất báo cáo HTML trực quan |
| **[prototype](./skills/engineering/prototype/SKILL.md)** | Model/User | Xây dựng bản mẫu nhanh (Throwaway Prototype) kiểm chứng logic hoặc phương án giao diện |
| **[research](./skills/engineering/research/SKILL.md)** | Model/User | Nghiên cứu vấn đề kỹ thuật từ nguồn tin cậy và lưu báo cáo markdown trích dẫn đầy đủ |
| **[resolving-merge-conflicts](./skills/engineering/resolving-merge-conflicts/SKILL.md)** | Model/User | Xử lý xung đột git merge/rebase từng khối dựa trên chủ đích gốc, không dùng `--abort` |
| **[system-logs-and-diagnostics](./skills/engineering/system-logs-and-diagnostics/SKILL.md)** | Model/User | Xây dựng hệ thống chẩn đoán từ xa và xử lý lỗi log cho Chrome Extension |
| **[to-spec](./skills/engineering/to-spec/SKILL.md)** | User | Tổng hợp nội dung cuộc trò chuyện thành bản đặc tả kỹ thuật (Spec) hoàn chỉnh |
| **[to-tickets](./skills/engineering/to-tickets/SKILL.md)** | User | Chia nhỏ kế hoạch thành các ticket rõ ràng với thứ tự phụ thuộc |
| **[triage](./skills/engineering/triage/SKILL.md)** | User | Phân loại và điều phối issues qua máy trạng thái phân vai |
| **[wayfinder](./skills/engineering/wayfinder/SKILL.md)** | User | Lập bản đồ các quyết định lớn cho khối lượng công việc vượt quá một phiên chat |
| **[wizard](./skills/engineering/wizard/SKILL.md)** | Model/User | Sinh script bash tương tác từng bước hướng dẫn người dùng làm việc thủ công |
| **[codebase-line-budget-guard](./skills/engineering/codebase-line-budget-guard/SKILL.md)** | Model/User | Giám sát và kiểm soát giới hạn dòng code, đảm bảo tính mô-đun hoá |
| **[fullstack-boilerplate-architect](./skills/engineering/fullstack-boilerplate-architect/SKILL.md)** | Model/User | Thiết kế khung sườn (boilerplate) fullstack chuẩn mực, sẵn sàng cho sản phẩm thực tế |
| **[project-blueprint-loop-architect](./skills/engineering/project-blueprint-loop-architect/SKILL.md)** | Model/User | Thiết kế blueprint vòng lặp dự án và chu kỳ lặp lại của Agent |
| **[setup-matt-pocock-skills](./skills/engineering/setup-matt-pocock-skills/SKILL.md)** | User | Khởi tạo cấu hình issue tracker, labels và thư mục docs cho repo |
| **[ask-matt](./skills/engineering/ask-matt/SKILL.md)** | User | Bộ định tuyến hỏi đáp gợi ý skill kỹ thuật phù hợp với tình huống |

---

### ✍️ 2. Writing (Sáng Tác & Xây Dựng Cốt Truyện)

* **[novel-world-building](./skills/writing/novel-world-building/SKILL.md)**: Thiết kế thế giới, bối cảnh, hệ thống quy tắc (magic/sci-fi system) và chiều sâu lịch sử cho tác phẩm.
* **[story-character-arc](./skills/writing/story-character-arc/SKILL.md)**: Xây dựng tâm lý nhân vật, động lực nội tâm (Lie vs Truth), xung đột và hành trình biến đổi sâu sắc.
* **[writing-beats](./skills/in-progress/writing-beats/SKILL.md)**: Phát triển và sắp xếp các nhịp truyện (story beats) theo cao trào cấu trúc.
* **[writing-fragments](./skills/in-progress/writing-fragments/SKILL.md)**: Chắp nối các phân cảnh, ý tưởng vụn vặt thành trường đoạn thống nhất.
* **[writing-shape](./skills/in-progress/writing-shape/SKILL.md)**: Định hình cấu trúc tổng thể và nhịp điệu của toàn bộ tác phẩm.

---

### 🎨 3. Art (Nghệ Thuật Thị Giác & Prompt Kỹ Thuật)

* **[midjourney-prompt-architect](./skills/art/midjourney-prompt-architect/SKILL.md)**: Kiến trúc sư prompt chuyên sâu cho Midjourney v6, Flux.1 và Stable Diffusion: kiểm soát góc máy, ánh sáng, chất liệu, màu sắc và tham số kỹ thuật render.

---

### 📊 4. Finance (Phân Tích Tài Chính & Dòng Tiền)

* **[financial-statement-analyzer](./skills/finance/financial-statement-analyzer/SKILL.md)**: Bóc tách và phân tích chuyên sâu 3 báo cáo tài chính (Bảng CĐKT, Báo cáo KQKD, Báo cáo LCTT): đo lường sức khỏe dòng tiền, chất lượng lợi nhuận và phát hiện rủi ro kế toán.

---

### ⚡ 5. Productivity (Năng Suất & Tương Tác Cùng Agent)

* **[grill-me](./skills/productivity/grill-me/SKILL.md)**: Yêu cầu AI phỏng vấn dồn dập về một kế hoạch, ý tưởng phi kỹ thuật cho đến khi thông suốt.
* **[grilling](./skills/productivity/grilling/SKILL.md)**: Lõi phỏng vấn truy vấn chuyên sâu dùng làm nền tảng cho các skill định hình ý tưởng.
* **[handoff](./skills/productivity/handoff/SKILL.md)**: Đóng gói cô đọng toàn bộ ngữ cảnh phiên làm việc để chuyển giao mượt mà sang Agent khác.
* **[teach](./skills/productivity/teach/SKILL.md)**: Hướng dẫn người dùng học kỹ năng hoặc khái niệm mới qua không gian thực hành trực quan.
* **[to-questionnaire](./skills/productivity/to-questionnaire/SKILL.md)**: Biến một quyết định nan giải thành bảng câu hỏi khảo sát ngắn gọn, trúng đích.
* **[wait-what](./skills/productivity/wait-what/SKILL.md)**: Kích hoạt khi lời giải thích của AI khó hiểu — yêu cầu AI giải thích lại bằng ví dụ đời thường.
* **[writing-for-agents](./skills/productivity/writing-for-agents/SKILL.md)**: Quy chuẩn viết tài liệu cho AI Agent (skills, AGENTS.md, CLAUDE.md).

---

## 🛠️ Công Cụ Quản Lý & Tự Động Hóa

* **[scripts/auto_get_skills.py](./scripts/auto_get_skills.py)**: Bộ máy tự động săn tìm (`--discover`), kiểm định uy tín Gate 0 (Stars ≥ 10,000, Forks ≥ 500), quét bảo mật sâu `scripts/` (Gate 5), tự động ghi nhận nguồn gốc GitHub (`provenance`) vào `SKILL.md` và lưu vết lịch sử nạp (`--history`).
* **[scripts/track_usage.py](./scripts/track_usage.py)**: Theo dõi, ghi nhận và thống kê tần suất sử dụng skills của các AI Agent (Claude, Antigravity, Cursor...) trong toàn dự án.
* **[scripts/link-skills.sh](./scripts/link-skills.sh)**: Script tạo liên kết symlink vào `~/.agents/skills` và `~/.claude/skills`.
* **[scripts/build_web_data.py](./scripts/build_web_data.py)**: Trình tạo dữ liệu tự động cho Web Hub.
* **[tests/test_pipeline.py](./tests/test_pipeline.py)**: Bộ kiểm thử tự động (55 unit tests) bảo vệ pipeline, sandbox mã độc và tính toàn vẹn hệ thống.

---

## 🤝 Đóng Góp Kỹ Năng Mới

Mọi đóng góp kỹ năng mới đều được chào đón! Trước khi gửi Pull Request, vui lòng tham khảo:
- [Hướng dẫn Đóng góp (CONTRIBUTING.md)](./CONTRIBUTING.md)
- [Quy chuẩn 6 Quality Gates (SKILL_STANDARDS.md)](./SKILL_STANDARDS.md)

Chạy kiểm thử trước khi commit:
```bash
python3 tests/test_pipeline.py
```

---

## 📄 Bản Quyền & Cảm Ơn

* Mã nguồn phát hành dưới giấy phép [MIT License](./LICENSE).
* Khởi nguồn ý tưởng từ kho kỹ năng kỹ thuật của [Matt Pocock](https://github.com/mattpocock/skills) và được mở rộng thành hệ thống quản lý kỹ năng đa lĩnh vực bởi **hungdaimedia-gif**.
