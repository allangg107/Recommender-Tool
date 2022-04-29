"""
INSTRUCTION TO RUN ALL TEST:
$ pytest
"""
import sys
sys.path.append("..") # Adds higher directory to python modules path.
from Loader import ConstraintSolverClassLoader, CustomizedMetricScoreClassLoader
def test_ConstraintSolverClassLoader():
    
    from Interfaces import ConstraintSolverInterface
    from Utils import CreateTemp

    text = """from Interfaces import ConstraintSolverInterface
    \nclass ConstraintSolverClone(ConstraintSolverInterface):
        def __init__(self, constraintObjectList, defenderDict, defenderNames):
            ConstraintSolverInterface.__init__(self,
                constraintObjectList = constraintObjectList,
                defenderDict = defenderDict,
                defenderNames = defenderNames
            )
        def buildConstraint(self):
            return None
    """
    createTemp = CreateTemp(tempPath="..", suffix=".py")
    createTemp.createTempFile(contentToWrite=text)
    tempFileName = (createTemp.tempFileName).split('/')[-1][:-3]
    constraintSolverClassLoader = ConstraintSolverClassLoader(
        path=tempFileName,
        name="ConstraintSolverClone",
        kwargs={
            "constraintObjectList": {},
            "defenderDict": {},
            "defenderNames": {}
        }
    )
    
    constraintSolver = constraintSolverClassLoader.loadSolver()
    constraintSolver.buildConstraint()
    assert isinstance(constraintSolver, ConstraintSolverInterface)
    createTemp.closeTempFile()

def test_CustomizedMetricScoreClassLoader():
    import sys
    sys.path.append("..") # Adds higher directory to python modules path.
    from Interfaces import CustomizedMetricScoreInterface
    from Utils import CreateTemp

    text = """from Interfaces import CustomizedMetricScoreInterface
    \nclass MetricClone(CustomizedMetricScoreInterface):
    def __init__(self, kwargs):
        CustomizedMetricScoreInterface.__init__(self, kwargs=kwargs)
        self.alpha = self.kwargs['alpha']  # time tradeoff coefficient
        self.beta = self.kwargs['beta']    # natural accuracy tradeoff coefficient
        self.gamma = self.kwargs['gamma']  # robust accuracy coefficient
        self.showDetails = self.kwargs['showDetails']
    def getScore(self, scoreDictionary):
        return None
    """
    createTemp = CreateTemp(tempPath="..", suffix=".py")
    createTemp.createTempFile(contentToWrite=text)
    tempFileName = (createTemp.tempFileName).split('/')[-1][:-3]
    customizedMetricScoreClassLoader = CustomizedMetricScoreClassLoader(
        path=tempFileName,
        name="MetricClone",
        kwargs={
            "alpha":1,
            "beta":1,
            "gamma":1,
            "showDetails":False
        }
    )
    scoreCalculator = customizedMetricScoreClassLoader.loadScore()
    assert isinstance(scoreCalculator, CustomizedMetricScoreInterface)
    createTemp.closeTempFile()