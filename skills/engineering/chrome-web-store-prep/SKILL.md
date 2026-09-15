---
name: chrome-web-store-prep
description: Chuẩn hoá một Chrome Extension để nộp lên Chrome Web Store — rà quyền hạn tối thiểu, quét bảo mật MV3, kiểm icon, dựng script đóng gói .zip không xoá file, soạn store listing và privacy policy. Dùng khi người dùng nói tới "đóng gói extension", "upload CWS", "Chrome Web Store", "publish tiện ích", "rà soát quyền hạn manifest", hoặc khi cần dựng thư mục hồ sơ upload.
---

# Chuẩn hoá Chrome Extension cho Chrome Web Store

Quy trình 7 bước đã chạy thật trên repo `hungdaitool` (07/09/2026). Mỗi bước có
sẵn cái bẫy cụ thể đã vấp phải — đọc phần "Bẫy" trước khi làm bước đó.

## Nguyên tắc bao trùm: KHÔNG XOÁ GÌ CẢ

Repo này có **ĐIỀU 0** trong [`RULES.md`](../../../hungdaitool/RULES.md): agent không được chạy
bất kỳ lệnh xoá/ghi đè nào. Điều đó **không** cản trở việc dọn dẹp — chỉ cần đổi
cách nghĩ:

| Thay vì | Làm thế này |
|---|---|
| Xoá file rác trong `dist/` | Dùng **danh sách cho phép (allowlist)** khi nén — rác không lọt vào zip, vẫn nằm trên đĩa |
| Ghi đè file zip cũ | **Dừng với mã lỗi**, in ra lệnh để người dùng tự chạy |
| Ghi đè file người dùng đã sửa tay | Chỉ ghi khi file **chưa tồn tại**, báo ra màn hình những file đã bỏ qua |

Nhờ vậy mọi script sinh ra đều **chạy lại được nhiều lần** mà không mất dữ liệu.

---

## Bước 1 — Rà quyền hạn (Minimum permissions)

Với **mỗi** quyền trong manifest, tìm nơi gọi thật. Không tìm thấy ⇒ gỡ.

```bash
grep -rhoE "chrome\.[a-zA-Z]+\.[a-zA-Z]+" src/ | sort | uniq -c | sort -rn
```

Đối chiếu bảng đếm này với danh sách `permissions`. Quyền nào không xuất hiện
thì kiểm tra thêm một lượt (có quyền chỉ dùng khai báo, không gọi API) rồi gỡ.

**Các quyền dễ thừa nhất:** `cookies` (kiểm tra cả `document.cookie`),
`webRequest` (thường đã bị `declarativeNetRequest` thay thế), `background`,
`unlimitedStorage`, `notifications`.

### Bẫy 1a — quyền có nơi gọi ẩn

Đừng gỡ vội khi grep ra 0 kết quả. Ba trường hợp cần giữ dù không thấy `chrome.X`:

- `declarativeNetRequest` — dùng qua `rules.json`, không có lời gọi JS nào.
- `activeTab` — **bắt buộc** cho `chrome.tabs.captureVisibleTab` (nếu không có
  `<all_urls>`). Grep `captureVisibleTab` trước khi gỡ.
- `sidePanel` — dùng qua khoá `side_panel` trong manifest.

### Bẫy 1b — pattern `*.` KHÔNG khớp host trần

Đây là lỗi im lặng nguy hiểm nhất, đã gặp thật:

```
❌ https://*.flow-content.google/*     ← KHÔNG khớp https://flow-content.google/...
✅ https://flow-content.google/*       ← phải khai thêm dòng này
```

Luật DNR nhắm host đó **chưa từng chạy** mà không báo lỗi gì. Với mỗi
`host_permissions` dạng `*.`, hãy grep trong `src/` xem URL thật có subdomain
không:

```bash
grep -rhoE "https?://[a-zA-Z0-9._-]+" src/ --include=*.ts --include=*.tsx | sort -u
```

### Bẫy 1c — đừng siết quyền làm hỏng tính năng lõi

Nếu một host pattern rộng (`https://*.googleapis.com/*`) đang phục vụ đường tải
media, **đừng tự siết**. Ghi vào báo cáo là "rủi ro khi duyệt, cần test thủ công
trước khi thu hẹp" và để người dùng quyết. Ở repo này `CLAUDE.md` điều 2 nói rõ:
xung đột thì **tab Gen thắng**.

