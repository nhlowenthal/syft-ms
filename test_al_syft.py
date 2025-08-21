from unittest import TestCase

from al_syft import findMassScansFileNames, processMassScans
from al_syft import ROOT


class Test(TestCase):
    def test_find_mass_scans(self):
        outputList = findMassScansFileNames("AL-07", ROOT)

        self.assertEqual(outputList, [("/Users/school/Downloads/Chem-H Metabolite data and Mass Scans/AL-07/2-AL-7 Mass Scans/2-Mass-Scan-pos-neg-AL-07 30min-20181219-163117.csv", 30)])

    def test_processMassScans(self):
        processMassScans("AL-07", ROOT, "foo")
