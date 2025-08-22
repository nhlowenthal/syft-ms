import os
from unittest import TestCase

from al_syft import findMassScansFileNames, processMassScans, processBaseline, findAllBaselinesinOutputFolder, \
    readFileData, catenateFilesWithAverage, writeFileDatas
from al_syft import ROOT
from al_syft import OUTPUT_FOLDER


class Test(TestCase):
    def test_find_mass_scans(self):
        outputList = findMassScansFileNames("AL-07", ROOT)

        self.assertEqual(outputList, [("/Users/school/Downloads/Chem-H Metabolite data and Mass Scans/AL-07/2-AL-7 Mass Scans/2-Mass-Scan-pos-neg-AL-07 30min-20181219-163117.csv", 30)])

    def test_processMassScans(self):
        processMassScans("AL-07", ROOT, OUTPUT_FOLDER)

    def test_processBaseline(self):
        processBaseline("AL-66", ROOT, OUTPUT_FOLDER)

    def test_findAllBaselinesinOutputFolder(self):
        allFiles = findAllBaselinesinOutputFolder(OUTPUT_FOLDER)
        allFiles.sort()
        allNames = []
        allDatas = []
        for file in allFiles:
           data = readFileData(file)
           if data != {}:
               allNames.append(file.stem)
               allDatas.append(data)

        (newNames, newData) = catenateFilesWithAverage(allNames, allDatas)
        writeFileDatas(OUTPUT_FOLDER, "averageBaseline", newNames, newData)

        pass
