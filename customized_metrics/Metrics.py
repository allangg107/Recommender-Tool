# Customized score 01
from Interfaces import CustomizedMetricScoreInterface
class CS01(CustomizedMetricScoreInterface):
  def __init__(self, kwargs):
    CustomizedMetricScoreInterface.__init__(self, kwargs=kwargs)
    self.alpha = self.kwargs['alpha']  # time tradeoff coefficient
    self.beta = self.kwargs['beta']    # natural accuracy tradeoff coefficient
    self.gamma = self.kwargs['gamma']  # robust accuracy coefficient
    self.showDetails = self.kwargs['showDetails']

  """
  This public method returns the score of the given user-defined metric
  @param scoreDictionary data passed from the user's input data
  @return a dictionary containing the score
  """
  def getScore(self, scoreDictionary):
    initialTime = scoreDictionary['baseline_performance']['inference_elapsed_time_per_1000_in_s']
    addedTime = scoreDictionary['defender_performance']['inference_elapsed_time_per_1000_in_s']

    naturalAccuracyWithoutDefense = scoreDictionary['baseline_performance']['natural_accuracy']
    robustAccuracyWithoutDefense = scoreDictionary['attacker_performance']['robust_accuracy']

    naturalAccuracyWithDefense = scoreDictionary['defender_performance']['natural_accuracy']
    robustAccuracyWithDefense = scoreDictionary['defender_performance']['robust_accuracy']

    timeTradeOff = self.alpha * ((addedTime) / initialTime)
    naturalAccTradeOff = self.beta * ((naturalAccuracyWithDefense - naturalAccuracyWithoutDefense) / naturalAccuracyWithoutDefense)
    robustAccImprove = self.gamma * ((robustAccuracyWithDefense - robustAccuracyWithoutDefense) / robustAccuracyWithoutDefense)

    CS01_score = ( -timeTradeOff + \
       naturalAccTradeOff + \
         robustAccImprove)

    result = {
      "denoiser_name": scoreDictionary['nameOfDefender'],
      "score": CS01_score,        # required from users
      "details" : {
        "timeTradeOff": timeTradeOff,
        "naturalAccTradeOff": naturalAccTradeOff,
        "robustAccImprove": robustAccImprove
      }
    }
    if self.showDetails:
      print('\n')
      print(result)

    return result
  