### Bẫy 1d — Single purpose

CWS đòi tiện ích có **một** mục đích. Nếu extension chạm nhiều trang không liên
quan bề ngoài, hãy diễn đạt chúng là **tính năng phụ trợ cho cùng một mục đích**,
và viết sẵn 1 câu single-purpose để người dùng dán vào Dashboard.

---

## Bước 2 — Quét bảo mật MV3

```bash
# Mã bị cấm — quét cả src/ lẫn bundle đã build
grep -rnE "\beval\s*\(|new Function\s*\(" src/ dist/assets/*.js
grep -rnE "<script[^>]+src=\"https?://" dist/*.html
ls dist/assets/*.map 2>/dev/null          # source map không được lọt vào gói

# Log dữ liệu nhạy cảm
grep -rniE "console\.[a-z]+\([^)]*(token|cookie|authoriz|bearer|password|apikey|secret|credential)" src/

# Bí mật khoá cứng
grep -rniE "(sk-|eyJ[A-Za-z0-9_-]{10,}|api[_-]?key\s*[:=]\s*['\"])" src/
```

### Bẫy 2a — `chrome.scripting.executeScript` có 2 kiểu

`files:` trỏ tới file trong gói ⇒ **an toàn**, khai "No remote code".
`func:` hoặc chuỗi động ⇒ phải xem kỹ. Luôn đọc chỗ gọi, đừng chỉ đếm.

### Bẫy 2b — anon key lộ ra là bình thường, RLS mới là vấn đề

Supabase/Firebase anon key **vốn được thiết kế để lộ** ở client — không phải lỗi
CWS. Nhưng nếu code có `upsert`/`insert` vào bảng người dùng, phải cảnh báo:
**chưa bật Row Level Security thì ai giải nén tiện ích cũng tự cấp quyền cho
mình được**. Đây là lỗ hổng bản quyền thật, nêu vào báo cáo.

### Bẫy 2c — Google Fonts từ xa

CSS/font từ CDN **không** vi phạm luật "remote hosted code" (chỉ mã thực thi mới
tính) nên không chặn duyệt. Nhưng có lộ IP người dùng. Nêu ra, **đừng tự sửa** —
việc đó đụng vào giao diện.

---

## Bước 3 — Kiểm icon bằng cách đọc header PNG

Đừng tin tên file. Đọc thẳng byte:

```bash
node -e "
const fs=require('fs');
for(const f of ['icons/icon-16.png','icons/icon-32.png','icons/icon-48.png','icons/icon-128.png']){
  const b=fs.readFileSync(f);
  if(b.subarray(0,8).toString('hex')!=='89504e470d0a1a0a'){console.log(f,'NOT PNG');continue;}
  const t={0:'Gray',2:'RGB',3:'Palette',4:'GrayAlpha',6:'RGBA'};
  console.log(f, b.readUInt32BE(16)+'x'+b.readUInt32BE(20), t[b[25]], 'alpha='+([6,4,3].includes(b[25])?'yes':'no'));
}"
```

Cần đủ **16/32/48/128**, đúng số đo, có kênh alpha (colorType 6, 4, hoặc 3).

---

## Bước 4 — Script đóng gói

Dựng `scripts/package-zip.mjs`. Bốn yêu cầu bắt buộc:

1. **`manifest.json` ở GỐC zip**, không lồng thư mục `dist/`.
2. **Allowlist**, không xoá — xem nguyên tắc bao trùm ở trên.
3. **Không ghi đè** zip đã có; dừng và in lệnh cho người dùng tự chạy.
4. **Không thêm dependency** — viết bộ ghi ZIP bằng `zlib` có sẵn của Node
   (`deflateRawSync` + bảng CRC32). Giữ `package.json` sạch để reviewer dễ đọc.

Đặt timestamp cố định trong zip ⇒ hai lần build cùng nội dung cho ra file giống
hệt nhau, tiện đối chiếu.

### Bẫy 4a — `dist/_metadata/` làm CWS từ chối thẳng

