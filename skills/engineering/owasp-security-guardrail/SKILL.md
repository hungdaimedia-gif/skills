---
name: owasp-security-guardrail
description: "Quy chuẩn rà soát và phòng vệ an ninh ứng dụng theo tiêu chuẩn OWASP Top 10: Chống Injection, xác thực JWT/Session an toàn, kiểm soát phân quyền (BOLA/IDOR), mã hóa mật khẩu, vệ sinh biến môi trường và xử lý dữ liệu đầu vào (Input Sanitization)."
provenance:
  repo: "OWASP/CheatSheetSeries"
  branch: "master"
  stars: 30000
  forks: 4000
  verified_at: "2026-09-15"
---

# 🛡️ OWASP Security Guardrail
### Quy Chuẩn Phòng Vệ An Ninh Ứng Dụng & Chống Lỗ Hổng Web Thực Chiến

> **Triết lý cốt lõi**: "Không bao giờ tin tưởng dữ liệu từ người dùng (Never trust user input)."
> Mọi lỗ hổng bảo mật nghiêm trọng đều xuất phát từ việc thiếu kiểm định dữ liệu đầu vào, quản lý phiên làm việc lỏng lẻo hoặc kiểm tra phân quyền hời hợt.

---

## 🎯 Khi Nào Cần Sử Dụng Skill Này?

- Khi xây dựng API xác thực người dùng (Login, Register, Refresh Token, Password Reset).
- Khi xử lý dữ liệu gửi lên từ form hoặc query params truyền vào Database/Command shell.
- Khi cấp quyền truy cập tài nguyên (kiểm tra quyền sở hữu ID tài nguyên - chống IDOR/BOLA).
- Trước khi release mã nguồn lên môi trường Production để rà soát lỗ hổng an toàn thông tin.

---

## ⚠️ 5 Lỗ Hổng Chết Người & Cách Khắc Phục Chuẩn OWASP

### 1. SQL / NoSQL Injection & Command Injection
- **Rủi ro**: Ghép chuỗi truy vấn trực tiếp (`SELECT * FROM users WHERE id = '` + userId + `'`) cho phép kẻ tấn công vượt quyền hoặc drop database.
- **Quy tắc bắt buộc**:
  - 100% truy vấn SQL phải dùng **Parameterized Queries (Prepared Statements)** hoặc Type-Safe ORM (Prisma, Drizzle, SQLAlchemy).
  - Tuyệt đối không dùng `eval()`, `exec()`, `system()`, `child_process.exec()` với tham số từ người dùng.

```typescript
// ❌ NGUY HIỂM: Nối chuỗi SQL
const query = `SELECT * FROM users WHERE email = '${req.body.email}'`;

// ✅ CHUẨN OWASP: Parameterized query với PostgreSQL / Drizzle
const user = await db.execute(
  sql`SELECT id, email, password_hash, role FROM users WHERE email = ${req.body.email} LIMIT 1`
);
```

### 2. Broken Object Level Authorization (BOLA / IDOR)
- **Rủi ro**: Người dùng đổi `id` trên URL (`/api/orders/123` ➔ `/api/orders/124`) để xem trộm đơn hàng của người khác.
- **Quy tắc bắt buộc**: Mọi truy vấn đọc/sửa/xoá tài nguyên phải luôn kèm điều kiện `userId` của người dùng hiện tại đang đăng nhập.

```typescript
// ❌ NGUY HIỂM: Chỉ kiểm tra orderId mà không kiểm tra ai là chủ
const order = await db.query.orders.findFirst({
  where: eq(orders.id, req.params.orderId),
});

// ✅ CHUẨN OWASP: Ràng buộc chặt chẽ với currentUserId từ token
const order = await db.query.orders.findFirst({
  where: and(
    eq(orders.id, req.params.orderId),
    eq(orders.userId, req.user.id)
  ),
});
if (!order) {
  throw new ForbiddenError("Không có quyền truy cập hoặc tài nguyên không tồn tại.");
}
```

### 3. Quản Lý JWT & Cookie An Toàn
- **Quy tắc bắt buộc**:
  - **Access Token**: Hạn dùng ngắn (15 - 30 phút).
  - **Refresh Token**: Lưu trữ trong `httpOnly, secure, sameSite: 'strict'` cookie. Không bao giờ lưu token nhạy cảm trong `localStorage` (dễ bị tấn công XSS trộm cắp).
  - **Ký Token**: Sử dụng thuật toán bất đối xứng `RS256` hoặc `Ed25519`, hoặc `HS256` với secret key dài tối thiểu 256 bits ngẫu nhiên (`crypto.randomBytes(32)`).

```typescript
// ✅ Thiết lập cookie cho Refresh Token
res.cookie('refreshToken', refreshToken, {
  httpOnly: true, // Chống Javascript XSS đọc trộm
  secure: process.env.NODE_ENV === 'production', // Chỉ gửi qua HTTPS
  sameSite: 'strict', // Chống tấn công CSRF
  path: '/api/v1/auth/refresh',
  maxAge: 7 * 24 * 60 * 60 * 1000 // 7 ngày
});
```

### 4. Hash Mật Khẩu Chuẩn Mực
- **Cấm kỵ**: Tuyệt đối không dùng MD5, SHA-1, SHA-256 thuần để lưu mật khẩu người dùng.
- **Tiêu chuẩn**: Sử dụng **Argon2id** (khuyến nghị số 1) hoặc **bcrypt** với work factor / cost factor $\ge 12$.

```typescript
import bcrypt from 'bcrypt';

const SALT_ROUNDS = 12;
export async function hashPassword(password: string): Promise<string> {
  return await bcrypt.hash(password, SALT_ROUNDS);
}

export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return await bcrypt.compare(password, hash);
}
```

### 5. Vệ Sinh Biến Môi Trường (Secret Hygiene)
- Không commit file `.env`, `.env.production` hay bất kỳ API keys, private keys nào vào Git.
- Sử dụng công cụ `trufflehog` hoặc `gitleaks` trong pre-commit hook để ngăn chặn lộ lọt bí mật.
- Luôn cung cấp file `.env.example` với các giá trị giả lập rõ ràng.

---

## 📋 Checklist Rà Soát Bảo Mật (AppSec Verification)

Trước khi đóng task hoặc tạo Pull Request, kiểm tra 6 mục sau:
- [ ] 1. Mọi endpoint nhận input đều được validate chặt chẽ qua schema (Zod/Pydantic).
- [ ] 2. Không có câu lệnh SQL/NoSQL hay shell command nào ghép chuỗi biến thô.
- [ ] 3. Tất cả các thao tác GET/UPDATE/DELETE tài nguyên nhạy cảm đều có kiểm tra quyền sở hữu (BOLA/IDOR).
- [ ] 4. Token xác thực không lưu ở LocalStorage; mật khẩu được hash bằng bcrypt (cost $\ge 12$) hoặc Argon2id.
- [ ] 5. Đã bật các header bảo mật cơ bản (`helmet` trong Express / Fastify): HSTS, X-Content-Type-Options, CSP.
- [ ] 6. Rate Limit được cấu hình cho các endpoint nhạy cảm (Login, Forgot Password, Send OTP) tối đa 5 req/phút.
