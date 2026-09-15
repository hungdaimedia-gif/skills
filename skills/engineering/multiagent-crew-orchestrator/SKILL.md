---
name: multiagent-crew-orchestrator
description: "Kiến trúc điều phối Đa Tác Nhân (Multi-Agent System với CrewAI / AutoGen): Phân vai tác nhân chuyên biệt (Role-Playing), quy trình phân cấp ủy quyền (Hierarchical & Sequential Process), chia sẻ bộ nhớ dùng chung và cơ chế đồng thuận (Consensus & Verification)."
provenance:
  repo: "joaomdmoura/crewAI"
  branch: "main"
  stars: 33000
  forks: 4500
  verified_at: "2026-09-15"
---

# 🤖 Multi-Agent Crew Orchestrator
### Kiến Trúc Điều Phối Nhóm Tác Nhân AI Phân Vai Chuyên Biệt

> **Triết lý cốt lõi**: "Một AI làm tất cả = Kết quả trung bình. Một nhóm AI chuyên môn hoá = Đột phá chất lượng."
> Thay vì nhồi nhét một Prompt khổng lồ dài 5,000 từ bắt 1 LLM vừa nghiên cứu, vừa viết code, vừa test; kiến trúc Multi-Agent phân chia thành các thực thể độc lập với ranh giới trách nhiệm rõ ràng.

---

## 🎯 Khi Nào Cần Sử Dụng Skill Này?

- Khi bài toán quá phức tạp để 1 LLM giải quyết trong 1 lượt (cần khảo sát ➔ thiết kế ➔ lập trình ➔ kiểm thử ➔ nghiệm thu).
- Khi cần cơ chế phản biện độc lập (Chuyên gia Reviewer bắt lỗi Chuyên gia Coder trước khi xuất dữ liệu).
- Khi xây dựng hệ thống tự hành (Autonomous Pipeline) chạy liên tục không cần con người can thiệp từng bước nhỏ.

---

## 👥 3 Trụ Cột Cốt Lõi Của Một Crew (Nhóm Tác Nhân)

```
        ┌────────────────────────────────────────────────────────┐
        │                 CREW ORCHESTRATOR                      │
        └────────────────────────────────────────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           ▼                        ▼                        ▼
    [Agent: Researcher]      [Agent: Engineer]       [Agent: Quality Gate]
    - Role: Khảo sát         - Role: Lập trình       - Role: Đánh giá
    - Goal: Dữ liệu sạch     - Goal: Mã nguồn TDD    - Goal: Kiểm duyệt
    - Tools: Search, Web     - Tools: Terminal, IDE  - Tools: Linter, Test
```

### 1. Định Nghĩa Agent Chuẩn (Role, Goal, Backstory)
Mỗi Agent phải có:
- **Role**: Danh xưng vai trò (vd: Senior Security Auditor).
- **Goal**: Mục tiêu cụ thể, đo lường được (vd: Tìm ra ít nhất 3 lỗ hổng logic hoặc xác nhận mã nguồn an toàn 100%).
- **Backstory**: Ngữ cảnh chuyên gia định hình tư duy và cách hành văn.
- **Verbose & Memory**: Bật ghi nhật ký chi tiết và bộ nhớ ngữ cảnh ngắn hạn/dài hạn.

### 2. Định Nghĩa Task Chuẩn (Description & Expected Output)
Mỗi Task phải nêu rõ:
- **Description**: Yêu cầu chi tiết cần thực hiện.
- **Expected Output**: Cấu trúc kết quả đầu ra bắt buộc (JSON, Markdown report, hoặc file code cụ thể).
- **Agent Phụ Trách**: Gán đích danh Agent chịu trách nhiệm.

---

## 💻 Code Mẫu Triển Khai (Python CrewAI Architecture)

```python
from crewai import Agent, Crew, Process, Task
from langchain_openai import ChatOpenAI

# 1. Khởi tạo LLM Provider
llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

# 2. Định nghĩa các Agent chuyên biệt
researcher = Agent(
    role="Chuyên Gia Phân Tích Yêu Cầu Kỹ Thuật",
    goal="Mổ xẻ tài liệu đặc tả, liệt kê danh sách edge cases và yêu cầu phi chức năng",
    backstory="Bạn là Principal Architect với 15 năm kinh nghiệm phân tích rủi ro hệ thống.",
    verbose=True,
    memory=True,
    llm=llm
)

lead_engineer = Agent(
    role="Kỹ Sư Lập Trình Backend Cấp Cao",
    goal="Viết mã nguồn đáp ứng 100% tài liệu kiến trúc, tuân thủ nguyên tắc Clean Code và TDD",
    backstory="Bạn là Kỹ sư phần mềm xuất sắc, ghét code ẩu, luôn viết test trước khi implement.",
    verbose=True,
    llm=llm
)

qa_inspector = Agent(
    role="Trưởng Nhóm Kiểm Định An Toàn & Chất Lượng",
    goal="Tìm kiếm lỗi tiềm ẩn, kiểm tra bảo mật OWASP và đo lường độ chịu tải của code",
    backstory="Bạn là chuyên gia QA khét tiếng khó tính, không bao giờ bỏ qua dù chỉ một lỗi nhỏ.",
    verbose=True,
    llm=llm
)

# 3. Định nghĩa chuỗi nhiệm vụ tuần tự có phụ thuộc (Sequential Tasks)
task1 = Task(
    description="Khảo sát bài toán kết nối Webhook thanh toán Stripe và liệt kê các rủi ro bảo mật.",
    expected_output="Bản đặc tả danh sách 5 rủi ro và giải pháp khắc phục bằng tiếng Việt.",
    agent=researcher
)

task2 = Task(
    description="Viết mã nguồn xử lý Webhook theo bản đặc tả từ Task 1, có xác thực HMAC.",
    expected_output="Khối mã nguồn Python FastAPI hoàn chỉnh có đầy đủ type annotations.",
    agent=lead_engineer,
    context=[task1] # Nhận dữ liệu đầu ra từ task1
)

task3 = Task(
    description="Rà soát mã nguồn ở Task 2 theo tiêu chuẩn an toàn thông tin và test coverage.",
    expected_output="Báo cáo nghiệm thu PASS/FAIL kèm danh sách khuyến nghị tối ưu.",
    agent=qa_inspector,
    context=[task2]
)

# 4. Khởi chạy Crew với quy trình tuần tự chặt chẽ
system_crew = Crew(
    agents=[researcher, lead_engineer, qa_inspector],
    tasks=[task1, task2, task3],
    process=Process.sequential,
    verbose=True
)

result = system_crew.kickoff()
print("Kết quả bàn giao cuối cùng:\n", result)
```

---

## 📋 Checklist Thiết Kế Multi-Agent Hệ Thống

- [ ] 1. Ranh giới vai trò giữa các Agent không bị chồng chéo (Agent A không làm việc của Agent B).
- [ ] 2. Định nghĩa `expected_output` của từng Task cực kỳ tường minh (tránh để AI tự do trả lời lan man).
- [ ] 3. Luôn có ít nhất 1 Agent giữ vai trò **Phản biện / Quality Gate** trước khi kết thúc quy trình.
- [ ] 4. Bật cơ chế chia sẻ ngữ cảnh (`context=[...]`) giữa các Task có quan hệ nhân quả.
- [ ] 5. Thiết lập giới hạn số lượt suy luận tối đa (`max_iter` hoặc `max_rpm`) để ngăn chặn Agent gọi vòng lặp tốn token vô ích.
