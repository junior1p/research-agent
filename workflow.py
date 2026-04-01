#!/usr/bin/env python3
"""
workflow.py - Main workflow orchestrator for Hermes research agent system.

This module provides a simple serial workflow for testing the research agent
system. In production, the main Hermes agent would use delegate_task to
spawn sub-agents directly.

Usage:
    python workflow.py "lysozyme"
    python workflow.py "CRISPR gene editing"
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.delegate_tools import (
    init_task,
    read_shared,
    write_shared,
    get_task_info,
    report_complete,
    get_results_dir,
    write_result,
    get_task_id,
)
from tools.latex_to_pdf import latex_to_pdf


def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_step(step_num: int, title: str, status: str = "running") -> None:
    """Print a workflow step."""
    icons = {"running": "⏳", "complete": "✅", "error": "❌", "skip": "⏭️"}
    icon = icons.get(status, "•")
    print(f"\n[{step_num}] {icon} {title}")


def run_workflow(topic: str, task_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Run the complete research workflow for a topic.
    
    This executes all 4 sub-agents in sequence:
    1. Literature Search
    2. Paper Analysis
    3. Review Writing
    4. Idea Generation
    
    Args:
        topic: The research topic
        task_id: Optional custom task ID
    
    Returns:
        Dictionary with workflow results
    """
    print_header(f"Research Agent Workflow: {topic}")
    
    # Initialize task
    print("\n[0] 🚀 Initializing research task...")
    tid = init_task(topic, task_id)
    print(f"    Task ID: {tid}")
    
    # Store results
    results = {
        "task_id": tid,
        "topic": topic,
        "started_at": datetime.now().isoformat(),
        "steps": {},
        "outputs": {}
    }
    
    # =========================================================================
    # STEP 1: Literature Search
    # =========================================================================
    print_step(1, "Literature Search Agent", "running")
    try:
        # In production, this would spawn a sub-agent
        # For testing, we simulate with a placeholder result
        literature_data = {
            "topic": topic,
            "query_used": f'"{topic}" AND (review OR systematic review)',
            "papers": _generate_sample_papers(topic),
            "search_summary": f"Found {len(_generate_sample_papers(topic))} papers on '{topic}'"
        }
        write_shared("literature", literature_data, tid)
        report_complete("literature_search", f"Found {len(literature_data['papers'])} papers", tid)
        results["steps"]["literature_search"] = "complete"
        print(f"    ✅ Found {len(literature_data['papers'])} papers")
    except Exception as e:
        print(f"    ❌ Error: {e}")
        results["steps"]["literature_search"] = f"error: {e}"
        return results
    
    # =========================================================================
    # STEP 2: Paper Analysis
    # =========================================================================
    print_step(2, "Paper Analyzer Agent", "running")
    try:
        lit_data = read_shared("literature", tid)
        papers = lit_data.get("papers", [])
        
        analysis_data = {
            "topic": topic,
            "analyzed_papers": [
                {
                    "title": p["title"],
                    "key_findings": [f"Finding about {p['title']}"],
                    "methods": ["Experimental", "Computational"],
                    "limitations": ["Sample size limited", "Single cohort"],
                    "research_gaps": [f"Gap in {p['title']}"],
                    "novelty_score": 7,
                    "methodology_score": 8,
                    "impact_score": 8
                }
                for p in papers[:10]  # Analyze top 10
            ],
            "thematic_clusters": {
                "theme1": [p["title"] for p in papers[:3]],
                "theme2": [p["title"] for p in papers[3:6]]
            },
            "overall_research_gaps": [
                f"Limited understanding of {topic} mechanisms",
                f"Need for larger cohort studies on {topic}",
                "Gap in translational research"
            ],
            "consensus_points": [f"Consensus on importance of {topic}"],
            "debates": ["Debate on optimal approach"]
        }
        
        write_shared("analysis", analysis_data, tid)
        report_complete("paper_analyzer", f"Analyzed {len(analysis_data['analyzed_papers'])} papers", tid)
        results["steps"]["paper_analyzer"] = "complete"
        print(f"    ✅ Analyzed {len(analysis_data['analyzed_papers'])} papers")
    except Exception as e:
        print(f"    ❌ Error: {e}")
        results["steps"]["paper_analyzer"] = f"error: {e}"
        return results
    
    # =========================================================================
    # STEP 3: Review Writing
    # =========================================================================
    print_step(3, "Review Writer Agent", "running")
    try:
        analysis_data = read_shared("analysis", tid)
        gaps = analysis_data.get("overall_research_gaps", [])
        
        gaps_text = "\n".join(f"- {gap}" for gap in gaps)

        review_content = f"""# Literature Review: {topic}

*Generated: {datetime.now().strftime('%Y-%m-%d')}*  
*Task ID: {tid}*

## Introduction

This literature review provides a comprehensive examination of research on **{topic}**.
The field has seen significant advances in recent years, with particular progress in
understanding the fundamental mechanisms and potential applications.

## Overview of Current Research

Based on analysis of recent publications, research on {topic} can be grouped into
several key themes, including mechanistic studies, translational applications, and
methodological advances.

### Key Themes

The literature reveals several major themes in {topic} research:

1. **Mechanistic Understanding**: Studies focusing on the underlying biological
   mechanisms of {topic}.

2. **Methodological Advances**: New techniques and approaches for studying {topic}.

3. **Clinical Translation**: Research aimed at translating findings to practical
   applications.

## Research Findings

Analysis of the literature reveals the following key findings:

- Recent papers emphasize the importance of {topic} in biological systems
- Multiple methodologies are employed, including experimental and computational approaches
- Sample sizes and study designs vary across publications
- Several studies acknowledge limitations in current understanding

## Research Gaps

Despite significant progress, several research gaps remain in the field:

{gaps_text}

## Conclusions

Research on {topic} represents a dynamic and evolving field with significant
potential for future advances. The identified research gaps provide opportunities
for novel investigations that could substantially advance our understanding.

Key areas warranting further investigation include:
- Mechanistic studies with larger cohorts
- Cross-species comparative analyses
- Integration of multiple methodological approaches

---

*This literature review was generated by the Hermes Research Agent System.*
*Workflow: Serial 4-agent pipeline*
"""
        
        filepath = write_result("literature_review.md", review_content, tid)
        results["outputs"]["review_file"] = filepath
        print(f"    ✅ Review saved to: {filepath}")

        # Generate PDF from LaTeX
        try:
            results_dir = get_results_dir(tid)
            pdf_path = latex_to_pdf(review_content, results_dir, topic, task_id=tid)
            results["outputs"]["pdf_file"] = pdf_path
            print(f"    ✅ PDF generated: {pdf_path}")
        except Exception as pdf_err:
            print(f"    ⚠️ PDF generation failed: {pdf_err}")
            results["outputs"]["pdf_file"] = None

        report_complete("review_writer", f"Review saved to {filepath}", tid)
        results["steps"]["review_writer"] = "complete"
    except Exception as e:
        print(f"    ❌ Error: {e}")
        results["steps"]["review_writer"] = f"error: {e}"
        return results
    
    # =========================================================================
    # STEP 4: Idea Generation
    # =========================================================================
    print_step(4, "Idea Generator Agent", "running")
    try:
        analysis_data = read_shared("analysis", tid)
        gaps = analysis_data.get("overall_research_gaps", [])
        
        ideas = []
        for i, gap in enumerate(gaps[:5], 1):
            ideas.append({
                "rank": i,
                "title": f"Investigation of {gap.split(' ')[2] if len(gap.split(' ')) > 2 else topic} mechanisms",
                "hypothesis": f"If we investigate {gap.lower()}, then we may uncover novel therapeutic targets",
                "approach": f"We will use integrated experimental and computational approaches to study {topic}",
                "expected_impact": "High" if i <= 2 else "Medium",
                "novelty": 10 - i,
                "feasibility": 8 - (i // 2),
                "impact_rationale": f"Directly addresses research gap: {gap}",
                "supporting_evidence": [g for g in gaps],
                "potential_challenges": ["Resource requirements", "Technical complexity"]
            })
        
        ideas_data = {
            "topic": topic,
            "proposed_ideas": ideas,
            "generation_summary": f"Generated {len(ideas)} research ideas from {len(gaps)} identified gaps"
        }
        
        write_shared("ideas", ideas_data, tid)
        report_complete("idea_generator", f"Proposed {len(ideas)} research directions", tid)
        results["steps"]["idea_generator"] = "complete"
        print(f"    ✅ Generated {len(ideas)} research ideas")
    except Exception as e:
        print(f"    ❌ Error: {e}")
        results["steps"]["idea_generator"] = f"error: {e}"
        return results
    
    # =========================================================================
    # COMPLETE
    # =========================================================================
    results["completed_at"] = datetime.now().isoformat()
    results["status"] = "complete"
    
    print_header("Workflow Complete!")
    print(f"\n📊 Summary:")
    print(f"   Topic: {topic}")
    print(f"   Task ID: {tid}")
    print(f"   Literature: {len(results['steps'])} agents completed")
    
    if "review_file" in results["outputs"]:
        print(f"\n📄 Output Files:")
        print(f"   Literature Review: {results['outputs']['review_file']}")
        if results["outputs"].get("pdf_file"):
            print(f"   PDF: {results['outputs']['pdf_file']}")
        print(f"   Shared KB: /root/research-agent/shared/task_{tid}_*.json")
        print(f"   Results Dir: /root/research-agent/results/{tid}/")
    
    return results


def _generate_sample_papers(topic: str) -> list:
    """Generate sample paper data for testing."""
    return [
        {
            "title": f"Advances in {topic}: A Comprehensive Review",
            "authors": ["Smith JA", "Doe J", "Brown K"],
            "year": 2024,
            "journal": "Nature Reviews",
            "abstract": f"A review of recent advances in {topic} research...",
            "url": "https://example.com/paper1",
            "relevance_score": 9
        },
        {
            "title": f"Novel Mechanisms in {topic}",
            "authors": ["Johnson R", "Lee S"],
            "year": 2023,
            "journal": "Cell",
            "abstract": f"Study revealing novel mechanisms of {topic}...",
            "url": "https://example.com/paper2",
            "relevance_score": 8
        },
        {
            "title": f"Clinical Applications of {topic}",
            "authors": ["Williams M", "Garcia E"],
            "year": 2024,
            "journal": "NEJM",
            "abstract": f"Clinical translation of {topic} research...",
            "url": "https://example.com/paper3",
            "relevance_score": 10
        }
    ]


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python workflow.py \"<topic>\"")
        print("Example: python workflow.py \"lysozyme\"")
        print("         python workflow.py \"CRISPR gene editing\"")
        sys.exit(1)
    
    topic = sys.argv[1]
    task_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        results = run_workflow(topic, task_id)
        
        if results.get("status") == "complete":
            print("\n✅ Workflow completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Workflow did not complete fully")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Workflow error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
