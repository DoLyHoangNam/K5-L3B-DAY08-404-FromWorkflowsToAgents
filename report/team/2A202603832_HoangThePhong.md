# Báo cáo cá nhân — 2A202603832_HoangThePhong

## 1. Thông tin thành viên

- Họ tên: Hoàng Thế Phong
- MSSV: 2A202603832
- Email: phonghoangthe112@gmail.com
- GitHub: Hphong2305 (htphong23)

## 2. Phần việc phụ trách

- Chuyên viên Báo cáo & Dữ liệu (nhánh `Phong`):
  - Phân tích và tổng hợp số liệu thực nghiệm từ bộ dữ liệu chuẩn `src/reports/benchmark.json` (4 shape × 14 claims × 5 seeds = 280 trials) và `src/reports/crash.json` (20 kịch bản crash).
  - Thực hiện thực nghiệm ablation R3 (`reports/ablation_benchmark.json`) đo lường sự đánh đổi hiệu năng - chi phí giữa Workflow (Shape A) và Orchestrator (Shape C).
  - Soạn thảo và hoàn thiện hồ sơ quyết định kiến trúc: `report/team/decision_adr.md`.
  - Soạn thảo và hoàn thiện phiếu nghiên cứu: `report/team/research_card.md`.
  - Viết toàn bộ nội dung báo cáo nhóm 8 mục: `report/team/group_report.md`.
  - Xây dựng bộ test kiểm tra tính toàn vẹn dữ liệu và tuân thủ định dạng: `src/tests/test_phong_report_metrics.py`.

## 3. Đóng góp cụ thể

- **Xây dựng bộ test kiểm chuẩn cá nhân (`src/tests/test_phong_report_metrics.py`):** Viết 6 test chạy ở tầng host (`pytest -q`, không gắn `@pytest.mark.student`), thực thi tức thì (0.04s) nhằm xác minh:
  + Tính đầy đủ và nhất quán của 4 shapes trong `src/reports/benchmark.json` (đủ 70 trials/shape, `workflow` đạt `pass_rate = 1.0`, `seed_variance = 0.0`, chi phí thấp nhất 28.79 VND).
  + Khả năng chịu lỗi tuyệt đối `crash_safety: "20/20"` trong `src/reports/crash.json`.
  + Công thức tính phương sai mẫu (population variance) và tỷ lệ bền vững `pass^5` trong `lab8.metrics.summarize`.
  + Sự tuân thủ định dạng máy đọc của các file báo cáo `decision_adr.md`, `research_card.md`, và `group_report.md`.
- **Thực hiện thực nghiệm Ablation R3 (Architecture choices):** Chạy thực nghiệm với lệnh:
  `python -m lab8.benchmark --shapes workflow,orchestrator --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_benchmark.json`
  Kết quả xác nhận giả thuyết khoa học: việc chuyển đổi từ Workflow sang Orchestrator làm tăng chi phí mô phỏng thêm +95.8% (từ 28.79 VND lên 56.37 VND) và tăng số bước từ 1.86 lên 5.21 bước mà không cải thiện tỷ lệ pass rate (cả hai đều đạt 1.000).
- **Lập luận quyết định kiến trúc (ADR):** Đưa ra luận điểm bảo vệ kiến trúc `workflow`: loại bỏ hoàn toàn nguy cơ prompt injection từ văn bản ticket của khách hàng, đảm bảo tính tất định và tuân thủ nghiêm ngặt chính sách nghiệp vụ.
- **Hoàn thiện tài liệu nhóm:** Viết đầy đủ 8 mục trong `report/team/group_report.md`, đối chiếu chính xác các ranh giới Code/Model, Trace Contract v1 và cơ chế xử lý trần đơn hàng (order cap).

## 4. Bằng chứng

- **Mã nguồn và bộ test:**
  + File test cá nhân: `src/tests/test_phong_report_metrics.py` (6 passed trong 0.04s).
  + File dữ liệu thực nghiệm: `src/reports/ablation_benchmark.json`.
- **Kết quả kiểm thử tự động:**
  + `pytest -q`: **101 passed, 263 deselected** (xanh 100%).
  + `pytest -q -m student -o addopts=`: **263 passed, 101 deselected** (xanh 100%).
  + `python -m lab8.check_submission`: **0 FAIL** (đạt chuẩn định dạng nộp bài của hệ thống grader).
- **Các báo cáo đã hoàn thành:**
  + `report/team/decision_adr.md` (chọn `workflow`, đầy đủ 4 mục phân tích sâu).
  + `report/team/research_card.md` (đầy đủ 7 trường nghiên cứu R3 và kết quả ablation).
  + `report/team/group_report.md` (hoàn thiện 8 mục theo chuẩn rubric).
- **Run ID dẫn chứng tiêu biểu:**
  + `R-workflow-C-001-s11` (thành công chuẩn với chi phí tối ưu).
  + `R-workflow-C-002-s55` (ổn định tất định tại seed 55).
  + `R-swarm-C-002-s55` (bằng chứng Swarm thất bại khi tin vào dữ liệu người dùng).

## 5. Công cụ AI đã dùng

- **Công cụ:** Antigravity AI Assistant (Gemini).
- **Mục đích sử dụng:**
  + Rà soát quy tắc chấm điểm và kiểm tra đối chiếu các trường bắt buộc theo `src/lab8/check_submission.py`.
  + Hỗ trợ cấu trúc hóa bài toán ablation và xây dựng các ca kiểm thử unit test cho các hàm thống kê trong `lab8.metrics`.
- **Phương thức tự kiểm tra kết quả:**
  + Mọi số liệu trong báo cáo đều được trích xuất trực tiếp bằng script Python từ file kết quả máy sinh `src/reports/benchmark.json`, `reports/crash.json` và `reports/ablation_benchmark.json`, tuyệt đối không nhập số liệu thủ công hoặc ước lượng.
  + Chạy kiểm thử tự động độc lập qua terminal sandbox: `pytest -q`, `pytest -v -k phong`, và `python -m lab8.check_submission` để đảm bảo tính đúng đắn trước khi commit.

## 6. Tự đánh giá

- **Mức độ hoàn thành:** Hoàn thành 100% nhiệm vụ Chuyên viên Báo cáo & Dữ liệu.
- **Chất lượng:** Toàn bộ hồ sơ báo cáo nhóm và cá nhân được hoàn thiện mạch lạc, bám sát số liệu thực nghiệm khoa học, không có lỗi định dạng máy đọc (`0 FAIL`), bộ test cá nhân chạy nhanh và ổn định. Sẵn sàng tạo Pull Request để nhóm trưởng review và merge vào `main`.
