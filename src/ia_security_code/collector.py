import time
from pathlib import Path
from typing import Protocol

from ia_security_code.audit_logger import GenerationAuditEvent, GovernanceLogger
from ia_security_code.code_sanitizer import extract_python_code, is_valid_syntax
from ia_security_code.llm_client import LLMResponse
from ia_security_code.prompt_loader import PromptLoader


class CodeGeneratorProtocol(Protocol):
    def generate(self, prompt_code: str) -> LLMResponse: ...


class ExperimentCollector:
    def __init__(
        self,
        prompt_loader: PromptLoader,
        llm_client: CodeGeneratorProtocol,
        audit_logger: GovernanceLogger,
        output_dir: Path | str = Path("data/raw_samples"),
        delay_seconds: float = 0.0,
    ) -> None:
        self.prompt_loader = prompt_loader
        self.llm_client = llm_client
        self.audit_logger = audit_logger
        self.output_dir = Path(output_dir)
        self.delay_seconds = delay_seconds

    def run_collection(self, run_id: str, samples_per_scenario: int = 5) -> dict[str, int]:
        scenarios = self.prompt_loader.list_scenarios()
        stats = {"total_requested": 0, "valid_syntax_count": 0, "invalid_syntax_count": 0}

        for scenario in scenarios:
            scenario_out_dir = self.output_dir / scenario.cwe_id
            scenario_out_dir.mkdir(parents=True, exist_ok=True)

            for idx in range(1, samples_per_scenario + 1):
                stats["total_requested"] += 1
                response = self.llm_client.generate(scenario.content)
                clean_code = extract_python_code(response.raw_text)
                valid = is_valid_syntax(clean_code)

                output_file_str: str | None = None
                if valid:
                    stats["valid_syntax_count"] += 1
                    safe_model = response.model.replace("/", "_").replace(":", "_")
                    file_path = scenario_out_dir / f"{scenario.variant}_{safe_model}_{idx:02d}.py"
                    file_path.write_text(clean_code + "\n", encoding="utf-8")
                    output_file_str = str(file_path)
                else:
                    stats["invalid_syntax_count"] += 1

                self.audit_logger.record_generation(
                    GenerationAuditEvent(
                        run_id=run_id,
                        cwe_id=scenario.cwe_id,
                        variant=scenario.variant,
                        provider=response.provider,
                        model=response.model,
                        prompt_text=scenario.content,
                        generated_code=clean_code,
                        is_valid_syntax=valid,
                        sample_index=idx,
                        output_file=output_file_str,
                    )
                )

                if self.delay_seconds > 0:
                    time.sleep(self.delay_seconds)

        return stats
