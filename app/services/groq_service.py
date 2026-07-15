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
        transcript: str
    ):

        prompt = f"""
You are an expert AI Call Quality Analyst.

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
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content.strip()

        # Remove markdown code fences if present
        if content.startswith("```"):
            lines = content.splitlines()

            # Remove first line (``` or ```json)
            lines = lines[1:]

            # Remove last line if it is ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            content = "\n".join(lines)

        return json.loads(content)