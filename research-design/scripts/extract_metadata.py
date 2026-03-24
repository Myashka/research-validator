#!/usr/bin/env python3
"""
Metadata extraction for scholarly identifiers.

Given a DOI, PMID, arxiv ID, or URL, queries the appropriate API
(CrossRef, PubMed E-utilities, arxiv, DataCite) and returns structured
bibliographic metadata. Supports batch mode and BibTeX output.

Original concept and design adapted from:
  claude-scientific-skills (https://github.com/anthropics/claude-scientific-skills)
"""

import argparse
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

try:
    import requests
except ImportError:
    print(
        "Error: 'requests' library is required. Install it with:\n"
        "  uv sync",
        file=sys.stderr,
    )
    sys.exit(1)

USER_AGENT = "ResearchValidator/1.0 (metadata extraction)"
REQUEST_TIMEOUT = 15

# --- Identifier Detection ---

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
ARXIV_RE = re.compile(r"^(\d{4}\.\d{4,5})(v\d+)?$")
PMID_RE = re.compile(r"^(\d{6,9})$")
URL_RE = re.compile(r"^https?://")


def classify_identifier(raw: str) -> tuple:
    """Classify an identifier string and return (type, normalized_id)."""
    ident = raw.strip()

    # DOI (with or without URL prefix)
    if ident.startswith("https://doi.org/"):
        return ("doi", ident[len("https://doi.org/"):])
    if ident.startswith("http://doi.org/"):
        return ("doi", ident[len("http://doi.org/"):])
    if ident.lower().startswith("doi:"):
        return ("doi", ident[4:].strip())
    if DOI_RE.match(ident):
        return ("doi", ident)

    # arxiv (with or without prefix)
    if ident.lower().startswith("arxiv:"):
        ident = ident[6:]
    m = ARXIV_RE.match(ident)
    if m:
        return ("arxiv", ident)

    # PMID (with or without prefix)
    if ident.lower().startswith("pmid:"):
        return ("pmid", ident[5:].strip())
    if PMID_RE.match(ident):
        return ("pmid", ident)

    # URL
    if URL_RE.match(ident):
        # Check for arxiv URL
        arxiv_url = re.search(r"arxiv\.org/abs/(\d{4}\.\d{4,5}(?:v\d+)?)", ident)
        if arxiv_url:
            return ("arxiv", arxiv_url.group(1))
        return ("url", ident)

    return ("unknown", ident)


# --- API Clients ---


