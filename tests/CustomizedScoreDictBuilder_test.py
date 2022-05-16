import sys
sys.path.append("..") # Adds higher directory to python modules path.
from UserDefinedMetricHandler import CustomizedScoreDictionaryBuilder
from Utils import CreateTemp
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
def test_buildCustomizedDict_with_empty_setting():
  import pytest
  with pytest.raises(Exception):
    setting = {}
    customizedScoreDictBuilder = CustomizedScoreDictionaryBuilder(setting=setting)
    actualResult = customizedScoreDictBuilder.buildCustomizedDict()

def test_buildCustomizedDict_with_invalid_setting():
  import pytest
  with pytest.raises(Exception):
    setting = {"hello":"world"}
    customizedScoreDictBuilder = CustomizedScoreDictionaryBuilder(setting=setting)
    actualResult = customizedScoreDictBuilder.buildCustomizedDict()

def test_buildCustomizedDict_with_non_empty_valid_setting():

  # build temp metric calculator
  customized_metric_text = """from Interfaces import CustomizedMetricScoreInterface
    \nclass MetricClone_01(CustomizedMetricScoreInterface):
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
  metric_createTemp = CreateTemp(tempPath=".", suffix = ".py")
  metric_createTemp.createTempFile(contentToWrite=customized_metric_text)
  tempFileName = (metric_createTemp.tempFileName).split('/')[-1][:-3]

  setting = {
    "customized_metric_score": [
      {
        "name":"MetricClone_01",
        "path": tempFileName,
        "scoreCalculatorParam":{
          "showDetails": True,
          "alpha": 1,
          "beta": 1,
          "gamma": 1
        }
      }
    ]
  }
  customizedScoreDictBuilder = CustomizedScoreDictionaryBuilder(setting=setting)
  actualCustomizedScoresDict = customizedScoreDictBuilder.buildCustomizedDict()
  expectedCustomizedScoresDict = {
    "MetricClone_01": getScore
  }
  #https://stackoverflow.com/a/20059029
  assert(expectedCustomizedScoresDict.keys() == actualCustomizedScoresDict.keys())
  for key in expectedCustomizedScoresDict.keys():
    assert(expectedCustomizedScoresDict[key].__code__.co_code == actualCustomizedScoresDict[key].__code__.co_code)
  metric_createTemp.closeTempFile()