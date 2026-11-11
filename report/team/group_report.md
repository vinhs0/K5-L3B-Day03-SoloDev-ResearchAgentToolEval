# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: SoloDev (nhóm 1 người)
- Thành viên và phân công: Trần Thành Vinh (2A202603821) thực hiện toàn bộ bài làm; xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: OpenRouter, model `openai/gpt-4o-mini` (xác nhận từ trường `provider`/`model` trong `starter_v0/runs/v0_*.json` … `v3_*.json`; v4–v6 cũng dùng cùng model).

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent tiếng Việt: tìm tin tức/web, bài đăng Twitter/X (theo từ khóa hoặc theo tài khoản), bài Hacker News, bài Wikipedia và paper arXiv, đọc URL do người dùng đưa, tổng hợp thành bản tin, và chỉ gửi lên Telegram sau khi người dùng xác nhận. Agent hỏi lại (`clarify`) khi thiếu thông tin và từ chối/trả lời thẳng khi yêu cầu ngoài phạm vi.

**Cách chạy UI:**

```bash
cd starter_v0
pip install -r requirements.txt
streamlit run app.py
```

Dependency `streamlit>=1.30.0` đã được thêm vào `starter_v0/requirements.txt`. UI chạy ở cổng 8501 (`http://localhost:8501`).

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: https://alfred-multimedia-ebooks-beijing.trycloudflare.com
>
> (Cloudflare quick tunnel -> `streamlit run app.py` trên máy local, cổng 8501. Link chỉ sống khi máy chạy UI và `cloudflared tunnel --protocol http2 --url http://localhost:8501` còn mở.)

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng (text / yes_no / choice) khi thiếu thông tin hoặc cần xác nhận trước khi gửi | không |
| timeline | Lấy bài đăng gần đây của MỘT tài khoản X/Twitter đã được nêu tên | không |
| social_search | Tìm bài đăng Twitter/X theo từ khóa/chủ đề (Latest/Top) | không |
| lookup | Tìm kiếm web: tin tức, bài báo, thông tin chung (topic news/general, timeframe) | không |
| fetch | Đọc nội dung đầy đủ của một URL do người dùng cung cấp | không |
| format | Trình bày các item đã thu thập thành bản tin theo khuôn (brief, sections, bullets, thread, daily_ai_vn) | không |
| send | Gửi văn bản ra ngoài (Telegram), chỉ sau khi người dùng xác nhận (`confirmed=true`) | không |
| policy | Tra cứu chính sách/quy định nội bộ (trích dẫn, quyền riêng tư, đăng bài ra ngoài, cách dùng tool) | không |
| papers | Tìm paper khoa học trên arXiv theo từ khóa | không |
| paper_text | Lấy text của MỘT paper arXiv đã biết ID/URL | không |
| wikipedia | Lấy bản tóm tắt một bài Wikipedia (hỗ trợ en, vi, fr, de, es, ja, zh) | có |
| hackernews | Tìm bài (story) trên Hacker News theo từ khóa, sắp xếp relevance/date | có |
| current_time | Cho biết ngày/giờ/thứ hiện tại theo múi giờ IANA (mặc định Asia/Ho_Chi_Minh) | có |

### A3. Câu hỏi mẫu để thử

1. "Wikipedia nói gì về Alan Turing? Cho tôi bản tiếng Việt." (wikipedia, lang=vi)
2. "Tìm 5 bài mới nhất trên Hacker News về Rust." (hackernews, sort=date)
3. "Bây giờ là mấy giờ ở Tokyo, hôm nay thứ mấy?" (current_time, timezone=Asia/Tokyo)
4. "3 tweet mới nhất của Sam Altman" (timeline, screenname=sama); sau đó thử "Tweet mới nhất của tôi" để thấy agent gọi `clarify`.
5. "Gửi bản tin này lên Telegram" (agent phải gọi `clarify` yes_no xác nhận trước, không gửi ngay).

## 3. Giải pháp

**Thay đổi trong `starter_v0/artifacts/system_prompt.md`** (v0 starter cố ý sai: "đừng hỏi, cứ đoán", "gửi luôn", "một bước, một tool"):

