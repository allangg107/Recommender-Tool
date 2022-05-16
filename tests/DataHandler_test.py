import sys
sys.path.append("..") # Adds higher directory to python modules path.
from DataHandler import InputDataHandler
from collections import defaultdict
from Utils import CreateTemp

SOLVER_CODE = """from pulp import *
  \nfrom Interfaces import ConstraintSolverInterface
  \nclass PulP(ConstraintSolverInterface):
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
    
    def getStatusCode(self) -> int:
      return self.statusCode

    def getVariables(self):
      return (self.constraintObject).variables()

    def solve(self):
      if self.constraintObject is None:
        raise Exception("PulP's constraint object is None")
      if (self.numberOfMaxConditionsLimit != self.numberOfCurrentMaxConditions) or (self.numberOfMinConditionsLimit != self.numberOfCurrentMinConditions):
        raise Exception("Need to add min/max constraint")

      return (self.constraintObject).solve()

    def _buildAContraint(self, constraintObject, expression = []):
      op = constraintObject['constraint']
      value, expression = None, None
      if 'metric_name' in constraintObject:
        metric_name = constraintObject['metric_name']
        expression = [self.defenderDict[i]['defender_performance'][metric_name] * self.defenderVars[i] for i in self.defenderVars]

      if 'constraint_value' in constraintObject:
        value = float(constraintObject['constraint_value'])
      
      if op == 'LpMaximize':
        self.numberOfMaxConditionsLimit = 1
        return LpProblem(constraintObject['problem_statement'], LpMaximize)
      elif op == 'LpMinimize':
        self.numberOfMinConditionsLimit = 1
        return LpProblem(constraintObject['problem_statement'], LpMinimize)
      
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
  """

inputData={
    "data": {
      "dataset_1": {
        "model_1": {
          "baseline_performance": {
            "natural_accuracy": 89.75,
            "inference_elapsed_time_per_1000_in_s": 4.4
          },
           "grey-box_setting": {
            "PGD": {
              "type_of_attack": "evasion",
              "attackParams": {},
              "attacker_performance": {
                  "robust_accuracy": 1.92,
              },
              "defenders": [
                  {
                      "nameOfDefender": "defender_1",
                      "type": "PREPROCESSOR",
                      "defense_params": {},
                      "defender_performance": {
                          "natural_accuracy": 85.68,
                          "robust_accuracy": 50,
                          "inference_elapsed_time_per_1000_in_s": 0.0229
                      }
                  },
                  {
                      "nameOfDefender": "defender_2",
                      "type": "PREPROCESSOR",
                      "defense_params": {},
                      "defender_performance": {
                          "natural_accuracy": 84.68,
                          "robust_accuracy": 70,
                          "inference_elapsed_time_per_1000_in_s": 3
                      }
                  }
              ]
           }
        }
      }
    }
  }
  }

def test_InputDataHander_no_solving():
  expected_recommendation_result = defaultdict()
  expected_recommendation_result['dataset_1'] = {
      'model_1': {
        'grey-box_setting': {
          'PGD': {
            'solver_status': 'Not solved',
            'recommendation': None
          }
        }
      }
  }

  
  createTemp = CreateTemp(tempPath=".", suffix = ".json")
  createTemp.createTempFile(contentToWrite=inputData)

  inputDataHandler = InputDataHandler(
    scoreCalculatorFuncDict={},
    settingKwargs={},
    show_outcome_details=False
  )
  recommendation = inputDataHandler.handle(jsonFilePath=(createTemp.tempFileName))
  createTemp.closeTempFile()
  assert(expected_recommendation_result == recommendation)

def test_InputDataHander_with_solving_without_customized_metric():
  # create solver file
  solver_createTemp = CreateTemp(tempPath=".", suffix = ".py")
  solver_createTemp.createTempFile(contentToWrite=SOLVER_CODE)
  solverTempFileName = (solver_createTemp.tempFileName).split('/')[-1][:-3]
  settingKwargs = {
    "solver":{
      "name": "PulP",
      "path": solverTempFileName,
      "constraints":[
        {
          "constraint": "LpMaximize",
          "problem_statement": "best_defender_problem"
        },
        {
          "constraint": "max",
          "metric_name": "natural_accuracy"
        }
      ]
    }
  }

  expected_recommendation_result = defaultdict()
  expected_recommendation_result['dataset_1'] = {
      'model_1': {
        'grey-box_setting': {
          'PGD': {
            'solver_status': 'Optimal solution found',
            'recommendation': "Defenders_defender_1"
          }
        }
      }
  }

  createTemp = CreateTemp(tempPath=".", suffix = ".json")
  createTemp.createTempFile(contentToWrite=inputData)

  inputDataHandler = InputDataHandler(
    scoreCalculatorFuncDict={},
    settingKwargs=settingKwargs,
    show_outcome_details=False
  )
  recommendation = inputDataHandler.handle(jsonFilePath=(createTemp.tempFileName))
  createTemp.closeTempFile()
  assert(expected_recommendation_result == recommendation)

