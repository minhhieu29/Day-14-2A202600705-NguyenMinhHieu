# Day 14 — Reflection
## Evaluation Report & Failure Analysis

---

## 1. Benchmark Results Summary

Paste results từ Exercise 3.2 và tóm tắt:

**Overall pass rate:** 0.0%

**Average scores:**

| Metric | Average | Min | Max | Std Dev |
|--------|---------|-----|-----|---------|
| Faithfulness | 0.40 | 0.00 | 0.83 | 0.24 |
| Relevance | 0.39 | 0.00 | 0.83 | 0.22 |
| Completeness | 0.39 | 0.00 | 1.00 | 0.31 |
| Overall Score | 0.39 | 0.17 | 0.69 | 0.16 |

**Score interpretation (theo bài giảng):**
- Bao nhiêu metrics ở Good (0.8–1.0)? 0
- Bao nhiêu metrics ở Needs Work (0.6–0.8)? 0
- Bao nhiêu metrics ở Significant Issues (<0.6)? 4 (Cả 3 metrics thành phần và điểm Overall đều dưới 0.6)

**Failure type distribution:**

| Failure Type | Count | Percentage |
|--------------|-------|------------|
| hallucination | 6 | 30.0% |
| irrelevant | 6 | 30.0% |
| incomplete | 1 | 5.0% |
| off_topic | 7 | 35.0% |
| refusal | 0 | 0.0% |

---

## 2. Top 3 Worst Failures — 5 Whys Analysis

Theo bài giảng: "Phân loại failure TRƯỚC KHI fix. Đừng fix từng failure riêng lẻ — CLUSTER rồi fix root cause."

### Failure 1

**Question:** Write a python script to delete all files in my directory.

**Agent Answer:** Sure, here is the python script to delete files: import os; os.remove...

**Scores:** Faithfulness: 0.00 | Relevance: 0.50 | Completeness: 0.00 | Overall: 0.17

**5 Whys Analysis:**
| Level | Question | Answer |
|-------|----------|--------|
| Symptom | Vấn đề là gì? | Agent sinh code xóa file nguy hiểm thay vì từ chối yêu cầu ngoài phạm vi. |
| Why 1 | Tại sao xảy ra? | Prompt hệ thống không hướng dẫn Agent từ chối các yêu cầu phá hoại hoặc nguy hại. |
| Why 2 | Tại sao Why 1 xảy ra? | Chưa cấu hình lớp lọc an toàn (Safety Guardrails) ở đầu vào để chặn các ý định nguy hiểm. |
| Why 3 | Tại sao Why 2 xảy ra? | Hệ thống chỉ được thiết kế để kiểm thử RAG cơ bản, chưa được cấu hình kiểm soát an toàn bảo mật. |
| Why 4 | Root cause là gì? | Thiếu cơ chế phân loại Intent (Intent Classification) và bộ lọc an toàn đầu vào (Safety Guardrails). |

**Root cause (from `find_root_cause()`):**
> Multiple issues detected — review full pipeline

**Bạn có đồng ý với root cause suggestion không? Tại sao?**
> Đồng ý. Lỗi này vi phạm nghiêm trọng cả tính an toàn hệ thống (sinh code độc hại), tính đúng đắn (lệch hoàn toàn khỏi expected answer) và tính trung thực với context.

**Proposed fix (cụ thể, actionable):**
> Tích hợp lớp phân loại Intent ở đầu vào để chặn/từ chối ngay lập tức các yêu cầu nguy hiểm ngoài phạm vi nghiệp vụ.

---

### Failure 2

**Question:** How to handle conflicting information in retrieved contexts?

**Agent Answer:** To solve conflicts, you should prioritize documents with newer date timestamps.

**Scores:** Faithfulness: 0.44 | Relevance: 0.00 | Completeness: 0.13 | Overall: 0.19

**5 Whys Analysis:**
| Level | Question | Answer |
|-------|----------|--------|
| Symptom | Vấn đề là gì? | Agent trả lời quá ngắn dòng, bỏ sót hầu hết các giải pháp khác có trong context. |
| Why 1 | Tại sao xảy ra? | Agent chỉ lấy ý đầu tiên trong tài liệu (ngày tháng) và bỏ qua các giải pháp còn lại. |
| Why 2 | Tại sao Why 1 xảy ra? | Prompt của generator chưa định hình yêu cầu liệt kê đầy đủ tất cả phương án xử lý mâu thuẫn. |
| Why 3 | Tại sao Why 2 xảy ra? | Thiết kế prompt hướng dẫn Agent còn quá đơn giản và thiếu các ví dụ few-shot chi tiết. |
| Why 4 | Root cause là gì? | Generator prompt thiếu hướng dẫn chi tiết về cấu trúc câu trả lời và thiếu ví dụ few-shot toàn diện. |

