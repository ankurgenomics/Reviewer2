"""Tests for the MCP server's tool implementations.

These exercise ``_get_evidence_impl``/``_review_variant_impl`` directly rather than
through a real MCP session — they're plain top-level functions specifically so they
can be unit-tested without the optional 'mcp' extra installed (CI's default `uv sync
--extra dev` doesn't include it).
"""

from __future__ import annotations

import json

import pytest
from mcp_server.server import _get_evidence_impl, _review_variant_impl

# The BRCA1 fixture case bundled in eval/fixtures/evidence.json.
_BRCA1 = {"chrom": "17", "pos": 43093464, "ref": "A", "alt": "T", "gene": "BRCA1"}


def test_get_evidence_returns_fixture_evidence(monkeypatch):
    monkeypatch.delenv("REVIEWER2_EVIDENCE_PROVIDER", raising=False)
    raw = _get_evidence_impl(**_BRCA1)
    items = json.loads(raw)
    assert items
    assert any(item["source"] == "VEP" for item in items)
    assert all("source_quote" in item for item in items)


def test_get_evidence_respects_evidence_provider_env_var(monkeypatch):
    """Regression test for the env-var-ignoring bug.

    ``get_evidence`` used to call ``get_evidence_provider()`` with no argument,
    which always resolved to the fixture provider — silently ignoring
    ``REVIEWER2_EVIDENCE_PROVIDER=live`` even with the extra installed. Since the
    live provider's fetch methods are still v1.1 stubs, switching to "live" here
    must now return an empty (not fixture) result instead of quietly serving
    fixture data.
    """
    pytest.importorskip("httpx")
    monkeypatch.setenv("REVIEWER2_EVIDENCE_PROVIDER", "live")
    raw = _get_evidence_impl(**_BRCA1)
    assert json.loads(raw) == []  # live provider is an honest no-op stub in v1


def test_review_variant_tool_accepts_snake_case_proposed_classification():
    """Regression test: the same input the broken README quick-start used.

    Previously ``ACMGClassification(proposed_classification)`` crashed on
    "uncertain_significance"; the tool now routes through
    ``ACMGClassification.parse``.
    """
    raw = _review_variant_impl(**_BRCA1, proposed_classification="uncertain_significance")
    dossier = json.loads(raw)
    assert dossier["independent_classification"] == "Pathogenic"
    assert dossier["request"]["proposed_classification"] == "Uncertain significance"


def test_review_variant_tool_without_proposed_classification():
    raw = _review_variant_impl(**_BRCA1)
    dossier = json.loads(raw)
    assert dossier["request"]["proposed_classification"] is None
