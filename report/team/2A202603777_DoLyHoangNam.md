# Báo cáo cá nhân — 2A202603777_DoLyHoangNam

## 1. Thông tin thành viên

- Họ tên: Đỗ Lý Hoàng Nam
- MSSV: 2A202603777
- Email: dolyhoangnam13072005@gmail.com
- GitHub: DoLyHoangNam

## 2. Phần việc phụ trách

- Nhóm trưởng & Kiểm soát chất lượng (QA) trên nhánh `main`:
  - Thiết lập môi trường (CP0/CP1), quản lý tiến độ và phân công 5 thành viên trong `TEAM.md`.
  - Review và merge toàn bộ Pull Request (#1–#7) từ các thành viên (`Hau`, `DoanCongHai`, `LeNgocKhanh`, `Phong`) vào `main` bằng merge commit, kiểm soát không sửa file thước đo.
  - Viết bộ test QA (`src/tests/test_qa_must_pass.py`) kiểm tra các điều kiện must-pass (prompt injection, rò rỉ `CANARY_SECRET_*`/PII, approval thuộc claim khác, crash 3 mốc và resume).
  - Chạy `pytest -q`, `pytest -m student`, crash suite (`src/reports/crash.json`), benchmark 4 shape × 5 seed (`src/reports/benchmark.json`) và `python -m lab8.check_submission`.
  - Triển khai phần mở rộng Bonus Topic B3 (`src/bonus/swarm_verified.py`, 8 ca đối kháng `src/bonus/cases.jsonl` + `world.json`, 3 test `src/tests/test_bonus_swarm_verified.py` và `report/team/bonus_report.md`).

## 3. Đóng góp cụ thể

- Thiết lập repo nhóm, cấu hình `.venv` (Python 3.12.16) và kiểm tra cổng host đầu buổi (`54 passed` → `101 passed` sau khi gộp đủ test của cả 5 thành viên và Bonus B3).
- Cập nhật thông tin phân công 5 thành viên trong `TEAM.md` (`35d58b2`, `05b97b6`, `bf70d26`), duyệt và merge PR #1 (`387a7d0`), PR #2 (`ad025c3`), PR #3 (`60b7668`), PR #4 (`f719eb2`), PR #5 (`0b474e1`), PR #6 (`a26c561`), PR #7 (`e1d8649`).
- Viết bộ kiểm tra must-pass và độ bền crash trong `src/tests/test_qa_must_pass.py` (`6e10b54`).
- Chạy `lab8.crash_test` đạt `crash_safety = 20/20` (`src/reports/crash.json`) và `lab8.benchmark` 4 shape × 14 claim × 5 seed (`src/reports/benchmark.json`): `workflow` đạt `pass_rate = 1.0`, `pass^5 = 1.0`, `seed_variance = 0.0`, `cost/success = 28.79` VND.
- Triển khai Bonus Topic B3 (`15ebe13`): viết code verifier cho `swarm_verified` kéo kết quả trên bộ public về `1.000` (`49.00` VND/success) và trên 8 ca đối kháng từ `0.900` (`swarm`) lên `1.000` (`55.30` VND/success).
- Quyết định kỹ thuật: tách kiểm thử QA thành hai nhóm (host-level chạy mặc định qua `pytest -q` và nhóm `@pytest.mark.student` kiểm tra adversarial must-pass trên cả 3 shape của nhóm) để giữ cổng host luôn xanh trong lúc các nhánh phát triển song song.

## 4. Bằng chứng

- File code & test đã thêm: `src/tests/test_qa_must_pass.py`, `src/bonus/swarm_verified.py`, `src/bonus/cases.jsonl`, `src/bonus/world.json`, `src/tests/test_bonus_swarm_verified.py`.
- Kết quả test: `pytest -q` (`101 passed, 263 deselected`), `pytest -q -m student -o addopts=` (`263 passed, 101 deselected`), `lab8.check_submission` (`0 FAIL, 0 WARN`).
- Báo cáo công cụ sinh ra: `src/reports/crash.json` (`crash_safety: 20/20`), `src/reports/benchmark.json` (70 trial/shape, vd: `R-workflow-C-001-s11`), `src/reports/bonus_benchmark.json`, `src/reports/bonus_adversarial.json`, `report/team/bonus_report.md`.
- Commit chính: `35d58b2`, `05b97b6`, `6e10b54`, `15ebe13`, `bf70d26`.

## 5. Công cụ AI đã dùng

- Công cụ: Antigravity (Gemini) để rà soát toàn bộ tài liệu đề bài/contract/rubric, hỗ trợ phân công 5 thành viên đúng tiêu chí chấm điểm, soạn bộ test QA `src/tests/test_qa_must_pass.py`, triển khai Bonus B3 `swarm_verified`, và kiểm tra tính nhất quán giữa các file báo cáo của nhóm trước khi nộp.
- Cách tự kiểm tra kết quả: đối chiếu trực tiếp với `RULES.md`, `RUBRIC.md`, `docs/business_rules.md`, `docs/contracts.md`, `docs/bonus_topics.md`; chạy độc lập `python -m lab8.smoke`, `python -m pytest -q`, `python -m pytest -q -m student -o addopts=`, `python -m lab8.crash_test`, `python -m lab8.benchmark` và `python -m lab8.check_submission` trong `src/` để xác minh kết quả thực tế.

## 6. Tự đánh giá

- Hoàn thành đầy đủ 100% vai trò Nhóm trưởng, QA và triển khai Bonus B3: cổng host xanh (`101 passed`), 3 shape pass 100% ma trận public (`263 passed`), crash safety `20/20`, toàn bộ 5 thành viên đều có commit kỹ thuật, test cá nhân và báo cáo cá nhân, `check_submission` đạt `0 FAIL, 0 WARN`.
