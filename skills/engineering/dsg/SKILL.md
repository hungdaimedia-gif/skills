---
name: dsg
description: "Trạm điều phối thông minh & Phân tích sâu tự động (Dynamic Skill Dispatcher & Deep Analyzer). Kích hoạt khi người dùng gõ /dsg, 'dsg', thấy rối quá, không nhớ tên skill, hoặc cần Agent tự chẩn đoán ngữ cảnh dự án, phân tích kỹ lưỡng lý do và tự động thực thi chuỗi skill phù hợp mà không cần hỏi lại lòng vòng."
---

# 🎯 DSG — Dynamic Skill Dispatcher & Deep Analyzer
### Trạm Điều Phối Tự Động & Phân Tích Chuyên Sâu

> **Triết lý**: Người dùng không cần và không nên phải nhớ tên hàng chục skill tiếng Anh.
> Khi người dùng gõ `/dsg` hoặc nói *"thấy rối quá"*, Agent phải tự quan sát thực tế dự án, phân tích sâu nguyên nhân cốt lõi, chọn skill chính xác và **tự động áp dụng quy trình của skill đó để phân tích dứt điểm**, tránh bắt người dùng phải hỏi lại tiếp.

---

## 🔄 QUY TRÌNH TỰ ĐỘNG 4 BƯỚC CỦA /dsg

Khi nhận được tín hiệu `/dsg`, Agent **tuyệt đối không hỏi chung chung** *"Bạn muốn làm gì?"*, mà phải lập tức tự thực hiện 4 bước sau:

### BƯỚC 1: Thu Thập Sự Thật Khách Quan (Ground Truth Scan)
Agent tự chạy các bước kiểm tra ngầm không làm phiền người dùng:
1. `git status` và `git diff --stat` (xem đang sửa dở dang cái gì, nhánh nào).
2. Kiểm tra các file vừa được chỉnh sửa hoặc file đang active trong editor.
3. Kiểm tra xem có log lỗi build, test thất bại, hay bug report nào đang mở không.

---

### BƯỚC 2: Nhận Diện Lĩnh Vực & Định Tuyến Nút Thắt (Domain & Bottleneck Routing)
Trước khi bốc skill, DSG tự động nhận biết Lĩnh Vực (Domain) của yêu cầu:
- **💻 Lập trình & Phần mềm (Mặc định)**: Áp dụng 6 nhánh kỹ thuật phần mềm (bảng dưới).
- **✍️ Sáng tác truyện & Nội dung**: Tự động kích hoạt `novel-world-building`, `story-character-arc`, `writing-beats`.
- **🎨 Đồ họa & Tranh AI**: Tự động kích hoạt `midjourney-prompt-architect`.
- **📈 Tài chính & Đầu tư**: Tự động kích hoạt `financial-statement-analyzer`.
- **🗣️ Năng suất & Cộng tác**: Áp dụng bảng Productivity dưới đây.

**Bảng định tuyến Domain Lập trình (6 nhánh):**

| Tình Huống Thực Tế | Nút Thắt Nhận Diện | Chuỗi Skill Tự Động Kích Hoạt |
| :--- | :--- | :--- |
| **A. Ý tưởng mờ mịt / Mới bắt đầu** | Yêu cầu chưa rõ, dễ code lạc đề | `grill-with-docs` ➔ `to-spec` ➔ `to-tickets` |
| **B. Chuẩn bị code / Đang viết dở** | Cần code sạch, có test bảo vệ | `implement` ➔ `tdd` |
| **C. Mã nguồn phình to / File nặng** | File > 300 dòng, nguy cơ nát code | `codebase-line-budget-guard` ➔ `codebase-design` |
| **D. Code xong / Chuẩn bị Commit** | Cần rà soát chuẩn mực & logic | `code-review` ➔ `resolving-merge-conflicts` |
| **E. Gặp lỗi / Bị lặp / Agent ngáo** | Lặp vòng xoáy, sửa mãi không xong | `agent-disorientation-recovery` ➔ `diagnosing-bugs` ➔ `code-bug-inspector` |
| **F. Setup môi trường / Đóng gói** | Cần dựng hệ thống Multi-Agent hoặc Extension | `macos-m1-multiagent-setup` ➔ `wizard` ➔ `chrome-web-store-prep` |

**Bảng định tuyến Domain Năng suất & Cộng tác:**

