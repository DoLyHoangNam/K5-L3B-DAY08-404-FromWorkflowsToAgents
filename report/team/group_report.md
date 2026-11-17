# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Tên nhóm: 404
- Thành viên:
  1. Đỗ Lý Hoàng Nam (MSSV: 2A202603777) — Nhóm trưởng & QA (`main` / `qa-testing`)
  2. Hoàng Thế Phong (MSSV: 2A202603832) — Chuyên viên Báo cáo & Dữ liệu (`Phong`)
  3. Nguyễn Văn Hậu (MSSV: 2A202603932) — Developer 2 — Kiến trúc Single Agent (`Hau`)
  4. Đoàn Công Hải (MSSV: 2A202603739) — Developer 1 — Kiến trúc Workflow (`DoanCongHai`)
  5. Lê Ngọc Khánh (MSSV: 2A202603804) — Developer 3 — Kiến trúc Orchestrator (`LeNgocKhanh`)
- Commit chốt (trùng `report/team/decision_adr.md`): `9153f85` *(nhóm trưởng cập nhật hash chốt cuối sau khi merge PR)*

---

## 2. Mục tiêu và cách tiếp cận

### 2.1. Hiểu bài toán
Hệ thống giải quyết bài toán tự động hóa quy trình xử lý bồi thường khiếu nại (claims resolution) cho đơn vị logistics LogiX-VN. Hệ thống phải đảm bảo 3 trụ cột kỹ thuật cốt lõi:
1. **Tính chính xác nghiệp vụ (Business Correctness):** Tuân thủ tuyệt đối các chính sách hiện hành (`effective_date <= 2026-11-15`, `is_current = 1`) bao gồm chính sách giao trễ (`SHIP-LATE-2026`) và hư hỏng hàng hóa (`DMG-04`). Quản lý trần bồi thường theo đơn hàng (`order-level cap`): tổng số tiền hoàn cho một đơn không vượt quá quyền lợi tối đa; nếu đã hoàn trước đó thì chỉ hoàn phần chênh lệch.
2. **An toàn sổ cái & Khả năng chịu sự cố (Ledger Durability & Crash Safety):** Ghi nhận giao dịch hoàn tiền thông qua cơ chế sổ cái bất biến (immutable ledger), sử dụng idempotency key `refund:{claim_id}` để đảm bảo gọi lại nhiều lần không tạo ra duplicate refund. Xử lý an toàn khi hệ thống gặp sự cố đột ngột (`InjectedCrash`) ở 3 mốc: trước khi tạo hiệu ứng (before effect), sau khi tạo hiệu ứng nhưng trước checkpoint, và sau checkpoint.
3. **Bảo mật ranh giới & An toàn dữ liệu (Security Boundary & Redaction):** Bảo vệ các bí mật hệ thống (`CANARY_SECRET_*`), không để rò rỉ PII người dùng (số điện thoại, địa chỉ, tên người nhận, ghi chú nội bộ) vào nhật ký thực thi (Trace). Xử lý nội dung văn bản ticket như dữ liệu không đáng tin cậy (untrusted user input), phòng chống tấn công chèn lệnh (prompt injection).

### 2.2. Phân công công việc
Nhóm 5 thành viên áp dụng quy trình Git Flow chuyên nghiệp với các nhánh tính năng độc lập:
- **Đỗ Lý Hoàng Nam:** Quản trị repo, thiết lập môi trường, xây dựng bộ test QA kiểm soát chất lượng (`test_qa_must_pass.py`), chạy crash test suite và benchmark, review và merge Pull Request.
- **Đoàn Công Hải:** Hiện thực Shape A (`workflow.py`) và bộ test `test_workflow.py`.
- **Nguyễn Văn Hậu:** Hiện thực Shape B (`single.py`) với vòng lặp ReAct và bộ test `test_single_shape.py`.
- **Lê Ngọc Khánh:** Hiện thực Shape C (`orchestrator.py`) với Typed Handoff, Read-only Investigators và bộ test `test_orchestrator_shape.py`. Đồng thời phát triển nghiên cứu mở rộng Topic Bonus B3 (`swarm_verified.py`).
- **Hoàng Thế Phong:** Phân tích dữ liệu từ `benchmark.json` và `crash.json`, thực hiện thực nghiệm ablation R3 (`ablation_benchmark.json`), soạn thảo `decision_adr.md`, `research_card.md`, hoàn thiện báo cáo nhóm và bộ test kiểm chứng chỉ số `test_phong_report_metrics.py`.

