---
name: system-logs-and-diagnostics
description: Xây và bảo trì hệ Nhật ký hệ thống + Chẩn đoán từ xa cho Chrome Extension MV3. Kích hoạt khi cần thêm dòng log mới, dựng nút "Chẩn đoán" kiểm tra chuỗi kết nối side panel ↔ content script ↔ DOM trang đích, đọc log do người dùng gửi về để tìm nguyên nhân, hoặc gỡ các lỗi kinh điển của log (message port closed, báo động giả, log lộ API key, log biến mất khi đóng panel).
---

# 🩺 NHẬT KÝ HỆ THỐNG & CHẨN ĐOÁN TỪ XA

> Đúc kết từ **HungDaiTool** (Chrome MV3 + React + Zustand), sau một ngày phát
> hiện nút "Chẩn đoán" **chưa từng chạy quá bước 1** kể từ khi được viết.
>
> **Mọi con số và tên hàm dưới đây lấy từ mã nguồn thật.** Chỗ nào là khuyến
> nghị chưa kiểm chứng sẽ ghi rõ.

---

## ⚡ 1. Điều kiện kích hoạt

- *"Thêm dòng log cho bước X"* / *"log ra để biết nó chạy tới đâu"*
- *"Người dùng báo không chạy được mà tôi không biết vì sao"*
- *"Dựng nút Chẩn đoán"* / *"kiểm tra content script còn sống không"*
- *"Log báo `The message port closed before a response was received`"*
- *"Log báo lỗi nhưng thực tế vẫn chạy bình thường"* (báo động giả)

---

## 🎯 2. Vì sao hệ này tồn tại — hiểu sai mục đích là làm hỏng nó

Log **KHÔNG phải** để lập trình viên xem lúc code (đã có DevTools console).
Nó tồn tại vì **một tình huống duy nhất**:

> Người dùng ở xa báo *"không tạo được ảnh"*. Bạn không nhìn thấy máy họ,
> không mở được DevTools của họ, không tái hiện được lỗi trên máy mình.

Log là **đường quan sát duy nhất** vào máy người khác. Mọi quyết định thiết kế
dưới đây đều suy ra từ đúng một câu đó:

| Vì mục đích là vậy… | …nên |
|---|---|
| Người dùng phải gửi được log đi | Có nút **Sao chép** và **Xuất .log** |
| Người dùng không đọc log, họ chỉ gửi | Câu chữ viết cho **bạn**, không cần hoa mỹ |
| Bạn phải tin được thứ đọc trong log | **Báo động giả là lỗi nghiêm trọng** (mục 7) |
| Log đi ra khỏi máy người dùng | **TUYỆT ĐỐI không log bí mật** (mục 6) |

---

## 🏗️ 3. Kiến trúc — 4 mảnh, không hơn

```
addLog()  ──►  useStore().logs  ──►  <LogsTab/>  ──►  Sao chép / Xuất .log
   ▲                                     │
   │                                     └──► nút Chẩn đoán
   │                                              │
   └────────── kết quả trả về ◄── content script ─┘  (DIAGNOSE_FLOW)
```

### 3.1 Kiểu dữ liệu (`src/state/store.ts`)

```ts
export interface LogEntry {
  workflowId: string;                    // 'system' | 'debug' | id workflow thật
  level: 'INFO' | 'WARN' | 'ERROR';
  message: string;
  ts: number;
}

logs: [ { workflowId:'system', level:'INFO',
          message:'hungdaitool Engine initialized successfully', ts: Date.now() } ],
addLog: (entry) => set((s) => ({ logs: [entry, ...s.logs].slice(0, 500) })),
clearLogs: () => set({ logs: [] }),
```

Ba điều phải nhớ:
1. **Prepend** — mới nhất lên đầu. Danh sách đọc từ trên xuống là ngược thời gian.
2. **Trần 500 dòng**, cắt đuôi. Một lượt chạy dài có thể đẩy dòng cũ ra ngoài.
3. **Dòng "Engine initialized successfully" là GIÁ TRỊ KHỞI TẠO**, không phải log
   thật. Thấy nó ở đáy mọi ảnh chụp là bình thường.

### 3.2 💡 LOG ĐÃ ĐƯỢC LƯU BỀN VỮNG — trần an toàn 200 dòng

`logs` **đã được đưa vào `partialize`** của zustand `persist` (từ 2026-09-10).
- **Trần an toàn:** Hạ từ 500 xuống **200 dòng** (`slice(0, 200)`), chỉ chiếm ~20–30 KB, hoàn toàn an toàn trong trần dung lượng của `chrome.storage.local`.
- **Hệ quả thực tế:** Người dùng gặp lỗi, tắt side panel đi làm việc khác rồi mở lại vẫn còn nguyên lịch sử để xuất file `.log` gửi hỗ trợ.
- **Dọn dẹp:** Nút "Xoá sạch" (`clearLogs`) xoá cả trong RAM lẫn trong storage.

