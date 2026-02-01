#!/usr/bin/env python3
"""
Build script for Analytic Introduction textbook.
Generates PDF and EPUB versions in multiple languages using Pandoc.
"""

import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Tuple
import shutil


# Configuration
BASE_NAME = "analytic-introduction"
AVAILABLE_LANGUAGES = ["en", "it", "sp"]
AVAILABLE_FORMATS = ["pdf", "epub"]

INPUT_PATH = Path("md")
OUTPUT_PATH = Path("output")
TEMPLATES_PATH = Path("templates")

# Format-specific settings
FORMAT_SETTINGS = {
    "epub": [],
    "pdf": [
        "--pdf-engine=lualatex",
        f"--template={TEMPLATES_PATH / 'logic-textbook.latex'}",
    ],
}


class BuildError(Exception):
    """Custom exception for build errors."""
    pass


def check_prerequisites(verbose: bool = False) -> None:
    """Check that all required tools and paths exist."""
    # Check for pandoc
    if not shutil.which("pandoc"):
        raise BuildError(
            "pandoc not found. Please install it:\n"
            "  macOS: brew install pandoc\n"
            "  Linux: sudo apt-get install pandoc\n"
            "  Windows: choco install pandoc"
        )

    if verbose:
        result = subprocess.run(
            ["pandoc", "--version"],
            capture_output=True,
            text=True
        )
        version = result.stdout.split('\n')[0]
        print(f"✓ Found {version}")

    # Check for pdflatex/lualatex if building PDFs
    if not shutil.which("lualatex"):
        print(
            "Warning: lualatex not found. PDF generation may fail.\n"
            "  Install TeX Live or MiKTeX for PDF support.",
            file=sys.stderr
        )

    # Check input directory exists
    if not INPUT_PATH.exists():
        raise BuildError(f"Input directory not found: {INPUT_PATH}")

    if verbose:
        print(f"✓ Input directory: {INPUT_PATH}")

    # Check/create output directory
    OUTPUT_PATH.mkdir(exist_ok=True)
    if verbose:
        print(f"✓ Output directory: {OUTPUT_PATH}")


def get_markdown_files(language: str) -> List[Path]:
    """Get all markdown files for a given language, sorted."""
    lang_dir = INPUT_PATH / language

    if not lang_dir.exists():
        raise BuildError(f"Language directory not found: {lang_dir}")

    md_files = sorted(lang_dir.glob("*.md"))

    if not md_files:
        raise BuildError(f"No markdown files found in {lang_dir}")

    return md_files


def build_document(
    language: str,
    format_type: str,
    verbose: bool = False
) -> Tuple[str, str, bool]:
    """
    Build a single document.

    Returns:
        Tuple of (language, format, success)
    """
    try:
        # Get markdown files
        md_files = get_markdown_files(language)

        # Prepare output file
        extension = format_type
        output_file = OUTPUT_PATH / f"{BASE_NAME}-{language}.{extension}"

        # Prepare pandoc command
        pandoc_args = FORMAT_SETTINGS[format_type].copy()
        pandoc_args.extend(["-o", str(output_file)])

        if verbose:
            print(f"Building {language} {format_type.upper()}...")
            print(f"  Input files: {len(md_files)} markdown files")
            print(f"  Output: {output_file}")

        # Concatenate markdown content
        combined_content = []
        for md_file in md_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                combined_content.append(f.read())

        full_content = '\n\n'.join(combined_content)

        # Run pandoc
        result = subprocess.run(
            ["pandoc"] + pandoc_args,
            input=full_content,
            text=True,
            capture_output=True,
            check=False
        )

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout
            raise BuildError(
                f"Pandoc failed for {language} {format_type}:\n{error_msg}"
            )

        if verbose:
            print(f"✓ Successfully built {output_file}")

        return (language, format_type, True)

    except Exception as e:
        if verbose:
            print(f"✗ Failed to build {language} {format_type}: {e}", file=sys.stderr)
        return (language, format_type, False)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build Analytic Introduction textbook in multiple formats and languages.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Build all languages and formats
  %(prog)s -l en                    # Build only English
  %(prog)s -l en it                 # Build English and Italian
  %(prog)s -f pdf                   # Build only PDFs
  %(prog)s -l en -f pdf             # Build English PDF only
  %(prog)s -v                       # Verbose output
  %(prog)s -l sp -f epub -v         # Build Spanish EPUB with verbose output
        """
    )

    parser.add_argument(
        "-l", "--languages",
        nargs="+",
        choices=AVAILABLE_LANGUAGES,
        default=AVAILABLE_LANGUAGES,
        metavar="LANG",
        help=f"Languages to build (choices: {', '.join(AVAILABLE_LANGUAGES)}). Default: all"
    )

    parser.add_argument(
        "-f", "--formats",
        nargs="+",
        choices=AVAILABLE_FORMATS,
        default=AVAILABLE_FORMATS,
        metavar="FORMAT",
        help=f"Formats to build (choices: {', '.join(AVAILABLE_FORMATS)}). Default: all"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "-j", "--jobs",
        type=int,
        default=4,
        metavar="N",
        help="Number of parallel jobs (default: 4)"
    )

    args = parser.parse_args()

    try:
        # Check prerequisites
        if args.verbose:
            print("Checking prerequisites...")
        check_prerequisites(args.verbose)

        # Build task list
        tasks = [
            (lang, fmt)
            for lang in args.languages
            for fmt in args.formats
        ]

        if args.verbose:
            print(f"\nBuilding {len(tasks)} document(s):")
            for lang, fmt in tasks:
                print(f"  - {lang} {fmt}")
            print()
        else:
            print(f"Building {len(tasks)} document(s)...")

        # Execute builds in parallel
        results = []
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(build_document, lang, fmt, args.verbose): (lang, fmt)
                for lang, fmt in tasks
            }

            for future in as_completed(futures):
                lang, fmt, success = future.result()
                results.append((lang, fmt, success))

                if not args.verbose:
                    status = "✓" if success else "✗"
                    print(f"  {status} {lang} {fmt}")

        # Summary
        successful = sum(1 for _, _, success in results if success)
        failed = len(results) - successful

        print(f"\n{'='*50}")
        print(f"Build complete: {successful} succeeded, {failed} failed")

        if failed > 0:
            print("\nFailed builds:")
            for lang, fmt, success in results:
                if not success:
                    print(f"  ✗ {lang} {fmt}")
            sys.exit(1)
        else:
            print(f"All outputs in: {OUTPUT_PATH}")
            sys.exit(0)

    except BuildError as e:
        print(f"Build error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nBuild interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
