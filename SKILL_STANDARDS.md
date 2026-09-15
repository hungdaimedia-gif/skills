# TIÊU CHUẨN CHẤT LƯỢNG SKILL (SKILL QUALITY GATE)

> Mọi skill — dù từ GitHub ngoài hay tự tạo — đều **bắt buộc** phải vượt qua
> 5 cổng kiểm tra này trước khi được nạp vào kho `hungdaimedia-gif/skills`.
> Pipeline `auto_get_skills.py` sẽ tự động kiểm tra và từ chối nếu không đạt.

---

## GATE 0: UY TÍN CỘNG ĐỒNG (Social Proof Gate) — BẮT BUỘC TRƯỚC KHI CLONE

Trước khi clone bất kỳ repo nào vào máy, pipeline tự động kiểm tra metadata của repo qua GitHub API:

| Tiêu chuẩn uy tín | Ngưỡng bắt buộc | Mục đích ngăn chặn |
| :--- | :---: | :--- |
| **Số lượt Stars (⭐)** | **≥ 10,000 ⭐** | Chỉ nhận repo hàng đầu thế giới (Top-tier), chặn triệt để repo rác/vô danh |
| **Số lượt Forks (🍴)** | **≥ 500 🍴** | Chứng minh có cộng đồng kỹ sư khổng lồ kế thừa và kiểm chứng thực tế |
| **Độ tươi mới (Freshness)** | **≤ 180 ngày (6 tháng)** | Chặn repo chết yểu, bị bỏ hoang, không tương thích Agent mới |
| **Trạng thái repo** | **Active (Không Archived)** | Chặn repo đã bị tác giả đóng băng/ngừng bảo trì |

---

## GATE 1: CẤU TRÚC HỢP LỆ (Structure) — BẮT BUỘC

Skill phải có file `SKILL.md` với:

```yaml
---
name: tên-skill-chữ-thường-gạch-ngang   # BẮT BUỘC
description: "Mô tả 1 câu, rõ ràng, không mơ hồ"  # BẮT BUỘC
---
```

**Từ chối nếu:**
- Không có file `SKILL.md`
- Thiếu field `name` hoặc `description` trong frontmatter
- Tên chứa khoảng trắng, ký tự đặc biệt (chỉ cho phép `a-z`, `0-9`, `-`)
- `description` dưới 20 ký tự (quá mơ hồ) hoặc trên 200 ký tự (quá dài)

---

## GATE 2: ĐỦ NỘI DUNG TỐI THIỂU (Substance) — BẮT BUỘC

Skill phải trả lời được ít nhất 2 trong 3 câu hỏi sau trong nội dung:

| Câu hỏi | Từ khóa nhận biết |
| :--- | :--- |
| **Khi nào dùng skill này?** | `when`, `use when`, `trigger`, `activate`, `khi nào` |
| **Skill này làm gì?** | `what`, `purpose`, `goal`, `how to`, `làm gì` |
| **Quy trình cụ thể là gì?** | `step`, `phase`, `bước`, `process`, `workflow`, `protocol` |

**Từ chối nếu:**
- Nội dung dưới **150 từ** (skill quá sơ sài, chỉ là placeholder)
- Không trả lời được ít nhất 2/3 câu hỏi trên

---

## GATE 3: KHÔNG TRÙNG LẶP THỰC CHẤT (Novelty) — BẮT BUỘC

- Nếu tên trùng với skill đã có: So sánh nội dung
  - **≥ 85% giống**: Tự động skip (cùng nguồn gốc)
  - **50% - 84% giống**: Cảnh báo, yêu cầu người dùng duyệt thủ công
  - **< 50% giống**: Coi là skill mới thực sự, cho phép nạp
- Nếu tên khác nhưng description quá giống (≥ 80%): Cảnh báo khả năng trùng chức năng

**Từ chối nếu:**
- Độ giống nội dung ≥ 85% (cùng nội dung, khác tên — là bản copy)

---

