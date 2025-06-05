import os
import re


LATEX_REPLACE_MARKS: str = r":marks\[(\d+)\]"
LATEX_REPLACE_IMAGE: str = r"!\[([^\]]*)\]\(([^)]+)\)"
LATEX_REMOVE_NESTING: str = (
    r"\$\$\s*\\begin\{([a-zA-Z]+[*])\}\s*([\s\S]+?)\s*\\end\{\1\}\s*\$\$"
)
LATEX_REPLACE_ALIGN: str = r"(\\begin\{aligned\}[\s\S]*?\\end\{aligned\})"

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
\usepackage{tikz}
\usepackage{siunitx}
\usepackage[most]{tcolorbox}
\usepackage{textcomp}

\newcommand{\m}[2]{\frac{#1}{#2}}
\newcommand{\s}[1]{\sqrt{#1}}
\newcommand{\answer}[1]{#1}
\newcommand{\vv}[1]{\overrightarrow{#1}}
\newcommand{\medmath}[1]{#1}
\newcommand{\qref}[1]{\hspace{0.25em}\htmlClass{qref}{#1}}
\newcommand{\floor}[1]{\lfloor{#1}\rfloor}
\newcommand{\ceil}[1]{\lceil{#1}\rceil}
\newcommand{\vspacecmd}[1]{}
\newcommand{\intertextcmd}[1]{\text{#1}\notag\\}
\newcommand{\cancel}[1]{%
	\tikz[baseline=(X.base)]{
		\node[inner sep=0pt, outer sep=0pt] (X) {$#1$};
		\draw[red, thick] (X.south west) -- (X.north east);
	}%
}

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
    inp = re.sub(LATEX_REPLACE_MARKS, r"\\hfill[\1]", inp)
    inp = re.sub(r".\[Maximum mark: ([^a-z]*)\\]", r"[Maximum mark: \1]", inp)
    inp = re.sub(r"\*\*([^*\n]*?)\*\*", r"\\textbf{\1}", inp)
    inp = re.sub(r"\_\_([^*\n]*?)\_\_", r"\\textit{\1}", inp)
    inp = re.sub(LATEX_REMOVE_NESTING, r"\\begin{\1}\2\\end{\1}", inp, flags=re.DOTALL)

    def tagstar_inside_aligned(m: re.Match[str]):
        content = re.sub(r"\\tag\*\{([^}]*)\}", r"\1", m.group(0))
        return content

    inp = re.sub(LATEX_REPLACE_ALIGN, tagstar_inside_aligned, inp, flags=re.DOTALL)

    inp += LATEX_FILE_END
    return inp

