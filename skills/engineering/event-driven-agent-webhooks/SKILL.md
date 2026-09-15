---
name: event-driven-agent-webhooks
description: "Kích hoạt Agent theo sự kiện & Webhooks: Kết nối Agent với GitHub, Telegram, Discord, Stripe, xác thực chữ ký HMAC chống giả mạo và xử lý hàng đợi bất đồng bộ."
provenance:
  source_repo: "anthropics/anthropic-quickstarts"
  source_url: "https://github.com/anthropics/anthropic-quickstarts"
  source_commit: "9c3f81e"
  imported_at: "2026-09-15T11:34:00+07:00"
  stars_at_import: 21500
  forks_at_import: 2600
---

# ⚡ Event-Driven Agent Webhooks — Kích Hoạt Agent Theo Sự Kiện Bất Đồng Bộ

> **Triết lý cốt lõi**: AI Agent không thể ngồi im thụ động chờ con người mở chat để gõ lệnh. Một hệ thống tự hành thực thụ phải **tự động thức tỉnh khi có sự kiện từ thế giới bên ngoài** (Có người mở Pull Request trên GitHub, có tin nhắn mới từ khách hàng trên Telegram/Slack, hoặc có giao dịch thanh toán thành công).

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Cần xây dựng Agent tự động review code mỗi khi có ai đó mở Pull Request trên GitHub/GitLab.
2. Cần kết nối Agent với **Telegram Bot**, **Discord Bot** hoặc **Slack Webhooks**.
3. Cần lắng nghe sự kiện từ bên thứ ba (Stripe payment, Hubspot webhook, Jira ticket created) và tự động kích hoạt Agent xử lý.
4. Tác vụ của Agent chạy lâu (1–3 phút) và cần phản hồi HTTP 200 ngay lập tức cho Webhook provider, sau đó đẩy việc vào hàng đợi xử lý nền (Background Queue).

---

## 🔐 BƯỚC 1: Xác Thực Chữ Ký Webhook Bằng HMAC-SHA256 (Chống Giả Mạo)

Tuyệt đối không bao giờ tin tưởng một request webhook nếu chưa kiểm tra chữ ký bí mật (Signature verification). Kẻ gian có thể gửi request giả mạo để lừa Agent thực thi mã độc!

### Triển khai xác thực GitHub Webhook bằng Node.js:
```ts
import crypto from 'crypto';

export function verifyWebhookSignature(payloadRaw: string, signatureHeader: string, secret: string): boolean {
  if (!signatureHeader || !secret) return false;
  
  // 1. Tạo chữ ký từ raw body và secret
  const hmac = crypto.createHmac('sha256', secret);
  const digest = 'sha256=' + hmac.update(payloadRaw).digest('hex');

  // 2. So sánh an toàn chống tấn công Timing Attack
  try {
    return crypto.timingSafeEqual(Buffer.from(digest), Buffer.from(signatureHeader));
  } catch {
    return false;
  }
}
```

---

## 📬 BƯỚC 2: Kiến Trúc Phản Hồi Nhanh ➔ Đẩy Hàng Đợi (Acknowledge & Queue Pattern)

Hầu hết các nền tảng (GitHub, Stripe, Telegram) sẽ báo lỗi Timeout nếu webhook endpoint của bạn không trả về HTTP 200 trong vòng 5 giây. Trong khi đó, Agent suy luận có thể mất 30–60 giây.

```text
[Webhook Event từ GitHub / Telegram]
                 │
                 ▼
     [1. Webhook Endpoint]
                 │
                 ├─────(A) Trả về ngay HTTP 200 OK (< 50ms)
                 │
                 ▼
     [2. Đẩy Job vào Hàng Đợi Redis / BullMQ]
                 │
                 ▼
     [3. Background Agent Worker] ──> Tự động xử lý, gọi LLM, comment kết quả
```

```ts
// Endpoint nhận Webhook:
app.post('/api/webhooks/github', async (req, res) => {
  // 1. Verify chữ ký HMAC
  const isValid = verifyWebhookSignature(req.rawBody, req.headers['x-hub-signature-256'], WEBHOOK_SECRET);
  if (!isValid) return res.status(401).send("Unauthorized Webhook");

  // 2. Trả về 200 ngay lập tức cho GitHub
  res.status(200).json({ status: "queued" });

  // 3. Đẩy tác vụ vào hàng đợi bất đồng bộ
  const eventType = req.headers['x-github-event'];
  if (eventType === 'pull_request') {
    await agentJobQueue.add('review_pull_request', {
      pr_number: req.body.number,
      repo: req.body.repository.full_name,
    });
  }
});
```

---

## 🤖 BƯỚC 3: Worker Xử Lý Tự Động Phản Hồi Về Nền Tảng

Agent Worker bốc job từ hàng đợi, kích hoạt các skill liên quan (`code-review`, `diagnosing-bugs`) và gửi phản hồi ngược lại nền tảng:
* Nếu là GitHub: Tự động đăng bình luận (PR Review Comment).
* Nếu là Telegram: Dùng Telegram Bot API gửi câu trả lời về nhóm chat.
* Nếu là Slack: Đăng tin nhắn vào kênh kèm các nút bấm tương tác (Slack Blocks).

---

## 🎯 CÂU HỎI KIỂM ĐỊNH (Checklist)
* Webhook endpoint đã có cơ chế xác thực chữ ký số HMAC-SHA256 chưa?
* Endpoint có phản hồi HTTP 200 ngay lập tức trước khi Agent bắt đầu chạy tác vụ dài không?
* Đã có cơ chế chống xử lý trùng lặp (Idempotency Key / Delivery ID) khi nhà cung cấp gửi lại webhook 2 lần không?
