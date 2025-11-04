#!/usr/bin/env python3
"""
Convert Markdown files to PDF.

The script prefers the WeasyPrint engine when it can be imported. On Windows
that requires the GTK/Pango runtime described in the WeasyPrint docs. If
WeasyPrint is unavailable (or its native libraries are missing), a pure-Python
fallback based on xhtml2pdf is used instead. Install one of these dependency
sets:

    pip install markdown weasyprint      # requires additional system packages
    pip install markdown xhtml2pdf reportlab
"""

from __future__ import annotations

import argparse
import html
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Optional

DEFAULT_CSS = """
body { font-family: Arial, sans-serif; margin: 2rem; }
h1, h2, h3, h4, h5, h6 { font-weight: 600; }
pre { background: #f5f5f5; padding: 0.75rem; border-radius: 4px; }
code { font-family: Consolas, "Courier New", monospace; }
blockquote { border-left: 4px solid #999; padding-left: 1rem; color: #555; }
""".strip()


@dataclass(slots=True)
class ConversionJob:
    source: Path
    target: Path


@dataclass(slots=True)
class Backend:
    name: str
    convert: Callable[[str, Path, Optional[Path], Optional[str], Path], None]
    inline_css_required: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert Markdown (.md) files to PDF")
    parser.add_argument(
        "input",
        nargs="?",
        default=".",
        help="Markdown file or directory to convert",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output PDF path when converting a single file",
    )
    parser.add_argument(
        "-d",
        "--out-dir",
        help="Output directory when converting a folder",
    )
    parser.add_argument(
        "--css",
        help="Optional CSS stylesheet applied to the PDF",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process Markdown files in subdirectories too",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing PDFs",
    )
    return parser.parse_args()


def ensure_dependencies() -> tuple[object, Backend]:
    try:
        import markdown  # type: ignore
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise SystemExit(
            "Missing dependency: markdown. Install it with 'pip install markdown'."
        ) from exc

    weasyprint_error: Optional[Exception] = None
    try:
        from weasyprint import CSS, HTML  # type: ignore
    except (ImportError, OSError) as exc:
        weasyprint_error = exc
    else:
        def convert_weasyprint(
            html_document: str,
            target: Path,
            css_path: Optional[Path],
            inline_css: Optional[str],
            base_dir: Path,
        ) -> None:
            stylesheets = []
            if css_path:
                stylesheets.append(CSS(filename=str(css_path)))
            else:
                stylesheets.append(CSS(string=DEFAULT_CSS))
            HTML(string=html_document, base_url=str(base_dir)).write_pdf(
                str(target), stylesheets=stylesheets
            )

        return markdown, Backend(
            name="weasyprint",
            convert=convert_weasyprint,
            inline_css_required=False,
        )

    try:
        from xhtml2pdf import pisa  # type: ignore
    except ImportError as exc:  # pragma: no cover - dependency guard
        message = [
            "Neither WeasyPrint nor the xhtml2pdf fallback could be imported.",
            "Install one of the following dependency sets:",
            "  pip install markdown weasyprint",
            "  pip install markdown xhtml2pdf reportlab",
        ]
        if weasyprint_error is not None:
            message.insert(
                1,
                f"WeasyPrint import failed with: {type(weasyprint_error).__name__}: {weasyprint_error}",
            )
        raise SystemExit("\n".join(message)) from exc

    def convert_xhtml2pdf(
        html_document: str,
        target: Path,
        css_path: Optional[Path],
        inline_css: Optional[str],
        base_dir: Path,
    ) -> None:
        def link_callback(uri: str, rel: str) -> str:
            candidate = Path(uri)
            if candidate.is_absolute() and candidate.exists():
                return str(candidate)
            resolved = (base_dir / uri).resolve()
            if resolved.exists():
                return str(resolved)
            return uri

        with target.open("wb") as output_file:
            pisa_status = pisa.CreatePDF(
                html_document,
                dest=output_file,
                link_callback=link_callback,
            )
        if pisa_status.err:
            raise RuntimeError("xhtml2pdf failed to render the document.")

    return markdown, Backend(
        name="xhtml2pdf",
        convert=convert_xhtml2pdf,
        inline_css_required=True,
    )


