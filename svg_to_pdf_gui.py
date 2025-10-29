"""Simple drag-and-drop GUI for converting SVG files to PDF documents."""
from __future__ import annotations

import pathlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Sequence

try:  # pragma: no cover - import guard
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ModuleNotFoundError as exc:  # pragma: no cover - dependency hint
    raise SystemExit(
        "The 'tkinterdnd2' package is required to run the GUI. "
        "Install it with 'pip install -r requirements.txt'."
    ) from exc

from svg_to_pdf import DEFAULT_SVG_DPI, convert_svg_to_pdf


class SvgToPdfApp(TkinterDnD.Tk):
    """Main application window providing drag-and-drop conversion."""

    def __init__(self) -> None:
        super().__init__()
        self.title("SVG to PDF Converter")
        self.geometry("480x360")
        self.minsize(420, 320)

        self.output_dir_var = tk.StringVar()
        self.dpi_var = tk.DoubleVar(value=DEFAULT_SVG_DPI)

        self._build_ui()

    def _build_ui(self) -> None:
        """Create and lay out widgets for the interface."""
        padding = {"padx": 12, "pady": 8}

        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, **padding)

        instructions = ttk.Label(
            main,
            text=(
                "Drag and drop SVG files onto the area below or click 'Browse SVGs'.\n"
                "Each SVG will be converted to PDF using the configured DPI."
            ),
            justify=tk.CENTER,
            wraplength=420,
        )
        instructions.pack(fill=tk.X, pady=(0, 12))

        drop_frame = ttk.LabelFrame(main, text="Drop SVG files here")
        drop_frame.pack(fill=tk.BOTH, expand=True)

        self.drop_area = tk.Label(
            drop_frame,
            text="Drop files here",
            relief=tk.SOLID,
            background="#f7f7f7",
            anchor=tk.CENTER,
        )
        self.drop_area.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind("<<Drop>>", self._handle_drop)

        controls = ttk.Frame(main)
        controls.pack(fill=tk.X, pady=(12, 0))

        output_label = ttk.Label(controls, text="Output directory (optional):")
        output_label.grid(row=0, column=0, sticky=tk.W)

        output_entry = ttk.Entry(controls, textvariable=self.output_dir_var)
        output_entry.grid(row=0, column=1, sticky=tk.EW, padx=(8, 8))

        browse_button = ttk.Button(controls, text="Browse…", command=self._choose_output_dir)
        browse_button.grid(row=0, column=2, sticky=tk.E)

        dpi_label = ttk.Label(controls, text="DPI:")
        dpi_label.grid(row=1, column=0, sticky=tk.W, pady=(8, 0))

        dpi_spinbox = ttk.Spinbox(
            controls,
            from_=10,
            to=600,
            increment=10,
            textvariable=self.dpi_var,
            width=6,
        )
        dpi_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(8, 0), pady=(8, 0))

        browse_svgs = ttk.Button(
            controls,
            text="Browse SVGs",
            command=self._choose_svg_files,
        )
        browse_svgs.grid(row=1, column=2, sticky=tk.E, pady=(8, 0))

        controls.columnconfigure(1, weight=1)

        log_frame = ttk.LabelFrame(main, text="Conversion log")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        self.log_widget = tk.Text(log_frame, height=6, state=tk.DISABLED)
        self.log_widget.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    def _choose_output_dir(self) -> None:
        """Prompt the user for an output directory."""
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_dir_var.set(directory)

    def _choose_svg_files(self) -> None:
        """Prompt the user to select SVG files for conversion."""
        paths = filedialog.askopenfilenames(
            title="Select SVG files",
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")],
        )
        if paths:
            self._process_paths(paths)

    def _handle_drop(self, event: tk.Event) -> None:
        """Handle files dropped onto the drop area."""
        paths = self.tk.splitlist(event.data)
        self._process_paths(paths)

    def _process_paths(self, paths: Sequence[str]) -> None:
        """Validate and convert the provided file paths."""
        if not paths:
            return

        dpi = self._get_dpi()
        if dpi is None:
            return

        output_dir_value = self.output_dir_var.get().strip()
        output_dir = pathlib.Path(output_dir_value) if output_dir_value else None
        if output_dir:
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                messagebox.showerror("Output error", f"Failed to create directory: {exc}")
                return

        for raw_path in paths:
            cleaned_path = raw_path.strip()
            if cleaned_path.startswith("{") and cleaned_path.endswith("}"):
                cleaned_path = cleaned_path[1:-1]

            input_path = pathlib.Path(cleaned_path)
            if not input_path.exists():
                self._log(f"Skipping missing file: {input_path}")
                continue
            if input_path.suffix.lower() != ".svg":
                self._log(f"Skipping non-SVG file: {input_path}")
                continue

            output_path = (
                output_dir / (input_path.stem + ".pdf") if output_dir else input_path.with_suffix(".pdf")
            )
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                convert_svg_to_pdf(input_path, output_path, dpi)
            except Exception as exc:  # pragma: no cover - GUI feedback
                messagebox.showerror(
                    "Conversion failed",
                    f"Could not convert {input_path.name}: {exc}",
                )
            else:
                self._log(f"Converted {input_path} → {output_path}")

    def _get_dpi(self) -> float | None:
        """Retrieve a valid DPI value from the UI."""
        try:
            dpi = float(self.dpi_var.get())
        except (TypeError, tk.TclError, ValueError):
            messagebox.showerror("Invalid DPI", "Please enter a numeric DPI value.")
            return None
        if dpi <= 0:
            messagebox.showerror("Invalid DPI", "DPI must be greater than zero.")
            return None
        return dpi

    def _log(self, message: str) -> None:
        """Append a message to the log widget."""
        self.log_widget.configure(state=tk.NORMAL)
        self.log_widget.insert(tk.END, message + "\n")
        self.log_widget.see(tk.END)
        self.log_widget.configure(state=tk.DISABLED)


def main() -> None:
    """Launch the drag-and-drop SVG to PDF converter GUI."""
    app = SvgToPdfApp()
    app.mainloop()


if __name__ == "__main__":  # pragma: no cover - GUI entry point
    main()
