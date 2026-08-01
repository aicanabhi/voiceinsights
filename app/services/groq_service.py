import json

from groq import Groq

from app.core.config import settings


class GroqService:

    def __init__(self):
        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )

    def analyze_transcript(
        self,
        transcript: str,
        system_prompt: str,
        rules: dict
    ):

        prompt = f"""
You are an AI Call Quality Analyst.

Follow these instructions carefully.

SYSTEM PROMPT:
{system_prompt}

RULES:
{json.dumps(rules, indent=2)}

Analyze the following customer support call transcript.

Return ONLY valid JSON.

Do not wrap the JSON in markdown.

Do not use ```json or ```.

Do not add any explanation.

JSON format:

{{
    "summary":"",
    "sentiment":"",
    "compliance_score":0,
    "professionalism_score":0,
    "empathy_score":0,
    "overall_score":0,
    "greeting_followed":true,
    "closing_followed":true,
    "violations":"",
    "recommendations":"",
    "ai_feedback":""
}}

Transcript:

{transcript}
"""

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI Call Quality Analyst."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content.strip()

        if content.startswith("```"):
            lines = content.splitlines()
            lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            content = "\n".join(lines)

        return json.loads(content)