- Bỏ chỉ dẫn đoán tài khoản/URL; thêm mục "Missing information": thiếu handle/URL/chủ đề thì gọi `clarify` (text), không bịa và không dùng lại tên người ở câu hỏi trước làm tài khoản.
- Thêm mục "Routing" rõ ràng: timeline (chỉ khi user nêu tên tài khoản ở lượt hiện tại, kèm map tên -> handle), social_search, lookup, fetch, clarify; giữ limit/timeframe từ lượt trước nếu user không đổi.
- Thêm mục "Sending": mọi yêu cầu gửi/đăng đều phải `clarify` yes_no trước; chỉ gọi `send` với `confirmed=true` sau khi user đồng ý.
- Thêm mục "Other": được gọi nhiều tool trong một lượt; yêu cầu ngoài phạm vi (code, toán, nấu ăn) hoặc không cần tool thì trả lời thẳng, không gọi tool.

**Thay đổi trong `starter_v0/artifacts/tools.yaml`:**

- Viết lại mô tả mọi tool theo dạng "làm gì / DÙNG KHI / KHÔNG DÙNG khi" bằng tiếng Việt, để phân biệt các tool gần nhau (timeline vs social_search vs lookup; papers vs paper_text; fetch vs lookup).
- Ghi rõ quy ước tham số: handle không có @ và viết thường; `lookup` dùng `topic=news` và bỏ chữ "news/mới nhất/hôm nay" khỏi query, timeframe theo ngày/tuần/tháng/năm; `social_search` dùng `Top` khi user nói phổ biến/nổi bật, `Latest` còn lại; limit theo đúng số user nêu.
- Làm rõ ranh giới `send`: chỉ `confirmed=true` khi user đã xác nhận, và `clarify` yes_no dùng cho mọi yêu cầu gửi.
- Khai báo thêm 3 tool nhóm ở mục "Team tools" cuối file (13 tool tổng cộng).

**Tool mới (mỗi tool có `starter_v0/tools/<tên>/TOOL.md`):**

