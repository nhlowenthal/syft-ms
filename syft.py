import glob
import os
import re
from collections import namedtuple
from pathlib import Path

FilePath=namedtuple('FilePath', ['path', 'time'])

def findBaselines(baselinePath, massScanPath):
    pass

def findOtherScans(dirName):
    pass

def getBaselinePathNames(dirName):
    baselines1 = [f for f in os.listdir(dirName) if re.match(r'.*Baseline Data', f)]
    return os.path.join(dirName,baselines1[0])

def getScanPathName(dirName):
    scans = [f for f in os.listdir(dirName) if re.match(r'.*Mass Scan', f)]
    return os.path.join(dirName, scans[0])

def render_report(dirName):
    baslines = findBaselines(dirName)



dir="/Users/school/Downloads/Chem-H Metabolite data and Mass Scans/AL-01"
baselinePath=getBaselinePathNames(dir)
print(baselinePath)

scanPath=getScanPathName(dir)
print(scanPath)