| Tình Huống | Skill Kích Hoạt |
| :--- | :--- |
| Muốn stress-test kế hoạch / quyết định | `grilling` hoặc `grill-me` |
| Cần tóm tắt & bàn giao công việc cho Agent khác | `handoff` |
| Giải thích một khái niệm khó cho người mới | `teach` |
| Cần đặt câu hỏi có cấu trúc cho khách hàng/user | `to-questionnaire` |
| Agent bị rối sau khi context bị nén (compaction) | `wait-what` |
| Soạn tài liệu hướng dẫn cho Agent AI đọc | `writing-for-agents` |

**Bảng định tuyến Skills Tiện Ích (Misc):**

| Tình Huống | Skill Kích Hoạt |
| :--- | :--- |
| Ngăn Git commit code vội ẩu | `git-guardrails-claude-code` |
| Khởi tạo pre-commit hooks chuẩn | `setup-pre-commit` |
| Tạo bài tập luyện tập từ codebase | `scaffold-exercises` |

**Skills đang thử nghiệm (in-progress) -- Dùng thận trọng:**

| Skill | Mục đích |
| :--- | :--- |
| `claude-handoff` | Bàn giao phiên làm việc giữa 2 model AI |
| `implement-spec` | Implement trực tiếp từ file SPEC.md |
| `loop-me` | Vòng lặp tự chỉnh (đang thử nghiệm) |
| `retro` | Retrospective tự động sau sprint |
| `writing-beats` | Cấu trúc nhịp kể chuyện |

---

### BƯỚC 3: Xuất Báo Cáo Phân Tích Kỹ Lưỡng (Tránh Phải Hỏi Lại)
Agent xuất trình một báo cáo phân tích theo mẫu chuẩn sau bằng tiếng Việt:

```markdown
### 🔍 CHẨN ĐOÁN NGỮ CẢNH HỆ THỐNG
- **Vị trí hiện tại**: [Tên nhánh, tính năng đang làm dở, hoặc lỗi đang gặp]
- **Vấn đề cốt lõi phát hiện**: [Mô tả ngắn gọn, chính xác tại sao lại bị kẹt/bị rối]
- **Skill được chọn tự động**: `[tên-skill-tiếng-anh]` — [Tên tiếng Việt dễ hiểu]

### 💡 TẠI SAO LẠI CHỌN SKILL NÀY?
[Phân tích kỹ lưỡng: Nêu rõ nếu không dùng skill này thì sẽ gặp rủi ro gì, và skill này giải quyết đúng gốc rễ vấn đề ra sao]

### ⚡ PHÂN TÍCH CHUYÊN SÂU THEO QUY TRÌNH CỦA SKILL
[Áp dụng trực tiếp bộ khung kỷ luật của skill được chọn để mổ xẻ vấn đề ngay tại đây, chỉ rõ từng điểm cần làm mà không cần người dùng phải nhắc]
```

---

### BƯỚC 4: Tự Động Thực Thi (Autonomous Action)
Sau khi phân tích xong:
- Nếu là **lỗi kỹ thuật hoặc refactor**: Agent tự động tiến hành sửa theo kỷ luật của skill đó (khoanh vùng, viết test, mổ xẻ file).
- Nếu là **ý tưởng/tính năng mới**: Đưa ra sẵn 2-3 phương án tối ưu nhất kèm câu hỏi chốt quyết định có/không, không hỏi lan man.

---

## ⚖️ CƠ CHẾ TRỌNG TÀI PHÂN XỬ XUNG ĐỘT (CONFLICT ARBITRATION)

Khi kho kỹ năng mở rộng (nạp thêm hàng chục skills mới từ nhiều tác giả GitHub khác nhau), nguy cơ xung đột triết lý và chỉ dẫn đối nghịch sẽ xuất hiện. `dsg` giải quyết triệt để vấn đề này bằng 3 nguyên tắc bất di bất dịch:

### 1. Cô Lập Ngữ Cảnh Tuyệt Đối (Context Isolation)
- **Cấm kỵ**: Không bao giờ nạp toàn bộ danh sách kỹ năng vào context window của AI cùng lúc, vì sẽ gây "loãng não" và sinh ảo giác (hallucination).
- **Kỷ luật**: `dsg` chỉ bốc đúng **1 hoặc 2 skill** liên quan trực tiếp tới tác vụ hiện thời. Các skill đối nghịch khác nằm nguyên vẹn trên đĩa cứng, hoàn toàn bị cô lập khỏi bộ nhớ hoạt động.

