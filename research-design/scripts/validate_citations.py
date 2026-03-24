#!/usr/bin/env python3
"""
Citation validation pipeline for research proposal output.

Reads a markdown file, extracts DOIs, arxiv IDs, and URLs, then verifies
each against external APIs (CrossRef, arxiv, HTTP HEAD). Reports invalid
citations and duplicates.

This is the key anti-hallucination tool -- it verifies every citation in
generated output files is real.

Original concept and design adapted from:
  claude-scientific-skills (https://github.com/anthropics/claude-scientific-skills)
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Tuple

try:
    import requests
except ImportError:
    print(
        "Error: 'requests' library is required. Install it with:\n"
        "  uv sync",
        file=sys.stderr,
    )
    sys.exit(1)


# --- Extraction ---

DOI_PATTERN = re.compile(r"10\.\d{4,9}/[^\s\)\]\}>,;\"']+")
ARXIV_PATTERN = re.compile(r"\b(\d{4}\.\d{4,5}(?:v\d+)?)\b")
URL_PATTERN = re.compile(
    r"https?://[^\s\)\]\}>,;\"'<]+"
)


def extract_dois(text: str) -> List[str]:
    """Extract DOIs from text."""
    matches = DOI_PATTERN.findall(text)
    # Strip trailing punctuation that may have been captured
    cleaned = []
    for doi in matches:
        doi = doi.rstrip(".")
        cleaned.append(doi)
    return cleaned


def extract_arxiv_ids(text: str) -> List[str]:
    """Extract arxiv IDs from text."""
    return ARXIV_PATTERN.findall(text)


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text, excluding DOI and arxiv URLs."""
    matches = URL_PATTERN.findall(text)
    filtered = []
    for url in matches:
        # Skip DOI URLs (already handled via DOI extraction)
        if "doi.org/" in url:
            continue
        # Skip arxiv abstract/pdf URLs (already handled via arxiv ID extraction)
        if "arxiv.org/abs/" in url or "arxiv.org/pdf/" in url:
            continue
        filtered.append(url)
    return filtered


# --- Verification ---


def verify_doi(doi: str, timeout: int = 10) -> Dict[str, Any]:
    """Verify a DOI via doi.org HEAD request and CrossRef metadata API."""
    result = {"type": "doi", "id": doi, "valid": False, "details": {}}

    # Step 1: Check doi.org resolves
    try:
        resp = requests.head(
            f"https://doi.org/{doi}",
            allow_redirects=True,
            timeout=timeout,
        )
        result["details"]["doi_org_status"] = resp.status_code
        if resp.status_code >= 400:
            result["message"] = f"DOI does not resolve (HTTP {resp.status_code})"
            return result
    except requests.RequestException as e:
        result["message"] = f"DOI resolution failed: {e}"
        return result

    # Step 2: Check CrossRef metadata
    try:
        resp = requests.get(
            f"https://api.crossref.org/works/{doi}",
            timeout=timeout,
            headers={"Accept": "application/json"},
        )
        result["details"]["crossref_status"] = resp.status_code
        if resp.status_code == 200:
            data = resp.json()
            message = data.get("message", {})
            result["details"]["title"] = (
                message.get("title", [""])[0] if message.get("title") else ""
            )
            result["valid"] = True
        else:
            # DOI resolved but no CrossRef metadata -- still mark as valid
            # since some DOIs are from publishers not in CrossRef
            result["valid"] = True
            result["details"]["note"] = "No CrossRef metadata (may be non-CrossRef DOI)"
    except requests.RequestException:
        # doi.org resolved, so DOI exists even if CrossRef is unreachable
        result["valid"] = True
        result["details"]["note"] = "CrossRef unreachable, but DOI resolves"

    return result


