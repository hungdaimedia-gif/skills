---
name: claude-task-runner
description: Tự động hoá toàn diện chu trình nhận và làm nhiệm vụ từ Claude (hoặc Tech Lead AI khác). Kích hoạt khi người dùng gõ "/goal do claude ask", "do claude ask", "nhận việc từ claude", "làm task claude giao" hoặc yêu cầu tự động xử lý task theo giao thức bàn giao máy trạng thái. Tự động kiểm tra task, nhận việc, viết code tuân thủ ranh giới tuyệt đối, chạy typecheck & build, ghi TASK_REPORT.md và bật cờ ready để đánh thức Tech Lead review.
---

# Claude Task Runner (Multi-Agent Handshake Protocol)

Skill này biến Antigravity thành một **Autonomous Worker** hoàn toàn độc lập phối hợp với **Claude (Tech Lead / Reviewer)** qua giao thức Heartbeat file-based mà không cần người dùng can thiệp thủ công.

---

## 1. Điều kiện kích hoạt (Triggers)
Kích hoạt skill này ngay khi người dùng gõ:
- `/goal do claude ask`
- `do claude ask`
- `nhận task claude` / `làm task claude giao` / `check task mới`

---

## 2. Quy trình thực thi 7 bước chuẩn (Tự động 100%)

Thực hiện lần lượt 7 bước sau trong thư mục dự án:

### Bước 1: Quét trạng thái nhiệm vụ
Chạy lệnh kiểm tra task đang được giao:
```bash
node scripts/task-status.js show
```
- Nếu `status === "ASSIGNED"`: Ghi nhận `taskId` và `title`.
- Nếu `status === "DONE"` hoặc `status === "READY_FOR_REVIEW"`: Kiểm tra thêm trong tài liệu bàn giao `HANDOFF_ANTIGRAVITY.md` xem có task mới nào chưa được assign hay không, hoặc báo cho người dùng biết hiện tại chưa có task mới.

### Bước 2: Kích hoạt nhận việc (Claim Task)
Chạy lệnh chuyển trạng thái sang `IN_PROGRESS`:
```bash
node scripts/task-status.js start <TASK_ID> "Antigravity đã nhận task, bắt đầu đọc đề và code"
```

### Bước 3: Đọc kỹ đề bài & Xác định ranh giới
1. Đọc nội dung chi tiết của task trong file bàn giao nhiệm vụ (ví dụ: `HANDOFF_ANTIGRAVITY.md`).
2. Đối chiếu **Ranh giới tuyệt đối** trong `RULES.md`:
   - Kiểm tra các đường dẫn trong danh sách đen (Blacklist Paths) tuyệt đối không được sửa.
   - Tuân thủ nguyên tắc: Không tạo nút trang trí, mọi nút bấm phải hoạt động thật.
   - Tuân thủ `CONVENTIONS.md`: Giữ file dưới 350 dòng, tách 4 tầng, đặt tên chuẩn A/HC/LC.

### Bước 4: Viết code & Cập nhật tiến độ
1. Triển khai code chính xác theo yêu cầu và contract đã thoả thuận.
2. Nếu quá trình viết code kéo dài, chạy cập nhật nhịp tim:
   ```bash
   node scripts/task-status.js progress "Đang viết component..."
   ```

### Bước 5: Kiểm tra chất lượng & Cổng ranh giới
Chạy bộ ba lệnh bắt buộc được định nghĩa trong `CLAUDE.md`:
1. `npm run typecheck` (hoặc lệnh tương đương) — phải **0 lỗi**.
2. `npm run build` — phải **0 lỗi** và tạo bundle thành công.
3. Kiểm tra cổng vùng cấm (không có diff ngoài phạm vi cho phép):
   ```bash
   git diff --stat -- <blacklist-paths>
   ```
4. Nếu có lỗi: **tự động sửa ngay tại chỗ**, chạy lại kiểm tra tới khi sạch 100%.

### Bước 6: Khai báo Build Pass & Ghi Biên Bản Bàn Giao
1. Chạy lệnh:
   ```bash
   node scripts/task-status.js build pass
   ```
2. Ghi đè file `TASK_REPORT.md` với các mục:
   - File đã đổi (`git diff --name-only`)
   - Output thực tế của typecheck và build
   - Kết quả rỗng của lệnh kiểm tra cổng vùng cấm
   - Checklist nghiệm thu (từng mục đã kiểm bằng cách nào)
   - Các điểm suy đoán / chọn phương án kỹ thuật
   - Đề nghị phần Claude làm tiếp (nếu có)

### Bước 7: Bật cờ sẵn sàng (Ready) đánh thức Claude
Chạy lệnh bàn giao chính thức:
```bash
node scripts/task-status.js ready "Xong <TASK_ID>, build sạch 0 lỗi, đã ghi TASK_REPORT.md, mời Claude review"
```
Khi lệnh này chạy xong, trạng thái đổi thành `READY_FOR_REVIEW`. Watcher `wait-task.js` của Claude sẽ tự động bắt được và đánh thức Claude tiến hành review!

Báo cáo ngắn gọn, súc tích kết quả cho người dùng.
