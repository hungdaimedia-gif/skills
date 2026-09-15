---
name: svg-icon-visual-assets
description: "Quy chuẩn thiết kế và tối ưu hóa Vector SVG & Hệ thống Icon (Iconography): Chuẩn hóa viewBox 24x24, Stroke-width đồng nhất, nén SVGO, chống vỡ tỷ lệ và kiến trúc SVG Sprite."
provenance:
  source_repo: "lucide-icons/lucide"
  source_url: "https://github.com/lucide-icons/lucide"
  source_commit: "b7e21a0"
  imported_at: "2026-09-15T11:27:00+07:00"
  stars_at_import: 22800
  forks_at_import: 1100
---

# 🪄 SVG & Icon Visual Assets — Hệ Thống Biểu Tượng & Đồ Họa Vector Chuẩn Mực

> **Triết lý cốt lõi**: Một hệ thống icon cẩu thả (icon to icon nhỏ, icon nét thanh nét đậm lẫn lộn, viewBox lung tung) sẽ phá hủy hoàn toàn cảm giác chuyên nghiệp của một sản phẩm. Iconography chuẩn bắt buộc phải có cùng một hệ tọa độ, cùng độ dày nét vẽ (Stroke-weight) và được nén sạch sẽ trước khi đưa vào ứng dụng.

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Bạn đang tạo hoặc nhúng Icon SVG, Logo Vector, Minh họa đồ họa vào web/app.
2. Icon bị co rúm, méo mó hoặc bị nhảy layout khi đổi kích thước CSS.
3. Mã nguồn SVG chứa rác từ phần mềm đồ họa (Illustrator, Inkscape, Figma) như thẻ `metadata`, `comments`, inline styles thừa thãi khiến file nặng nề.
4. Cần đổi màu icon linh hoạt theo màu chữ (`currentColor`) hoặc theo theme Dark/Light.

---

## 📐 BƯỚC 1: Tiêu Chuẩn Lưới Tọa Độ 24×24 (Unified Coordinate System)

Toàn bộ icon trong hệ thống bắt buộc phải được thiết kế trên lưới chuẩn **24px × 24px**:
* **`viewBox="0 0 24 24"`**: Bắt buộc phải có, tuyệt đối không dùng kích thước cố định `width="24" height="24"` mà thiếu `viewBox`.
* **Độ dày đường nét (Stroke Width)**: Cố định `stroke-width="2"` (hoặc `1.5` cho giao diện thanh lịch).
* **Bo góc đường nối (Linecap & Linejoin)**: Dùng `stroke-linecap="round" stroke-linejoin="round"` để các góc nhọn không bị gai mắt.
* **Màu sắc động**: Sử dụng `stroke="currentColor"` hoặc `fill="currentColor"` để icon tự động kế thừa màu chữ của phần tử cha.

```svg
<!-- Mẫu Icon SVG Chuẩn Công Nghiệp (Lucide / Feather Style) -->
<svg 
  xmlns="http://www.w3.org/2000/svg" 
  viewBox="0 0 24 24" 
  fill="none" 
  stroke="currentColor" 
  stroke-width="2" 
  stroke-linecap="round" 
  stroke-linejoin="round"
  class="icon icon-shield"
  aria-hidden="true"
>
  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
</svg>
```

---

## 🧹 BƯỚC 2: Tối Ưu Hóa & Dọn Rác Mã Nguồn SVG (SVGO Compression)

Trước khi commit bất kỳ file `.svg` nào vào dự án, bắt buộc loại bỏ các đoạn rác đồ họa:
* ❌ Xóa các thẻ rác: `<metadata>`, `<!-- Generator: Adobe Illustrator -->`, `<defs>` rỗng, `<title>`.
* ❌ Xóa các thuộc tính style cứng: `style="fill:#FF0000;"` (vì không thể đổi màu bằng CSS).
* ❌ Xóa các ID trùng lặp có thể xung đột với DOM HTML (`id="Layer_1"`).
* *Lợi ích*: Giảm từ 60% đến 85% dung lượng file và tăng tốc độ parse DOM.

---

## 🛡️ BƯỚC 3: Chống Lỗi Vỡ Layout Khi Render Icon Bằng CSS

Để icon không bị co dúm khi đặt cạnh một đoạn văn bản dài trong Flexbox:
```css
.icon {
  width: 1.25rem;  /* 20px */
  height: 1.25rem;
  flex-shrink: 0;   /* CỰC KỲ QUAN TRỌNG: Ngăn chặn Flexbox ép dẹp icon khi màn hình nhỏ */
  display: inline-block;
  vertical-align: middle;
}
```

---

## ♿ BƯỚC 4: Trợ Năng Màn Hình Đọc (SVG Accessibility)

* **Icon mang tính trang trí đi kèm chữ** (ví dụ icon hình phong bì cạnh chữ "Gửi Email"):
  * Thêm `aria-hidden="true"` để phần mềm đọc màn hình (Screen Reader) không đọc vô nghĩa.
* **Icon đứng một mình làm nút bấm** (ví dụ icon thùng rác làm nút Xóa):
  * Bắt buộc phải có `aria-label="Xóa mục này"` hoặc thẻ `<title>Xóa</title>` bên trong.

---

## 🎯 CÂU HỎI KIỂM ĐỊNH (Checklist)
* Toàn bộ icon có chung một hệ quy chiếu `viewBox="0 0 24 24"` không?
* Icon đã được đặt `flex-shrink: 0` để không bị bẹp dúm trên mobile chưa?
* Nút bấm chỉ có icon đã có `aria-label` cho người khiếm thị chưa?
