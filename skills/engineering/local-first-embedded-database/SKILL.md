---
name: local-first-embedded-database
description: "Kiến trúc CSDL Local-First & Nhúng (SQLite, Turso, PGlite, DuckDB): Thiết kế ứng dụng Offline-First, tối ưu hóa WAL mode, đồng bộ dữ liệu đám mây hai chiều và xử lý xung đột CRDT."
provenance:
  source_repo: "libsql/libsql"
  source_url: "https://github.com/libsql/libsql"
  source_commit: "c381fa0"
  imported_at: "2026-09-15T11:30:00+07:00"
  stars_at_import: 14200
  forks_at_import: 680
---

# 📱 Local-First & Embedded Database — CSDL Nhúng & Ứng Dụng Offline-First

> **Triết lý cốt lõi**: Người dùng không muốn thấy màn hình quay vòng vòng (Loading Spinner) chỉ để gõ một ghi chú hay mở một danh sách việc cần làm. Phong trào **Local-First Software** đưa dữ liệu về lưu trực tiếp trên thiết bị của người dùng (SQLite, PGlite, DuckDB), cho phép đọc/ghi tức thì không có độ trễ (< 0.1ms), hoạt động hoàn hảo khi mất mạng và tự động đồng bộ khi có kết nối trở lại.

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Bạn đang phát triển ứng dụng di động (React Native, Flutter, iOS/Android) hoặc Desktop App (Tauri, Electron).
2. Xây dựng công cụ lập trình CLI, Desktop tool (như Obsidian, Linear, Notion-like) cần tốc độ phản hồi tức thì.
3. Cần phân tích dữ liệu phân tích ngay trên máy cục bộ bằng **DuckDB** mà không cần dựng Data Warehouse cồng kềnh.
4. Cần đồng bộ dữ liệu hai chiều giữa Client (SQLite trên máy) và Cloud (Turso / PostgreSQL / Supabase).

---

## ⚡ BƯỚC 1: Cấu Hình SQLite Chuẩn Cấp Công Nghiệp (WAL Mode)

Mặc định, SQLite chỉ cho phép 1 kết nối đọc HOẶC ghi tại một thời điểm. Để ứng dụng không bị lỗi khóa database (`SQLITE_BUSY: database is locked`), bắt buộc cấu hình các PRAGMA sau ngay khi mở kết nối:

```sql
-- 1. Bật chế độ Write-Ahead Logging: Cho phép NHIỀU người đọc trong khi 1 người đang ghi
PRAGMA journal_mode = WAL;

-- 2. Đặt mức đồng bộ bình thường: Tăng tốc độ ghi gấp 10 lần mà vẫn an toàn chống sập nguồn
PRAGMA synchronous = NORMAL;

-- 3. Thời gian chờ khi bị khóa: Chờ tối đa 5000ms trước khi báo lỗi
PRAGMA busy_timeout = 5000;

-- 4. Bắt buộc kích hoạt ràng buộc khóa ngoại (Mặc định SQLite tắt tính năng này)
PRAGMA foreign_keys = ON;

-- 5. Tăng kích thước bộ nhớ đệm RAM (Cache size = -64000 tương đương 64MB RAM)
PRAGMA cache_size = -64000;
```

---

## 🔄 BƯỚC 2: Chiến Lược Đồng Bộ Hai Chiều & Xử Lý Xung Đột (Sync Architecture)

Khi người dùng sửa dữ liệu trên cả 2 thiết bị (điện thoại và laptop) trong lúc mất mạng, khi có mạng trở lại sẽ xử lý ra sao?

1. **Chiến lược Last-Write-Wins (LWW)**:
   * Mỗi bản ghi lưu trường `updated_at` (chuẩn thời gian UTC micro-giây).
   * Bản cập nhật có timestamp lớn hơn sẽ chiến thắng và ghi đè.
   * *Ưu điểm*: Rất dễ triển khai, phù hợp 90% ứng dụng ghi chú, todo, quản lý chi tiêu.

2. **Chiến lược CRDTs (Conflict-free Replicated Data Types)**:
   * Áp dụng thư viện như Yjs, Automerge cho các ứng dụng cộng tác thời gian thực nhiều người cùng gõ (Collaborative Text Editing).

---

## 🦆 BƯỚC 3: Phân Tích Dữ Liệu Lớn Trên Máy Cục Bộ Bằng DuckDB

Nếu dự án cần truy vấn, phân tích và thống kê trên các file CSV, Parquet hàng chục Gigabytes:
* Tuyệt đối không import vào SQLite (vì SQLite là row-oriented, quét cột rất chậm).
* Sử dụng **DuckDB** (Columnar Embedded Engine):
  ```sql
  -- Chạy tức thì trực tiếp trên file Parquet mà không cần import vào DB:
  SELECT category, SUM(revenue) 
  FROM 'sales_2026_*.parquet' 
  GROUP BY category 
  ORDER BY SUM(revenue) DESC 
  LIMIT 5;
  ```

---

## 🎯 CÂU HỎI KIỂM ĐỊNH (Checklist)
* Kết nối SQLite đã được bật `PRAGMA journal_mode = WAL` và `busy_timeout` chưa?
* Đã bật `PRAGMA foreign_keys = ON` để bảo vệ khóa ngoại chưa?
* Khi mất kết nối internet hoàn toàn, ứng dụng có tiếp tục cho người dùng tạo và sửa dữ liệu mượt mà không?
