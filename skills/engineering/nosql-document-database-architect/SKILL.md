---
name: nosql-document-database-architect
description: "Thiết kế cơ sở dữ liệu NoSQL & Document Store (MongoDB, DynamoDB): Quy chuẩn Embedding vs Referencing, chống lỗi Unbounded Array, Partition Key và tối ưu hóa chi phí đọc/ghi."
provenance:
  source_repo: "PatrickJS/awesome-cursorrules"
  source_url: "https://github.com/PatrickJS/awesome-cursorrules"
  source_commit: "f82b1c4"
  imported_at: "2026-09-15T11:30:00+07:00"
  stars_at_import: 40786
  forks_at_import: 3484
---

# 🍃 NoSQL & Document Database Architect — Mô Hình Hóa Dữ Liệu NoSQL

> **Triết lý cốt lõi**: Trong thế giới cơ sở dữ liệu quan hệ (RDBMS), bạn thiết kế dữ liệu dựa trên **Mối quan hệ thực thể (Data Relationships)**. Nhưng trong NoSQL (MongoDB, DynamoDB), bạn bắt buộc phải thiết kế cấu trúc dữ liệu dựa trên **Mẫu truy vấn của người dùng (Access Patterns & Query-Driven Design)**.

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Dự án sử dụng **MongoDB**, **AWS DynamoDB**, **Google Firestore** hoặc **Couchbase**.
2. Dữ liệu có cấu trúc linh hoạt, thường xuyên thay đổi (Catalogs sản phẩm E-commerce, Log sự kiện, Lịch sử hội thoại AI chat, IoT Sensor data).
3. Đang phân vân giữa: **Nhúng dữ liệu con vào trong Document (Embedding)** hay **Lưu bảng riêng rồi trỏ ID (Referencing)**.
4. Document trong MongoDB phình to vượt quá giới hạn cứng 16MB (Lỗi Unbounded Array).

---

## ⚖️ BƯỚC 1: Quy Tắc Vàng — Embedding (Nhúng) vs Referencing (Tham Chiếu)

### 1. Khi nào nên DÙNG EMBEDDING (Nhúng trực tiếp vào trong Document)?
* **Quan hệ 1 - Ít (One-to-Few)**: Số lượng phần tử con cố định hoặc rất ít (ví dụ: Địa chỉ giao hàng của User - tối đa 3-5 địa chỉ).
* **Dữ liệu luôn được đọc cùng nhau**: Khi lấy thông tin Đơn hàng, luôn cần hiển thị danh sách các món hàng (Order Items).
* **Ưu điểm**: 1 câu lệnh đọc duy nhất, không cần JOIN, tốc độ đọc siêu nhanh.

```json
// Ví dụ Embedding tốt:
{
  "_id": "order_123",
  "customer_id": "user_456",
  "total_amount": 540000,
  "items": [
    { "sku": "SHOE-01", "name": "Giày thể thao", "price": 500000, "quantity": 1 },
    { "sku": "SOCK-02", "name": "Vớ cotton", "price": 40000, "quantity": 1 }
  ]
}
```

### 2. Khi nào BẮT BUỘC DÙNG REFERENCING (Tham chiếu ID)?
* **Quan hệ 1 - Vô số (One-to-Squillions)**: Số lượng phần tử con có thể tăng vô hạn theo thời gian (ví dụ: Bình luận của bài viết, Lịch sử thao tác log của hệ thống).
* **Dữ liệu được cập nhật độc lập thường xuyên**: Tránh việc phải ghi khóa toàn bộ Document lớn chỉ để cập nhật một trường nhỏ.
* **Cảnh báo nguy hiểm (Anti-Pattern)**: Nhúng danh sách bình luận vào trong bài viết `comments: []`. Khi bài viết đạt 100,000 bình luận, document sẽ phát nổ quá 16MB và làm crash database!

---

## 🔑 BƯỚC 2: Chiến Lược Phân Vùng Trong DynamoDB (Single Table Design)

Trong DynamoDB, hiệu năng phụ thuộc 100% vào việc chọn **Partition Key (PK)** và **Sort Key (SK)**:
* **Tránh Hot Partition**: Tuyệt đối không dùng các giá trị có tính lặp lại cao (như `status` hay `country_code`) làm Partition Key vì hàng triệu request sẽ dồn vào đúng 1 node phần cứng.
* **Kỹ thuật PK phân tán**: Dùng mã định danh có độ ngẫu nhiên cao (như `USER#<user_id>` hoặc `TENANT#<tenant_id>`).

---

## 🎯 CÂU HỎI KIỂM ĐỊNH (Checklist)
* Có mảng (Array) nào trong Document có nguy cơ tăng trưởng không giới hạn (Unbounded Array) không?
* Các truy vấn thường xuyên nhất đã được tạo Index (Single-field hoặc Compound Index) chưa?
* Cấu trúc Document có phục vụ trực tiếp cho màn hình hiển thị mà không cần phải thực hiện quá nhiều thao tác `$lookup` (JOIN) không?
