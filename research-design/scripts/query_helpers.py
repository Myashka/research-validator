#!/usr/bin/env python3
"""
High-level research query helpers using OpenAlex.

Provides compound query functions that combine multiple OpenAlexClient calls
for common research investigation patterns: author lookup, citation graphs,
trend analysis, and research output evaluation.

Original concept and design adapted from:
  claude-scientific-skills (https://github.com/anthropics/claude-scientific-skills)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

# Import OpenAlexClient from the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openalex_client import OpenAlexClient


def _is_error(result: Dict[str, Any]) -> bool:
    """Check if an API result is an error."""
    return result.get("error", False)


def find_author_works(name: str, max_results: int = 25) -> Dict[str, Any]:
    """Search for an author by name, then retrieve their works.

    Two-step compound query:
      1. Search authors by name
      2. Get works for the top matching author
    """
    client = OpenAlexClient()

    # Step 1: Search for the author
    authors = client.search_authors(name, max_results=5)
    if _is_error(authors):
        return authors
    if not authors.get("results"):
        return {"error": True, "message": f"No authors found matching '{name}'"}

    # Step 2: Get works for the best match
    author = authors["results"][0]
    author_id = author["id"]

    works = client.get_author_works(
        author_id, max_results=max_results, sort_field="cited_by_count"
    )
    if _is_error(works):
        return works

    return {
        "author": author,
        "works": works.get("results", []),
        "meta": {"works_count": len(works.get("results", []))},
    }


def find_institution_works(name: str, max_results: int = 25) -> Dict[str, Any]:
    """Search for an institution, then retrieve works affiliated with it.

    Two-step compound query:
      1. Search institutions by name
      2. Search works filtered by institution
    """
    client = OpenAlexClient()

    # Step 1: Search for the institution
    institutions = client.search_institutions(name, max_results=5)
    if _is_error(institutions):
        return institutions
    if not institutions.get("results"):
        return {"error": True, "message": f"No institutions found matching '{name}'"}

    # Step 2: Get works associated with the institution
    institution = institutions["results"][0]
    inst_name = institution["display_name"]

    works = client.search_works(
        inst_name, max_results=max_results, sort_field="cited_by_count"
    )
    if _is_error(works):
        return works

    return {
        "institution": institution,
        "works": works.get("results", []),
        "meta": {"works_count": len(works.get("results", []))},
    }


def find_citing_papers(paper_id: str, max_results: int = 25) -> Dict[str, Any]:
    """Forward citation graph: find papers that cite a given work.

    Also retrieves the original paper's metadata for context.
    """
    client = OpenAlexClient()

    # Get the original work
    work = client.get_work(paper_id)
    if _is_error(work):
        return work

    # Get citing papers
    citations = client.get_citations(
        paper_id, max_results=max_results, sort_field="cited_by_count"
    )
    if _is_error(citations):
        return citations

    return {
        "source_paper": work,
        "citing_papers": citations.get("results", []),
        "meta": {"citing_count": len(citations.get("results", []))},
    }


def find_cited_papers(paper_id: str, max_results: int = 25) -> Dict[str, Any]:
    """Backward references: find papers cited by a given work.

    Also retrieves the original paper's metadata for context.
    """
    client = OpenAlexClient()

    # Get the original work
    work = client.get_work(paper_id)
    if _is_error(work):
        return work

    # Get referenced papers
    references = client.get_references(paper_id, max_results=max_results)
    if _is_error(references):
        return references

    return {
        "source_paper": work,
        "cited_papers": references.get("results", []),
        "meta": {"cited_count": len(references.get("results", []))},
    }


def analyze_trends(topic: str, years: int = 10) -> Dict[str, Any]:
    """Analyze publication volume trends for a topic over time.

    Returns yearly publication counts and basic trend statistics.
    """
    client = OpenAlexClient()

    current_year = datetime.now().year
    year_start = current_year - years
    year_end = current_year

    trends = client.get_trends(topic, year_start=year_start, year_end=year_end)
    if _is_error(trends):
        return trends

    # Compute basic statistics
    counts = [t["count"] for t in trends.get("trends", []) if not t.get("error")]
    if counts:
        total = sum(counts)
        avg = total / len(counts)
        peak_year_entry = max(
            (t for t in trends["trends"] if not t.get("error")),
            key=lambda t: t["count"],
        )
        trends["statistics"] = {
            "total_publications": total,
            "average_per_year": round(avg, 1),
            "peak_year": peak_year_entry["year"],
            "peak_count": peak_year_entry["count"],
        }

    return trends


def find_highly_cited(
    topic: str, min_citations: int = 100, max_results: int = 25
) -> Dict[str, Any]:
    """Find influential (highly cited) papers on a topic."""
    client = OpenAlexClient()

    result = client.get_highly_cited(
        topic, min_citations=min_citations, max_results=max_results
    )
    if _is_error(result):
        return result

    return {
        "topic": topic,
        "min_citations": min_citations,
        "papers": result.get("results", []),
        "meta": {"count": len(result.get("results", []))},
    }


def evaluate_output(
    name: str, entity_type: str = "author"
) -> Dict[str, Any]:
    """Comprehensive research output analysis for an author or institution.

    Searches for the entity, retrieves works, and computes summary statistics
    including citation metrics, publication timeline, and top works.
    """
    client = OpenAlexClient()

    if entity_type == "author":
        # Search and get author info
        authors = client.search_authors(name, max_results=5)
        if _is_error(authors):
            return authors
        if not authors.get("results"):
            return {"error": True, "message": f"No authors found matching '{name}'"}

        entity = authors["results"][0]
        entity_id = entity["id"]

        # Get detailed info
        info = client.get_author_info(entity_id)
        if _is_error(info):
            info = entity

        # Get works
        works_result = client.get_author_works(
            entity_id, max_results=50, sort_field="cited_by_count"
        )
        if _is_error(works_result):
            return works_result
        works = works_result.get("results", [])

    elif entity_type == "institution":
        # Search institution
        institutions = client.search_institutions(name, max_results=5)
        if _is_error(institutions):
            return institutions
        if not institutions.get("results"):
            return {
                "error": True,
                "message": f"No institutions found matching '{name}'",
            }

        entity = institutions["results"][0]
        info = entity

        # Get works by searching with institution name
        works_result = client.search_works(
            entity["display_name"], max_results=50, sort_field="cited_by_count"
        )
        if _is_error(works_result):
            return works_result
        works = works_result.get("results", [])

    else:
        return {
            "error": True,
            "message": f"Unknown entity_type '{entity_type}'. Use 'author' or 'institution'.",
        }

    # Compute summary statistics from works
    citations = [w.get("cited_by_count", 0) for w in works]
    years = [w.get("publication_year") for w in works if w.get("publication_year")]

    stats = {
        "total_works_retrieved": len(works),
        "total_citations": sum(citations),
        "mean_citations": round(sum(citations) / len(citations), 1) if citations else 0,
        "max_citations": max(citations) if citations else 0,
    }
    if years:
        stats["year_range"] = f"{min(years)}-{max(years)}"

    # Top 5 works by citation count
    top_works = sorted(works, key=lambda w: w.get("cited_by_count", 0), reverse=True)[
        :5
    ]

    return {
        "entity_type": entity_type,
        "entity": info,
        "statistics": stats,
        "top_works": top_works,
    }


def output_json(data: Dict[str, Any]) -> None:
    """Print JSON to stdout."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="High-level research query helpers using OpenAlex.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s find-author-works "Yoshua Bengio"
  %(prog)s find-institution-works "MIT"
  %(prog)s find-citing-papers W2741809807
  %(prog)s find-cited-papers W2741809807
  %(prog)s analyze-trends "large language models" --years 5
  %(prog)s find-highly-cited "reinforcement learning" --min-citations 500
  %(prog)s evaluate-output "Geoffrey Hinton" --type author
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- find-author-works ---
    p = subparsers.add_parser(
        "find-author-works", help="Search author by name, then get their works"
    )
    p.add_argument("name", type=str, help="Author name to search")
    p.add_argument(
        "--max", "-m", type=int, default=25, dest="max_results",
        help="Maximum works to return (default: 25)",
    )

    # --- find-institution-works ---
    p = subparsers.add_parser(
        "find-institution-works", help="Search institution, then get affiliated works"
    )
    p.add_argument("name", type=str, help="Institution name to search")
    p.add_argument(
        "--max", "-m", type=int, default=25, dest="max_results",
        help="Maximum works to return (default: 25)",
    )

    # --- find-citing-papers ---
    p = subparsers.add_parser(
        "find-citing-papers", help="Forward citation graph (papers citing this one)"
    )
    p.add_argument("paper_id", type=str, help="OpenAlex work ID or DOI")
    p.add_argument(
        "--max", "-m", type=int, default=25, dest="max_results",
        help="Maximum results (default: 25)",
    )

    # --- find-cited-papers ---
    p = subparsers.add_parser(
        "find-cited-papers", help="Backward references (papers cited by this one)"
    )
    p.add_argument("paper_id", type=str, help="OpenAlex work ID or DOI")
    p.add_argument(
        "--max", "-m", type=int, default=25, dest="max_results",
        help="Maximum results (default: 25)",
    )

    # --- analyze-trends ---
    p = subparsers.add_parser(
        "analyze-trends", help="Publication volume over time"
    )
    p.add_argument("topic", type=str, help="Topic to analyze")
    p.add_argument(
        "--years", "-y", type=int, default=10,
        help="Number of years to look back (default: 10)",
    )

    # --- find-highly-cited ---
    p = subparsers.add_parser(
        "find-highly-cited", help="Find influential papers by citation count"
    )
    p.add_argument("topic", type=str, help="Topic to search")
    p.add_argument(
        "--min-citations", type=int, default=100,
        help="Minimum citation count (default: 100)",
    )
    p.add_argument(
        "--max", "-m", type=int, default=25, dest="max_results",
        help="Maximum results (default: 25)",
    )

    # --- evaluate-output ---
    p = subparsers.add_parser(
        "evaluate-output",
        help="Comprehensive research output analysis (author or institution)",
    )
    p.add_argument("name", type=str, help="Author or institution name")
    p.add_argument(
        "--type", "-t", type=str, default="author",
        choices=["author", "institution"], dest="entity_type",
        help="Entity type (default: author)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "find-author-works":
        result = find_author_works(args.name, max_results=args.max_results)
    elif args.command == "find-institution-works":
        result = find_institution_works(args.name, max_results=args.max_results)
    elif args.command == "find-citing-papers":
        result = find_citing_papers(args.paper_id, max_results=args.max_results)
    elif args.command == "find-cited-papers":
        result = find_cited_papers(args.paper_id, max_results=args.max_results)
    elif args.command == "analyze-trends":
        result = analyze_trends(args.topic, years=args.years)
    elif args.command == "find-highly-cited":
        result = find_highly_cited(
            args.topic,
            min_citations=args.min_citations,
            max_results=args.max_results,
        )
    elif args.command == "evaluate-output":
        result = evaluate_output(args.name, entity_type=args.entity_type)
    else:
        parser.print_help()
        sys.exit(1)

    result["retrieved_at"] = datetime.now().isoformat()
    output_json(result)


if __name__ == "__main__":
    main()