### 3.3 Giao diện (`src/tabs/Logs.tsx`)

| Thành phần | Ghi chú |
|---|---|
| Chip lọc `All / INFO / WARN / ERROR` | Kèm số đếm — nhìn phát biết có lỗi không |
| Ô tìm kiếm | Có tô sáng từ khoá khớp (`highlightMessage`) |
| **Sao chép** | Chép **log đang hiển thị** (đã lọc), không phải toàn bộ |
| **Xuất .log** | Tên file `hungdai-flow-YYYYMMDD-HHmmss.log` |
| **Xoá sạch** | Xoá thật, không hoàn tác được |

---

## 🔍 4. Nút "Chẩn đoán" — thiết kế theo CHUỖI, không theo điểm

Sai lầm phổ biến: chẩn đoán chỉ kiểm "có kết nối không". Vô dụng — người dùng
đã biết là không chạy rồi. Cái họ (và bạn) cần biết là **mắt xích nào đứt**.

Nên chẩn đoán phải đi **dọc cả chuỗi**, mỗi bước một câu trả lời dứt khoát:

| Bước | Câu hỏi | Trả lời "không" nghĩa là |
|---|---|---|
| 1 | Có tab trang đích đang mở? | Người dùng chưa mở trang — hết, không cần bước sau |
| 2 | Content script có phản hồi? | Chưa F5 sau khi cập nhật, **hoặc thiếu `case`** (mục 5) |
| 3 | Có ô nhập prompt? | Trang đổi DOM, **hoặc trang dựng theo nhu cầu** (mục 7) |
| 4 | Có nút Tạo? Đang bật hay tắt? | `disabled` khi ô prompt trống là **bình thường** |
| 5 | Đang ở trong dự án hay ngoài trang chủ? | Sai ngữ cảnh — triệu chứng giống hệt lỗi thật |
| 6 | Storage đang giữ dữ liệu gì? | Cache lệch với thực tế |

**Vì sao chia nhỏ đến vậy:** ba nguyên nhân *"chưa mở tab"*, *"chưa F5"*,
*"đang đứng ngoài dự án"* cho ra **triệu chứng y hệt nhau** khi nhìn từ ngoài,
nhưng cách xử khác hẳn. Không tách bạch thì bạn sẽ đoán, và đoán sai.

### 4.1 ⚠️ Lỗi ở bước giữa làm CHẾT mọi bước sau

```ts
if (diagRes?.error) {
  addLog(...); setDiagnosing(false);
  return;          // ← bước 3,4,5,6 KHÔNG BAO GIỜ CHẠY
}
```

Đây chính là cách sự cố ở mục 5 ẩn mình suốt thời gian dài: nhìn log thấy đúng
một dòng lỗi, tưởng "chỉ hỏng chỗ đó", thực ra **cả nửa sau của chẩn đoán chưa
từng chạy**. Khi dựng chẩn đoán, hãy tự hỏi: *bước này hỏng thì còn bao nhiêu
bước phía sau không được chạy?*

---

## 💣 5. CẠM BẪY SỐ 1: gửi tin mà không ai nhận

### Sự cố thật (2026-09-10)

`Logs.tsx` gửi `{ type: 'DIAGNOSE_FLOW' }`. Content script **không hề có
`case 'DIAGNOSE_FLOW'`** ⇒ rơi xuống `default: break;` ⇒ **không ai gọi
`sendResponse`** ⇒ Chrome đóng cổng:

```
The message port closed before a response was received.
```

Giao diện dịch câu đó thành *"Content script chưa phản hồi, hãy F5 tab"* —
**một câu đổ lỗi sai**: F5 bao nhiêu lần cũng vẫn thế.

### Vì sao TypeScript im lặng

Vì `'DIAGNOSE_FLOW'` **chưa từng được khai** trong union `RuntimeMessage`.
Không có trong union ⇒ không có gì để đối chiếu ⇒ thiếu `case` là hợp lệ.

### 🔑 Quy tắc bất di bất dịch

> **Khai type TRƯỚC, viết `case` SAU.**
> Không bao giờ gửi một loại tin chưa có trong union message.

Khai rồi thì lần sau quên `case` là **build chặn ngay** — cơ chế này đã tự chứng
minh: thêm `case` trước khi khai type, `tsc` báo đỏ lập tức.

### Danh sách kiểm cho mọi tin mới