| Tool | Làm gì | Khi nào agent nên gọi |
|---|---|---|
| `wikipedia` | Lấy tóm tắt một bài Wikipedia theo tiêu đề, chọn ngôn ngữ (`lang`) | Khi hỏi định nghĩa/khái niệm/tiểu sử nền tảng ("X là gì", "who is Y"). Không dùng cho tin mới (lookup) hoặc URL user đưa (fetch) |
| `hackernews` | Tìm story trên Hacker News theo từ khóa, `sort` relevance/date, `limit` 1–20 | Chỉ khi user nhắc rõ Hacker News/HN. Không dùng cho tin chung (lookup) hoặc tweet (social_search) |
| `current_time` | Trả về ngày, giờ, thứ hiện tại theo múi giờ IANA; múi giờ sai trả về dict lỗi thay vì raise | Chỉ khi user hỏi bây giờ mấy giờ/hôm nay ngày nào/thứ mấy. Không dùng để tìm tin "hôm nay" (lookup, timeframe=day) |

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`. Tất cả run dùng model `openai/gpt-4o-mini` (OpenRouter), bộ eval `day03_v2_research_base` (20 case). Metric là `case_accuracy`; cả 4 run dưới đây có `provider_error_cases = 0`, `measured_cases = total_cases = 20`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi chưa tối ưu trước khi sửa (prompt v0 bảo "đoán, đừng hỏi, gửi ngay") | — (không có) | 0.70 (14/20) | `starter_v0/runs/v0_B_base_openrouter_20261110T215302319097.json` |
| v1 | `system_prompt.md` | Bỏ chỉ dẫn xấu, thêm rule routing + `clarify` + xác nhận trước khi gửi sẽ sửa lỗi hỏi lại và routing | 0.70 | 0.85 (17/20) | `starter_v0/runs/v1_B_base_openrouter_20261110T230309847563.json` |
| v2 | `tools.yaml` (description của tool) | Description tool quá mơ hồ; thêm "DÙNG KHI / KHÔNG DÙNG" cho mỗi tool sẽ sửa routing và multi-turn | 0.85 | 0.95 (19/20) | `starter_v0/runs/v2_B_base_openrouter_20261110T230434205765.json` |
| v3 | `tools.yaml` (parameter descriptions) | Còn R12 (gửi bản tin chưa chọn `clarify yes_no`); nêu rõ convention args (handle không có @, topic/timeframe/search_type) và `response_type=yes_no` cho mọi yêu cầu gửi | 0.95 | 1.00 (20/20) | `starter_v0/runs/v3_B_base_openrouter_20261110T230627333223.json` |

Chi tiết các metric phụ (từ `summary` của từng run JSON):

| Version | passed/total | tool_routing | argument | multiturn | failure_counts |
|---|---:|---:|---:|---:|---|
| v0 | 14/20 | 0.75 | 0.70 | 1.00 | out_of_scope 2, missing_info 2, wrong_boundary 1, wrong_tool 1 |
| v1 | 17/20 | 0.95 | 0.85 | 0.8333 | missing_info 1, wrong_boundary 1, wrong_arg_value 1 |
| v2 | 19/20 | 1.00 | 0.95 | 1.00 | wrong_boundary 1 |
| v3 | 20/20 | 1.00 | 1.00 | 1.00 | không có |

Lưu ý: `version_log.csv` chỉ ghi v0–v3. Các run v4–v6 có trong `starter_v0/runs/` nhưng chưa có dòng trong CSV nên không đưa vào bảng chính (xem bảng bổ sung bên dưới, số liệu lấy trực tiếp từ run JSON).

Bổ sung — run v3–v6 trên bộ `group` (suite `day03_v2_research_group`) và `base` sau v3 (chưa có trong `version_log.csv`; đều `provider_error_cases = 0`, `measured_cases = total_cases`):

| Version | Suite | passed/total | case_accuracy | Run File |
|---|---|---:|---:|---|
| v3 (tools hash `dc422bbc7e89`) | group | 9/10 | 0.90 | `starter_v0/runs/v3_B_group_openrouter_20261111T094159646938.json` |
| v4 (prompt hash `d9a6cd2ad96c`) | group | 9/11 | 0.8182 | `starter_v0/runs/v4_B_group_openrouter_20261111T003821947742.json` |
| v4 (prompt hash `45ad071f97a8`) | group | 10/10 | 1.00 | `starter_v0/runs/v4_B_group_openrouter_20261111T094239522986.json` |
| v4 | base | 20/20 | 1.00 | `starter_v0/runs/v4_B_base_openrouter_20261111T094337180628.json` |
| v5 | base / group | 20/20 và 10/10 | 1.00 / 1.00 | `starter_v0/runs/v5_B_base_openrouter_20261111T094935275426.json`, `starter_v0/runs/v5_B_group_openrouter_20261111T095000925383.json` |
| v6 | base / group | 20/20 và 10/10 | 1.00 / 1.00 | `starter_v0/runs/v6_B_base_openrouter_20261111T095130488153.json`, `starter_v0/runs/v6_B_group_openrouter_20261111T095157789370.json` |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON. Đã đối chiếu từng dòng với `starter_v0/runs/v0_B_base_openrouter_20261110T215302319097.json`: v0 có đúng 6 case fail (R08, R10, R11, R12, R13, R14), khớp với 14/20 pass. Chỉ R13 cần chỉnh lại cho đúng args thật (thêm `max_results=5`; `social_search` có thêm `search_type="Latest"`, `limit=5`); các dòng còn lại khớp với log.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `lookup(query="nguyên hàm của x^2", topic="general")` | Câu hỏi toán ngoài phạm vi nhưng model vẫn gọi tool; mong đợi không gọi tool (`failures`: "expected no tool call") | Thêm rule trong system prompt: yêu cầu ngoài phạm vi nghiên cứu (toán, code) thì trả lời/từ chối trực tiếp, không gọi tool |
| R10_missing_handle | missing_info | `timeline(screenname="sama", limit=5)` | User không nói rõ tài khoản, model tự đoán "sama" thay vì gọi `clarify` (`failures`: "missing tool call clarify", "extra tool call timeline"); do prompt v0 bảo "đoán, đừng hỏi" | Bỏ chỉ dẫn đoán; thêm rule: thiếu handle thì gọi `clarify` (response_type=text) |
| R11_missing_url | missing_info | `fetch(url="https://www.example.com/article")` | User chỉ nói "bài viết này", model bịa URL thay vì gọi `clarify` (`failures`: "missing tool call clarify", "extra tool call fetch") | Bỏ chỉ dẫn "assume a likely URL"; thêm rule: thiếu URL thì gọi `clarify`; mô tả `fetch` yêu cầu URL do user cung cấp |
| R12_confirm_before_send | wrong_boundary | `send(text="Bản tin này")` | Gửi Telegram ngay mà chưa hỏi xác nhận; mong đợi `clarify` (yes_no) trước (`failures`: "missing tool call clarify", "extra tool call send"). Tool trả về `status: needs_confirmation` | Rule: `send` chỉ gọi sau khi user xác nhận, với `confirmed=true`; mô tả `send` trong `tools.yaml` nêu rõ điều này. Về sau còn phải ép `response_type=yes_no` (xem hàng R12 ở v1/v2 bên dưới) |
| R13_parallel_web_and_tweets | wrong_tool (observed: `wrong_arg_value`) | `lookup(query="AI news", timeframe="day", max_results=5)` + `social_search(query="AI", search_type="Latest", limit=5)` | Routing đúng (gọi đủ 2 tool) nhưng sai args của `lookup`: query "AI news" thay vì "AI", thiếu `topic="news"` (`failures`: "query: expected 'AI', got 'AI news'", "topic: expected 'news', got None") | Mô tả convention args trong `tools.yaml`: tin tức dùng `topic=news`, không đưa chữ "news" vào query |
| R14_out_of_scope_coding | out_of_scope | `send(text="def fibonacci(n): ...")` (nội dung là cả đoạn code Python đệ quy) | Yêu cầu viết code ngoài phạm vi nhưng model gọi `send` để gửi đoạn code lên Telegram; mong đợi không gọi tool | Rule phạm vi như R08; không bao giờ gọi `send` nếu user chưa yêu cầu gửi |

Các lỗi còn lại đáng chú ý ở phiên bản sau (cũng từ `results[*].result.failures`):

| Case ID (run) | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R10_missing_handle (v1) | missing_info / `wrong_arg_value` | `clarify(question="Bạn muốn tóm tắt tweet của tài khoản nào?")` | Routing đã đúng (hết đoán "sama") nhưng thiếu `response_type="text"` (expected 'text', got None) | Nêu rõ `response_type` trong mô tả tham số của `clarify` (`tools.yaml`) |
| R12_confirm_before_send (v1, v2) | wrong_boundary / `wrong_arg_value` | `clarify(question="Bạn có thể cung cấp nội dung bản tin ... không?", response_type="text")` | Đã gọi `clarify` nhưng dùng `text` thay vì `yes_no` (expected 'yes_no', got 'text'): model hiểu là đang xin nội dung chứ không phải xin xác nhận gửi | v3: mô tả tham số trong `tools.yaml` nêu `response_type=yes_no` cho mọi yêu cầu gửi. Hết lỗi ở v3 base |
| M02_carryover_timeframe (v1) | wrong_arg_value (multi-turn) | `social_search(query="robotics", search_type="Latest", limit=5)` | Sau khi bỏ chỉ dẫn "một bước", model chọn nhầm `social_search` thay vì `lookup(query="robotics", topic="news", timeframe="day")` ở lượt 3 ("Chỉ tìm robotics thôi, vẫn là tin hôm nay") | v2: thêm "DÙNG KHI / KHÔNG DÙNG" cho `lookup`/`social_search` trong `tools.yaml`; multiturn về 1.00 |
| S04_confirm_before_send (v3, suite group) | wrong_boundary | `clarify(question="Bạn muốn gửi tóm tắt về chủ đề gì?", response_type="text")` | Lỗi R12 tái xuất ở case mới của nhóm: nội dung gửi mơ hồ nên model hỏi `text` thay vì `yes_no` | system prompt: "áp dụng cho MỌI yêu cầu gửi, kể cả nội dung mơ hồ; không dùng response_type=text cho yêu cầu gửi" |
| G06_missing_info_vague_search (v4 group, run 003821) | missing_info / `wrong_arg_value` | `clarify(question="Bạn muốn tìm tin tức về chủ đề gì?")` | Thiếu `response_type="text"` (expected 'text', got None) | Run sau (094239, prompt hash `45ad071f97a8`) đạt 10/10 |
| G07_confirm_before_send_email (v4 group, run 003821) | wrong_boundary | `clarify(question="Bạn có thể cho biết nội dung cụ thể ... Telegram không?", response_type="text")` | Cùng kiểu lỗi R12/S04: dùng `text` thay vì `yes_no` | Bổ sung câu trong system prompt (xem B6) |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

Dataset có 10 case: 5 single turn (S01–S05) + 5 multi turn (M01–M05). Kết quả lấy từ run mới nhất của suite group: `starter_v0/runs/v6_B_group_openrouter_20261111T095157789370.json` (version v6, model `openai/gpt-4o-mini`): 10/10 passed (case_accuracy = tool_routing = argument = multiturn = 1.0).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| S01_route_wikipedia | Câu hỏi tiểu sử/định nghĩa nền tảng -> `wikipedia` (tool mới), không phải `lookup` | Gọi `wikipedia` | PASS (run v6 20261111T095157) |
| S02_route_hackernews_args | Nhắc rõ Hacker News -> `hackernews` (tool mới) với sort=date ("mới nhất") và limit=3 | `hackernews(sort="date", limit=3)` | PASS (run v6 20261111T095157) |
| S03_route_current_time_tz | Hỏi giờ hiện tại -> `current_time` (tool mới) với timezone IANA Asia/Tokyo | `current_time(timezone="Asia/Tokyo")` | PASS (run v6 20261111T095157) |
| S04_confirm_before_send | Yêu cầu gửi ra ngoài -> `clarify` yes_no xin xác nhận, KHÔNG gọi `send` trực tiếp | `clarify(response_type="yes_no")` | PASS (run v6 20261111T095157); từng FAIL ở run `v3_B_group_openrouter_20261111T094159646938` (9/10) |
| S05_out_of_scope_recipe | Câu nấu ăn ngoài phạm vi research/news -> KHÔNG gọi tool | Không gọi tool, từ chối lịch sự | PASS (run v6 20261111T095157) |
| M01_switch_web_to_social_top | Chuyển từ web sang Twitter: `social_search`, search_type=Top ("nổi bật"), limit=3 | `social_search(query="Anthropic", search_type="Top", limit=3)` | PASS (run v6 20261111T095157) |
| M02_hackernews_correction | 3 turns với `hackernews` (tool mới): sửa chủ đề Rust -> Go, sort=date và limit=3 từ lượt cuối | `hackernews(query="Go", sort="date", limit=3)` | PASS (run v6 20261111T095157) |
| M03_current_time_change_tz | Lượt sau đổi múi giờ: `current_time` (tool mới) với timezone America/New_York | `current_time(timezone="America/New_York")` | PASS (run v6 20261111T095157) |
| M04_wikipedia_switch_language | Lượt sau yêu cầu tiếng Việt: `wikipedia` (tool mới) với lang=vi | `wikipedia(lang="vi")` | PASS (run v6 20261111T095157) |
| M05_clarify_topic_then_news_month | 3 turns: thiếu chủ đề ban đầu, điền robotics ở lượt 2, timeframe=month ở lượt 3, topic=news | `lookup(query="robotics", topic="news", timeframe="month")` | PASS (run v6 20261111T095157) |

Ghi chú: run `v5_B_group_openrouter_20261111T095000925383.json` cũng 10/10; run `v4_B_group_openrouter_20261111T003821947742.json` (9/11, fail G06_missing_info_vague_search và G07_confirm_before_send_email) dùng bộ case cũ 11 case, đã được thay bằng bộ 10 case hiện tại.

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| Nghiên cứu thường (UI, turn 1) | "Tin tức AI hôm nay có gì nổi bật?" | `lookup(query="AI", topic="news", timeframe="day", max_results=5)` | v6 (`v6+p6bb896774331+tdc422bbc7e89`), `transcripts/v6_openrouter_ui_20261111T100603940683.transcript.json` | status `answered`: agent trả danh sách tin AI từ kết quả `lookup` |
| Nghiên cứu thường (CLI, turn 1) | "Alan Turing là ai?" | `wikipedia(title="Alan_Turing", lang="vi")` | v6, `transcripts/v6_openrouter_20261111T095011357260.transcript.json` | status `answered`: tóm tắt tiểu sử từ Wikipedia tiếng Việt |
| Thiếu thông tin (turn 2) | "Tóm tắt 3 tweet mới nhất giúp mình" (không nêu tài khoản) | `clarify(question="Bạn muốn tóm tắt tweet của tài khoản nào?", response_type="text")` | v6, `transcripts/v6_openrouter_20261111T095011357260.transcript.json` | status `waiting_for_user`: agent hỏi lại, không bịa tài khoản |
| User bổ sung thông tin (turn 3) | "Của Andrej Karpathy nhé" | `timeline(screenname="karpathy", limit=3)` | v6, cùng transcript như trên | status `answered`: tóm tắt 3 tweet của karpathy |
| Yêu cầu gửi Telegram (turn 4) | "Đăng bản tin này lên Telegram giúp mình" | `clarify(question="Bạn có chắc chắn muốn đăng bản tin này lên Telegram không?", response_type="yes_no")`; không gọi `send` | v6, cùng transcript như trên | status `waiting_for_user`: agent xác nhận trước khi gửi (chưa gửi) |
| Gửi Telegram sau xác nhận (turn 4 -> 6) | Turn 4: yêu cầu đăng tin lên Telegram; turn 5: "Publish to the current Telegram channel you have information in"; turn 6: "Yes" | Turn 4 và 5: `clarify(response_type="yes_no")` (agent hỏi lại 2 lần, chưa gọi `send`); turn 6: `send(text="Jensen Huang was honey potted by a Chinese spy.", confirmed=true)` -> `{"tool": "send_telegram", "status": "sent"}` | Nhãn `v3` nhưng `prompt_hash` / `tools_hash` trùng với v6 (`v3+p6bb896774331+tdc422bbc7e89`), `transcripts/v3_openrouter_20261111T095317099669.transcript.json` | Agent confirm trước, chỉ gọi `send` với `confirmed=true` sau khi user trả lời "Yes"; kết quả `sent` |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) | `starter_v0/tools/wikipedia/`, `starter_v0/tools/hackernews/`, `starter_v0/tools/current_time/` (mỗi thư mục có `tool.py` + `TOOL.md`) | 3 tool mới ngoài bộ starter: `wikipedia` (tóm tắt trang Wikipedia, có tham số `lang`), `hackernews` (tìm bài Hacker News, sort/limit), `current_time` (giờ hiện tại theo timezone IANA). Có case eval group tương ứng (S01–S03, M02–M04), đều PASS ở run v6 | Input sai (sort/timezone/title/query rỗng) trả error dict thay vì ném exception; limit được kẹp; lỗi HTTP trả error dict (xem test) |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output: `107 passed in 0.28s` (chạy offline: `.venv/Scripts/python.exe -m pytest -q` trong `starter_v0/`; 0 failed, 0 skipped) | Số test trong `tests/test_tools_todo.py` (theo `--collect-only`): `wikipedia` 6, `hackernews` 4, `current_time` 3; thêm 5 contract test/tool trong `tests/test_tool_contract.py` | `current_time` có đúng 3 test riêng, sát ngưỡng tối thiểu |
| UI (lệnh chạy + link dùng thử) | `starter_v0/app.py`; transcript UI: `transcripts/v6_openrouter_ui_20261111T100531832412.transcript.json`, `transcripts/v6_openrouter_ui_20261111T100603940683.transcript.json` | Lệnh chạy: `streamlit run app.py` (trong `starter_v0/`, http://localhost:8501; `streamlit>=1.30.0` có trong `requirements.txt`). Link dùng thử: https://alfred-multimedia-ebooks-beijing.trycloudflare.com | Link Cloudflare quick tunnel chỉ sống khi máy chạy UI và tunnel còn mở |

Tool unit tests: nhóm có 107 test pass (offline, mock HTTP bằng fixture `fake_http`), 0 failed, 0 skipped. Cho 3 tool mới: `wikipedia` 6 test (map summary và kiểm tra request, 4 trường hợp input sai không gửi request, trang không tồn tại trả error dict), `hackernews` 4 test (map hits, sort sai/query rỗng không gửi request, kẹp limit và chấp nhận limit dạng string, lỗi HTTP trả error dict), `current_time` 3 test (UTC trả ISO date + weekday, mặc định múi giờ Việt Nam, timezone lạ trả error dict). Ví dụ lỗi unit test bắt được mà eval không bắt được: [CẦN NHÓM TỰ ĐIỀN — repo không có bằng chứng về một bug cụ thể nên không ghi bịa].

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 | Không làm | Không làm |
| Hơn 3 tool mới (≥ 4) | Không làm | Không làm (chỉ có 3 tool mới: `wikipedia`, `hackernews`, `current_time`) | Không làm |
| `send` gửi thật lên Telegram sau xác nhận | `transcripts/v3_openrouter_20261111T095317099669.transcript.json` (turn 4–6) | Agent gọi `clarify` yes_no trước, user trả lời "Yes", rồi `send(confirmed=true)` trả `{"tool": "send_telegram", "status": "sent"}` | Nội dung gửi là tin thử nghiệm do user nhập; nhãn version trong transcript là `v3` nhưng hash prompt/tools trùng v6. Agent hỏi xác nhận 2 lần trước khi gửi |
| Test challenge (0 skipped / regression test) | `pytest` output: `107 passed in 0.28s`, 0 skipped | 0 skipped: mọi test trong `tests/test_tools_todo.py` đã được viết thật (không còn `pytest.skip`) | Không có bằng chứng trong repo về bug tìm được ở tool có sẵn hay test regression riêng, nên chỉ nhận phần 0 skipped |

Test challenge: 0 skipped, 0 failed trên 107 test. Số bug tìm được trong tool có sẵn và test regression tương ứng: không có bằng chứng trong repo (nhóm tự bổ sung nếu có).

### B7. Small Local Model Challenge (bonus)

Nhóm không làm bonus này (không có run ollama nào trong `starter_v0/runs/`).

## 5. Khó khăn và cách xử lý

- **Regression giữa các phiên bản.** Khi sửa `system_prompt.md` ở v1, `case_accuracy` tăng 0.70 -> 0.85 và `tool_routing` 0.75 -> 0.95, nhưng `multiturn_accuracy` giảm từ 1.00 xuống 0.8333: case `M02_carryover_timeframe` đang pass ở v0 lại fail ở v1 (model gọi `social_search` thay vì `lookup`). Bằng chứng: `starter_v0/runs/v1_B_base_openrouter_20261110T230309847563.json`. Nhóm xử lý bằng cách sửa mô tả tool ở v2 (DÙNG KHI / KHÔNG DÙNG), multiturn về 1.00 trong `v2_B_base_...230434205765.json`. Bài học: chỉ nhìn `case_accuracy` tổng sẽ không thấy được metric thành phần tụt.
- **Lỗi "sửa một nửa" ở `clarify`.** Ở v1 và v2, R12 vẫn fail dù đã gọi đúng tool `clarify`, vì dùng `response_type="text"` thay vì `yes_no`; R10 ở v1 thiếu `response_type`. Routing đúng nhưng args sai nên phải sửa thêm ở mức mô tả tham số (v3), không phải ở prompt.
- **Eval cho kết quả không hoàn toàn lặp lại.** Cùng case "gửi bản tóm tắt lên Telegram" fail ở `v3_B_group_...094159` (S04), rồi `v4_B_group_...003821` (G07 + G06, 9/11), và chỉ đạt 10/10 sau khi sửa prompt (`v4_B_group_...094239`). Nhóm phải chạy lại nhiều lần: có 2 run v4 base, 2 run v4 group, và hai bản prompt khác nhau mang cùng nhãn v4 (hash `d9a6cd2ad96c` và `45ad071f97a8`). Phải dựa vào `prompt_hash`/`tools_hash` trong JSON để biết run nào ứng với artifact nào.
- **Chạy lại baseline.** Log v0 cũ bị xóa ở commit "Redo" rồi chạy lại (`v0_B_base_openrouter_20261110T215302319097.json`), nên toàn bộ v0–v3 trong CSV là các run mới; số liệu trong báo cáo lấy từ các run này.
- **Provider lỗi.** Tất cả 13 file trong `starter_v0/runs/` đều có `provider_error_cases = 0` và `measured_cases = total_cases`, không có run nào bị loại vì lỗi provider/quota.
- **Encoding trên Windows.** Khi đọc run JSON/CSV bằng Python trên Windows, mặc định dùng cp1252 nên gặp `UnicodeDecodeError`/hiển thị sai tiếng Việt. Cách xử lý: mở file với `encoding='utf-8'` và chạy với `PYTHONIOENCODING=utf-8` (dùng `starter_v0/.venv/Scripts/python.exe`).
- **Số liệu v4–v6 chưa vào `version_log.csv`.** CSV chỉ ghi v0–v3 trong khi `runs/` đã có v4–v6; báo cáo ghi các run này ở bảng bổ sung B1, cần nhóm bổ sung dòng CSV nếu muốn tính vào bằng chứng chính.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- **Fix nào thuộc `system_prompt.md`?** v1 (`d9a6cd2ad96c`): bỏ persona "fast, proactive" và chỉ dẫn đoán/gửi ngay/làm một bước; thêm các mục Missing information (thiếu handle/URL/chủ đề -> `clarify` text, không đoán), Routing (timeline / social_search / lookup / fetch / clarify), Sending (`clarify yes_no` trước, rồi `send confirmed=true`) và Other (không gọi tool cho yêu cầu ngoài phạm vi như code/toán). Các lỗi được sửa: R08, R10, R11, R14 (và R12/R13 một phần). Các bản sau chỉ thêm câu vào prompt: không tái dùng chủ thể của câu hỏi trước làm account cho "tweet mới nhất" mới, và `clarify yes_no` cho MỌI yêu cầu gửi kể cả nội dung mơ hồ (S04, G07).
- **Fix nào thuộc `tools.yaml`?** v2 (`0eda1e544c47`): thêm "DÙNG KHI / KHÔNG DÙNG" cho mỗi tool, sửa routing và multi-turn (M02 trở lại pass, routing 0.95 -> 1.00). v3 (`385d0e759dbb`): mô tả tham số có convention rõ ràng (handle không có @, `topic`/`timeframe`/`search_type`, `response_type=yes_no` cho yêu cầu gửi), sửa lỗi sai args ở R12, R13 (case_accuracy 0.95 -> 1.00). Nói chung: lỗi routing/args thuộc `tools.yaml`; lỗi hành vi (đoán bừa, gửi ngay, ngoài phạm vi) thuộc `system_prompt.md`.
- **Failure nào cần review thủ công thay vì chấm tự động?** (1) R14 ở v0: `send` kèm cả đoạn code Python trong `text`: chấm tự động chỉ báo "expected no tool call", nhưng cần người xem xét xem nội dung trả lời có hợp lý không và rủi ro gửi nhầm (tool trả `needs_confirmation` nên chưa gửi thật). (2) Các lỗi `wrong_arg_value` kiểu thiếu `response_type` (R10 v1, G06 v4): model hỏi đúng câu, hậu quả thực tế gần như bằng 0 nhưng bị chấm fail, nên cần người đánh giá xem có chấp nhận được không. (3) S04/G07: `clarify` với `text` hỏi "gửi nội dung gì" cũng là hành vi hợp lý của người dùng thật nhưng bị chấm `wrong_boundary`. (4) Kết quả 1.00 trên bộ base 20 case không chứng minh agent tốt trong thực tế (xem rủi ro dưới).
- **Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?** Quan sát: v3 đạt 1.00 trên base nhưng cùng artifact chỉ đạt 0.90 trên bộ group (`v3_B_group_...094159`), và v4 group dao động 0.8182 -> 1.00 giữa các lần chạy; nghĩa là cải thiện có thể bị overfit vào bộ base và kết quả có độ nhiễu giữa các lần chạy. Giả thuyết tiếp theo: (a) chạy mỗi version nhiều lần (ví dụ 3 lần) trên cả base và group để đo phương sai trước khi kết luận; (b) ép `response_type` thành tham số bắt buộc (required) trong `tools.yaml` thay vì chỉ nhắc trong prompt, kỳ vọng loại hẳn lỗi thiếu `response_type`; (c) thêm case mới với cách diễn đạt khác của yêu cầu gửi/ngoài phạm vi để kiểm tra generalization; (d) thử model khác ngoài `openai/gpt-4o-mini` để xem fix có phụ thuộc model không.

## 8. Tài liệu tham khảo

- `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml` (bản hiện tại) và bản gốc ở commit `1536df8` (`git show 1536df8:starter_v0/artifacts/...`)
- `starter_v0/tools/README.md` và `starter_v0/tools/<tên>/TOOL.md` (wikipedia, hackernews, current_time và các tool starter)
- `starter_v0/app.py`, `starter_v0/requirements.txt`, `starter_v0/README.md` (chạy UI Streamlit, deploy Cloudflare Tunnel)
- `starter_v0/runs/*.json` (provider/model và kết quả eval), `starter_v0/artifacts/version_log.csv`
- `starter_v0/tests/test_tool_contract.py` (kiểm tra đồng bộ tools.yaml – TOOL_FUNCTIONS – eval)
- [TEAM.md](../../TEAM.md), [RUBRIC.md](../../RUBRIC.md)
