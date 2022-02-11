from ConstraintHandlerInterface import ConstraintSolverInterface

class DynamicClassLoader:
  def load(self, classPath : str = None,className : str = None):
    Kclass = getattr(__import__(classPath, fromlist=[className]), className)
    return Kclass

class SolverClassLoader:
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