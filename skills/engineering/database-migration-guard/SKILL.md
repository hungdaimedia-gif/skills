---
name: database-migration-guard
description: "Quy trình Migration cơ sở dữ liệu an toàn không downtime (Zero-Downtime Migration): Khóa bảng (Table Locks), Expand and Contract Pattern, Rollback an toàn."
provenance:
  source_repo: "pressly/goose"
  source_url: "https://github.com/pressly/goose"
  source_commit: "7e14a29"
  imported_at: "2026-09-15T11:23:00+07:00"
  stars_at_import: 11459
  forks_at_import: 698
---

# 🛡️ Database Migration Guard — Quy Chuẩn Migration An Toàn Tuyệt Đối

> **Triết lý cốt lõi**: Trong môi trường Production có hàng triệu người dùng, một câu lệnh `ALTER TABLE` thiếu cẩn trọng có thể chiếm độc quyền khóa bảng (Exclusive Lock), khiến mọi request ghi/đọc bị treo và làm sập toàn bộ dịch vụ. Mọi thay đổi Schema bắt buộc phải tuân theo quy tắc **Zero-Downtime Migration**.

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Bạn chuẩn bị viết hoặc chạy migration (Prisma migrate, Goose, Flyway, Alembic, Drizzle-kit).
2. Cần thêm cột mới, đổi tên cột, xóa cột hoặc đổi kiểu dữ liệu trên bảng có dữ liệu lớn.
3. Cần tạo Index trên bảng production mà không muốn làm gián đoạn người dùng.
4. Chuẩn bị kịch bản Rollback an toàn nếu bản deploy gặp sự cố bất ngờ.

---

## 🚫 BƯỚC 1: 5 Lệnh Cấm Kỵ Khi Migration Trực Tiếp Trên Production

1. ❌ **CẤM: `ALTER TABLE ... ADD COLUMN ... NOT NULL;` (Không có DEFAULT)**:
   * Sẽ fail ngay lập tức nếu bảng đã có dữ liệu.
2. ❌ **CẤM: `ALTER TABLE ... ADD COLUMN ... NOT NULL DEFAULT 'value';` trên PostgreSQL cũ**:
   * Sẽ viết lại toàn bộ bảng (Table Rewrite), khóa bảng suốt hàng chục phút.
3. ❌ **CẤM: `ALTER TABLE ... RENAME COLUMN old_name TO new_name;`**:
   * Code backend cũ đang chạy sẽ lập tức quăng lỗi 500 vì không tìm thấy `old_name`.
4. ❌ **CẤM: `CREATE INDEX idx_name ON table_name;`**:
   * Khóa quyền ghi của toàn bộ bảng. Bắt buộc phải dùng `CREATE INDEX CONCURRENTLY`.
5. ❌ **CẤM: Xóa cột (`DROP COLUMN`) trong cùng lần deploy với code mới**.

---

## 🔄 BƯỚC 2: Mô Hình Expand & Contract (4 Giai Đoạn Zero-Downtime)

Để thay đổi cấu trúc bảng một cách an toàn mà không làm sập ứng dụng, bắt buộc chia làm 4 giai đoạn:

```text
[Giai đoạn 1: EXPAND]     Thêm cột mới (cho phép NULL). Code cũ vẫn chạy bình thường.
         │
[Giai đoạn 2: WRITE BOTH] Deploy code mới: Ghi dữ liệu đồng thời vào CẢ cột cũ VÀ cột mới.
         │
[Giai đoạn 3: BACKFILL]   Chạy script chạy nền (Worker) cập nhật dữ liệu cũ theo từng batch nhỏ.
         │
[Giai đoạn 4: CONTRACT]   Chuyển code đọc cột mới hoàn toàn ➔ Sau đó mới DROP cột cũ.
```

### Ví dụ Thực Tế: Đổi tên cột từ `fullname` thành `full_name`
1. **Bước 1 (Migration 1)**: `ALTER TABLE users ADD COLUMN full_name TEXT NULL;`
2. **Bước 2 (Code Deploy)**:
   ```ts
   // Khi tạo mới hoặc update, ghi vào cả 2 cột
   await db.users.create({
     data: { fullname: name, full_name: name }
   });
   ```
3. **Bước 3 (Backfill Script chạy nền theo lô 1,000 dòng)**:
   ```sql
   UPDATE users SET full_name = fullname WHERE full_name IS NULL LIMIT 1000;
   ```
4. **Bước 4 (Migration 2 sau 1 tuần an toàn)**: `ALTER TABLE users DROP COLUMN fullname;`

---

## ⚡ BƯỚC 3: Tạo Index Không Khóa Bảng (Concurrent Indexing)

Trên PostgreSQL, luôn sử dụng từ khóa `CONCURRENTLY`:
```sql
-- An toàn 100%: Người dùng vẫn đọc và ghi dữ liệu bình thường trong lúc tạo Index
CREATE INDEX CONCURRENTLY idx_users_phone ON users (phone_number);
```
> *Lưu ý: `CREATE INDEX CONCURRENTLY` không được chạy bên trong một khối Transaction (`BEGIN ... COMMIT`).*

---

## 🔙 BƯỚC 4: Kế Hoạch Rollback Hai Chiều (Reversible Migrations)

Mọi file migration đều phải có 2 phần đối xứng:
* `UP`: Thay đổi nâng cấp.
* `DOWN`: Lệnh khôi phục nguyên trạng.

Kiểm tra trước khi commit:
```bash
# Chạy thử nghiệm trên máy local
npm run migrate:up
npm run migrate:down
npm run migrate:up
```

---

## 🎯 CÂU HỎI KIỂM ĐỊNH (Checklist)
* Lệnh migration có gây chiếm khóa độc quyền (Exclusive Table Lock) kéo dài không?
* Các câu lệnh tạo Index đã có từ khóa `CONCURRENTLY` chưa?
* Code backend phiên bản hiện tại có tiếp tục hoạt động được khi migration vừa chạy xong không?
