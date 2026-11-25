import os
from dataclasses import dataclass
from google import genai
from google.genai import types
from openai import OpenAI


@dataclass(frozen=True)
class LLMResponse:
    provider: str
    model: str
    raw_text: str


class UnifiedLLMClient:
    """Adapter for free-tier code generation APIs (Gemini, Groq, OpenRouter)."""

    SYSTEM_INSTRUCTION = (
        "You are an AI pair programmer. Complete the provided Python file cleanly. "
        "Return the complete valid Python file inside a single ```python code block "
        "without extra explanations."
    )

    def __init__(self, provider: str = "gemini", model: str | None = None, temperature: float = 0.7) -> None:
        self.provider = provider.lower()
        self.temperature = temperature

        if self.provider == "gemini":
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY is missing in environment.")
            self.model = model or "gemini-2.5-flash"
            self._gemini = genai.Client(api_key=api_key)

        elif self.provider == "groq":
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY is missing in environment.")
            self.model = model or "qwen-2.5-coder-32b"
            self._openai = OpenAI(api_key=api_key, base_url="[https://api.groq.com/openai/v1](https://api.groq.com/openai/v1)")

        elif self.provider == "openrouter":
            api_key = os.environ.get("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY is missing in environment.")
            self.model = model or "qwen/qwen-2.5-coder-32b-instruct:free"
            self._openai = OpenAI(api_key=api_key, base_url="[https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)")

        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def generate(self, prompt_code: str) -> LLMResponse:
        if self.provider == "gemini":
            resp = self._gemini.models.generate_content(
                model=self.model,
                contents=prompt_code,
                config=types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_INSTRUCTION,
                    temperature=self.temperature,
                ),
            )
            return LLMResponse(provider=self.provider, model=self.model, raw_text=resp.text or "")

        resp = self._openai.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": self.SYSTEM_INSTRUCTION},
                {"role": "user", "content": prompt_code},
            ],
        )
        content = resp.choices[0].message.content or ""
        return LLMResponse(provider=self.provider, model=self.model, raw_text=content)
