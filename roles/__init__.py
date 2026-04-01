"""roles/ - Agent system prompts for Hermes research sub-agents."""

from .literature_searcher import SYSTEM_PROMPT as LITERATURE_SEARCHER_PROMPT
from .paper_analyzer import SYSTEM_PROMPT as PAPER_ANALYZER_PROMPT
from .review_writer import SYSTEM_PROMPT as REVIEW_WRITER_PROMPT
from .idea_generator import SYSTEM_PROMPT as IDEA_GENERATOR_PROMPT

__all__ = [
    'LITERATURE_SEARCHER_PROMPT',
    'PAPER_ANALYZER_PROMPT',
    'REVIEW_WRITER_PROMPT',
    'IDEA_GENERATOR_PROMPT',
]
