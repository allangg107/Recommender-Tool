from Interfaces import ConstraintSolverInterface, CustomizedMetricScoreInterface
"""
This class dynamically loads a class given a path to the class description.
"""
class DynamicClassLoader:
  """
  This public method returns an instance of the class given a path to the class description.
  @param classPath path to the class description
  @param className name of class to be instantiated
  @return class instance
  """
  def load(self, classPath : str = None, className : str = None):
    Kclass = getattr(__import__(classPath, fromlist=[className]), className)
    return Kclass

"""
This component focuses on loading a constraint solver class.
"""
class ConstraintSolverClassLoader:
  def __init__(self, path : str, name : str, kwargs : dict):
    self.path = path
    self.name = name
    self.kwargs = kwargs
    self._checkParams()

  def _checkParams(self):
    if self.path is None or self.name is None:
      raise Exception("either path or name is None")
    if self.path == "" or self.name == "":
      raise Exception("path and name must not be empty strings")
    kwargsContainsRequiredKey = ("constraintObjectList" in self.kwargs and "defenderDict" in self.kwargs and "defenderNames" in self.kwargs)
    if not kwargsContainsRequiredKey:
      raise Exception("Missing constraintObjectList, defenderDict or defenderNames required keys in kwargs")

  """
  This public method load and instantiate a constraint solver component.
  @param None
  @return instance of desired constraint solver class
  """
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

"""
This class instantiate an user-defined metric score.
"""
class CustomizedMetricScoreClassLoader:
  def __init__(self, path : str = None, name : str = None, kwargs = {}):
    self.path = path
    self.name = name
    self.kwargs = kwargs
  
  """
  This public method load and instantiate the user-defined metric score class.
  @param None
  @return an instance of the user-defined metric score class
  """
  def loadScore(self):
    scoreCalculatorClass = DynamicClassLoader().load(
      classPath = self.path,
      className=self.name
    )
    assert(issubclass(scoreCalculatorClass, CustomizedMetricScoreInterface))
    scoreCalculatorObject = scoreCalculatorClass(kwargs = self.kwargs)
    return scoreCalculatorObject