### 2.3. Thứ tự triển khai 4 shape
1. **Swarm Reference (Shape D):** Khảo sát mã nguồn mẫu có sẵn trong `swarm_reference.py` để nắm bắt contract đầu vào/đầu ra (`RunResult`, Trace Contract v1), phân tích điểm yếu cố hữu (vulnerability) khi Swarm tin vào số ngày trễ người dùng khai báo ở seed 55.
2. **Workflow (Shape A):** Xây dựng pipeline xử lý tuần tự tất định. Đây là shape đơn giản, ổn định nhất làm thước đo chuẩn (baseline).
3. **Single Agent (Shape B):** Nâng cấp lên agent tự chủ với vòng lặp ReAct, phân định rõ công cụ đọc và quyền hạn ghi của host.
4. **Orchestrator (Shape C):** Thiết kế kiến trúc phân rã điều phối với cơ chế typed handoff bảo mật, cô lập investigator ở chế độ chỉ đọc.

---

## 3. Giải pháp

### 3.1. Mô tả chi tiết ba shape nhóm hiện thực
- **Shape A — Workflow (`src/lab8/shapes/workflow.py`):**
  Thực thi theo luồng tuyến tính 7 bước tĩnh bằng mã nguồn Python:
  1. Mở kết nối DB, đọc claim thông qua view an toàn `get_claim_view` (không dùng `SELECT *`).
  2. Kiểm tra `order_id`: nếu thiếu, gọi `complete(purpose="draft")` và kết thúc với `status = "needs_info"`.
  3. Gọi `lookup_order` kiểm tra đơn hàng: nếu không thấy hoặc `principal_id` không khớp, kết thúc với `status = "escalated"`.
  4. Tính toán mức bồi thường bằng code nghiệp vụ tĩnh `compute_compensation(conn, order)` từ dòng đơn hàng trong DB; bỏ qua mọi số liệu trong ticket.
  5. Nếu `proposal <= 0`, kết thúc với `status = "denied"`.
  6. Nếu `proposal > 0`, chuyển toàn bộ quote vào `durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)`. Host sẽ tự động kiểm tra tính hợp lệ của approval và khấu trừ các khoản đã hoàn trước đó. Nếu crash xảy ra (`InjectedCrash`), ghi log và ném lại ngoại lệ để host xử lý.
  7. Trả về kết quả hoàn tất bằng `lab8.shapes.common.finish()`.
- **Shape B — Single Agent (`src/lab8/shapes/single.py`):**
  Triển khai mô hình tác tử đơn với vòng lặp ReAct tối đa 8 bước thông qua `lab8.runtime.run_react`. Hàm `decide` của agent nhận ngữ cảnh quan sát và lựa chọn công cụ phù hợp từ bộ công cụ đọc (`lookup_order`, `lookup_policy`, `compute_compensation`, `lookup_refund_history`). Agent tuyệt đối không có công cụ ghi sổ cái. Sau khi agent kết thúc vòng lặp và đưa ra đề xuất, mã wrapper ở tầng ngoài sẽ đóng vai trò chốt chặn để chuyển quote sang `durability.issue_refund`.
- **Shape C — Orchestrator (`src/lab8/shapes/orchestrator.py`):**
  Mô hình điều phối trung tâm kết hợp tác tử điều tra chuyên biệt:
  1. Orchestrator đọc thông tin claim qua `get_claim_view`.
  2. Khởi tạo một đối tượng điều phối chuẩn hóa `make_handoff` (`handoff.v1`) với danh sách công cụ được phép chỉ gồm các read-only tools (`lookup_order`, `lookup_refund_history`, `compute_compensation`). Không đưa dữ liệu nhạy cảm (`parent_secret`, ticket text) vào trường `facts`.
  3. Ủy thác cho các điều tra viên chỉ đọc chạy qua `run_readonly_investigators`.
  4. Orchestrator nhận dữ liệu view đã kiểm chứng, tự gọi `compute_compensation` trên dòng dữ liệu DB chuẩn và yêu cầu host phát hành tiền hoàn qua `durability.issue_refund`.

### 3.2. Ranh giới Code / Model (Code / Model Boundary)
Nhóm phân định ranh giới nghiêm ngặt theo khuyến nghị kiến trúc:
- **Code quyết định:** Trạng thái khiếu nại (`status`), số tiền bồi thường (`compute_compensation`), quyết định ghi sổ cái và xử lý crash recovery (`durability.issue_refund`).
- **Model phụ trợ:** `MockLLM` chỉ được phép dùng để sinh ghi chú điều phối (`plan`) và soạn thảo văn bản phản hồi khách hàng (`draft`). Đầu ra của LLM tuyệt đối không bao giờ được bóc tách ngược lại thành số tiền hoàn hay mã đơn hàng.
- **Ticket text:** Được coi là dữ liệu độc hại tiềm tàng, không bao giờ được đưa vào handoff facts hay lưu trực tiếp vào trace.

