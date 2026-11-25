import json
from pathlib import Path
from unittest.mock import MagicMock

from ia_security_code.audit_logger import GovernanceLogger
from ia_security_code.collector import ExperimentCollector
from ia_security_code.llm_client import LLMResponse
from ia_security_code.prompt_loader import PromptLoader


def test_collector_saves_valid_samples_and_logs_governance_events(tmp_path: Path):
    # 1. Setup de prompts fictícios
    prompts_dir = tmp_path / "prompts"
    cwe_dir = prompts_dir / "cwe_89_sqli"
    cwe_dir.mkdir(parents=True)
    (cwe_dir / "neutral.py.tpl").write_text("def login(user):\n    pass\n", encoding="utf-8")

    # 2. Mock do cliente LLM devolvendo 1 resposta válida (em markdown) e 1 com erro de sintaxe
    mock_client = MagicMock()
    mock_client.generate.side_effect = [
        LLMResponse(
            provider="groq",
            model="qwen-2.5-coder-32b",
            raw_text="```python\ndef login(user):\n    return f'SELECT * FROM u WHERE id={user}'\n```",
        ),
        LLMResponse(
            provider="groq",
            model="qwen-2.5-coder-32b",
            raw_text="```python\ndef login(user\n    return 'broken syntax'\n```",
        ),
    ]

    output_dir = tmp_path / "raw_samples"
    audit_log = tmp_path / "audit" / "governance_log.jsonl"

    collector = ExperimentCollector(
        prompt_loader=PromptLoader(prompts_dir=prompts_dir),
        llm_client=mock_client,
        audit_logger=GovernanceLogger(log_path=audit_log),
        output_dir=output_dir,
    )

    summary = collector.run_collection(run_id="run-test-01", samples_per_scenario=2)

    # Verifica estatísticas retornadas
    assert summary["total_requested"] == 2
    assert summary["valid_syntax_count"] == 1
    assert summary["invalid_syntax_count"] == 1

    # Apenas o arquivo válido deve ser salvo em raw_samples para análise SAST
    saved_files = list((output_dir / "cwe_89_sqli").glob("*.py"))
    assert len(saved_files) == 1
    assert "SELECT * FROM u" in saved_files[0].read_text(encoding="utf-8")

    # Ambos os eventos (válido e descartado) devem constar no log de governança
    log_entries = [json.loads(line) for line in audit_log.read_text(encoding="utf-8").splitlines()]
    assert len(log_entries) == 2
    assert log_entries[0]["is_valid_syntax"] is True
    assert log_entries[0]["output_file"] is not None
    assert log_entries[1]["is_valid_syntax"] is False
    assert log_entries[1]["output_file"] is None
