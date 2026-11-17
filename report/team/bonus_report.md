# Bonus report: B3

- Topic + nguồn (tên, năm, slide): **B3 · Verifier/aggregator chống khuếch đại lỗi** — Google Research 2026, *Towards a Science of Scaling Agent Systems* (error amplification, Evaluator–optimizer, Reflection; slide 17, 22, 42).
- CLAIM của nguồn (1 câu): Các agent độc lập có thể khuếch đại lỗi tới 17,2×, trong khi có cơ chế kiểm chứng/điều phối tập trung (evaluator–optimizer / verifier) giúp kéo mức khuếch đại lỗi xuống còn 4,4×.
- BOUNDARY (model / dataset / setup): Kết luận của nguồn đo trên bài toán multi-agent LLM thực tế; trên LogiX-VN bị giới hạn bởi `MockLLM` seeded (`seed % 5 == 0` mô phỏng lỗi đọc nhầm `delay_days` từ ticket), 14 claim public và 8 claim đối kháng tự viết (viết nhãn tay theo `docs/business_rules.md`), giá mô phỏng (`config/pricing.yaml`), latency `unavailable`.
- HYPOTHESIS trên LogiX: Thêm một **code verifier** (`swarm_verified`) đối chiếu `(delay_days, status, damage_verified)` với dữ liệu order có cấu trúc và sửa tối đa 1 vòng trước khi ghi sẽ loại bỏ lỗi khuếch đại ở seed 55 của `swarm` (đưa `pass_rate` và `pass^5` về `1.000`, `variance = 0.0`) với mức chi phí nhỉnh hơn nhẹ do tối đa 1 lần gọi `compute_compensation` bổ sung khi can thiệp.
- Biến cố định / biến thay đổi: Cố định `MockLLM`, 5 seed `11,22,33,44,55`, `as_of=2026-11-15`, bảng giá `pricing.yaml`, mỗi trial 1 SQLite mới, cùng hàm `trial_pass`. Biến thay đổi duy nhất: topology (`workflow` vs `swarm` vs `swarm_verified` có code verifier).
- Lệnh tái lập (copy-paste được):
  - Public: `python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/bonus_benchmark.json`
  - Adversarial: `python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --cases bonus/cases.jsonl --world bonus/world.json --seeds 11,22,33,44,55 --out reports/bonus_adversarial.json`
  - Tests: `python -m pytest -q tests/test_bonus_swarm_verified.py`
- File report + run id: `src/reports/bonus_benchmark.json`, `src/reports/bonus_adversarial.json`; run id minh họa `R-swarm_verified-C-002-s55`, `R-swarm_verified-B-001-s55`, `R-swarm_verified-B-002-s55`.

## Kết quả

### 1. Bộ public (`src/reports/bonus_benchmark.json` — 14 claim × 5 seed = 70 trial/shape)

| Shape | Pass rate | Pass^5 | Seed variance | Min–Max | Cost/success (VND) | Mean steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `workflow` | 1.000 | 1.000 | 0.000000 | 1.000–1.000 | 28.79 | 1.86 |
| `swarm` | 0.986 | 0.929 | 0.000816 | 0.929–1.000 | 49.57 | 2.80 |
| `swarm_verified` | **1.000** | **1.000** | **0.000000** | 1.000–1.000 | **49.00** | 2.81 |

### 2. Bộ đối kháng tự viết (`src/reports/bonus_adversarial.json` — 8 claim × 5 seed = 40 trial/shape)

| Shape | Pass rate | Pass^5 | Seed variance | Min–Max | Cost/success (VND) | Mean steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `workflow` | 1.000 | 1.000 | 0.000000 | 1.000–1.000 | 30.91 | 2.00 |
| `swarm` | 0.900 | 0.500 | 0.040000 | 0.500–1.000 | 59.78 | 3.15 |
| `swarm_verified` | **1.000** | **1.000** | **0.000000** | 1.000–1.000 | **55.30** | 3.30 |

- **Số lần verifier can thiệp (`verifier_override`):** **1 lần** trên public (`R-swarm_verified-C-002-s55`) và **6 lần** ở seed 55 trên bộ đối kháng (`B-001`, `B-002`, `B-004`, `B-006`, `B-007`, `B-008`), chặn 1 lỗi trên public (`C-002@55`) và 4 lỗi sai quyết định của `swarm` trên bộ đối kháng (`B-001`, `B-004`, `B-006` trả nhầm thành `resolved`; `B-002` từ chối nhầm thành `denied`).
- **Safety counts:** `0` secret leak và `0` approval bypass trên toàn bộ 70 + 40 trial của `swarm_verified`.
- **Trace minh họa (`R-swarm_verified-C-002-s55`):** `handoff` → `investigator (O-202, delay_days=2)` → `model_override (delay_days=5)` → `verifier_override (round=1, delay_days: 5 -> 2, repaired_amount_vnd=0)` → `quote (amount_vnd=0, no_entitlement)` → `denied`.

## Kết luận

- **Ủng hộ hypothesis:** Code verifier đưa chất lượng của `swarm_verified` về **ngang bằng hoàn toàn `workflow`** về độ chính xác (`pass_rate = 1.000`, `pass^5 = 1.000`, `variance = 0.000000`). Thậm chí `cost/success` của `swarm_verified` (`49.00` VND public / `55.30` VND đối kháng) còn thấp hơn `swarm` gốc (`49.57` / `59.78` VND) vì không còn các trial fail làm đội mẫu số chi phí trên mỗi ca thành công.
- **Trả lời câu hỏi B3 — Verifier đưa swarm về gần workflow tới đâu và giá trị còn lại của swarm là gì?**
  - Về độ chính xác và phương sai, verifier đưa `swarm` lên đúng `1.000` của `workflow`, nhưng tổng chi phí mô phỏng vẫn đắt hơn `workflow` ~**1.70×–1.79×** (`49.00` vs `28.79` VND ở public; `55.30` vs `30.91` VND ở đối kháng) và số bước nhiều hơn (`2.81` vs `1.86` bước) do vẫn phải trả tiền cho các cuộc gọi `peer`/`parse` của `swarm`.
  - Khi verifier bằng code đã đối chiếu toàn bộ dữ kiện tính tiền (`delay_days`, `status`, `damage_verified`) và tự gọi lại `compute_compensation` từ DB, phần quyết định tiền của `swarm` thực chất không còn vai trò độc lập; giá trị duy nhất mà `swarm` giữ lại lúc đó chỉ nằm ở phần đọc ngôn ngữ tự nhiên không có cấu trúc (soạn câu trả lời hoặc gợi ý thông tin khi chưa có trường cấu trúc) — và với task tuần tự/có cấu trúc như LogiX-VN thì `workflow` vẫn tối ưu hơn về chi phí.
- **Điều kiện đảo ngược kết luận:** Kết luận ủng hộ `workflow` sẽ đảo ngược nếu xuất hiện các trường dữ liệu thật sự phi cấu trúc đòi hỏi suy luận ngôn ngữ trước khi tra DB, hoặc nếu `verifier` kiểm lỗi bằng chính LLM thay vì code tất định (lúc đó verifier có thể bỏ sót hoặc tự khuếch đại lỗi).

## Giới hạn

- `MockLLM` không phải model thật, chỉ mô phỏng sai số đọc ticket tại `seed % 5 == 0`.
- `latency` là `unavailable` (không đo được độ trễ thực của vòng sửa +1 bước).
- Bộ public (14 claim) và bộ đối kháng tự viết (8 claim) còn nhỏ; các claim viết tay chỉ kiểm chứng cơ chế lỗi `delay_days`/từ khóa có cấu trúc đã biết.
