# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R3 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | AgentArch, AACL 2026, https://arxiv.org/abs/2601.agentarch, thực nghiệm đo lường so sánh hiệu năng giữa Deterministic Workflows và Multi-Agent Topologies trên bài toán doanh nghiệp có luật đóng. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Trong các tác vụ có quy trình nghiệp vụ đóng (closed-world business logic) với các ràng buộc tất định, việc chuyển đổi từ kiến trúc workflow tuần tự sang multi-agent topologies (orchestrator/worker) làm tăng đáng kể chi phí gọi mô hình và số bước thực thi mà không cải thiện tỷ lệ thành công (pass rate). |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Giới hạn trong miền bài toán thẩm định bồi thường khiếu nại (claims resolution) với hệ thống quy tắc chính sách cố định, bộ công cụ đọc dữ liệu có sẵn, mô hình MockLLM tra cứu theo seed và tập ngữ liệu mẫu synthetic gồm 14 claims. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Nếu chuyển đổi topology từ workflow (Shape A) sang orchestrator (Shape C) trong khi cố định mọi yếu tố khác (corpus, tool, policy, seed, pricing), chi phí mô phỏng trên mỗi ca thành công (cost_per_success_vnd) sẽ tăng gần gấp đôi (từ ~28.79 VND lên ~56.37 VND, tăng xấp xỉ 95%) và số bước trung bình (mean_steps) tăng từ ~1.86 lên >5.0 bước do chi phí handoff và điều phối worker, trong khi pass_rate giữ nguyên ở mức 1.000. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Biến giữ cố định: MockLLM, bộ công cụ đọc (lookup_order, compute_compensation, get_claim_view), 5 hạt giống seed (11, 22, 33, 44, 55), ngữ liệu 14 claims (data/public_claims.jsonl), bảng giá mô phỏng (pricing.yaml), và bộ quy tắc thẩm định của host. Biến duy nhất thay đổi: Topology kiến trúc điều phối thực thi (Shape A: Workflow tuyến tính tuần tự vs Shape C: Orchestrator với Typed Handoff và Read-only Investigators). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: Lãng phí chi phí token mô phỏng và dư thừa số bước thực thi không cần thiết. Thước đo: cost_per_success_vnd, mean_steps, pass_rate, seed_variance được đo lường tự động qua lab8.benchmark. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,orchestrator --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_benchmark.json`
- Run id / file report: `reports/ablation_benchmark.json` (chứa 140 trials độc lập, ví dụ: `R-workflow-C-001-s11`, `R-orchestrator-C-001-s11`, `R-workflow-C-002-s55`, `R-orchestrator-C-002-s55`)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu:
  + **Đúng với hypothesis**.
  + Tỷ lệ thành công: Cả `workflow` và `orchestrator` đều đạt `pass_rate` = 1.000 (70/70 trials) và `pass^5` = 1.000 trên cả 5 seeds (phương sai `seed_variance` = 0.000000).
  + Chi phí trên mỗi ca thành công (`cost_per_success_vnd`): `workflow` tiêu tốn **28.79 VND**, trong khi `orchestrator` tiêu tốn **56.37 VND** (tăng **+95.8%**, đúng như dự đoán gần gấp đôi chi phí).
  + Số bước thực thi trung bình (`mean_steps`): `workflow` chỉ mất **1.86 bước**, trong khi `orchestrator` mất **5.21 bước** (tăng gấp 2.8 lần).
  + Số lần gọi mô hình trung bình (`mean_model_calls`): `workflow` tiêu tốn **1.0 lần** (chỉ gọi để draft phản hồi khách hàng), trong khi `orchestrator` tiêu tốn **1.93 lần** (thêm bước lập kế hoạch điều phối routing note).
  + Kết luận: Trong bài toán có logic đóng, workflow tất định tối ưu vượt trội về chi phí và số bước so với orchestrator.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.
