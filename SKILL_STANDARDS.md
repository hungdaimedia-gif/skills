# TIÊU CHUẨN CHẤT LƯỢNG SKILL (SKILL QUALITY GATE)

> Mọi skill — dù từ GitHub ngoài hay tự tạo — đều **bắt buộc** phải vượt qua
> 5 cổng kiểm tra này trước khi được nạp vào kho `hungdaimedia-gif/skills`.
> Pipeline `auto_get_skills.py` sẽ tự động kiểm tra và từ chối nếu không đạt.

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

Skill phải rõ ràng thuộc 1 trong 5 domain:

| Domain | Dấu hiệu nhận biết |
| :--- | :--- |
| `engineering` | Code, test, architecture, deploy, debug |
| `writing` | Story, character, plot, novel, creative |
| `art` | Midjourney, image, visual, prompt, AI art |
| `finance` | Balance sheet, cash flow, investment, financial |
| `productivity` | Workflow, handoff, teach, question, meeting |

**Từ chối nếu:**
- Không thể xác định domain (nội dung quá chung chung, không có chủ đề rõ ràng)
- Skill giải quyết quá nhiều domain cùng lúc (quá rộng, thiếu focus)

---

## GATE 5: AN TOÀN & TRIẾT LÝ (Safety & Philosophy) — BẮT BUỘC

Skill KHÔNG được vi phạm các nguyên tắc cốt lõi:

**Từ chối nếu skill:**
- Khuyến khích bỏ qua test hoặc viết code ẩu để "nhanh hơn"
- Khuyến khích ghi đè lịch sử Git nguy hiểm (`git push --force`)
- Khuyến khích viết file đơn lẻ vượt quá 500 dòng mà không có kế hoạch tách module
- Tự xưng là "luôn đúng" hoặc "không cần con người duyệt" (vi phạm Human-in-the-loop)
- Có nội dung độc hại, phân biệt đối xử, hoặc vi phạm pháp luật

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
