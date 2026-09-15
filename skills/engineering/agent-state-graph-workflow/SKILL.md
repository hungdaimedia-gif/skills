---
name: agent-state-graph-workflow
description: "Thiết kế Luồng Công Việc Agent Dạng Đồ Thị Trạng Thái (LangGraph State Graph): Điều khiển chu trình lặp (Cyclical Execution), phân nhánh rẽ có điều kiện (Conditional Edges), lưu vết Checkpoints và điểm dừng can thiệp của con người (Human-in-the-Loop)."
provenance:
  repo: "langchain-ai/langgraph"
  branch: "main"
  stars: 18000
  forks: 2500
  verified_at: "2026-09-15"
---

# 📊 Agent State Graph Workflow
### Thiết Kế Quy Trình Tác Nhân Bằng Máy Trạng Thái Đồ Thị (State Graph)

> **Triết lý cốt lõi**: "Đồ thị chu trình (DAG + Cycles) phản ánh đúng bản chất tư duy của Agent hơn là đường thẳng tuyến tính."
> Các Agent mạnh mẽ nhất trong thực tế không chạy từ A ➔ Z rồi tắt, mà luôn có chu trình: **Làm ➔ Thử nghiệm ➔ Bắt lỗi ➔ Tự sửa lại** cho đến khi đạt chuẩn.

---

## 🎯 Khi Nào Cần Sử Dụng Skill Này?

- Khi quy trình Agent cần vòng lặp tự sửa lỗi (vd: viết code ➔ chạy test fail ➔ sửa code ➔ chạy lại test đến khi pass).
- Khi luồng xử lý cần phân nhánh rẽ phức tạp dựa trên quyết định của mô hình AI (Router Pattern).
- Khi có các bước nhạy cảm bắt buộc phải dừng lại chờ người dùng bấm "Đồng ý" (Human-in-the-Loop) rồi mới đi tiếp.
- Khi cần khả năng tua lại lịch sử (Time Travel) hoặc khôi phục trạng thái sau khi ứng dụng gặp sự cố crash.

---

## 🔄 Kiến Trúc Đồ Thị Trạng Thái Mẫu

```
                   ┌──────────────┐
                   │    START     │
                   └──────┬───────┘
                          ▼
                   ┌──────────────┐
                   │  Generator   │ ◄────────────────┐
                   └──────┬───────┘                  │
                          ▼                          │
                   ┌──────────────┐                  │ (Chưa đạt)
                   │  Evaluator   │                  │ Tự động sửa lại
                   └──────┬───────┘                  │
                          ▼                          │
                     [Đạt Chuẩn?] ─── (Cần chỉnh sửa)┘
                          │
                   (Đạt 100%)
                          ▼
                   ┌──────────────┐
                   │     END      │
                   └──────────────┘
```

---

## 💻 Code Mẫu Triển Khai (LangGraph Core Concepts)

```python
from typing import TypedDict, Literal, Annotated
import operator
from langgraph.graph import StateGraph, END

# 1. Định nghĩa Schema Trạng Thái Hệ Thống (Global State)
class AgentState(TypedDict):
    task_prompt: str
    generated_code: str
    feedback: str
    iteration_count: int
    is_approved: bool

# 2. Định nghĩa các Nodes (Hàm xử lý đơn nhất)
def code_generator_node(state: AgentState) -> dict:
    current_iter = state.get("iteration_count", 0) + 1
    feedback = state.get("feedback", "")
    
    # Mô phỏng AI sinh mã nguồn (kèm feedback từ vòng trước nếu có)
    code = f"// Code phiên bản {current_iter} xử lý: {state['task_prompt']}"
    return {
        "generated_code": code,
        "iteration_count": current_iter
    }

def quality_gate_node(state: AgentState) -> dict:
    code = state["generated_code"]
    iteration = state["iteration_count"]
    
    # Giả lập kiểm tra chất lượng: Lần thứ 2 trở đi mới đạt
    if iteration >= 2:
        return {"feedback": "Mã nguồn đạt chuẩn.", "is_approved": True}
    else:
        return {"feedback": "Thiếu unit test và type check.", "is_approved": False}

# 3. Định nghĩa Hàm Rẽ Nhánh Có Điều Kiện (Conditional Routing)
def router_logic(state: AgentState) -> Literal["code_generator", END]:
    if state["is_approved"] or state["iteration_count"] >= 3:
        return END # Dừng lại nếu đã đạt hoặc chạm trần ngân sách vòng lặp
    return "code_generator" # Quay ngược lại Generator để sửa lỗi

# 4. Xây dựng và Biên dịch Đồ Thị Trạng Thái
workflow = StateGraph(AgentState)

# Thêm nodes
workflow.add_node("code_generator", code_generator_node)
workflow.add_node("quality_gate", quality_gate_node)

# Thiết lập điểm bắt đầu và các cạnh nối
workflow.set_entry_point("code_generator")
workflow.add_edge("code_generator", "quality_gate")

# Thêm cạnh rẽ nhánh chu trình (Cyclical Loop)
workflow.add_conditional_edges(
    "quality_gate",
    router_logic,
    {
        "code_generator": "code_generator",
        END: END
    }
)

app = workflow.compile()

# 5. Thực thi đồ thị
initial_input = {"task_prompt": "Tạo API đăng nhập người dùng", "iteration_count": 0}
final_state = app.invoke(initial_input)
print("Trạng thái cuối cùng sau khi hoàn tất:", final_state)
```

---

## 📋 Checklist Thiết Kế State Graph An Toàn

- [ ] 1. **Terminal Condition**: Luôn luôn có điều kiện thoát cứng (Hard Exit) dựa trên `max_iterations` để chống vòng lặp vô hạn tốn token.
- [ ] 2. **Type Safety**: Trạng thái `State` được định kiểu nghiêm ngặt bằng `TypedDict` hoặc `Pydantic`.
- [ ] 3. **Immutable Updates**: Các Node chỉ trả về phần dữ liệu thay đổi (`delta dict`), không làm biến dạng toàn bộ state gốc.
- [ ] 4. **Checkpointer**: Sử dụng `SqliteSaver` hoặc `PostgresSaver` khi cần lưu phiên làm việc dài hạn cho người dùng.
