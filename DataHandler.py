from Constants import BASELINE_PERFORMANCE, THREAT_MODELS, STATUS_DICT
from ConstraintBuilder import PulPConstraintBuilder
import json
from collections import defaultdict
from pulp import *

# TODO: we probably need 'recommendation_score' as per each testing parameter

class InputDataHandler:
  def __init__(self, scoreCalculatorFunc = None, verbose = False, kwargs = {}):
    self.scoreCalculatorFunc = scoreCalculatorFunc
    self.verbose = verbose
    self.kwargs = kwargs

  def _solveConstraintProblem(self, defenderDict):
    recommendations = []
    defenderNames = list(defenderDict.keys())
    constraintObjectList=self.kwargs['pulp_settings']['constraints']
    pulPConstraintBuilder = PulPConstraintBuilder(
      defenderNames = defenderNames,
      defenderDict = defenderDict,
      constraintObjectList = constraintObjectList,
      topK = self.kwargs['pulp_settings']['top_K_rec_per_parameter']
    ) # TODO: create constants for each string here
    totalScore = pulPConstraintBuilder.build()
    statusCode = totalScore.solve()
    for v in totalScore.variables():
      if v.varValue > 0:
        recommendations.append(v.name)
        # print("result: {}".format(v.name))
    # print("status: {}".format(status)) # -1: Infeasible, 1: optimal solution found, 0: not solved
    # print("recommendations: {}, type of recommendations: {}, status: {}".format(recommendations, type(recommendations), STATUS_DICT[statusCode]))
    return recommendations, STATUS_DICT[statusCode]

  def handle(self, jsonFilePath):
    recommendation_result = defaultdict()
    inputData = {}
    with open(jsonFilePath, 'r') as fp:
        inputData = json.load(fp)
    
    if 'data' not in inputData:
      raise Exception("data key is not found in {}".format(jsonFilePath))

    data = inputData['data']
    datasetNames = data.keys()
    modelNames = []
    attackerNames = []
    defenderNames = []
    
    for datasetName, datasetValue in data.items():
      modelNames = datasetValue.keys()
      if datasetName not in recommendation_result:
        recommendation_result[datasetName] = {}

      for modelName, modelValue in datasetValue.items():
        if modelName not in recommendation_result[datasetName]:
          recommendation_result[datasetName][modelName] = {}
        threatModelDict = {}

        for threatModel in THREAT_MODELS:
          if threatModel in modelValue:
            if threatModel not in recommendation_result[datasetName][modelName]:
              recommendation_result[datasetName][modelName][threatModel] = {}

            threatModelDict[threatModel] = modelValue[threatModel]
            attackerNames = threatModelDict[threatModel].keys()

            for attackerName, attackerData in threatModelDict[threatModel].items():
              scoreDictionary = {
                "baseline_performance": modelValue[BASELINE_PERFORMANCE],
                "attacker_performance": attackerData['attacker_performance']
              }
              # print("\nattackerPerformance: {}".format(attackerPerformance))
              defenderListForCurrentAttack = attackerData['defenders']
              defenderDict = {}

              for defenderObjectIdx, defenderObject in enumerate(defenderListForCurrentAttack):
                defenderDict[defenderObject['nameOfDefender']] = defenderObject

                scoreDictionary['defender_performance'] = defenderObject['defender_performance']
                if self.scoreCalculatorFunc is not None:
                  result = self.scoreCalculatorFunc(scoreDictionary = scoreDictionary)
                  scoreName = result['score_name']
                  score = result['score']
                  defenderDict[defenderObject['nameOfDefender']]['defender_performance'][scoreName] = score
                  # data[datasetName][modelName][threatModel][attackerName]['defenders'][defenderObjectIdx][scoreName] = score

                  if self.verbose:
                    print("\n[InputDataHandler] datasetName: {}, modelName: {}, threatModel: {}, attackerName: {}, defender's name: {}, cs01_score: {}".format(
                            datasetName, modelName, threatModel, attackerName, defenderObject['nameOfDefender'], score
                    ))
              recommendations, status = self._solveConstraintProblem(defenderDict = defenderDict)
              recommendation_result[datasetName][modelName][threatModel][attackerName] = {
                "solver_status": status,
                "recommendations": recommendations
              }
    return recommendation_result
