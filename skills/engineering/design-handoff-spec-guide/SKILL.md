---
name: design-handoff-spec-guide
description: "Quy chuẩn bàn giao thiết kế sang lập trình (Design Handoff & Spec Guide): Chuyển hóa bản vẽ Figma thành code sạch, quy chuẩn đặt tên Token, trích xuất tài nguyên đa phân giải (1x, 2x, 3x, WebP) và tài liệu hóa Edge Cases."
provenance:
  source_repo: "VoltAgent/awesome-design-md"
  source_url: "https://github.com/VoltAgent/awesome-design-md"
  source_commit: "d3e89a1"
  imported_at: "2026-09-15T11:27:00+07:00"
  stars_at_import: 115902
  forks_at_import: 13019
---

# 🤝 Design Handoff & Spec Guide — Bàn Giao Thiết Kế Sang Code Chuẩn Xác

> **Triết lý cốt lõi**: Sự đứt gãy lớn nhất giữa Designer và Developer là: "Designer vẽ bản đẹp trên Figma, nhưng Developer code ra một sản phẩm sai lệch tỉ lệ và vỡ vụn khi gặp dữ liệu thực tế". Một bản Handoff hoàn hảo phải nói chung một ngôn ngữ kỹ thuật: có Token rõ ràng, lường trước các trường hợp văn bản dài/ngắn bất thường và có tài liệu đặc tả tương tác.

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Bạn đang chuyển giao một bản vẽ Figma/UI mockup thành code HTML/CSS/React thực tế.
2. Code giao diện bị "lệch màu, lệch font, lệch khoảng cách" so với thiết kế gốc.
3. Giao diện bị vỡ khi gặp tên người dùng quá dài, mô tả sản phẩm 5 dòng hoặc ảnh tải thất bại.
4. Cần đóng gói thư mục tài nguyên hình ảnh (Assets) theo đúng tỷ lệ chuẩn retina display (1x, 2x, 3x) và định dạng hiện đại (WebP, SVG).

---

## 🔤 BƯỚC 1: Thống Nhất Bảng Từ Điển Tên Biến (Token Mapping Table)

Tuyệt đối không để Developer tự "đo pixel" thủ công từng phần tử. Designer và Coder phải thống nhất chung một bộ Token:

| Tên Token Trong Figma | Giá Trị CSS Biến | Class Tailwind Tương Đương |
| :--- | :--- | :--- |
| `Color/Brand/Primary` | `--accent-primary: #6366f1` | `bg-indigo-600` |
| `Color/Surface/Card` | `--bg-surface: #111827` | `bg-gray-900` |
| `Spacing/md` | `--spacing-md: 16px` | `p-4` / `gap-4` |
| `Radius/lg` | `--radius-lg: 12px` | `rounded-xl` |
| `Shadow/Glow` | `--shadow-glow: 0 0 20px ...` | `shadow-glow` |

---

## 💣 BƯỚC 2: Kiểm Thử 4 Tình Huống Cực Đoan (Edge Cases Checklist)

Một bản thiết kế đẹp chỉ là 50% chặng đường. Bắt buộc phải đặc tả 4 tình huống dữ liệu biên:
1. **Văn bản quá dài (Long Content Overflows)**:
   * Họ tên dài 40 ký tự có bị nhảy dòng làm vỡ nút không?
   * Có cần cắt bớt bằng dấu 3 chấm (`text-ellipsis` & `line-clamp-2`) không?
2. **Văn bản quá ngắn hoặc rỗng (Empty Content)**:
   * Nếu user không đặt tên, hiển thị placeholder gì?
3. **Ảnh không tải được (Broken Images)**:
   * Có avatar mặc định (Fallback Avatar) hoặc icon placeholder không?
4. **Mất mạng hoặc lỗi máy chủ (Offline / 500 State)**:
   * Có nút "Thử lại (Retry)" để người dùng không bị kẹt không?

---

## 🖼️ BƯỚC 3: Quy Chuẩn Xuất Tài Nguyên Đồ Họa (Asset Export Standards)

* **Icon & Logo**: 100% xuất định dạng **SVG** (vector sắc nét trên mọi màn hình, dung lượng nhẹ).
* **Ảnh chụp, Poster, Banner**:
  * Định dạng hiện đại: **WebP** hoặc **AVIF** (nhẹ hơn PNG/JPG 40%).
  * Xuất 2 phiên bản: `1x` (màn hình thường) và `2x` (Retina display / iPhone) kèm cú pháp `<picture>` hoặc `srcset`:

```html
<picture>
  <source srcset="hero-banner.webp 1x, hero-banner@2x.webp 2x" type="image/webp">
  <img src="hero-banner.jpg" alt="Mô tả banner" loading="lazy" decoding="async">
</picture>
```

---

## 📝 BƯỚC 4: Bảng Đặc Tả Hành Vi Tương Tác (Interaction Spec)

Mọi component phức tạp (như Modal, Dropdown) phải ghi chú rõ:
* Bấm ra ngoài (Click outside) có tự đóng không?
* Bấm phím `ESC` trên bàn phím có đóng modal không?
* Focus chuột vào ô đầu tiên (Autofocus) khi popup hiện lên không?
* Thanh cuộn (Scrollbar) của trang nền có bị khóa lại khi modal mở không?

---

## 🎯 CÂU HỎI KIỂM ĐỊNH (Checklist)
* Tên biến trên code có khớp 1-1 với tên Style trên Figma không?
* Đã có ảnh fallback khi link ảnh bị chết (404) chưa?
* Ảnh banner đã có định dạng WebP và thuộc tính `loading="lazy"` chưa?