Chrome tự sinh thư mục này khi nạp extension chưa đóng gói. **Mọi đường dẫn bắt
đầu bằng `_` đều bị CWS từ chối.** Bộ kiểm tra trước khi nén phải bắt được nó.

### Bẫy 4b — file rác thật nằm ở `public/`, không phải `dist/`

Xoá trong `dist/` là vô ích, build sau tạo lại. Muốn dứt điểm phải xoá ở `public/`.
Liệt kê lệnh `git rm` cho người dùng, **không tự chạy**.

### Bẫy 4c — bộ kiểm tra trước khi nén phải có 5 mục này

- Có `manifest.json` ở gốc gói.
- Không có đường dẫn bắt đầu bằng `_`.
- Đủ 4 icon, **đúng số đo đọc từ header PNG**, có alpha.
- **Mọi file mà `manifest.json` trỏ tới đều thực sự nằm trong gói** — bắt được lỗi
  quên cập nhật allowlist sau khi sửa manifest. Quét `background.service_worker`,
  `content_scripts[].js`, `web_accessible_resources[].resources` (bỏ mục có `*`),
  `declarative_net_request.rule_resources[].path`, `side_panel.default_path`.
- Cảnh báo nếu có `.map`, `eval(`, `new Function(`, `<script src>` từ CDN.

---

## Bước 5 — Store listing

### Bẫy 5a — 2 giới hạn ký tự chặn nộp, kiểm ngay từ đầu

| Trường | Nguồn | Giới hạn | Hậu quả nếu vượt |
|---|---|---|---|
| Tiêu đề | `manifest.name` | **45** | Bị cắt cụt trên trang cửa hàng |
| Mô tả ngắn | `manifest.description` | **132** | Dashboard **từ chối không cho lưu** |

```bash
node -e "const m=require('./dist/manifest.json');console.log('name',m.name.length+'/45','| desc',m.description.length+'/132')"
```

Cả hai đều **lấy thẳng từ manifest**, không phải ô nhập riêng — nên phải sửa
trong `manifest.config.ts` (hoặc `manifest.json`), không phải sửa trên Dashboard.

### Bẫy 5b — thiếu đoạn phủ nhận thương hiệu

Nếu extension thao tác trên sản phẩm của hãng khác hoặc mang tên hãng đó, **bắt
buộc** có đoạn kiểu: *"X là sản phẩm độc lập, không liên kết, không được tài trợ
và không được Y xác nhận. Y là thương hiệu của Y LLC."* Thiếu là lý do bị từ chối
vì mạo nhận thương hiệu.

### Bẫy 5c — `minimum_chrome_version`

`chrome.sidePanel` cần Chrome ≥ 114. Khai `minimum_chrome_version` để Chrome cũ
không cài rồi mới hỏng.

---

## Bước 6 — Privacy policy: PHẢI TRUNG THỰC

**Đây là bước dễ làm sai nhất, và làm sai thì bị gỡ khỏi cửa hàng.**

Người dùng thường yêu cầu viết *"tiện ích chỉ lưu trên thiết bị, không gửi dữ
liệu về server bên thứ ba nào"*. **Đừng viết câu đó chỉ vì được yêu cầu.** Kiểm
chứng trước:

```bash
grep -rn "supabase\|firebase\|analytics\|gtag\|amplitude\|sentry\|mixpanel" src/ -il
grep -rhoE "https?://[a-zA-Z0-9._-]+" src/ --include=*.ts --include=*.tsx | sort -u
```

Nếu có gửi dữ liệu đi thật:

1. Tìm **chính xác** những trường nào được gửi (đọc chỗ `insert`/`upsert`/`post`).
2. Xác minh tính năng đó **đang bật**, không phải mã chết — grep xem component
   có được render không.
3. Viết chính sách **trung thực**, nhưng bố cục theo hướng trấn an đúng chỗ:
   - Cái người dùng quan tâm nhất (nội dung họ tạo) — nói rõ là **không rời máy**.
   - Cái thật sự được gửi — nói rõ **chỉ khi họ tự bấm**, và liệt kê từng trường.
4. **Báo lại cho người dùng** rằng bạn đã viết khác yêu cầu và tại sao, kèm lối
   ra: muốn câu gốc thành sự thật thì phải gỡ tính năng nào.