def fetch_crossref(doi: str) -> Optional[Dict[str, Any]]:
    """Fetch metadata from CrossRef API for a DOI."""
    try:
        resp = requests.get(
            f"https://api.crossref.org/works/{doi}",
            headers={"Accept": "application/json", "User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            return None
        msg = resp.json().get("message", {})

        authors = []
        for a in msg.get("author", []):
            name = f"{a.get('given', '')} {a.get('family', '')}".strip()
            if name:
                authors.append(name)

        title = msg.get("title", [""])[0] if msg.get("title") else ""
        container = msg.get("container-title", [""])[0] if msg.get("container-title") else ""

        # Year from published-print or published-online or issued
        year = None
        for date_field in ["published-print", "published-online", "issued"]:
            parts = msg.get(date_field, {}).get("date-parts", [[]])
            if parts and parts[0] and parts[0][0]:
                year = parts[0][0]
                break

        return {
            "source": "crossref",
            "identifier_type": "doi",
            "identifier": doi,
            "title": title,
            "authors": authors,
            "year": year,
            "journal": container,
            "volume": msg.get("volume", ""),
            "issue": msg.get("issue", ""),
            "pages": msg.get("page", ""),
            "abstract": msg.get("abstract", ""),
            "doi": doi,
            "url": msg.get("URL", f"https://doi.org/{doi}"),
            "type": msg.get("type", ""),
        }
    except requests.RequestException:
        return None


def fetch_datacite(doi: str) -> Optional[Dict[str, Any]]:
    """Fetch metadata from DataCite API (for dataset DOIs)."""
    try:
        resp = requests.get(
            f"https://api.datacite.org/dois/{doi}",
            headers={"Accept": "application/json", "User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            return None
        attrs = resp.json().get("data", {}).get("attributes", {})

        authors = []
        for c in attrs.get("creators", []):
            name = c.get("name", "")
            if not name and c.get("givenName"):
                name = f"{c.get('givenName', '')} {c.get('familyName', '')}".strip()
            if name:
                authors.append(name)

        titles = attrs.get("titles", [])
        title = titles[0].get("title", "") if titles else ""

        year = attrs.get("publicationYear")
        descriptions = attrs.get("descriptions", [])
        abstract = descriptions[0].get("description", "") if descriptions else ""

        return {
            "source": "datacite",
            "identifier_type": "doi",
            "identifier": doi,
            "title": title,
            "authors": authors,
            "year": year,
            "journal": attrs.get("publisher", ""),
            "volume": "",
            "issue": "",
            "pages": "",
            "abstract": abstract,
            "doi": doi,
            "url": f"https://doi.org/{doi}",
            "type": attrs.get("types", {}).get("resourceTypeGeneral", ""),
        }
    except requests.RequestException:
        return None


def fetch_doi(doi: str) -> Optional[Dict[str, Any]]:
    """Try CrossRef first, then DataCite for DOI metadata."""
    result = fetch_crossref(doi)
    if result:
        return result
    return fetch_datacite(doi)


def fetch_arxiv(arxiv_id: str) -> Optional[Dict[str, Any]]:
    """Fetch metadata from arxiv API."""
    try:
        resp = requests.get(
            f"http://export.arxiv.org/api/query?id_list={arxiv_id}",
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            return None

        root = ET.fromstring(resp.text)
        ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

        entries = root.findall("atom:entry", ns)
        if not entries:
            return None

        entry = entries[0]

        # Check for error entry
        entry_id = entry.find("atom:id", ns)
        if entry_id is not None and "errors" in (entry_id.text or ""):
            return None

        title_el = entry.find("atom:title", ns)
        title = " ".join(title_el.text.strip().split()) if title_el is not None and title_el.text else ""

        summary_el = entry.find("atom:summary", ns)
        abstract = " ".join(summary_el.text.strip().split()) if summary_el is not None and summary_el.text else ""

        authors = []
        for author_el in entry.findall("atom:author", ns):
            name_el = author_el.find("atom:name", ns)
            if name_el is not None and name_el.text:
                authors.append(name_el.text.strip())

        published_el = entry.find("atom:published", ns)
        year = None
        if published_el is not None and published_el.text:
            year = int(published_el.text[:4])

        # Check for journal-ref and DOI
        journal_ref = entry.find("arxiv:journal_ref", ns)
        journal = journal_ref.text.strip() if journal_ref is not None and journal_ref.text else "arXiv preprint"

        doi_el = entry.find("arxiv:doi", ns)
        doi = doi_el.text.strip() if doi_el is not None and doi_el.text else ""

        # Primary categories
        primary_cat = entry.find("arxiv:primary_category", ns)
        category = primary_cat.get("term", "") if primary_cat is not None else ""

        return {
            "source": "arxiv",
            "identifier_type": "arxiv",
            "identifier": arxiv_id,
            "title": title,
            "authors": authors,
            "year": year,
            "journal": journal,
            "volume": "",
            "issue": "",
            "pages": "",
            "abstract": abstract,
            "doi": doi,
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "type": "preprint",
            "category": category,
        }
    except (requests.RequestException, ET.ParseError):
        return None


def fetch_pubmed(pmid: str) -> Optional[Dict[str, Any]]:
    """Fetch metadata from PubMed E-utilities."""
    try:
        resp = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            params={"db": "pubmed", "id": pmid, "retmode": "xml"},
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            return None

        root = ET.fromstring(resp.text)
        article = root.find(".//PubmedArticle/MedlineCitation/Article")
        if article is None:
            return None

        title_el = article.find("ArticleTitle")
        title = title_el.text.strip() if title_el is not None and title_el.text else ""

        abstract_el = article.find("Abstract/AbstractText")
        abstract = abstract_el.text.strip() if abstract_el is not None and abstract_el.text else ""

        authors = []
        for author_el in article.findall("AuthorList/Author"):
            last = author_el.find("LastName")
            fore = author_el.find("ForeName")
            if last is not None and last.text:
                name = last.text
                if fore is not None and fore.text:
                    name = f"{fore.text} {name}"
                authors.append(name)

        journal_el = article.find("Journal")
        journal = ""
        volume = ""
        issue = ""
        year = None
        if journal_el is not None:
            j_title = journal_el.find("Title")
            if j_title is not None and j_title.text:
                journal = j_title.text
            ji = journal_el.find("JournalIssue")
            if ji is not None:
                vol = ji.find("Volume")
                if vol is not None and vol.text:
                    volume = vol.text
                iss = ji.find("Issue")
                if iss is not None and iss.text:
                    issue = iss.text
                pub_date = ji.find("PubDate/Year")
                if pub_date is not None and pub_date.text:
                    year = int(pub_date.text)

        pages_el = article.find("Pagination/MedlinePgn")
        pages = pages_el.text if pages_el is not None and pages_el.text else ""

        # Find DOI in ArticleIdList
        doi = ""
        id_list = root.find(".//PubmedArticle/PubmedData/ArticleIdList")
        if id_list is not None:
            for aid in id_list.findall("ArticleId"):
                if aid.get("IdType") == "doi" and aid.text:
                    doi = aid.text

        return {
            "source": "pubmed",
            "identifier_type": "pmid",
            "identifier": pmid,
            "title": title,
            "authors": authors,
            "year": year,
            "journal": journal,
            "volume": volume,
            "issue": issue,
            "pages": pages,
            "abstract": abstract,
            "doi": doi,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "type": "journal-article",
        }
    except (requests.RequestException, ET.ParseError):
        return None


# --- BibTeX Formatting ---


def _bibtex_escape(text: str) -> str:
    """Escape special LaTeX characters."""
    for ch in ("&", "%", "#", "_"):
        text = text.replace(ch, f"\\{ch}")
    return text


def to_bibtex(meta: Dict[str, Any]) -> str:
    """Convert metadata dict to BibTeX entry."""
    # Generate citation key: FirstAuthorLastName + Year + first meaningful word of title
    first_author = meta["authors"][0].split()[-1] if meta["authors"] else "Unknown"
    year = meta.get("year") or "XXXX"
    title_words = [w for w in meta.get("title", "").split() if len(w) > 3]
    key_word = title_words[0] if title_words else "untitled"
    key = re.sub(r"[^a-zA-Z0-9]", "", f"{first_author}{year}{key_word}")

    entry_type = "article"
    if meta.get("type") == "preprint" or meta.get("source") == "arxiv":
        entry_type = "misc"
    elif "Dataset" in meta.get("type", ""):
        entry_type = "misc"

    lines = [f"@{entry_type}{{{key},"]
    lines.append(f"  title = {{{_bibtex_escape(meta.get('title', ''))}}},")

    if meta["authors"]:
        lines.append(f"  author = {{{_bibtex_escape(' and '.join(meta['authors']))}}},")

    if meta.get("year"):
        lines.append(f"  year = {{{meta['year']}}},")

    if meta.get("journal"):
        field = "journal" if entry_type == "article" else "howpublished"
        lines.append(f"  {field} = {{{_bibtex_escape(meta['journal'])}}},")

    if meta.get("volume"):
        lines.append(f"  volume = {{{meta['volume']}}},")
    if meta.get("issue"):
        lines.append(f"  number = {{{meta['issue']}}},")
    if meta.get("pages"):
        lines.append(f"  pages = {{{meta['pages']}}},")
    if meta.get("doi"):
        lines.append(f"  doi = {{{meta['doi']}}},")
    if meta.get("url"):
        lines.append(f"  url = {{{meta['url']}}},")
    if meta.get("abstract"):
        lines.append(f"  abstract = {{{_bibtex_escape(meta['abstract'][:500])}}},")

    lines.append("}")
    return "\n".join(lines)


# --- Main Logic ---


def extract_metadata(identifier: str) -> Dict[str, Any]:
    """Extract metadata for a single identifier."""
    id_type, normalized = classify_identifier(identifier)

    if id_type == "doi":
        result = fetch_doi(normalized)
    elif id_type == "arxiv":
        result = fetch_arxiv(normalized)
    elif id_type == "pmid":
        result = fetch_pubmed(normalized)
    elif id_type == "url":
        # Try to extract DOI from URL
        doi_match = re.search(r"(10\.\d{4,9}/\S+)", normalized)
        if doi_match:
            result = fetch_doi(doi_match.group(1))
        else:
            result = None
    else:
        result = None

    if result is None:
        return {
            "error": f"Could not resolve identifier: {identifier}",
            "identifier": identifier,
            "identifier_type": id_type,
        }

    return result


def process_batch(filepath: str) -> List[Dict[str, Any]]:
    """Process a file with one identifier per line."""
    results = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            result = extract_metadata(line)
            results.append(result)
            time.sleep(0.5)  # Rate limiting between requests
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Extract bibliographic metadata from DOI, PMID, arxiv ID, or URL.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 10.1038/s41586-021-03819-2
  %(prog)s 2301.07041
  %(prog)s arxiv:2301.07041
  %(prog)s PMID:12345678
  %(prog)s https://doi.org/10.1038/s41586-021-03819-2
  %(prog)s 2301.07041 --format bibtex
  %(prog)s --batch identifiers.txt --format json

Supported identifier types:
  DOI       10.xxxx/... or https://doi.org/10.xxxx/... or doi:10.xxxx/...
  arxiv     2301.07041 or arxiv:2301.07041 or https://arxiv.org/abs/2301.07041
  PMID      12345678 or PMID:12345678
  URL       https://... (attempts DOI extraction from URL)
        """,
    )
    parser.add_argument(
        "identifier", nargs="?", type=str,
        help="Identifier to look up (DOI, arxiv ID, PMID, or URL)",
    )
    parser.add_argument(
        "--format", type=str, choices=["json", "bibtex"], default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--batch", type=str, metavar="FILE",
        help="Process a file with one identifier per line",
    )

    args = parser.parse_args()

    if not args.identifier and not args.batch:
        parser.print_help()
        sys.exit(1)

    if args.batch:
        results = process_batch(args.batch)
    else:
        results = [extract_metadata(args.identifier)]

    if args.format == "bibtex":
        for r in results:
            if "error" in r:
                print(f"% ERROR: {r['error']}", file=sys.stderr)
            else:
                print(to_bibtex(r))
                print()
    else:
        output = results if len(results) > 1 else results[0]
        print(json.dumps(output, indent=2, ensure_ascii=False))

    # Exit 1 if any errors
    has_errors = any("error" in r for r in results)
    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()
