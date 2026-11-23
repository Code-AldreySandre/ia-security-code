import json
from pathlib import Path
from ia_security_code.audit_logger import GovernanceLogger, GenerationAuditEvent


def test_log_generation_event_appends_valid_jsonl(tmp_path: Path):
    log_file = tmp_path / "governance_log.jsonl"
    logger = GovernanceLogger(log_path=log_file)

    event = GenerationAuditEvent(
        run_id="exp-001",
        cwe_id="cwe_89_sqli",
        variant="contaminated",
        provider="groq",
        model="qwen-2.5-coder-32b",
        prompt_text="def login(user): ...",
        generated_code="cursor.execute('SELECT * FROM u WHERE id=' + user)",
        is_valid_syntax=True,
        sample_index=1,
    )
    logger.record_generation(event)

    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1

    payload = json.loads(lines[0])
    assert payload["event_type"] == "CODE_GENERATION"
    assert payload["run_id"] == "exp-001"
    assert payload["cwe_id"] == "cwe_89_sqli"
    assert payload["variant"] == "contaminated"
    assert payload["model"] == "qwen-2.5-coder-32b"
    assert payload["is_valid_syntax"] is True
    assert len(payload["prompt_sha256"]) == 64
    assert len(payload["code_sha256"]) == 64
    assert "timestamp_utc" in payload


def test_log_security_verdict_links_to_code_hash(tmp_path: Path):
    log_file = tmp_path / "governance_log.jsonl"
    logger = GovernanceLogger(log_path=log_file)

    logger.record_security_scan(
        run_id="exp-001",
        sample_file="data/raw_samples/cwe_89_sqli/contaminated_01.py",
        code_sha256="a" * 64,
        scanner="bandit",
        is_vulnerable=True,
        detected_cwes=["CWE-89"],
        severity="HIGH",
    )

    payload = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert payload["event_type"] == "SECURITY_GATE_SCAN"
    assert payload["is_vulnerable"] is True
    assert payload["detected_cwes"] == ["CWE-89"]
    assert payload["gate_decision"] == "BLOCKED"