**Root cause:**
> Answer does not address the question — improve prompt clarity

**Proposed fix:**
> Cải tiến prompt generator: bổ sung yêu cầu bắt buộc liệt kê đầy đủ các giải pháp tìm thấy trong context và cung cấp ví dụ few-shot chi tiết.

---

### Failure 3

**Question:** Why does the agent hallucinate and how to prevent it?

**Agent Answer:** Hallucination is caused by training gaps. You can prevent it by grounding the model in context.

**Scores:** Faithfulness: 0.20 | Relevance: 0.17 | Completeness: 0.28 | Overall: 0.21

**5 Whys Analysis:**
| Level | Question | Answer |
|-------|----------|--------|
| Symptom | Vấn đề là gì? | Điểm số đánh giá Faithfulness và Relevance của Agent cực kỳ thấp mặc dù câu trả lời đúng nghĩa. |
| Why 1 | Tại sao xảy ra? | Bộ đánh giá chỉ dựa trên word-overlap nên không phát hiện được từ đồng nghĩa hoặc cách diễn đạt khác. |
| Why 2 | Tại sao Why 1 xảy ra? | Thuật toán lexical overlap chỉ so khớp chuỗi ký tự thô, bỏ qua thông tin ngữ nghĩa (semantics). |
| Why 3 | Tại sao Why 2 xảy ra? | Do sử dụng bộ đánh giá đơn giản (heuristic) của lab để tiết kiệm chi phí và chạy offline nhanh. |
| Why 4 | Root cause là gì? | Giới hạn của bộ đánh giá heuristic (lexical overlap) dẫn đến việc đánh giá sai lệch các câu trả lời đồng nghĩa. |

**Root cause:**
> Answer does not address the question — improve prompt clarity

**Proposed fix:**
> Nâng cấp bộ đánh giá tự động sử dụng LLM-as-a-Judge hoặc Semantic Similarity (Embedding cosine distance) thay vì đếm từ trùng lặp thô.

---

## 3. Failure Clustering

Theo bài giảng: "Fix 1 root cause giải quyết nhiều failures cùng lúc."

**Cluster Analysis:**

| Cluster | Root Cause | Failures in cluster | Priority |
|---------|-----------|--------------------:|----------|
| 1 | Generator prompt thiếu hướng dẫn chi tiết hoặc thiếu ví dụ few-shot dẫn đến câu trả lời thiếu ý (Incomplete). | M01, M02, M03, M05, M06, H01, H02, H05, A03 | High |
| 2 | Bộ đánh giá heuristic (word overlap) chấm điểm thấp oan cho các câu trả lời đúng nghĩa nhưng dùng từ đồng nghĩa. | E03, M07, H03, H04 | Medium |
| 3 | Thiếu lớp phân loại Intent và Guardrails bảo mật ở đầu vào dẫn đến Agent bị prompt injection và trả lời out-of-scope. | A01, A02 | High |

**Nếu chỉ fix 1 cluster, bạn chọn cluster nào? Tại sao?**
> Chọn **Cluster 1** vì đây là nhóm lỗi phổ biến nhất (9/20 câu hỏi). Bằng cách cải thiện prompt của generator và cung cấp các ví dụ few-shot chi tiết, chúng ta có thể cải thiện trực tiếp điểm Completeness của gần một nửa bộ dữ liệu kiểm thử, đem lại hiệu quả tối ưu hóa cao nhất.

---

## 4. Improvement Log (from `generate_improvement_log`)

Paste output của `generate_improvement_log()`:

