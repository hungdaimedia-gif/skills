import os
import re
import json

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
skills_dir = os.path.join(REPO_ROOT, "skills")
output_web_dir = os.path.join(REPO_ROOT, "web")
os.makedirs(output_web_dir, exist_ok=True)

skills = []

# Refined 6-Branch User-Centric Taxonomy
branch_mapping = {
    # 1. Ý tưởng & Đặc tả (Discovery & Planning)
    "dsg": "💡 Ý tưởng & Đặc tả",
    "ask-matt": "💡 Ý tưởng & Đặc tả",
    "grill-me": "💡 Ý tưởng & Đặc tả",
    "grill-with-docs": "💡 Ý tưởng & Đặc tả",
    "grilling": "💡 Ý tưởng & Đặc tả",
    "domain-modeling": "💡 Ý tưởng & Đặc tả",
    "to-spec": "💡 Ý tưởng & Đặc tả",
    "to-tickets": "💡 Ý tưởng & Đặc tả",
    "wayfinder": "💡 Ý tưởng & Đặc tả",
    "to-questionnaire": "💡 Ý tưởng & Đặc tả",
    "research": "💡 Ý tưởng & Đặc tả",
    "project-blueprint-loop-architect": "💡 Ý tưởng & Đặc tả",

    # 2. Kiến trúc & Thiết kế hệ thống (Architecture & Design)
    "codebase-design": "🏗️ Kiến trúc & Thiết kế",
    "fullstack-boilerplate-architect": "🏗️ Kiến trúc & Thiết kế",
    "workflow-node-studio": "🏗️ Kiến trúc & Thiết kế",
    "prototype": "🏗️ Kiến trúc & Thiết kế",
    "setup-ts-deep-modules": "🏗️ Kiến trúc & Thiết kế",
    "improve-codebase-architecture": "🏗️ Kiến trúc & Thiết kế",

    # 3. Thực thi & Viết Code chuẩn mực (Implementation & TDD)
    "implement": "⚡ Viết Code & TDD",
    "implement-spec": "⚡ Viết Code & TDD",
    "tdd": "⚡ Viết Code & TDD",
    "claude-task-runner": "⚡ Viết Code & TDD",
    "loop-me": "⚡ Viết Code & TDD",
    "teach": "⚡ Viết Code & TDD",
    "writing-beats": "⚡ Viết Code & TDD",
    "writing-fragments": "⚡ Viết Code & TDD",
    "writing-shape": "⚡ Viết Code & TDD",
    "writing-for-agents": "⚡ Viết Code & TDD",

    # 4. Kiểm soát chất lượng & Review (Quality & Guardrails)
    "codebase-line-budget-guard": "🛡️ Kiểm soát & Review",
    "code-review": "🛡️ Kiểm soát & Review",
    "resolving-merge-conflicts": "🛡️ Kiểm soát & Review",
    "git-guardrails-claude-code": "🛡️ Kiểm soát & Review",
    "setup-pre-commit": "🛡️ Kiểm soát & Review",
    "retro": "🛡️ Kiểm soát & Review",
    "handoff": "🛡️ Kiểm soát & Review",
    "claude-handoff": "🛡️ Kiểm soát & Review",

    # 5. Cứu hộ & Gỡ lỗi chuyên sâu (Debugging & Recovery)
    "agent-disorientation-recovery": "🩺 Cứu hộ & Gỡ lỗi",
    "code-bug-inspector": "🩺 Cứu hộ & Gỡ lỗi",
    "diagnosing-bugs": "🩺 Cứu hộ & Gỡ lỗi",
    "system-logs-and-diagnostics": "🩺 Cứu hộ & Gỡ lỗi",
    "triage": "🩺 Cứu hộ & Gỡ lỗi",
    "wait-what": "🩺 Cứu hộ & Gỡ lỗi",

    # 6. Nền tảng & Đóng gói phát hành (Platform & Deployment)
    "macos-m1-multiagent-setup": "🚀 Nền tảng & Vận hành",
    "multiagent-setup-crossplatform": "🚀 Nền tảng & Vận hành",
    "chrome-web-store-prep": "🚀 Nền tảng & Vận hành",
    "wizard": "🚀 Nền tảng & Vận hành",
    "setup-matt-pocock-skills": "🚀 Nền tảng & Vận hành",
    "migrate-to-shoehorn": "🚀 Nền tảng & Vận hành",
    "scaffold-exercises": "🚀 Nền tảng & Vận hành",

    # Sáng tác & Viết truyện
    "novel-world-building": "📖 Cốt truyện & Thế giới",
    "story-character-arc": "🎭 Nhân vật & Tâm lý",

    # Đồ họa & Tranh AI
    "midjourney-prompt-architect": "🎨 Prompt & Bố cục Thị giác",

    # Tài chính & Đầu tư
    "financial-statement-analyzer": "📊 Phân tích BCTC & Dòng tiền"
}

