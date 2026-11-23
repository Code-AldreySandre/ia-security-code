from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PromptScenario:
    cwe_id: str
    variant: str
    content: str
    source_path: Path


class PromptLoader:
    def __init__(self, prompts_dir: Path | str = Path("prompts")) -> None:
        self.prompts_dir = Path(prompts_dir)

    def list_scenarios(self) -> list[PromptScenario]:
        scenarios: list[PromptScenario] = []
        if not self.prompts_dir.exists():
            return scenarios

        for cwe_dir in sorted(p for p in self.prompts_dir.iterdir() if p.is_dir()):
            for tpl_file in sorted(cwe_dir.glob("*.py.tpl")):
                variant = tpl_file.name.removesuffix(".py.tpl")
                scenarios.append(
                    PromptScenario(
                        cwe_id=cwe_dir.name,
                        variant=variant,
                        content=tpl_file.read_text(encoding="utf-8"),
                        source_path=tpl_file,
                    )
                )
        return scenarios

    def get_scenario(self, cwe_id: str, variant: str) -> PromptScenario:
        tpl_path = self.prompts_dir / cwe_id / f"{variant}.py.tpl"
        if not tpl_path.exists():
            raise FileNotFoundError(f"Template not found: {tpl_path}")
        return PromptScenario(
            cwe_id=cwe_id,
            variant=variant,
            content=tpl_path.read_text(encoding="utf-8"),
            source_path=tpl_path,
        )