from pulp import *
from Interfaces import ConstraintSolverInterface

"""
This component build and solve the problem based on a set of constraints by utilizing PulP constraint solver
"""
class PulP(ConstraintSolverInterface):
  def __init__(self, constraintObjectList, defenderDict, defenderNames):
    self.numberOfMinConditionsLimit = 0
    self.numberOfMaxConditionsLimit = 0
    self.numberOfCurrentMinConditions = 0
    self.numberOfCurrentMaxConditions = 0
    ConstraintSolverInterface.__init__(self,
      constraintObjectList = constraintObjectList,
      defenderDict = defenderDict,
      defenderNames = defenderNames
    )
    self._checkParams()
  
  def _checkParams(self):
    if self.constraintObjectList is None or self.constraintObjectList == []:
      raise Exception("constraintObjectList is either None of []")

  def getStatusCode(self) -> int:
    return self.statusCode

  def getVariables(self):
    return (self.constraintObject).variables()

  """
  Build and solve constrained problem
  @param None
  @return solution of the given problem
  """
  def solve(self):
    if self.constraintObject is None:
      raise Exception("PulP's constraint object is None")
    if (self.numberOfMaxConditionsLimit != self.numberOfCurrentMaxConditions) or (self.numberOfMinConditionsLimit != self.numberOfCurrentMinConditions):
      raise Exception("Need to add min/max constraint")

    return (self.constraintObject).solve()

  """
  Build a single constraint
  @param constraintObject current constraint object
  @param expression mathematical expression
  @return constraint object
  """
  def _buildAContraint(self, constraintObject, expression = []):
    op = constraintObject['constraint']
    value, expression = None, None
    if 'metric_name' in constraintObject:
      metric_name = constraintObject['metric_name']
      expression = [self.defenderDict[i]['defender_performance'][metric_name] * self.defenderVars[i] for i in self.defenderVars]

    if 'constraint_value' in constraintObject:
      value = float(constraintObject['constraint_value'])
    
    problem_statement = (constraintObject['problem_statement'] if 'problem_statement' in constraintObject else "")
    if op == 'LpMaximize':
      self.numberOfMaxConditionsLimit = 1
      return LpProblem(problem_statement, LpMaximize)
    elif op == 'LpMinimize':
      self.numberOfMinConditionsLimit = 1
      return LpProblem(problem_statement, LpMinimize)
    
    elif op == 'max' or op == 'min':
      if op == 'max':
        if self.numberOfMaxConditionsLimit == self.numberOfCurrentMaxConditions:
          raise Exception("Only 1 Max constraint")
        self.numberOfCurrentMaxConditions += 1
      elif op == 'min':
        if self.numberOfMinConditionsLimit == self.numberOfCurrentMinConditions:
          raise Exception("Only 1 Min constraint")
        self.numberOfCurrentMinConditions += 1
      return lpSum(expression)
    elif op == '>=':
      return lpSum(expression) >= value
    elif op == '<=':
      return lpSum(expression) <= value
    elif op == '==':
      return lpSum(expression) == value
  
  """
  Build a set of constraint and store it in state variable 'constraintObject'
  @param None
  @return None
  """
  def buildConstraint(self):
    self.defenderVars = LpVariable.dicts("Defenders", self.defenderNames, lowBound=0, upBound=1, cat='Integer')
    totalScore = None
    for constraintObject in self.constraintObjectList:
      if totalScore is None:
        totalScore = self._buildAContraint(
          constraintObject = constraintObject
        )
      else:
        totalScore += self._buildAContraint(
          constraintObject = constraintObject
        )
    totalScore += lpSum([self.defenderVars[i] for i in self.defenderVars]) == 1 # top 1 result
    self.constraintObject = totalScore
    # return totalScore