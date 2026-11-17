# Báo cáo cá nhân — 2A202603777_DoLyHoangNam

## 1. Thông tin thành viên

- Họ tên: Đỗ Lý Hoàng Nam
- MSSV: 2A202603777
- Email: dolyhoangnam13072005@gmail.com
- GitHub: DoLyHoangNam

## 2. Phần việc phụ trách

- Nhóm trưởng & Kiểm soát chất lượng (QA) trên nhánh `main` / `DoLyHoangNam_2A202603777`:
  - Thiết lập môi trường (CP0/CP1), quản lý tiến độ và phân công 5 thành viên trong `TEAM.md`.
  - Review và merge Pull Request từ các thành viên (`Hau`, `DoanCongHai`, `LeNgocKhanh`, `Phong`) vào `main` bằng merge commit, kiểm soát không sửa file thước đo.
  - Viết bộ test QA (`src/tests/test_qa_must_pass.py`) kiểm tra các điều kiện must-pass (prompt injection, rò rỉ `CANARY_SECRET_*`/PII, approval thuộc claim khác, crash 3 mốc và resume).
  - Chạy `pytest -q`, `pytest -m student`, crash suite (`src/reports/crash.json`), benchmark 4 shape × 5 seed (`src/reports/benchmark.json`), tự kiểm `student_drop/` (khi có) và `python -m lab8.check_submission`.

## 3. Đóng góp cụ thể

- Thiết lập repo nhóm, cấu hình `.venv` (Python 3.12.16) và kiểm tra cổng host đầu buổi (`54 passed` → `82 passed` sau khi bổ sung test QA và test của thành viên).
- Cập nhật thông tin phân công 5 thành viên trong `TEAM.md` (`35d58b2`, `05b97b6`), duyệt và merge PR #1 (`387a7d0` — Shape B), PR #2 (`ad025c3` — Shape A), PR #3 (`60b7668` — Shape C).
- Viết bộ kiểm tra must-pass và độ bền crash trong `src/tests/test_qa_must_pass.py` (5 test host-level + 15 test `@pytest.mark.student` trên `workflow`, `single`, `orchestrator`).
- Chạy `lab8.crash_test` đạt `crash_safety = 20/20` (`src/reports/crash.json`) và `lab8.benchmark` 4 shape × 14 claim × 5 seed (`src/reports/benchmark.json`): `workflow` đạt `pass_rate = 1.0`, `pass^5 = 1.0`, `seed_variance = 0.0`, `cost/success = 28.79` VND (thấp nhất).
- Quyết định kỹ thuật: tách kiểm thử QA thành hai nhóm (host-level chạy mặc định qua `pytest -q` và nhóm `@pytest.mark.student` kiểm tra adversarial must-pass trên cả 3 shape của nhóm) để giữ cổng host luôn xanh trong lúc các nhánh phát triển song song.

## 4. Bằng chứng

- File test đã thêm: `src/tests/test_qa_must_pass.py`
- Kết quả test: `pytest -q` (`82 passed, 263 deselected`), `pytest -q -m student -o addopts=` (`263 passed, 82 deselected`)
- Báo cáo công cụ sinh ra: `src/reports/crash.json` (`crash_safety: 20/20`), `src/reports/benchmark.json` (vd: `R-workflow-C-001-s11`, 70 trial/shape)
- Commit chính: `35d58b2`, `05b97b6`, và commit chốt cuối `<TODO sau CP5>`

## 5. Công cụ AI đã dùng

- Công cụ: Antigravity (Gemini) để rà soát toàn bộ tài liệu đề bài/contract/rubric, hỗ trợ phân công 5 thành viên đúng tiêu chí chấm điểm, soạn bộ test QA `src/tests/test_qa_must_pass.py` và rà soát PR của thành viên trước khi merge.
- Cách tự kiểm tra kết quả: đối chiếu trực tiếp với `RULES.md`, `RUBRIC.md`, `docs/business_rules.md`, `docs/contracts.md`; chạy độc lập `python -m lab8.smoke`, `python -m pytest -q`, `python -m pytest -q -m student -o addopts=`, `python -m lab8.crash_test`, `python -m lab8.benchmark` và `python -m lab8.check_submission` trong `src/` để xác minh kết quả thực tế.

## 6. Tự đánh giá

- Đã hoàn thành đầy đủ vai trò kiểm soát chất lượng và tổng hợp số liệu CP1–CP5 (cổng host xanh, 3 shape pass 100% public matrix + QA must-pass, crash 20/20); tiếp tục theo dõi hoàn thiện test cá nhân của các thành viên còn lại và rà soát `check_submission` đạt `0 FAIL` trước khi chốt nộp.