- [ ] Đã khai `interface XxxMsg` và nối vào union `RuntimeMessage`?
- [ ] Content script có `case` tương ứng?
- [ ] **Mọi nhánh** trong `case` đều gọi `sendResponse`? (kể cả nhánh lỗi)
- [ ] Trả lời nằm sau `await` ⇒ đã `return true` để giữ cổng mở?

Thiếu ô cuối là tái hiện đúng lỗi "message port closed" — kể cả khi `case` đã có.

---

## 🔐 6. CẠM BẪY SỐ 2: log là thứ RỜI KHỎI MÁY người dùng

Người dùng bấm **Xuất .log** rồi gửi file đó cho bạn qua Facebook/email. Nên:

> **TUYỆT ĐỐI không `addLog` bất cứ thứ gì là bí mật.**
> API key, token phiên, mật khẩu, nội dung riêng tư.

Kiểm chứng hiện trạng HungDaiTool (2026-09-10) — **đang sạch**:

```bash
grep -rn "apiKey" src/tabs/Logs.tsx src/state/store.ts     # → rỗng
grep -rn "addLog" src/services/geminiService.ts \
                  src/services/elevenlabsService.ts         # → rỗng
```

Hai file BYOK **cố ý không gọi `addLog`**. Ai thêm log vào đó sau này phải giữ
nguyên tính chất này. Đưa việc kiểm vào thói quen review, vì đây là loại lỗi
**không có test nào bắt được** và hậu quả thì không thu hồi được.

⚠️ Cẩn thận cả với log gián tiếp: `JSON.stringify(response)` có thể kéo theo
trường nhạy cảm mà bạn không ngờ. Log đối tượng thô là rủi ro; hãy chọn trường.

---

## 🐺 7. CẠM BẪY SỐ 3: báo động giả — còn tệ hơn không có chẩn đoán

### Sự cố thật (cùng ngày, ngay trong bản vá cho mục 5)

Chẩn đoán báo `❌ Không tìm thấy ô nhập prompt`, trong khi nút Tạo thì thấy và
lượt bơm prompt thật **thành công**.

**Nguyên nhân:** chẩn đoán dò **đúng một lần, không chờ**. Nhưng trang đích dựng
ô nhập **theo nhu cầu**, còn luồng chạy thật (`insertPrompt()`) **chờ tới 3
giây** cho nó xuất hiện.

⇒ Chẩn đoán **khắt khe hơn** luồng thật ⇒ kết luận "hỏng" trong khi mọi thứ bình
thường ⇒ người dùng đi tìm lỗi không tồn tại.

### 🔑 Quy tắc

> **Chẩn đoán phải dò bằng ĐÚNG điều kiện luồng chạy thật dùng — kể cả thời
> gian chờ.**
> Khắt khe hơn ⇒ báo động giả. Lỏng hơn ⇒ bỏ sót lỗi thật.

Cụ thể:
- **Dùng lại đúng hàm dò của luồng thật** (`findFlowPromptEditor()`,
  `findSubmitButton()`), **không viết selector riêng cho chẩn đoán**. Hai bộ
  selector song song sẽ phân kỳ, và chẩn đoán sẽ nói về một thế giới khác với
  thế giới mà lượt chạy thật nhìn thấy.
- **Chờ tương đương, được phép ngắn hơn** — nhưng khi đó câu chữ phải nói rõ là
  *"chưa thấy ngay lúc này"*, không phải *"không có"*. (Bản hiện tại: chẩn đoán
  chờ 1.5s, luồng thật chờ 3s.)

### Chọn mức log cho đúng nghĩa

| Mức | Nghĩa | Ví dụ |
|---|---|---|
| `INFO` | Sự thật, kể cả sự thật "chưa thấy" mà **không phải hỏng** | *"Chưa thấy ô nhập ngay lúc này — trang dựng theo nhu cầu"* |
| `WARN` | **Có khả năng** hỏng, đáng để mắt | Dùng đường dự phòng thay vì đường chính |
| `ERROR` | **Chắc chắn** hỏng, việc không hoàn thành | Không tìm thấy tab; content script không phản hồi |

**Đừng đặt `WARN` cho thứ mà chính câu chữ của nó nói là "thường không sao"** —
mâu thuẫn đó làm người đọc mất tin vào toàn bộ hệ log.

---

## 🌐 8. Song ngữ — tách NHÃN và NỘI DUNG

```
t.logs.*        →  NHÃN GIAO DIỆN  (nút, chip, ô tìm kiếm)
t.logs.msg.*    →  NỘI DUNG DÒNG LOG
```

Hai nhóm khác bản chất và đổi theo nhịp khác nhau — gộp chung thì sau này sửa
một cái không biết ảnh hưởng tới đâu.

### ⚠️ Câu có biến để dạng HÀM, không dùng chuỗi thay thế

