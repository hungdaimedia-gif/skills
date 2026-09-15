---
name: mcp-connector-client-integration
description: "Tích hợp MCP Client vào mã nguồn: Kết nối AI Agent với hệ sinh thái MCP Servers (GitHub, Slack, Postgres, Notion), khám phá công cụ động và quản lý Transport."
provenance:
  source_repo: "modelcontextprotocol/servers"
  source_url: "https://github.com/modelcontextprotocol/servers"
  source_commit: "9f3e1b0"
  imported_at: "2026-09-15T11:34:00+07:00"
  stars_at_import: 38500
  forks_at_import: 4200
---

# 🔌 MCP Connector Client — Tích Hợp Giao Thức Kết Nối MCP Vào Mã Nguồn

> **Triết lý cốt lõi**: Model Context Protocol (MCP) là tiêu chuẩn mở của toàn ngành AI (khởi xướng bởi Anthropic) cho phép một AI Agent kết nối cắm-và-chạy (Plug-and-Play) với bất kỳ hệ thống dữ liệu nào. Thay vì tự viết hàng chục API tích hợp riêng cho GitHub, Slack, Jira, Database ➔ Chỉ cần viết **1 MCP Client duy nhất** trong code của bạn.

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Bạn đang viết code backend (Node.js/TypeScript hoặc Python) cho AI Agent và muốn Agent tự động có sẵn các công cụ kết nối ngoài.
2. Cần kết nối Agent với các MCP Server chính thức:
   * **GitHub MCP**: Tự động tạo Issue, Pull Request, đọc code diff.
   * **Postgres / SQLite MCP**: Cho phép Agent tự chạy truy vấn kiểm tra CSDL an toàn.
   * **Slack / Discord MCP**: Cho phép Agent gửi tin nhắn, đọc kênh chat.
   * **Filesystem MCP**: Cho phép Agent đọc ghi file trong thư mục cho phép.
3. Cần chuyển đổi tự động từ định dạng MCP Tools sang định dạng mà Claude/OpenAI/Gemini có thể gọi trực tiếp.

---

## 🏗️ BƯỚC 1: Khởi Tạo MCP Client Bằng TypeScript SDK

Cài đặt SDK chính thức: `npm install @modelcontextprotocol/sdk`

```ts
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

// 1. Khởi tạo Transport kết nối tới 1 MCP Server (ví dụ: GitHub MCP Server)
const transport = new StdioClientTransport({
  command: "npx",
  args: ["-y", "@modelcontextprotocol/server-github"],
  env: {
    ...process.env,
    GITHUB_PERSONAL_ACCESS_TOKEN: process.env.GITHUB_TOKEN!,
  },
});

// 2. Khởi tạo MCP Client
const mcpClient = new Client(
  { name: "MyAgentClient", version: "1.0.0" },
  { capabilities: { prompts: {}, resources: {}, tools: {} } }
);

await mcpClient.connect(transport);
console.log("✅ Đã kết nối thành công với GitHub MCP Server!");
```

---

## 🔍 BƯỚC 2: Tự Động Khám Phá Tools & Nạp Vào LLM (Dynamic Tool Discovery)

Không cần phải định nghĩa lại schema thủ công. MCP Client tự động kéo danh sách tool về và chuyển hóa thành định dạng của LLM:

```ts
// 1. Kéo toàn bộ danh sách tools mà MCP Server hỗ trợ
const { tools } = await mcpClient.listTools();

// 2. Chuyển đổi sang format của Claude API hoặc OpenAI API
const llmTools = tools.map((tool) => ({
  name: tool.name,
  description: tool.description,
  input_schema: tool.inputSchema, // Chuẩn JSON Schema tương thích 100%
}));

// 3. Khi LLM quyết định gọi tool (Tool Call):
async function handleLlmToolCall(toolName: string, toolInput: any) {
  const result = await mcpClient.callTool({
    name: toolName,
    arguments: toolInput,
  });
  return result.content;
}
```

---

## 🛡️ BƯỚC 3: Rào Chắn Bảo Mật Khi Nhúng MCP (Security Sandbox)

MCP Server có quyền truy cập vào tài nguyên thật của bạn. Bắt buộc áp dụng 3 quy tắc an toàn:
1. **Cô lập quyền hạn (Least Privilege)**: Không chạy MCP Server với quyền Root hoặc token Admin toàn quyền. Dùng token chỉ có quyền đọc (Read-only) nếu Agent chỉ cần tra cứu thông tin.
2. **Khóa thư mục (Filesystem Directory Scoping)**: Nếu dùng Filesystem MCP Server, chỉ cho phép truy cập đúng 1 thư mục dự án cụ thể, tuyệt đối không trỏ vào `/` hoặc `$HOME`.
3. **Con người phê duyệt (Human-in-the-loop)**: Đối với các tool có tính hủy diệt (xóa database, push commit trực tiếp), bắt buộc hiển thị modal xác nhận cho người dùng trước khi gọi `callTool`.

---

## 🎯 CÂU HỎI KIỂM ĐỊNH (Checklist)
* MCP Client đã xử lý sự kiện ngắt kết nối (Reconnection handling) khi tiến trình con bị chết chưa?
* Các biến môi trường nhạy cảm (API Keys, Tokens) có được truyền an toàn qua `env` của Transport không?
* Đã có cơ chế Human-in-the-loop đối với các thao tác ghi dữ liệu nhạy cảm chưa?