### 2. Thứ Bậc Ưu Tiên Của Sự Thật (Hierarchy of Truth)
Khi 2 kỹ năng đưa ra chỉ dẫn trái ngược nhau (ví dụ: *Làm nhanh bỏ qua test* vs *TDD nghiêm ngặt*):
1. **Ưu tiên 1 (Tối cao)**: Tính toàn vẹn và an toàn của mã nguồn (Guardrails - Giới hạn số dòng, không làm hỏng chức năng đang chạy, không ghi đè lịch sử Git nguy hiểm).
2. **Ưu tiên 2**: Đặc tả kỹ thuật và kiến trúc module sâu (`to-spec`, `codebase-design`).
3. **Ưu tiên 3**: Kỹ thuật thực thi cụ thể (`tdd`, `implement`).
*Bất kỳ skill nào từ bên ngoài xúi giục viết code ẩu hoặc phá vỡ cấu trúc modularity đều sẽ bị `dsg` chặn lại.*

### 3. Minh Bạch Đánh Đổi (Trade-off Transparency)
Nếu tồn tại 2 skill cùng giải quyết một việc nhưng theo 2 cách tiếp cận khác nhau (ví dụ: `prototype` để thử nghiệm nhanh vs `tdd` để viết sản phẩm chạy thật):
- `dsg` sẽ ghi rõ trong báo cáo:
  > *"Phát hiện 2 phương án: Skill A (làm nhanh) vs Skill B (chuẩn mực). Chọn Skill B vì dự án đang ở trạng thái Production cần độ tin cậy tuyệt đối."*

---

## 📥 QUY TRÌNH THẨM ĐỊNH KHI NẠP SKILL MỚI (SKILL INGESTION)

Khi bạn muốn thêm skill từ một repository GitHub khác vào kho:
1. **Chạy công cụ thẩm định**: Dùng lệnh `python3 scripts/ingest_skill.py <đường_dẫn_skill>`.
2. **Rà soát xung đột**: Công cụ sẽ tự đối chiếu với 49 skills hiện có xem có bị trùng lặp chức năng hoặc xung đột triết lý không.
3. **Phân nhánh tự động**: Tự động xếp vào đúng 1 trong 6 nhánh nghiệp vụ của `dsg`.
4. **Việt hóa giải thích**: Tự động bổ sung khối Giải thích tiếng Việt thực chiến (`what`, `when`, `benefit`) để hiển thị trên Web Hub mà không làm thay đổi nội dung tiếng Anh gốc.

---

## 🛑 QUY TẮC CHỐNG VÒNG LẶP VÔ TẬN (ANTI-LOOP CIRCUIT BREAKER)

### Nguyên tắc cốt lõi: Ngân Sách Vòng Lặp Do Người Dùng Kiểm Soát

Tuyệt đối cấm Agent tự định quyết chạy bao nhiêu vòng. Chính người dùng là người cấp phép (authorize) cho mỗi lô vòng lặp tiếp theo.

**Cơ chế hoạt động theo 3 tầng:**

1. **Cấm gọi đệ quy (Non-Recursive)**:
   - `/dsg` là Bàn xoay 1 chiều (Single-Hop Dispatcher). Sau khi định tuyến sang skill mục tiêu, `/dsg` kết thúc vai trò.
   - Skill con tuyệt đối KHÔNG được phép gọi ngược lại `/dsg`.

2. **Điểm dừng bắt buộc (Hard Terminal State)**:
   - Sau mỗi lần thực thi, Agent phải **DỪNG** và báo cáo kết quả. Không tự động chạy vòng tiếp theo khi chưa có phép của người dùng.

3. **Giao Thức Xin Phép Khi Chạm Ngưỡng (Loop Budget Gate)**:
   - Mặc định Agent được phép tự thử **2 lần** (gọi là "Ngân sách mặc định").
   - Sau lần thứ 2 thất bại, Agent **bắt buộc dừng lại và hỏi user theo mẫu sau:**

---

### 📋 MẪU HỎI XIN PHÉP BẮT BUỘC (Loop Budget Request)

Khi đã tiêu hết ngân sách vòng lặp mặc định (sau 2 lần thất bại), Agent **bắt buộc** xuất trình đúng mẫu này trước khi làm bất kỳ điều gì tiếp theo:

