from pathlib import Path
from unittest import TestCase
from render_pdf import renderClientPDF


class Test(TestCase):
    def test_render_pdf(self):
        renderClientPDF(Path("/Users/school/Downloads/Chem-H Metabolite data and Mass Scans/results/AL-07-baseline.csv"),
                   Path("/Users/school/Downloads/Chem-H Metabolite data and Mass Scans/results/AL-07-30min.csv"))