def discover_markdown_files(root: Path, recursive: bool) -> Iterable[Path]:
    pattern = "**/*.md" if recursive else "*.md"
    yield from sorted(root.glob(pattern))


def build_jobs(input_path: Path, args: argparse.Namespace) -> list[ConversionJob]:
    if input_path.is_file():
        if input_path.suffix.lower() != ".md":
            raise SystemExit(f"Input file must have .md extension: {input_path}")
        if args.out_dir:
            raise SystemExit("--out-dir can only be used when the input is a directory")
        output = Path(args.output) if args.output else input_path.with_suffix(".pdf")
        return [ConversionJob(source=input_path, target=output)]

    if not input_path.is_dir():
        raise SystemExit(f"Input path does not exist: {input_path}")

    output_dir = Path(args.out_dir) if args.out_dir else input_path
    output_dir.mkdir(parents=True, exist_ok=True)

    jobs: list[ConversionJob] = []
    for markdown_file in discover_markdown_files(input_path, args.recursive):
        relative = markdown_file.relative_to(input_path)
        target = (output_dir / relative).with_suffix(".pdf")
        target.parent.mkdir(parents=True, exist_ok=True)
        jobs.append(ConversionJob(source=markdown_file, target=target))

    if not jobs:
        raise SystemExit("No Markdown files found to convert.")

    return jobs


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise SystemExit(f"Unable to read {path}: file is not valid UTF-8.")


def load_inline_css(css_path: Optional[Path]) -> str:
    if css_path:
        try:
            return css_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise SystemExit(f"Failed to read CSS file {css_path}: {exc}") from exc
    return DEFAULT_CSS


def build_html_document(body_fragment: str, title: str, inline_css: Optional[str]) -> str:
    head_parts = ["<meta charset=\"utf-8\">", f"<title>{title}</title>"]
    if inline_css:
        head_parts.append("<style>")
        head_parts.append(inline_css)
        head_parts.append("</style>")
    head_html = "".join(head_parts)
    return f"<html><head>{head_html}</head><body>{body_fragment}</body></html>"


def convert_markdown_to_pdf(
    job: ConversionJob,
    css_path: Optional[Path],
    overwrite: bool,
    markdown_mod,
    backend: Backend,
) -> None:
    if job.target.exists() and not overwrite:
        raise SystemExit(
            f"Refusing to overwrite existing file: {job.target}. Use --overwrite to replace it."
        )

    markdown_text = read_text(job.source)
    html_fragment = markdown_mod.markdown(markdown_text, extensions=["extra", "tables"])
    document_title = html.escape(job.source.stem)
    inline_css = load_inline_css(css_path) if backend.inline_css_required else None
    html_document = build_html_document(html_fragment, document_title, inline_css)

    job.target.parent.mkdir(parents=True, exist_ok=True)
    backend.convert(html_document, job.target, css_path, inline_css, job.source.parent)


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser()
    css_path: Optional[Path] = None
    if args.css:
        css_path = Path(args.css).expanduser()
        if not css_path.is_file():
            raise SystemExit(f"CSS file not found: {css_path}")

    markdown_mod, backend = ensure_dependencies()
    jobs = build_jobs(input_path, args)

    print(f"[INFO] Using {backend.name} backend")

    failures: list[str] = []
    for job in jobs:
        try:
            convert_markdown_to_pdf(job, css_path, args.overwrite, markdown_mod, backend)
            print(f"[OK] {job.source} -> {job.target}")
        except SystemExit as exc:
            failures.append(f"{job.source}: {exc}")
        except Exception as exc:  # pragma: no cover - unexpected runtime error
            failures.append(f"{job.source}: {exc}")

    if failures:
        print("\nConversion failed for the following files:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
