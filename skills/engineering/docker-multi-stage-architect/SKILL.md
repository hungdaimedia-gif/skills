---
name: docker-multi-stage-architect
description: "Kiến trúc đóng gói Docker & Compose chuẩn Production: Xây dựng Dockerfile Multi-stage build siêu nhẹ, tối ưu layer caching, bảo mật quyền Non-root user, Healthcheck endpoint và quản trị tài nguyên container (Resource limits)."
provenance:
  repo: "docker/awesome-compose"
  branch: "master"
  stars: 35000
  forks: 6500
  verified_at: "2026-09-15"
---

# 🐳 Docker Multi-Stage Architect
### Kiến Trúc Đóng Gói Container Chuẩn Production & Tối Ưu Layer Caching

> **Triết lý cốt lõi**: "Image nhẹ hơn = Build nhanh hơn = Khởi động lẹ hơn = Tấn công ít hơn."
> Một Dockerfile cẩu thả sẽ mang theo toàn bộ compiler, node_modules thừa, mã nguồn dev và chạy dưới quyền `root`, tạo ra lỗ hổng bảo mật nghiêm trọng.

---

## 🎯 Khi Nào Cần Sử Dụng Skill Này?

- Khi đóng gói ứng dụng Node.js, Python, Go, hoặc Next.js để triển khai lên máy chủ VPS hoặc Kubernetes.
- Khi dung lượng Docker image quá lớn (1GB+ thay vì < 150MB).
- Khi thời gian build image trên CI/CD quá lâu vì không tận dụng được cơ chế Docker Layer Cache.
- Khi cần dựng môi trường chạy phối hợp nhiều container (App + Postgres + Redis + Nginx) bằng `docker-compose.yml`.

---

## 📐 Kiến Trúc Multi-Stage Build Mẫu (Node.js / TypeScript)

Quy trình 3 tầng cô lập tuyệt đối môi trường Build khỏi môi trường Production:

```dockerfile
# ==========================================
# Giai đoạn 1: Base & Cài đặt Dependencies
# ==========================================
FROM node:20-alpine AS deps
WORKDIR /app
RUN apk add --no-cache libc6-compat
COPY package.json package-lock.json ./
RUN npm ci

# ==========================================
# Giai đoạn 2: Builder (Biên dịch TypeScript)
# ==========================================
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Tạo production build và chỉ giữ lại production node_modules
RUN npm run build && npm prune --production

# ==========================================
# Giai đoạn 3: Production Runner (Siêu gọn & An toàn)
# ==========================================
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

# Tạo non-root user để chạy container an toàn (không dùng quyền root)
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Chỉ copy những file thực sự cần thiết để chạy ứng dụng
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Phân quyền cho non-root user
USER nextjs

EXPOSE 3000

# Khai báo Healthcheck để Docker daemon tự khởi động lại nếu crash
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/healthz || exit 1

CMD ["node", "dist/main.js"]
```

---

## 🛠️ Chuẩn Mực docker-compose.yml Môi Trường Production

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: runner
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgres://app_user:${DB_PASSWORD}@db:5432/app_db
      - REDIS_URL=redis://cache:6379
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M

  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: app_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app_user -d app_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --save 60 1 --loglevel warning
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

---

## 📋 Checklist Kiểm Định Docker Container (DevOps Gate)

- [ ] 1. **Dung lượng image**: Image sản phẩm cuối cùng < 200MB (sử dụng Alpine hoặc Distroless base).
- [ ] 2. **Non-root user**: Container tuyệt đối không chạy bằng quyền `root` (dùng `USER nodejs` hoặc `USER 1001`).
- [ ] 3. **Tận dụng cache**: `package.json` và `npm ci` được COPY và RUN trước khi copy toàn bộ mã nguồn.
- [ ] 4. **Loại bỏ file rác**: Đã tạo `.dockerignore` để loại trừ `node_modules`, `.git`, `.env`, test files.
- [ ] 5. **Cấu hình Healthcheck**: Đã thiết lập `HEALTHCHECK` endpoint `/healthz` cho từng dịch vụ.
- [ ] 6. **Giới hạn tài nguyên**: Đã thiết lập CPU và Memory `limits` trong compose/k8s để tránh 1 container làm treo toàn bộ máy chủ.
