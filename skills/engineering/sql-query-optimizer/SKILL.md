---
name: sql-query-optimizer
description: "Tối ưu hóa truy vấn SQL và phân tích hiệu năng: Đọc EXPLAIN ANALYZE, thiết kế Index (B-Tree, Partial, Composite), diệt lỗi N+1 query và Pagination."
provenance:
  source_repo: "supabase/supabase"
  source_url: "https://github.com/supabase/supabase"
  source_commit: "4c718b2"
  imported_at: "2026-09-15T11:23:00+07:00"
  stars_at_import: 109231
  forks_at_import: 13768
---

# ⚡ SQL Query Optimizer — Tối Ưu Hóa Truy Vấn & Đánh Index Chuẩn Chuyên Gia

> **Triết lý cốt lõi**: "Viết câu lệnh SQL chạy được" chỉ mất 1 phút, nhưng "viết câu lệnh SQL chạy mượt mà trên 10 triệu bản ghi" đòi hỏi sự thấu hiểu sâu sắc về cách Database Engine thực thi. Quét tuần tự toàn bộ bảng (Sequential Scan) trên bảng lớn là tội đồ số một gây sập server.

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Truy vấn cơ sở dữ liệu bị chậm (Latency > 100ms), CPU Database tăng vọt lên 90–100%.
2. Cần đọc và giải mã kế hoạch thực thi câu lệnh bằng `EXPLAIN (ANALYZE, BUFFERS)`.
3. Gặp lỗi kinh điển N+1 query khi sử dụng các ORM (Prisma, Hibernate, SQLAlchemy, TypeORM).
4. Phân trang dữ liệu bằng `OFFSET 100000 LIMIT 20` làm đơ máy chủ.

---

## 🔍 BƯỚC 1: Đọc & Giải Mã Kế Hoạch Thực Thi (EXPLAIN ANALYZE)

Luôn chạy lệnh sau trước khi phán đoán:
```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM orders WHERE customer_id = 'c123' AND status = 'completed' ORDER BY created_at DESC LIMIT 10;
```

### Các dấu hiệu báo động đỏ cần xử lý ngay:
* 🔴 **`Seq Scan on orders`**: Đang quét từng dòng của cả bảng orders. Nếu bảng có hàng triệu dòng, đây là thảm họa.
* 🔴 **`Rows Removed by Filter: 999900`**: Quét 1 triệu dòng nhưng chỉ lấy 10 dòng ➔ Thiếu Index!
* 🔴 **`Sort Method: external merge Disk`**: Không đủ bộ nhớ RAM (`work_mem`), CSDL phải ghi dữ liệu tạm ra ổ đĩa để sắp xếp ➔ Cực kỳ chậm.
* 🟢 **Mục tiêu đạt được**: `Index Scan` hoặc `Bitmap Index Scan` với `Cost` thấp và thời gian thực thi `< 5ms`.

---

## 🏗️ BƯỚC 2: Chiến Lược Thiết Kế Index Chuẩn Xác (Indexing Mastery)

1. **Quy tắc Vàng cho Composite Index (Cột ghép ESR: Equality ➔ Sort ➔ Range)**:
   * **E (Equality)**: Đặt các cột tìm kiếm bằng (`=`) lên đầu Index (VD: `customer_id`, `status`).
   * **S (Sort)**: Đặt cột dùng để sắp xếp `ORDER BY` ở giữa (VD: `created_at DESC`).
   * **R (Range)**: Đặt các cột tìm kiếm khoảng (`>`, `<`, `BETWEEN`) ở cuối cùng.
   ```sql
   -- Index hoàn hảo cho: WHERE customer_id = ? AND status = ? ORDER BY created_at DESC
   CREATE INDEX idx_orders_cust_status_created 
   ON orders (customer_id, status, created_at DESC);
   ```

2. **Index Cắt Tỉa Có Điều Kiện (Partial Index)**:
   Nếu chỉ thường xuyên truy vấn các đơn hàng chưa hoàn tất (`status = 'pending'`), đừng đánh index toàn bộ bảng:
   ```sql
   -- Tiết kiệm 90% dung lượng RAM và đĩa:
   CREATE INDEX idx_orders_pending ON orders (created_at) WHERE status = 'pending';
   ```

3. **Chỉ số Tìm Kiếm Văn Bản & JSONB (GIN Index)**:
   Đối với cột JSONB trong PostgreSQL, dùng `GIN` thay vì B-Tree:
   ```sql
   CREATE INDEX idx_metadata_gin ON products USING GIN (metadata jsonb_path_ops);
   ```

---

## 🪓 BƯỚC 3: Diệt Tận Gốc Lỗi N+1 Query

* **Hiện tượng**: Lấy danh sách 100 bài viết (1 query), sau đó vòng lặp gọi 100 query để lấy tác giả của từng bài viết (Tổng cộng 101 queries).
* **Giải pháp dứt điểm**:
  * **Cách 1**: Dùng `JOIN` kết hợp lấy dữ liệu trong 1 câu lệnh duy nhất.
  * **Cách 2 (Batching)**: Lấy toàn bộ `author_id` rồi dùng `WHERE id IN (...)` trong 1 query thứ hai.

---

## 📜 BƯỚC 4: Phân Trang Bằng Keyset (Cursor-Based Pagination)

Tuyệt đối tránh `OFFSET` khi dữ liệu lớn hơn 10,000 dòng. Thay vào đó dùng Keyset Pagination:

```sql
-- ❌ CHẬM (CSDL phải đọc 50,000 dòng đầu rồi vứt đi):
SELECT * FROM posts ORDER BY id DESC LIMIT 20 OFFSET 50000;

-- ✅ TỨC THÌ (< 1ms nhờ tận dụng trực tiếp Index):
SELECT * FROM posts 
WHERE id < 'last_seen_post_id' 
ORDER BY id DESC 
LIMIT 20;
```

---

## 🎯 CÂU HỎI KIỂM ĐỊNH (Checklist)
* Đã chạy `EXPLAIN ANALYZE` để đo lường trước và sau khi tối ưu chưa?
* Thứ tự các cột trong Composite Index có tuân thủ đúng quy tắc ESR không?
* Đã loại bỏ hoàn toàn các vòng lặp gọi query đơn lẻ (N+1) chưa?
