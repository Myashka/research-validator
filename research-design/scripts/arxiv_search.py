#!/usr/bin/env python3
"""
arXiv Search Client for Research Validator.

Searches the arXiv API for papers by keyword, author, ID, or category,
with date filtering and structured JSON output.

Inspired by and adapted from the claude-scientific-skills repository.
"""

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta


ARXIV_API_URL = "http://export.arxiv.org/api/query"
MAX_RESULTS_LIMIT = 300
RATE_LIMIT_SECONDS = 3

# Atom/OpenSearch namespaces used in arXiv API responses
NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
    "arxiv": "http://arxiv.org/schemas/atom",
}

# Shortcut category mappings
CATEGORY_SHORTCUTS = {
    "ml": "cs.LG",
    "nlp": "cs.CL",
    "cv": "cs.CV",
    "ai": "cs.AI",
    "statml": "stat.ML",
}


def _extract_arxiv_id(entry):
    """Extract the arXiv ID from an entry's <id> element."""
    raw_id = entry.findtext("atom:id", default="", namespaces=NS)
    # ID looks like http://arxiv.org/abs/2301.12345v1
    return raw_id.split("/abs/")[-1] if "/abs/" in raw_id else raw_id


def _extract_links(entry):
    """Extract PDF and abstract URLs from entry links."""
    links = {}
    for link in entry.findall("atom:link", NS):
        rel = link.get("rel", "")
        href = link.get("href", "")
        link_type = link.get("type", "")
        if rel == "alternate":
            links["abstract_url"] = href
        elif link_type == "application/pdf":
            links["pdf_url"] = href
    return links


def _extract_categories(entry):
    """Extract all category terms from an entry."""
    categories = []
    for cat in entry.findall("atom:category", NS):
        term = cat.get("term", "")
        if term:
            categories.append(term)
    return categories


def _parse_entry(entry):
    """Parse a single Atom entry into a structured dict."""
    authors = []
    for author in entry.findall("atom:author", NS):
        name = author.findtext("atom:name", default="", namespaces=NS).strip()
        if name:
            authors.append(name)

    abstract = entry.findtext("atom:summary", default="", namespaces=NS).strip()
    # Collapse internal whitespace in abstract
    abstract = " ".join(abstract.split())

    arxiv_id = _extract_arxiv_id(entry)
    links = _extract_links(entry)
    categories = _extract_categories(entry)

    published = entry.findtext("atom:published", default="", namespaces=NS).strip()
    updated = entry.findtext("atom:updated", default="", namespaces=NS).strip()

    # arXiv-specific fields
    comment = entry.findtext("arxiv:comment", default="", namespaces=NS).strip()
    journal_ref = entry.findtext("arxiv:journal_ref", default="", namespaces=NS).strip()
    doi = entry.findtext("arxiv:doi", default="", namespaces=NS).strip()
    primary_category_el = entry.find("arxiv:primary_category", NS)
    primary_category = primary_category_el.get("term", "") if primary_category_el is not None else ""

    result = {
        "arxiv_id": arxiv_id,
        "title": " ".join(entry.findtext("atom:title", default="", namespaces=NS).strip().split()),
        "authors": authors,
        "abstract": abstract,
        "categories": categories,
        "primary_category": primary_category,
        "published": published,
        "updated": updated,
        "abstract_url": links.get("abstract_url", ""),
        "pdf_url": links.get("pdf_url", ""),
    }

    if comment:
        result["comment"] = comment
    if journal_ref:
        result["journal_ref"] = journal_ref
    if doi:
        result["doi"] = doi

    return result


def build_search_query(keywords=None, title=None, abstract=None, author=None,
                       arxiv_id=None, categories=None):
    """Build an arXiv search_query string from structured parameters."""
    parts = []

    if arxiv_id:
        # Direct ID lookup uses id_list, not search_query
        return None

    if keywords:
        parts.append(f"all:{keywords}")
    if title:
        parts.append(f"ti:{title}")
    if abstract:
        parts.append(f"abs:{abstract}")
    if author:
        parts.append(f"au:{author}")

    if categories:
        cat_parts = [f"cat:{c}" for c in categories]
        cat_query = " OR ".join(cat_parts)
        if len(cat_parts) > 1:
            cat_query = f"({cat_query})"
        parts.append(cat_query)

    return " AND ".join(parts) if parts else ""


