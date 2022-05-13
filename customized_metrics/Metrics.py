# Customized score 01
from Interfaces import CustomizedMetricScoreInterface
class CS01(CustomizedMetricScoreInterface):
  def __init__(self, kwargs):
    CustomizedMetricScoreInterface.__init__(self, kwargs=kwargs)
    self.alpha = self.kwargs['alpha']  # time tradeoff coefficient
    self.beta = self.kwargs['beta']    # natural tradeoff coefficient
    self.gamma = self.kwargs['gamma']  # robust coefficient
    self.showDetails = self.kwargs['showDetails']

  """
  This public method returns the score of the given user-defined metric
  @param scoreDictionary data passed from the user's input data
  @return a dictionary containing the score
  """
  def getScore(self, scoreDictionary):
    initialTime = scoreDictionary['baseline_performance']['inference_elapsed_time_per_1000_in_s']
    addedTime = scoreDictionary['defender_performance']['inference_elapsed_time_per_1000_in_s']

    naturalF1ScoreWithoutDefense = scoreDictionary['baseline_performance']['natural_f1-score']
    robustF1ScoreWithoutDefense = scoreDictionary['attacker_performance']['robust_f1-score']

    naturalF1ScoreWithDefense = scoreDictionary['defender_performance']['natural_f1-score']
    robustF1ScoreWithDefense = scoreDictionary['defender_performance']['robust_f1-score']

    timeTradeOff = self.alpha * ((addedTime) / initialTime)
    naturalAccTradeOff = self.beta * ((naturalF1ScoreWithDefense - naturalF1ScoreWithoutDefense) / naturalF1ScoreWithoutDefense)
    robustAccImprove = self.gamma * ((robustF1ScoreWithDefense - robustF1ScoreWithoutDefense) / robustF1ScoreWithoutDefense)

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
  