---
name: high-concurrency-system-design
description: "Thiết kế Kiến Trúc Hệ Thống Chịu Tải Cao (High-Concurrency System Design): Chiến lược Load Balancing, Hàng đợi thông điệp bất đồng bộ (Message Queues - Kafka/RabbitMQ), Phân vùng Database (Sharding/Partitioning), Chiến lược Caching đa tầng và Rate Limiting chống sập hệ thống."
provenance:
  repo: "donnemartin/system-design-primer"
  branch: "master"
  stars: 290000
  forks: 46000
  verified_at: "2026-09-15"
---

# 🏛️ High-Concurrency System Design
### Kiến Trúc Hệ Thống Phân Tán & Chịu Tải Hàng Triệu Yêu Cầu

> **Triết lý cốt lõi**: "Không có hệ thống nào không thể sập, chỉ có hệ thống suy giảm hiệu năng một cách duyên dáng (Graceful Degradation)."
> Thiết kế chịu tải cao không phải là cố gắng mua server mạnh hơn (Vertical Scaling), mà là phân tán áp lực công việc ra nhiều tầng độc lập (Horizontal Scaling).

---

## 🎯 Khi Nào Cần Sử Dụng Skill Này?

- Khi hệ thống bắt đầu đón nhận lượng truy cập tăng đột biến (Flash Sale, sự kiện viral, hàng chục ngàn người dùng đồng thời).
- Khi Database bị nghẽn cổ chai CPU 100% do quá nhiều lượt đọc/ghi đồng thời.
- Khi cần thiết kế hệ thống xử lý tác vụ nặng không đồng bộ (xử lý video, gửi thông báo hàng loạt, tính toán số liệu).
- Khi phỏng vấn hoặc thẩm định thiết kế kiến trúc kỹ thuật (System Design Review).

---

## 📐 5 Trụ Cột Giảm Tải Hệ Thống Kinh Điển

```
[Clients] ──► [Cloudflare CDN] ──► [Nginx / Envoy Load Balancer]
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
             [App Instance 1]                            [App Instance 2]
                       │                                           │
         ┌─────────────┴─────────────┐               ┌─────────────┴─────────────┐
         ▼                           ▼               ▼                           ▼
  [Redis Cache Cluster]       [Message Queue]  [Redis Cache Cluster]       [Message Queue]
         │                           │
         ▼                           ▼
[Postgres Read Replica]       [Background Workers] ──► [Postgres Master Write]
```

### 1. Phân Tách Đọc / Ghi (Read-Write Splitting)
- Hầu hết các ứng dụng Web có tỷ lệ 80% Đọc - 20% Ghi.
- Thiết lập **Primary Database** chỉ nhận các lệnh `INSERT`, `UPDATE`, `DELETE`.
- Thiết lập cụm **Read Replicas** nhận toàn bộ truy vấn `SELECT` để giảm tải 80% áp lực cho database chính.

### 2. Chiến Lược Caching Đa Tầng (Multi-Tier Caching)
- **Tầng 1 (Client / Edge)**: CDN (Cloudflare) cache các tài nguyên tĩnh và các phản hồi API công khai (`Cache-Control: public, max-age=300`).
- **Tầng 2 (Application Cache)**: Redis cụm lưu trữ session và các bản ghi truy vấn nặng.
- **Phòng chống lỗi kinh điển**:
  - *Cache Avalanche (Tuyết lở)*: Thêm thời gian ngẫu nhiên (`TTL + Math.random() * 60s`) để các key không hết hạn cùng lúc.
  - *Cache Breakdown (Thủng cache)*: Dùng Distributed Lock (Redlock) chỉ cho 1 thread truy vấn database khi cache vừa hết hạn.

### 3. San Bằng Đỉnh Tải Bằng Hàng Đợi (Peak Shaving with Message Queues)
- Khi có 10,000 yêu cầu đặt hàng/phút, không bao giờ ghi trực tiếp 10,000 giao dịch vào DB cùng lúc.
- Đẩy yêu cầu vào hàng đợi tin nhắn (Kafka, RabbitMQ, Redis BullMQ).
- Cụm **Background Workers** tiêu thụ thông điệp với tốc độ ổn định (ví dụ: 1,000 giao dịch/phút) mà DB có thể chịu tải an toàn.

### 4. Phòng Vệ Ngưỡng Tải (Rate Limiting & Shedding)
- Cấu hình thuật toán **Token Bucket** hoặc **Leaky Bucket** để giới hạn số request trên mỗi IP/User.
- Khi tải hệ thống chạm ngưỡng 90% CPU, kích hoạt chế độ **Load Shedding**: từ chối các request không quan trọng (vd: tính toán gợi ý, analytics) để ưu tiên giữ vững luồng thanh toán và đăng nhập.

---

## 📋 Checklist Kiểm Định Thiết Kế Chịu Tải (Scalability Gate)

- [ ] 1. **Stateless Backend**: Server ứng dụng hoàn toàn không lưu trạng thái phiên trong bộ nhớ RAM cục bộ (mọi session lưu ở Redis).
- [ ] 2. **Database Connection Pooling**: Luôn dùng connection pool (PgBouncer hoặc HikariCP) với giới hạn kết nối an toàn.
- [ ] 3. **Asynchronous Heavy Tasks**: Mọi tác vụ tốn > 200ms (gửi mail, sinh PDF, gọi AI) đều được đẩy ra background worker.
- [ ] 4. **Graceful Degradation**: Khi cache Redis tạm thời gặp sự cố, hệ thống có cơ chế fallback không làm sập API.
- [ ] 5. **Idempotency Consumer**: Worker nhận thông điệp từ Queue đảm bảo xử lý Idempotent (nhận trùng tin nhắn không làm trừ tiền 2 lần).