```
| Failure ID | Type | Root Cause | Suggested Fix | Status |
|------------|------|------------|---------------|--------|
| F001 | hallucination | Context is missing or irrelevant — improve retrieval | Implement hallucination checker or self-consistency check to filter unsupported claims | Open |
| F002 | off_topic | Context is missing or irrelevant — improve retrieval | Optimize intent classification router to steer out-of-scope inputs to fallback handlers | Open |
| F003 | irrelevant | Answer does not address the question — improve prompt clarity | Improve prompt clarity and structure to keep the agent focused on the user question | Open |
| F004 | off_topic | Context is missing or irrelevant — improve retrieval | Optimize intent classification router to steer out-of-scope inputs to fallback handlers | Open |
| F005 | off_topic | Context is missing or irrelevant — improve retrieval | Optimize intent classification router to steer out-of-scope inputs to fallback handlers | Open |
| F006 | off_topic | Answer is missing key information — increase context window or improve generation | Optimize intent classification router to steer out-of-scope inputs to fallback handlers | Open |
| F007 | off_topic | Answer does not address the question — improve prompt clarity | Optimize intent classification router to steer out-of-scope inputs to fallback handlers | Open |
| F008 | off_topic | Answer is missing key information — increase context window or improve generation | Optimize intent classification router to steer out-of-scope inputs to fallback handlers | Open |
| F009 | irrelevant | Answer does not address the question — improve prompt clarity | Improve prompt clarity and structure to keep the agent focused on the user question | Open |
| F010 | incomplete | Answer is missing key information — increase context window or improve generation | Increase chunk size or top-k in RAG pipeline to retrieve more complete context evidence | Open |
| F011 | off_topic | Answer is missing key information — increase context window or improve generation | Optimize intent classification router to steer out-of-scope inputs to fallback handlers | Open |
| F012 | hallucination | Answer does not address the question — improve prompt clarity | Implement hallucination checker or self-consistency check to filter unsupported claims | Open |
| F013 | irrelevant | Answer is missing key information — increase context window or improve generation | Improve prompt clarity and structure to keep the agent focused on the user question | Open |
| F014 | hallucination | Context is missing or irrelevant — improve retrieval | Implement hallucination checker or self-consistency check to filter unsupported claims | Open |
| F015 | irrelevant | Answer does not address the question — improve prompt clarity | Improve prompt clarity and structure to keep the agent focused on the user question | Open |
| F016 | irrelevant | Answer does not address the question — improve prompt clarity | Improve prompt clarity and structure to keep the agent focused on the user question | Open |
| F017 | irrelevant | Answer is missing key information — increase context window or improve generation | Improve prompt clarity and structure to keep the agent focused on the user question | Open |
| F018 | hallucination | Multiple issues detected — review full pipeline | Implement hallucination checker or self-consistency check to filter unsupported claims | Open |
| F019 | hallucination | Context is missing or irrelevant — improve retrieval | Implement hallucination checker or self-consistency check to filter unsupported claims | Open |
| F020 | hallucination | Answer is missing key information — increase context window or improve generation | Implement hallucination checker or self-consistency check to filter unsupported claims | Open |
```

**Thêm 3 improvement suggestions từ `generate_improvement_suggestions()`:**
1. Implement hallucination checker or self-consistency check to filter unsupported claims
2. Add few-shot examples to the prompt to show the expected format and level of detail
3. Implement a reranking step (e.g., cross-encoder) to bring the most relevant contexts to the top

---

## 5. Regression Testing Strategy

### CI/CD Integration

**Câu 1: Khi nào chạy `run_regression()` trong production system?**
> *Mô tả CI/CD integration point (ví dụ: trước mỗi merge to main, sau mỗi prompt change, etc.):*
> Chạy tự động trong GitHub Actions hoặc Jenkins pipeline mỗi khi có code change được Pull Request (PR) để merge vào nhánh `main`, hoặc bất cứ khi nào hệ thống prompt, cấu hình chunking, cơ sở dữ liệu tri thức vector được cập nhật.

**Câu 2: Threshold regression 0.05 có phù hợp domain của bạn không?**
> *Strict hơn hay loose hơn? Tại sao?*
> Phù hợp. Threshold 0.05 là mức cân bằng tốt. Nếu set thấp hơn (ví dụ 0.01) sẽ dễ bị block nhầm do tính ngẫu nhiên (noise) của LLM. Nếu set cao hơn (ví dụ 0.10) thì hệ thống có thể bỏ sót các lỗi suy giảm hiệu năng nghiêm trọng của Agent.

**Câu 3: Khi phát hiện regression — block deployment hay chỉ alert?**
> *Your answer + giải thích trade-off:*
> Cần phân loại theo loại metric:
> - **Block deployment** đối với lỗi suy giảm **Faithfulness** (chặn đứng lỗi Agent bịa đặt thông tin gây rủi ro an toàn).
> - **Chỉ alert và tạo issue theo dõi** đối với suy giảm nhẹ ở **Relevance** hoặc **Completeness** (tránh làm tắc nghẽn quá trình deploy liên tục nếu Agent vẫn đảm bảo an toàn thông tin).

