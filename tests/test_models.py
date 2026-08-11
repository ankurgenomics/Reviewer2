"""Tests for the typed domain model — currently just the lenient classification parser."""

from __future__ import annotations

import pytest

from reviewer2.models import ACMGClassification


def test_parse_accepts_canonical_value():
    assert ACMGClassification.parse("Pathogenic") is ACMGClassification.PATHOGENIC
    assert ACMGClassification.parse("Uncertain significance") is ACMGClassification.VUS


def test_parse_accepts_snake_case():
    """Regression test: the README's own quick-start example uses this form.

    ``uv run reviewer2 review ... --proposed uncertain_significance`` previously
    crashed with a bare ``ValueError`` because ``ACMGClassification(raw)`` only
    accepts the exact canonical string. Both the CLI and the MCP server's
    ``review_variant_tool`` route free-form input through here.
    """
    assert ACMGClassification.parse("uncertain_significance") is ACMGClassification.VUS
    assert ACMGClassification.parse("likely_pathogenic") is ACMGClassification.LIKELY_PATHOGENIC
    assert ACMGClassification.parse("likely_benign") is ACMGClassification.LIKELY_BENIGN


def test_parse_is_case_and_spacing_insensitive():
    assert ACMGClassification.parse("PATHOGENIC") is ACMGClassification.PATHOGENIC
    assert ACMGClassification.parse("likely pathogenic") is ACMGClassification.LIKELY_PATHOGENIC
    assert ACMGClassification.parse("Likely-Benign") is ACMGClassification.LIKELY_BENIGN
    assert ACMGClassification.parse("  benign  ") is ACMGClassification.BENIGN


def test_parse_raises_helpful_error_on_garbage():
    with pytest.raises(ValueError, match="not a valid ACMGClassification"):
        ACMGClassification.parse("definitely_not_a_call")
