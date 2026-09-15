---
name: agent-tool-calling-schema
description: "Quy chuẩn định nghĩa Tool & Function Calling cho AI Agent: Thiết kế JSON Schema, Zod/Pydantic validation, Strict Mode, chống ảo giác tham số và xử lý lỗi Tool Execution."
provenance:
  source_repo: "langchain-ai/langchain"
  source_url: "https://github.com/langchain-ai/langchain"
  source_commit: "7b4c91a"
  imported_at: "2026-09-15T11:34:00+07:00"
  stars_at_import: 146348
  forks_at_import: 24451
---

# 🛠️ Agent Tool Calling Schema — Định Nghĩa Công Cụ Chuẩn Mực Cho AI

> **Triết lý cốt lõi**: AI Agent chỉ thông minh và an toàn khi các công cụ (Tools/Functions) được trang bị cho nó có **Ranh giới tham số rõ ràng (Strict Schema)**, mô tả công năng chính xác và có cơ chế xử lý lỗi tự phục hồi (Self-Correction). Tool không có schema chặt chẽ là nguồn cơn của 90% lỗi ảo giác tham số (Hallucinated Arguments).

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Bạn đang viết mã nguồn (TypeScript, Python, Go) cung cấp Tool cho các LLM (Claude, OpenAI, Gemini, DeepSeek).
2. LLM truyền sai kiểu dữ liệu (truyền chuỗi `"123"` thay vì số `123`, hoặc truyền thiếu các tham số bắt buộc).
3. LLM tự bịa ra tham số không tồn tại trong schema (Hallucination).
4. Tool bị lỗi (API timeout, 404, invalid input) và cần trả về thông báo lỗi có cấu trúc để LLM tự biết đường sửa sai và thử lại.

---

## 📐 BƯỚC 1: Cấu Trúc Định Nghĩa Tool Chuẩn Strict Mode

Bắt buộc cấu hình `strict: true` (hoặc định nghĩa Zod/Pydantic có `additionalProperties: false`):

### 1. Triển khai bằng TypeScript + Zod:
```ts
import { z } from 'zod';

// Định nghĩa Schema tham số cực kỳ chặt chẽ
export const SendEmailToolSchema = z.object({
  recipient_email: z.string().email({ message: "Phải là email hợp lệ, ví dụ user@example.com" }),
  subject: z.string().min(5).max(150).describe("Tiêu đề ngắn gọn của email, không quá 150 ký tự"),
  body_markdown: z.string().min(10).describe("Nội dung email định dạng Markdown"),
  urgency: z.enum(["low", "medium", "high"]).default("medium").describe("Mức độ khẩn cấp"),
  idempotency_key: z.string().uuid().describe("Khóa UUID duy nhất chống gửi trùng lặp"),
}).strict(); // CẤM LLM tự ý thêm trường ngoài schema

export type SendEmailInput = z.infer<typeof SendEmailToolSchema>;

export const sendEmailToolDefinition = {
  name: "send_email",
  description: "Gửi email cho khách hàng hoặc đối tác qua hệ thống gửi thư. Chỉ gọi công cụ này khi đã có sự đồng ý rõ ràng của người dùng.",
  parameters: zodToJsonSchema(SendEmailToolSchema),
};
```

---

## 🛡️ BƯỚC 2: Mô Tả Công Năng Không Mơ Hồ (Tool Docstring Engineering)

Mô tả của Tool là thứ duy nhất LLM đọc để quyết định **khi nào nên gọi** và **khi nào KHÔNG ĐƯỢC gọi**:
* ❌ **Mô tả tồi**: `"Gửi dữ liệu"` (LLM không biết gửi cái gì, gửi đi đâu).
* ✅ **Mô tả chuẩn mực**:
  * **Nêu rõ mục đích**: Tool này làm gì?
  * **Nêu rõ ranh giới**: Khi nào KHÔNG được gọi?
  * **Nêu rõ định dạng đầu vào**: Ví dụ cụ thể của các tham số.

---

## 🔄 BƯỚC 3: Cơ Chế Tự Sửa Sai Khi Tool Lỗi (Self-Healing Loop)

Khi Tool thực thi bị lỗi, tuyệt đối không quăng Exception 500 làm sập ứng dụng. Hãy trả về kết quả lỗi có cấu trúc để LLM đọc và tự sửa:

```ts
async function executeTool(name: string, rawArgs: unknown) {
  // 1. Kiểm tra tính hợp lệ của tham số trước khi chạy
  const parseResult = SendEmailToolSchema.safeParse(rawArgs);
  if (!parseResult.success) {
    return {
      is_error: true,
      error_message: `Tham số không hợp lệ: ${parseResult.error.issues.map(i => `${i.path.join('.')}: ${i.message}`).join(', ')}`,
      suggestion: "Vui lòng xem lại schema và truyền lại đúng định dạng."
    };
  }

  // 2. Chạy logic nghiệp vụ có bọc try/catch
  try {
    const result = await emailService.send(parseResult.data);
    return { is_error: false, data: result };
  } catch (error: any) {
    return {
      is_error: true,
      error_message: `Gửi email thất bại: ${error.message}`,
      suggestion: "Có thể máy chủ SMTP đang quá tải, hãy thử lại sau hoặc báo cho người dùng."
    };
  }
}
```

---

## 🎯 CÂU HỎI KIỂM ĐỊNH (Checklist)
* Schema của Tool đã có `strict: true` (chặn các tham số tự bịa) chưa?
* Mọi tham số đều có trường `.describe()` giải thích rõ ràng và ví dụ mẫu chưa?
* Đã có `idempotency_key` cho các thao tác nhạy cảm (thanh toán, gửi email, xóa dữ liệu) chưa?
