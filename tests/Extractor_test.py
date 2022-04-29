import sys
sys.path.append("..") # Adds higher directory to python modules path.
from Utils import CreateTemp
from Constants import BASELINE_PERFORMANCE
import copy

inputData = {
    "data":{
    "cifar100":{
      "EfficientNetB0_0":{
        "baseline_performance": {
          "natural_accuracy": 89.75,
          "natural_precision": 89.84966927588432,
          "natural_recall": 89.75000000000001,
          "natural_f1-score": 89.75525642610718,
          "inference_elapsed_time_per_1000_in_s": 4.430695599999998
      },
      "grey-box_setting": {
        "PGD": {
            "type_of_attack": "evasion",
            "attackParams": {
                "batch_size": 20,
                "max_iter": 150,
                "eps": 0.85,
                "num_random_init": 3
            },
            "attacker_performance": {
                "robust_accuracy": 1.92,
                "robust_precision": 2.51718052533673,
                "robust_recall": 1.9200000000000002,
                "robust_f1-score": 2.0987320627962514
            },
            "defenders": [
                {
                    "nameOfDefender": "emulated-ae",
                    "type": "PREPROCESSOR",
                    "defense_params": {
                        "intermediary_size": 28,
                        "method": "bilinear"
                    },
                    "defender_performance": {
                        "natural_accuracy": 85.68,
                        "natural_precision": 85.80686387484933,
                        "natural_recall": 85.68,
                        "natural_f1-score": 85.67074707812651,
                        "robust_accuracy": 77.60000000000001,
                        "robust_precision": 77.84991382138296,
                        "robust_recall": 77.6,
                        "robust_f1-score": 77.58655585393535,
                        "inference_elapsed_time_per_1000_in_s": 0.022953600000000005
                    }
                }]
          }
        }
      }
    }
  }
  }

def test_JSONKeysExtractorWithFullInput():
  from Extractors import JSONKeysExtractor
  copyInputData = copy.deepcopy(inputData)
  createTemp = CreateTemp(tempPath=".", suffix = ".json")
  createTemp.createTempFile(contentToWrite=copyInputData)
  
  extractor = JSONKeysExtractor(jsonFilePath=createTemp.tempFileName)
  actualResult = extractor.provideKeyList()
  expectedResult = {
    'baseline_performance': ['natural_accuracy', 'natural_precision', 'natural_recall', 'natural_f1-score', 'inference_elapsed_time_per_1000_in_s'], 
    'attacker_performance': ['robust_accuracy', 'robust_precision', 'robust_recall', 'robust_f1-score'], 
    'defender_performance': [
      'natural_accuracy', 'natural_precision', 'natural_recall', 'natural_f1-score',
      'robust_accuracy', 'robust_precision', 'robust_recall', 'robust_f1-score',
      'inference_elapsed_time_per_1000_in_s']
    }
  assert(expectedResult == actualResult)
  createTemp.closeTempFile()

def test_JSONKeysExtractorWithPartialInput():
  from Extractors import JSONKeysExtractor
  copyInputData = copy.deepcopy(inputData)
  copyInputData['data']['cifar100']['EfficientNetB0_0'][BASELINE_PERFORMANCE] = {}

  createTemp = CreateTemp(tempPath=".", suffix = ".json")
  createTemp.createTempFile(contentToWrite=copyInputData)
  
  extractor = JSONKeysExtractor(jsonFilePath=createTemp.tempFileName)
  actualResult = extractor.provideKeyList()
  expectedResult = {
    'baseline_performance': [], 
    'attacker_performance': ['robust_accuracy', 'robust_precision', 'robust_recall', 'robust_f1-score'], 
    'defender_performance': [
      'natural_accuracy', 'natural_precision', 'natural_recall', 'natural_f1-score',
      'robust_accuracy', 'robust_precision', 'robust_recall', 'robust_f1-score',
      'inference_elapsed_time_per_1000_in_s']
    }
  assert(expectedResult == actualResult)
  createTemp.closeTempFile()

def test_JSONKeysExtractorWithNoKeys():
  from Extractors import JSONKeysExtractor
  copyInputData = {'data':{}}
  createTemp = CreateTemp(tempPath=".", suffix = ".json")
  createTemp.createTempFile(contentToWrite=copyInputData)
  
  extractor = JSONKeysExtractor(jsonFilePath=createTemp.tempFileName)
  import pytest
  with pytest.raises(Exception):
    actualResult = extractor.provideKeyList()
    expectedResult = {
      'baseline_performance': [], 
      'attacker_performance': [], 
      'defender_performance': []
      }
    assert(expectedResult == actualResult)
  createTemp.closeTempFile()

def test_JSONKeysExtractorWithEmptyFile():
  from Extractors import JSONKeysExtractor
  copyInputData = {}
  createTemp = CreateTemp(tempPath=".", suffix = ".json")
  createTemp.createTempFile(contentToWrite=copyInputData)
  
  extractor = JSONKeysExtractor(jsonFilePath=createTemp.tempFileName)
  import pytest
  with pytest.raises(Exception):
    actualResult = extractor.provideKeyList()
    expectedResult = {
      'baseline_performance': [], 
      'attacker_performance': [], 
      'defender_performance': []
      }
    assert(expectedResult == actualResult)
  createTemp.closeTempFile()
