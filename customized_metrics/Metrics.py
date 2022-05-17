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
    naturalF1ScoreTradeOff = self.beta * ((naturalF1ScoreWithDefense - naturalF1ScoreWithoutDefense) / naturalF1ScoreWithoutDefense)
    robustF1ScoreImprove = self.gamma * ((robustF1ScoreWithDefense - robustF1ScoreWithoutDefense) / robustF1ScoreWithoutDefense)

    CS01_score = ( -timeTradeOff + \
       naturalF1ScoreTradeOff + \
         robustF1ScoreImprove)

    result = {
      "denoiser_name": scoreDictionary['nameOfDefender'],
      "score": CS01_score,        # required from users
      "details" : {
        "weighted_inference_time_tradeOff": timeTradeOff,
        "weighted_natural_F1_score_tradeOff": naturalF1ScoreTradeOff,
        "weighted_robust_F1_score_improvement": robustF1ScoreImprove
      }
    }
    if self.showDetails:
      print('\n')
      print(result)

    return result
  