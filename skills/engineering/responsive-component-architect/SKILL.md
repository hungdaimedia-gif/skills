---
name: responsive-component-architect
description: "Kiến trúc component giao diện tương tác (Shadcn/ui, Tailwind, Radix): Phân tách Presentational vs Container, State machine, Responsive Grid và Mobile-First."
provenance:
  source_repo: "PatrickJS/awesome-cursorrules"
  source_url: "https://github.com/PatrickJS/awesome-cursorrules"
  source_commit: "f82b1c4"
  imported_at: "2026-09-15T11:23:00+07:00"
  stars_at_import: 40786
  forks_at_import: 3484
---

# 🧱 Responsive Component Architect — Kiến Trúc Component Chuẩn Mực

> **Triết lý cốt lõi**: Một component hoàn hảo không chỉ đẹp trên màn hình máy tính của lập trình viên, mà phải co giãn mượt mà trên mọi kích thước màn hình từ điện thoại 360px đến màn hình 4K, đồng thời xử lý trọn vẹn 8 trạng thái tương tác (Component State Machine).

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Bạn đang lập trình các UI Components bằng React, Vue, Svelte hoặc Web Components.
2. Sử dụng thư viện Tailwind CSS, Shadcn/ui, Radix UI hoặc tự viết CSS component.
3. Component bị vỡ layout khi co màn hình nhỏ (RenderFlex overflow, text tràn ra ngoài).
4. Component thiếu các trạng thái quan trọng như: Loading Skeleton, Empty Data, Error State.

---

## 🏛️ BƯỚC 1: Phân Tách 2 Tầng — Presentational vs Container

Tuyệt đối không nhồi nhét logic gọi API, quản lý state phức tạp vào cùng một file render HTML/CSS:
* **Presentational Component (UI thuần túy - Dumb Component)**:
  * Chỉ nhận dữ liệu qua `props`.
  * Không gọi `fetch()`, không dính líu đến backend hay redux store trực tiếp.
  * 100% độc lập, dễ viết Storybook hoặc Preview.
* **Container Component (Smart Component / Hook)**:
  * Đảm nhiệm việc fetch dữ liệu, caching, validate form, xử lý lỗi.
  * Truyền dữ liệu sạch xuống cho Presentational component hiển thị.

---

## 🔄 BƯỚC 2: Kiểm Soát Trọn Vẹn 8 Trạng Thái (8-State Machine)

Mỗi component tương tác (Button, Card, Table, Input) bắt buộc phải được thiết kế và kiểm thử qua đủ 8 trạng thái:

```text
[1. Default] ──────> [2. Hover] ──────> [3. Active / Pressed]
       │
       ├────────────> [4. Focus-Visible (Keyboard Tab)]
       │
       ├────────────> [5. Loading / Skeleton]
       │
       ├────────────> [6. Disabled]
       │
       ├────────────> [7. Empty State (Không có dữ liệu)]
       │
       └────────────> [8. Error State (Báo lỗi & nút Retry)]
```

### Triển khai ví dụ với Tailwind CSS:
```tsx
export function PrimaryButton({ children, isLoading, isDisabled, ...props }) {
  return (
    <button
      disabled={isDisabled || isLoading}
      className="
        inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-semibold
        bg-indigo-600 text-white shadow-sm transition-all duration-150
        hover:bg-indigo-500 hover:shadow-md hover:-translate-y-0.5
        active:translate-y-0 active:bg-indigo-700
        focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2
        disabled:pointer-events-none disabled:opacity-50 disabled:shadow-none
      "
      {...props}
    >
      {isLoading ? <Spinner className="animate-spin h-4 w-4" /> : children}
    </button>
  );
}
```

---

## 📱 BƯỚC 3: Thiết Kế Mobile-First & Container Queries

1. **Nguyên tắc Mobile-First**:
   * Luôn viết CSS mặc định cho màn hình nhỏ điện thoại trước.
   * Chỉ dùng tiền tố `sm:`, `md:`, `lg:`, `xl:` để mở rộng layout khi màn hình to dần ra.
   * Tuyệt đối tránh viết code cho desktop trước rồi mới còng lưng sửa lỗi trên mobile.

2. **Áp dụng Grid co giãn tự động (Fluid Auto-Fit)**:
   Không cần phải định nghĩa hàng chục breakpoint cứng, dùng hàm `repeat(auto-fit, minmax(...))` để danh sách card tự động dàn đều:
   ```css
   .card-grid {
     display: grid;
     grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
     gap: 1.5rem;
   }
   ```

---

## 🧩 BƯỚC 4: Compound Component Pattern & Slot Composition

Để component linh hoạt, tránh bị "bệnh truyền cả chục tham số prop" (`buttonProps`, `titleProps`, `iconProps`...):
Sử dụng mô hình ghép nối Component (Composition):

```tsx
<Modal open={isOpen} onClose={handleClose}>
  <Modal.Header title="Xác nhận xóa tài khoản" />
  <Modal.Body>
    <p>Hành động này sẽ xóa vĩnh viễn dữ liệu của bạn.</p>
  </Modal.Body>
  <Modal.Footer>
    <Button variant="ghost" onClick={handleClose}>Hủy</Button>
    <Button variant="danger" onClick={handleDelete}>Xóa vĩnh viễn</Button>
  </Modal.Footer>
</Modal>
```

---

## 🎯 CÂU HỎI KIỂM ĐỊNH (Checklist)
* Component có bị tràn (overflow) khi màn hình chỉ rộng 360px không?
* Đã có giao diện Skeleton hiển thị trong lúc chờ dữ liệu API chưa?
* Khi người dùng không có dữ liệu (Empty state), component hiển thị như thế nào?
