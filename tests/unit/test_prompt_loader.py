import pytest
from pathlib import Path
from ia_security_code.prompt_loader import PromptLoader, PromptScenario


@pytest.fixture
def temp_prompts_dir(tmp_path: Path) -> Path:
    cwe_dir = tmp_path / "cwe_89_sqli"
    cwe_dir.mkdir()
    (cwe_dir / "neutral.py.tpl").write_text("# neutral prompt\ndef get_user(uid):\n", encoding="utf-8")
    (cwe_dir / "contaminated.py.tpl").write_text("# contaminated prompt\ndef get_user(uid):\n", encoding="utf-8")
    (cwe_dir / "hardened.py.tpl").write_text("# hardened prompt\ndef get_user(uid):\n", encoding="utf-8")
    return tmp_path


def test_list_scenarios_discovers_all_templates(temp_prompts_dir: Path):
    loader = PromptLoader(prompts_dir=temp_prompts_dir)
    scenarios = loader.list_scenarios()

    assert len(scenarios) == 3
    variants = {s.variant for s in scenarios}
    assert variants == {"neutral", "contaminated", "hardened"}
    assert all(s.cwe_id == "cwe_89_sqli" for s in scenarios)


def test_load_specific_scenario_returns_content(temp_prompts_dir: Path):
    loader = PromptLoader(prompts_dir=temp_prompts_dir)
    scenario = loader.get_scenario(cwe_id="cwe_89_sqli", variant="contaminated")

    assert isinstance(scenario, PromptScenario)
    assert "# contaminated prompt" in scenario.content


def test_get_nonexistent_scenario_raises_file_not_found(temp_prompts_dir: Path):
    loader = PromptLoader(prompts_dir=temp_prompts_dir)
    with pytest.raises(FileNotFoundError):
        loader.get_scenario(cwe_id="cwe_999", variant="neutral")