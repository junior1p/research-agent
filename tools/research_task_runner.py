#!/usr/bin/env python3
"""
research_task_runner.py - CLI entry point for sub-agents.

This script is the main entry point for sub-agents spawned by Hermes.
It reads the task from the shared knowledge base, determines which role
to execute, and runs the appropriate agent.

Usage:
    python research_task_runner.py literature_search "CRISPR gene editing"
    python research_task_runner.py paper_analyze
    python research_task_runner.py review_writer
    python research_task_runner.py idea_generator
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.delegate_tools import (
    read_shared,
    write_shared,
    get_task_info,
    report_complete,
    init_task,
    get_results_dir,
    write_result,
    get_task_id,
)

# Base directory
BASE_DIR = Path(__file__).parent.parent


def load_role_prompt(role_name: str) -> str:
    """Load the system prompt for a given role."""
    role_file = BASE_DIR / "roles" / f"{role_name}.py"
    if role_file.exists():
        with open(role_file, "r", encoding="utf-8") as f:
            content = f.read()
        # Extract docstring if present
        lines = content.strip().split("\n")
        docstring_lines = []
        in_docstring = False
        for line in lines:
            if '"""' in line or "'''" in line:
                if not in_docstring:
                    in_docstring = True
                    # Handle single-line docstring
                    if line.count('"""') == 2 or line.count("'''") == 2:
                        docstring_lines.append(line)
                        break
                else:
                    docstring_lines.append(line)
                    break
            elif in_docstring:
                docstring_lines.append(line)
        
        if docstring_lines:
            docstring = "\n".join(docstring_lines).strip()
            if docstring:
                return docstring
    
    # Fallback: return basic role description
    role_descriptions = {
        "literature_searcher": "You are an academic literature search expert. Search comprehensively for papers on the given research topic using web search.",
        "paper_analyzer": "You are a biomedical paper analysis expert. Analyze academic papers and extract key insights.",
        "review_writer": "You are an academic writing expert specializing in literature reviews. Synthesize analyzed papers into a coherent literature review.",
        "idea_generator": "You are an innovative research idea generator. Propose novel research directions based on literature gaps.",
    }
    return role_descriptions.get(role_name, f"You are a {role_name} agent.")


# =============================================================================
# LITERATURE SEARCH AGENT
# =============================================================================

