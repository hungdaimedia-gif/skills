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

### BƯỚC 2: Chẩn Đoán & Định Tuyến Nút Thắt (Bottleneck Diagnosis)
Phân loại chính xác tình trạng dự án vào 1 trong 5 tình huống:

| Tình Huống Thực Tế | Nút Thắt Nhận Diện | Chuỗi Skill Tự Động Kích Hoạt |
| :--- | :--- | :--- |
| **A. Ý tưởng mờ mịt / Mới bắt đầu** | Yêu cầu chưa rõ, dễ code lạc đề | `grill-with-docs` ➔ `to-spec` ➔ `to-tickets` |
| **B. Chuẩn bị code / Đang viết dở** | Cần code sạch, có test bảo vệ | `implement` ➔ `tdd` |
| **C. Mã nguồn phình to / File nặng** | File > 300 dòng, nguy cơ nát code | `codebase-line-budget-guard` ➔ `codebase-design` |
| **D. Code xong / Chuẩn bị Commit** | Cần rà soát chuẩn mực & logic | `code-review` ➔ `resolving-merge-conflicts` |
| **E. Gặp lỗi / Bị lặp / Agent ngáo** | Lặp vòng xoáy, sửa mãi không xong | `agent-disorientation-recovery` ➔ `diagnosing-bugs` ➔ `code-bug-inspector` |

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

## 📋 MẪU THỰC TẾ MINH HOẠ KHI CHẠY /dsg

### Ví dụ: Khi bạn sửa file dài 600 dòng và bắt đầu thấy rối
> **Bạn**: `/dsg`  
> **Agent phản hồi**:  
> "🔍 **Chẩn đoán**: File `WorkflowCanvas.jsx` đã đạt 640 dòng, chứa lẫn lộn cả state kéo thả node và API call. Đây là nguyên nhân khiến agent trước đó sửa một chỗ lại hỏng chỗ khác.  
> ⚡ **Skill tự kích hoạt**: `codebase-line-budget-guard` + `codebase-design` (Bảo vệ ngân sách dòng & Thiết kế Deep Module).  
> 💡 **Phân tích kỹ**: Cần phải tách `useNodeDrag` và `useWorkflowApi` thành 2 module độc lập trước khi thêm tính năng mới, nếu không file sẽ vượt ngưỡng 1,000 dòng và tê liệt.  
> 🚀 **Thực thi ngay**: Tôi đang tiến hành cô lập và tách hook đầu tiên..."
