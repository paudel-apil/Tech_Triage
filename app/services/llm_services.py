import re, json
from groq import Groq

class LLMService:
    def __init__(self, api_key: str, model: str = 'qwen/qwen3-32b'):
        self.client = Groq(api_key=api_key)
        self.model = model

    @staticmethod
    def extract_json(text: str) -> str:
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        m = re.search(r"\{.*\}", text, re.DOTALL)
        return m.group(0) if m else text.strip()

    def generate_solution(self, description: str, label: str,
                          priority: str, similar_tickets: list) -> str:
        context = "\n".join([
            f"- [{t['similarity']:.2f}] {t['description']}"
            for t in similar_tickets[:3]
        ])
        prompt = f"""You are a senior IT operations expert. A support ticket has been classified as follows:

TICKET: {description}
CATEGORY: {label}
PRIORITY: {priority}

Most similar past tickets:
{context}

"Write a clear, step-by-step resolution plan (under 150 words). Format the plan as a bulleted list using dashes (-). Return ONLY a JSON object with the key 'solution'. /no_think"""
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model, temperature=0.2, max_tokens=400,
            )
            raw = response.choices[0].message.content
            result = json.loads(self.extract_json(raw))
            return result.get('solution') or "A solution could not be generated."
        except:
            return "Solution generation temporarily unavailable."

    def fallback_free(self, description: str) -> dict:
        prompt = f"""You are an expert IT support triage assistant. For the ticket below, provide a short, descriptive category label (e.g., "Office Wi-Fi Connectivity Issue", "Database Credential Expiry", "Build Memory Exhaustion") and a step-by-step solution (under 150 words).

Return ONLY a valid JSON object. Do NOT include any markdown fences, explanations, or extra text. The JSON must have exactly two keys:
- "label": your short category label
- "solution": your step-by-step solution

Ticket: {description} /no_think"""
        for attempt in range(2):
            try:
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model, temperature=0.1, max_tokens=500,
                )
                raw = response.choices[0].message.content
                result = json.loads(self.extract_json(raw))
                label = result.get("label", "").strip()
                solution = result.get("solution") or "A solution could not be generated."
                if label:
                    return {"label": label, "solution": solution}
            except:
                if attempt == 1:
                    return {"label": "Uncategorised / Rare Issues",
                            "solution": "Unable to generate solution – please check the ticket manually."}
        return {"label": "Uncategorised / Rare Issues",
                "solution": "Unable to generate solution – please check the ticket manually."}