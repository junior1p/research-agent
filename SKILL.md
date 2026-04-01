# Research Agent Skill

A research agent for paper search, literature review, paper analysis, and research idea generation.

## Overview

This agent automates academic research workflows by coordinating specialized roles:
- **Literature Searcher** — searches papers via tools
- **Paper Analyzer** — reads and summarizes papers
- **Review Writer** — writes structured literature reviews
- **Idea Generator** — proposes novel research directions

## Usage

```
# Run a research task
python workflow.py --task "your research topic"

# Or import as a module
from workflow import ResearchWorkflow
```

## Project Structure

```
research-agent/
├── workflow.py              # Main workflow orchestration
├── roles/
│   ├── literature_searcher.py
│   ├── paper_analyzer.py
│   ├── review_writer.py
│   └── idea_generator.py
├── tools/
│   ├── research_task_runner.py
│   ├── delegate_tools.py
│   └── latex_to_pdf.py
├── templates/
│   └── literature_review.tex
├── shared/                  # Task intermediate results
└── results/                 # Final outputs
```

## Requirements

```
pip install -r requirements.txt
```

## Configuration

Set your API keys as environment variables:
- `HF_TOKEN` — HuggingFace token (for paper search)
- Tavily tools if needed
