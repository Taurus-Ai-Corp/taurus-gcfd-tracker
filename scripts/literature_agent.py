#!/usr/bin/env python3
"""GCFD Literature Research Agent — arXiv/PubMed/Scholar search with persistent memory.

Adapted from the arxiv_researcher_agent_with_memori project.
Searches academic sources for EEG, neuroscience, and cross-frequency coupling literature.

Usage:
    # Research mode — search for papers
    python scripts/literature_agent.py "theta-gamma phase coupling EEG biomarker"

    # Memory mode — recall past searches
    python scripts/literature_agent.py --memory "what did we find about PLV algorithms"

Requirements:
    pip install -r scripts/requirements-agent.txt

Environment:
    Copy scripts/.env.example to scripts/.env and fill in API keys.
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from textwrap import dedent

from dotenv import load_dotenv

# Load .env from scripts directory
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()  # Try default locations

# Lazy imports — check dependencies before failing
try:
    from agents import Agent, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel
    from pydantic import BaseModel
    from tavily import TavilyClient
    from memori import Memori, create_memory_tool
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install -r scripts/requirements-agent.txt")
    sys.exit(1)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LLM Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

api_key = os.getenv("LLM_API_KEY") or os.getenv("NEBIUS_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: Set LLM_API_KEY, NEBIUS_API_KEY, or OPENAI_API_KEY in your environment.")
    sys.exit(1)

model_name = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")
base_url = os.getenv("LLM_BASE_URL", "https://api.studio.nebius.ai/v1")

model = OpenAIChatCompletionsModel(
    model=model_name,
    openai_client=AsyncOpenAI(base_url=base_url, api_key=api_key)
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Pydantic Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class PaperSearchResult(BaseModel):
    query: str
    results: str
    found_papers: bool

class MemorySearchResult(BaseModel):
    query: str
    results: str
    found_memories: bool


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Global instance (required by OpenAI Agents SDK @function_tool pattern)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_agent_instance = None


@function_tool
def search_papers(query: str) -> PaperSearchResult:
    """Search for research papers on arXiv, PubMed, and Google Scholar.

    Args:
        query: Research topic (e.g., "theta-gamma coupling EEG depression biomarker")
    """
    global _agent_instance
    if _agent_instance is None:
        return PaperSearchResult(query=query, results="Agent not initialized", found_papers=False)

    try:
        search_query = f"research papers {query} EEG neuroscience latest findings"
        search_result = _agent_instance.tavily_client.search(
            query=search_query,
            search_depth="advanced",
            include_domains=[
                "arxiv.org",
                "scholar.google.com",
                "pubmed.ncbi.nlm.nih.gov",
                "biorxiv.org",
                "medrxiv.org",
            ],
            max_results=10
        )

        if not search_result.get("results"):
            return PaperSearchResult(query=query, results=f"No papers found for: {query}", found_papers=False)

        papers = []
        for result in search_result["results"][:5]:
            title = result.get("title", "No title")
            url = result.get("url", "")
            content = result.get("content", "")
            summary = content[:200] + "..." if len(content) > 200 else content
            papers.append({"title": title, "url": url, "summary": summary})

        text = f"## Research Papers: {query}\n\nFound {len(papers)} papers:\n\n"
        for i, p in enumerate(papers, 1):
            text += f"### {i}. {p['title']}\n**URL:** {p['url']}\n**Summary:** {p['summary']}\n\n"

        return PaperSearchResult(query=query, results=text, found_papers=True)

    except Exception as e:
        return PaperSearchResult(query=query, results=f"Search error: {e}", found_papers=False)


@function_tool
def search_memory(query: str) -> MemorySearchResult:
    """Search past research sessions for previously found papers and insights.

    Args:
        query: What to recall (e.g., "PLV algorithms", "Posner molecule coherence")
    """
    global _agent_instance
    if _agent_instance is None:
        return MemorySearchResult(query=query, results="Memory not initialized", found_memories=False)

    try:
        result = _agent_instance.memory_tool.execute(query=query.strip())
        found = bool(result and "No relevant memories found" not in result and "Error" not in result)
        return MemorySearchResult(
            query=query,
            results=result if result else "No relevant memories found",
            found_memories=found
        )
    except Exception as e:
        return MemorySearchResult(query=query, results=f"Memory error: {e}", found_memories=False)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Agent Class
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class GCFDLiteratureAgent:
    """Literature research agent specialized for EEG cross-frequency coupling."""

    def __init__(self):
        global _agent_instance
        _agent_instance = self

        db_path = Path(__file__).parent / "gcfd_literature.db"
        self.memori = Memori(
            database_connect=f"sqlite:///{db_path}",
            conscious_ingest=True,
            auto_ingest=True,
            verbose=False,
        )
        self.memori.enable()
        self.memory_tool = create_memory_tool(self.memori)

        tavily_key = os.getenv("TAVILY_API_KEY")
        if not tavily_key:
            print("ERROR: TAVILY_API_KEY not set. Get one at tavily.com")
            sys.exit(1)
        self.tavily_client = TavilyClient(api_key=tavily_key)

        self.research_agent = Agent(
            name="GCFD Literature Agent",
            model=model,
            instructions=dedent("""\
                You are a neuroscience literature research agent specialized in EEG
                cross-frequency coupling, phase synchronization, and theta-gamma coherence.

                Your domain expertise:
                - Phase Locking Value (PLV) methodology
                - Cross-frequency coupling (CFC) and phase-amplitude coupling (PAC)
                - Theta-gamma oscillations in health and disease
                - EEG biomarkers for MDD, Alzheimer's/MCI, epilepsy, ADHD
                - Neurofeedback and brain-computer interfaces
                - Signal processing (Hilbert transform, Butterworth filters, Welch PSD)

                Research workflow:
                1. Check memory for related past research
                2. Search arXiv, PubMed, Scholar for current papers
                3. Cross-reference findings with previous sessions
                4. Structure report: key findings, methodology, implications, future directions
                5. Include proper citations with URLs

                Focus on methodological papers that describe algorithms, not just clinical results.
                Note publication year — prefer recent papers (2020+) but include foundational work.
            """),
            tools=[search_papers, search_memory],
        )

        self.memory_agent = Agent(
            name="GCFD Memory Assistant",
            model=model,
            instructions=dedent("""\
                You help recall past literature research sessions about EEG and neuroscience.
                Search memory, organize results by topic and date, highlight key papers found.
            """),
            tools=[search_memory],
        )

    async def research(self, topic: str) -> str:
        """Run a research query and save to memory."""
        result = await Runner.run(self.research_agent, input=topic)
        response = result.final_output if hasattr(result, "final_output") else str(result)
        self.memori.record_conversation(user_input=topic, ai_output=response)
        return response

    async def recall(self, query: str) -> str:
        """Recall past research from memory."""
        result = await Runner.run(self.memory_agent, input=query)
        return result.final_output if hasattr(result, "final_output") else str(result)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def main():
    parser = argparse.ArgumentParser(description="GCFD Literature Research Agent")
    parser.add_argument("query", nargs="?", help="Research topic or memory query")
    parser.add_argument("--memory", action="store_true", help="Search past research memory instead of new papers")
    args = parser.parse_args()

    if not args.query:
        parser.print_help()
        print("\nExamples:")
        print('  python scripts/literature_agent.py "PLV cross-frequency coupling clinical EEG"')
        print('  python scripts/literature_agent.py --memory "theta-gamma depression"')
        return

    agent = GCFDLiteratureAgent()

    if args.memory:
        print(f"Searching memory for: {args.query}\n")
        result = await agent.recall(args.query)
    else:
        print(f"Researching: {args.query}\n")
        result = await agent.research(args.query)

    print(result)

    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = Path(__file__).parent / "reports"
    report_dir.mkdir(exist_ok=True)
    report_path = report_dir / f"research_{timestamp}.md"
    with open(report_path, 'w') as f:
        f.write(f"# Literature Research: {args.query}\n")
        f.write(f"**Date:** {datetime.now().isoformat()}\n\n")
        f.write(result)
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
