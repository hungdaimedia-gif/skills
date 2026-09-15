---
name: redis-caching-realtime-mastery
description: "Làm chủ Redis Caching & Xử lý thời gian thực: Chiến lược Cache-Aside, Write-Through, Rate Limiting chống DDoS, Pub/Sub thời gian thực và Distributed Lock."
provenance:
  source_repo: "redis/redis"
  source_url: "https://github.com/redis/redis"
  source_commit: "a812fc4"
  imported_at: "2026-09-15T11:30:00+07:00"
  stars_at_import: 76366
  forks_at_import: 24807
---

# ⚡ Redis Caching & Realtime Mastery — Tối Ưu Hóa Bộ Nhớ Đệm & Thời Gian Thực

> **Triết lý cốt lõi**: "Truy vấn nhanh nhất là truy vấn không cần chạm vào ổ đĩa". Redis (hoặc Valkey/KeyDB) là lá chắn đầu tiên bảo vệ Database quan hệ khỏi các đợt bùng nổ truy cập (Traffic Spikes). Tuy nhiên, cache không hợp lý sẽ dẫn đến thảm họa dữ liệu cũ (Stale Data), Cache Stampede và tràn bộ nhớ RAM.

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Database bị quá tải bởi hàng ngàn câu lệnh SELECT giống hệt nhau mỗi giây (Trang chủ, chi tiết sản phẩm hot, bảng giá).
2. Cần giới hạn tần suất gọi API (Rate Limiting) để chống cào dữ liệu trái phép hoặc chống DDoS.
3. Ứng dụng cần tính năng Real-time: Chat trực tiếp, Thông báo tức thì (Notifications), Bảng xếp hạng (Leaderboard).
4. Cần khóa phân tán (Distributed Lock) để chống việc 2 người cùng mua trúng 1 chiếc vé máy bay cuối cùng (Race Condition).

---

## 🛡️ BƯỚC 1: Chiến Lược Cache-Aside Chuẩn Xác

Mô hình phổ biến và an toàn nhất cho hầu hết hệ thống:

```text
[Request từ Client]
         │
         ▼
[1. Kiểm tra Redis Cache] ──(Có Data: Cache Hit)──> Trả về kết quả ngay (< 1ms)
         │
    (Cache Miss)
         │
         ▼
[2. Query vào PostgreSQL/MySQL]
         │
         ▼
[3. Ghi dữ liệu vào Redis kèm TTL]
         │
         ▼
[4. Trả kết quả về cho Client]
```

### Triển khai chuẩn bằng TypeScript:
```ts
async function getProductWithCache(productId: string) {
  const cacheKey = `product:${productId}`;
  
  // 1. Thử lấy từ Redis
  const cached = await redis.get(cacheKey);
  if (cached) return JSON.parse(cached);

  // 2. Cache miss -> Lấy từ DB
  const product = await db.product.findUnique({ where: { id: productId } });
  if (!product) return null;

  // 3. Ghi vào Redis với thời hạn TTL 3600 giây (1 giờ) + biến thiên ngẫu nhiên (Jitter)
  // Jitter (cộng thêm ngẫu nhiên 0-300s) để tránh toàn bộ cache cùng hết hạn 1 lúc (Cache Stampede)
  const ttl = 3600 + Math.floor(Math.random() * 300);
  await redis.setex(cacheKey, ttl, JSON.stringify(product));

  return product;
}
```

---

## 🚦 BƯỚC 2: Giới Hạn Tần Suất Gọi API (Sliding Window Rate Limiter)

Sử dụng cấu trúc `ZSET` (Sorted Set) trong Redis để tính toán số request chính xác theo cửa sổ thời gian trượt (chống gian lận ở ranh giới phút):

```ts
async function isRateLimited(userId: string, limit = 60, windowSeconds = 60): Promise<boolean> {
  const key = `ratelimit:${userId}`;
  const now = Date.now();
  const windowStart = now - (windowSeconds * 1000);

  const tx = redis.multi();
  // 1. Xóa các request cũ hơn cửa sổ thời gian
  tx.zremrangebyscore(key, 0, windowStart);
  // 2. Thêm request hiện tại với điểm số là timestamp
  tx.zadd(key, now, `${now}-${Math.random()}`);
  // 3. Đếm số request còn lại trong cửa sổ
  tx.zcard(key);
  // 4. Gia hạn thời gian sống của key
  tx.expire(key, windowSeconds);

  const results = await tx.exec();
  const requestCount = results[2][1] as number;

  return requestCount > limit; // Nếu vượt quá 60 request/phút -> Chặn
}
```

---

## 🔒 BƯỚC 3: Khóa Phân Tán An Toàn (Distributed Lock - Redlock Pattern)

Khi cần thực hiện một thao tác độc quyền (ví dụ trừ tiền tài khoản hoặc trừ tồn kho):

```ts
async function acquireLock(resourceId: string, ttlMs = 5000): Promise<string | null> {
  const lockToken = crypto.randomUUID();
  const lockKey = `lock:${resourceId}`;
  
  // Lệnh SET với cờ NX (chỉ set nếu chưa tồn tại) và PX (hết hạn sau mili-giây)
  const result = await redis.set(lockKey, lockToken, 'PX', ttlMs, 'NX');
  return result === 'OK' ? lockToken : null;
}

// Giải phóng khóa an toàn bằng Lua script (chỉ người nắm khóa mới được xóa khóa)
const releaseLockLua = `
  if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
  else
    return 0
  end
`;
```

---

## 🎯 CÂU HỎI KIỂM ĐỊNH (Checklist)
* Mọi Key ghi vào Redis đã có thời gian hết hạn (TTL) chưa hay để vĩnh viễn gây tràn RAM?
* Đã có cơ chế Jitter (thời gian ngẫu nhiên) để chống sập đồng loạt (Cache Stampede) chưa?
* Khi dữ liệu gốc trong CSDL bị cập nhật, đã có cơ chế xóa cache tương ứng (Cache Invalidation) chưa?
