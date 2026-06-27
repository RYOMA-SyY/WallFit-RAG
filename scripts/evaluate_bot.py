import os
import json
import re
import time
from datetime import datetime
from dotenv import load_dotenv
from wallfit_rag.engine import RAGEngine
from wallfit_rag.config import Settings
from openrouter import OpenRouter

# Load environment
load_dotenv()

class WahibaEvaluator:
    def __init__(self):
        print("--- Initializing WahibaFit Evaluator ---")
        self.settings = Settings()
        self.engine = RAGEngine(self.settings)
        self.engine.load_vector_store()
        self.engine.load_generator()
        
        self.judge_client = None
        if self.settings.openai_api_key:
            self.judge_client = OpenRouter(api_key=self.settings.openai_api_key)

    def automated_score(self, prompt, answer):
        """Run regex and heuristic checks on the response."""
        # check for sentence limit instructions
        sentence_limit = None
        limit_match = re.search(r'(\d+)\s+sentences?', prompt, re.I)
        if limit_match:
            sentence_limit = int(limit_match.group(1))

        # count sentences in answer (rough heuristic)
        # remove sources before counting
        answer_no_sources = re.sub(r'sources?:.*$', '', answer, flags=re.I | re.S).strip()
        sentences = [s for s in re.split(r'[.!?]+', answer_no_sources) if len(s.strip()) > 5]
        
        follows_limit = 1
        if sentence_limit is not None:
            follows_limit = 1 if len(sentences) <= sentence_limit else 0

        scores = {
            "no_robotic_headers": 1 if not re.search(r'^#|^\d\.|Key Points|Conclusion|Summary', answer, re.M) else 0,
            "no_pdf_labels": 1 if not re.search(r'\[.*\.pdf\]', answer) else 0,
            "has_caring_closing": 1 if re.search(r'\?|care|feeling|khti|chérie|love|how are|hope|take care', answer[-100:].lower()) else 0,
            "is_concise": 1 if len(answer) < 800 else 0,
            "identifies_correctly": 1 if "WahibaFit" in answer and "OWL" not in answer else 0,
            "is_lowercase_style": 1 if len(re.findall(r'[a-z]', answer)) > len(re.findall(r'[A-Z]', answer)) * 3 else 0,
            "follows_sentence_limit": follows_limit
        }
        return scores

    def llm_judge_score(self, prompt, answer, expected):
        """Use a high-reasoning model to judge quality."""
        if not self.judge_client:
            return {"score": 0, "justification": "No judge client available"}

        judge_prompt = f"""
        You are an expert evaluator for a fitness coach AI named WahibaFit.
        
        USER PROMPT: {prompt}
        AI RESPONSE: {answer}
        EXPECTED BEHAVIOR: {expected}
        
        Score the AI RESPONSE on a scale of 1-5 based on:
        1. ACCURACY: Is the fitness/health advice scientifically sound?
        2. PERSONA: Is it warm, sisterly, and professional (WahibaFit persona)?
        3. BREVITY: Is it concise and direct?
        
        Return ONLY a JSON object: {{"score": float, "justification": "string"}}
        """
        
        try:
            resp = self.judge_client.chat.send(
                model="openrouter/owl-alpha",
                messages=[{"role": "user", "content": judge_prompt}]
            )
            raw_text = resp.choices[0].message.content
            # Extract JSON if model adds chatter
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return json.loads(raw_text)
        except Exception as e:
            print(f"\n    [JUDGE ERROR] {e}")
            return {"score": 0, "justification": f"Judge Error: {e}"}

    def run_eval(self, eval_set_path):
        # Use absolute path or relative to project root
        if not os.path.isabs(eval_set_path):
            eval_set_path = os.path.join(os.getcwd(), eval_set_path)
            
        with open(eval_set_path, 'r', encoding='utf-8') as f:
            test_cases = json.load(f)

        results = []
        print(f"\nRunning {len(test_cases)} test cases...")

        for case in test_cases:
            print(f"  [{case['id']}] {case['category']}... ", end="", flush=True)
            
            start_time = time.time()
            # We use ask() which handles RAG + Persona
            output = self.engine.ask(case['prompt'])
            latency = time.time() - start_time
            
            answer = output.get("answer") or "BLOCKED"
            
            auto = self.automated_score(case['prompt'], answer)
            judge = self.llm_judge_score(case['prompt'], answer, case['expected_behavior'])
            
            results.append({
                "case": case,
                "response": answer,
                "auto_scores": auto,
                "judge_score": judge.get("score"),
                "judge_justification": judge.get("justification"),
                "latency": latency
            })
            print(f"Score: {judge.get('score')}/5")

        self.generate_report(results)

    def generate_report(self, results):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"evaluation_report_{timestamp}.md"
        
        avg_judge = sum(r['judge_score'] for r in results) / len(results)
        avg_latency = sum(r['latency'] for r in results) / len(results)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# WahibaFit Evaluation Report - {timestamp}\n\n")
            f.write(f"## Summary\n")
            f.write(f"- **Avg Judge Score:** {avg_judge:.2f}/5\n")
            f.write(f"- **Avg Latency:** {avg_latency:.2f}s\n\n")
            
            f.write("## Detailed Results\n\n")
            f.write("| ID | Category | Judge | Auto-Score (Avg) | Latency | Result |\n")
            f.write("|---|---|---|---|---|---|\n")
            
            for r in results:
                auto_avg = sum(r['auto_scores'].values()) / len(r['auto_scores'])
                status = "✅" if r['judge_score'] >= 4 else "⚠️" if r['judge_score'] >= 3 else "❌"
                f.write(f"| {r['case']['id']} | {r['case']['category']} | {r['judge_score']} | {auto_avg:.2f} | {r['latency']:.2f}s | {status} |\n")
            
            f.write("\n## Failure Analysis\n\n")
            for r in results:
                if r['judge_score'] < 3.5:
                    f.write(f"### {r['case']['id']} ({r['case']['category']})\n")
                    f.write(f"**Prompt:** {r['case']['prompt']}\n\n")
                    f.write(f"**Response:** {r['response']}\n\n")
                    f.write(f"**Judge Reason:** {r['judge_justification']}\n\n")
                    f.write("---\n")

        print(f"\nDONE! Report generated: {report_path}")

if __name__ == "__main__":
    evaluator = WahibaEvaluator()
    evaluator.run_eval("scripts/evaluation_set.json")
