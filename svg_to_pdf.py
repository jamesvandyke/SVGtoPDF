"""Simple CLI tool to convert SVG files to PDF documents."""
from __future__ import annotations

import argparse
import pathlib
import sys
from typing import Iterable

try:
    from reportlab.graphics import renderPDF
    from svglib.svglib import svg2rlg
except ModuleNotFoundError as exc:  # pragma: no cover - import guard
    raise SystemExit(
        "The 'svglib' and 'reportlab' packages are required to run this tool. "
        "Install them with 'pip install -r requirements.txt'."
    ) from exc


DEFAULT_SVG_DPI = 96.0


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert one or more SVG files to PDF.",
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        type=pathlib.Path,
        help="Path(s) to SVG file(s) to convert.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        help=(
            "Output file or directory. When converting multiple inputs, this must "
            "be a directory. If omitted, the PDF will be written next to the input "
            "file with the same name."
        ),
    )
    parser.add_argument(
        "--dpi",
        type=float,
        default=DEFAULT_SVG_DPI,
        help=f"Dots per inch to use when scaling (default: {DEFAULT_SVG_DPI:.0f}).",
    )
    return parser.parse_args(argv)


def resolve_output_path(
    input_path: pathlib.Path,
    output: pathlib.Path | None,
    multiple_inputs: bool,
) -> pathlib.Path:
    """Determine the output path for a given input file."""
    if output is None:
        return input_path.with_suffix(".pdf")

    if output.is_dir() or (multiple_inputs and output.exists()):
        return output / (input_path.stem + ".pdf")

    if multiple_inputs and not output.is_dir():
        raise SystemExit(
            "When converting multiple SVG files the output must be a directory."
        )

    return output


def convert_svg_to_pdf(input_path: pathlib.Path, output_path: pathlib.Path, dpi: float) -> None:
    """Convert a single SVG file to PDF."""
    drawing = svg2rlg(str(input_path))
    if drawing is None:
        raise ValueError(f"Unable to parse SVG file: {input_path}")

    scale = dpi / DEFAULT_SVG_DPI if dpi else 1.0
    if scale <= 0:
        raise ValueError("DPI must be greater than zero.")

    if scale != 1.0:
        drawing.width *= scale
        drawing.height *= scale
        drawing.scale(scale, scale)

    renderPDF.drawToFile(drawing, str(output_path))


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)

    multiple_inputs = len(args.inputs) > 1

    if args.dpi <= 0:
        raise SystemExit("DPI must be greater than zero.")

    if args.output and multiple_inputs:
        if args.output.exists() and not args.output.is_dir():
            raise SystemExit(
                "When converting multiple SVG files the output must be a directory."
            )
        args.output.mkdir(parents=True, exist_ok=True)

    exit_code = 0

    for input_path in args.inputs:
        if not input_path.exists():
            print(f"Input file not found: {input_path}", file=sys.stderr)
            return 1
        if input_path.suffix.lower() != ".svg":
            print(f"Skipping non-SVG file: {input_path}", file=sys.stderr)
            continue

        output_path = resolve_output_path(input_path, args.output, multiple_inputs)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            convert_svg_to_pdf(input_path, output_path, args.dpi)
        except Exception as exc:  # pragma: no cover - user feedback
            print(
                f"Failed to convert {input_path} -> {output_path}: {exc}",
                file=sys.stderr,
            )
            exit_code = 1
            continue

        print(f"Converted {input_path} -> {output_path}")

    return exit_code


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
