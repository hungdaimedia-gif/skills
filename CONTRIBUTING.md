## Cách Đóng Góp / How to Contribute

### Thêm Skill Mới

1. Tạo thư mục `skills/<domain>/<tên-skill>/`
2. Viết `SKILL.md` theo chuẩn trong [SKILL_STANDARDS.md](./SKILL_STANDARDS.md)
3. Chạy kiểm tra chất lượng:
   ```bash
   python3 scripts/auto_get_skills.py --dry-run
   python3 tests/test_pipeline.py
   ```
4. Mở Pull Request với mô tả rõ: skill giải quyết vấn đề gì, domain nào

### Chuẩn Tối Thiểu Cho Skill Mới

- ✅ Có frontmatter `name` + `description` hợp lệ
- ✅ Trên 150 từ
- ✅ Trả lời được: *khi nào dùng*, *làm gì*, *quy trình cụ thể*
- ✅ Không vi phạm triết lý Human-in-the-loop
- ✅ Điểm Quality Gate ≥ 70/100

Chi tiết tại [SKILL_STANDARDS.md](./SKILL_STANDARDS.md).

### Báo Lỗi

Mở Issue với nhãn:
- `bug` — Skill hoạt động sai
- `skill-request` — Đề xuất skill mới
- `improvement` — Cải thiện skill hiện có

### Add a New GitHub Source Repo

Edit [sources.yml](./sources.yml) and add:
```yaml
- repo: "owner/repo"
  domain: "engineering"
  conflict: "skip"
```
Then run `python3 scripts/auto_get_skills.py`.
