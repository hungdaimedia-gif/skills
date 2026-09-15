---
name: codebase-line-budget-guard
description: Kỹ thuật thiết lập và vận hành cổng kiểm soát ngân sách dòng code (File Line Budget Guard) ≤ 350 dòng và cơ chế Ratchet Baseline bảo vệ Điều 0 (Zero Destruction) cho dự án phần mềm có AI Coding Agent tham gia. Kích hoạt khi người dùng muốn: thiết lập giới hạn số dòng code cho mỗi file (line budget), chống AI viết file khổng lồ spaghetti code (>1,000 dòng), cài đặt cơ chế Ratchet giữ an toàn cho code legacy cũ, hoặc thiết lập GitHub Actions CI workflow tự động kiểm định chất lượng mã nguồn.
---

# 🛡️ CODEBASE LINE BUDGET GUARD & RATCHET MECHANISM

> **Mục tiêu tối thượng:** Ngăn chặn triệt để tình trạng AI Coding Agent (hoặc Lập trình viên) nhồi nhét code biến một file thành "quái vật khổng lồ" (> 1,000 dòng) gây tràn ngữ cảnh, ảo giác và không thể bảo trì.  
> **Nguyên tắc cốt lõi (ADR-001 & CONVENTIONS.md):**  
> 1. Mọi file mã nguồn mới trong `src/` **BẮT BUỘC ≤ 350 dòng**.  
> 2. **Cơ chế Ratchet Baseline (Bảo toàn Điều 0):** Không bao giờ làm vỡ các file legacy cũ đang chạy ổn định; chỉ khóa chặt file mới và ngăn file cũ phình to thêm.

---

## ⚡ 1. Điều Kiện Kích Hoạt (Triggers)

Kích hoạt skill này khi:
- Người dùng yêu cầu: *"Giới hạn số dòng code mỗi file"*, *"Cài đặt script check line budget"*, *"Làm sao để bot không viết file quá dài?"*, *"Setup CI kiểm tra độ dài file"*.
- Khi bắt đầu một dự án mới và muốn áp dụng quy chuẩn **Clean Architecture / Bulletproof React**.
- Khi một dự án cũ có nhiều file khổng lồ (> 500 dòng) và cần lộ trình phẫu thuật thu nhỏ dần mà không gây downtime hay hỏng tính năng đang chạy.

---

## 🧭 2. Cơ Chế Ratchet Baseline Là Gì? (The Ratchet Guard)

Nếu bạn đột ngột đặt lệnh cấm file > 350 dòng vào một dự án đang chạy thực tế:
- Dự án sẽ có hàng chục file legacy (ví dụ: `index.ts`, `Gen.tsx`, `flowAssetPicker.ts`) vượt quá 350 dòng.
- Lệnh `npm test` hoặc CI sẽ lập tức báo đỏ ❌, làm tê liệt toàn bộ quy trình phát triển.
- Nếu AI cố tình refactor vội vàng cả chục file lớn cùng lúc, **Điều 0** (Zero Destruction) sẽ bị phá vỡ, tính năng cũ sẽ chết hàng loạt!

👉 **Giải pháp Ratchet Baseline:**
```mermaid
flowchart TD
    Scan["1. Quét toàn bộ src/"] --> Detect["2. Phát hiện file > 350 dòng"]
    Detect --> Check{"Có nằm trong baseline.json?"}
    Check -->|Có (File Legacy)| CheckGrowth{"Có phình to thêm > 50 dòng?"}
    CheckGrowth -->|Có| RejectLegacy["❌ BÁO ĐỎ: File legacy phình to đột biến!"]
    CheckGrowth -->|Không| AllowLegacy["⚠️ Cảnh báo & Cho qua (Bảo toàn code cũ)"]
    Check -->|Không (File MỚI)| RejectNew["❌ BÁO ĐỎ: File mới vượt quá 350 dòng!"]
```

1. **Khóa hiện trường:** Ghi nhận toàn bộ file > 350 dòng hiện có vào `scripts/line-budget-baseline.json`.
2. **Khóa file mới:** Bất kỳ file nào mới tạo ra nếu vượt quá 350 dòng ➔ **Fail ngay lập tức**.
3. **Chặn phình to:** File legacy cũ chỉ được sửa đổi nhỏ (±50 dòng), nếu phình to thêm ➔ **Fail**.
4. **Bánh cóc 1 chiều (Ratchet):** Khi một file legacy được refactor giảm từ 1,000 dòng xuống 300 dòng, xóa nó khỏi baseline. Từ đó trở đi, file đó vĩnh viễn không được phép vượt quá 350 dòng nữa!

