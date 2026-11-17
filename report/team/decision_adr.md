# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: ca52050
- Run id dẫn chứng: R-workflow-C-001-s11, R-workflow-C-002-s55, R-swarm-C-002-s55
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0.000000
- Cost per success (mô phỏng, VND): 28.79
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0

## Vì sao shape này

So sánh trên cùng corpus công khai 14 claims qua 5 seeds (70 trials/shape) tại `src/reports/benchmark.json`, kiến trúc `workflow` (Shape A) chứng minh ưu thế tuyệt đối về mọi chỉ số hiệu năng và độ ổn định. `workflow` đạt `pass_rate` tuyệt đối 1.000 (70/70), `pass^5` đạt 1.000, và phương sai giữa các hạt giống `seed_variance` bằng 0.000000 (hoàn toàn tất định, không suy giảm qua các seed 11, 22, 33, 44, 55). Về mặt kinh tế và tài nguyên tính toán, `workflow` có chi phí mô phỏng trên mỗi ca thành công thấp nhất (28.79 VND vs 29.54 VND của `single`, 56.37 VND của `orchestrator`, 49.57 VND của `swarm`) và số bước thực thi trung bình gọn gàng nhất (1.86 steps vs 3.79 của `single`, 5.21 của `orchestrator`, 2.80 của `swarm`). Do bài toán khiếu nại bồi thường LogiX-VN có không gian trạng thái đóng và các quy tắc nghiệp vụ rõ ràng (closed-world business rules), một pipeline workflow tất định bằng mã nguồn Python loại bỏ triệt để rủi ro ảo giác (hallucination), miễn nhiễm trước prompt injection từ ticket người dùng, và đảm bảo tuân thủ nghiêm ngặt chính sách công ty.

## Có đáng đổi lấy multi-agent không

Nhóm quyết định giữ nguyên `workflow` và không đánh đổi lấy các cấu trúc multi-agent (`orchestrator` hay `swarm`). Trên dữ liệu đo kiểm thực tế, multi-agent không đem lại bất kỳ cải thiện nào về tỷ lệ thành công (`workflow`, `single`, `orchestrator` đều đạt pass rate 1.000, trong khi `swarm` tham chiếu bị giảm xuống 0.986 và xuất hiện phương sai 0.000816 do tin vào số ngày trễ ghi trong ticket ở seed 55 tại claim C-002: `R-swarm-C-002-s55`). Đổi lại, multi-agent làm tăng vọt chi phí mô phỏng lên gần gấp đôi (orchestrator: 56.37 VND, tăng +95.8% so với workflow) và số bước điều phối tăng lên 5.21 bước (+180.4%).

Quyết định kiến trúc chỉ đảo lại (chọn `orchestrator` hoặc multi-agent) khi và chỉ khi thỏa mãn đồng thời các điều kiện:
1. Nghiệp vụ mở rộng sang dữ liệu phi cấu trúc hoặc đa phương thức (ví dụ: cần thị giác máy tính CV để thẩm định ảnh hàng hỏng, trích xuất hóa đơn vận chuyển dạng scan phức tạp).
2. Các bước nghiệp vụ có tính phân tán cao, cần gọi đồng thời nhiều dịch vụ/API bên thứ ba không đồng nhất mà một luồng tĩnh khó bao quát hết các nhánh lỗi.
3. Có cơ chế xác thực chéo (consensus/verifier) chặt chẽ giữa các agent để bù đắp chi phí token tăng thêm bằng việc giảm thiểu sai số phán đoán của con người.

## Trace và bằng chứng

Trace của nhóm tuân thủ nghiêm ngặt Trace Contract v1 (`docs/contracts.md`), lưu trữ nhật ký độc lập cho từng run id với cấu trúc `{"run_id": <run_id>, "events": [...]}`.
- Các event được ghi nhận trong `workflow`:
  + `order_view`: Ghi nhận dữ liệu tối thiểu cần cho thẩm định (`order_id`, `status`).
  + `quote`: Ghi nhận kết quả tính toán định lượng từ code (`amount_vnd`, `clauses`, `reason`).
  + `decision`: Ghi nhận quyết định trạng thái (`status`, `proposal_amount`, `reason`).
  + `crash`: Ghi nhận mốc sự cố giả lập (`crash_at`) trước khi ném ngoại lệ `InjectedCrash`.
- Các field cố ý **KHÔNG** ghi vào trace:
  + Tuyệt đối không ghi `parent_secret` từ bảng claims.
  + Không ghi dữ liệu định danh cá nhân (PII) của khách hàng từ bảng orders (`phone`, `address`, `recipient_name`).
  + Không ghi các ghi chú nội bộ nhạy cảm (`internal_note`) hay chi tiết đơn hàng thô (`item_name`).
  + Không đưa văn bản ticket thô (`ticket` text) của người dùng vào trace.
- Bảo vệ ranh giới an ninh: Grader áp dụng nguyên tắc fail-closed: nếu trace nằm ngoài thư mục chỉ định hoặc sai format (`missing_trace`, `stale_trace`, `invalid_trace`, `trace_run_id_mismatch`), lần chạy sẽ bị đánh rớt ngay lập tức. Đội ngũ an ninh kiểm chứng tính an toàn của hệ thống thông qua bộ quét tự động đối sánh biểu thức chính quy (quét tiền tố `CANARY_SECRET_*` và định dạng số điện thoại/địa chỉ), cùng việc kiểm tra tĩnh (static code analysis) đảm bảo mọi truy vấn dữ liệu đều đi qua các view rút gọn đã áp dụng allowlist (`get_claim_view`, `lookup_order`).

## Giới hạn

- Môi trường đánh giá sử dụng `MockLLM` dựa trên seed và tra cứu chuỗi mẫu định sẵn, chưa phản ánh đầy đủ độ trễ mạng, tính bất định (non-deterministic stochasticity), hay hiện tượng suy giảm ngữ cảnh của các mô hình ngôn ngữ lớn thương mại trong môi trường production.
- Chỉ số thời gian phản hồi (`latency`) được ghi nhận là `unavailable` do bản chất thực thi tức thì của mock framework.
- Bộ dữ liệu public gồm 14 claims tập trung vào các kịch bản kiểm chứng cơ bản; dù nhóm đã bổ sung 20 kịch bản crash (`reports/crash.json`), bộ test adversarial QA nội bộ (`test_qa_must_pass.py`), và 8 ca đối kháng trong Bonus B3, vẫn cần tiếp tục mở rộng kiểm thử trên các bộ dữ liệu quy mô lớn hơn với nhiều trường hợp góc (edge cases) trước khi triển khai thực tế.
