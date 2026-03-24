#!/usr/bin/env python3
"""
Papers With Code API Client for Research Validator.

Provides SOTA verification, paper-code mapping, method/dataset/task search,
and leaderboard retrieval via the Papers With Code API.

API documentation: https://paperswithcode.com/api/v1/docs/

IMPORTANT LIMITATION (as of 2026-03):
The Papers With Code API (paperswithcode.com/api/v1) redirects all requests
to Hugging Face (huggingface.co). The API appears to be defunct following
the Hugging Face acquisition. This client attempts the original API endpoints
and returns structured error information when they fail.

Fallback strategy for SOTA verification:
  1. Use WebFetch to scrape huggingface.co/papers for paper search
  2. Use semantic_scholar.py for citation-based verification
  3. Use arxiv_search.py for recent papers on specific benchmarks
  4. Manual verification via conference proceedings
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote

try:
    import requests
except ImportError:
    print(
        "Error: 'requests' library is required. Install it with:\n"
        "  uv sync",
        file=sys.stderr,
    )
    sys.exit(1)


class PapersWithCodeClient:
    """Client for interacting with the Papers With Code API.

    Note: As of 2026-03, the Papers With Code API redirects to Hugging Face.
    This client attempts requests but will return structured error responses
    when the API is unavailable. Use the fallback recommendations in error
    messages for alternative data sources.
    """

    BASE_URL = "https://paperswithcode.com/api/v1"

    def __init__(self, throttle: float = 1.0):
        """
        Initialize the client.

        Args:
            throttle: Minimum seconds between requests (default: 1.0).
        """
        self.throttle = throttle
        self._last_request_time: float = 0.0
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "ResearchValidator/1.0"
        self.session.headers["Accept"] = "application/json"
        # Track whether the API is available (set False on first redirect)
        self._api_available: Optional[bool] = None

    def _rate_limit(self) -> None:
        """Enforce minimum interval between requests."""
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed < self.throttle:
            time.sleep(self.throttle - elapsed)
        self._last_request_time = time.monotonic()

    @staticmethod
    def _api_unavailable_error(endpoint: str) -> Dict[str, Any]:
        """Return a structured error for when the API is unavailable."""
        return {
            "error": True,
            "status": "api_unavailable",
            "message": (
                f"Papers With Code API is unavailable (redirects to Hugging Face). "
                f"Attempted endpoint: {endpoint}"
            ),
            "fallback": (
                "Use these alternatives for SOTA verification:\n"
                "  1. WebFetch https://huggingface.co/papers?search=<query>\n"
                "  2. semantic_scholar.py search '<task> state of the art'\n"
                "  3. arxiv_search.py '<task> benchmark' --sort relevance\n"
                "  4. WebSearch '<task> <dataset> leaderboard site:paperswithcode.com'\n"
                "     (cached pages may still be indexed by search engines)"
            ),
        }

    def _get(
        self, url: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a rate-limited GET request and return parsed JSON.

        Handles the common case where the API redirects to Hugging Face
        by detecting redirects and returning a structured error.
        """
        # Short-circuit if we already know the API is down
        if self._api_available is False:
            return self._api_unavailable_error(url)

        self._rate_limit()
        try:
            resp = self.session.get(
                url, params=params, timeout=30, allow_redirects=False
            )

            # Detect redirect (API is defunct)
            if resp.status_code in (301, 302, 303, 307, 308):
                self._api_available = False
                location = resp.headers.get("Location", "unknown")
                return {
                    "error": True,
                    "status": resp.status_code,
                    "message": (
                        f"Papers With Code API redirected to {location}. "
                        f"The API appears to be defunct."
                    ),
                    "fallback": self._api_unavailable_error(url)["fallback"],
                }

            resp.raise_for_status()
            self._api_available = True
            return resp.json()

        except requests.exceptions.HTTPError as e:
            status = (
                e.response.status_code if e.response is not None else "unknown"
            )
            body = ""
            if e.response is not None:
                try:
                    body = e.response.json().get(
                        "message", e.response.text[:200]
                    )
                except Exception:
                    body = e.response.text[:200]
            return {"error": True, "status": status, "message": str(body)}
        except requests.exceptions.RequestException as e:
            return {"error": True, "message": str(e)}

    # ---- Task search ----

    def search_tasks(
        self, query: str, limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search for ML tasks by name.

        Args:
            query: Task name to search (e.g., "image classification").
            limit: Maximum number of results.

        API endpoint: GET /v1/tasks/?q={query}
        """
        params: Dict[str, Any] = {
            "q": query,
            "items_per_page": min(limit, 50),
            "format": "json",
        }
        data = self._get(f"{self.BASE_URL}/tasks/", params=params)
        if data.get("error"):
            return data

        results = []
        for task in data.get("results", []):
            results.append({
                "id": task.get("id", ""),
                "name": task.get("name", ""),
                "description": task.get("description", "")[:200],
                "paper_count": task.get("paper_count", 0),
                "url": f"https://paperswithcode.com/task/{task.get('id', '')}",
            })

        return {
            "meta": {
                "total": data.get("count", len(results)),
                "count": len(results),
            },
            "results": results,
        }

    # ---- SOTA / Evaluations ----

    def get_sota(
        self, task: str, dataset: Optional[str] = None, limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get state-of-the-art results for a task, optionally filtered by dataset.

        Args:
            task: Task ID/slug (e.g., "image-classification").
            dataset: Optional dataset name to filter by.
            limit: Maximum number of evaluation results.

        API endpoint: GET /v1/evaluations/?task={task}
        """
        params: Dict[str, Any] = {
            "format": "json",
            "items_per_page": min(limit, 50),
        }

        # Try the evaluations endpoint with task filter
        # The API may support /v1/tasks/{task}/evaluations/ or
        # /v1/evaluations/?task={task}
        url = f"{self.BASE_URL}/evaluations/"
        params["task"] = task
        if dataset:
            params["dataset"] = dataset

        data = self._get(url, params=params)
        if data.get("error"):
            # Try alternative endpoint pattern
            alt_url = f"{self.BASE_URL}/tasks/{quote(task, safe='')}/evaluations/"
            alt_params = {
                "format": "json",
                "items_per_page": min(limit, 50),
            }
            if dataset:
                alt_params["dataset"] = dataset

            data = self._get(alt_url, params=alt_params)
            if data.get("error"):
                return data

        results = []
        for evaluation in data.get("results", []):
            entry = {
                "id": evaluation.get("id", ""),
                "task": evaluation.get("task", task),
                "dataset": evaluation.get("dataset", ""),
                "metric": evaluation.get("metric", ""),
            }
            # Include SOTA rows if present
            rows = evaluation.get("rows", evaluation.get("results", []))
            if isinstance(rows, list):
                entry["results"] = []
                for row in rows[:limit]:
                    entry["results"].append({
                        "rank": row.get("rank"),
                        "model": row.get("model_name", row.get("model", "")),
                        "score": row.get("metric_value", row.get("score")),
                        "paper": row.get("paper_title", row.get("paper", "")),
                        "paper_url": row.get("paper_url", ""),
                        "code_url": row.get("code_link", row.get("code_url", "")),
                    })
            results.append(entry)

        return {
            "meta": {
                "total": data.get("count", len(results)),
                "count": len(results),
                "task": task,
                "dataset": dataset,
            },
            "results": results,
        }

    # ---- Paper -> Code repository mapping ----

    def get_paper_repos(
        self, paper_id: str
    ) -> Dict[str, Any]:
        """
        Get code repositories for a paper.

        Args:
            paper_id: Paper ID or slug on Papers With Code.

        API endpoint: GET /v1/papers/{paper_id}/repositories/
        """
        url = f"{self.BASE_URL}/papers/{quote(paper_id, safe='')}/repositories/"
        params = {"format": "json"}

        data = self._get(url, params=params)
        if data.get("error"):
            return data

        repos = []
        for repo in data.get("results", []):
            repos.append({
                "url": repo.get("url", ""),
                "owner": repo.get("owner", ""),
                "name": repo.get("name", ""),
                "stars": repo.get("stars", 0),
                "framework": repo.get("framework", ""),
                "is_official": repo.get("is_official", False),
            })

        return {
            "meta": {
                "paper_id": paper_id,
                "count": len(repos),
            },
            "results": repos,
        }

    # ---- Method search ----

    def search_methods(
        self, query: str, limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search for ML methods.

        Args:
            query: Method name or keyword (e.g., "attention", "resnet").
            limit: Maximum number of results.

        API endpoint: GET /v1/methods/?q={query}
        """
        params: Dict[str, Any] = {
            "q": query,
            "items_per_page": min(limit, 50),
            "format": "json",
        }

        data = self._get(f"{self.BASE_URL}/methods/", params=params)
        if data.get("error"):
            return data

        results = []
        for method in data.get("results", []):
            results.append({
                "id": method.get("id", ""),
                "name": method.get("name", ""),
                "full_name": method.get("full_name", ""),
                "description": method.get("description", "")[:200],
                "paper": method.get("paper", {}).get("title", "")
                if isinstance(method.get("paper"), dict)
                else "",
                "url": f"https://paperswithcode.com/method/{method.get('id', '')}",
            })

        return {
            "meta": {
                "total": data.get("count", len(results)),
                "count": len(results),
            },
            "results": results,
        }

    # ---- Dataset search ----

    def search_datasets(
        self, query: str, limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search for datasets.

        Args:
            query: Dataset name or keyword (e.g., "imagenet", "squad").
            limit: Maximum number of results.

        API endpoint: GET /v1/datasets/?q={query}
        """
        params: Dict[str, Any] = {
            "q": query,
            "items_per_page": min(limit, 50),
            "format": "json",
        }

        data = self._get(f"{self.BASE_URL}/datasets/", params=params)
        if data.get("error"):
            return data

        results = []
        for ds in data.get("results", []):
            results.append({
                "id": ds.get("id", ""),
                "name": ds.get("name", ""),
                "full_name": ds.get("full_name", ds.get("name", "")),
                "description": ds.get("description", "")[:200],
                "paper_count": ds.get("num_papers", ds.get("paper_count", 0)),
                "url": f"https://paperswithcode.com/dataset/{ds.get('id', '')}",
            })

        return {
            "meta": {
                "total": data.get("count", len(results)),
                "count": len(results),
            },
            "results": results,
        }


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
        description="Papers With Code API client for SOTA verification "
                    "and paper-code mapping.\n\n"
                    "NOTE: The PwC API (paperswithcode.com/api/v1) currently "
                    "redirects to Hugging Face and may be unavailable. "
                    "Fallback recommendations are included in error output.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for ML tasks
  %(prog)s tasks "image classification" --limit 5

  # Get SOTA results for a task
  %(prog)s sota "image-classification" --dataset imagenet

  # Get code repos for a paper
  %(prog)s paper-code "attention-is-all-you-need"

  # Search for methods
  %(prog)s methods "transformer" --limit 5

  # Search for datasets
  %(prog)s datasets "imagenet" --limit 5

Fallback (if API is unavailable):
  Use WebFetch with Hugging Face or cached search engine results:
    WebFetch https://huggingface.co/papers?search=<query>
    WebSearch "<task> <dataset> leaderboard site:paperswithcode.com"
        """,
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Write JSON output to file instead of stdout",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- tasks subcommand ---
    tasks_parser = subparsers.add_parser(
        "tasks", help="Search for ML tasks by name"
    )
    tasks_parser.add_argument("query", type=str, help="Task name to search")
    tasks_parser.add_argument(
        "--limit", "-l", type=int, default=10,
        help="Maximum number of results (default: 10)",
    )

    # --- sota subcommand ---
    sota_parser = subparsers.add_parser(
        "sota", help="Get SOTA results for a task/benchmark"
    )
    sota_parser.add_argument(
        "task", type=str,
        help="Task ID/slug (e.g., 'image-classification')",
    )
    sota_parser.add_argument(
        "--dataset", "-d", type=str, default=None,
        help="Filter by dataset name",
    )
    sota_parser.add_argument(
        "--limit", "-l", type=int, default=10,
        help="Maximum number of results (default: 10)",
    )

    # --- paper-code subcommand ---
    papercode_parser = subparsers.add_parser(
        "paper-code", help="Get code repositories for a paper"
    )
    papercode_parser.add_argument(
        "paper_id", type=str,
        help="Paper ID or slug on Papers With Code",
    )

    # --- methods subcommand ---
    methods_parser = subparsers.add_parser(
        "methods", help="Search for ML methods"
    )
    methods_parser.add_argument(
        "query", type=str, help="Method name or keyword"
    )
    methods_parser.add_argument(
        "--limit", "-l", type=int, default=10,
        help="Maximum number of results (default: 10)",
    )

    # --- datasets subcommand ---
    datasets_parser = subparsers.add_parser(
        "datasets", help="Search for datasets"
    )
    datasets_parser.add_argument(
        "query", type=str, help="Dataset name or keyword"
    )
    datasets_parser.add_argument(
        "--limit", "-l", type=int, default=10,
        help="Maximum number of results (default: 10)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    client = PapersWithCodeClient()

    if args.command == "tasks":
        result = client.search_tasks(
            query=args.query,
            limit=args.limit,
        )
        if not result.get("error"):
            result["query"] = args.query
        result["retrieved_at"] = datetime.now().isoformat()
        output_json(result, args.output)

    elif args.command == "sota":
        result = client.get_sota(
            task=args.task,
            dataset=args.dataset,
            limit=args.limit,
        )
        if not result.get("error"):
            result["query_task"] = args.task
            if args.dataset:
                result["query_dataset"] = args.dataset
        result["retrieved_at"] = datetime.now().isoformat()
        output_json(result, args.output)

    elif args.command == "paper-code":
        result = client.get_paper_repos(
            paper_id=args.paper_id,
        )
        if not result.get("error"):
            result["query_paper_id"] = args.paper_id
        result["retrieved_at"] = datetime.now().isoformat()
        output_json(result, args.output)

    elif args.command == "methods":
        result = client.search_methods(
            query=args.query,
            limit=args.limit,
        )
        if not result.get("error"):
            result["query"] = args.query
        result["retrieved_at"] = datetime.now().isoformat()
        output_json(result, args.output)

    elif args.command == "datasets":
        result = client.search_datasets(
            query=args.query,
            limit=args.limit,
        )
        if not result.get("error"):
            result["query"] = args.query
        result["retrieved_at"] = datetime.now().isoformat()
        output_json(result, args.output)


if __name__ == "__main__":
    main()