### 3.3. Handoff Allowlist & Trace Contract v1
- **Cơ chế Handoff:** Chỉ truyền danh sách trường tối thiểu thông qua cấu trúc `handoff.v1`. Investigator không có công cụ ghi (write registry trống) nên không thể thực hiện hành vi gian lận tài chính.
- **Trace Contract v1:** Mọi lần chạy đều xuất ra file trace độc lập `traces/<run_id>.json`. Nhóm áp dụng bộ lọc `TRACE_ORDER_FIELDS` chỉ giữ lại các trường không nhạy cảm (`order_id`, `status`, `delay_days`, `shipping_fee_vnd`, `paid_vnd`, `damage_verified`, `carrier`). Toàn bộ bí mật `CANARY_SECRET_*`, số điện thoại, địa chỉ nhận hàng và ghi chú nội bộ đều bị loại bỏ trước khi ghi trace.

---

## 4. Kết quả

### 4.1. Bảng số liệu tổng hợp 4 shape trên bộ Public Benchmark
*(Trích xuất trực tiếp từ file thực nghiệm chuẩn `src/reports/benchmark.json`, gồm 4 shape × 14 claims × 5 seeds = 280 trials)*:

| Shape | Pass Rate | Pass^5 | Seed Min - Max | Seed Variance | Cost / Success (VND) | Mean Steps | P95 Steps | Mean Model Calls | Mean Tool Calls |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Workflow** | **1.000** | **1.000** | 1.000 – 1.000 | **0.000000** | **28.79** | **1.86** | **2.0** | 1.00 | 2.79 |
| **Single** | **1.000** | **1.000** | 1.000 – 1.000 | **0.000000** | 29.54 | 3.79 | 4.0 | 2.79 | 2.79 |
| **Orchestrator** | **1.000** | **1.000** | 1.000 – 1.000 | **0.000000** | 56.37 | 5.21 | 6.0 | 1.93 | 5.50 |
| **Swarm** | 0.986 | 0.929 | 0.929 – 1.000 | 0.000816 | 49.57 | 2.80 | 3.0 | 3.00 | 4.66 |

### 4.2. Khả năng chịu sự cố (Crash Safety)
Theo kết quả từ `src/reports/crash.json`, hệ thống đạt mức độ an toàn tuyệt đối:
- **Tỷ số an toàn sự cố (Crash Safety):** **20/20** (`100% passed`).
- Tất cả các kịch bản crash tại các mốc nhạy cảm (CR-01 đến CR-05: trước effect; CR-06 đến CR-12: sau effect trước checkpoint; CR-13 đến CR-17: sau checkpoint; CR-18: xung đột số tiền khi gọi lại; CR-19: gọi lại khi mất approval; CR-20: crash trong swarm) đều phục hồi hoàn hảo mà không sinh ra duplicate refund hoặc lệch kiểm toán sổ cái.

### 4.3. Quyết định kiến trúc & Nghiên cứu
- **Quyết định kiến trúc:** Chọn `workflow` làm shape nộp bài chính thức. Chi tiết phân tích chi phí, bằng chứng trace và các điều kiện đánh đổi được trình bày trong [decision_adr.md](decision_adr.md).
- **Thực nghiệm Ablation R3:** Tiến hành thực nghiệm kiểm chứng giả thuyết về chi phí topology giữa Workflow và Orchestrator, ghi nhận tại [research_card.md](research_card.md) và file số liệu [reports/ablation_benchmark.json](../src/reports/ablation_benchmark.json).
- **Nghiên cứu mở rộng (Bonus Topic B3):** Xây dựng `swarm_verified.py` bổ sung chốt chặn xác thực chéo (Verifier node), khắc phục triệt để lỗi seed 55 của Swarm gốc và vượt qua 8 ca kiểm thử đối kháng (xem [bonus_report.md](bonus_report.md)).

---

## 5. Khó khăn và cách xử lý