def verify_arxiv(arxiv_id: str, timeout: int = 10) -> Dict[str, Any]:
    """Verify an arxiv ID exists via the arxiv API."""
    result = {"type": "arxiv", "id": arxiv_id, "valid": False, "details": {}}

    try:
        resp = requests.get(
            f"http://export.arxiv.org/api/query?id_list={arxiv_id}",
            timeout=timeout,
        )
        result["details"]["api_status"] = resp.status_code
        if resp.status_code != 200:
            result["message"] = f"arxiv API returned HTTP {resp.status_code}"
            return result

        # Parse XML response
        root = ET.fromstring(resp.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        entries = root.findall("atom:entry", ns)
        if not entries:
            result["message"] = "No entry found in arxiv response"
            return result

        entry = entries[0]

        # Check if the entry is an error (arxiv returns an entry with
        # id "http://arxiv.org/api/errors#..." for invalid IDs)
        entry_id = entry.find("atom:id", ns)
        if entry_id is not None and "errors" in (entry_id.text or ""):
            result["message"] = "arxiv ID not found"
            return result

        title = entry.find("atom:title", ns)
        if title is not None:
            result["details"]["title"] = " ".join(title.text.strip().split())

        result["valid"] = True
    except requests.RequestException as e:
        result["message"] = f"arxiv API request failed: {e}"
    except ET.ParseError as e:
        result["message"] = f"Failed to parse arxiv API response: {e}"

    return result


def verify_url(url: str, timeout: int = 10) -> Dict[str, Any]:
    """Check URL accessibility via HEAD request."""
    result = {"type": "url", "id": url, "valid": False, "details": {}}

    try:
        resp = requests.head(
            url,
            allow_redirects=True,
            timeout=timeout,
            headers={"User-Agent": "ResearchValidator/1.0"},
        )
        result["details"]["status_code"] = resp.status_code
        if resp.status_code < 400:
            result["valid"] = True
        else:
            result["message"] = f"URL returned HTTP {resp.status_code}"
    except requests.RequestException as e:
        result["message"] = f"URL request failed: {e}"

    return result


# --- Duplicate Detection ---


def _normalize_title(title: str) -> str:
    """Normalize a title for comparison."""
    return re.sub(r"[^a-z0-9\s]", "", title.lower()).strip()


def detect_duplicates(
    results: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """Detect duplicate citations by DOI or similar title."""
    warnings = []

    # Check for duplicate DOIs
    doi_seen: Dict[str, int] = {}
    for i, r in enumerate(results):
        if r["type"] == "doi":
            doi = r["id"]
            if doi in doi_seen:
                warnings.append({
                    "type": "duplicate_doi",
                    "id": doi,
                    "severity": "warning",
                    "message": f"DOI appears multiple times",
                })
            else:
                doi_seen[doi] = i

    # Check for similar titles
    titles: List[Tuple[int, str, str]] = []
    for i, r in enumerate(results):
        title = r.get("details", {}).get("title", "")
        if title:
            titles.append((i, title, _normalize_title(title)))

    for i in range(len(titles)):
        for j in range(i + 1, len(titles)):
            idx_a, title_a, norm_a = titles[i]
            idx_b, title_b, norm_b = titles[j]
            # Simple similarity: check if one is a substring of the other
            # or if they share >80% of words
            if not norm_a or not norm_b:
                continue
            if norm_a == norm_b:
                warnings.append({
                    "type": "duplicate_title",
                    "id": f"{results[idx_a]['type']}:{results[idx_a]['id']} vs {results[idx_b]['type']}:{results[idx_b]['id']}",
                    "severity": "warning",
                    "message": f"Very similar titles: '{title_a[:60]}...' and '{title_b[:60]}...'",
                })
                continue
            words_a = set(norm_a.split())
            words_b = set(norm_b.split())
            if words_a and words_b:
                overlap = len(words_a & words_b) / max(len(words_a), len(words_b))
                if overlap > 0.8:
                    warnings.append({
                        "type": "similar_title",
                        "id": f"{results[idx_a]['type']}:{results[idx_a]['id']} vs {results[idx_b]['type']}:{results[idx_b]['id']}",
                        "severity": "info",
                        "message": f"Possibly similar titles ({overlap:.0%} word overlap)",
                    })

    return warnings


# --- Report Generation ---


def validate_file(filepath: str, timeout: int = 10) -> Dict[str, Any]:
    """Validate all citations in a markdown file."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    dois = extract_dois(text)
    arxiv_ids = extract_arxiv_ids(text)
    urls = extract_urls(text)

    results = []
    errors = []

    # Verify DOIs
    for doi in dois:
        r = verify_doi(doi, timeout=timeout)
        results.append(r)
        if not r["valid"]:
            errors.append({
                "type": "invalid_doi",
                "id": doi,
                "severity": "error",
                "message": r.get("message", "DOI validation failed"),
            })

    # Verify arxiv IDs
    for arxiv_id in arxiv_ids:
        r = verify_arxiv(arxiv_id, timeout=timeout)
        results.append(r)
        if not r["valid"]:
            errors.append({
                "type": "invalid_arxiv",
                "id": arxiv_id,
                "severity": "error",
                "message": r.get("message", "arxiv validation failed"),
            })

    # Verify URLs
    for url in urls:
        r = verify_url(url, timeout=timeout)
        results.append(r)
        if not r["valid"]:
            errors.append({
                "type": "invalid_url",
                "id": url,
                "severity": "warning",
                "message": r.get("message", "URL validation failed"),
            })

    # Detect duplicates
    warnings = detect_duplicates(results)

    valid_count = sum(1 for r in results if r["valid"])
    invalid_count = sum(1 for r in results if not r["valid"])

    report = {
        "file": filepath,
        "summary": {
            "total_citations": len(results),
            "dois_found": len(dois),
            "arxiv_ids_found": len(arxiv_ids),
            "urls_found": len(urls),
            "valid": valid_count,
            "invalid": invalid_count,
        },
        "errors": errors,
        "warnings": warnings,
        "details": results,
    }

    return report


def format_text_report(report: Dict[str, Any]) -> str:
    """Format validation report as human-readable text."""
    lines = []
    summary = report["summary"]

    lines.append(f"Citation Validation Report: {report['file']}")
    lines.append("=" * 60)
    lines.append(f"Total citations found: {summary['total_citations']}")
    lines.append(f"  DOIs: {summary['dois_found']}")
    lines.append(f"  arxiv IDs: {summary['arxiv_ids_found']}")
    lines.append(f"  URLs: {summary['urls_found']}")
    lines.append(f"Valid: {summary['valid']}")
    lines.append(f"Invalid: {summary['invalid']}")
    lines.append("")

    if report["errors"]:
        lines.append("ERRORS:")
        lines.append("-" * 40)
        for err in report["errors"]:
            lines.append(f"  [{err['severity'].upper()}] {err['type']}: {err['id']}")
            lines.append(f"    {err['message']}")
        lines.append("")

    if report["warnings"]:
        lines.append("WARNINGS:")
        lines.append("-" * 40)
        for warn in report["warnings"]:
            lines.append(f"  [{warn['severity'].upper()}] {warn['type']}: {warn['id']}")
            lines.append(f"    {warn['message']}")
        lines.append("")

    status = "PASS" if summary["invalid"] == 0 else "FAIL"
    lines.append(f"Result: {status}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate citations in a markdown file against external APIs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s paper.md
  %(prog)s paper.md --output text
  %(prog)s paper.md --output json --timeout 15

Exit codes:
  0 - All citations valid
  1 - One or more citations invalid
        """,
    )
    parser.add_argument(
        "markdown_file", type=str, help="Path to markdown file containing citations"
    )
    parser.add_argument(
        "--output", type=str, choices=["json", "text"], default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--timeout", type=int, default=10,
        help="HTTP request timeout in seconds (default: 10)",
    )

    args = parser.parse_args()

    report = validate_file(args.markdown_file, timeout=args.timeout)

    if args.output == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(format_text_report(report))

    # Exit code: 0 if all valid, 1 if any invalid
    sys.exit(0 if report["summary"]["invalid"] == 0 else 1)


if __name__ == "__main__":
    main()
