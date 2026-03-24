#!/usr/bin/env python3
"""
Semantic Scholar API Client for Research Validator.

Provides citation graph analysis, paper recommendations, TLDR summaries,
author profiles, and batch paper lookups via the Semantic Scholar Academic
Graph API.

API documentation: https://api.semanticscholar.org/api-docs/graph
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
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


# Default fields to request from the API (keeps responses lean)
DEFAULT_PAPER_FIELDS = (
    "title,abstract,tldr,citationCount,year,venue,authors,"
    "externalIds,url,influentialCitationCount"
)

# Fields for citation/reference context (includes the citing/cited paper info)
CITATION_FIELDS = (
    "title,abstract,tldr,citationCount,year,venue,authors,"
    "externalIds,url,influentialCitationCount"
)

AUTHOR_FIELDS = "name,affiliations,paperCount,citationCount,hIndex,url,externalIds"


class SemanticScholarClient:
    """Client for interacting with the Semantic Scholar Academic Graph API."""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    RECOMMENDATIONS_URL = "https://api.semanticscholar.org/recommendations/v1"

    def __init__(self, api_key: Optional[str] = None, throttle: float = 1.0):
        """
        Initialize the client.

        Args:
            api_key: Optional S2 API key for higher rate limits.
            throttle: Minimum seconds between requests (default: 1.0).
        """
        self.api_key = api_key or os.getenv("S2_API_KEY")
        self.throttle = throttle
        self._last_request_time: float = 0.0
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "ResearchValidator/1.0"
        if self.api_key:
            self.session.headers["x-api-key"] = self.api_key

    def _rate_limit(self) -> None:
        """Enforce minimum interval between requests."""
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed < self.throttle:
            time.sleep(self.throttle - elapsed)
        self._last_request_time = time.monotonic()

    def _get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a rate-limited GET request and return parsed JSON."""
        self._rate_limit()
        try:
            resp = self.session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            body = ""
            if e.response is not None:
                try:
                    body = e.response.json().get("message", e.response.text[:200])
                except Exception:
                    body = e.response.text[:200]
            return {"error": True, "status": status, "message": str(body)}
        except requests.exceptions.RequestException as e:
            return {"error": True, "message": str(e)}

    def _post(self, url: str, json_body: Any, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a rate-limited POST request and return parsed JSON."""
        self._rate_limit()
        try:
            resp = self.session.post(url, json=json_body, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            body = ""
            if e.response is not None:
                try:
                    body = e.response.json().get("message", e.response.text[:200])
                except Exception:
                    body = e.response.text[:200]
            return {"error": True, "status": status, "message": str(body)}
        except requests.exceptions.RequestException as e:
            return {"error": True, "message": str(e)}

    @staticmethod
    def _extract_ids(paper: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """Extract paper IDs (S2, DOI, arXiv) for the verification pipeline."""
        external = paper.get("externalIds") or {}
        return {
            "s2_id": paper.get("paperId"),
            "doi": external.get("DOI"),
            "arxiv_id": external.get("ArXiv"),
        }

    @staticmethod
    def _parse_paper(paper: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a Semantic Scholar paper object into a standardized dict."""
        external = paper.get("externalIds") or {}
        authors = []
        for a in paper.get("authors") or []:
            entry: Dict[str, Any] = {"name": a.get("name", "")}
            if a.get("authorId"):
                entry["authorId"] = a["authorId"]
            authors.append(entry)

        tldr_obj = paper.get("tldr")
        tldr_text = tldr_obj.get("text", "") if isinstance(tldr_obj, dict) else ""

        result: Dict[str, Any] = {
            "paperId": paper.get("paperId", ""),
            "title": paper.get("title", ""),
            "year": paper.get("year"),
            "venue": paper.get("venue", ""),
            "citationCount": paper.get("citationCount", 0),
            "influentialCitationCount": paper.get("influentialCitationCount", 0),
            "authors": authors,
            "url": paper.get("url", ""),
            "externalIds": {
                "DOI": external.get("DOI"),
                "ArXiv": external.get("ArXiv"),
            },
        }

        abstract = paper.get("abstract")
        if abstract:
            result["abstract"] = abstract

        if tldr_text:
            result["tldr"] = tldr_text

        return result

    # ---- Core search and paper details ----

    def search_papers(
        self,
        query: str,
        limit: int = 10,
        year: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search papers by keyword query.

        Args:
            query: Search keywords.
            limit: Maximum number of results (default: 10, API max: 100).
            year: Filter by year, e.g. "2023" or "2020-2024".
            fields: Comma-separated field names (default: DEFAULT_PAPER_FIELDS).
        """
        params: Dict[str, Any] = {
            "query": query,
            "limit": min(limit, 100),
            "fields": fields or DEFAULT_PAPER_FIELDS,
        }
        if year:
            params["year"] = year

        data = self._get(f"{self.BASE_URL}/paper/search", params=params)
        if data.get("error"):
            return data

        papers = [self._parse_paper(p) for p in data.get("data", [])]
        return {
            "meta": {
                "total": data.get("total", len(papers)),
                "count": len(papers),
                "offset": data.get("offset", 0),
            },
            "results": papers,
        }

    def get_paper(
        self,
        paper_id: str,
        fields: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get details for a single paper by ID.

        Args:
            paper_id: S2 paper ID, or prefixed ID like "arxiv:2106.09685",
                      "DOI:10.xxxx/yyyy", "PMID:xxx", etc.
            fields: Comma-separated field names.
        """
        params = {"fields": fields or DEFAULT_PAPER_FIELDS}
        data = self._get(f"{self.BASE_URL}/paper/{paper_id}", params=params)
        if data.get("error"):
            return data
        return self._parse_paper(data)

    # ---- Citation graph ----

    def get_citations(
        self,
        paper_id: str,
        limit: int = 100,
        fields: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get papers that cite this paper (forward citations).

        Args:
            paper_id: S2 paper ID or prefixed ID.
            limit: Maximum number of results (API max per page: 1000).
            fields: Fields for each citing paper.
        """
        params: Dict[str, Any] = {
            "fields": fields or CITATION_FIELDS,
            "limit": min(limit, 1000),
        }
        data = self._get(f"{self.BASE_URL}/paper/{paper_id}/citations", params=params)
        if data.get("error"):
            return data

        papers = []
        for item in data.get("data", []):
            citing = item.get("citingPaper")
            if citing and citing.get("paperId"):
                parsed = self._parse_paper(citing)
                if item.get("isInfluential"):
                    parsed["isInfluential"] = True
                papers.append(parsed)

        return {
            "meta": {"count": len(papers)},
            "results": papers,
        }

    def get_references(
        self,
        paper_id: str,
        limit: int = 100,
        fields: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get papers cited by this paper (backward references).

        Args:
            paper_id: S2 paper ID or prefixed ID.
            limit: Maximum number of results.
            fields: Fields for each referenced paper.
        """
        params: Dict[str, Any] = {
            "fields": fields or CITATION_FIELDS,
            "limit": min(limit, 1000),
        }
        data = self._get(f"{self.BASE_URL}/paper/{paper_id}/references", params=params)
        if data.get("error"):
            return data

        papers = []
        for item in data.get("data", []):
            cited = item.get("citedPaper")
            if cited and cited.get("paperId"):
                parsed = self._parse_paper(cited)
                if item.get("isInfluential"):
                    parsed["isInfluential"] = True
                papers.append(parsed)

        return {
            "meta": {"count": len(papers)},
            "results": papers,
        }

    # ---- Author profiles ----

    def search_authors(
        self,
        query: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Search for authors by name.

        Args:
            query: Author name to search.
            limit: Maximum number of results.
        """
        params: Dict[str, Any] = {
            "query": query,
            "limit": min(limit, 1000),
            "fields": AUTHOR_FIELDS,
        }
        data = self._get(f"{self.BASE_URL}/author/search", params=params)
        if data.get("error"):
            return data

        authors = []
        for a in data.get("data", []):
            authors.append({
                "authorId": a.get("authorId", ""),
                "name": a.get("name", ""),
                "affiliations": a.get("affiliations", []),
                "paperCount": a.get("paperCount", 0),
                "citationCount": a.get("citationCount", 0),
                "hIndex": a.get("hIndex", 0),
                "url": a.get("url", ""),
            })

        return {
            "meta": {
                "total": data.get("total", len(authors)),
                "count": len(authors),
            },
            "results": authors,
        }

    def get_author_papers(
        self,
        author_id: str,
        limit: int = 100,
        fields: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get papers by a specific author.

        Args:
            author_id: Semantic Scholar author ID.
            limit: Maximum number of results.
            fields: Fields for each paper.
        """
        params: Dict[str, Any] = {
            "fields": fields or DEFAULT_PAPER_FIELDS,
            "limit": min(limit, 1000),
        }
        data = self._get(f"{self.BASE_URL}/author/{author_id}/papers", params=params)
        if data.get("error"):
            return data

        papers = [self._parse_paper(p) for p in data.get("data", [])]
        return {
            "meta": {"count": len(papers)},
            "results": papers,
        }

    # ---- Recommendations ----

    def get_recommendations(
        self,
        paper_id: str,
        limit: int = 10,
        fields: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get recommended papers based on a seed paper.

        Args:
            paper_id: S2 paper ID (must be a plain S2 ID, not prefixed).
            limit: Maximum number of results.
            fields: Fields for each recommended paper.
        """
        params: Dict[str, Any] = {
            "fields": fields or DEFAULT_PAPER_FIELDS,
            "limit": min(limit, 500),
        }
        data = self._get(
            f"{self.RECOMMENDATIONS_URL}/papers/forpaper/{paper_id}",
            params=params,
        )
        if data.get("error"):
            return data

        papers = [self._parse_paper(p) for p in data.get("recommendedPapers", [])]
        return {
            "meta": {"count": len(papers)},
            "results": papers,
        }

    # ---- Batch operations ----

    def batch_papers(
        self,
        paper_ids: List[str],
        fields: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Look up multiple papers in a single request (up to 500).

        Args:
            paper_ids: List of paper IDs (S2, arxiv:{id}, DOI:{doi}, etc.).
            fields: Fields for each paper.
        """
        if len(paper_ids) > 500:
            return {
                "error": True,
                "message": f"Batch limit is 500 papers, got {len(paper_ids)}",
            }

        params = {"fields": fields or DEFAULT_PAPER_FIELDS}
        data = self._post(
            f"{self.BASE_URL}/paper/batch",
            json_body={"ids": paper_ids},
            params=params,
        )

        if isinstance(data, dict) and data.get("error"):
            return data

        # Batch returns a list directly
        if isinstance(data, list):
            papers = []
            for p in data:
                if p is not None:
                    papers.append(self._parse_paper(p))
                else:
                    papers.append(None)
            return {
                "meta": {"requested": len(paper_ids), "found": sum(1 for p in papers if p is not None)},
                "results": papers,
            }

        return {"error": True, "message": "Unexpected response format"}


def output_json(data: Any, output_file: Optional[str] = None) -> None:
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
        description="Semantic Scholar API client for citation graph analysis "
                    "and paper recommendations.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for papers
  %(prog)s search "low-rank adaptation" --limit 5

  # Get paper details by S2 ID or arxiv ID
  %(prog)s paper arxiv:2106.09685

  # Forward citations (papers that cite this one)
  %(prog)s citations 649def34f8be52c8b66281af98ae884c09aef38b

  # Backward references (papers cited by this one)
  %(prog)s references arxiv:2106.09685

  # Author search
  %(prog)s author "Edward Hu" --limit 5

  # Paper recommendations
  %(prog)s recommend 649def34f8be52c8b66281af98ae884c09aef38b

  # Batch lookup
  %(prog)s batch "arxiv:2106.09685,DOI:10.18653/v1/N19-1423"
        """,
    )

    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Semantic Scholar API key (or set S2_API_KEY env var)",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Write JSON output to file instead of stdout",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- search subcommand ---
    search_parser = subparsers.add_parser(
        "search", help="Search papers by keyword query"
    )
    search_parser.add_argument("query", type=str, help="Search query keywords")
    search_parser.add_argument(
        "--limit", "-l", type=int, default=10,
        help="Maximum number of results (default: 10, max: 100)",
    )
    search_parser.add_argument(
        "--year", type=str, default=None,
        help="Filter by year (e.g., '2023' or '2020-2024')",
    )
    search_parser.add_argument(
        "--fields", type=str, default=None,
        help="Comma-separated field names to request",
    )

    # --- paper subcommand ---
    paper_parser = subparsers.add_parser(
        "paper", help="Get details for a single paper by ID"
    )
    paper_parser.add_argument(
        "paper_id", type=str,
        help="Paper ID: S2 ID, arxiv:{id}, DOI:{doi}, etc.",
    )
    paper_parser.add_argument(
        "--fields", type=str, default=None,
        help="Comma-separated field names to request",
    )

    # --- citations subcommand ---
    citations_parser = subparsers.add_parser(
        "citations", help="Get forward citations (papers citing this one)"
    )
    citations_parser.add_argument(
        "paper_id", type=str,
        help="Paper ID: S2 ID, arxiv:{id}, DOI:{doi}, etc.",
    )
    citations_parser.add_argument(
        "--limit", "-l", type=int, default=100,
        help="Maximum number of results (default: 100)",
    )
    citations_parser.add_argument(
        "--fields", type=str, default=None,
        help="Comma-separated field names for citing papers",
    )

    # --- references subcommand ---
    references_parser = subparsers.add_parser(
        "references", help="Get backward references (papers cited by this one)"
    )
    references_parser.add_argument(
        "paper_id", type=str,
        help="Paper ID: S2 ID, arxiv:{id}, DOI:{doi}, etc.",
    )
    references_parser.add_argument(
        "--limit", "-l", type=int, default=100,
        help="Maximum number of results (default: 100)",
    )
    references_parser.add_argument(
        "--fields", type=str, default=None,
        help="Comma-separated field names for referenced papers",
    )

    # --- author subcommand ---
    author_parser = subparsers.add_parser(
        "author", help="Search for authors by name"
    )
    author_parser.add_argument("name", type=str, help="Author name to search")
    author_parser.add_argument(
        "--limit", "-l", type=int, default=10,
        help="Maximum number of results (default: 10)",
    )

    # --- recommend subcommand ---
    recommend_parser = subparsers.add_parser(
        "recommend", help="Get paper recommendations based on a seed paper"
    )
    recommend_parser.add_argument(
        "paper_id", type=str,
        help="S2 paper ID for the seed paper",
    )
    recommend_parser.add_argument(
        "--limit", "-l", type=int, default=10,
        help="Maximum number of recommendations (default: 10)",
    )
    recommend_parser.add_argument(
        "--fields", type=str, default=None,
        help="Comma-separated field names for recommended papers",
    )

    # --- batch subcommand ---
    batch_parser = subparsers.add_parser(
        "batch", help="Look up multiple papers in a single request (up to 500)"
    )
    batch_parser.add_argument(
        "ids", type=str,
        help="Comma-separated paper IDs (S2, arxiv:{id}, DOI:{doi})",
    )
    batch_parser.add_argument(
        "--fields", type=str, default=None,
        help="Comma-separated field names to request",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    client = SemanticScholarClient(api_key=args.api_key)

    if args.command == "search":
        result = client.search_papers(
            query=args.query,
            limit=args.limit,
            year=args.year,
            fields=args.fields,
        )
        result["query"] = args.query
        result["retrieved_at"] = datetime.now().isoformat()
        output_json(result, args.output)

    elif args.command == "paper":
        result = client.get_paper(
            paper_id=args.paper_id,
            fields=args.fields,
        )
        result["retrieved_at"] = datetime.now().isoformat()
        output_json(result, args.output)

    elif args.command == "citations":
        result = client.get_citations(
            paper_id=args.paper_id,
            limit=args.limit,
            fields=args.fields,
        )
        result["paper_id"] = args.paper_id
        result["direction"] = "forward"
        result["retrieved_at"] = datetime.now().isoformat()
        output_json(result, args.output)

    elif args.command == "references":
        result = client.get_references(
            paper_id=args.paper_id,
            limit=args.limit,
            fields=args.fields,
        )
        result["paper_id"] = args.paper_id
        result["direction"] = "backward"
        result["retrieved_at"] = datetime.now().isoformat()
        output_json(result, args.output)

    elif args.command == "author":
        result = client.search_authors(
            query=args.name,
            limit=args.limit,
        )
        result["query"] = args.name
        result["retrieved_at"] = datetime.now().isoformat()
        output_json(result, args.output)

    elif args.command == "recommend":
        result = client.get_recommendations(
            paper_id=args.paper_id,
            limit=args.limit,
            fields=args.fields,
        )
        result["seed_paper_id"] = args.paper_id
        result["retrieved_at"] = datetime.now().isoformat()
        output_json(result, args.output)

    elif args.command == "batch":
        paper_ids = [pid.strip() for pid in args.ids.split(",") if pid.strip()]
        result = client.batch_papers(
            paper_ids=paper_ids,
            fields=args.fields,
        )
        result["retrieved_at"] = datetime.now().isoformat()
        output_json(result, args.output)


if __name__ == "__main__":
    main()
