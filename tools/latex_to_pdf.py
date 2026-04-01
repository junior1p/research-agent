#!/usr/bin/env python3
"""
LaTeX to PDF converter for research agent output.
Converts LaTeX literature reviews to PDF documents.

Usage:
    from latex_to_pdf import latex_to_pdf
    pdf_path = latex_to_pdf(latex_content, output_dir, task_id)
"""

import os
import re
import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# Minimal template - no external bibliography file needed
LATEX_TEMPLATE = r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\usepackage{setspace}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{graphicx}
\usepackage[colorlinks=true,linkcolor=blue,urlcolor=cyan]{hyperref}
\geometry{margin=2.5cm}
\doublespacing

\title{\textbf{#TITLE#}}
\author{Hermes Research Agent System}
\date{#DATE#}

\begin{document}
\maketitle
\thispagestyle{empty}

\vspace{0.5cm}
\textbf{Topic:} #TOPIC#

\vspace{1cm}
#CONTENT#

\end{document}
"""


def _escape_latex(text: str) -> str:
    """Escape special LaTeX characters."""
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
    }
    for char, escaped in replacements.items():
        text = text.replace(char, escaped)
    return text


def _process_inline(text: str) -> str:
    """Process inline formatting (bold, italic, links)."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'\\textit{\1}', text)
    # Links [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\\href{\2}{\1}', text)
    return text


def _markdown_to_latex(md_content: str) -> str:
    """Convert Markdown to LaTeX."""
    lines = md_content.split('\n')
    latex_lines = []
    in_itemize = False
    in_enumerate = False
    in_code_block = False

    for line in lines:
        original = line

        # Code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                latex_lines.append('\\end{verbatim}')
                in_code_block = False
            else:
                latex_lines.append('\\begin{verbatim}')
                in_code_block = True
            continue

        if in_code_block:
            latex_lines.append(_escape_latex(line))
            continue

        # Headers - only process if not a bullet/numbered list marker
        if line.startswith('#### '):
            latex_lines.append(f"\\subsubsection*{{{_process_inline(line[5:])}}}")
            continue
        elif line.startswith('### '):
            latex_lines.append(f"\\subsection*{{{_process_inline(line[4:])}}}")
            continue
        elif line.startswith('## '):
            latex_lines.append(f"\\section*{{{_process_inline(line[3:])}}}")
            continue
        elif line.startswith('# '):
            # Article title - skip, handled in template
            continue

        # Horizontal rule
        stripped = line.strip()
        if stripped in ['---', '***', '___']:
            latex_lines.append('\\vspace{0.5cm}\\hrule\\vspace{0.5cm}')
            continue

        # Bullet list items
        if stripped.startswith('- ') or stripped.startswith('* '):
            if in_enumerate:
                latex_lines.append('\\endenumerate')
                in_enumerate = False
            if not in_itemize:
                latex_lines.append('\\begin{itemize}')
                in_itemize = True
            latex_lines.append(f"\\item {_process_inline(line.lstrip('-* '))}")
            continue

        # Numbered list items
        num_match = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if num_match:
            if in_itemize:
                latex_lines.append('\\end{itemize}')
                in_itemize = False
            if not in_enumerate:
                latex_lines.append('\\begin{enumerate}')
                in_enumerate = True
            latex_lines.append(f"\\item {_process_inline(num_match.group(2))}")
            continue

        # Close open lists when we hit regular text
        if in_itemize:
            latex_lines.append('\\end{itemize}')
            in_itemize = False
        if in_enumerate:
            latex_lines.append('\\endenumerate')
            in_enumerate = False

        # Empty lines
        if stripped == '':
            latex_lines.append('')
            continue

        # Regular paragraph text
        latex_lines.append(_process_inline(line))

    # Close any open lists at end
    if in_itemize:
        latex_lines.append('\\end{itemize}')
    if in_enumerate:
        latex_lines.append('\\endenumerate')

    return '\n'.join(latex_lines)


def latex_to_pdf(
    markdown_content: str,
    output_dir: str,
    topic: str,
    title: Optional[str] = None,
    task_id: str = "unknown"
) -> str:
    """
    Convert Markdown literature review to PDF via LaTeX.
    """
    os.makedirs(output_dir, exist_ok=True)

    if title is None:
        title = topic

    # Convert markdown to LaTeX
    content = _markdown_to_latex(markdown_content)

    # Build LaTeX document
    from datetime import datetime
    latex_content = LATEX_TEMPLATE
    latex_content = latex_content.replace('#TITLE#', _escape_latex(title))
    latex_content = latex_content.replace('#TOPIC#', _escape_latex(topic))
    latex_content = latex_content.replace('#DATE#', datetime.now().strftime('%Y-%m-%d'))
    latex_content = latex_content.replace('#CONTENT#', content)

    # Write LaTeX file
    tex_path = os.path.join(output_dir, 'literature_review.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(latex_content)

    # Compile to PDF (2 passes for proper cross-references)
    pdf_path = os.path.join(output_dir, 'literature_review.pdf')

    try:
        for pass_num in range(2):
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', output_dir, tex_path],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                logger.warning(f"pdflatex pass {pass_num+1} had issues: {result.stderr[-300:]}")

        if os.path.exists(pdf_path):
            logger.info(f"PDF generated successfully: {pdf_path}")
        else:
            alt_path = tex_path.replace('.tex', '.pdf')
            if os.path.exists(alt_path):
                pdf_path = alt_path
            else:
                raise RuntimeError(f"PDF not found after compilation")

    except subprocess.TimeoutExpired:
        raise RuntimeError("LaTeX compilation timed out")
    except FileNotFoundError:
        raise RuntimeError("pdflatex not found - please install TeX Live")

    return pdf_path


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        md_file = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
        topic = sys.argv[3] if len(sys.argv) > 3 else 'Test'

        with open(md_file, 'r') as f:
            content = f.read()

        pdf = latex_to_pdf(content, output_dir, topic)
        print(f"PDF: {pdf}")
