---
name: macos-m1-multiagent-setup
description: Hướng dẫn đầy đủ cài đặt hệ thống Multi-Agent AI (CrewAI + OpenRouter + Agent Loop Blueprint) trên MacBook M1 macOS — bao gồm mọi bước, lỗi thực tế gặp phải và cách khắc phục đã được kiểm chứng.
---

# 🚀 Skill: Cài đặt Hệ thống Multi-Agent AI trên MacBook M1

> **Được tổng hợp từ phiên thực tế ngày 12/09/2026**  
> Môi trường: MacBook M1, macOS, không có Homebrew, không có Node.js sẵn.  
> Mục tiêu: Dựng hệ thống AI Agent (Researcher + Coder + Reviewer + Tester) tự phối hợp viết phần mềm, dùng model miễn phí qua OpenRouter.

---

## 📋 Mục lục
1. [Kiểm tra điều kiện tiên quyết](#1-điều-kiện-tiên-quyết)
2. [Cài Python 3.10+ bằng uv (thay thế Homebrew)](#2-cài-python-310-bằng-uv)
3. [Tạo dự án agent-team + cài CrewAI](#3-tạo-dự-án-agent-team)
4. [Thiết lập SSH Key cho GitHub](#4-thiết-lập-ssh-key-github)
5. [Clone và cài Agent Loop Blueprint](#5-clone-agent-loop-blueprint)
6. [Cài Node.js bằng nvm](#6-cài-nodejs-bằng-nvm)
7. [Chọn model miễn phí OpenRouter](#7-chọn-model-miễn-phí-openrouter)
8. [Lỗi thực tế & cách khắc phục](#8-lỗi-thực-tế--cách-khắc-phục)

---

## 1. Điều kiện tiên quyết

Trước khi bắt đầu, kiểm tra:

```bash
python3 --version     # Cần >= 3.10
echo $OPENROUTER_API_KEY  # Phải có giá trị, không được để trống
```

> **⚠️ QUAN TRỌNG:** Nếu `OPENROUTER_API_KEY` chưa có → DỪNG và yêu cầu người dùng cung cấp.  
> Đăng ký tại: https://openrouter.ai → Dashboard → API Keys → Create Key

---

## 2. Cài Python 3.10+ bằng `uv`

**Lý do dùng `uv` thay Homebrew:**  
- Homebrew yêu cầu quyền `sudo` — trên môi trường managed/corporate thường bị chặn.  
- `uv` cài không cần sudo, siêu nhanh, tự tải Python mọi phiên bản.

```bash
# Cài uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Thêm vào PATH (chỉ cần cho phiên hiện tại, sau đó tự động qua .zshrc)
export PATH="$HOME/.local/bin:$PATH"

# Kiểm tra
uv --version
```

**Tạo thư mục dự án + virtual environment Python 3.10:**

```bash
mkdir -p ~/agent-team && cd ~/agent-team
uv venv --python 3.10 agentenv
source agentenv/bin/activate
```

> ✅ `uv` sẽ tự tải Python 3.10.x về nếu máy chưa có (~24MB).

---

## 3. Tạo dự án agent-team

### 3.1 Tạo `requirements.txt`

```txt
crewai>=0.70.0
crewai-tools>=0.12.0
litellm>=1.40.0
```

### 3.2 Cài thư viện

```bash
# Dùng uv pip thay vì pip trực tiếp (pip thường không có trong PATH với uv venv)
uv pip install -r requirements.txt
```

> ⏱️ Lần đầu cài ~157 packages, mất khoảng 30-60 giây tùy tốc độ mạng.

### 3.3 Tạo `main.py` — Pipeline 4 Agent

File `main.py` cần có các thành phần:
- **Kiểm tra kết nối OpenRouter trước** (1 request thử) để tránh lãng phí rate limit.
- 4 Agent: `Researcher`, `Coder`, `Reviewer`, `Tester`.
- Chạy theo `Process.sequential` (tuần tự).

```python
from crewai import Agent, Task, Crew, Process, LLM
import os, requests

openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
if not openrouter_api_key:
    print("Lỗi: Không tìm thấy OPENROUTER_API_KEY")
    exit(1)

# Kiểm tra kết nối
response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {openrouter_api_key}"},
    json={"model": "google/gemma-4-31b-it:free", "messages": [{"role": "user", "content": "Hi"}]}
)
if response.status_code == 429:
    print("Lỗi 429: Rate limit. Vui lòng chờ rồi thử lại.")
    exit(1)
elif response.status_code != 200:
    print(f"Lỗi kết nối: {response.status_code} - {response.text}")
    exit(1)

llm = LLM(model="openrouter/google/gemma-4-31b-it:free", api_key=openrouter_api_key)
# ... định nghĩa 4 agent và chạy crew
```

### 3.4 Chạy pipeline

```bash
export PATH="$HOME/.local/bin:$PATH"
export OPENROUTER_API_KEY="sk-or-v1-..."
cd ~/agent-team && source agentenv/bin/activate
python3 main.py
```

---

## 4. Thiết lập SSH Key GitHub

**Lý do cần SSH Key:**  
Để clone/push repo Private trên GitHub từ Terminal mà không cần nhập password mỗi lần.

### 4.1 Kiểm tra SSH key đã có chưa

```bash
ls -la ~/.ssh
# Nếu thấy id_ed25519 và id_ed25519.pub → đã có, bỏ qua bước 4.2
```

### 4.2 Tạo SSH key mới

```bash
ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519
```

> `-N ""` = không đặt passphrase (tiện dùng trong dev).

### 4.3 Lấy Public Key và thêm vào GitHub

```bash
cat ~/.ssh/id_ed25519.pub
# Copy toàn bộ output
```

Truy cập: **https://github.com/settings/ssh/new**
- **Title:** `MacBook M1 - Antigravity`
- **Key type:** Authentication Key
- **Key:** Dán public key vừa copy
- Nhấn **Add SSH key**

### 4.4 Kiểm tra kết nối

```bash
ssh -T -o StrictHostKeyChecking=no git@github.com
# Kết quả thành công: "Hi <username>! You've successfully authenticated..."
```

> ℹ️ Trên GitHub, trạng thái key sẽ hiển thị `Never used` lúc đầu — đây là bình thường,  
> GitHub cập nhật trễ. Key vẫn hoạt động nếu bước kiểm tra trên trả về `Hi <username>!`.

### 4.5 Clone repo

```bash
git clone git@github.com:<username>/<repo>.git ~/Projects/<repo>
```

---

## 5. Clone Agent Loop Blueprint

```bash
git clone git@github.com:hungdaimedia-gif/idea-agent-loop-blueprint.git \
    ~/Projects/idea-agent-loop-blueprint
cd ~/Projects/idea-agent-loop-blueprint
```

---

## 6. Cài Node.js bằng `nvm`

**Lý do cần Node.js:**  
Script `setup.js` và `scripts/task-status.js` của Agent Loop Blueprint yêu cầu Node.js.

```bash
# Cài nvm (Node Version Manager) — không cần sudo
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# Load nvm vào shell hiện tại
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Cài Node.js phiên bản mới nhất
nvm install node

# Kiểm tra
node --version   # v26.x.x
npm --version
```

### 6.1 Chạy setup Agent Loop Blueprint

```bash
cd ~/Projects/idea-agent-loop-blueprint
node setup.js .
```

> Script sẽ tự sinh 14 file/thư mục cốt lõi:  
> `CLAUDE.md`, `RULES.md`, `CONVENTIONS.md`, `LOOP.md`, `AGENT_TASKS.md`,  
> `DEV_SYNC.md`, `CHANGELOG.md`, `TASK_STATUS.json`, `scripts/task-status.js`,  
> `scripts/check-line-budget.mjs`, `docs/`, `.github/workflows/ci.yml`, `.agents/skills/`

### 6.2 Kiểm tra trạng thái hệ thống

```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
node scripts/task-status.js show
# Kết quả mong đợi: {"status": "IDLE", "currentAction": "Hệ thống sẵn sàng nhận nhiệm vụ mới"}
```

---

## 7. Chọn Model Miễn Phí OpenRouter

Model free thay đổi liên tục. Lấy danh sách model đang hoạt động:

```bash
curl -s https://openrouter.ai/api/v1/models | grep -o '"id":"[^"]*:free"'
```

**Model đã kiểm chứng hoạt động (tháng 09/2026):**

| Model ID | Ghi chú |
|---|---|
| `google/gemma-4-31b-it:free` | ✅ Hoạt động |
| `google/gemma-4-26b-a4b-it:free` | ✅ Hoạt động |
| `nvidia/nemotron-3.5-lightning:free` | ✅ Hoạt động |

**Model ĐÃ HẾT free (không dùng được):**

| Model ID | Lý do |
|---|---|
| `meta-llama/llama-3.1-8b-instruct:free` | ❌ 404 — chuyển sang bản trả phí |
| `google/gemini-2.0-flash-exp:free` | ❌ 404 — không còn endpoint |

> **⚠️ Lỗi 429 (Rate Limit):** Model free có giới hạn thấp (~20 req/phút).  
> Pipeline 4 agent gọi nhiều lần liên tục dễ bị chặn tạm.  
> Khi gặp 429: DỪNG, không tự retry vòng lặp. Đợi 1-5 phút rồi thử lại thủ công.

---

## 8. Lỗi thực tế & Cách khắc phục

### ❌ `command not found: brew`
**Nguyên nhân:** Homebrew chưa cài, hoặc cài nhưng không có quyền sudo.  
**Fix:** Dùng `uv` thay thế (xem Bước 2).

---

### ❌ `command not found: pip`
**Nguyên nhân:** Trong uv venv, `pip` không có trong PATH mặc định.  
**Fix:** Dùng `uv pip install` thay vì `pip install`.

---

### ❌ `git@github.com: Permission denied (publickey)`
**Nguyên nhân:** Chưa tạo SSH key hoặc chưa thêm vào GitHub.  
**Fix:** Làm theo Bước 4 đầy đủ. Kiểm tra bằng `ssh -T git@github.com`.

---

### ❌ `remote: Repository not found`
**Nguyên nhân:** Repo Private + chưa cấp quyền SSH, hoặc URL sai.  
**Fix:** Kiểm tra URL → thêm SSH key vào GitHub → thử lại.

---

### ❌ `FileNotFoundError: [Errno 2] No such file or directory: 'node'`
**Nguyên nhân:** `node` chưa có trong PATH khi chạy bằng Python system (3.9).  
**Fix:** Luôn load nvm trước khi chạy script liên quan đến Node:
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

---

### ❌ `404 — This model is unavailable for free`
**Nguyên nhân:** Model free đã bị OpenRouter đưa về bản trả phí.  
**Fix:** Lấy danh sách model mới (xem Bước 7) và cập nhật `model=` trong `main.py`.

---

### ❌ `Lỗi 429 — Rate Limit`
**Nguyên nhân:** Gọi API quá nhiều trong thời gian ngắn (pipeline 4 agent).  
**Fix:** Dừng, đợi 1-5 phút, chạy lại thủ công. KHÔNG tự retry vòng lặp.

---

## ✅ Checklist hoàn thành

```
[x] uv cài thành công (~/.local/bin/uv)
[x] Python 3.10.21 virtual env tại ~/agent-team/agentenv
[x] 157 packages cài thành công (crewai, litellm, crewai-tools...)
[x] SSH key ed25519 tạo tại ~/.ssh/id_ed25519
[x] SSH key thêm vào GitHub
[x] Repo idea-agent-loop-blueprint clone thành công
[x] nvm + Node.js v26.8.2 cài thành công
[x] Agent Loop Blueprint setup: 14 file cốt lõi + 8 skills
[x] Skill code-bug-inspector tạo và kiểm chứng hoạt động
```

---

_Skill này được tổng hợp từ phiên làm việc thực tế ngày 12/09/2026 bởi Eric & Antigravity._
