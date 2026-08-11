"""Tests for the evidence provider factory."""

from __future__ import annotations

import pytest

from reviewer2.evidence import (
    FixtureEvidenceProvider,
    LiveEvidenceProvider,
    get_evidence_provider,
)


def test_defaults_to_fixtures_when_env_unset(monkeypatch):
    monkeypatch.delenv("REVIEWER2_EVIDENCE_PROVIDER", raising=False)
    assert isinstance(get_evidence_provider(), FixtureEvidenceProvider)


def test_reads_env_var_when_name_not_given_explicitly(monkeypatch):
    """Regression test: every caller must see the same provider choice.

    ``mcp_server/server.py``'s ``get_evidence`` tool used to call
    ``get_evidence_provider()`` with no argument, which used to default to the
    "fixtures" literal regardless of ``REVIEWER2_EVIDENCE_PROVIDER`` —
    silently ignoring the env var that ``pipeline.py`` respected. The env-var
    read now lives inside the factory itself so every call site (pipeline,
    CLI, MCP server) picks it up automatically.
    """
    pytest.importorskip("httpx")  # LiveEvidenceProvider needs the 'live' extra
    monkeypatch.setenv("REVIEWER2_EVIDENCE_PROVIDER", "live")
    assert isinstance(get_evidence_provider(), LiveEvidenceProvider)


def test_explicit_name_overrides_env_var(monkeypatch):
    pytest.importorskip("httpx")
    monkeypatch.setenv("REVIEWER2_EVIDENCE_PROVIDER", "live")
    assert isinstance(get_evidence_provider("fixtures"), FixtureEvidenceProvider)