def fetch_results(search_query=None, id_list=None, start=0, max_results=10,
                  sort_by=None, sort_order=None):
    """Fetch results from the arXiv API. Returns parsed XML root."""
    params = {
        "start": str(start),
        "max_results": str(max_results),
    }

    if search_query:
        params["search_query"] = search_query
    if id_list:
        params["id_list"] = id_list
    if sort_by:
        params["sortBy"] = sort_by
    if sort_order:
        params["sortOrder"] = sort_order

    url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "ResearchValidator/1.0"})

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()

    return ET.fromstring(data)


def filter_by_date(entries, since_date):
    """Filter entries to only include those published on or after since_date."""
    filtered = []
    for entry in entries:
        published = entry.get("published", "")
        if published:
            # Parse ISO date (e.g. 2024-01-15T00:00:00Z)
            try:
                pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
                if pub_date.date() >= since_date:
                    filtered.append(entry)
            except ValueError:
                # If we can't parse, include it anyway
                filtered.append(entry)
        else:
            filtered.append(entry)
    return filtered


def search(keywords=None, title=None, abstract=None, author=None,
           arxiv_id=None, categories=None, max_results=10,
           sort_by=None, sort_order=None, since_months=None):
    """
    Execute an arXiv search and return structured results.

    Returns a dict with metadata and a list of paper entries.
    """
    max_results = min(max_results, MAX_RESULTS_LIMIT)

    search_query = build_search_query(
        keywords=keywords, title=title, abstract=abstract,
        author=author, arxiv_id=arxiv_id, categories=categories,
    )

    id_list = arxiv_id if arxiv_id else None

    # Map sort options
    sort_map = {"relevance": "relevance", "date": "submittedDate"}
    api_sort_by = sort_map.get(sort_by) if sort_by else None
    api_sort_order = "descending" if sort_by == "date" else None
    if sort_order:
        api_sort_order = sort_order

    all_entries = []
    start = 0
    batch_size = min(max_results, 100)  # arXiv recommends <= 100 per request
    remaining = max_results

    while remaining > 0:
        fetch_count = min(batch_size, remaining)

        root = fetch_results(
            search_query=search_query,
            id_list=id_list,
            start=start,
            max_results=fetch_count,
            sort_by=api_sort_by,
            sort_order=api_sort_order,
        )

        # Parse total results from opensearch
        total_str = root.findtext("opensearch:totalResults", default="0", namespaces=NS)
        total_available = int(total_str)

        entries = root.findall("atom:entry", NS)
        if not entries:
            break

        for entry in entries:
            parsed = _parse_entry(entry)
            # Skip error entries (arXiv returns an entry with error info on bad queries)
            if not parsed["arxiv_id"] or parsed["title"].startswith("Error"):
                continue
            all_entries.append(parsed)

        start += len(entries)
        remaining -= len(entries)

        # Stop if we've fetched everything available
        if start >= total_available:
            break

        # Rate limiting between pages
        if remaining > 0:
            time.sleep(RATE_LIMIT_SECONDS)

    # Apply date filter if requested
    since_date = None
    if since_months:
        since_date = (datetime.now() - timedelta(days=since_months * 30)).date()
        all_entries = filter_by_date(all_entries, since_date)

    # Build the verbatim query for provenance
    verbatim_query = search_query if search_query else f"id_list:{arxiv_id}"

    result = {
        "query": verbatim_query,
        "parameters": {
            "keywords": keywords,
            "title": title,
            "abstract": abstract,
            "author": author,
            "arxiv_id": arxiv_id,
            "categories": categories,
            "max_results": max_results,
            "sort_by": sort_by,
            "since_months": since_months,
        },
        "total_results": len(all_entries),
        "retrieved_at": datetime.now().isoformat(),
        "papers": all_entries,
    }

    return result