```ts
// ĐÚNG — TypeScript kiểm được kiểu và số tham số
tabFound: (n: number, title: string, id: number, url: string) => `...`

// SAI — sai một chỗ là in ra chữ "{n}" hoặc "undefined" cho người dùng
tabFound: 'Found {n} tabs...'   →   .replace('{n}', x)
```

Bằng chứng: cách làm bằng hàm **đã bắt được một lỗi thật** —
`chrome.runtime.lastError.message` là `string | undefined`, truyền thẳng vào là
lỗi kiểu, `tsc` chặn ngay. Cách `.replace()` sẽ để nó lọt tới người dùng.

### ⚠️ Khối `en` KHÔNG được TypeScript đối chiếu

`type TranslationMap = typeof translations.vi` ⇒ thiếu khoá bên `en` là **hỏng
im lặng lúc chạy**, build vẫn xanh. **Phải đối chiếu bằng tay** mỗi lần thêm khoá:

```bash
# đếm khoá hai khối msg, phải bằng nhau
```

---

## 💸 9. Nút "Test" trong khu chẩn đoán có thể TIÊU TIỀN

Sự cố thật: nút *"Test gửi prompt"* nghe như phép thử suông, nhưng nó gửi lệnh
thật vào trang đích và **kích hoạt nút Tạo** ⇒ sinh ảnh thật, **trừ credit thật**.

> Mọi nút trong khu chẩn đoán mà **chạm tới hạn mức trả phí** đều phải có bước
> xác nhận nói rõ cái giá, **trước** khi chạy.

Cách viết câu xác nhận cho đúng:
- Nói **hậu quả cụ thể**, không nói chung chung: *"sẽ tạo 1 ảnh THẬT và trừ credit"*.
- **Nhãn nút đồng ý cũng phải mang cái giá**: `Vẫn test (tốn 1 lượt)` — người
  đọc lướt vẫn thấy, không cần đọc hết đoạn văn.
- **Esc = Huỷ**, listener chỉ gắn khi hộp đang mở rồi gỡ ngay.
- Dùng hộp trong giao diện, **không dùng `window.confirm()`**: side panel hẹp,
  hộp thoại gốc của trình duyệt hiện ra thô và lạc tông.

---

## ✅ 10. Danh sách kiểm — thêm một dòng log mới

- [ ] Chọn đúng mức: `INFO` / `WARN` / `ERROR` theo bảng ở mục 7.
- [ ] Chuỗi nằm ở `t.logs.msg.*`, có mặt ở **cả hai** khối `vi` và `en`.
- [ ] Câu có biến ⇒ để dạng **hàm**, không dùng `.replace()`.
- [ ] **Không** log API key / token / nội dung riêng tư, kể cả gián tiếp qua
      `JSON.stringify` một đối tượng thô.
- [ ] Nếu là log của một bước chẩn đoán: dò bằng **đúng hàm và đúng thời gian
      chờ** mà luồng chạy thật dùng.
- [ ] Nếu dòng log kết luận "hỏng": tự hỏi *có trường hợp bình thường nào cũng
      cho ra kết quả này không?* Có ⇒ đổi câu chữ và hạ mức.

## ✅ 11. Danh sách kiểm — thêm một bước chẩn đoán mới

- [ ] Đã khai type message và nối vào union? (mục 5)
- [ ] `case` phía nhận gọi `sendResponse` ở **mọi** nhánh?
- [ ] Trả lời sau `await` ⇒ đã `return true`?
- [ ] Bước này hỏng thì **bao nhiêu bước phía sau bị bỏ qua**? Có nên `return`
      hay nên chạy tiếp phần độc lập? (mục 4.1)
- [ ] Đã thử **cả hai** kịch bản: trạng thái tốt và trạng thái hỏng thật?
      Chẩn đoán chưa từng thấy trạng thái hỏng là chẩn đoán chưa được kiểm.

---

## 🧭 12. Đọc log do người dùng gửi — thứ tự nên theo

1. **Nhìn số đếm chip trước.** `ERROR (0)` mà người dùng vẫn kêu ⇒ vấn đề nằm
   ngoài tầm quan sát của log, đừng đào trong log nữa.
2. **Đọc từ dưới lên** — log prepend, đáy là sớm nhất. Nguyên nhân gốc gần đáy,
   phần trên thường chỉ là hậu quả dây chuyền.
3. **Đối chiếu dòng khởi tạo.** Không thấy *"Engine initialized"* ⇒ người dùng
   gửi log của một phiên khác, hoặc đã bấm Xoá sạch.
4. **Cảnh giác với log thiếu.** Chẩn đoán dừng giữa chừng (mục 4.1) trông rất
   giống chẩn đoán chạy đủ mà không phát hiện gì. **Đếm đủ số bước.**
