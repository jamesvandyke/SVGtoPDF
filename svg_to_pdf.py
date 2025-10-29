"""Simple CLI tool to convert SVG files to PDF documents."""
from __future__ import annotations

import argparse
import pathlib
import sys
from typing import Iterable

try:
    import cairosvg
except ModuleNotFoundError as exc:  # pragma: no cover - import guard
    raise SystemExit(
        "The 'cairosvg' package is required to run this tool. "
        "Install it with 'pip install -r requirements.txt'."
    ) from exc


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
        default=96.0,
        help="Dots per inch to use when rasterizing (default: 96).",
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
    cairosvg.svg2pdf(url=str(input_path), write_to=str(output_path), dpi=dpi)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)

    multiple_inputs = len(args.inputs) > 1

    if args.output and multiple_inputs:
        if args.output.exists() and not args.output.is_dir():
            raise SystemExit(
                "When converting multiple SVG files the output must be a directory."
            )
        args.output.mkdir(parents=True, exist_ok=True)

    for input_path in args.inputs:
        if not input_path.exists():
            print(f"Input file not found: {input_path}", file=sys.stderr)
            return 1
        if input_path.suffix.lower() != ".svg":
            print(f"Skipping non-SVG file: {input_path}", file=sys.stderr)
            continue

        output_path = resolve_output_path(input_path, args.output, multiple_inputs)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        convert_svg_to_pdf(input_path, output_path, args.dpi)
        print(f"Converted {input_path} -> {output_path}")

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