def test_InputDataHander_with_solving_with_customized_metric():
  from Loader import CustomizedMetricScoreClassLoader
  # create solver file
  solver_createTemp = CreateTemp(tempPath=".", suffix = ".py")
  solver_createTemp.createTempFile(contentToWrite=SOLVER_CODE)
  solverTempFileName = (solver_createTemp.tempFileName).split('/')[-1][:-3]
  # create input data
  input_data_createTemp = CreateTemp(tempPath=".", suffix = ".json")
  input_data_createTemp.createTempFile(contentToWrite=inputData)

  settingKwargs = {
    "solver":{
      "name": "PulP",
      "path": solverTempFileName,
      "constraints":[
        {
          "constraint": "LpMaximize",
          "problem_statement": "best_defender_problem"
        },
        {
          "constraint": "max",
          "metric_name": "MetricClone"
        }
      ]
    }
  }
  # create customized metric
  customized_metric_text = """from Interfaces import CustomizedMetricScoreInterface
    \nclass MetricClone(CustomizedMetricScoreInterface):
    def __init__(self, kwargs):
        CustomizedMetricScoreInterface.__init__(self, kwargs=kwargs)
        self.alpha = self.kwargs['alpha']  # time tradeoff coefficient
        self.beta = self.kwargs['beta']    # natural accuracy tradeoff coefficient
        self.gamma = self.kwargs['gamma']  # robust accuracy coefficient
        self.showDetails = self.kwargs['showDetails']
    def getScore(self, scoreDictionary):
      initialTime = scoreDictionary['baseline_performance']['inference_elapsed_time_per_1000_in_s']
      addedTime = scoreDictionary['defender_performance']['inference_elapsed_time_per_1000_in_s']

      naturalAccuracyWithoutDefense = scoreDictionary['baseline_performance']['natural_accuracy']
      robustAccuracyWithoutDefense = scoreDictionary['attacker_performance']['robust_accuracy']

      naturalAccuracyWithDefense = scoreDictionary['defender_performance']['natural_accuracy']
      robustAccuracyWithDefense = scoreDictionary['defender_performance']['robust_accuracy']

      timeTradeOff = self.alpha * ((addedTime) / initialTime)
      naturalAccScoreTradeOff = self.beta * ((naturalAccuracyWithDefense - naturalAccuracyWithoutDefense) / naturalAccuracyWithoutDefense)
      robustAccImprove = self.gamma * ((robustAccuracyWithDefense - robustAccuracyWithoutDefense) / robustAccuracyWithoutDefense)

      MetricClone_score = ( -timeTradeOff + \
        naturalAccScoreTradeOff + \
          robustAccImprove)
      result = {
        "denoiser_name": scoreDictionary['nameOfDefender'],
        "score": MetricClone_score,        # required from users
        "details" : {
          "timeTradeOff": timeTradeOff,
          "naturalAccScoreTradeOff": naturalAccScoreTradeOff,
          "robustAccImprove": robustAccImprove
        }
      }
      if self.showDetails:
        print(result)

      return result
    """
  metric_createTemp = CreateTemp(tempPath=".", suffix = ".py")
  metric_createTemp.createTempFile(contentToWrite=customized_metric_text)

  customizedScoresDict = {}
  tempFileName = (metric_createTemp.tempFileName).split('/')[-1][:-3]
  customizedMetricScoreClassLoader = CustomizedMetricScoreClassLoader(
    path = tempFileName,
    name = "MetricClone",
    kwargs = {
      "showDetails": True,
      "alpha": 1,
      "beta": 1,
      "gamma": 10
    }
  )
  scoreCalculator = customizedMetricScoreClassLoader.loadScore()
  customizedScoresDict["MetricClone"] = scoreCalculator.getScore

  inputDataHandler = InputDataHandler(
    scoreCalculatorFuncDict=customizedScoresDict,
    settingKwargs=settingKwargs,
    show_outcome_details=False
  )
  recommendation = inputDataHandler.handle(jsonFilePath=(input_data_createTemp.tempFileName))
  expected_recommendation_result = defaultdict()
  expected_recommendation_result['dataset_1'] = {
      'model_1': {
        'grey-box_setting': {
          'PGD': {
            'solver_status': 'Optimal solution found',
            'recommendation': "Defenders_defender_2"
          }
        }
      }
  }
  assert(expected_recommendation_result == recommendation)
  metric_createTemp.closeTempFile()
  input_data_createTemp.closeTempFile()
  solver_createTemp.closeTempFile()