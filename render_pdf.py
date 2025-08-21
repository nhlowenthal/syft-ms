import os
from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.legends import LineLegend

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
# from al_syft import OUTPUT_FOLDER
from al_syft import OUTPUT_FOLDER, ROOT, process_file, find_first_subfolder_starting_with, find_30min_csv
import csv

LINEPLOT_COLORMAP = [
    HexColor('#0e70f0'),
    HexColor("#fc8003"),
    HexColor("#ff1c6f"),
]

def render_pdf(data_file):
    output_file = Path(data_file).with_suffix(".pdf")
    print(f"Rendering {data_file} to {output_file}")
    id_number = Path(data_file).stem

    data = []
    with open(data_file, "r") as f:
        reader = csv.reader(f)
        data = list(reader)[1:]

    pdfmetrics.registerFont(TTFont("Montserrat", "./Montserrat.ttf"))

    c = canvas.Canvas(str(output_file), pagesize=letter)

    c.setFont("Montserrat", 28)
    c.drawCentredString(letter[0] * 0.5, letter[1] * 0.91, id_number)

    c.setFont("Montserrat", 14)
    c.drawCentredString(letter[0] * 0.5, letter[1] * 0.885, "Patient Report")

    drawing = Drawing(400, 200)  # Define drawing dimensions

    # Sample data for the line plot
    # Each inner list represents a series of (x, y) points

    data_to_plot = {}

    for row in data:
        reagent, product, intensity, *other = row
        if reagent not in data_to_plot:
            data_to_plot[reagent] = []

        # Manually filter out too high values
        if int(product) <= 150:
            data_to_plot[reagent].append((int(product), float(intensity)))

    lp = LinePlot()
    lp.height = letter[1] * 0.1  # Height of the chart area
    lp.width = letter[0] * 0.65  # Width of the chart area
    lp.data = list(data_to_plot.values())  # Assign the data to the line plot
    lp.xValueAxis.valueMin = 0
    lp.xValueAxis.valueMax = 150

    for i in range(len(list(data_to_plot.values()))):
        lp.lines[i].strokeColor = LINEPLOT_COLORMAP[i % len(LINEPLOT_COLORMAP)]

    legend = LineLegend()
    legend.x = lp.x + lp.width + 10
    legend.y = lp.y + lp.height
    legend.colorNamePairs = list(
        zip(LINEPLOT_COLORMAP, data_to_plot.keys())
    )
    legend.fontName = 'Montserrat'
    legend.fontSize = 8

    drawing.add(lp)
    drawing.add(legend)

    if data_to_plot:
        drawing.drawOn(c, letter[0] * 0.13, letter[1] * 0.6)
    else:
        c.drawCentredString(letter[0] * 0.5, letter[1] * 0.6, "No Mass Scan")

    c.showPage()
    c.save()

if __name__ == "__main__":
    for file in os.listdir(OUTPUT_FOLDER):# --- Helpers for locating the 30-min scan, used by render_pdf.py ---
def find_first_subfolder_starting_with(parent: Path, prefix: str) -> Path | None:
    for p in sorted(parent.iterdir()):
        if p.is_dir() and p.name.startswith(prefix):
            return p
    return None

def find_30min_csv(folder: Path) -> Path | None:
    for p in sorted(folder.iterdir()):
        if p.is_file() and p.suffix.lower() == ".csv" and "30min" in p.name.lower():
            return p
    return None

        render_pdf(os.path.join(OUTPUT_FOLDER, file))
