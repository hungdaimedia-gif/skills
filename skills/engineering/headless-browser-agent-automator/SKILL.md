---
name: headless-browser-agent-automator
description: "Tự động hóa trình duyệt cho AI Agent (Playwright & Stagehand): Điều khiển click, điền form, chụp ảnh màn hình, trích xuất cây Accessibility DOM sạch và xử lý Session."
provenance:
  source_repo: "microsoft/playwright"
  source_url: "https://github.com/microsoft/playwright"
  source_commit: "4e912a7"
  imported_at: "2026-09-15T11:34:00+07:00"
  stars_at_import: 68500
  forks_at_import: 3800
---

# 🌐 Headless Browser Agent Automator — Tự Động Hóa Trình Duyệt Cho AI

> **Triết lý cốt lõi**: Đưa toàn bộ mã nguồn thô của một trang web (HTML 50,000 dòng đầy thẻ `div` rác, script, inline CSS) vào LLM sẽ làm nổ tung context window và ngốn sạch token. Một Agent duyệt web xuất sắc chỉ đọc **Cây trợ năng sạch (Accessibility Tree)**, thao tác chính xác bằng các bộ chọn ngữ nghĩa (Semantic Selectors) và duy trì phiên làm việc (Session) bền vững.

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Bạn xây dựng AI Agent cần tự động duyệt web: Cào dữ liệu đối thủ, tự động đăng nhập, tải file báo cáo, đặt lịch hẹn.
2. Cần tương tác với các trang web không có API chính thức (chỉ có giao diện Web HTML/JS).
3. Cần chụp ảnh màn hình (Screenshot) để gửi cho các Multimodal LLM (Claude 3.7 Sonnet, GPT-4o) phân tích thị giác.
4. Cần vượt qua các rào cản cơ bản (chờ trang tải xong Network Idle, tự động giải quyết Cookie Consent Banner).

---

## 🧹 BƯỚC 1: Trích Xuất DOM Siêu Nhẹ Bằng Accessibility Tree (Tiết Kiệm 95% Token)

Thay vì gửi `page.content()` (hàng chục ngàn dòng HTML), hãy xuất cây trợ năng của Playwright:

```ts
import { chromium } from 'playwright';

async function getCleanPageSnapshot(page) {
  // 1. Trích xuất cây Accessibility Tree: Chỉ giữ lại nút bấm, ô nhập liệu, tiêu đề và link
  const snapshot = await page.accessibility.snapshot({ interestingOnly: true });
  
  // 2. Định dạng thành văn bản ngắn gọn có định danh để LLM dễ ra lệnh click:
  function formatA11y(node, depth = 0) {
    const indent = "  ".repeat(depth);
    let out = `${indent}- [${node.role}] "${node.name || ''}"`;
    if (node.value) out += ` (value: "${node.value}")`;
    out += "\n";
    if (node.children) {
      for (const child of node.children) {
        out += formatA11y(child, depth + 1);
      }
    }
    return out;
  }

  return formatA11y(snapshot);
}
```

---

## 🕹️ BƯỚC 2: Các Hành Động Chuẩn Mực Cho Agent Điều Khiển (Agent Action Primitives)

Cung cấp cho Agent 5 công cụ cơ bản với khả năng tự chờ (Auto-waiting):

```ts
// 1. Nhập văn bản an toàn
await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');

// 2. Click nút bấm ngữ nghĩa (Tránh dùng XPath dễ vỡ)
await page.getByRole('button', { name: 'Đăng nhập' }).click({ timeout: 5000 });

// 3. Chờ trạng thái tải mạng ổn định
await page.waitForLoadState('networkidle');

// 4. Chụp ảnh màn hình khu vực nghi vấn
await page.screenshot({ path: 'debug_screen.png', fullPage: false });

// 5. Cuộn trang mượt mà để kích hoạt Infinite Scroll
await page.evaluate(() => window.scrollBy(0, window.innerHeight));
```

---

## 🍪 BƯỚC 3: Quản Lý Phiên & Cookie Bền Vững (Session Reuse)

Tuyệt đối không bắt Agent phải đăng nhập lại từ đầu ở mỗi lượt chạy (tránh kích hoạt mã 2FA hoặc Captcha):

```ts
// Lưu trạng thái đăng nhập (Cookies, LocalStorage) vào file JSON
await context.storageState({ path: 'auth_session.json' });

// Lần sau khởi tạo browser với session có sẵn:
const context = await browser.newContext({
  storageState: 'auth_session.json',
  viewport: { width: 1280, height: 800 },
  userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...',
});
```

---

## 🎯 CÂU HỎI KIỂM ĐỊNH (Checklist)
* Đã lọc DOM sạch trước khi gửi cho LLM chưa hay vẫn đang nhét nguyên cục HTML thô?
* Các câu lệnh click/fill có dùng Semantic Locators (`getByRole`, `getByLabel`) không?
* Đã có cơ chế tái sử dụng `storageState` để không bị vướng form login liên tục chưa?
