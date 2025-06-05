import os
import re


LATEX_REMOVE_PAR: str = r"\\(\[|\])"
LATEX_REPLACE_MARKS: str = r":marks\[(\d+)\]"
LATEX_REPLACE_BOLD: str = r"\*\*([^*\n]*?)\*\*"
LATEX_REPLACE_BOLD_EDGE: str = r"\*\*((?:[^*]|\*(?!\*))*?)\*\*"
LATEX_REPLACE_ITALIC: str = r"\_\_([^_\n]*?)\_\_"
LATEX_REPLACE_ITALIC_EDGE: str = r"\_\_((?:[^_]|_(?!_))*?)\_\_"
LATEX_REMOVE_NESTING: str = r"\$\$\s*\\begin\{([^}]+)\}(.*?)\\end\{\1\}\s*\$\$"
LATEX_REPLACE_IMAGE: str = r"!\[([^\]]*)\]\(([^)]+)\)"
LATEX_NESTING_ALT: str = r"$$\\begin{\1}\2\\end{\1}$$"

LATEX_FILE: str = r"""
% !TeX TXS-program:compile = txs:///pdflatex/[-shell-escape]
\documentclass{article}

\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{mathtools}
\usepackage{xcolor}
\usepackage{gensymb}
\usepackage{textcomp}
\usepackage{array}
\usepackage{graphicx}
\usepackage[margin=1in]{geometry}
\usepackage{bm}
\usepackage{svg}
\usepackage{tabto}

\TabPositions{1cm, 2cm, 3cm, 4cm}
\makeatletter
\def\UTFviii@undefined@err#1{}
\makeatother

\begin{document}

\setlength{\parskip}{1em}
\setlength{\parindent}{0pt}

"""
LATEX_FILE_END: str = r"\end{document}"


def convert_indentation_to_tabs(
    latex_content: str, tab_levels: list[tuple[str, str]] | None = None
):
    """
    Convert manual indentation to \tab commands
    """
    if tab_levels is None:
        tab_levels = [
            (r"^\s{4}(\d+\.)", r"\\tab \1"),
            (r"^\s{8}(\d+\.)", r"\\tab\\tab \1"),
            (r"^\s{12}(\d+\.)", r"\\tab\\tab\\tab \1"),
        ]

    for pattern, replacement in tab_levels:
        latex_content = re.sub(pattern, replacement, latex_content, flags=re.MULTILINE)

    return latex_content


def process_latex(inp: str) -> str:
    inp = LATEX_FILE + inp
    inp = re.sub(LATEX_REMOVE_PAR, r"\1", inp)
    inp = re.sub(LATEX_REPLACE_MARKS, r"\\hfill[\1]", inp)
    inp = re.sub(LATEX_REPLACE_BOLD, r"\\textbf{\1}", inp)
    inp = re.sub(LATEX_REPLACE_ITALIC, r"\\textit{\1}", inp)
    inp = re.sub(LATEX_REPLACE_BOLD_EDGE, r"\\textbf{\1}", inp)
    inp = re.sub(LATEX_REPLACE_ITALIC_EDGE, r"\\textit{\1}", inp)

    def replacement(match: re.Match[str]) -> str:
        alt_text = match.group(1)
        filename = os.path.basename(alt_text)
        _, ext = os.path.splitext(filename)

        if ext.lower() == ".svg":
            return f"\\includesvg{{{filename}}}"
        else:
            return f"\\includegraphics{{{filename}}}"

    inp = re.sub(LATEX_REPLACE_IMAGE, replacement, inp)
    inp = inp.replace(":::center", "")
    inp = inp.replace(":::", "")
    inp = re.sub(LATEX_REMOVE_NESTING, LATEX_NESTING_ALT, inp, flags=re.DOTALL)
    inp = convert_indentation_to_tabs(inp)
    inp = inp.replace("$$\\begin{align*}", "\\[\\begin{aligned}")
    inp = inp.replace("\\end{align*}$$", "\\end{aligned}\\]")
    inp += LATEX_FILE_END
    return inp