def run_literature_search(topic: str, task_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Run the literature search agent.
    
    Searches academic databases for relevant papers and saves results.
    """
    print(f"[Literature Search Agent] Starting search for: {topic}")
    
    # This function would typically use web_search to query databases
    # For now, it creates a template that the actual agent fills in
    result = {
        "topic": topic,
        "query_used": _build_search_query(topic),
        "papers": [],
        "search_summary": "Papers will be populated by the agent",
        "status": "in_progress",
        "started_at": datetime.now().isoformat()
    }
    
    # Save initial result
    filepath = write_shared("literature", result, task_id)
    print(f"[Literature Search Agent] Initial result saved to: {filepath}")
    
    return result


def _build_search_query(topic: str) -> str:
    """Build a search query from a topic."""
    # Simple query builder - could be enhanced with NLP
    return f'"{topic}" AND (review OR systematic review OR meta-analysis)'


# =============================================================================
# PAPER ANALYZER AGENT
# =============================================================================

def run_paper_analyze(task_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Run the paper analyzer agent.
    
    Reads literature search results and produces deep analysis.
    """
    print(f"[Paper Analyzer Agent] Starting analysis")
    
    # Read literature search results
    lit_data = read_shared("literature", task_id)
    if not lit_data:
        print("[Paper Analyzer Agent] No literature data found!")
        return {"error": "No literature data found. Run literature search first."}
    
    topic = lit_data.get("topic", "Unknown")
    papers = lit_data.get("papers", [])
    
    result = {
        "topic": topic,
        "analyzed_papers": [],
        "thematic_clusters": {},
        "overall_research_gaps": [],
        "status": "in_progress",
        "started_at": datetime.now().isoformat()
    }
    
    # Save initial result
    filepath = write_shared("analysis", result, task_id)
    print(f"[Paper Analyzer Agent] Initial result saved to: {filepath}")
    
    return result


# =============================================================================
# REVIEW WRITER AGENT
# =============================================================================

def run_review_writer(task_id: Optional[str] = None) -> str:
    """
    Run the review writer agent.
    
    Reads paper analysis and writes a structured literature review.
    """
    print(f"[Review Writer Agent] Starting review writing")
    
    # Read paper analysis
    analysis_data = read_shared("analysis", task_id)
    if not analysis_data:
        print("[Review Writer Agent] No analysis data found!")
        return "Error: No analysis data found. Run paper analysis first."
    
    topic = analysis_data.get("topic", "Unknown")
    
    # Create literature review template
    review = f"""# Literature Review: {topic}

*Generated: {datetime.now().strftime('%Y-%m-%d')}*

## Introduction

This literature review examines the current state of research on **{topic}**.
The review synthesizes findings from recent academic publications to provide
a comprehensive overview of the field.

*(This is a template - detailed content to be filled by the agent)*

## Key Themes

*(Thematic synthesis to be added)*

## Methodology Overview

*(Methodological approaches in the field)*

## Research Gaps

*(Identified gaps in current research)*

## Conclusions

*(Summary and future directions)*

---

*This literature review was generated by the Hermes Research Agent System.*
"""
    
    # Save to results directory
    results_dir = get_results_dir(task_id)
    filepath = results_dir / "literature_review.md"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(review)
    
    print(f"[Review Writer Agent] Review saved to: {filepath}")
    
    # Also save reference in shared
    write_shared("review", {
        "topic": topic,
        "review_file": str(filepath),
        "status": "completed",
        "completed_at": datetime.now().isoformat()
    }, task_id)
    
    return str(filepath)


# =============================================================================
# IDEA GENERATOR AGENT
# =============================================================================

def run_idea_generator(task_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Run the idea generator agent.
    
    Reads analysis and research gaps, proposes novel research directions.
    """
    print(f"[Idea Generator Agent] Starting idea generation")
    
    # Read paper analysis
    analysis_data = read_shared("analysis", task_id)
    if not analysis_data:
        print("[Idea Generator Agent] No analysis data found!")
        return {"error": "No analysis data found. Run paper analysis first."}
    
    topic = analysis_data.get("topic", "Unknown")
    gaps = analysis_data.get("overall_research_gaps", [])
    
    result = {
        "topic": topic,
        "proposed_ideas": [],
        "status": "in_progress",
        "started_at": datetime.now().isoformat()
    }
    
    # Save initial result
    filepath = write_shared("ideas", result, task_id)
    print(f"[Idea Generator Agent] Initial result saved to: {filepath}")
    
    return result


# =============================================================================
# MAIN DISPATCHER
# =============================================================================

def main():
    """Main entry point - dispatch to appropriate agent."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python research_task_runner.py init \"<topic>\"")
        print("  python research_task_runner.py literature_search \"<topic>\"")
        print("  python research_task_runner.py paper_analyze")
        print("  python research_task_runner.py review_writer")
        print("  python research_task_runner.py idea_generator")
        print("  python research_task_runner.py status")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "init":
        if len(sys.argv) < 3:
            print("Error: Topic required")
            print("Usage: python research_task_runner.py init \"<topic>\"")
            sys.exit(1)
        topic = sys.argv[2]
        task_id = sys.argv[3] if len(sys.argv) > 3 else None
        tid = init_task(topic, task_id)
        print(f"Initialized task: {tid}")
        print(f"Topic: {topic}")
        
    elif command == "literature_search":
        if len(sys.argv) < 3:
            print("Error: Topic required")
            print("Usage: python research_task_runner.py literature_search \"<topic>\"")
            sys.exit(1)
        topic = sys.argv[2]
        task_id = sys.argv[3] if len(sys.argv) > 3 else None
        
        # Ensure task is initialized
        if not get_task_id():
            init_task(topic, task_id)
        
        result = run_literature_search(topic, task_id)
        report_complete("literature_search", f"Found {len(result.get('papers', []))} papers on '{topic}'", task_id)
        print(f"[Complete] Literature search for '{topic}'")
        
    elif command == "paper_analyze":
        task_id = sys.argv[2] if len(sys.argv) > 2 else None
        result = run_paper_analyze(task_id)
        
        if "error" not in result:
            analyzed = len(result.get("analyzed_papers", []))
            report_complete("paper_analyzer", f"Analyzed {analyzed} papers", task_id)
            print(f"[Complete] Paper analysis")
        else:
            print(f"[Error] {result.get('error')}")
        
    elif command == "review_writer":
        task_id = sys.argv[2] if len(sys.argv) > 2 else None
        filepath = run_review_writer(task_id)
        report_complete("review_writer", f"Literature review written to {filepath}", task_id)
        print(f"[Complete] Review written to: {filepath}")
        
    elif command == "idea_generator":
        task_id = sys.argv[2] if len(sys.argv) > 2 else None
        result = run_idea_generator(task_id)
        
        if "error" not in result:
            ideas_count = len(result.get("proposed_ideas", []))
            report_complete("idea_generator", f"Proposed {ideas_count} research ideas", task_id)
            print(f"[Complete] Idea generation")
        else:
            print(f"[Error] {result.get('error')}")
        
    elif command == "status":
        task_id = sys.argv[2] if len(sys.argv) > 2 else None
        task_info = get_task_info(task_id)
        print(f"Task ID: {task_info.get('task_id', 'unknown')}")
        print(f"Topic: {task_info.get('topic', 'unknown')}")
        print(f"Status: {task_info.get('status', 'unknown')}")
        print(f"Completed agents: {len(task_info.get('agents_completed', []))}")
        for agent in task_info.get("agents_completed", []):
            print(f"  - {agent['agent']}: {agent['summary']}")
        
    else:
        print(f"Unknown command: {command}")
        print("Available commands: init, literature_search, paper_analyze, review_writer, idea_generator, status")
        sys.exit(1)


if __name__ == "__main__":
    main()
