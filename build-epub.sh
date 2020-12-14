#!/bin/sh
cat *-en.md | pandoc -o pdf/analytic-introduction-en.epub
cat *-it.md | pandoc -o pdf/analytic-introduction-it.epub
