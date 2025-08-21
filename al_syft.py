import os
import re
from pathlib import Path
import csv
import logging

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
        data[key] = sum(data[key]) / len(data[key])

    return data


def process_folder(clientDirectoryName, rootDir, outputPath):
    logging.info(f"Processing {clientDirectoryName}")

    outputFilePath = Path(outputPath) / (clientDirectoryName + '.csv')
    clientPath = Path(rootDir) / clientDirectoryName

    files_to_process = []

    for item in os.listdir(clientPath):
        filename = os.path.join(clientPath, item)

        if os.path.isfile(filename):
            continue

        if (
            re.match(r'0.*baseline.*', item.lower())
            or re.match(r'2.*mass.*', item.lower())
        ):
            files_to_process.extend([os.path.join(filename, f) for f in os.listdir(filename)])


    def filter_files(fileName):
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
        ]:
            if item.lower() in fileName.lower():
                return True

        return False

    files_to_process = list(filter(filter_files, files_to_process))

    data = {}
    successfully_processed = []

    for file in files_to_process:
        processed_file = process_file(file)

        if processed_file is None:
            continue

        successfully_processed.append(Path(file).name)

        for key, value in processed_file.items():
            if key not in data:
                data[key] = [value]
            else:
                data[key].append(value)


    with open(outputFilePath, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["Reagent", "Product", "Average Intensity", *successfully_processed])
        for (reagent, product), values in data.items():
            average = sum(values) / len(values)
            writer.writerow([reagent, product, average, *values])

def findMassScansFileNames(clientFolder, rootDir):
    clientPath = Path(rootDir) / clientFolder
    allDirectoresUnderClient = [os.path.join(clientPath,d) for d in os.listdir(clientPath) if os.path.isdir(os.path.join(clientPath, d))]
    allScanFiles = []
    for subDir in allDirectoresUnderClient:
        for fileName in os.listdir(os.path.join(subDir,subDir)):
            res = re.search(r"2-Mass-Scan-pos-neg.* ([0-9]+)min.*\.csv$", fileName)
            if res is None:
                continue
            minutes = int(res.group(1))
            if minutes == 30:
                allScanFiles.append((os.path.join(subDir,fileName), minutes))
    return allScanFiles

def processMassScans(clientFolder, rootDir, outputPath):
    allScanNames = findMassScansFileNames(clientFolder, rootDir)
    clientPath = Path(rootDir) / clientFolder
    for fileName in allScanNames:
       massScanData = process_file(os.path.join(fileName[0]))


if __name__ == "__main__":
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    clientFolders = [f for f in os.listdir(ROOT) if re.match(r'AL-\d*', f)]

    for clientFolder in clientFolders:
        process_folder(clientFolder, ROOT, OUTPUT_FOLDER)


