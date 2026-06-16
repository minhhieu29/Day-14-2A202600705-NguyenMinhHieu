import os
import sys

# Add solution folder to path
solution_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(solution_dir)
from solution import QAPair, RAGASEvaluator, BenchmarkRunner, FailureAnalyzer

def run():
    print("Initializing test benchmark with the 10 Oral Exam questions...")
    
    # 10 QA Pairs based on the oral exam questions
    qa_pairs = [
        QAPair(
            question="Cho một câu hỏi mà expected answer dùng từ đồng nghĩa với các chunk — recall có bị ảnh hưởng không? Tại sao?",
            expected_answer="Có bị ảnh hưởng và bị giảm điểm rất nặng do bộ đánh giá sử dụng lexical word overlap thô, không nắm bắt được ngữ nghĩa đồng nghĩa.",
            context="RAGASEvaluator dùng lexical word overlap để tính recall. Nếu expected answer dùng từ đồng nghĩa nhưng context không có từ đó, phép giao token sẽ rất nhỏ dẫn đến recall thấp.",
            metadata={"id": "Q01", "category": "retrieval"}
        ),
        QAPair(
            question="Nếu tăng top_k từ 3 lên 6, Context Recall thay đổi thế nào? Context Precision thay đổi thế nào? Hai cái có cùng chiều không?",
            expected_answer="Context Recall tăng hoặc giữ nguyên. Context Precision giảm hoặc giữ nguyên. Chúng thường ngược chiều nhau.",
            context="Tăng top-k giúp lấy thêm nhiều chunk, tăng độ phủ (Recall). Nhưng nếu các chunk mới là nhiễu, nó làm giảm độ chính xác xếp hạng (Precision).",
            metadata={"id": "Q02", "category": "retrieval"}
        ),
        QAPair(
            question="Reranker của bạn dùng lexical overlap — trường hợp nào reranker thất bại dù chunk thực sự relevant?",
            expected_answer="Reranker thất bại khi chunk có liên quan thực sự sử dụng các từ đồng nghĩa hoặc cách mô tả gián tiếp không chứa từ khóa trùng khớp ký tự với câu hỏi.",
            context="Reranker so khớp từ khóa thô (lexical overlap). Nếu chunk chứa thông tin đúng nhưng dùng từ đồng nghĩa hoặc viết tắt, overlap score sẽ thấp và bị xếp cuối.",
            metadata={"id": "Q03", "category": "retrieval"}
        ),
        QAPair(
            question="Faithfulness = 1.0 nhưng Completeness = 0.2 — điều này có nghĩa gì về hành vi của agent?",
            expected_answer="Agent trả lời hoàn toàn trung thực, không bịa đặt thông tin ngoài context nhưng trả lời quá ngắn gọn, sơ sài, bỏ sót phần lớn thông tin expected.",
            context="Faithfulness = 1.0 nghĩa là tất cả phát biểu đều có trong context. Completeness = 0.2 nghĩa là chỉ bao phủ 20% thông tin mong đợi.",
            metadata={"id": "Q04", "category": "generation"}
        ),
        QAPair(
            question="Một câu trả lời dài, dùng nhiều từ trong context nhưng không trả lời đúng câu hỏi — metrics nào phát hiện được, metrics nào bị đánh lừa?",
            expected_answer="Answer Relevancy phát hiện được và chấm điểm thấp. Faithfulness bị đánh lừa và chấm điểm cao vì các từ đều có trong context.",
            context="Faithfulness chỉ check xem câu trả lời có trong context không. Answer Relevancy check xem câu trả lời có liên quan đến câu hỏi hay không.",
            metadata={"id": "Q05", "category": "generation"}
        ),
        QAPair(
            question="Tại sao overall pass rate = 0% trong benchmark của bạn mà vẫn chấp nhận được trong context của lab này?",
            expected_answer="Vì đây là mock benchmark được thiết kế cố ý chứa lỗi để thực hành phân loại lỗi, phân nhóm lỗi (clustering), tìm nguyên nhân gốc rễ và kiểm thử quality gate.",
            context="Lab học phần thiết kế mock benchmark có pass rate = 0% để người học có mẫu lỗi thực hành Failure Analyzer và CI/CD regression testing.",
            metadata={"id": "Q06", "category": "generation"}
        ),
        QAPair(
            question="Position bias trong LLM-as-Judge là gì? Hệ thống của bạn detect nó bằng cách nào?",
            expected_answer="Position bias là thiên kiến Judge ưu tiên cho điểm cao hơn cho phương án xuất hiện trước. Hệ thống detect bằng cách so sánh điểm của câu đầu tiên với điểm trung bình các câu sau.",
            context="Position bias ưu tiên vị trí đầu tiên. detect_bias check xem điểm trung bình của vị trí 1 có lớn hơn điểm các vị trí sau cộng với 0.1 hay không.",
            metadata={"id": "Q07", "category": "evaluation"}
        ),
        QAPair(
            question="Nếu Judge luôn cho điểm 4/5 bất kể câu trả lời — detect_bias() của bạn có phát hiện được không? Đây là loại bias gì?",
            expected_answer="Có phát hiện được, đây là Leniency Bias (thiên kiến nương tay). Điểm 4/5 tương đương 0.8, đạt ngưỡng leniency_bias.",
            context="Judge chấm 4/5 (0.8) bất kể câu trả lời là biểu hiện của Leniency Bias. Hàm detect_bias kiểm tra nếu điểm trung bình > 0.8.",
            metadata={"id": "Q08", "category": "evaluation"}
        ),
        QAPair(
            question="run_regression() trả về regression_detected = True — bạn làm gì tiếp theo? Block hay alert? Với metric nào thì block?",
            expected_answer="Gửi alert cho dev, phân tích log. Block deploy nếu metric Faithfulness hoặc Context Recall giảm mạnh. Alert nếu Relevance/Completeness giảm nhẹ.",
            context="Regression_detected báo hiệu sụt giảm chất lượng. Cần block deploy khi Faithfulness (độ trung thực) giảm để tránh hallucination.",
            metadata={"id": "Q09", "category": "pipeline"}
        ),
        QAPair(
            question="Nếu phải chọn 1 metric duy nhất làm quality gate cho CI/CD, bạn chọn cái nào trong 5 metrics? Lý do?",
            expected_answer="Chọn Faithfulness vì sự trung thực là quan trọng nhất trong hệ thống RAG thực tế, giúp loại bỏ hoàn toàn rủi ro hallucination gây nguy hại.",
            context="Faithfulness đo tính grounded của câu trả lời. Đây là gate quan trọng nhất vì bịa đặt thông tin (hallucination) gây thiệt hại lớn nhất.",
            metadata={"id": "Q10", "category": "pipeline"}
        )
    ]

    # Let's write the actual answers generated by the "system under test" (agent)
    # We will simulate a mix of high-quality answers and some failed/deviating answers
    agent_outputs = {
        "Q01": "Có bị ảnh hưởng và điểm số sẽ giảm vì hệ thống so sánh từ trùng thô chứ không hiểu nghĩa đồng nghĩa.", # Good, but uses synonyms like "hệ thống", "so sánh từ trùng thô" instead of "bộ đánh giá", "lexical word overlap". Recall/Completeness will be medium.
        "Q02": "Context Recall tăng hoặc giữ nguyên do lấy nhiều tài liệu hơn. Context Precision giảm do nhiễu tăng. Chúng ngược chiều nhau.", # High match
        "Q03": "Reranker sẽ thất bại nếu chunk đúng lại dùng từ đồng nghĩa hay viết tắt.", # Slightly short (low completeness)
        "Q04": "Nghĩa là Agent trả lời trung thực (không bịa đặt) nhưng trả lời quá ngắn gọn, bỏ sót thông tin.", # High match
        "Q05": "Faithfulness bị lừa chấm cao vì từ lấy từ context, còn Answer Relevancy sẽ phát hiện và chấm thấp do không khớp câu hỏi.", # High match
        "Q06": "Vì đây là mock benchmark để thực hành phân loại lỗi và test tính năng Failure Analyzer.", # High match
        "Q07": "Là thiên kiến Judge thích chấm điểm cao cho câu đầu tiên. Hệ thống detect bằng cách so sánh điểm câu 1 với trung bình các câu sau.", # High match
        "Q08": "Hệ thống phát hiện được Leniency Bias vì điểm trung bình bằng 0.8.", # High match
        "Q09": "Cần gửi alert. Block deploy khi Faithfulness hoặc Context Recall giảm, alert khi các metric khác giảm.", # High match
        "Q10": "Chọn Faithfulness vì tính chính xác và trung thực của thông tin trong RAG là quan trọng nhất để tránh hallucination." # High match
    }

    def agent_fn(question: str) -> str:
        for pair in qa_pairs:
            if pair.question == question:
                qid = pair.metadata["id"]
                return agent_outputs.get(qid, "Không có câu trả lời.")
        return "Default answer."

    evaluator = RAGASEvaluator()
    runner = BenchmarkRunner()

    print("Running evaluation runner over the 10 QA pairs...")
    results = runner.run(qa_pairs, agent_fn, evaluator)
    report = runner.generate_report(results)
    failures = runner.identify_failures(results, threshold=0.5)
    analyzer = FailureAnalyzer()
    
    # Write output to console and to file
    output_path = os.path.join(solution_dir, "oral_questions_benchmark_output.txt")
    print(f"Writing report to: {output_path}")
    
    with open(output_path, "w", encoding="utf-8") as f_out:
        f_out.write("=== ORAL EXAM QUESTIONS BENCHMARK REPORT ===\n")
        f_out.write(f"Total test cases: {report['total']}\n")
        f_out.write(f"Passed cases: {report['passed']} (Pass Rate: {report['pass_rate']:.2%})\n")
        f_out.write(f"Average Faithfulness: {report['avg_faithfulness']:.4f}\n")
        f_out.write(f"Average Relevance: {report['avg_relevance']:.4f}\n")
        f_out.write(f"Average Completeness: {report['avg_completeness']:.4f}\n")
        
        f_out.write("\n=== FAILURE DISTRIBUTION ===\n")
        for k, v in report["failure_types"].items():
            f_out.write(f"  {k}: {v}\n")
            
        f_out.write("\n=== DETAILED QA PAIR RESULTS ===\n")
        f_out.write("| ID | Faithfulness | Relevance | Completeness | Overall | Passed | Failure Type | Root Cause |\n")
        f_out.write("|----|--------------|-----------|--------------|---------|--------|--------------|------------|\n")
        for r in results:
            qid = r.qa_pair.metadata["id"]
            passed_str = "Yes" if r.passed else "No"
            ftype_str = r.failure_type if r.failure_type else "None"
            cause = analyzer.find_root_cause(r) if not r.passed else "None"
            f_out.write(f"| {qid} | {r.faithfulness:.2f} | {r.relevance:.2f} | {r.completeness:.2f} | {r.overall_score():.2f} | {passed_str} | {ftype_str} | {cause} |\n")
            
        f_out.write(f"\n=== FAILURES ({len(failures)}) ===\n")
        for f in failures:
            qid = f.qa_pair.metadata["id"]
            f_out.write(f"\n--- Failure {qid} ---\n")
            f_out.write(f"Question: {f.qa_pair.question}\n")
            f_out.write(f"Agent Answer: {f.actual_answer}\n")
            f_out.write(f"Expected Answer: {f.qa_pair.expected_answer}\n")
            f_out.write(f"Scores - Faithfulness: {f.faithfulness:.2f} | Relevance: {f.relevance:.2f} | Completeness: {f.completeness:.2f} | Overall: {f.overall_score():.2f}\n")
            f_out.write(f"Root cause: {analyzer.find_root_cause(f)}\n")
            
        suggestions = analyzer.generate_improvement_suggestions(failures)
        f_out.write("\n=== AUTO-GENERATED IMPROVEMENT LOG ===\n")
        log = analyzer.generate_improvement_log(failures, suggestions)
        f_out.write(log + "\n")

    # Also print summary to terminal
    print("\n=======================================================")
    print("                   BENCHMARK SUMMARY                   ")
    print("=======================================================")
    print(f"Total: {report['total']} | Passed: {report['passed']} | Pass Rate: {report['pass_rate']:.2%}")
    print(f"Avg Faithfulness: {report['avg_faithfulness']:.4f}")
    print(f"Avg Relevance:    {report['avg_relevance']:.4f}")
    print(f"Avg Completeness: {report['avg_completeness']:.4f}")
    print("=======================================================")
    
    if failures:
        print(f"Detected {len(failures)} failures. Detailed log saved to solution/oral_questions_benchmark_output.txt.")
    else:
        print("All test cases passed successfully!")

if __name__ == "__main__":
    run()
