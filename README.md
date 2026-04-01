# Research Agent Orchestration System for Hermes

A multi-agent research workflow system where specialized sub-agents collaborate via a shared knowledge base to produce literature reviews and research proposals.

## Architecture

```
hermes-research-agent/
├── README.md
├── requirements.txt
├── workflow.py              # Main workflow orchestrator
├── tools/
│   ├── __init__.py
│   ├── delegate_tools.py     # Shared KB tools for sub-agents
│   └── research_task_runner.py  # CLI entry point for sub-agents
├── roles/                   # Agent system prompts
│   ├── __init__.py
│   ├── literature_searcher.py
│   ├── paper_analyzer.py
│   ├── review_writer.py
│   └── idea_generator.py
├── shared/                   # Shared knowledge base (JSON files)
└── results/                 # Output results (one subdir per task)
```

## How It Works

1. **Main agent** receives user request: "我想做关于 XXX 的文献综述"
2. **Main agent** spawns sub-agents using `delegate_task`
3. **Sub-agents** communicate via shared JSON files
4. **Main agent** coordinates execution order and synthesizes final output

## Sub-Agent Roles

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| Literature Search | Search academic databases | Topic | `shared/literature_search.json` |
| Paper Analyzer | Deep analysis of papers | `shared/literature_search.json` | `shared/paper_analysis.json` |
| Review Writer | Write structured review | `shared/paper_analysis.json` | `results/{task_id}/literature_review.md` |
| Idea Generator | Propose research directions | `shared/paper_analysis.json` | `shared/proposed_ideas.json` |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Main Workflow (via Hermes)

```
User: "我想做关于 CRISPR 基因编辑的文献综述"
Main agent → spawns sub-agents in sequence
```

### Testing Directly

```bash
# Run full workflow with a test topic
python workflow.py "lysozyme"

# Run individual sub-agents
python -m tools.research_task_runner literature_search "CRISPR gene editing"
python -m tools.research_task_runner paper_analyze
python -m tools.research_task_runner review_writer
python -m tools.research_task_runner idea_generator
```

## Workflow Steps

1. **Literature Search** → Searches PubMed, Semantic Scholar, arXiv for relevant papers
2. **Paper Analysis** → Deep-dives into found papers, extracts themes and gaps
3. **Review Writing** → Synthesizes into structured Markdown review
4. **Idea Generation** → Proposes novel research directions based on gaps

## Shared Knowledge Base

All sub-agents read/write JSON files in `shared/`:

- `task_{task_id}_literature_search.json` - Raw search results
- `task_{task_id}_paper_analysis.json` - Thematic analysis
- `task_{task_id}_proposed_ideas.json` - Research directions

Results are stored in `results/{task_id}/`.
