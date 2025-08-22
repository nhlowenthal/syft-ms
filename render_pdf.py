import os
import re
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
import csv

LINEPLOT_COLORMAP = [
    HexColor('#0e70f0'),
    HexColor("#fc8003"),
    HexColor("#ff1c6f"),
]

def drawChart(scanData):
    drawing = Drawing(400, 200)  # Define drawing dimensions
    # Sample data for the line plot
    # Each inner list represents a series of (x, y) points
    data_to_plot = {}
    for row in scanData:
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
    lp.yValueAxis.valueMax = 2000000
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

    has_data = len(data_to_plot) > 0
    return has_data, drawing

def renderClientPDF(baselinePath, scanData30Path):
    stem = baselinePath.stem
    res = re.match(r"(.*)-baseline", stem)
    id_number = res.group(1)

    output_file = Path(baselinePath).with_stem(id_number).with_suffix(".pdf")
    print(f"Rendering {baselinePath} to {output_file}")
    # id_number = Path(baselinePath).stem


    baselineData = {}
    scan30Data = {}

    if baselinePath.is_file():
        with open(baselinePath, "r") as f:
            reader = csv.reader(f)
            baselineData = list(reader)[1:]

    if scanData30Path.is_file():
        with open(scanData30Path, "r") as f:
            reader = csv.reader(f)
            scan30Data = list(reader)[1:]

    pdfmetrics.registerFont(TTFont("Montserrat", "./Montserrat.ttf"))

    c = canvas.Canvas(str(output_file), pagesize=letter)

    c.setFont("Montserrat", 28)
    c.drawCentredString(letter[0] * 0.5, letter[1] * 0.91, id_number)

    c.setFont("Montserrat", 14)
    c.drawCentredString(letter[0] * 0.5, letter[1] * 0.885, "Patient Report")

    hasBaselineData, baselineDrawing = drawChart(baselineData)

    if hasBaselineData:
        c.drawCentredString(letter[0] * 0.5, letter[1] * 0.825, "Baseline")
        baselineDrawing.drawOn(c, letter[0] * 0.13, letter[1] * 0.7)
    else:
        c.drawCentredString(letter[0] * 0.5, letter[1] * 0.7, "No Baseline Scan")

    hasMassScan30, massScan30Drawing = drawChart(scan30Data)

    if hasMassScan30:
        c.drawCentredString(letter[0] * 0.5, letter[1] * 0.525, "Mass Scan 30 mins")
        massScan30Drawing.drawOn(c, letter[0] * 0.13, letter[1] * 0.4)
    else:
        c.drawCentredString(letter[0] * 0.5, letter[1] * 0.525, "No Mass Scan 30 mins")

    c.showPage()
    c.save()


def renderAverageBaseline(consoladatedBaselinePath):

    output_file = Path(consoladatedBaselinePath).with_suffix(".pdf")
    print(f"Rendering {consoladatedBaselinePath} to {output_file}")
    # id_number = Path(baselinePath).stem


    baselineData = {}

    if consoladatedBaselinePath.is_file():
        with open(consoladatedBaselinePath, "r") as f:
            reader = csv.reader(f)
            baselineData = list(reader)[1:]


    pdfmetrics.registerFont(TTFont("Montserrat", "./Montserrat.ttf"))

    c = canvas.Canvas(str(output_file), pagesize=letter)

    c.setFont("Montserrat", 14)
    c.drawCentredString(letter[0] * 0.5, letter[1] * 0.885, "Average Baseline")

    hasBaselineData, baselineDrawing = drawChart(baselineData)

    if hasBaselineData:
        c.drawCentredString(letter[0] * 0.5, letter[1] * 0.825, "Baseline")
        baselineDrawing.drawOn(c, letter[0] * 0.13, letter[1] * 0.7)
    else:
        c.drawCentredString(letter[0] * 0.5, letter[1] * 0.7, "No Baseline Scan")


    c.showPage()
    c.save()

