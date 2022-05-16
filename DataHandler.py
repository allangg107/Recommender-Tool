from Constants import BASELINE_PERFORMANCE, THREAT_MODELS, STATUS_DICT
import json
from collections import defaultdict
from Loader import ConstraintSolverClassLoader

"""
This component handles the parsing and processing of the input data
"""
class InputDataHandler:
  """
  scoreCalculatorFuncDict: a dictionary of user-defined metrics.
      Key of scoreCalculatorFuncDict is the metric name and value is a callable method to calculate the score
  settingKwargs: user setting including constraints and path to solvers and user-defined metric score implementation
  """
  def __init__(self, scoreCalculatorFuncDict = {}, verbose = False, settingKwargs = {}, show_outcome_details = False):
    self.scoreCalculatorFuncDict = scoreCalculatorFuncDict
    self.verbose = verbose
    self.settingKwargs = settingKwargs
    self.show_outcome_details = (show_outcome_details if 'show_outcome_details' not in settingKwargs else settingKwargs['show_outcome_details'])

  """
  This public method parses and processes the input data
  @param jsonFilePath string file path to the user's input JSON data file
  @return recommendations based on the user's input JSON data file
  """
  def handle(self, jsonFilePath:str):
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

  """
  This private method build a recommendation dictionary for each dataset
  @param recommendation_result previous recommendation dictionary
  @param datasetName name of the current dataset
  @param datasetValue performance of the current classifier
  @return recommendation dictionary of a given dataset
  """
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

  """
  This private method build a recommendation dictionary for each classifier
  @param recommendation_result previous recommendation dictionary
  @param datasetName name of the current dataset
  @param modelName name of the current classifier
  @param modelValue performance of the current classifier
  @return recommendation dictionary of a given classifier
  """
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

  """
  This private method build a recommendation dictionary for each attack scenario
  @param threatModelData a dictionary where key is threat model and value is the corresponding data
  @param modelValue a dictionary where name is a classifier name and value is its performance
  @param recommendation_result previous recommendation dictionary
  @param datasetName current dataset
  @param modelName current classifier name
  @param threatModel current threat model setting
  @return recommendation dictionary of a given attack
  """
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

      recommendation, status = self._solveConstraintProblem(defenderDict = defenderDict)
      recommendation_result[datasetName][modelName][threatModel][attackerName] = {
        "solver_status": status,
        "recommendation": recommendation
      }
      if self.show_outcome_details:
        recommendation_result[datasetName][modelName][threatModel][attackerName]["outcome_details"] = [denoiserPerformanceObeject for denoiserName, denoiserPerformanceObeject in defenderDict.items()]
    return recommendation_result

  """
  This private method build the defender dictionary including the defender's name and its performance
  @param defenderListForCurrentAttack list of defender names
  @param scoreDictionary a dictionary where key is name of a score and value is the score
  @return dictionary where key is a namee of a defender and value is its performance object
  """
  def _buildDefenderDict(self, defenderListForCurrentAttack, scoreDictionary):
    defenderDict = {}
    for defenderObjectIdx, defenderObject in enumerate(defenderListForCurrentAttack):
      defenderDict[defenderObject['nameOfDefender']] = defenderObject
      scoreDictionary['defender_performance'] = defenderObject['defender_performance']
      scoreDictionary['nameOfDefender'] = defenderObject['nameOfDefender']
      if self.scoreCalculatorFuncDict is not None and self.scoreCalculatorFuncDict != {}:
        for scoreCalculatorFuncName, scoreCalculatorFunc in self.scoreCalculatorFuncDict.items():
          if scoreCalculatorFunc is not None:
            result = scoreCalculatorFunc(scoreDictionary = scoreDictionary)
            scoreName = scoreCalculatorFuncName
            score = result['score']
            defenderDict[defenderObject['nameOfDefender']]['defender_performance'][scoreName] = score
            defenderDict[defenderObject['nameOfDefender']]['defender_performance']['details_of_{}'.format(scoreName)] = result # additional details of output of user-defined metric
            if self.verbose:
              print("\n[InputDataHandler] datasetName: {}, modelName: {}, threatModel: {}, attackerName: {}, defender's name: {}, cs01_score: {}".format(
                      datasetName, modelName, threatModel, attackerName, defenderObject['nameOfDefender'], score
              ))
    return defenderDict

  """
  This private method solves the problem given a set of constraints
  @param defenderDict dictionary where key is a name of a defender and value is its performance object
  @return a tuple of recommendation and status dictionary
  """
  def _solveConstraintProblem(self, defenderDict):
    recommendation = None
    statusCode = 0
    if self.settingKwargs is not None and self.settingKwargs != {}:
      constraintObjectList = self.settingKwargs['solver']['constraints']
      solverClassLoader = ConstraintSolverClassLoader(path=self.settingKwargs['solver']['path'], name=self.settingKwargs['solver']['name'],kwargs={
        "defenderNames": list(defenderDict.keys()),
        "defenderDict": defenderDict,
        "constraintObjectList": constraintObjectList
      })
      constraintSolver = solverClassLoader.loadSolver()
      constraintSolver.buildConstraint()
      statusCode = constraintSolver.solve()
      for v in constraintSolver.getVariables():
        if v.varValue > 0:
          recommendation = v.name
      if statusCode != 1: # either problem is infeasible or not solved
        recommendation = None
    return recommendation, STATUS_DICT[statusCode]
