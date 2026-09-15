---
name: mobile-touch-interaction-ux
description: "Thiết kế trải nghiệm cảm ứng di động (Mobile Touch UX): Xử lý Safe Area insets (tai thỏ & home bar iPhone), Bottom Sheet, vùng chạm ngón tay (Tap Targets) và chống bàn phím ảo che khuất."
provenance:
  source_repo: "akveo/react-native-ui-kitten"
  source_url: "https://github.com/akveo/react-native-ui-kitten"
  source_commit: "9c12e8a"
  imported_at: "2026-09-15T11:27:00+07:00"
  stars_at_import: 10667
  forks_at_import: 962
---

# 📱 Mobile Touch & Interaction UX — Trải Nghiệm Cảm Ứng Di Động Đỉnh Cao

> **Triết lý cốt lõi**: Màn hình điện thoại được thao tác bằng **ngón tay cái (Thumb Zone)** chứ không phải con trỏ chuột chính xác từng pixel. Một giao diện di động chuẩn phải tính đến vùng an toàn (Safe Area), độ lớn của ngón tay người dùng và không bao giờ để bàn phím ảo che mất nút bấm quan trọng.

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Bạn đang tối ưu giao diện web/app cho điện thoại thông minh (iOS Safari, Android Chrome, PWA, React Native).
2. Nút bấm ở chân trang bị thanh Home Bar của iPhone che mất hoặc nội dung chạm vào tai thỏ (Notch / Dynamic Island).
3. Người dùng bấm nhầm nút vì các phần tử đặt quá sát nhau (ngón tay to bấm trúng 2 nút cùng lúc).
4. Khi bấm vào ô nhập liệu (Input), bàn phím ảo trồi lên che khuất nút "Gửi / Xác nhận".

---

## 📐 BƯỚC 1: Xử Lý Vùng An Toàn Màn Hình (iOS Safe Area Insets)

Bắt buộc cấu hình viewport hỗ trợ phủ kín màn hình tràn viền:

```html
<!-- Trong thẻ <head> của HTML -->
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
```

### Sử dụng biến CSS Safe Area:
```css
:root {
  --sat: env(safe-area-inset-top, 0px);
  --sab: env(safe-area-inset-bottom, 0px);
}

/* Header không bị lẹm vào camera / Dynamic Island */
.mobile-header {
  padding-top: calc(12px + var(--sat));
}

/* Footer & Nút bấm cố định ở đáy không bị thanh Home Bar che */
.mobile-bottom-bar {
  padding-bottom: calc(16px + var(--sab));
}
```

---

## 👆 BƯỚC 2: Vùng Chạm Ngón Tay Chuẩn Nhân Trắc Học (Tap Targets ≥ 48px)

Theo chuẩn thiết kế của Apple (Human Interface Guidelines) và Google (Material Design):
* **Kích thước vùng bấm tối thiểu**: **48px × 48px** (không phải kích thước mắt nhìn của icon, mà là vùng bấm nhận diện cảm ứng).
* **Khoảng cách tối thiểu giữa 2 nút bấm**: **8px** (chống bấm nhầm).

```css
/* Tăng diện tích bấm mà không làm icon bị to thô kệch */
.touch-target {
  min-width: 48px;
  min-height: 48px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  -webkit-tap-highlight-color: transparent; /* Bỏ vệt xám nhấp nháy xấu xí trên Safari */
}
```

---

## 🗂️ BƯỚC 3: Ưu Tiên Thao Tác Ở Chân Trang (Thumb-Zone & Bottom Sheet)

Ngón tay cái người dùng khó với lên 2 góc trên cùng của điện thoại. Do đó:
* Thay thế Popup Modal ở giữa màn hình bằng **Bottom Sheet (Bảng kéo từ đáy lên)**.
* Đặt các nút điều hướng quan trọng (Navigation Bar, CTA mua hàng) ở nửa dưới màn hình.
* Hỗ trợ cử chỉ vuốt xuống nhẹ để đóng bảng (`swipe down to dismiss`).

---

## ⌨️ BƯỚC 4: Chống Bàn Phím Ảo Che Khuất (Virtual Keyboard Avoidance)

Khi người dùng chạm vào ô input ở cuối trang, bàn phím ảo trồi lên có thể đẩy văng hoặc che lấp nút bấm:
```css
/* Sử dụng đơn vị dvh (Dynamic Viewport Height) thay cho 100vh lỗi thời */
.mobile-screen {
  min-height: 100dvh; /* Tự động co lại khi bàn phím ảo xuất hiện */
  display: flex;
  flex-direction: column;
}

.form-scroll-container {
  flex: 1;
  overflow-y: auto;
  scroll-padding-bottom: 20px;
}
```

---

## 🎯 CÂU HỎI KIỂM ĐỊNH (Checklist)
* Giao diện đã có `viewport-fit=cover` và `env(safe-area-inset-bottom)` chưa?
* Mọi nút bấm trên điện thoại có đạt kích thước tối thiểu 48px × 48px không?
* Khi bàn phím ảo mở lên, nút submit có còn nhìn thấy và bấm được không?
