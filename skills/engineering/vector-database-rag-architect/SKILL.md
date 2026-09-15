---
name: vector-database-rag-architect
description: "Kiến trúc Vector Database cho ứng dụng AI & RAG: Thiết kế pgvector, Qdrant, Pinecone, chiến lược Hybrid Search (BM25 + Dense Vector), HNSW Indexing và Chunking dữ liệu."
provenance:
  source_repo: "pgvector/pgvector"
  source_url: "https://github.com/pgvector/pgvector"
  source_commit: "e1a98c2"
  imported_at: "2026-09-15T11:30:00+07:00"
  stars_at_import: 16800
  forks_at_import: 920
---

# 🧠 Vector Database & RAG Architect — Cơ Sở Dữ Liệu Vector Cho Ứng Dụng AI

> **Triết lý cốt lõi**: Trong kỷ nguyên AI, dữ liệu không chỉ được tìm kiếm bằng từ khóa chính xác (`WHERE title LIKE '%abc%'`), mà phải được tìm kiếm bằng **Ý nghĩa Ngữ nghĩa (Semantic Search)**. Một kiến trúc Vector DB chuẩn phải cân bằng giữa độ chính xác truy hồi (Recall), tốc độ tìm kiếm (< 50ms) và tối ưu hóa chi phí RAM.

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này? (When to Trigger)

Kích hoạt kỹ năng này khi:
1. Bạn đang xây dựng ứng dụng AI: Chatbot RAG (Retrieval-Augmented Generation), Tìm kiếm thông minh, Hệ thống gợi ý sản phẩm (Recommendation System).
2. Cần lưu trữ và truy vấn Embedding Vectors (OpenAI `text-embedding-3`, Cohere, Gemini embeddings).
3. Phân vân giữa dùng **pgvector (tận dụng luôn PostgreSQL có sẵn)** hay dựng Vector DB chuyên dụng (**Qdrant, Milvus, Pinecone**).
4. Tìm kiếm ngữ nghĩa trả về kết quả quá mơ hồ, cần kết hợp **Tìm kiếm lai (Hybrid Search: Vector + Full-text BM25)**.

---

## ⚖️ BƯỚC 1: Chọn Giải Pháp Vector DB Cho Quy Mô Dự Án

| Quy Mô Dữ Liệu | Giải Pháp Đề Xuất | Lý Do & Đánh Đổi |
| :--- | :--- | :--- |
| **< 1,000,000 Vectors** (Hầu hết dự án SME / Startup) | **PostgreSQL + pgvector** | **Lựa chọn số 1**: Không cần dựng thêm hạ tầng mới, JOIN trực tiếp với dữ liệu bảng User/Product, hỗ trợ ACID đầy đủ. |
| **1M - 100M Vectors** (Ứng dụng AI chuyên sâu, nhiều tài liệu) | **Qdrant (Rust)** | Siêu nhanh, lọc Payload Metadata cực mạnh, hỗ trợ Disk-backed vector (giảm ngốn RAM). |
| **Đám mây phi quản trị (Serverless AI)** | **Pinecone / Cloudflare Vectorize** | Không cần quản lý server, tự động mở rộng theo lưu lượng. |

---

## 📐 BƯỚC 2: Chiến Lược Phân Đoạn Dữ Liệu (Chunking Strategy)

Embedding một tài liệu 50 trang vào 1 vector duy nhất sẽ làm mất sạch chi tiết. Bắt buộc phải chia nhỏ:
* **Kích thước đoạn (Chunk size)**: `400 - 800 tokens` (vừa đủ 1 ý hoàn chỉnh).
* **Độ gối đầu (Chunk overlap)**: `10% - 15%` (khoảng 50-100 tokens) để không bị đứt gãy ngữ cảnh ở ranh giới đoạn.
* **Metadata đính kèm**: Luôn lưu kèm `document_id`, `page_number`, `created_at`, `author_id` để lọc bảo mật (Access Control Filtering) trước khi tìm kiếm vector.

---

## ⚡ BƯỚC 3: Chọn Index Vector: HNSW vs IVFFlat (pgvector)

Trong PostgreSQL với pgvector:
```sql
-- Kích hoạt extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Tạo bảng lưu tài liệu và vector (ví dụ 1536 chiều của OpenAI text-embedding-3-small)
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 1. CHỌN HNSW (Hierarchical Navigable Small World): KHUYÊN DÙNG HẦU HẾT DỰ ÁN
-- Tốc độ truy vấn cực nhanh, độ chính xác (Recall) > 95%, không cần train trước
CREATE INDEX idx_chunks_hnsw ON document_chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

---

## 🔀 BƯỚC 4: Tìm Kiếm Lai (Hybrid Search: Vector + Keyword BM25)

Tìm kiếm Vector giỏi hiểu ngữ nghĩa trừu tượng nhưng rất dốt khi tìm mã sản phẩm cụ thể (như mã lỗi `ERR_502_TIMEOUT` hoặc mã đơn hàng `DH-98231`).
* **Giải pháp chuẩn công nghiệp**: Kết hợp cả hai bằng thuật toán xếp hạng hợp nhất **RRF (Reciprocal Rank Fusion)**:
  1. Chạy Full-text search (BM25) lấy Top 20 kết quả từ khóa.
  2. Chạy Vector similarity search lấy Top 20 kết quả ngữ nghĩa.
  3. Dùng RRF chấm điểm tổng hợp để đưa bài viết phù hợp nhất lên đầu.

---

## 🎯 CÂU HỎI KIỂM ĐỊNH (Checklist)
* Dữ liệu vector đã có Index HNSW chưa hay đang tính toán Cosine Distance quét toàn bảng?
* Có phân quyền truy cập (Access Control) để user không thể search trúng tài liệu bí mật của user khác không?
* Các trường hợp tìm kiếm từ khóa chính xác (mã code, tên riêng) có được Hybrid Search hỗ trợ không?