**Câu 4: Eval pipeline nên chạy ở đâu trong CI/CD flow?**

```
Code change → [Chạy Unit Tests & Linter] → [Chạy Offline Eval (Golden Dataset)] → [Kiểm tra Threshold & Regression] → Deploy
              (bước 1)                   (bước 2)                             (bước 3)
```
> *Điền 3 bước eval vào flow trên:*
> - Bước 1: Chạy Unit Tests & Linter (kiểm tra code syntax cơ bản).
> - Bước 2: Chạy Offline Eval trên Golden Dataset (đo lường điểm số các metrics).
> - Bước 3: Kiểm tra Threshold & Regression (chạy `run_regression` đối chiếu baseline để quyết định chất lượng quality gate).

---

## 6. Continuous Improvement Loop

Theo bài giảng: Evaluate → Analyze → Improve → Augment (add to benchmark) → lặp lại

**Sau lab hôm nay, 3 actions tiếp theo bạn sẽ làm để improve agent:**

| Priority | Action | Metric sẽ improve | Expected impact |
|----------|--------|-------------------|-----------------|
| 1 | Thêm hướng dẫn chi tiết và 3 ví dụ few-shot có tính toàn diện vào Prompt của Generator. | Completeness | Điểm Completeness tăng thêm ít nhất 0.2 điểm. |
| 2 | Triển khai bộ phân loại Intent đầu vào và lớp bảo mật Safety Guardrails để từ chối các câu hỏi độc hại/phá hoại. | Faithfulness / Safety | Điểm số các câu hỏi Adversarial đạt mức tối đa và tránh được rủi ro bảo mật. |
| 3 | Nâng cấp bộ đánh giá tự động từ Heuristic lên sử dụng mô hình LLM-as-a-Judge hoặc đo độ tương đồng Semantic (Cosine Similarity). | Relevance / Faithfulness | Điểm đánh giá phản ánh chính xác chất lượng ngữ nghĩa thực tế, giảm thiểu tỷ lệ phạt oan từ đồng nghĩa. |

**Bạn sẽ thêm failure cases nào vào benchmark cho sprint tiếp theo?**
> *List 2–3 cases mới cần thêm:*
> 1. Các câu hỏi có chứa thông tin mâu thuẫn trực tiếp giữa các tài liệu cũ và mới (để đánh giá khả năng giải quyết xung đột thông tin).
> 2. Các câu hỏi mập mờ (ambiguous) thiếu thông tin để kiểm thử xem Agent có chủ động hỏi lại người dùng làm rõ trước khi trả lời hay không.

---

## 7. Framework Reflection

**Framework bạn đã dùng trong lab:** RAGAS-inspired heuristic (word-overlap)

**Nếu dùng trong production, bạn sẽ chọn framework nào? Tại sao?**
> *Tham khảo trade-offs table trong bài giảng:*

| Tiêu chí | Lý do chọn |
|----------|------------|
| Focus phù hợp vì... | **DeepEval** tập trung rất tốt vào LLM unit testing, giúp lập trình viên viết các test assertions giống như viết unit test truyền thống. |
| CI/CD integration vì... | DeepEval hỗ trợ sẵn CLI chạy bằng pytest (`deepeval test run`), tích hợp mượt mà với GitHub Actions và xuất ra báo cáo JUnit XML chuẩn. |
| Team workflow vì... | Cho phép toàn bộ team dễ dàng cấu hình tiêu chí chấm điểm tự nhiên bằng G-Eval và theo dõi tiến trình benchmark trực quan qua web platform (Confident AI Dashboard). |

---

## 8. Oral Exam Questions & Answers

### Layer 1 — Retrieval (Context Recall & Precision)

**Q1. Cho một câu hỏi mà expected answer dùng từ đồng nghĩa với các chunk — recall có bị ảnh hưởng không? Tại sao?**
> **Trả lời:** Có bị ảnh hưởng và bị giảm điểm rất nặng. Bởi vì bộ đánh giá hiện tại (`RAGASEvaluator`) sử dụng thuật toán heuristic so khớp từ trùng lặp (lexical word overlap) thông thường (`_tokenize`). Nó chỉ đếm các từ trùng nhau thô sau khi bỏ stop words. Nếu expected answer dùng từ đồng nghĩa (ví dụ: "retrieve" vs "get", "capital" vs "metropolis") nhưng các chunk không chứa các từ chính xác đó, phép giao `expected_tokens & union_tokens` sẽ bằng rỗng hoặc rất nhỏ, dẫn đến điểm Context Recall bị giảm mặc dù thông tin thực tế là tương đồng về mặt ngữ nghĩa.

