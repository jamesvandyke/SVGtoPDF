# SVG to PDF Converter

A small Python-based command-line utility for converting Scalable Vector Graphics (SVG) files to Portable Document Format (PDF) documents. The script is cross-platform and works on Windows 11 with Python 3.9 or newer.

## Requirements

- Python 3.9+
- [ReportLab](https://www.reportlab.com/dev/) (installed via `pip`)
- [svglib](https://pypi.org/project/svglib/) SVG parser (installed via `pip`)
- [tkinterdnd2](https://github.com/pmgagne/tkinterdnd2) for drag-and-drop GUI support

> **Why not CairoSVG?**
> The original implementation depended on CairoSVG, which requires additional native
> Cairo libraries on Windows. Switching to ReportLab + svglib keeps everything installable
> directly from PyPI wheels so no external DLLs are needed.

## Installation

1. Install Python 3.9 or newer from [python.org](https://www.python.org/downloads/). Ensure that "Add Python to PATH" is selected during installation on Windows.
2. Open **Command Prompt** or **PowerShell**.
3. Navigate to the project directory and install dependencies:

   ```powershell
   cd path\to\SVGtoPDF
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Usage

### Graphical interface

Launch the drag-and-drop GUI:

```powershell
python svg_to_pdf_gui.py
```

Drop one or more SVG files onto the window (or click **Browse SVGs**) and they will be
converted to PDFs. Optionally choose an output directory and DPI before dropping the
files. When no output directory is selected, the PDFs are created alongside each source
SVG file.

### Command line

Convert a single file:

```powershell
python svg_to_pdf.py input.svg
```

Convert a file while specifying the output path:

```powershell
python svg_to_pdf.py input.svg -o output.pdf
```

Convert multiple files to a directory (created automatically if it does not exist):

```powershell
python svg_to_pdf.py artwork1.svg artwork2.svg -o converted\
```

Adjust the output DPI scaling (defaults to 96):

```powershell
python svg_to_pdf.py diagram.svg --dpi 144
```

## Creating a standalone Windows executable

To distribute the drag-and-drop app without requiring Python on the target machine,
build a single-file executable with [PyInstaller](https://pyinstaller.org/). Run the
following command from the project root inside your virtual environment:

```powershell
pyinstaller svg_to_pdf_gui.py --name SVGtoPDF --onefile --windowed
```

The generated executable will be located in the `dist\SVGtoPDF.exe` directory. Copy the
entire `dist` folder to another Windows computer to run the app.

## Development

Run a quick syntax check:

```bash
python -m compileall svg_to_pdf.py svg_to_pdf_gui.py
```

## License

This project is released under the terms of the [MIT License](LICENSE).