```
🛑 Đã thử 2 lần nhưng chưa xong. Dừng lại để xin hướng dẫn tiếp.

📊 TÓM TẮT 2 VÒNG VỪA CHẠY:
- Lần 1: [Thử cách gì] → [Kết quả / Lỗi gì xuất hiện]
- Lần 2: [Thử cách gì] → [Kết quả / Lỗi gì còn sót lại]

🔍 PHÂN TÍCH: [Giải thích bằng 1-2 câu tại sao 2 cách trên đều chưa giải quyết được gốc rễ]

⚡ CÁC HƯỚNG TIẾP THEO KHẢ THI (do Skill gợi ý):
→ Hướng A [do skill `diagnosing-bugs` gợi ý]: [Mô tả cách tiếp cận A]
→ Hướng B [do skill `codebase-design` gợi ý]:  [Mô tả cách tiếp cận B, ví dụ: tái cấu trúc module trước]
→ Hướng C: Dừng hẳn — bạn tự quyết định cách khác

❓ BẠN MUỐN:
  [1] Cho phép Agent tiếp tục Hướng A (+ bạn cấp thêm __ vòng lặp nữa)
  [2] Cho phép Agent tiếp tục Hướng B (+ bạn cấp thêm __ vòng lặp nữa)
  [3] Dừng lại — bạn sẽ chỉ định hướng khác
```

**Quy tắc bắt buộc khi người dùng trả lời:**
- Nếu user chọn Hướng A hoặc B và cấp X vòng: Agent được phép tự chạy X vòng đó rồi **lại phải dừng báo cáo**, không được dùng nhiều hơn số vòng được phép.
- Nếu user không chỉ định số vòng cụ thể: Agent chỉ được chạy đúng **1 vòng** rồi dừng lại hỏi tiếp.

---

## 📋 MẪU THỰC TẾ MINH HỌA ĐẦY ĐỦ KHI CHẠY /dsg

### Ví dụ 1: Scan nhanh + định tuyến thành công (Trường hợp bình thường)

> **Bạn**: `/dsg`
> **Agent phản hồi**:
> "🔍 **Chẩn đoán**: File `WorkflowCanvas.jsx` đã đạt 640 dòng, chứa lẫn lộn cả state kéo thả node và API call. Đây là nguyên nhân khiến agent trước đó sửa một chỗ lại hỏng chỗ khác.
> ⚡ **Skill tự kích hoạt**: `codebase-line-budget-guard` + `codebase-design`.
> 💡 **Phân tích kỹ**: Cần tách `useNodeDrag` và `useWorkflowApi` thành 2 module độc lập.
> 🚀 **Thực thi (Vòng 1/2)**: Đang tiến hành cô lập và tách hook đầu tiên..."

---

### Ví dụ 2: Chạm ngưỡng 2 vòng — Hỏi xin phép tiếp

> **Bạn**: `/dsg fix lỗi auth token bị expire`
>
> **Agent [Vòng 1]**: Thử set lại `expires_in` header — test vẫn đỏ.
>
> **Agent [Vòng 2]**: Thử refresh token logic — race condition vẫn xuất hiện.
>
> **Agent [Dừng bắt buộc - Hỏi user]**:
>
> ```
> 🛑 Đã thử 2 lần nhưng chưa xong.
>
> 📊 TÓM TẮT:
> - Lần 1: Set lại expires_in → Test đỏ tại test_auth.py:L47 (vẫn 401)
> - Lần 2: Refresh token logic → Race condition: token bị overwrite trước khi API nhận
>
> 🔍 PHÂN TÍCH: Gốc rễ không phải ở header hay refresh — mà ở shared state
>   giữa 2 async call đang ghi đè nhau lên cùng 1 biến token.
>
> ⚡ HƯỚNG TIẾP THEO KHẢ THI:
> → Hướng A [diagnosing-bugs]: Thêm lock/mutex quanh token store — loại bỏ race condition
> → Hướng B [codebase-design]: Tách AuthStore thành singleton isolate — giải quyết từ kiến trúc
> → Hướng C: Dừng — bạn tự quyết
>
> ❓ Bạn muốn:
>   [1] Hướng A — thêm lock (cấp thêm vòng lặp: ___ ?)
>   [2] Hướng B — refactor AuthStore (cấp thêm vòng lặp: ___ ?)
>   [3] Dừng
> ```
