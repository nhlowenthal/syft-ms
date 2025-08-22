import os
import re
from pathlib import Path
import csv
import logging

from render_pdf import renderClientPDF, renderAverageBaseline

# --------------
# VARIABLES
# --------------

ROOT = "/Users/school/Downloads/Chem-H Metabolite data and Mass Scans/"
OUTPUT_FOLDER = Path(ROOT) / "results"

# --------------

logging.basicConfig(format='[ %(levelname)s ] - %(message)s', level=logging.INFO)


def process_file(fileName):
    logging.info(f"Processing file {fileName}")
    data = []

    with open(fileName, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)

    data = data[266:1424]

    # Skip Incomplete  Files
    for row in data:
        if row[0] == '':
            logging.warning("File Incomplete")
            return None

    row_len = data[0].index(':')

    data = list([row[:row_len] for row in data])

    data = {
        (int(reagent), int(product)): list(map(float, intensities)) for reagent, product, *intensities in data
    }

    # Manually Filter Some Combinations
    filters = {
        19: (19, 37),
        30: (30,),
        32: (32,),
    }

    for reagent, products in filters.items():
        for product in products:
            if (reagent, product) in data:
                del data[(reagent, product)]

    for key in data.keys():
        data[key] = [sum(data[key]) / len(data[key])]

    return data

def catenateFilesWithAverage(fileNames, fileDatas):
    newData = {}
    for fileData in fileDatas:
        for key, valueList in fileData.items():
            value = valueList[0]
            if key not in newData:
                newData[key] = [value]
            else:
                newData[key].append(value)

    for reagent_product, intensities in newData.items():
        averageIntensity = sum(intensities) / len(intensities)
        intensitiesWithAverage = [averageIntensity]
        intensitiesWithAverage.extend(intensities)
        newData[reagent_product] = intensitiesWithAverage

    newFilenames = ["Average Intensity", *fileNames]

    return (newFilenames, newData)

def readFileData(filePath):
    data = []
    output = {}
    with open(filePath, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)

    for row in data[1:]:
        reagent, product, intensity, *other = row
        output[(int(reagent), int(product))] = [float(intensity)]

    return output



def writeFileDatas(outputPath, outputName, columnNames, fileDatas):
    outputFilePath = Path(outputPath) / (outputName + '.csv')

    with open(outputFilePath, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["Reagent", "Product", *columnNames])
        for (reagent, product), values in fileDatas.items():
            writer.writerow([reagent, product, *values])

def findBaselineFilenames(clientDirectoryName, rootDir):
    logging.info(f"Processing {clientDirectoryName}")

    clientPath = Path(rootDir) / clientDirectoryName

    baselineFiles = []

    for item in os.listdir(clientPath):
        filename = os.path.join(clientPath, item)

        if os.path.isfile(filename):
            continue

        if (re.match(r'0.*baseline.*', item.lower()) or re.match(r'2.*mass.*', item.lower())):
            baselineFiles.extend([os.path.join(filename, f) for f in os.listdir(filename)])

    def baselineFilenameFilter(fileName):
        if not fileName.endswith('.csv'):
            return False

        # Manually Filter out relevant files
        # Adjust if needed
        for item in [
            'baseline',
            ' 0min',
            ' 0 min',
            'neg3',
            'neg7',
            'neg 3',
            'neg 7',
            ' -3 ',
            ' -7 ',
            ' -3min',
            ' -7min',
        ]:
            if item.lower() in fileName.lower():
                return True

        return False

    baselineFiles = list(filter(baselineFilenameFilter, baselineFiles))
    return baselineFiles


def processBaseline(clientDirectoryName, rootDir, outputPath):
    successfulFileName = []
    successfulFileData = []

    files_to_process = findBaselineFilenames(clientDirectoryName, rootDir)

    for file in files_to_process:
        fileData = process_file(file)

        if fileData is None:
            continue

        successfulFileName.append(Path(file).name)
        successfulFileData.append(fileData)

    (catenatedFileNames, catenatedFileDatas) = catenateFilesWithAverage(successfulFileName, successfulFileData)

    writeFileDatas(outputPath, clientDirectoryName + "-baseline", catenatedFileNames, catenatedFileDatas)



def findMassScansFileNames(clientFolder, rootDir):
    clientPath = Path(rootDir) / clientFolder
    allDirectoresUnderClient = [os.path.join(clientPath, d) for d in os.listdir(clientPath) if
                                os.path.isdir(os.path.join(clientPath, d))]
    allScanFiles = []
    for subDir in allDirectoresUnderClient:
        for fileName in os.listdir(os.path.join(subDir, subDir)):
            res = re.search(r"2-Mass-Scan-pos-neg.* ([0-9]+)min.*\.csv$", fileName)
            if res is None:
                continue
            minutes = int(res.group(1))
            if minutes == 30:
                allScanFiles.append((os.path.join(subDir, fileName), minutes))
    return allScanFiles


def processMassScans(clientFolder, rootDir, outputPath):
    allScanPaths = findMassScansFileNames(clientFolder, rootDir)
    clientPath = Path(rootDir) / clientFolder

    for (scanPath,time) in allScanPaths:
        scanData = process_file(scanPath)
        fileName = Path(scanPath).name
        outputName = clientFolder + "-" + str(time) + "min"
        writeFileDatas(outputPath, outputName, [fileName], scanData)

def findAllBaselinesinOutputFolder(outputPath):
    baselineFiles = [Path(outputPath)/f for f in os.listdir(outputPath) if f.endswith('baseline.csv')]
    return baselineFiles


def computeConsolodatedBaselines(outputPath):
    allFiles = findAllBaselinesinOutputFolder(outputPath)
    allFiles.sort()
    allNames = []
    allDatas = []
    for file in allFiles:
        data = readFileData(file)
        if data != {}:
            allNames.append(file.stem)
            allDatas.append(data)

    (newNames, newData) = catenateFilesWithAverage(allNames, allDatas)
    writeFileDatas(outputPath, "averageBaseline", newNames, newData)


if __name__ == "__main__":
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    clientFolders = [f for f in os.listdir(ROOT) if re.match(r'AL-\d*', f)]

    for clientFolder in clientFolders:
        processBaseline(clientFolder, ROOT, OUTPUT_FOLDER)
        processMassScans(clientFolder, ROOT, OUTPUT_FOLDER)

        outputBaseline = OUTPUT_FOLDER / (clientFolder +"-baseline.csv")
        output30min = OUTPUT_FOLDER / (clientFolder +"-30min.csv")
        renderClientPDF(outputBaseline, output30min)

        computeConsolodatedBaselines(OUTPUT_FOLDER)
        aveageBaselinePath = OUTPUT_FOLDER / "averageBaseline.csv"
        renderAverageBaseline(aveageBaselinePath)


