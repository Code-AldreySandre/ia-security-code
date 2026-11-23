import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class GenerationAuditEvent:
    run_id: str
    cwe_id: str
    variant: str
    provider: str
    model: str
    prompt_text: str
    generated_code: str
    is_valid_syntax: bool
    sample_index: int
    output_file: str | None = None


class GovernanceLogger:
    """Append-only JSONL audit logger for AI code provenance and security governance."""

    def __init__(self, log_path: Path | str = Path("data/audit/governance_log.jsonl")) -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _write_entry(self, entry: dict) -> None:
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def record_generation(self, event: GenerationAuditEvent) -> str:
        code_hash = _sha256(event.generated_code)
        entry = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "event_type": "CODE_GENERATION",
            "run_id": event.run_id,
            "cwe_id": event.cwe_id,
            "variant": event.variant,
            "sample_index": event.sample_index,
            "provider": event.provider,
            "model": event.model,
            "prompt_sha256": _sha256(event.prompt_text),
            "code_sha256": code_hash,
            "is_valid_syntax": event.is_valid_syntax,
            "output_file": event.output_file,
        }
        self._write_entry(entry)
        return code_hash

    def record_security_scan(
        self,
        run_id: str,
        sample_file: str,
        code_sha256: str,
        scanner: str,
        is_vulnerable: bool,
        detected_cwes: list[str],
        severity: str = "NONE",
    ) -> None:
        entry = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "event_type": "SECURITY_GATE_SCAN",
            "run_id": run_id,
            "sample_file": sample_file,
            "code_sha256": code_sha256,
            "scanner": scanner,
            "is_vulnerable": is_vulnerable,
            "detected_cwes": detected_cwes,
            "severity": severity,
            "gate_decision": "BLOCKED" if is_vulnerable else "APPROVED",
        }
        self._write_entry(entry)