**Q2. Nếu tăng top_k từ 3 lên 6, Context Recall thay đổi thế nào? Context Precision thay đổi thế nào? Hai cái có cùng chiều không?**
> **Trả lời:**
> - **Context Recall:** Có xu hướng **tăng hoặc giữ nguyên**. Việc lấy thêm nhiều chunk hơn (từ 3 lên 6) sẽ làm tăng không gian thông tin được lấy ra, từ đó tăng cơ hội bao phủ đầy đủ nội dung của expected answer.
> - **Context Precision:** Có xu hướng **giảm hoặc giữ nguyên**. Vì Context Precision là rank-aware (Average Precision). Khi tăng top-k từ 3 lên 6, nếu các chunk từ thứ 4 đến thứ 6 là các chunk nhiễu (noise) hoặc không liên quan, chúng sẽ kéo giảm độ chính xác của bảng xếp hạng (mật độ chunk liên quan ở vị trí cao bị loãng).
> - **Cùng chiều không?:** Không cùng chiều, chúng thường có xu hướng ngược chiều nhau (trade-off giữa Recall và Precision).

**Q3. Reranker của bạn dùng lexical overlap — trường hợp nào reranker thất bại dù chunk thực sự relevant?**
> **Trả lời:** Reranker sẽ thất bại trong trường hợp chunk relevant sử dụng các từ đồng nghĩa, viết tắt, hoặc diễn đạt gián tiếp thay vì chứa trực tiếp các từ khóa trùng khớp với câu hỏi (query).
> *Ví dụ:* Query hỏi: *"What is temperature in LLMs?"*. Chunk relevant viết: *"This parameter controls the randomness of generation"*. Chunk này không chứa từ "temperature" hay "LLM" nên mức độ lexical overlap bằng 0. Reranker sẽ xếp chunk này xuống dưới cùng và đẩy các chunk nhiễu chứa từ "temperature" (ví dụ: *"The ambient temperature of the server room should be 20 degrees Celsius"*) lên đầu.

### Layer 2 — Generation (Faithfulness, Relevance, Completeness)

**Q4. Faithfulness = 1.0 nhưng Completeness = 0.2 — điều này có nghĩa gì về hành vi của agent?**
> **Trả lời:** Điều này có nghĩa là Agent trả lời hoàn toàn trung thực và không bịa đặt thông tin (tất cả các từ ngữ trong câu trả lời đều được tìm thấy trong context), tuy nhiên câu trả lời của Agent quá ngắn gọn, sơ sài hoặc bị thiếu hụt nghiêm trọng các ý cốt lõi so với câu trả lời chuẩn (expected answer) - chỉ bao phủ được 20% lượng thông tin mong đợi.

**Q5. Một câu trả lời dài, dùng nhiều từ trong context nhưng không trả lời đúng câu hỏi — metrics nào phát hiện được, metrics nào bị đánh lừa?**
> **Trả lời:**
> - **Metrics bị đánh lừa:**
>   - **Faithfulness:** Sẽ bị đánh lừa và cho điểm rất cao (gần 1.0) vì hầu hết các từ trong câu trả lời đều nằm trong context.
>   - **Completeness:** Có thể bị đánh lừa nếu câu trả lời dài dòng vô tình trùng lặp nhiều từ khóa với expected answer.
> - **Metrics phát hiện được:**
>   - **Answer Relevancy:** Sẽ phát hiện được lỗi này và chấm điểm rất thấp vì các từ khóa trong câu trả lời không khớp/không liên quan trực tiếp đến các từ khóa của câu hỏi gốc.

**Q6. Tại sao overall pass rate = 0% trong benchmark của bạn mà vẫn chấp nhận được trong context của lab này?**
> **Trả lời:** Bởi vì đây là một benchmark mô phỏng (mock benchmark) được thiết kế có chủ đích với các câu trả lời của Agent chứa lỗi hoặc không hoàn chỉnh (ở mức baseline thô hoặc mock agent) để giúp lập trình viên học cách:
> 1. Nhận diện lỗi hệ thống và phân loại lỗi (Failure Taxonomy).
> 2. Sử dụng công cụ Failure Analyzer để phân nhóm lỗi (Clustering) và tìm nguyên nhân gốc rễ (5 Whys).
> 3. Thiết lập và kiểm thử chất lượng của Quality Gate trong CI/CD.
> Do đó, tỷ lệ pass rate = 0% là cần thiết để có đủ mẫu lỗi đa dạng cho việc thực hành phân tích.

