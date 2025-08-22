import os
import re
from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.graphics.shapes import (Drawing, Rect, String, Line, Group)
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

def drawChart(scanData, y_min=0, y_max=2_000_000):
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
    lp.yValueAxis.valueMin = y_min
    lp.yValueAxis.valueMax = y_max
    lp.yValueAxis.labels.fontName = "Montserrat"
    lp.xValueAxis.labels.fontName = "Montserrat"
    lp.yValueAxis.visibleGrid = 1
    lp.yValueAxis.gridStrokeColor = HexColor("#a0a0a0")

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

    drawing.add(String(
        225,
        -10,
        "Mass (AMU)",
        textAnchor='middle',
        fontName='Montserrat',
        fontSize=10,
    ))
    y_label = Drawing(400, 200)
    y_label.rotate(90)
    y_label.add(String(
        60,
        40,
        "Intensity (Counts)",
        textAnchor='middle',
        fontName='Montserrat',
        fontSize=10
    ))
    drawing.add(y_label)

    drawing.add(String(
        450,
        100,
        "Reagent",
        textAnchor='middle',
        fontName='Montserrat',
        fontSize=8,
    ))


    has_data = len(data_to_plot) > 0
    return has_data, drawing

def drawMetaboliteData(metaboliteBaselinePath, metabolite30minPath):
    with open(metaboliteBaselinePath, "r") as f:
        reader = csv.reader(f)
        baselineData = list(reader)[1:]

    with open(metabolite30minPath, "r") as f:
        reader = csv.reader(f)
        min30Data = list(reader)[1:]

    baselineData = {
        analyte: float(concentration) for analyte, concentration in baselineData
    }

    min30Data = {
        analyte: float(concentration) for analyte, concentration in min30Data
    }

    drawingWidth = letter[0] * 0.8
    drawing = Drawing(drawingWidth, 200)

    spacing = drawingWidth / len(baselineData.keys())
    for i, (analyte, baselineConcentration) in enumerate(baselineData.items()):
        x = i * spacing + spacing / 3

        min30Concentration = min30Data[analyte]

        percentIncrease = int(100 * (min30Concentration - baselineConcentration) / baselineConcentration)

        increaseIcon = '='
        percentChangeFontColor = HexColor("#247cd4")

        if percentIncrease < -5:
            increaseIcon = '↓'
            percentChangeFontColor = HexColor("#d11342")

        elif percentIncrease > 5:
            increaseIcon = '↑'
            percentChangeFontColor = HexColor("#0fa616")


        details = Group(
            String(
                x,
                100,
                analyte.title(),
                textAnchor='middle',
                fontName='Montserrat',
                fontSize=15,
            ),
            String(
                x,
                70,
                f"{increaseIcon} {percentIncrease} %",
                textAnchor='middle',
                fontName='Montserrat',
                fontSize=18,
                fillColor=percentChangeFontColor,
            ),
            String(
                x,
                40,
                f"{baselineConcentration:.2f} → {min30Concentration:.2f} ppb",
                textAnchor='middle',
                fontName='Montserrat',
                fontSize=10,
            )
        )

        drawing.add(details)

    return drawing

def renderClientPDF(baselinePath, scanData30Path, metaboliteBaselinePath, metabolite30minPath):
    stem = baselinePath.stem
    res = re.match(r"(.*)-baseline", stem)
    id_number = res.group(1)

    output_file = Path(baselinePath).with_stem(id_number).with_suffix(".pdf")
    print(f"Rendering {baselinePath} to {output_file}")

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

    hasMetaboliteBaseline = os.path.exists(metaboliteBaselinePath)
    hasMetabolite30min = os.path.exists(metabolite30minPath)

    if hasMetaboliteBaseline and hasMetabolite30min:
        chart = drawMetaboliteData(metaboliteBaselinePath, metabolite30minPath)
        chart.drawOn(c, letter[0] * 0.13, letter[1] * 0.7)
    else:
        c.drawCentredString(letter[0] * 0.5, letter[1] * 0.8, "No Mass Scan Metabolite Data")

    chartSpacing = letter[0] * 0.25
    chartTitleSpacing = letter[1] * 0.125
    chartsStart = letter[1] * 0.55

    if hasBaselineData:
        c.drawCentredString(letter[0] * 0.5, chartsStart + chartTitleSpacing, "Baseline")
        baselineDrawing.drawOn(c, letter[0] * 0.16, chartsStart)
    else:
        c.drawCentredString(letter[0] * 0.5, chartsStart + chartTitleSpacing, "No Baseline Scan")

    hasMassScan30, massScan30Drawing = drawChart(scan30Data)

    if hasMassScan30:
        c.drawCentredString(letter[0] * 0.5, chartsStart - chartSpacing + chartTitleSpacing, "Mass Scan 30 mins")
        massScan30Drawing.drawOn(c, letter[0] * 0.16, chartsStart - chartSpacing)
    else:
        c.drawCentredString(letter[0] * 0.5, chartsStart - chartSpacing + chartTitleSpacing, "No Mass Scan 30 mins")

    if hasMassScan30 and hasBaselineData:
        scanDifferneceData = []

        for i, row in enumerate(scan30Data):
            reagent30, product30, intensity30, *other = row
            _, _, intensityBaseline, *other = baselineData[i]

            scanDifferneceData.append(
                [reagent30, product30, float(intensity30) - float(intensityBaseline)]
            )

        _, _, differneces = zip(*scanDifferneceData)

        _, massScanDifferenceDrawing = drawChart(scanDifferneceData, y_min=min(differneces), y_max=max(differneces))

        c.drawCentredString(letter[0] * 0.5,  chartsStart - chartSpacing * 2 + chartTitleSpacing, "Mass Scan Difference")
        massScanDifferenceDrawing.drawOn(c, letter[0] * 0.16,  chartsStart - chartSpacing * 2)
    else:
        c.drawCentredString(letter[0] * 0.5,  chartsStart - chartSpacing * 2 + chartTitleSpacing, "No Mass Scan baseline or 30 mins")

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
        baselineDrawing.drawOn(c, 0, letter[1] * 0.7)
    else:
        c.drawCentredString(letter[0] * 0.5, letter[1] * 0.7, "No Baseline Scan")

    c.showPage()
    c.save()

