from pulp import *

class PulPConstraintBuilder:
  def __init__(self, constraintObjectList, defenderDict, defenderNames):
    self.constraintObjectList = constraintObjectList
    self.defenderDict = defenderDict
    self.defenderNames = defenderNames
  
  def _buildAContraint(self, constraintObject, expression = []):
    op = constraintObject['constraint']
    value, expression = None, None
    if 'metric_name' in constraintObject:
      metric_name = constraintObject['metric_name']
      expression = [self.defenderDict[i]['defender_performance'][metric_name] * self.defenderVars[i] for i in self.defenderVars]

    if 'constraint_value' in constraintObject:
      value = float(constraintObject['constraint_value'])
    
    if op == 'LpMaximize':
      return LpProblem(constraintObject['problem_statement'], LpMaximize)
    elif op == 'LpMinimize':
      return LpProblem(constraintObject['problem_statement'], LpMinimize)
    elif op == 'max':
      return lpSum(expression)
    elif op == '>=':
      return lpSum(expression) >= value
    elif op == '<=':
      return lpSum(expression) <= value
    elif op == '==':
      return lpSum(expression) == value
  
  def build(self):
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
    return totalScore