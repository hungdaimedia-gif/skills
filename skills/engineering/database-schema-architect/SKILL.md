---
name: database-schema-architect
description: "Thiết kế cơ sở dữ liệu quan hệ (PostgreSQL, MySQL, SQLite): Chuẩn hóa 3NF, mô hình hóa ERD, chọn kiểu dữ liệu tối ưu, Ràng buộc khóa ngoại và Index."
provenance:
  source_repo: "prisma/orm"
  source_url: "https://github.com/prisma/orm"
  source_commit: "9a21ce3"
  imported_at: "2026-09-15T11:23:00+07:00"
  stars_at_import: 47610
  forks_at_import: 2537
---

# 🗄️ Database Schema Architect — Thiết Kế Cơ Sở Dữ Liệu Chuyên Nghiệp

> **Triết lý cốt lõi**: Cơ sở dữ liệu là trái tim của hệ thống. Một Schema được thiết kế cẩu thả sẽ kéo sập hiệu năng, sinh ra dữ liệu rác và làm đội chi phí bảo trì lên gấp 10 lần. Schema tốt phải đảm bảo tính toàn vẹn dữ liệu ở cấp độ Database Engine chứ không phó mặc hoàn toàn cho code ứng dụng.

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Bạn bắt đầu một dự án mới và cần mô hình hóa thực thể (ERD), thiết kế bảng (Tables).
2. Cần chọn hệ quản trị CSDL phù hợp: PostgreSQL (cho quan hệ phức tạp, JSONB), SQLite (cho local/nhúng), MySQL.
3. Schema bị trùng lặp dữ liệu, không có ràng buộc khóa ngoại (Foreign Key) dẫn đến rác dữ liệu mồ côi (Orphan records).
4. Phân vân giữa UUIDv7, Bigint autoincrement hay CUID cho Primary Key.

---

## 📐 BƯỚC 1: Chuẩn Hóa Dữ Liệu 3NF (Third Normal Form)

Bắt buộc tuân thủ 3 cấp độ chuẩn hóa trước khi code:
1. **1NF (First Normal Form)**: Mỗi ô chỉ chứa 1 giá trị nguyên tử (Atomic). Tuyệt đối không lưu danh sách chuỗi ngăn cách bằng dấu phẩy như `"tag1,tag2,tag3"` trong một cột TEXT (hãy tách thành bảng quan hệ nhiều-nhiều hoặc dùng kiểu `text[]` / `JSONB` có index).
2. **2NF (Second Normal Form)**: Mọi thuộc tính không khóa phải phụ thuộc hoàn toàn vào toàn bộ khóa chính (Composite Primary Key).
3. **3NF (Third Normal Form)**: Không có sự phụ thuộc bắc cầu (Transitive dependency). Ví dụ: Không lưu cả `unit_price`, `quantity` và `total_price` trong bảng OrderItem (vì `total_price` = `unit_price * quantity`, có thể tính toán tức thì).

---

## 🔑 BƯỚC 2: Chiến Lược Chọn Khóa Chính (Primary Key Strategy)

| Loại Khóa | Ưu Điểm | Nhược Điểm | Khuyên Dùng Khi |
| :--- | :--- | :--- | :--- |
| **`BIGINT GENERATED ALWAYS AS IDENTITY`** | Cực kỳ nhanh, tốn ít dung lượng (8 bytes), Index nén tốt | Lộ số lượng bản ghi thực tế ra ngoài URL (`/users/12`) | Bảng nội bộ, bảng dữ liệu lớn, bảng trung gian |
| **`UUIDv7` (Time-ordered UUID)** | Toàn cục duy nhất, phân tán an toàn, có sẵn thứ tự thời gian | Tốn 16 bytes dung lượng | Khóa chính chuẩn hiện đại cho bảng Public, API endpoints |
| **`UUIDv4` (Random)** | Ngẫu nhiên tuyệt đối | Làm phân mảnh cây B-Tree Index nghiêm trọng khi dữ liệu lớn | Chỉ dùng khi không cần sắp xếp theo thời gian |

---

## 🛡️ BƯỚC 3: Ràng Buộc Dữ Liệu Nghiêm Ngặt (Database Constraints)

Tuyệt đối không chỉ dựa vào logic kiểm tra ở tầng code backend. Bắt buộc đặt ràng buộc tại Database:
1. **NOT NULL & DEFAULT**: Mọi cột nếu không có lý do để NULL thì bắt buộc phải là `NOT NULL`.
2. **Khóa Ngoại & Hành Vi Xóa (Foreign Key Actions)**:
   * Dùng `ON DELETE RESTRICT` cho dữ liệu tài chính (không cho phép xóa khách hàng nếu còn hóa đơn).
   * Dùng `ON DELETE CASCADE` cho bảng con phụ thuộc hoàn toàn (ví dụ: xóa `Post` thì xóa toàn bộ `PostTags`).
3. **Ràng Buộc Điều Kiện (CHECK Constraints)**:
   ```sql
   ALTER TABLE accounts ADD CONSTRAINT check_positive_balance CHECK (balance >= 0);
   ALTER TABLE users ADD CONSTRAINT check_valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');
   ```

---

## 🕒 BƯỚC 4: Bảng Mẫu Chuẩn Cho Mọi Thực Thể (Base Entity Template)

Mọi bảng chính trong hệ thống đều phải sở hữu các trường kiểm toán (Audit Columns):

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    
    -- Audit Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ NULL -- Dùng cho Soft Delete nếu cần
);

-- Tạo Unique Index không phân biệt chữ hoa chữ thường
CREATE UNIQUE INDEX idx_users_email_lower ON users (LOWER(email));
```

---

## 🎯 CÂU HỎI KIỂM ĐỊNH (Checklist)
* Bảng đã có đầy đủ ràng buộc khóa ngoại (Foreign Keys) để chống dữ liệu rác mồ côi chưa?
* Các cột tìm kiếm thường xuyên (`email`, `status`, `user_id`) đã được tạo Index chưa?
* Có đang lưu dữ liệu tính toán dư thừa vi phạm 3NF không?
