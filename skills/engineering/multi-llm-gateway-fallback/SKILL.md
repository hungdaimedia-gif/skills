---
name: multi-llm-gateway-fallback
description: "Kiến trúc cổng kết nối Đa Mô Hình & Dự Phòng (Multi-LLM Gateway & Fallback): Tự động chuyển đổi giữa Claude, OpenAI, Gemini, DeepSeek, xử lý Rate Limit 429 và tối ưu chi phí Token."
provenance:
  source_repo: "BerriAI/litellm"
  source_url: "https://github.com/BerriAI/litellm"
  source_commit: "5a891e2"
  imported_at: "2026-09-15T11:34:00+07:00"
  stars_at_import: 24500
  forks_at_import: 3200
---

# 🌐 Multi-LLM Gateway & Fallback — Cổng Kết Nối Đa Mô Hình Bất Tử

> **Triết lý cốt lõi**: "Phụ thuộc vào duy nhất một nhà cung cấp LLM là rủi ro kinh doanh chí mạng". Khi OpenAI gặp sự cố mạng (503 Service Unavailable) hoặc Anthropic bị chạm trần hạn mức (429 Rate Limit Exceeded), toàn bộ hệ thống Agent của bạn sẽ tê liệt nếu không có **Cổng kết nối dự phòng tự động chuyển đổi (Automatic Failover Gateway)**.

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Bạn đang viết code gọi API LLM cho hệ thống Production có người dùng thật 24/7.
2. Ứng dụng thường xuyên bị lỗi chạm trần gọi nhanh (`429 Too Many Requests` hoặc `Rate limit exceeded`).
3. Cần tối ưu chi phí: Dùng model rẻ/nhanh (Claude Haiku 3.5 / GPT-4o-mini / DeepSeek) cho tác vụ phân loại đơn giản, chỉ kích hoạt model đắt tiền (Claude Sonnet 3.7 / GPT-4o) khi cần suy luận phức tạp.
4. Muốn hỗ trợ chạy Local LLM (Ollama, vLLM) làm phương án dự phòng khi mất kết nối mạng bên ngoài.

---

## 🔄 BƯỚC 1: Chuỗi Dự Phòng Đa Tầng (Multi-Tier Fallback Chain)

Thiết kế danh sách mô hình dự phòng theo thứ tự ưu tiên:

```text
[Yêu cầu từ Agent]
        │
        ▼
[1. Ưu tiên 1: Claude 3.7 Sonnet] ──(Thành công)──> Hoàn tất
        │
    (Gặp lỗi 429 / 500 / Timeout 30s)
        │
        ▼
[2. Dự phòng 1: GPT-4o] ────────────(Thành công)──> Hoàn tất
        │
    (Gặp sự cố tiếp)
        │
        ▼
[3. Dự phòng 2: Gemini 1.5 Pro] ────(Thành công)──> Hoàn tất
        │
    (Mất mạng hoàn toàn)
        │
        ▼
[4. Cứu hộ khẩn cấp: Local Ollama (Qwen2.5-Coder)]
```

---

## ⚡ BƯỚC 2: Triển Khai Bộ Bọc Tự Động Thử Lại (Exponential Backoff & Failover Wrapper)

```ts
interface CompletionOptions {
  messages: Array<{ role: string; content: string }>;
  tools?: any[];
}

const MODEL_HIERARCHY = [
  { provider: "anthropic", model: "claude-3-7-sonnet-20250219" },
  { provider: "openai", model: "gpt-4o" },
  { provider: "google", model: "gemini-1.5-pro" },
  { provider: "deepseek", model: "deepseek-chat" },
];

async function executeLlmWithFallback(options: CompletionOptions) {
  let lastError = null;

  for (const target of MODEL_HIERARCHY) {
    try {
      console.log(`📡 Đang gọi model: [${target.provider}] ${target.model}...`);
      const response = await callProviderApi(target.provider, target.model, options, { timeoutMs: 25000 });
      return response; // Thành công -> Trả về ngay
    } catch (error: any) {
      console.warn(`⚠️ Lỗi từ [${target.provider}] (${error.status || error.message}) -> Đang kích hoạt Fallback...`);
      lastError = error;
      // Nếu là lỗi rate limit (429), chờ nhẹ 1 giây trước khi nhảy sang provider tiếp theo
      if (error.status === 429) {
        await new Promise((res) => setTimeout(res, 1000));
      }
    }
  }

  throw new Error(`Toàn bộ ${MODEL_HIERARCHY.length} nhà cung cấp LLM đều thất bại! Lỗi cuối: ${lastError?.message}`);
}
```

---

## 💰 BƯỚC 3: Phân Luồng Thông Minh Theo Chi Phí (Cost-Aware Routing)

Không dùng dao mổ trâu để giết gà:
* **Tác vụ phân loại (Routing, Intent detection, Sentiment)**: Điều hướng sang model siêu rẻ `gpt-4o-mini` hoặc `claude-3-5-haiku` (tiết kiệm 90% chi phí).
* **Tác vụ viết code, giải thuật, review logic**: Điều hướng sang `claude-3-7-sonnet`.
* **Tác vụ toán học, suy luận chuỗi dài (Reasoning)**: Điều hướng sang `deepseek-r1` hoặc `o3-mini`.

---

## 🎯 CÂU HỎI KIỂM ĐỊNH (Checklist)
* Hệ thống đã có danh sách mô hình dự phòng ít nhất 2 nhà cung cấp khác nhau chưa?
* Đã có cấu hình `timeout` (ví dụ 25-30s) để không bị treo request vô tận khi nhà cung cấp bị nghẽn mạng chưa?
* Đã bật lưu vết (Telemetry) ghi nhận chi phí token của từng nhà cung cấp chưa?
