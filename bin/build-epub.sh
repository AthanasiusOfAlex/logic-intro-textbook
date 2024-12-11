#!/bin/sh
cat md/*-en.md | pandoc -o pdf/analytic-introduction-en.epub
cat md/*-it.md | pandoc -o pdf/analytic-introduction-it.epub
