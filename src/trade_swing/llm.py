import logging

LOGGER = logging.getLogger(__name__)


class TradeBriefingService:
    """Optional Groq narrative layer; scanner decisions remain deterministic."""

    def __init__(self, api_key: str | None, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def explain(self, rows: list[dict]) -> str:
        if not self.api_key:
            return "Add GROQ_API_KEY to generate an AI market brief. The scores above are rule-based."
        try:
            from groq import Groq

            client = Groq(api_key=self.api_key)
            completion = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": f"Summarize these swing scanner results in 5 concise bullets. Do not give financial advice: {rows}"}],
                temperature=0.2, max_completion_tokens=600, stream=False,
            )
            return completion.choices[0].message.content or "No briefing returned."
        except Exception as exc:
            LOGGER.exception("Groq briefing failed")
            return f"AI briefing unavailable: {exc}"
