# integration test
import sys
sys.path.append("..") # Adds higher directory to python modules path.
from Utils import CreateTemp
import tempfile
import json
from Driver import Driver

INPUT_DATA_PATH = "integration_test_input_data"

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

METRIC_CALCULATOR_CODE = """from Interfaces import CustomizedMetricScoreInterface
    \nclass CS01(CustomizedMetricScoreInterface):
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
      naturalF1ScoreTradeOff = self.beta * ((naturalAccuracyWithDefense - naturalAccuracyWithoutDefense) / naturalAccuracyWithoutDefense)
      robustF1ScoreImprove = self.gamma * ((robustAccuracyWithDefense - robustAccuracyWithoutDefense) / robustAccuracyWithoutDefense)

      MetricClone_score = ( -timeTradeOff + \
        naturalF1ScoreTradeOff + \
          robustF1ScoreImprove)
      result = {
        "denoiser_name": scoreDictionary['nameOfDefender'],
        "score": MetricClone_score,        # required from users
        "details" : {
          "timeTradeOff": timeTradeOff,
          "naturalF1ScoreTradeOff": naturalF1ScoreTradeOff,
          "robustF1ScoreImprove": robustF1ScoreImprove
        }
      }
      if self.showDetails:
        print(result)

      return result
    """

def test_integration_01():
  testNumber = 1
  # set up metric calculator
  metric_createTemp = CreateTemp(tempPath=".", suffix = ".py")
  metric_createTemp.createTempFile(contentToWrite=METRIC_CALCULATOR_CODE)
  tempFileName = (metric_createTemp.tempFileName).split('/')[-1][:-3]

  # set up solver
  solver_createTemp = CreateTemp(tempPath=".", suffix = ".py")
  solver_createTemp.createTempFile(contentToWrite=SOLVER_CODE)
  solverTempFileName = (solver_createTemp.tempFileName).split('/')[-1][:-3]

  userSetting = {
    "input_data_path":"integration_test_input_data/input_01.json",
    "customized_metric_score":[
      {
        "name":"CS01",
        "path": tempFileName,
        "scoreCalculatorParam":{
          "showDetails": True,
          "alpha": 1,
          "beta": 1,
          "gamma": 1
        }
      }
    ],
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
          "metric_name": "CS01"
        },
        {
          "constraint": ">=",
          "constraint_value": 85,
          "metric_name": "natural_accuracy"
        },
        {
          "constraint": "<=",
          "constraint_value": 8,
          "metric_name": "inference_elapsed_time_per_1000_in_s"
        }
      ]
    },
    "output":{
      "output_file_path": "integration_outputs/outp_{}.json".format(testNumber)
    }
  }
  expectedResult = {
    "setting": {
        "input_data_path": "integration_test_input_data/input_01.json",
        "customized_metric_score": [
            {
                "name": "CS01",
                "path": tempFileName,
                "scoreCalculatorParam": {
                    "showDetails": True,
                    "alpha": 1,
                    "beta": 1,
                    "gamma": 1
                }
            }
        ],
        "solver": {
            "name": "PulP",
            "path": solverTempFileName,
            "constraints": [
                {
                    "constraint": "LpMaximize",
                    "problem_statement": "best_defender_problem"
                },
                {
                    "constraint": "max",
                    "metric_name": "CS01"
                },
                {
                    "constraint": ">=",
                    "constraint_value": 85,
                    "metric_name": "natural_accuracy"
                },
                {
                    "constraint": "<=",
                    "constraint_value": 8,
                    "metric_name": "inference_elapsed_time_per_1000_in_s"
                }
            ]
        },
        "output": {
            "output_file_path": "integration_outputs/outp_{}.json".format(testNumber)
        }
    },
    "recommendation_result": {
        "cifar100": {
            "EfficientNetB0_0": {
                "grey-box_setting": {
                    "PGD": {
                        "solver_status": "Optimal solution found",
                        "recommendation": "Defenders_emulated_ae"
                    },
                    "FGSM": {
                        "solver_status": "Optimal solution found",
                        "recommendation": "Defenders_emulated_ae"
                    }
                }
            }
        }
    }
  }
  userSettingTemp = CreateTemp(tempPath=".", suffix = ".json")
  userSettingTemp.createTempFile(contentToWrite=userSetting)
  userSettingTempFileName = (userSettingTemp.tempFileName).split('/')[-1]
  # print("userSettingTempFileName: {}".format(userSettingTempFileName))
  driver = Driver(settingPath=userSettingTempFileName)
  driver.drive()

  actualResult = {}
  with open("integration_outputs/outp_{}.json".format(testNumber), "r") as fp:
    actualResult = json.load(fp)
  
  metric_createTemp.closeTempFile()
  solver_createTemp.closeTempFile()
  userSettingTemp.closeTempFile()
  assert(expectedResult == actualResult)

