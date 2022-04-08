from Interfaces import ConstraintSolverInterface, CustomizedMetricScoreInterface

class DynamicClassLoader:
  def load(self, classPath : str = None,className : str = None):
    Kclass = getattr(__import__(classPath, fromlist=[className]), className)
    return Kclass

class ConstraintSolverClassLoader:
  def __init__(self, path : str = None, name : str = None, kwargs = {}):
    self.path = path
    self.name = name
    self.kwargs = kwargs

  def loadSolver(self):
    solverClass = DynamicClassLoader().load(
      classPath = self.path,
      className=self.name
    )
    assert(issubclass(solverClass, ConstraintSolverInterface))
    solverObject = solverClass(
      constraintObjectList = self.kwargs['constraintObjectList'],
      defenderDict = self.kwargs['defenderDict'],
      defenderNames = self.kwargs['defenderNames']
    )
    return solverObject

class CustomizedMetricScoreClassLoader:
  def __init__(self, path : str = None, name : str = None, kwargs = {}):
    self.path = path
    self.name = name
    self.kwargs = kwargs
  
  def loadScore(self):
    scoreCalculatorClass = DynamicClassLoader().load(
      classPath = self.path,
      className=self.name
    )
    assert(issubclass(scoreCalculatorClass, CustomizedMetricScoreInterface))
    scoreCalculatorObject = scoreCalculatorClass(kwargs = self.kwargs)
    return scoreCalculatorObject