# Domain mapping heuristic
domain_mapping = {
    "novel-world-building": "✍️ Sáng tác & Viết truyện",
    "story-character-arc": "✍️ Sáng tác & Viết truyện",
    "midjourney-prompt-architect": "🎨 Đồ họa & Tranh AI",
    "financial-statement-analyzer": "📈 Tài chính & Đầu tư"
}

# Rich Vietnamese Explanations for all skills
vi_explanations = {
    "novel-world-building": {
        "what": "Kiến tạo thế giới & bối cảnh truyện: Thiết lập quy tắc phép thuật, công nghệ, lịch sử và địa chính trị có logic chặt chẽ.",
        "when": "Dùng khi bắt đầu sáng tác tiểu thuyết, truyện dài hoặc viết kịch bản phim/game.",
        "benefit": "Thế giới truyện có chiều sâu sống động như thật, không bao giờ bị dính lỗi logic mâu thuẫn (plot holes)."
    },
    "story-character-arc": {
        "what": "Khắc họa chiều sâu tâm lý nhân vật: Xây dựng xung đột nội tâm, vết thương quá khứ và hành trình chuyển hóa nội tâm.",
        "when": "Dùng khi muốn nhân vật có hồn, lay động cảm xúc độc giả thay vì các khuôn mẫu một màu.",
        "benefit": "Nhân vật chân thực, có động lực hành động thuyết phục và hành trình trưởng thành cảm xúc."
    },
    "midjourney-prompt-architect": {
        "what": "Kỹ nghệ thiết kế prompt hình ảnh AI: Kiểm soát góc máy, ống kính, ánh sáng, chất liệu và color grading cinematic.",
        "when": "Dùng khi tạo ảnh với Midjourney v6, Flux.1 hoặc Stable Diffusion.",
        "benefit": "Tạo ra các tác phẩm thị giác đỉnh cao chuẩn nhiếp ảnh, thoát khỏi hình ảnh AI sáo rỗng (nhựa / generic)."
    },
    "financial-statement-analyzer": {
        "what": "Phân tích báo cáo tài chính chuyên sâu: Đo lường chất lượng dòng tiền, kiểm tra nợ vay và phát hiện rủi ro xào nấu số liệu.",
        "when": "Dùng khi đầu tư chứng khoán, thẩm định doanh nghiệp hoặc đánh giá sức khỏe đối tác.",
        "benefit": "Nhìn thấu bản chất kinh doanh thực sự đằng sau các con số kế toán bóng bẩy."
    },
    "dsg": {
        "what": "Trạm điều phối thông minh & Phân tích sâu: Tự động quét dự án, phát hiện nút thắt và tự kích hoạt chuỗi skill phù hợp để mổ xẻ vấn đề dứt điểm.",
        "when": "Dùng khi bạn thấy rối, không nhớ tên skill tiếng Anh, hoặc muốn agent tự chẩn đoán và làm ngay mà không hỏi lại.",
        "benefit": "Tiết kiệm 100% thời gian tìm kiếm skill, xử lý tận gốc vấn đề mà không phải trả lời câu hỏi thừa."
    },
    "ask-matt": {
        "what": "Điều hướng quy trình thông minh: Bạn không cần nhớ tên hàng chục skill, chỉ cần nói bạn đang muốn làm gì.",
        "when": "Dùng khi bắt đầu một công việc mới mà chưa biết nên gọi skill nào trước.",
        "benefit": "Tiết kiệm thời gian mò mẫm, định hướng quy trình chuẩn xác ngay từ câu chat đầu tiên."
    },
    "grill-me": {
        "what": "Phiên tra khảo ý tưởng: Agent sẽ liên tục đặt ra các câu hỏi sắc bén để đào sâu logic thay vì vội vàng bắt tay vào code.",
        "when": "Dùng khi bạn có một ý tưởng mới trong đầu nhưng chưa nghĩ hết các trường hợp biên (edge cases).",
        "benefit": "Loại bỏ hoàn toàn rủi ro AI code lạc đề hoặc hiểu sai ý đồ của bạn."
    },
    "grill-with-docs": {
        "what": "Tra khảo ý tưởng nâng cao: Vừa phỏng vấn làm rõ tính năng, vừa tự động cập nhật từ điển CONTEXT.md và quyết định kỹ thuật (ADRs).",
        "when": "Dùng khi bắt đầu một tính năng mới trong dự án phần mềm có cấu trúc.",
        "benefit": "Biến ý tưởng trong đầu thành tài liệu nghiệp vụ chuẩn mực mà cả người lẫn AI đều hiểu."
    },
    "grilling": {
        "what": "Bộ khung câu hỏi phỏng vấn nền tảng mà các skill như grill-me, grill-with-docs sử dụng bên dưới.",
        "when": "Agent tự động kích hoạt để dẫn dắt cuộc phỏng vấn phản biện.",
        "benefit": "Đảm bảo mọi nhánh quyết định kỹ thuật đều được cân nhắc thấu đáo."
    },
    "domain-modeling": {
        "what": "Xây dựng ngôn ngữ chung (Ubiquitous Language): Định nghĩa rõ ràng từng khái niệm trong dự án vào CONTEXT.md.",
        "when": "Dùng khi dự án có nhiều thuật ngữ chuyên môn hoặc nhiều người cùng làm.",
        "benefit": "Agent và Dev không bị 'ông nói gà bà nói vịt', đặt tên biến và hàm chuẩn xác 100%."
    },
    "to-spec": {
        "what": "Tạo bản đặc tả kỹ thuật (Spec): Đọc lại toàn bộ cuộc hội thoại vừa trao đổi và tóm tắt thành tài liệu kiến trúc chính thức.",
        "when": "Dùng ngay sau phiên tra khảo (grilling) khi hai bên đã thống nhất xong ý tưởng.",
        "benefit": "Có ngay file tài liệu spec chuẩn chỉ mà không cần tốn nửa ngày tự gõ tài liệu."
    },
    "to-tickets": {
        "what": "Cắt nhỏ công việc thành Ticket: Phân chia bản thiết kế thành các đầu việc nhỏ, độc lập, có khai báo thứ tự trước/sau rõ ràng.",
        "when": "Dùng sau khi đã có Spec, chuẩn bị bắt tay vào code từng phần.",
        "benefit": "Agent làm việc theo từng lát cắt nhỏ, không bao giờ bị quá tải bộ nhớ hay bỏ sót việc."
    },
    "wayfinder": {
        "what": "Dẫn đường cho các dự án khổng lồ: Khi khối lượng công việc quá lớn mà một phiên chat không thể chứa hết.",
        "when": "Dùng khi bắt đầu dự án lớn hoặc chuyển đổi hạ tầng phức tạp còn nhiều điểm mờ mịt.",
        "benefit": "Chia dự án thành bản đồ các quyết định, gỡ từng nút thắt một cách có hệ thống."
    },
    "to-questionnaire": {
        "what": "Tạo bảng câu hỏi khảo sát: Soạn sẵn danh sách câu hỏi có cấu trúc gửi cho khách hàng hoặc sếp để lấy ý kiến.",
        "when": "Dùng khi gặp quyết định mà chỉ bên thứ ba hoặc người ra quyết định mới trả lời được.",
        "benefit": "Thu thập thông tin đầy đủ, rõ ràng mà không phải họp hành dông dài."
    },
    "wait-what": {
        "what": "Giải thích lại bằng ngôn ngữ đời thường: Dừng agent lại và yêu cầu giải thích một thuật ngữ/đoạn code khó hiểu.",
        "when": "Dùng khi bạn đọc câu trả lời của AI hoặc tài liệu tiếng Anh mà 'chưa thấm'.",
        "benefit": "Bóc tách thuật ngữ chuyên ngành thành lời giải thích dễ hiểu, gần gũi."
    },
    "research": {
        "what": "Nghiên cứu tài liệu gốc: Cho một sub-agent chạy nền tìm kiếm và trích dẫn từ các nguồn chính thống (official docs, RFCs).",
        "when": "Dùng khi cần tìm hiểu thư viện mới hoặc công nghệ lạ mà không muốn gián đoạn mạch chat chính.",
        "benefit": "Đưa ra dẫn chứng xác thực từ tài liệu chính thức, tránh bị ảo giác (hallucination)."
    },
    "project-blueprint-loop-architect": {
        "what": "Thiết kế bản vẽ kiến trúc dự án và cỗ máy trạng thái (Agent Loop Blueprint).",
        "when": "Dùng khi thiết kế hệ thống multi-agent hoặc quy trình tự động hóa phức tạp.",
        "benefit": "Đảm bảo agent chạy theo vòng lặp có kiểm soát, có điểm dừng và có kiểm tra chất lượng."
    },
    "codebase-design": {
        "what": "Kỹ luật thiết kế module sâu (Deep Modules): Giao diện gọi hàm bên ngoài cực kỳ đơn giản, ẩn giấu toàn bộ độ phức tạp bên trong.",
        "when": "Dùng khi thiết kế các module cốt lõi hoặc chuẩn bị viết một package dùng chung.",
        "benefit": "Code cực kỳ dễ test, dễ tái sử dụng và không bị biến thành 'đống bùn lầy'."
    },
    "fullstack-boilerplate-architect": {
        "what": "Kiến trúc sư dựng khung Fullstack: Tạo cấu trúc thư mục, phân tầng UI/Logic/Data và cấu hình chuẩn chỉnh từ đầu.",
        "when": "Dùng khi khởi tạo dự án web/app mới tinh.",
        "benefit": "Có ngay bộ khung chuẩn mực chỉ sau vài giây, tránh viết code lộn xộn từ ngày đầu."
    },
    "workflow-node-studio": {
        "what": "Xây dựng Canvas Studio kéo thả Node: Hướng dẫn thiết kế Custom Node trên React Flow (@xyflow/react).",
        "when": "Dùng khi làm ứng dụng đồ họa canvas, flowchart hoặc kéo thả dây nối giống ComfyUI.",
        "benefit": "Giải quyết tận gốc các lỗi giật lag, dây nối nhảy loạn, rò rỉ bộ nhớ Object URL."
    },
    "prototype": {
        "what": "Dựng bản mẫu thử nghiệm (Throwaway Prototype): Tạo 1 file HTML duy nhất chạy thử UI hoặc kiểm chứng logic.",
        "when": "Dùng khi phân vân giữa 2-3 phương án giao diện hoặc muốn bấm thử xem có tiện không.",
        "benefit": "Biết ngay tính năng có khả thi không mà không tốn công cài đặt cả project."
    },
    "setup-ts-deep-modules": {
        "what": "Cấu hình dự án TypeScript theo tiêu chuẩn Deep Module với ranh giới rõ ràng.",
        "when": "Dùng khi bắt đầu dự án TypeScript mới.",
        "benefit": "Ép code tuân thủ ranh giới gói (package boundaries), code sáng sủa."
    },
    "improve-codebase-architecture": {
        "what": "Quét và phát hiện các cơ hội làm sâu module: Xuất báo cáo trực quan về các vùng code đang bị nông hoặc rối.",
        "when": "Dùng định kỳ vài ngày một lần trên dự án đang phát triển.",
        "benefit": "Giữ cho kiến trúc mã luôn trong sạch, phát hiện sớm dấu hiệu nợ kỹ thuật (technical debt)."
    },
    "implement": {
        "what": "Thực thi tính năng chuẩn mực: Đọc ticket, ép áp dụng TDD và tự động chạy code review trước khi bàn giao.",
        "when": "Dùng khi đã có ticket/spec và bắt đầu viết code thực tế.",
        "benefit": "Code xong là chạy được ngay, pass test và không bị thừa thãi."
    },
    "implement-spec": {
        "what": "Thực thi trực tiếp từ file Spec kỹ thuật theo từng phân đoạn nhỏ.",
        "when": "Dùng khi bạn có 1 file spec hoàn chỉnh và muốn agent tự làm từng bước.",
        "benefit": "Bám sát 100% nội dung spec, không tự ý thêm thắt tính năng ngoài luồng."
    },
    "tdd": {
        "what": "Lập trình hướng kiểm thử (Test-Driven Development): Viết test lỗi trước ➔ Viết code tối thiểu để test pass ➔ Tối ưu hoá (Refactor).",
        "when": "Dùng cho mọi tính năng quan trọng hoặc khi sửa các lỗi nghiêm trọng.",
        "benefit": "Bảo đảm code không có bug tiềm ẩn, an tâm sửa đổi mã nguồn về sau."
    },
    "claude-task-runner": {
        "what": "Runner tự động nhận và làm nhiệm vụ: Tuân thủ ranh giới tuyệt đối, tự chạy build/test và viết TASK_REPORT.md.",
        "when": "Dùng khi làm việc theo mô hình Tech Lead AI giao việc cho Coding Agent con.",
        "benefit": "Tự động hóa hoàn toàn chu trình nhận việc - viết code - kiểm tra - báo cáo."
    },
    "loop-me": {
        "what": "Vòng lặp tương tác có giám sát: Giữ agent trong vòng lặp thử nghiệm - sửa chữa có người dùng duyệt.",
        "when": "Dùng khi cần agent tinh chỉnh giao diện hoặc thuật toán nhiều vòng lặp.",
        "benefit": "Kiểm soát được tốc độ và chất lượng của từng lần thử."
    },
    "teach": {
        "what": "Gia sư AI 1-1: Dạy bạn một công nghệ hoặc kỹ năng mới từng bước tương tác.",
        "when": "Dùng khi bạn muốn tự học và hiểu sâu một khái niệm thay vì chỉ bảo AI làm hộ.",
        "benefit": "Học nhanh, có bài tập thực hành ngay trong thư mục làm việc."
    },
    "writing-beats": {
        "what": "Kỹ thuật viết tài liệu theo từng nhịp (beats) gãy gọn, súc tích.",
        "when": "Dùng khi cần viết tài liệu hướng dẫn kỹ thuật hoặc bài viết blog chuyên sâu.",
        "benefit": "Văn phong mạch lạc, dễ đọc, truyền tải thông điệp chính xác."
    },
    "writing-fragments": {
        "what": "Tổ chức tài liệu thành các mảnh nhỏ tái sử dụng (Atomic fragments).",
        "when": "Dùng khi xây dựng hệ thống tài liệu lớn cho dự án.",
        "benefit": "Dễ cập nhật, tránh lặp lại thông tin ở nhiều nơi."
    },
    "writing-shape": {
        "what": "Định hình cấu trúc văn bản tổng thể trước khi viết chi tiết.",
        "when": "Dùng trước khi bắt tay viết các tài liệu dài hoặc báo cáo dự án.",
        "benefit": "Không bị lan man, bài viết có mở bài, thân bài, kết luận chặt chẽ."
    },
    "writing-for-agents": {
        "what": "Soạn thảo văn bản cho AI Agent: Viết SKILL.md, AGENTS.md chuẩn chỉ để các agent đọc là hiểu ngay.",
        "when": "Dùng khi bạn muốn viết một skill mới hoặc tùy chỉnh hướng dẫn cho AI.",
        "benefit": "Agent đọc tài liệu là thực thi chính xác, không bị hiểu nhầm hoặc làm sai quy cách."
    },
    "code-review": {
        "what": "Rà soát mã 2 trục song song: Kiểm tra song song Chuẩn Coding (Standards) và Tính Đúng Đặc Tả (Spec).",
        "when": "Dùng trước khi tạo Pull Request hoặc commit code quan trọng.",
        "benefit": "Bắt trọn cả lỗi phong cách code lẫn lỗi sai nghiệp vụ."
    },
    "codebase-line-budget-guard": {
        "what": "Thần hộ vệ giới hạn số dòng code: Ngăn không cho file code vượt quá 300-500 dòng.",
        "when": "Agent tự động kích hoạt khi thấy file bắt đầu dài và phức tạp.",
        "benefit": "Buộc agent phải chia nhỏ component/file từ sớm, giữ dự án luôn gọn gàng và dễ đọc."
    },
    "resolving-merge-conflicts": {
        "what": "Gỡ xung đột Git chuyên nghiệp: Lần theo mục đích ban đầu của cả 2 nhánh để gỡ từng hunk, tuyệt đối không abort.",
        "when": "Dùng khi gặp xung đột git merge hoặc git rebase.",
        "benefit": "Giữ lại được đầy đủ tính năng của cả 2 bên mà không làm mất code của ai."
    },
    "git-guardrails-claude-code": {
        "what": "Hàng rào bảo vệ Git: Ngăn chặn các lệnh git nguy hiểm làm mất code hoặc ghi đè lịch sử bừa bãi.",
        "when": "Bảo vệ an toàn khi agent tự động thao tác với Git.",
        "benefit": "An tâm tuyệt đối không sợ mất mát commit hay hỏng repo."
    },
    "setup-pre-commit": {
        "what": "Thiết lập pre-commit hooks: Tự động chạy linter và formatter trước mỗi lần commit.",
        "when": "Dùng khi thiết lập dự án cho nhóm nhiều lập trình viên.",
        "benefit": "Đảm bảo 100% code commit lên đều sạch sẽ và đồng bộ."
    },
    "retro": {
        "what": "Họp rút kinh nghiệm (Retrospective): Phân tích những gì làm tốt, chưa tốt và cải tiến quy trình làm việc với AI.",
        "when": "Dùng sau khi kết thúc một mốc dự án (milestone) hoặc sau khi vừa giải quyết xong sự cố lớn.",
        "benefit": "Hệ thống và agent ngày càng thông minh và ăn ý hơn qua từng đợt làm việc."
    },
    "handoff": {
        "what": "Bàn giao ngữ cảnh: Nén toàn bộ bối cảnh cuộc trò chuyện thành tài liệu ngắn gọn cho agent hoặc ca làm việc tiếp theo.",
        "when": "Dùng khi cửa sổ ngữ cảnh (context window) sắp đầy hoặc chuyển giao việc cho người khác.",
        "benefit": "Không bị mất thông tin quan trọng khi bắt đầu phiên chat mới."
    },
    "claude-handoff": {
        "what": "Biên bản bàn giao chuyên dụng cho Claude Code tiếp quản công việc liền mạch.",
        "when": "Dùng khi chuyển đổi giữa các model AI hoặc mở session Claude mới.",
        "benefit": "Session mới nắm bắt ngay việc cần làm mà không cần giải thích lại từ đầu."
    },
    "agent-disorientation-recovery": {
        "what": "Cứu hộ khẩn cấp khi Agent mất phương hướng: Đóng băng không gian làm việc, định vị lại tọa độ và phẫu thuật gỡ lỗi an toàn.",
        "when": "Dùng khi agent bắt đầu sửa lung tung, lặp lại lỗi, hoặc bối rối sau khi context bị nén.",
        "benefit": "Kéo agent trở lại đúng hướng trong 3 bước, cứu dự án khỏi nguy cơ bị phá hỏng."
    },
    "code-bug-inspector": {
        "what": "Thanh tra mã lỗi tự động: Chạy script Python quét tĩnh AST phát hiện lỗi cú pháp, type, import vòng và logic.",
        "when": "Dùng khi dự án gặp lỗi đỏ mà chưa rõ nguồn cơn bắt đầu từ file nào.",
        "benefit": "Tìm ra tận gốc nguyên nhân trong 3 giây kèm đề xuất cách sửa tối ưu."
    },
    "diagnosing-bugs": {
        "what": "Quy trình gỡ lỗi có kỷ luật: Tái hiện bug bằng test ➔ Thu nhỏ phạm vi ➔ Đặt giả thuyết ➔ Đặt log ➔ Sửa ➔ Kiểm thử hồi quy.",
        "when": "Dùng khi gặp các con bug khó chịu, chập chờn hoặc lỗi sụt giảm hiệu năng.",
        "benefit": "Sửa đúng tận gốc, không bao giờ sửa mò (guess-and-check)."
    },
    "system-logs-and-diagnostics": {
        "what": "Nhật ký hệ thống & Chẩn đoán từ xa: Xây dựng nút 'Chẩn đoán' và hệ thống log chuỗi kết nối (Chrome Extension / Web App).",
        "when": "Dùng khi lập trình Chrome Extension MV3 hoặc các app giao tiếp nền phức tạp.",
        "benefit": "Bắt chính xác các lỗi kinh điển: Message port closed, ngắt kết nối sidepanel ↔ content script."
    },
    "triage": {
        "what": "Phân loại và điều phối sự cố (Triage): Đưa issue qua máy trạng thái để thẩm định, phân loại mức độ ưu tiên và viết brief cho agent sửa.",
        "when": "Dùng khi tiếp nhận bug report hoặc feature request mới trên issue tracker.",
        "benefit": "Công việc được xếp hàng ngăn nắp, có đủ thông tin trước khi bắt tay vào sửa."
    },
    "macos-m1-multiagent-setup": {
        "what": "Cẩm nang cài đặt Multi-Agent trên Apple Silicon (Mac M1/M2/M3/M4): Vượt qua các lỗi wheel, C compiler và môi trường Python.",
        "when": "Dùng khi cài CrewAI, LangChain, OpenRouter trên máy Mac chip Apple Silicon.",
        "benefit": "Cài đặt suôn sẻ trong 5 phút, không bị kẹt ở các lỗi biên dịch thư viện C/C++."
    },
    "multiagent-setup-crossplatform": {
        "what": "Cài đặt Multi-Agent tương thích đa nền tảng: Hướng dẫn chi tiết cho cả macOS, Linux và Windows.",
        "when": "Dùng khi triển khai hệ thống Agent lên máy chủ Linux hoặc máy dev Windows.",
        "benefit": "Đảm bảo mã nguồn agent chạy trơn tru trên mọi hệ điều hành."
    },
    "chrome-web-store-prep": {
        "what": "Chuẩn hóa extension nộp Chrome Web Store: Rà soát quyền hạn tối thiểu, kiểm tra bảo mật MV3, chuẩn bị icon và privacy policy.",
        "when": "Dùng trước khi nộp tiện ích lên Chrome Web Store duyệt.",
        "benefit": "Tăng tối đa tỷ lệ được duyệt ngay trong lần đầu, tránh bị Google từ chối vì thừa quyền hạn."
    },
    "wizard": {
        "what": "Trình phù thủy tương tác: Tạo script bash hướng dẫn con người từng bước làm các thao tác nhạy cảm (API key, server, deploy).",
        "when": "Dùng cho các công việc thủ công mà AI không được tự ý can thiệp một mình.",
        "benefit": "Hướng dẫn từng click chuột, an toàn tuyệt đối cho dữ liệu mật."
    },
    "setup-matt-pocock-skills": {
        "what": "Khởi tạo cấu hình repo theo chuẩn của bộ engineering skills (issue tracker, nhãn triage, bố cục docs).",
        "when": "Chạy 1 lần duy nhất trên repo mới trước khi dùng các skills khác.",
        "benefit": "Đồng bộ môi trường làm việc chuẩn mực."
    },
    "migrate-to-shoehorn": {
        "what": "Chuyển đổi dự án sang kiến trúc Shoehorn gọn gàng.",
        "when": "Dùng khi cần tái cấu trúc dự án cũ sang chuẩn mới.",
        "benefit": "Đơn giản hóa việc tổ chức mã nguồn."
    },
    "scaffold-exercises": {
        "what": "Tạo khung bài tập và câu đố lập trình tương tác.",
        "when": "Dùng khi tạo tài liệu giảng dạy hoặc bài kiểm tra kỹ năng cho học viên.",
        "benefit": "Tự động sinh test case và boilerplate câu đố nhanh chóng."
    }
}