def test_integration_02():
  testNumber = 2
  # set up metric calculator
  metric_createTemp = CreateTemp(tempPath=".", suffix = ".py")
  metric_createTemp.createTempFile(contentToWrite=METRIC_CALCULATOR_CODE)
  tempFileName = (metric_createTemp.tempFileName).split('/')[-1][:-3]

  # set up solver
  solver_createTemp = CreateTemp(tempPath=".", suffix = ".py")
  solver_createTemp.createTempFile(contentToWrite=SOLVER_CODE)
  solverTempFileName = (solver_createTemp.tempFileName).split('/')[-1][:-3]

  userSetting = {
    "input_data_path":"integration_test_input_data/input_01.json",
    "customized_metric_score":[
      {
        "name":"CS01",
        "path": tempFileName,
        "scoreCalculatorParam":{
          "showDetails": True,
          "alpha": 1,
          "beta": 1,
          "gamma": 1
        }
      }
    ],
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
          "metric_name": "CS01"
        },
        {
          "constraint": ">=",
          "constraint_value": 86,
          "metric_name": "natural_accuracy"
        }
      ]
    },
    "output":{
      "output_file_path": "integration_outputs/outp_{}.json".format(testNumber)
    }
  }
  expectedResult = {
    "setting": {
        "input_data_path": "integration_test_input_data/input_01.json",
        "customized_metric_score": [
            {
                "name": "CS01",
                "path": tempFileName,
                "scoreCalculatorParam": {
                    "showDetails": True,
                    "alpha": 1,
                    "beta": 1,
                    "gamma": 1
                }
            }
        ],
        "solver": {
            "name": "PulP",
            "path": solverTempFileName,
            "constraints": [
                {
                    "constraint": "LpMaximize",
                    "problem_statement": "best_defender_problem"
                },
                {
                    "constraint": "max",
                    "metric_name": "CS01"
                },
                {
                    "constraint": ">=",
                    "constraint_value": 86,
                    "metric_name": "natural_accuracy"
                }
            ]
        },
        "output": {
            "output_file_path": "integration_outputs/outp_{}.json".format(testNumber)
        }
    },
    "recommendation_result": {
        "cifar100": {
            "EfficientNetB0_0": {
                "grey-box_setting": {
                    "PGD": {
                        "solver_status": "Optimal solution found",
                        "recommendation": "Defenders_unet"
                    },
                    "FGSM": {
                        "solver_status": "Optimal solution found",
                        "recommendation": "Defenders_jpegCompression"
                    }
                }
            }
        }
    }
  }
  userSettingTemp = CreateTemp(tempPath=".", suffix = ".json")
  userSettingTemp.createTempFile(contentToWrite=userSetting)
  userSettingTempFileName = (userSettingTemp.tempFileName).split('/')[-1]
  # print("userSettingTempFileName: {}".format(userSettingTempFileName))
  driver = Driver(settingPath=userSettingTempFileName)
  driver.drive()

  actualResult = {}
  with open("integration_outputs/outp_{}.json".format(testNumber), "r") as fp:
    actualResult = json.load(fp)
  
  metric_createTemp.closeTempFile()
  solver_createTemp.closeTempFile()
  userSettingTemp.closeTempFile()
  assert(expectedResult == actualResult)