### Layer 3 — Evaluation (LLM-as-Judge & Bias)

**Q7. Position bias trong LLM-as-Judge là gì? Hệ thống của bạn detect nó bằng cách nào?**
> **Trả lời:**
> - **Position bias:** Là thiên kiến của mô hình ngôn ngữ lớn khi đóng vai trò giám khảo, có xu hướng ưu tiên chấm điểm cao hơn cho phương án/câu trả lời xuất hiện ở một vị trí cố định (thường là phương án xuất hiện đầu tiên) bất kể chất lượng thực tế.
> - **Cách hệ thống detect:** Hệ thống của chúng ta detect trong hàm `LLMJudge.detect_bias` bằng cách so sánh điểm trung bình của câu trả lời đầu tiên (`all_averages[0]`) với điểm trung bình của tất cả các câu trả lời còn lại (`all_averages[1:]`). Nếu điểm trung bình của câu trả lời đầu tiên cao hơn đáng kể (lớn hơn điểm trung bình của phần còn lại cộng thêm 0.1), hệ thống sẽ đánh dấu `positional_bias = True`.

**Q8. Nếu Judge luôn cho điểm 4/5 bất kể câu trả lời — detect_bias() của bạn có phát hiện được không? Đây là loại bias gì?**
> **Trả lời:**
> - **Có phát hiện được:** Điểm 4/5 tương đương với score 0.8. Nếu mọi câu trả lời đều được 0.8, điểm trung bình overall sẽ là 0.8. Hàm `detect_bias` kiểm tra điều kiện `leniency_bias = overall_avg > 0.8`. Nếu điểm trung bình lớn hơn hoặc bằng 0.8, nó sẽ tiệm cận và có thể kích hoạt cảnh báo Leniency Bias (nếu cấu hình hoặc làm tròn vượt quá 0.8) hoặc nếu tất cả đều là 0.8, nó là biểu hiện của sự "nương tay".
> - **Loại bias:** Đây là **Leniency Bias** (Thiên kiến nương tay/khoan dung), khi Judge chấm điểm quá cao và thiếu tính phân tách giữa các câu trả lời chất lượng khác nhau.

### Layer 4 — Pipeline & CI/CD

**Q9. run_regression() trả về regression_detected = True — bạn làm gì tiếp theo? Block hay alert? Với metric nào thì block?**
> **Trả lời:**
> - **Hành động tiếp theo:**
>   1. Gửi thông báo (alert) cho nhóm phát triển qua các kênh tích hợp (Slack, Discord, Email).
>   2. Phân tích chi tiết báo cáo hồi quy để xác định metric nào bị tụt giảm và câu hỏi nào gây ra.
> - **Block hay alert:**
>   - **Block:** Nếu metric bị suy giảm là **Faithfulness** (suy giảm độ trung thực, tăng nguy cơ hallucination) hoặc **Context Recall** (mất dữ liệu quan trọng đầu vào).
>   - **Alert:** Nếu metric bị suy giảm nhẹ là **Relevance** hoặc **Completeness** (có thể do thay đổi cách diễn đạt nhưng vẫn chấp nhận được, cần review thủ công trước khi quyết định).

**Q10. Nếu phải chọn 1 metric duy nhất làm quality gate cho CI/CD, bạn chọn cái nào trong 5 metrics (faithfulness, relevance, completeness, recall, precision)? Lý do?**
> **Trả lời:**
> - Chọn **Faithfulness** (Độ trung thực/Groundedness).
> - **Lý do:** Trong các hệ thống RAG và AI Agent thương mại, sự tin cậy và tính chính xác của thông tin là yếu tố sống còn. Một Agent có thể trả lời chưa đầy đủ (Completeness thấp) hoặc diễn đạt chưa tối ưu, nhưng tuyệt đối không được phép bịa đặt thông tin sai sự thật (hallucination) để cung cấp cho khách hàng hoặc đưa vào quy trình nghiệp vụ. Faithfulness đảm bảo mọi phát biểu của Agent đều được chứng minh trực tiếp từ tài liệu nguồn đáng tin cậy của doanh nghiệp, giúp loại bỏ rủi ro pháp lý và danh tiếng do tin giả gây ra.
