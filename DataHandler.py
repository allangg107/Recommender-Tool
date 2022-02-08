from Constants import BASELINE_PERFORMANCE, THREAT_MODELS, STATUS_DICT
from ConstraintHandler import PulPConstraintBuilder
import json
from collections import defaultdict

# TODO: we probably need 'recommendation_score' as per each testing parameter

class InputDataHandler:
  def __init__(self, scoreCalculatorFunc = None, verbose = False, kwargs = {}):
    self.scoreCalculatorFunc = scoreCalculatorFunc
    self.verbose = verbose
    self.kwargs = kwargs

  def handle(self, jsonFilePath):
    recommendation_result = defaultdict()
    inputData = {}
    with open(jsonFilePath, 'r') as fp:
        inputData = json.load(fp)
    
    if 'data' not in inputData:
      raise Exception("data key is not found in {}".format(jsonFilePath))

    data = inputData['data']
    
    for datasetName, datasetValue in data.items():
      if datasetName not in recommendation_result:
        recommendation_result[datasetName] = {}

      recommendation_result = self._buildRecommendationResultPerDataset(
        recommendation_result = recommendation_result,
        datasetName = datasetName,
        datasetValue = datasetValue
      )

    return recommendation_result

  def _buildRecommendationResultPerDataset(self, recommendation_result, datasetName, datasetValue):
    for modelName, modelValue in datasetValue.items():
      if modelName not in recommendation_result[datasetName]:
        recommendation_result[datasetName][modelName] = {}
      
      recommendation_result = self._buildRecommendationResultGivenModel(
        recommendation_result = recommendation_result,
        datasetName = datasetName,
        modelName = modelName,
        modelValue = modelValue
      )
    return recommendation_result

  def _buildRecommendationResultGivenModel(self, recommendation_result, datasetName, modelName, modelValue):
    threatModelDict = {}
    for threatModel in THREAT_MODELS:
      if threatModel in modelValue:
        if threatModel not in recommendation_result[datasetName][modelName]:
          recommendation_result[datasetName][modelName][threatModel] = {}

        threatModelDict[threatModel] = modelValue[threatModel]
        recommendation_result = self._buildRecommendationResultGivenAttack(
          modelValue = modelValue,
          recommendation_result = recommendation_result,
          datasetName = datasetName,
          modelName = modelName,
          threatModel = threatModel,
          threatModelData = threatModelDict[threatModel]
        )
    return recommendation_result

  def _buildRecommendationResultGivenAttack(self, threatModelData, modelValue,
    recommendation_result, datasetName, modelName, threatModel):
    for attackerName, attackerData in threatModelData.items():
      scoreDictionary = {
        "baseline_performance": modelValue[BASELINE_PERFORMANCE],
        "attacker_performance": attackerData['attacker_performance']
      }
      defenderDict = self._buildDefenderDict(
        defenderListForCurrentAttack = attackerData['defenders'],
        scoreDictionary = scoreDictionary
      )

      recommendations, status = self._solveConstraintProblem(defenderDict = defenderDict)
      recommendation_result[datasetName][modelName][threatModel][attackerName] = {
        "solver_status": status,
        "recommendations": recommendations
      }
    return recommendation_result

  def _buildDefenderDict(self, defenderListForCurrentAttack, scoreDictionary):
    defenderDict = {}
    for defenderObjectIdx, defenderObject in enumerate(defenderListForCurrentAttack):
      defenderDict[defenderObject['nameOfDefender']] = defenderObject
      scoreDictionary['defender_performance'] = defenderObject['defender_performance']
      if self.scoreCalculatorFunc is not None:
        result = self.scoreCalculatorFunc(scoreDictionary = scoreDictionary)
        scoreName = result['score_name']
        score = result['score']
        defenderDict[defenderObject['nameOfDefender']]['defender_performance'][scoreName] = score

        if self.verbose:
          print("\n[InputDataHandler] datasetName: {}, modelName: {}, threatModel: {}, attackerName: {}, defender's name: {}, cs01_score: {}".format(
                  datasetName, modelName, threatModel, attackerName, defenderObject['nameOfDefender'], score
          ))
    return defenderDict

  def _solveConstraintProblem(self, defenderDict):
    recommendations = []
    constraintObjectList=self.kwargs['pulp_settings']['constraints']
    pulPConstraintBuilder = PulPConstraintBuilder(
      defenderNames = list(defenderDict.keys()),
      defenderDict = defenderDict,
      constraintObjectList = constraintObjectList,
      topK = self.kwargs['pulp_settings']['top_K_rec_per_parameter']
    ) # TODO: create constants for each string here
    totalScore = pulPConstraintBuilder.build()
    statusCode = totalScore.solve()
    for v in totalScore.variables():
      if v.varValue > 0:
        recommendations.append(v.name)
    return recommendations, STATUS_DICT[statusCode]