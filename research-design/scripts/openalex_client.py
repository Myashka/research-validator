#!/usr/bin/env python3
"""
OpenAlex API Client for Research Validator.

Provides structured access to the OpenAlex scholarly database for paper search,
citation analysis, author lookup, institution analysis, and publication trends.

Inspired by and adapted from:
  - claude-scientific-skills repository (original concept and CLI design)
  - https://github.com/LeoGitGuy/alex-paper-search-mcp (pyalex-based search patterns)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import pyalex
    from pyalex import Authors, Institutions, Works, config
except ImportError:
    print(
        "Error: 'pyalex' library is required. Install it with:\n"
        "  uv sync",
        file=sys.stderr,
    )
    sys.exit(1)


class OpenAlexClient:
    """Client for interacting with the OpenAlex API via pyalex."""

    def __init__(self, mailto: Optional[str] = None):
        config.max_retries = 3
        config.retry_backoff_factor = 0.1
        config.retry_http_codes = [429, 500, 503]

        if mailto:
            config.email = mailto
        elif os.getenv("OPENALEX_EMAIL"):
            config.email = os.getenv("OPENALEX_EMAIL")

        api_key = os.getenv("OPENALEX_API_KEY")
        if api_key:
            config.api_key = api_key

    @staticmethod
    def _reconstruct_abstract(work: Dict[str, Any]) -> str:
        """Extract abstract from a pyalex work object."""
        # pyalex exposes abstract directly via work['abstract']
        abstract = work.get("abstract")
        if abstract:
            return abstract

        # Fallback: reconstruct from inverted index
        inverted_index = work.get("abstract_inverted_index")
        if not inverted_index:
            return ""
        word_positions = []
        for word, positions in inverted_index.items():
            for pos in positions:
                word_positions.append((pos, word))
        word_positions.sort()
        return " ".join(word for _, word in word_positions)

    def _parse_work(self, work: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key fields from an OpenAlex work object."""
        authors = []
        for authorship in work.get("authorships", []):
            author = authorship.get("author", {})
            name = author.get("display_name", "")
            if not name:
                continue
            entry = {"name": name, "id": author.get("id", "")}
            institutions = [
                inst.get("display_name", "")
                for inst in authorship.get("institutions", [])
                if inst.get("display_name")
            ]
            if institutions:
                entry["institutions"] = institutions
            authors.append(entry)

        # Best OA location
        best_oa = work.get("best_oa_location") or {}
        pdf_url = best_oa.get("pdf_url", "") or ""
        oa_url = best_oa.get("landing_page_url", "") or pdf_url

        # Primary location fallback
        if not oa_url:
            primary = work.get("primary_location") or {}
            oa_url = primary.get("landing_page_url", "") or ""
            if not pdf_url:
                pdf_url = primary.get("pdf_url", "") or ""

        # Topics (preferred over deprecated concepts)
        topics = []
        for topic in work.get("topics", [])[:5]:
            topic_name = topic.get("display_name")
            if topic_name:
                topics.append(topic_name)

        result = {
            "id": work.get("id", ""),
            "doi": work.get("doi", ""),
            "title": work.get("title", ""),
            "authors": authors,
            "publication_year": work.get("publication_year"),
            "publication_date": work.get("publication_date", ""),
            "cited_by_count": work.get("cited_by_count", 0),
            "is_oa": work.get("open_access", {}).get("is_oa", False),
            "oa_url": oa_url,
            "pdf_url": pdf_url,
            "type": work.get("type", ""),
            "language": work.get("language", ""),
            "source": (
                (work.get("primary_location") or {})
                .get("source", {})
                .get("display_name", "")
                if work.get("primary_location")
                else ""
            ),
            "topics": topics,
        }

        abstract = self._reconstruct_abstract(work)
        if abstract:
            result["abstract"] = abstract

        return result

    def search_works(
        self,
        query: str,
        max_results: int = 25,
        sort_field: Optional[str] = None,
        sort_order: str = "desc",
        year: Optional[str] = None,
        is_oa: Optional[bool] = None,
        work_type: Optional[str] = None,
        has_abstract: bool = False,
    ) -> Dict[str, Any]:
        """Search for papers by title, abstract, or topic."""
        try:
            works_query = Works().search(query)

            if year:
                if "-" in year:
                    start, end = year.split("-", 1)
                    works_query = works_query.filter(
                        from_publication_date=f"{start}-01-01",
                        to_publication_date=f"{end}-12-31",
                    )
                else:
                    works_query = works_query.filter(publication_year=int(year))

            if is_oa is not None:
                works_query = works_query.filter(is_oa=is_oa)

            if work_type:
                works_query = works_query.filter(type=work_type)

            if has_abstract:
                works_query = works_query.filter(has_abstract=True)

            if sort_field and sort_field != "relevance_score":
                works_query = works_query.sort(**{sort_field: sort_order})

            results = works_query.get()[:max_results]

            return {
                "meta": {"count": len(results)},
                "results": [self._parse_work(w) for w in results],
            }
        except Exception as e:
            return {"error": True, "message": str(e)}

    def get_work(self, work_id: str) -> Dict[str, Any]:
        """Get a specific work by OpenAlex ID or DOI."""
        try:
            if work_id.startswith("10."):
                work_id = f"https://doi.org/{work_id}"
            elif not work_id.startswith(("W", "https://", "doi:")):
                work_id = f"W{work_id}"

            work = Works()[work_id]
            return self._parse_work(work)
        except Exception as e:
            return {"error": True, "message": str(e)}

    def get_citations(
        self,
        work_id: str,
        max_results: int = 25,
        sort_field: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get papers that cite a given work."""
        try:
            if work_id.startswith("10."):
                work_id = f"https://doi.org/{work_id}"

            works_query = Works().filter(cites=work_id)

            if sort_field:
                works_query = works_query.sort(**{sort_field: sort_order})

            results = works_query.get()[:max_results]

            return {
                "meta": {"count": len(results)},
                "results": [self._parse_work(w) for w in results],
            }
        except Exception as e:
            return {"error": True, "message": str(e)}

    def get_references(
        self, work_id: str, max_results: int = 25
    ) -> Dict[str, Any]:
        """Get papers cited by a given work."""
        try:
            if work_id.startswith("10."):
                work_id = f"https://doi.org/{work_id}"

            works_query = Works().filter(cited_by=work_id)
            results = works_query.get()[:max_results]

            return {
                "meta": {"count": len(results)},
                "results": [self._parse_work(w) for w in results],
            }
        except Exception as e:
            return {"error": True, "message": str(e)}

    def search_authors(
        self, query: str, max_results: int = 10
    ) -> Dict[str, Any]:
        """Search for authors by name."""
        try:
            results = Authors().search(query).get()[:max_results]

            parsed = []
            for author in results:
                parsed.append(
                    {
                        "id": author.get("id", ""),
                        "display_name": author.get("display_name", ""),
                        "works_count": author.get("works_count", 0),
                        "cited_by_count": author.get("cited_by_count", 0),
                        "affiliation": (
                            author.get("last_known_institutions", [{}])[0].get(
                                "display_name", ""
                            )
                            if author.get("last_known_institutions")
                            else ""
                        ),
                        "h_index": author.get("summary_stats", {}).get(
                            "h_index", 0
                        ),
                        "orcid": author.get("orcid", ""),
                    }
                )

            return {"meta": {"count": len(parsed)}, "results": parsed}
        except Exception as e:
            return {"error": True, "message": str(e)}

    def get_author_works(
        self,
        author_id: str,
        max_results: int = 25,
        sort_field: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get works by a specific author."""
        try:
            if not author_id.startswith(("A", "https://")):
                author_id = f"A{author_id}"

            works_query = Works().filter(author={"id": author_id})

            if sort_field:
                works_query = works_query.sort(**{sort_field: sort_order})

            results = works_query.get()[:max_results]

            return {
                "meta": {"count": len(results)},
                "results": [self._parse_work(w) for w in results],
            }
        except Exception as e:
            return {"error": True, "message": str(e)}

    def get_author_info(self, author_id: str) -> Dict[str, Any]:
        """Get author details by ID."""
        try:
            if not author_id.startswith(("A", "https://")):
                author_id = f"A{author_id}"
            if author_id.startswith("A"):
                author_id = f"https://openalex.org/{author_id}"

            author = Authors()[author_id]
            return {
                "id": author.get("id", ""),
                "display_name": author.get("display_name", ""),
                "works_count": author.get("works_count", 0),
                "cited_by_count": author.get("cited_by_count", 0),
                "affiliation": (
                    author.get("last_known_institutions", [{}])[0].get(
                        "display_name", ""
                    )
                    if author.get("last_known_institutions")
                    else ""
                ),
                "h_index": author.get("summary_stats", {}).get("h_index", 0),
                "orcid": author.get("orcid", ""),
            }
        except Exception as e:
            return {"error": True, "message": str(e)}

    def search_institutions(
        self, query: str, max_results: int = 10
    ) -> Dict[str, Any]:
        """Search for institutions."""
        try:
            results = Institutions().search(query).get()[:max_results]

            parsed = []
            for inst in results:
                parsed.append(
                    {
                        "id": inst.get("id", ""),
                        "display_name": inst.get("display_name", ""),
                        "country_code": inst.get("country_code", ""),
                        "type": inst.get("type", ""),
                        "works_count": inst.get("works_count", 0),
                        "cited_by_count": inst.get("cited_by_count", 0),
                        "homepage_url": inst.get("homepage_url", ""),
                    }
                )

            return {"meta": {"count": len(parsed)}, "results": parsed}
        except Exception as e:
            return {"error": True, "message": str(e)}

    def get_trends(
        self,
        topic: str,
        year_start: Optional[int] = None,
        year_end: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get publication count trends for a topic over time."""
        if year_start is None:
            year_start = datetime.now().year - 10
        if year_end is None:
            year_end = datetime.now().year

        yearly_data = []
        for year in range(year_start, year_end + 1):
            try:
                works_query = (
                    Works()
                    .search(topic)
                    .filter(publication_year=year)
                )
                # Use group_by to get count efficiently, or just get page 1
                results = works_query.get()
                # pyalex returns up to 25 by default but meta has total count
                # Access the count from the paginator
                count = len(results)
                # Try to get actual count from the API response
                if hasattr(results, '_json') and 'meta' in results._json:
                    count = results._json['meta'].get('count', count)
                yearly_data.append({"year": year, "count": count})
            except Exception:
                yearly_data.append({"year": year, "count": 0, "error": True})

        return {
            "topic": topic,
            "year_range": f"{year_start}-{year_end}",
            "trends": yearly_data,
        }

    def get_highly_cited(
        self,
        topic: str,
        min_citations: int = 100,
        max_results: int = 25,
        year: Optional[int] = None,
        is_oa: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get highly cited papers in a field."""
        try:
            works_query = Works().search(topic).filter(
                cited_by_count=f">{min_citations}"
            )

            if year:
                works_query = works_query.filter(publication_year=year)
            if is_oa is not None:
                works_query = works_query.filter(is_oa=is_oa)

            works_query = works_query.sort(cited_by_count="desc")
            results = works_query.get()[:max_results]

            return {
                "meta": {"count": len(results)},
                "results": [self._parse_work(w) for w in results],
            }
        except Exception as e:
            return {"error": True, "message": str(e)}


def output_json(data, output_file=None):
    """Write JSON output to file or stdout."""
    text = json.dumps(data, indent=2, ensure_ascii=False)
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
            f.write("\n")
        print(f"Results written to {output_file}", file=sys.stderr)
    else:
        print(text)


def main():
    parser = argparse.ArgumentParser(
        description="OpenAlex API client for scholarly data retrieval.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for papers
  %(prog)s search "transformer attention mechanism"

  # Get papers citing a specific work
  %(prog)s citations W2741809807

  # Search authors
  %(prog)s author --search "Yoshua Bengio"

  # Get works by an author
  %(prog)s author --id A5023888391 --works

  # Search institutions
  %(prog)s institution "Stanford University"

  # Publication trends for a topic
  %(prog)s trends "large language models" --from 2018 --to 2025

  # Highly cited papers
  %(prog)s highly-cited "reinforcement learning" --min-citations 500

  # Use polite pool (faster rate limit)
  %(prog)s --mailto user@example.com search "graph neural networks"
        """,
    )

    parser.add_argument(
        "--mailto",
        type=str,
        default=None,
        help="Email for OpenAlex polite pool (faster rate limiting)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Write JSON output to file instead of stdout",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- search subcommand ---
    search_parser = subparsers.add_parser(
        "search", help="Search papers by title, abstract, or topic"
    )
    search_parser.add_argument("query", type=str, help="Search query")
    search_parser.add_argument(
        "--max", "-m", type=int, default=25, dest="max_results",
        help="Maximum number of results (default: 25)",
    )
    search_parser.add_argument(
        "--sort", "-s", type=str, default=None,
        help="Sort field (e.g., 'cited_by_count', 'publication_date')",
    )
    search_parser.add_argument(
        "--year", type=str, default=None,
        help="Filter by publication year (e.g., '2024' or '2020-2024')",
    )
    search_parser.add_argument(
        "--oa", action="store_true", default=False,
        help="Only return Open Access papers",
    )
    search_parser.add_argument(
        "--type", type=str, default=None, dest="work_type",
        help="Filter by work type (e.g., 'journal-article', 'proceedings-article')",
    )

    # --- citations subcommand ---
    citations_parser = subparsers.add_parser(
        "citations", help="Get papers citing or cited by a work"
    )
    citations_parser.add_argument(
        "work_id", type=str,
        help="OpenAlex ID, DOI, or other supported identifier",
    )
    citations_parser.add_argument(
        "--direction", type=str, choices=["citing", "cited_by"],
        default="citing",
        help="'citing' = papers that cite this work; 'cited_by' = references of this work",
    )
    citations_parser.add_argument(
        "--max", "-m", type=int, default=25, dest="max_results",
        help="Maximum results",
    )
    citations_parser.add_argument(
        "--sort", "-s", type=str, default=None,
        help="Sort field (e.g., 'cited_by_count')",
    )

    # --- author subcommand ---
    author_parser = subparsers.add_parser(
        "author", help="Search authors or get author works"
    )
    author_parser.add_argument(
        "--search", type=str, default=None,
        help="Search authors by name",
    )
    author_parser.add_argument(
        "--id", type=str, default=None, dest="author_id",
        help="OpenAlex author ID to look up works for",
    )
    author_parser.add_argument(
        "--works", action="store_true", default=False,
        help="Get works by the author (requires --id)",
    )
    author_parser.add_argument(
        "--max", "-m", type=int, default=25, dest="max_results",
        help="Maximum results",
    )
    author_parser.add_argument(
        "--sort", "-s", type=str, default=None,
        help="Sort field for works",
    )

    # --- institution subcommand ---
    inst_parser = subparsers.add_parser(
        "institution", help="Search institutions"
    )
    inst_parser.add_argument("query", type=str, help="Institution name to search")
    inst_parser.add_argument(
        "--max", "-m", type=int, default=10, dest="max_results",
        help="Maximum results",
    )

    # --- trends subcommand ---
    trends_parser = subparsers.add_parser(
        "trends", help="Publication count trends for a topic over time"
    )
    trends_parser.add_argument("topic", type=str, help="Topic to analyze")
    trends_parser.add_argument(
        "--from", type=int, default=None, dest="year_start",
        help="Start year (default: 10 years ago)",
    )
    trends_parser.add_argument(
        "--to", type=int, default=None, dest="year_end",
        help="End year (default: current year)",
    )

    # --- highly-cited subcommand ---
    hc_parser = subparsers.add_parser(
        "highly-cited", help="Get highly cited papers in a field"
    )
    hc_parser.add_argument("topic", type=str, help="Topic to search")
    hc_parser.add_argument(
        "--min-citations", type=int, default=100,
        help="Minimum citation count (default: 100)",
    )
    hc_parser.add_argument(
        "--max", "-m", type=int, default=25, dest="max_results",
        help="Maximum results",
    )
    hc_parser.add_argument(
        "--year", type=int, default=None,
        help="Filter by publication year",
    )
    hc_parser.add_argument(
        "--oa", action="store_true", default=False,
        help="Only return Open Access papers",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    client = OpenAlexClient(mailto=args.mailto)

    if args.command == "search":
        result = client.search_works(
            query=args.query,
            max_results=args.max_results,
            sort_field=args.sort,
            year=args.year,
            is_oa=True if args.oa else None,
            work_type=args.work_type,
        )
        result["query"] = args.query
        result["retrieved_at"] = datetime.now().isoformat()
        output_json(result, args.output)

    elif args.command == "citations":
        if args.direction == "citing":
            result = client.get_citations(
                args.work_id,
                max_results=args.max_results,
                sort_field=args.sort,
            )
        else:
            result = client.get_references(
                args.work_id, max_results=args.max_results
            )
        result["work_id"] = args.work_id
        result["direction"] = args.direction
        result["retrieved_at"] = datetime.now().isoformat()
        output_json(result, args.output)

    elif args.command == "author":
        if args.author_id and args.works:
            result = client.get_author_works(
                args.author_id,
                max_results=args.max_results,
                sort_field=args.sort,
            )
            result["author_id"] = args.author_id
        elif args.search:
            result = client.search_authors(
                args.search, max_results=args.max_results
            )
            result["query"] = args.search
        elif args.author_id:
            result = client.get_author_info(args.author_id)
        else:
            print(
                "Error: --search or --id is required for author command",
                file=sys.stderr,
            )
            sys.exit(1)
        result["retrieved_at"] = datetime.now().isoformat()
        output_json(result, args.output)

    elif args.command == "institution":
        result = client.search_institutions(
            args.query, max_results=args.max_results
        )
        result["query"] = args.query
        result["retrieved_at"] = datetime.now().isoformat()
        output_json(result, args.output)

    elif args.command == "trends":
        result = client.get_trends(
            args.topic,
            year_start=args.year_start,
            year_end=args.year_end,
        )
        result["retrieved_at"] = datetime.now().isoformat()
        output_json(result, args.output)

    elif args.command == "highly-cited":
        result = client.get_highly_cited(
            topic=args.topic,
            min_citations=args.min_citations,
            max_results=args.max_results,
            year=args.year,
            is_oa=True if args.oa else None,
        )
        result["query"] = args.topic
        result["min_citations"] = args.min_citations
        result["retrieved_at"] = datetime.now().isoformat()
        output_json(result, args.output)


if __name__ == "__main__":
    main()
