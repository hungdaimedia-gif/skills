---
name: ui-ux-design-system
description: "Quy chuẩn thiết kế giao diện hiện đại: Xây dựng Design Tokens, Palette màu sắc HSL, Typography, Spacing, Micro-interactions và Accessibility (WCAG)."
provenance:
  source_repo: "VoltAgent/awesome-design-md"
  source_url: "https://github.com/VoltAgent/awesome-design-md"
  source_commit: "d3e89a1"
  imported_at: "2026-09-15T11:23:00+07:00"
  stars_at_import: 115902
  forks_at_import: 13019
---

# 🎨 UI/UX Design System — Quy Chuẩn Thiết Kế Giao Diện Đẳng Cấp

> **Triết lý cốt lõi**: Thiết kế giao diện không phải là tô màu tùy tiện. Một giao diện cao cấp (Premium) bắt buộc phải dựa trên **Hệ thống Tokens (Design Tokens)** có quy luật toán học, tôn trọng phân cấp thị giác (Visual Hierarchy) và thân thiện với con người (Accessibility).

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Bạn chuẩn bị xây dựng giao diện người dùng mới (Landing page, Dashboard, Web app, Mobile app).
2. Giao diện trông bị thô, "phẳng lì", màu sắc quê mùa, thiếu chiều sâu hoặc không có điểm nhấn.
3. Cần thiết lập hệ thống Design System chuẩn: Màu sắc (Color Tokens), Typography, Khoảng cách (Spacing 8pt Grid), Hiệu ứng nổi (Elevation & Glassmorphism).
4. Cần tối ưu khả năng truy cập (a11y) theo tiêu chuẩn WCAG 2.1 AA (độ tương phản màu, keyboard navigation).

---

## 📐 BƯỚC 1: Xây Dựng Hệ Thống Design Tokens (Design Tokens Architecture)

Tuyệt đối **không dùng mã màu tùy tiện** rải rác trong code (`#ff0000`, `rgb(23, 45, 67)`). Toàn bộ phải được quy hoạch thành CSS Variables:

### 1. Quy tắc Màu sắc 60-30-10 & Tailored HSL
* **60% Màu nền & Cấu trúc (Background/Surface)**: 
  * Dark mode: Dùng màu xám than sang trọng `#0a0d14` hoặc `hsl(222, 47%, 7%)`, tuyệt đối tránh màu đen tuyền `#000000` gây mỏi mắt.
  * Light mode: Dùng màu trắng sữa ngà `#f8fafc` hoặc `hsl(210, 40%, 98%)`, tránh trắng gắt `#ffffff`.
* **30% Màu hỗ trợ (Secondary / Card / Border)**: Màu thẻ card nổi bật nhẹ, đường viền border tinh tế với độ mờ `rgba(255, 255, 255, 0.08)`.
* **10% Màu nhấn chủ đạo (Primary Accent)**: Màu sắc thương hiệu có độ bão hòa cao (Electric Indigo `hsl(243, 75%, 59%)`, Emerald `hsl(158, 64%, 52%)`, Cyber Cyan `hsl(192, 95%, 50%)`).

```css
:root {
  /* Surface & Base */
  --bg-canvas: #090d16;
  --bg-surface: #111827;
  --bg-surface-elevated: #1e293b;
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-active: rgba(99, 102, 241, 0.4);

  /* Brand Accents */
  --accent-primary: #6366f1;
  --accent-primary-hover: #4f46e5;
  --accent-glow: rgba(99, 102, 241, 0.25);
  --accent-success: #10b981;
  --accent-danger: #ef4444;

  /* Typography Colors */
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --text-faint: #64748b;
}
```

---

## 🔤 BƯỚC 2: Phân Cấp Typography Chuẩn Tỷ Lệ Vàng (Type Scale)

* **Font chữ tiêu chuẩn**:
  * Tiêu đề & Nhãn: `Plus Jakarta Sans` hoặc `Outfit` (hiện đại, geometric).
  * Văn bản nội dung: `Inter` (dễ đọc ở kích thước nhỏ).
  * Mã lệnh & Số liệu: `JetBrains Mono` (cố định độ rộng, dễ so sánh bảng).
* **Tỷ lệ bước nhảy (Modular Scale 1.25 - Major Third)**:
  * `Display / H1`: `2.25rem` (36px) — `font-weight: 800`, `letter-spacing: -0.025em`.
  * `H2`: `1.75rem` (28px) — `font-weight: 700`, `letter-spacing: -0.02em`.
  * `H3`: `1.25rem` (20px) — `font-weight: 600`.
  * `Body Text`: `1rem` (16px) — `line-height: 1.6` (giúp mắt không mỏi khi đọc đoạn văn dài).
  * `Caption / Badge`: `0.75rem` (12px) — `font-weight: 600`, `text-transform: uppercase`.

---

## 📏 BƯỚC 3: Quy Tắc Khoảng Cách 8-Point Grid (Spacing Rhythm)

Toàn bộ padding, margin, gap đều phải là bội số của **4px hoặc 8px**:
* `4px` (xs): Khoảng cách giữa icon và chữ nhỏ.
* `8px` (sm): Padding bên trong badge, khoảng cách giữa các phần tử phụ.
* `16px` (md): Padding chuẩn của input, button, khoảng cách giữa các cột.
* `24px` (lg): Padding của Card thông thường.
* `32px - 48px` (xl - 2xl): Khoảng cách giữa các Section lớn trên trang.

---

## ✨ BƯỚC 4: Chiều Sâu Thị Giác & Vi Tương Tác (Elevation & Micro-interactions)

1. **Hiệu ứng Kính Mờ (Glassmorphism)**:
   ```css
   .glass-card {
     background: rgba(17, 24, 39, 0.7);
     backdrop-filter: blur(16px);
     -webkit-backdrop-filter: blur(16px);
     border: 1px solid rgba(255, 255, 255, 0.08);
     box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
   }
   ```
2. **Hiệu ứng Hover có độ đàn hồi**:
   * Khi hover thẻ Card: Nâng nhẹ `transform: translateY(-2px)`, viền sáng lên và tỏa hào quang `box-shadow: 0 12px 24px -10px var(--accent-glow)`.
   * Thời gian chuyển đổi lý tưởng: `transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1)`.

---

## ♿ BƯỚC 5: Kiểm Định Tiếp Cận & Khả Năng Đọc (Accessibility Gates)

Trước khi nghiệm thu bất kỳ giao diện nào, bắt buộc kiểm tra 3 điều kiện:
* [ ] **Độ tương phản (Contrast Ratio)**: Chữ trên nền phải đạt tối thiểu **4.5:1** (tiêu chuẩn WCAG AA).
* [ ] **Vùng bấm di động (Tap Target)**: Nút bấm trên màn hình cảm ứng phải đạt tối thiểu **44px × 44px**.
* [ ] **Trạng thái Focus (Keyboard Accessible)**: Mọi phần tử bấm được phải có `focus-visible` viền rõ ràng khi bấm phím Tab.

---

## 🎯 CÂU HỎI THẨM ĐỊNH (Checklist)
* Giao diện đã có bảng màu token nhất quán chưa hay vẫn đang dùng mã màu bừa bãi?
* Kích thước chữ và khoảng cách có tuân thủ 8pt grid không?
* Khi người dùng rê chuột hoặc bấm phím Tab, giao diện có phản hồi sinh động không?