---

## ⚙️ 3. Bộ Mã Nguồn Chuẩn (Ready-to-Use Scripts)

### 3.1. Script khởi tạo Baseline ban đầu (`scripts/init-baseline.mjs`)
```javascript
import fs from 'node:fs';
import path from 'node:path';

function walk(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  for (const file of list) {
    const full = path.join(dir, file);
    if (fs.statSync(full).isDirectory()) results = results.concat(walk(full));
    else if (/\.(ts|tsx|js|jsx)$/.test(file)) results.push(full.replace(/\\/g, '/'));
  }
  return results;
}

const files = walk('src');
const baseline = {};
for (const f of files) {
  const lines = fs.readFileSync(f, 'utf8').split('\n').length;
  if (lines > 350) baseline[f] = lines;
}

fs.writeFileSync('scripts/line-budget-baseline.json', JSON.stringify(baseline, null, 2), 'utf8');
console.log(`✅ Đã lưu baseline gồm ${Object.keys(baseline).length} file legacy.`);
```

### 3.2. Script kiểm tra thường trực (`scripts/check-line-budget.mjs`)
```javascript
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const MAX_LINES = 350;
const TOLERANCE = 50;
const baselinePath = 'scripts/line-budget-baseline.json';
const baseline = fs.existsSync(baselinePath) ? JSON.parse(fs.readFileSync(baselinePath, 'utf8')) : {};

function walk(dir) {
  let results = [];
  for (const file of fs.readdirSync(dir)) {
    const full = path.join(dir, file);
    if (fs.statSync(full).isDirectory()) results = results.concat(walk(full));
    else if (/\.(ts|tsx|js|jsx)$/.test(file)) results.push(full.replace(/\\/g, '/'));
  }
  return results;
}

const files = walk('src');
const errors = [];

for (const file of files) {
  const lines = fs.readFileSync(file, 'utf8').split('\n').length;
  if (lines > MAX_LINES) {
    if (baseline[file] !== undefined) {
      if (lines > baseline[file] + TOLERANCE) {
        errors.push(`❌ [LEGACY SWELL] ${file}: ${lines} dòng (vượt trần baseline ${baseline[file] + TOLERANCE})`);
      }
    } else {
      errors.push(`❌ [NEW OVERSIZED FILE] ${file}: ${lines} dòng (vượt quá ${MAX_LINES} dòng theo ADR-001)`);
    }
  }
}

if (errors.length > 0) {
  console.error('\n🚨 VI PHẠM NGÂN SÁCH DÒNG CODE:\n' + errors.join('\n'));
  process.exit(1);
}
console.log(`✅ Toàn bộ file trong src/ thoả mãn ngân sách dòng code (<= ${MAX_LINES} dòng)!`);
```

---

## 🔄 4. Tích Hợp Vào Cổng Kiểm Tra Tự Động (CI/CD)

### 4.1. Trong `package.json`:
```json
{
  "scripts": {
    "check:budget": "node scripts/check-line-budget.mjs",
    "test": "... && node scripts/check-line-budget.mjs"
  }
}
```

### 4.2. Trong `.github/workflows/ci.yml`:
```yaml
      - name: Run Quality & Line Budget Gate
        run: npm test
```

---

## 🔪 5. Quy Trình Phẫu Thuật Rút Gọn File Lớn (Surgical Refactoring)

Khi một file chạm mốc cảnh báo (300 - 350 dòng), AI Agent thực hiện phân rã theo thứ tự 4 bước:

1. **Trích xuất Types & Interfaces:** Chuyển toàn bộ kiểu dữ liệu ra `types.ts` hoặc colocate `[module].types.ts` (~50-80 dòng tiết kiệm).
2. **Trích xuất Constants & Selectors:** Đưa các chuỗi DOM selectors, regex, hằng số cấu hình ra `constants.ts` (~30-60 dòng tiết kiệm).
3. **Trích xuất Custom Hook:** Đưa các đoạn logic `useEffect`, `useState`, gọi API ra một hook riêng trong `hooks/use[Feature].ts` (~100-150 dòng tiết kiệm).
4. **Tách Sub-Components:** Chia giao diện lớn thành các widget nhỏ hơn trong `components/` (~150-200 dòng tiết kiệm).

> 💡 **Kết quả:** File chính từ 800 dòng biến thành 1 file điều phối mỏng nhẹ chỉ ~120 dòng, cực kỳ dễ đọc, dễ kiểm thử và không bao giờ làm AI bị mất ngữ cảnh!
