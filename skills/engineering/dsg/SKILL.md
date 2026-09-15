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

## 📋 MẪU THỰC TẾ MINH HOẠ KHI CHẠY /dsg

### Ví dụ: Khi bạn sửa file dài 600 dòng và bắt đầu thấy rối
> **Bạn**: `/dsg`  
> **Agent phản hồi**:  
> "🔍 **Chẩn đoán**: File `WorkflowCanvas.jsx` đã đạt 640 dòng, chứa lẫn lộn cả state kéo thả node và API call. Đây là nguyên nhân khiến agent trước đó sửa một chỗ lại hỏng chỗ khác.  
> ⚡ **Skill tự kích hoạt**: `codebase-line-budget-guard` + `codebase-design` (Bảo vệ ngân sách dòng & Thiết kế Deep Module).  
> 💡 **Phân tích kỹ**: Cần phải tách `useNodeDrag` và `useWorkflowApi` thành 2 module độc lập trước khi thêm tính năng mới, nếu không file sẽ vượt ngưỡng 1,000 dòng và tê liệt.  
> 🚀 **Thực thi ngay**: Tôi đang tiến hành cô lập và tách hook đầu tiên..."