def resolve_categories(args):
    """Resolve category shortcut flags into a list of category strings."""
    categories = []
    if args.category:
        categories.extend(args.category)
    if args.ml:
        categories.append(CATEGORY_SHORTCUTS["ml"])
    if args.nlp:
        categories.append(CATEGORY_SHORTCUTS["nlp"])
    if args.cv:
        categories.append(CATEGORY_SHORTCUTS["cv"])
    if args.ai:
        categories.append(CATEGORY_SHORTCUTS["ai"])
    if args.statml:
        categories.append(CATEGORY_SHORTCUTS["statml"])
    return categories if categories else None


def main():
    parser = argparse.ArgumentParser(
        description="Search the arXiv API for ML/AI research papers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Keyword search across all fields
  %(prog)s --keywords "transformer attention mechanism"

  # Title-specific search in ML category
  %(prog)s --title "diffusion models" --ml

  # Author lookup
  %(prog)s --author "Vaswani"

  # Direct arXiv ID retrieval
  %(prog)s --id 2301.12345

  # Concurrent work detection (papers from last 6 months)
  %(prog)s --keywords "reward hacking RLHF" --since 6 --sort date

  # Combined search with multiple categories
  %(prog)s --keywords "multimodal learning" --ml --cv --max 50

Category shortcuts:
  --ml    cs.LG  (Machine Learning)
  --nlp   cs.CL  (Computation and Language / NLP)
  --cv    cs.CV  (Computer Vision)
  --ai    cs.AI  (Artificial Intelligence)
  --statml stat.ML (Statistics - Machine Learning)
        """,
    )

    # Search parameters
    search_group = parser.add_argument_group("search parameters")
    search_group.add_argument(
        "--keywords", "-k", type=str, default=None,
        help="Search keywords across all fields",
    )
    search_group.add_argument(
        "--title", "-t", type=str, default=None,
        help="Search within paper titles",
    )
    search_group.add_argument(
        "--abstract", "-a", type=str, default=None,
        help="Search within abstracts",
    )
    search_group.add_argument(
        "--author", "-u", type=str, default=None,
        help="Search by author name",
    )
    search_group.add_argument(
        "--id", type=str, default=None, dest="arxiv_id",
        help="Retrieve paper by arXiv ID (e.g., 2301.12345)",
    )

    # Category filters
    cat_group = parser.add_argument_group("category filters")
    cat_group.add_argument(
        "--category", "-c", type=str, action="append", default=None,
        help="Filter by arXiv category (e.g., cs.LG). Repeatable.",
    )
    cat_group.add_argument("--ml", action="store_true", help="Shortcut for cs.LG")
    cat_group.add_argument("--nlp", action="store_true", help="Shortcut for cs.CL")
    cat_group.add_argument("--cv", action="store_true", help="Shortcut for cs.CV")
    cat_group.add_argument("--ai", action="store_true", help="Shortcut for cs.AI")
    cat_group.add_argument("--statml", action="store_true", help="Shortcut for stat.ML")

    # Output controls
    output_group = parser.add_argument_group("output controls")
    output_group.add_argument(
        "--max", "-m", type=int, default=10, dest="max_results",
        help="Maximum number of results (default: 10, max: 300)",
    )
    output_group.add_argument(
        "--sort", "-s", type=str, choices=["relevance", "date"], default=None,
        help="Sort results by relevance or date (latest first)",
    )
    output_group.add_argument(
        "--since", type=int, default=None, metavar="MONTHS",
        help="Only show papers from the last N months (for concurrent work detection)",
    )
    output_group.add_argument(
        "--output", "-o", type=str, default=None,
        help="Write JSON output to file instead of stdout",
    )

    args = parser.parse_args()

    # Validate that at least one search parameter is given
    categories = resolve_categories(args)
    if not any([args.keywords, args.title, args.abstract, args.author, args.arxiv_id, categories]):
        parser.error("At least one search parameter is required "
                     "(--keywords, --title, --abstract, --author, --id, or a category filter)")

    results = search(
        keywords=args.keywords,
        title=args.title,
        abstract=args.abstract,
        author=args.author,
        arxiv_id=args.arxiv_id,
        categories=categories,
        max_results=args.max_results,
        sort_by=args.sort,
        since_months=args.since,
    )

    output = json.dumps(results, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
            f.write("\n")
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
