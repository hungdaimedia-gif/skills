---
name: multiagent-setup-crossplatform
description: Hướng dẫn đầy đủ cài đặt hệ thống Multi-Agent AI (CrewAI + OpenRouter + Agent Loop Blueprint) trên cả macOS M1, Linux và Windows — bao gồm mọi bước, lỗi thực tế và cách khắc phục đã được kiểm chứng.
---

# 🚀 Skill: Cài đặt Hệ thống Multi-Agent AI (Cross-Platform)

> **Môi trường đã kiểm chứng:** MacBook M1 macOS, ngày 12/09/2026  
> **Tương thích:** macOS · Linux · Windows (WSL2 hoặc Git Bash)  
> **Mục tiêu:** Dựng pipeline AI Agent (Researcher + Coder + Reviewer + Tester) tự phối hợp viết phần mềm, dùng model miễn phí qua OpenRouter.

---

## 📋 Mục lục
1. [Chọn môi trường theo hệ điều hành](#0-chọn-môi-trường)
2. [Điều kiện tiên quyết](#1-điều-kiện-tiên-quyết)
3. [Cài Python 3.10+](#2-cài-python-310)
4. [Tạo dự án agent-team + cài CrewAI](#3-tạo-dự-án-agent-team)
5. [Thiết lập SSH Key cho GitHub](#4-thiết-lập-ssh-key-github)
6. [Clone Agent Loop Blueprint](#5-clone-agent-loop-blueprint)
7. [Cài Node.js](#6-cài-nodejs)
8. [Chọn model miễn phí OpenRouter](#7-model-miễn-phí-openrouter)
9. [Lỗi thực tế & cách khắc phục](#8-lỗi-thực-tế--cách-khắc-phục)

---

## 0. Chọn môi trường

### 🍎 macOS / 🐧 Linux
Mọi lệnh chạy thẳng trong **Terminal**. Không cần cài thêm gì trước.

### 🪟 Windows
> **Bắt buộc chọn 1 trong 2 cách trước khi bắt đầu:**

**Cách A — WSL2 (Khuyên dùng, giống hệt Mac/Linux):**
```powershell
# Chạy trong PowerShell với quyền Admin (1 lần duy nhất):
wsl --install
# Khởi động lại máy, sau đó mọi lệnh chạy trong Ubuntu terminal
```

**Cách B — Git Bash (Nhẹ hơn, không cần restart):**
- Tải và cài: https://git-scm.com/download/win
- Mở **Git Bash** thay vì cmd.exe hoặc PowerShell

> Từ đây trở xuống, nếu dùng **Windows** hãy chạy tất cả lệnh trong **WSL2 Ubuntu** hoặc **Git Bash**, KHÔNG dùng cmd.exe / PowerShell thông thường.

---

## 1. Điều kiện tiên quyết

```bash
python3 --version     # Cần >= 3.10
echo $OPENROUTER_API_KEY  # Phải có giá trị
```

> **⚠️ Nếu `OPENROUTER_API_KEY` trống → DỪNG.**  
> Đăng ký tại: https://openrouter.ai → Dashboard → API Keys → Create Key

---

## 2. Cài Python 3.10+

### 🍎 macOS / 🐧 Linux / 🪟 WSL2 — Dùng `uv` (Không cần sudo)

```bash
# Cài uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Load vào shell hiện tại
export PATH="$HOME/.local/bin:$PATH"

# Kiểm tra
uv --version
```

> **Tại sao dùng `uv` thay Homebrew?**  
> `uv` không cần `sudo`, tự tải Python mọi phiên bản, chạy được trên cả 3 hệ điều hành.

### 🪟 Windows (Git Bash — nếu không dùng WSL2)

```bash
# Tải Python installer từ python.org
# https://www.python.org/downloads/windows/
# ✅ Tick "Add Python to PATH" khi cài

# Kiểm tra sau khi cài
python --version   # Windows dùng "python" thay vì "python3"
```

---

## 3. Tạo dự án agent-team

### 3.1 Tạo thư mục + Virtual Environment

**macOS / Linux / WSL2:**
```bash
mkdir -p ~/agent-team && cd ~/agent-team
uv venv --python 3.10 agentenv
source agentenv/bin/activate          # ← Lệnh kích hoạt venv
```

**Windows (cmd.exe):**
```cmd
mkdir %USERPROFILE%\agent-team && cd %USERPROFILE%\agent-team
python -m venv agentenv
agentenv\Scripts\activate             # ← Windows dùng dấu \
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Path ~\agent-team
cd ~\agent-team
python -m venv agentenv
agentenv\Scripts\Activate.ps1         # ← PowerShell dùng .ps1
```

### 3.2 Tạo `requirements.txt`

```txt
crewai>=0.70.0
crewai-tools>=0.12.0
litellm>=1.40.0
```

### 3.3 Cài thư viện

**macOS / Linux / WSL2 (dùng uv):**
```bash
uv pip install -r requirements.txt
```

**Windows (sau khi activate venv):**
```cmd
pip install -r requirements.txt
```

> ⏱️ Lần đầu cài ~157 packages, mất 30-60 giây tùy mạng.

### 3.4 Chạy pipeline

**macOS / Linux / WSL2:**
```bash
export PATH="$HOME/.local/bin:$PATH"
export OPENROUTER_API_KEY="sk-or-v1-..."
cd ~/agent-team && source agentenv/bin/activate
python3 main.py
```

**Windows (cmd.exe):**
```cmd
set OPENROUTER_API_KEY=sk-or-v1-...
cd %USERPROFILE%\agent-team
agentenv\Scripts\activate
python main.py
```

**Windows (PowerShell):**
```powershell
$env:OPENROUTER_API_KEY="sk-or-v1-..."
cd ~\agent-team
agentenv\Scripts\Activate.ps1
python main.py
```

---

## 4. Thiết lập SSH Key GitHub

### 4.1 Kiểm tra SSH key đã có chưa

**macOS / Linux / WSL2 / Git Bash:**
```bash
ls -la ~/.ssh
# Nếu thấy id_ed25519 và id_ed25519.pub → đã có, bỏ qua bước 4.2
```

**Windows (PowerShell):**
```powershell
ls $env:USERPROFILE\.ssh
```

### 4.2 Tạo SSH key mới

**macOS / Linux / WSL2 / Git Bash:**
```bash
ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub   # Copy output này
```

**Windows (PowerShell — cần bật OpenSSH):**
```powershell
# Bật OpenSSH Client nếu chưa có:
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0

# Tạo key:
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\id_ed25519" -N '""'
cat $env:USERPROFILE\.ssh\id_ed25519.pub   # Copy output này
```

### 4.3 Thêm Public Key vào GitHub

1. Truy cập: **https://github.com/settings/ssh/new**
2. **Title:** `MacBook M1` hoặc `Windows PC`
3. **Key:** Dán nội dung public key vừa copy
4. Nhấn **Add SSH key**

### 4.4 Kiểm tra kết nối

```bash
# macOS / Linux / WSL2 / Git Bash:
ssh -T -o StrictHostKeyChecking=no git@github.com
# Thành công: "Hi <username>! You've successfully authenticated..."
```

> ℹ️ Trên GitHub, trạng thái key hiển thị `Never used` lúc đầu là **bình thường**.  
> GitHub cập nhật trễ. Key đã hoạt động nếu lệnh trên trả về `Hi <username>!`.

---

## 5. Clone Agent Loop Blueprint

**macOS / Linux / WSL2 / Git Bash:**
```bash
git clone git@github.com:hungdaimedia-gif/idea-agent-loop-blueprint.git \
    ~/Projects/idea-agent-loop-blueprint
cd ~/Projects/idea-agent-loop-blueprint
```

**Windows (PowerShell hoặc cmd):**
```powershell
git clone git@github.com:hungdaimedia-gif/idea-agent-loop-blueprint.git `
    $env:USERPROFILE\Projects\idea-agent-loop-blueprint
cd $env:USERPROFILE\Projects\idea-agent-loop-blueprint
```

---

## 6. Cài Node.js

### macOS / Linux / WSL2 — Dùng `nvm`

```bash
# Cài nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# Load nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Cài Node.js
nvm install node

# Kiểm tra
node --version   # v26.x.x
```

### 🪟 Windows (Git Bash / PowerShell)

```powershell
# Tải Node.js installer (LTS) từ:
# https://nodejs.org/en/download
# Cài xong, kiểm tra:
node --version
npm --version
```

### 6.1 Chạy setup Agent Loop Blueprint

```bash
# macOS / Linux / WSL2:
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
node setup.js .

# Windows:
node setup.js .     # Chạy trong thư mục dự án
```

### 6.2 Kiểm tra trạng thái hệ thống

```bash
# macOS / Linux / WSL2:
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
node scripts/task-status.js show

# Windows:
node scripts\task-status.js show    # ← Dùng dấu \ trên Windows
```

---

## 7. Model Miễn Phí OpenRouter

### Lấy danh sách model đang hoạt động

**macOS / Linux / WSL2 / Git Bash:**
```bash
curl -s https://openrouter.ai/api/v1/models | grep -o '"id":"[^"]*:free"'
```

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri "https://openrouter.ai/api/v1/models").Content | `
  Select-String -Pattern '"id":"[^"]*:free"' -AllMatches | `
  % { $_.Matches } | % { $_.Value }
```

### Model đã kiểm chứng hoạt động (tháng 09/2026)

| Model ID | Trạng thái |
|---|---|
| `google/gemma-4-31b-it:free` | ✅ Hoạt động |
| `google/gemma-4-26b-a4b-it:free` | ✅ Hoạt động |
| `nvidia/nemotron-3.5-lightning:free` | ✅ Hoạt động |

### Model ĐÃ HẾT free

| Model ID | Lý do |
|---|---|
| `meta-llama/llama-3.1-8b-instruct:free` | ❌ 404 |
| `google/gemini-2.0-flash-exp:free` | ❌ 404 |

> **⚠️ Lỗi 429:** DỪNG, đợi 1-5 phút, chạy lại thủ công. KHÔNG tự retry vòng lặp.

---

## 8. Lỗi thực tế & Cách khắc phục

### ❌ `command not found: brew`
**Fix (macOS):** Dùng `uv` thay thế (xem Bước 2).

---

### ❌ `command not found: pip`
**Fix:** Trong uv venv, dùng `uv pip install` thay vì `pip install`.

---

### ❌ `git@github.com: Permission denied (publickey)`
**Fix:** Làm đầy đủ Bước 4. Kiểm tra bằng `ssh -T git@github.com`.

---

### ❌ `remote: Repository not found`
**Fix:** Kiểm tra URL repo → thêm SSH key vào GitHub → thử lại.

---

### ❌ `FileNotFoundError: 'node'` (khi chạy Python script)
**Fix (macOS/Linux):** Load nvm trước:
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```
**Fix (Windows):** Cài Node.js qua installer và khởi động lại terminal.

---

### ❌ `404 — This model is unavailable for free`
**Fix:** Lấy danh sách model mới (Bước 7) và cập nhật `model=` trong `main.py`.

---

### ❌ `zsh: no such file or directory: USERNAME_...`  
**Nguyên nhân:** Copy nhầm lệnh ví dụ có placeholder `<USERNAME>` vào terminal.  
**Fix:** Thay `<USERNAME>` và `<TOKEN>` bằng giá trị thực trước khi chạy.

---

### ❌ `agentenv\Scripts\Activate.ps1 cannot be loaded` (Windows PowerShell)
**Fix:** Bật quyền chạy script:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## ✅ Checklist hoàn thành

```
[x] uv cài thành công
[x] Python 3.10 virtual env tạo thành công
[x] 157 packages cài thành công (crewai, litellm, crewai-tools...)
[x] SSH key ed25519 tạo và thêm vào GitHub
[x] Repo idea-agent-loop-blueprint clone thành công
[x] Node.js cài thành công
[x] Agent Loop Blueprint setup: 14 file cốt lõi + 9 skills
[x] Skill code-bug-inspector tạo và kiểm chứng hoạt động
[x] Toàn bộ files push lên GitHub thành công
```

---

_Skill này được tổng hợp từ phiên làm việc thực tế ngày 12/09/2026 bởi Eric & Antigravity._  
_Tương thích: macOS M1 · Linux · Windows (WSL2 / Git Bash / cmd / PowerShell)_
