#!/bin/sh
cat *-en.md | pandoc -o pdf/analytic-introduction-en.pdf --pdf-engine=xelatex --standalone --template templates/logic-textbook.latex --top-level-division=chapter
cat *-it.md | pandoc -o pdf/analytic-introduction-it.pdf --pdf-engine=xelatex --standalone --template templates/logic-textbook.latex --top-level-division=chapter
