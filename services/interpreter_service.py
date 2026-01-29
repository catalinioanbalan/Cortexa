from openai import OpenAI

from config import settings


class InterpreterService:
    TONES = {
        "insightful": "Provide deep, thoughtful analysis",
        "supportive": "Be warm, encouraging, and validating",
        "analytical": "Be logical, structured, and objective",
        "creative": "Be imaginative and explore possibilities",
        "direct": "Be concise and straightforward"
    }

    STYLES = {
        "concise": "Keep responses brief and focused",
        "detailed": "Provide thorough explanations",
        "bullet_points": "Use bullet points for clarity",
        "narrative": "Use flowing, narrative prose"
    }

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.CHAT_MODEL

    def interpret(
        self,
        user_input: str,
        tone: str = "insightful",
        style: str = "concise",
        context: str | None = None
    ) -> dict:
        """Interpret user input with specified tone and style."""
        system_prompt = self._build_system_prompt(tone, style)
        user_prompt = self._build_user_prompt(user_input, context)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )

        return {
            "interpretation": response.choices[0].message.content,
            "tone": tone,
            "style": style
        }

    def _build_system_prompt(self, tone: str, style: str) -> str:
        tone_instruction = self.TONES.get(tone, self.TONES["insightful"])
        style_instruction = self.STYLES.get(style, self.STYLES["concise"])

        return f"""You are an interpreter that helps users understand and explore their thoughts, ideas, and experiences.

Tone: {tone_instruction}
Style: {style_instruction}

Provide meaningful interpretation that helps the user gain clarity and insight."""

    def _build_user_prompt(self, user_input: str, context: str | None) -> str:
        if context:
            return f"Context: {context}\n\nInterpret this: {user_input}"
        return f"Interpret this: {user_input}"


interpreter_service = InterpreterService()