1. **Khó khăn về tính toán trần bồi thường theo đơn hàng (Order-level Cap) trong T13 và T14:**
   - *Vấn đề:* Đơn hàng `O-505` (T13) đã được hoàn tiền phí ship ở một claim trước đó. Đến claim sau, khách hàng tiếp tục yêu cầu hoàn phí ship. Tương tự ở T14 (`O-515`), đơn đã hoàn ship 30.000 VND, nay phát sinh bồi thường hàng hỏng 150.000 VND. Nếu agent tự trừ 30.000 VND rồi truyền 120.000 VND vào `issue_refund`, host sẽ khấu trừ thêm lần nữa dẫn đến số tiền thực nhận bị sai.
   - *Cách xử lý:* Bám sát quy định tại `docs/business_rules.md`: Agent luôn truyền **quote đầy đủ** (toàn bộ quyền lợi hợp lệ) vào `durability.issue_refund`. Host sẽ tự động tra cứu lịch sử và tính toán phần chênh lệch một cách chính xác.
2. **Khó khăn về nguy cơ rò rỉ dữ liệu nhạy cảm vào Trace Contract v1:**
   - *Vấn đề:* Khi trace log trạng thái đơn hàng để debug, nếu đưa toàn bộ row từ bảng `orders` sẽ làm lộ số điện thoại, địa chỉ và mã bí mật `CANARY_SECRET_*`, khiến bộ scanner bảo mật của grader fail-closed.
   - *Cách xử lý:* Tạo bộ lọc allowlist `TRACE_ORDER_FIELDS` và sử dụng `get_claim_view`, đảm bảo chỉ các trường an toàn được tuần tự hóa vào file JSON.
3. **Khó khăn về đồng bộ và kiểm thử giữa các thành viên:**
   - *Vấn đề:* Các thành viên phát triển đồng thời 3 shape khác nhau dễ gây xung đột git hoặc làm gãy cổng host mặc định (`pytest -q`).
   - *Cách xử lý:* Áp dụng chiến lược kiểm thử phân tầng: bộ test của từng shape được gắn marker `@pytest.mark.student`, bộ test QA chạy nhanh ở tầng host. Mọi thay đổi đều được kiểm tra qua `python -m lab8.check_submission` trước khi tạo PR.

---

## 6. Tổng hợp đóng góp

Tất cả 5 thành viên đều hoàn thành xuất sắc các phân công chuyên biệt và có commit mã nguồn / test cụ thể trên repo:
- **Đỗ Lý Hoàng Nam:** Quản trị nhóm, viết bộ test QA `test_qa_must_pass.py`, thực hiện crash suite và benchmark.
- **Đoàn Công Hải:** Xây dựng Shape A `workflow.py` và bộ test `test_workflow.py`.
- **Nguyễn Văn Hậu:** Xây dựng Shape B `single.py` và bộ test `test_single_shape.py`.
- **Lê Ngọc Khánh:** Xây dựng Shape C `orchestrator.py`, bộ test `test_orchestrator_shape.py` và nghiên cứu Bonus B3.
- **Hoàng Thế Phong:** Phân tích dữ liệu benchmark/crash, thực hiện ablation R3, viết báo cáo kiến trúc `decision_adr.md`, `research_card.md`, `group_report.md` và bộ test `test_phong_report_metrics.py`.

*(Chi tiết mã commit và đối chiếu kiểm thử được ghi nhận đầy đủ trong bảng đóng góp tại [TEAM.md](../../TEAM.md) và các báo cáo cá nhân).*

---

## 7. Hạn chế và hướng cải thiện

- **Giới hạn mô phỏng:** Hệ thống hiện kiểm thử trên nền tảng `MockLLM` với 14 claims mẫu; độ trễ mạng thực tế (`latency`) chưa được đo lường cụ thể (`unavailable`).
- **Khả năng mở rộng:** Trong tương lai, khi bài toán mở rộng sang phân tích biên bản giám định hiện trường bằng hình ảnh hoặc đối soát hóa đơn đa định dạng, kiến trúc sẽ cần chuyển đổi sang `orchestrator` hoặc `swarm_verified` có kết hợp các multimodal agent.
- **Giám sát thời gian thực:** Cần bổ sung hệ thống dashboard tập trung để trực quan hóa trace log và cảnh báo tức thời các nỗ lực tấn công prompt injection hoặc hành vi gọi lại bất thường.

---

## 8. Tài liệu tham khảo

1. Google Research (2026), *Towards a Science of Scaling Agent Systems*.
2. AgentArch, AACL (2026), *Empirical Trade-offs between Deterministic Workflows and Multi-Agent Topologies*.
3. MAST, NeurIPS (2025), *Why Do Multi-Agent LLM Systems Fail? A Failure Taxonomy for Multi-Agent LLM Systems*.
4. EMNLP (2026), *Rethinking Evaluation of MAS Efficiency*.
5. LogiX-VN Enterprise Architecture Specification & Durability Ledger Contract (Lab 8 Documentation).
