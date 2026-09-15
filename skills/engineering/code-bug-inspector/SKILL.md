---
name: code-bug-inspector
description: Kỹ năng giúp Agent phân tích, kiểm tra và phát hiện lỗi (bug) trong mã nguồn của phần mềm hoặc công cụ, sau đó đề xuất giải pháp sửa chữa một cách có hệ thống.
---

# Kỹ năng Kiểm tra Lỗi Phần mềm (Code Bug Inspector)

Kỹ năng này cung cấp quy trình chuẩn để bạn (Agent) kiểm tra, xác minh và tìm ra lỗi trong bất kỳ hệ thống phần mềm hoặc công cụ nào. Thay vì đoán mò, hãy tuân thủ nghiêm ngặt quy trình dưới đây khi người dùng báo cáo một đoạn code chạy sai.

## 1. Thu thập thông tin (Reconnaissance)
Trước khi đưa ra kết luận, bạn phải:
- **Đọc Log Lỗi:** Yêu cầu người dùng cung cấp thông báo lỗi (StackTrace, Console Logs, Error Messages) nếu chưa có.
- **Tái hiện lỗi:** Hỏi rõ các bước để tái hiện lỗi (Steps to reproduce).
- **Kiểm tra môi trường:** Xác nhận phiên bản ngôn ngữ (Node.js, Python, v.v.) và thư viện (từ `package.json` hoặc `requirements.txt`).

## 2. Khoanh vùng mã nguồn (Isolation)
- Sử dụng các lệnh tìm kiếm (`grep_search` hoặc `view_file`) để tìm chính xác dòng code gây ra lỗi dựa trên StackTrace.
- KHÔNG đọc toàn bộ dự án nếu lỗi chỉ xuất hiện ở một hàm hoặc một module cụ thể.

## 3. Phân tích Nguyên nhân Cốt lõi (Root Cause Analysis)
Khi đã tìm thấy đoạn code khả nghi, hãy đánh giá qua 4 lăng kính:
1. **Lỗi Cú pháp / Biên dịch (Syntax/Compilation):** Thiếu dấu phẩy, sai kiểu dữ liệu, import sai đường dẫn.
2. **Lỗi Logic (Logical Errors):** Sai vòng lặp (vô hạn), sai điều kiện `if/else`, tính toán sai công thức.
3. **Lỗi Bất đồng bộ (Concurrency/Async):** Quên `await`, race conditions, deadlocks.
4. **Lỗi Trạng thái / Dữ liệu (State/Data):** Biến `null` hoặc `undefined` không được kiểm tra (NullPointerException).

## 4. Kiểm chứng và Đề xuất Giải pháp
- **Đề xuất cách fix:** Cung cấp mã nguồn sửa chữa chính xác (Diff) với giải thích rõ tại sao cách sửa này giải quyết được vấn đề cốt lõi.
- **Cách phòng ngừa:** Gợi ý cách tránh lỗi lặp lại trong tương lai (ví dụ: thêm Exception Handling, viết Unit Test, thêm kiểm tra kiểu dữ liệu).

## Nguyên tắc Vàng dành cho Agent:
- **KHÔNG đoán mò (No Guessing):** Nếu không chắc chắn, hãy dùng công cụ để chạy lệnh (như `python -m unittest` hoặc `npm test`) hoặc in thêm log (`console.log`, `print`) để kiểm chứng hành vi thực tế trước khi sửa.
- **Luôn giữ hiện trường:** Không tự ý xoá hay thay đổi diện rộng những file không liên quan trực tiếp đến lỗi.