## GATE 4: PHÙ HỢP DOMAIN (Domain Fit) — BẮT BUỘC

Skill phải rõ ràng thuộc 1 trong các domain: `engineering`, `writing`, `art`, `finance`, `productivity`, `misc`.

**Từ chối nếu:**
- Không thể xác định domain (nội dung quá chung chung, không có chủ đề rõ ràng)
- Skill giải quyết quá nhiều domain cùng lúc (quá rộng, thiếu focus)

---

## GATE 5: AN TOÀN & BẢO MẬT MÃ THỰC THI (Script Security Sandbox) — BẮT BUỘC

Cổng bảo mật kiểm tra cả nội dung file `SKILL.md` VÀ quét đệ quy toàn bộ thư mục `scripts/` (các file `.sh`, `.py`, `.js`):

**Từ chối và lập tức cách ly nếu phát hiện:**
1. **Đánh cắp bí mật & biến môi trường**: Truy cập trái phép `$OPENROUTER_API_KEY`, `$ANTHROPIC_API_KEY`, `$OPENAI_API_KEY`, file `.env`, hoặc khóa `.ssh/id_*`.
2. **Rò rỉ dữ liệu qua mạng (Data Exfiltration)**: Chứa lệnh gửi request ngầm như `curl -d`, `wget --post-data`, `nc -e`, kết nối socket ngầm `/dev/tcp/`.
3. **Phá hoại hệ thống**: Lệnh xoá nguy hiểm như `rm -rf /`, `rm -rf ~`, `rm -rf $HOME`.
4. **Thực thi mã độc làm mờ (Obfuscation)**: `base64 -d | sh`, `eval(base64...)`, `curl | bash`.
5. **Vi phạm đạo đức & triết lý**: Khuyến khích bỏ qua test (`skip test`), ép buộc `git push --force`, hoặc tự xưng "không cần con người kiểm duyệt".

---

## BẢNG TÓM TẮT ĐIỂM CHẤT LƯỢNG

Pipeline tự động chấm điểm mỗi skill theo thang 0-100:

| Gate | Điểm tối đa | Điều kiện Pass |
| :--- | :---: | :--- |
| Gate 1: Cấu trúc | 20đ | Có đủ frontmatter hợp lệ |
| Gate 2: Nội dung | 30đ | ≥ 150 từ + 2/3 câu hỏi |
| Gate 3: Không trùng | 20đ | Giống < 85% với mọi skill có sẵn |
| Gate 4: Domain fit | 15đ | Xác định được domain rõ ràng |
| Gate 5: An toàn | 15đ | Không vi phạm triết lý cốt lõi |
| **TỔNG** | **100đ** | **≥ 70đ mới được nạp** |

---

## VÍ DỤ THỰC TẾ

### ✅ Skill đạt chuẩn
```yaml
---
name: api-contract-testing
description: "Test contract giữa consumer và provider API để đảm bảo tích hợp không bị vỡ khi nâng cấp."
---
# API Contract Testing
Use when: Integration tests pass nhưng staging vẫn bị lỗi 404/422 sau deploy.
What: Viết consumer-driven contract tests dùng Pact...
Steps:
  1. Define consumer expectations
  2. Generate pact file
  3. Verify against provider
```
→ **Gate 1**: ✅ Frontmatter đầy đủ
→ **Gate 2**: ✅ Rõ when/what/steps
→ **Gate 3**: ✅ Không trùng với skill nào
→ **Gate 4**: ✅ Domain engineering
→ **Gate 5**: ✅ Không vi phạm
→ **Tổng: 95/100 → PASS**

### ❌ Skill bị từ chối
```yaml
---
name: do everything
description: "Help"
---
Just ask the AI to do stuff for you quickly without tests.
```
→ **Gate 1**: ❌ Tên chứa khoảng trắng, description 4 ký tự
→ **Gate 2**: ❌ < 150 từ, không có when/steps
→ **Gate 5**: ❌ Khuyến khích bỏ qua test
→ **Tổng: 15/100 → REJECT**
