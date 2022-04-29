class ConstraintSolverInterface:
  def __init__(self, constraintObjectList, defenderDict, defenderNames):
    self.constraintObjectList = constraintObjectList
    self.defenderDict = defenderDict
    self.defenderNames = defenderNames
    self.constraintObject = None
    self.statusCode = None
    self.variables = None
  
  def getStatusCode(self) -> int:
    raise Exception("getStatusCode() is not implemented yet")

  def getVariables(self):
    raise Exception("getVariables() is not implemented yet")

  def solve(self):
    raise Exception("solve() is not implemented yet")

  def buildConstraint(self):
    raise Exception("ConstraintSolverInterface.build() is not implemented yet")

class CustomizedMetricScoreInterface:
  def __init__(self, kwargs):
    self.kwargs = kwargs
  
  def getScore(self, scoreDictionary):
    raise Exception("CustomizedMetricScoreInterface.getScore() not implemented yet")