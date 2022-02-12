class ConstraintSolverInterface:
  def __init__(self, constraintObjectList, defenderDict, defenderNames):
    self.constraintObjectList = constraintObjectList
    self.defenderDict = defenderDict
    self.defenderNames = defenderNames
  
  def buildConstraint(self):
    raise Exception("ConstraintSolverInterface.build() is not implemented yet")

class CustomizedMetricScoreInterface:
  def __init__(self, kwargs):
    self.kwargs = kwargs
  
  def getScore(self, scoreDictionary):
    raise Exception("CustomizedMetricScoreInterface.getScore() not implemented yet")