5. Nhắc họ tick **"Personally identifiable information"** ở mục Data usage.

Google đối chiếu chính sách khai báo với hành vi thật của mã. Khai sai = gỡ khỏi
cửa hàng.

---

## Bước 7 — Dựng thư mục hồ sơ upload

`scripts/make-upload-folder.mjs` sinh ra `cws-upload/` — mỗi ô trên Dashboard một
file, dán thẳng không phải cắt gọt:

```
cws-upload/
├── README.md                          ← checklist theo đúng thứ tự bấm
├── 1-tien-ich/<tên>.zip               ← kéo thả vào ô upload
├── 2-noi-dung-hien-thi/
│   ├── tieu-de.txt                    ← sinh từ manifest.name
│   ├── mo-ta-ngan.txt                 ← sinh từ manifest.description
│   ├── mo-ta-chi-tiet.txt             ← trích từ khối ```text trong STORE_LISTING.md
│   └── giai-trinh-quyen.md            ← 1 mục / 1 quyền, lặp theo manifest.permissions
├── 3-quyen-rieng-tu/PRIVACY_POLICY.md
└── 4-anh-chup-man-hinh/               ← chỗ người dùng bỏ ảnh 1280×800 vào
```

### Bẫy 7a — chốt chặn zip cũ (quan trọng nhất)

Script **phải** đọc `manifest.json` *bên trong* file zip và so với
`dist/manifest.json`. Lệch ⇒ dừng, in ra cả hai bên để người dùng thấy rõ.

Đã bắt được lỗi thật: zip test tạo trước khi sửa manifest vẫn mang tên 53 ký tự
và 2 quyền đã gỡ (`cookies`, `webRequest`). Upload bản đó là phát hành nhầm quyền.

Đọc file trong zip bằng `zlib.inflateRawSync` sau khi duyệt central directory từ
EOCD ngược lên — khoảng 30 dòng, không cần thư viện.

### Bẫy 7b — sinh giải trình quyền theo vòng lặp, không viết cứng

Lặp qua `manifest.permissions` thật và tra bảng giải trình. Quyền nào chưa có
câu giải trình thì in `⚠️ CHƯA CÓ GIẢI TRÌNH` vào file — như vậy thêm quyền mới
mà quên viết justification sẽ lộ ra ngay, thay vì âm thầm thiếu.

---

## Cổng nghiệm thu

```bash
npm test && npm run typecheck && npm run build
npm run package:zip && npm run package:upload
```

Sau đó giải nén lại để tự xác minh, **đừng tin script của chính mình**:

```bash
powershell.exe -NoProfile -Command "Expand-Archive -LiteralPath '<zip>' -DestinationPath '<thư mục tạm>' -Force"
```

`manifest.json` phải nằm ngay gốc thư mục vừa giải nén.

### Nếu cần thử đường chạy thành công mà đang bị chặn bởi file cũ

Không được xoá file của người dùng. Thay vào đó **copy `dist/` + `scripts/` +
các file .md sang scratchpad rồi chạy ở đó**. Script tự tính gốc dự án bằng
`dirname(fileURLToPath(import.meta.url)) + '/..'` nên chạy đúng trong bản sao,
và người dùng không mất gì.

---

## Sản phẩm bàn giao

| File | Nội dung |
|---|---|
| `CWS_AUDIT.md` | Báo cáo rà soát: gỡ quyền nào và bằng chứng, kết quả quét bảo mật, danh sách file rác, việc người dùng phải tự quyết |
| `STORE_LISTING.md` | Bản thảo tiêu đề / mô tả / giải trình quyền + kích thước ảnh + danh mục |
| `PRIVACY_POLICY.md` | Chính sách trung thực, kèm mục xoá dữ liệu và liên hệ |
| `scripts/package-zip.mjs` | Nén theo allowlist + 5 bộ kiểm tra |
| `scripts/make-upload-folder.mjs` | Dựng `cws-upload/`, chốt chặn zip cũ |

Trong báo cáo, luôn tách bạch **"đã sửa"** và **"việc bạn phải tự quyết định"**.
Ba việc luôn thuộc nhóm sau vì agent không làm được: đưa privacy policy lên URL
công khai, chụp ảnh màn hình 1280×800, bật RLS trên backend.
