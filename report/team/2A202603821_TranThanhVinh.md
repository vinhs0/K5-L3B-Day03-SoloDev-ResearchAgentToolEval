# Báo cáo cá nhân — Trần Thành Vinh - 2A202603821

## 1. Thông tin thành viên

- Họ tên: Trần Thành Vinh
- MSSV: 2A202603821
- Email: vinhthanhtran03102004@gmail.com

## 2. Phần việc phụ trách

Nhóm chỉ có một thành viên (SoloDev) nên tôi thực hiện toàn bộ bài lab:

- Setup môi trường, provider OpenRouter, chạy pytest và preflight.
- Baseline v0 và phân tích lỗi (`starter_v0/runs/v0_*.json`).
- Tối ưu system prompt và khai báo tool qua các version v1 đến v6 (`starter_v0/artifacts/`).
- Viết 3 tool mới: `wikipedia`, `hackernews`, `current_time` (`starter_v0/tools/`).
- Unit test cho tool (`starter_v0/tests/test_tools_todo.py`).
- 10 case eval của nhóm: 5 single turn + 5 multi turn (`starter_v0/data/eval_group.json`).
- Giao diện Streamlit (`starter_v0/app.py`) và chia sẻ qua Cloudflare Tunnel (link ghi trong `report/team/group_report.md`).
- Chat live bằng `chat.py`, lưu transcript (`starter_v0/transcripts/`).
- Báo cáo cá nhân này và phần báo cáo nhóm.

## 3. Đóng góp cụ thể

- Baseline v0 (commit `Step 1` / `CP1`): chạy bộ base eval 20 case với `openai/gpt-4o-mini`, đạt 0.70. Lỗi gồm `out_of_scope` (2), `missing_info` (2), `wrong_boundary` (1), `wrong_tool` (1).
- Vòng lặp v1 đến v3 (commit `CP1, CP2`), mỗi version một giả thuyết, ghi trong `version_log.csv`:
  - v1 sửa system prompt (bỏ chỉ dẫn đoán/gửi ngay/một bước, thêm rule routing, clarify, xác nhận trước khi gửi): 0.70 → 0.85.
  - v2 viết lại description trong `tools.yaml` với "DÙNG KHI / KHÔNG DÙNG": 0.85 → 0.95.
  - v3 làm rõ convention tham số (handle không có `@`, topic/timeframe/search_type, `response_type=yes_no` cho yêu cầu gửi): 0.95 → 1.00.
- v4 đến v6 (commit `Cp3 cp4`, `chat.py`): tiếp tục chỉnh prompt/tools.yaml, chạy lại cả base và group. v4 group lần đầu 9/11 pass, sau khi sửa đạt 10/10; v5 và v6 đạt 20/20 base và 10/10 group.
- Tool mới (commit `Cp3 cp4`): `wikipedia`, `hackernews`, `current_time`. Mỗi tool có `tool.py` + `TOOL.md`, đăng ký trong `tools/__init__.py` (`TOOL_FUNCTIONS`) và `tools.yaml`.
- Unit test: `test_tools_todo.py` có test cho `clarify`, `format`, `send`, `lookup`, `fetch`, `timeline`, `social_search`, `policy` và mỗi tool mới đều có từ 3 test trở lên: wikipedia 6, hackernews 4, current_time 3 (happy path, input xấu, lỗi HTTP/timezone). Toàn suite: 107 passed, 0 failed, 0 skipped. Test dùng `fake_http`, không gọi mạng thật.
- Eval nhóm: `eval_group.json` có 10 case, trong đó có case route tới tool mới.
- UI Streamlit (commit `Step 5`): `app.py` + dependency trong `requirements.txt`, có 2 transcript chạy qua UI (`v6_openrouter_ui_*`).
- Chat live (commit `chat.py`): 5 transcript từ v3 đến v6.

## 4. Bằng chứng

- Commit (git log):
  - `00566bb` Redo
  - `8d40439` CP1, CP2
  - `5f18e69` Cp3 cp4
  - `b18d9b6` chat.py
  - `685dc15` Step 5
  - (trước đó: `02f3e08` CP1, `91356d4` Step 1)
- Run JSON: `starter_v0/runs/v0_B_base_...json`, `v1_...`, `v2_...`, `v3_...` (base và group), `v4_...`, `v5_...`, `v6_...`.
- Nhật ký version: `starter_v0/artifacts/version_log.csv`; artifact: `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`.
- Tool mới: `starter_v0/tools/wikipedia/`, `starter_v0/tools/hackernews/`, `starter_v0/tools/current_time/`.
- Test: `starter_v0/tests/test_tools_todo.py`; eval nhóm: `starter_v0/data/eval_group.json`.
- UI: `starter_v0/app.py`; chat: `starter_v0/chat.py`; transcript: `starter_v0/transcripts/*.transcript.json`.
- Báo cáo nhóm: `report/team/group_report.md`.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: Claude Code, dùng để sửa prompt/tools và chạy eval; kết quả được kiểm tra bằng cách xem các lệnh Claude chạy, đọc file run JSON (summary, failure_counts) và chạy lại lệnh bằng tay để xem output.

## 5. Tự đánh giá

- Làm tốt: quy trình dựa trên bằng chứng. Mỗi version một giả thuyết, đo trước/sau, điểm base tăng từ 0.70 (v0) lên 1.00 (v3). Các run đều hợp lệ (`provider_error_cases = 0`, `measured_cases = total_cases`). Tool mới có test không gọi mạng thật, trả error dict thay vì raise.
- Khó: phân biệt lỗi do prompt, do mô tả tool, hay do case eval viết chưa chặt (ví dụ run v4 group đầu tiên có 11 case và 2 lỗi `wrong_arg_value`, phải xem lại case và expect). Ngoài ra bộ base 20 case đã đạt 1.00 từ v3 nên v4 đến v6 khó chứng minh cải thiện thêm; điểm tuyệt đối có thể che overfitting vào bộ eval.
- Bài học: nên sửa một thứ mỗi lần, đọc từng case FAIL trong run JSON trước khi sửa, và mô tả tool kiểu "dùng khi / không dùng" cùng convention tham số mang lại hiệu quả lớn hơn việc viết prompt dài. Số liệu chỉ đáng tin khi run hợp lệ và có thể truy lại về file.
- Cần cải thiện, theo checklist trong `README.md` còn chưa tick:
  - `version_log.csv` mới có v0 đến v3; v4 đến v6 đã có run nhưng chưa được ghi dòng log với hash, giả thuyết, metric.
  - UI có code và transcript nhưng mục "UI chạy được + link dùng thử" chưa tick; link tunnel trong `group_report.md` có thể đã hết hạn.
  - Chưa tick: `chat.py` ≥ 3 lượt live, `group_report.md` Phần A/B, báo cáo cá nhân (file này), và `TEAM.md` vẫn ghi "commit chốt: chưa có".
  - Bonus đã làm: `send` gửi thật lên Telegram sau xác nhận (transcript `v3_openrouter_20261111T095317099669`, `status: sent`), và test challenge `pytest` 107 passed, 0 failed, 0 skipped. Bonus chưa làm: Small Local Model Challenge, hơn 3 tool mới (hiện chỉ 3 tool).
  - Nên thêm test tool mới tốt hơn và chạy lại trên nhiều model để kiểm tra khái quát hóa.
