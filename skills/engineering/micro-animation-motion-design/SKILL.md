---
name: micro-animation-motion-design
description: "Thiết kế chuyển động và vi tương tác (Motion Design & Micro-animations): Quy chuẩn hiệu ứng CSS Transitions, Spring Physics, Staggered Reveal, Shimmer Skeleton và Scroll-driven Animations."
provenance:
  source_repo: "VoltAgent/awesome-design-md"
  source_url: "https://github.com/VoltAgent/awesome-design-md"
  source_commit: "d3e89a1"
  imported_at: "2026-09-15T11:27:00+07:00"
  stars_at_import: 115902
  forks_at_import: 13019
---

# 🪄 Micro-Animation & Motion Design — Chuyển Động Vi Tương Tác Sống Động

> **Triết lý cốt lõi**: Chuyển động (Motion) không phải để khoe kỹ xảo hay làm hoa mắt người dùng. Motion sinh ra để **dẫn dắt sự chú ý (Guiding Attention)**, tạo cảm giác vật lý chân thật (Physical Weight) và xoa dịu sự sốt ruột khi hệ thống đang xử lý dữ liệu.

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Giao diện trang web/ứng dụng cảm giác bị "cứng đơ", giật cục khi mở popup, accordion hay đổi tab.
2. Cần tạo hiệu ứng tải dữ liệu mượt mà (Shimmer Skeleton) thay vì con quay spinner xoay tít nhàm chán.
3. Cần làm hiệu ứng xuất hiện tuần tự (Staggered Animation) cho danh sách thẻ bài viết, danh mục sản phẩm.
4. Cần tinh chỉnh thời gian (Duration) và đường cong gia tốc (Easing Curves) tự nhiên như vật lý ngoài đời thực.

---

## ⏱️ BƯỚC 1: Quy Tắc Thời Lượng & Đường Cong Gia Tốc (Duration & Easing)

Tuyệt đối **không dùng hiệu ứng chuyển động tuyến tính (`transition: linear`)** vì ngoài đời thực không có vật thể nào bắt đầu và dừng lại đột ngột với vận tốc không đổi.

### 1. Thời lượng chuẩn theo kích thước vật thể:
* **Vi tương tác nhỏ (Button hover, Icon scale, Toggle switch)**: `100ms - 200ms`.
* **Phần tử kích thước trung bình (Dropdown menu, Tooltip, Toast notification)**: `200ms - 300ms`.
* **Phần tử lớn (Modal dialog, Sidebar drawer, Page transition)**: `300ms - 450ms`.
* *Lưu ý: Mọi hiệu ứng vượt quá `500ms` sẽ khiến người dùng cảm thấy ứng dụng bị chậm chạp và lag.*

### 2. Đường cong gia tốc tự nhiên (Natural Easing Curves):
* **Xuất hiện (Enter)**: Bắt đầu cực nhanh rồi hãm phanh từ từ (Ease Out).
  ```css
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  ```
* **Biến mất (Exit)**: Bắt đầu chậm rồi lao nhanh biến mất (Ease In).
  ```css
  --ease-in-expo: cubic-bezier(0.7, 0, 0.84, 0);
  ```
* **Vật lý đàn hồi nhẹ (Spring Elastic)**:
  ```css
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  ```

---

## 🌊 BƯỚC 2: Hiệu Ứng Xuất Hiện Tuần Tự (Staggered Reveal)

Khi hiển thị danh sách gồm nhiều thẻ card (như kho skills), cho từng thẻ xuất hiện lệch nhau `0.05s` để tạo làn sóng thị giác tinh tế:

```css
@keyframes cardAppear {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.skill-card {
  animation: cardAppear 0.35s var(--ease-out-expo) backwards;
}

/* Áp dụng độ trễ từng thẻ bằng biến CSS */
.skill-card:nth-child(1) { animation-delay: 0.04s; }
.skill-card:nth-child(2) { animation-delay: 0.08s; }
.skill-card:nth-child(3) { animation-delay: 0.12s; }
.skill-card:nth-child(4) { animation-delay: 0.16s; }
.skill-card:nth-child(5) { animation-delay: 0.20s; }
```

---

## ✨ BƯỚC 3: Hiệu Ứng Ánh Sáng Quét Skeleton (Shimmer Loading)

Thay vì để màn hình trắng xóa hoặc spinner đơn điệu trong lúc fetch API, hiển thị khối hộp xám quét tia sáng mờ ảo:

```css
@keyframes shimmerWave {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.skeleton-box {
  position: relative;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 8px;
}

.skeleton-box::after {
  content: "";
  position: absolute;
  top: 0; right: 0; bottom: 0; left: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.08) 50%,
    transparent 100%
  );
  animation: shimmerWave 1.6s infinite;
}
```

---

## ♿ BƯỚC 4: Tôn Trọng Người Dùng Bị Rối Loạn Tiền Đình (prefers-reduced-motion)

Một số người dùng bị chóng mặt khi màn hình chuyển động quá nhiều. Bắt buộc phải tắt hoạt ảnh nếu hệ điều hành của họ kích hoạt chế độ giảm chuyển động:

```css
@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

---

## 🎯 CÂU HỎI KIỂM ĐỊNH (Checklist)
* Hiệu ứng chuyển động có nhanh gọn (< 400ms) không hay gây ức chế vì bắt người dùng phải chờ?
* Đã dùng đường cong gia tốc tự nhiên (`cubic-bezier`) thay vì `linear` chưa?
* Đã có truy vấn `@media (prefers-reduced-motion)` để bảo vệ người dùng nhạy cảm chưa?
