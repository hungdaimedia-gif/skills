---
name: design-wireframe-prototyping
description: "Phác thảo khung dây (Wireframing) và mẫu thử tương tác (Prototyping): Thiết kế kiến trúc thông tin (IA), bố cục Lo-Fi, luồng người dùng (User Journey) và kiểm chứng UX trước khi code."
provenance:
  source_repo: "VoltAgent/awesome-design-md"
  source_url: "https://github.com/VoltAgent/awesome-design-md"
  source_commit: "d3e89a1"
  imported_at: "2026-09-15T11:27:00+07:00"
  stars_at_import: 115902
  forks_at_import: 13019
---

# 📐 Design Wireframe & Prototyping — Phác Thảo Khung Dây & Mẫu Thử UX

> **Triết lý cốt lõi**: "Sửa một đường nét trên bản phác thảo chỉ tốn 1 giây, nhưng sửa một tính năng đã code xong tốn 1 tuần". Trước khi đụng vào mã nguồn hay tô màu gradient phức tạp, bắt buộc phải định hình khung xương Kiến trúc Thông tin (Information Architecture) và kiểm chứng tính hợp lý của Luồng Người Dùng (User Flow).

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Bạn chuẩn bị xây dựng một trang web, ứng dụng mới hoặc một tính năng lớn chưa có thiết kế sẵn.
2. Cần phác thảo nhanh bố cục màn hình (Dashboard, Checkout, Onboarding, Feed, Settings) dưới dạng Lo-Fi (Low Fidelity).
3. Người dùng hoặc khách hàng muốn hình dung cấu trúc trước khi lập trình viên bắt tay vào viết code.
4. Giao diện đang bị "nhồi nhét" quá nhiều thông tin, cần tổ chức lại hệ thống phân cấp hiển thị.

---

## 🗺️ BƯỚC 1: Mô Hình Hóa Kiến Trúc Thông Tin & User Flow (Information Architecture)

Trước khi vẽ màn hình, xác định rõ:
1. **Mục tiêu tối thượng của màn hình (Primary Goal)**: Người dùng vào trang này để làm đúng việc gì nhanh nhất? (Ví dụ: "Bấm nút nâng cấp", "Điền form tìm kiếm", "Đọc nhanh biểu đồ doanh thu").
2. **Luồng người dùng 3 bước (3-Step Flow)**:
   * Điểm bắt đầu (Entry point) ➔ Hành động chính (Core Action) ➔ Kết quả hoàn thành (Success state).
3. **Quy tắc phân cấp 3 mức thông tin**:
   * *Mức 1 (Must see)*: Tiêu đề lớn, dữ liệu quan trọng nhất, nút kêu gọi hành động (Call To Action - CTA).
   * *Mức 2 (Good to see)*: Mô tả chi tiết, danh sách các mục, bộ lọc phụ.
   * *Mức 3 (Optional)*: Chân trang (Footer), liên kết chính sách, thông số kỹ thuật.

---

## ✏️ BƯỚC 2: Phác Thảo Khung Dây ASCII / Markdown Lo-Fi

Sử dụng định dạng khung dây trực quan để thống nhất cấu trúc với người dùng:

```text
+-------------------------------------------------------------------------+
| [LOGO] Skills Hub          [Tìm kiếm skill...]           [🔔] [Avatar]  |
+-------------------------------------------------------------------------+
| [Banner]: Khám phá 92+ Kỹ Năng AI Kỹ Thuật              [+ Thêm Mới]    |
| ----------------------------------------------------------------------- |
| BỘ LỌC DOMAIN:                                                          |
| [Tất Cả (92)]  [Lập Trình (45)]  [Thiết Kế (15)]  [Văn Phòng (20)]      |
+-------------------------------------------------------------------------+
| +-------------------------+ +-------------------------+ +-------------+ |
| | [Icon] UI/UX Design Sys | | [Icon] SQL Optimizer    | | [Icon] ...  | |
| | ⭐ 115k stars  🍴 13k   | | ⭐ 109k stars  🍴 13k   | |             | |
| | Mô tả ngắn 2 dòng...    | | Mô tả ngắn 2 dòng...    | |             | |
| | [Xem Chi Tiết ➔]        | | [Xem Chi Tiết ➔]        | |             | |
| +-------------------------+ +-------------------------+ +-------------+ |
| [ << Trang 1 / 10 >> ]                                                  |
+-------------------------------------------------------------------------+
```

---

## 🧩 BƯỚC 3: Dựng Mẫu Thử Tương Tác Sớm (Clickable Prototype Skeleton)

Dùng HTML/CSS tối giản với màu xám (Grayscale) để tập trung 100% vào trải nghiệm và vị trí nút bấm, không bị phân tâm bởi màu mè:
* Nền: `#f1f5f9` (Light) hoặc `#0f172a` (Dark).
* Khối placeholder: Khối chữ nhật bo góc nhẹ `background: #e2e8f0`.
* Nút CTA chính: Dùng màu xám đậm nổi bật để người dùng định vị ngay điểm bấm.
* Thử nghiệm hành vi cuộn chuột (Scroll) và vị trí cố định của thanh điều hướng (Sticky Navbar).

---

## 🎯 CÂU HỎI KIỂM ĐỊNH (Checklist)
* Mắt người dùng có nhìn thấy ngay hành động quan trọng nhất (Primary CTA) trong 3 giây đầu không?
* Các khối nội dung có được phân nhóm hợp lý theo nguyên tắc gần gũi (Gestalt Proximity) không?
* Luồng di chuyển giữa các bước có liền mạch, không bị cụt hay bế tắc (Dead-end) không?