for root, dirs, files in os.walk(skills_dir):
    if "SKILL.md" in files:
        rel = os.path.relpath(root, skills_dir)
        parts = rel.split(os.sep)
        category = parts[0]
        skill_name = parts[-1]
        
        filepath = os.path.join(root, "SKILL.md")
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        name = skill_name
        description = ""
        user_invoked = False
        
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        body = content
        if fm_match:
            fm = fm_match.group(1)
            body = fm_match.group(2)
            name_m = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
            if name_m:
                name = name_m.group(1).strip().strip("\"'")
            desc_m = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
            if desc_m:
                description = desc_m.group(1).strip().strip("\"'")
            if "disable-model-invocation: true" in fm:
                user_invoked = True
                
        if not description:
            lines = [l.strip() for l in body.split("\n") if l.strip() and not l.startswith("#")]
            description = lines[0] if lines else "Engineering skill for coding agents."
            
        branch = branch_mapping.get(skill_name, "⚡ Viết Code & TDD")
        domain = domain_mapping.get(skill_name, "💻 Lập trình & Kỹ thuật")
        
        # Pull Vietnamese explanation
        vi_meta = vi_explanations.get(skill_name, {
            "what": description,
            "when": "Dùng khi cần giải quyết công việc kỹ thuật chuyên sâu.",
            "benefit": "Tăng độ tin cậy và sự chính xác cho Agent."
        })
        
        skills.append({
            "id": skill_name,
            "name": name,
            "category": category,
            "domain": domain,
            "branch": branch,
            "userInvoked": user_invoked,
            "description": description,       # Original English / source description
            "vi": vi_meta,                    # Rich Vietnamese plain explanation
            "content": body[:4000],          # Original markdown content preview
            "path": f"skills/{rel}/SKILL.md"
        })

skills.sort(key=lambda s: (s["domain"], s["branch"], s["name"]))

output_js = os.path.join(output_web_dir, "skills-data.js")
with open(output_js, "w", encoding="utf-8") as f:
    f.write("// Auto-generated skills data catalog with bilingual English & Vietnamese explanations\n")
    f.write("window.SKILLS_DATA = " + json.dumps(skills, ensure_ascii=False, indent=2) + ";\n")

print(f"Successfully generated {output_js} with {len(skills)} skills and rich Vietnamese explanations!")
