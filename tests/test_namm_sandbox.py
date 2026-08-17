"""Tests for NAMM sandbox delegation."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from eia.namm import CERTIFICATE_SCHEMA, NammAdapter, SandboxCertificate


def test_sandbox_certificate_schema_has_required_fields() -> None:
    assert "experiment_id" in CERTIFICATE_SCHEMA["required"]
    assert "status" in CERTIFICATE_SCHEMA["required"]


def test_run_sandbox_not_installed(tmp_path: Path) -> None:
    adapter = NammAdapter(namm_root=tmp_path / "missing-namm", log_dir=tmp_path / "logs")
    cert = adapter.run_sandbox("NAMM-2026-013")
    assert cert.status == "not_installed"
    assert cert.error is not None
    assert (tmp_path / "logs" / "sandbox-NAMM-2026-013.json").exists()


def test_run_sandbox_success_with_mock() -> None:
    adapter = NammAdapter(namm_root=Path("C:/fake/namm"), log_dir=Path("traces/test_namm"))

    cert_json = (
        '{"experiment_id":"NAMM-2026-013","protocol":"cognitive-antigravity-v1",'
        '"status":"VERIFIED","d_med_lift":"7440.5%","pipeline_compliance":"100.0%",'
        '"z_star_mean":0.744}'
    )
    result_json = (
        '{"experiment_id":"NAMM-2026-013","hypothesis_confirmed":true,'
        '"metrics_summary":{"d_med_lift_percent":7440.5}}'
    )

    with patch.object(Path, "exists", return_value=True):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
            with patch("pathlib.Path.read_text") as mock_read:
                mock_read.side_effect = [result_json, cert_json]

                cert = adapter.run_sandbox("NAMM-2026-013")

    assert cert.status == "verified"
    assert cert.hypothesis_confirmed is True
    assert cert.metrics.get("d_med_lift_percent") == 7440.5
