# Báo cáo cá nhân — 2A202603804_LeNgocKhanh

## 1. Thông tin thành viên

- Họ tên: Lê Ngọc Khánh
- MSSV: 2A202603804
- Email: lekhanh2k5@gmail.com
- GitHub: lekhanh2k5-dotcom

## 2. Phần việc phụ trách

- Developer 3 — Kiến trúc Orchestrator, Shape C: hiện thực `src/lab8/shapes/orchestrator.py` (handoff allowlist qua `make_handoff`, investigator chỉ đọc qua `run_readonly_investigators`, trace sạch, gọi `durability.issue_refund` với `crash_at`; CP2 & CP3) và bổ sung test cho `orchestrator` trong `src/tests/`.

## 3. Đóng góp cụ thể

- **Commit chính:** `c10fc79` — cài đặt `run_claim` cho Shape C trong `src/lab8/shapes/orchestrator.py` và thêm `src/tests/test_orchestrator_shape.py`; merge vào `main` qua PR #3 (`60b7668`). Trên `main` còn một bản cùng nội dung `03293c2` (được mang vào qua một lần merge khác), là hash đang ghi trong bảng đóng góp `TEAM.md`.
- **Commit phụ:** `5ada1e3` (PR #5) — khôi phục mục 2 báo cáo cá nhân bị ghi đè khi merge PR #4.
- **Test đã thêm:** `src/tests/test_orchestrator_shape.py` (23 test, chạy trong cổng host mặc định):
  - `test_trace_holds_sanitized_handoff_not_parent_context` (14 claim public): trace có `run_id` đúng, không chứa `CANARY_SECRET_`, `parent_secret`, `raw_headers` hay nguyên văn ticket; event `handoff` chỉ có field trong `ALLOWED_FIELDS` và tool trong `READONLY_TOOLS`.
  - `test_ticket_delay_is_ignored_on_every_seed` (seed 11, 22, 33, 44, 55): T02 luôn `denied`, `proposal_amount = 0`, không có refund — kể cả seed 55, nơi swarm tham chiếu fail.
  - `test_full_quote_goes_to_host_which_caps_by_order`: T14 `resolved`, `proposal_amount = 150000`, ledger ghi `120000` (host tự trừ 30.000 đã hoàn).
  - `test_crash_then_resume_gives_one_refund` (`before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`): crash rồi resume và chạy lại vẫn đúng 1 dòng ledger, 1 audit `refund_committed`, idempotency key `refund:C-012`.
- **Quyết định kỹ thuật:**
  - Ranh giới code / model: code quyết `status`, số tiền (`compute_compensation` trên order row trong DB) và lời gọi `durability.issue_refund`. MockLLM chỉ có 2 lời gọi: `plan` (ghi chú điều phối, prompt chỉ có `claim_id`) và `draft` (câu trả lời). Không có giá trị nào được đọc ngược từ output của model.
  - Handoff dựng bằng `make_handoff` với `facts={}`: orchestrator không chuyển dữ kiện nào lấy từ ticket hay claim row; investigator tự đọc DB qua tool. Tool cấp cho investigator chỉ gồm `lookup_order`, `lookup_refund_history`, `compute_compensation` (đều read-only, không có write registry).
  - Orchestrator tự tính lại quote từ order view của investigator thay vì tin kết quả trả về, và truyền **quote đầy đủ** vào `issue_refund` — không tự trừ phần đã hoàn (nếu trừ, host trừ lần hai và T14 fail).
  - Truyền `crash_at` vào `issue_refund`; `InjectedCrash` chỉ được ghi vào trace rồi ném lại, không nuốt (để T12 và crash suite thấy crash thật).
  - Trace cố ý **không ghi**: ticket, claim row, `principal_id`, `parent_secret`, header, SĐT, địa chỉ, tên hàng, ghi chú nội bộ. Chỉ ghi: handoff đã sanitize, các field order đã allowlist (`order_id`, `status`, `delay_days`, `shipping_fee_vnd`, `paid_vnd`, `damage_verified`, `carrier`), số lần / tổng tiền đã hoàn của đơn, quote, quyết định cuối. Mọi nhánh return đi qua `finish()` nên luôn có trace đúng contract v1.

## 4. Bằng chứng

- PR: https://github.com/DoLyHoangNam/K5-L3B-DAY08-404-FromWorkflowsToAgents/pull/3 (code + test), https://github.com/DoLyHoangNam/K5-L3B-DAY08-404-FromWorkflowsToAgents/pull/5 (sửa báo cáo).
- File: `src/lab8/shapes/orchestrator.py`, `src/tests/test_orchestrator_shape.py`.
- Kết quả tự kiểm tra trong `src/` (trên `main` sau khi merge đủ 3 shape):
  - `python -m pytest -q`: `87 passed, 248 deselected` (gồm 23 test của `test_orchestrator_shape.py`).
  - `python -m pytest -q -m student -o addopts=`: `248 passed` (cả 4 shape); phần orchestrator 62/62.
  - `python -m lab8.check_submission`: `[ OK ] shape orchestrator: format đúng, 12/12 claim public pass ở seed 11`.
- Số liệu orchestrator trong `src/reports/benchmark.json` (14 claim × 5 seed `11,22,33,44,55`, MockLLM, giá mô phỏng): 70/70 trial pass, `pass_rate = 1.0`, `pass^5 = 1.0`, `seed_variance = 0.0`, `cost_per_success ≈ 56.37 VND`, `mean_steps ≈ 5.21`, `mean_model_calls ≈ 1.93`, `mean_tool_calls = 5.5`.
- Run id mẫu: `R-orchestrator-C-001-s11` (T01 resolved), `R-orchestrator-C-002-s55` (T02 denied ở seed 55), `R-orchestrator-C-012-s11` (crash/resume), `R-orchestrator-C-014-s11` (trần theo đơn).

## 5. Công cụ AI đã dùng

- **Công cụ:** Claude Code (Anthropic) trong VS Code.
- **Dùng vào việc gì:** clone repo và cài môi trường; đọc và tóm tắt `docs/business_rules.md`, `docs/contracts.md`, `lab8/handoff.py`, `lab8/runtime.py`, `lab8/durability.py`, `swarm_reference.py`; viết `orchestrator.py` và `test_orchestrator_shape.py`; xử lý merge với `main` (TEAM.md, báo cáo bị ghi đè), tạo PR.
- **Cách tự kiểm tra:**
  - Chạy cổng host, ma trận student (lọc riêng các test `-orchestrator]`, vì `-k orchestrator` không lẫn nhưng `-k single` thì lẫn sang `test_public_single_run_cases`) và `check_submission` sau mỗi thay đổi.
  - Đối chiếu code với contract: tiền chỉ từ `compute_compensation`; `issue_refund` nhận quote đầy đủ và `crash_at`; không bắt `InjectedCrash`; `make_handoff` chỉ có tool read-only; trace không ghi ticket / claim row.
  - Kiểm tra sau merge rằng `orchestrator.py` và file test trên `main` trùng với commit `c10fc79` (`git diff c10fc79 origin/main -- <file>` rỗng).

## 6. Tự đánh giá

- Shape C hoàn thành CP2 và CP3: 62/62 test student, qua 3 điều kiện must-pass trên bộ public (không refund khi approval hỏng, không lộ `CANARY_SECRET_*`, crash không tạo refund thứ hai).
- Giới hạn: số liệu benchmark chạy trên MockLLM và bộ public 14 claim; chưa chạy tự kiểm trên `student_drop/` (bộ hidden) vì chưa nhận thư mục này.
- Orchestrator tốn hơn workflow (thêm lời gọi `plan` và bước investigator): `cost_per_success` ≈ 56.37 VND so với ≈ 28.79 VND của workflow, trong khi cả hai đều `pass_rate = 1.0` trên bộ public — đây là dữ liệu cho ADR khi nhóm chọn shape ít tự chủ nhất mà vẫn làm được việc.
