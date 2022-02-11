# Customized score 01
class CS01:
  def __init__(self, alpha = 1, beta = 1, gamma = 1, attackerName = "PGD", showDetails = False):
    self.attackerName = attackerName
    self.alpha = alpha  # time tradeoff coefficient
    self.beta = beta    # natural accuracy tradeoff coefficient
    self.gamma = gamma  # robust accuracy coefficient
    self.showDetails = showDetails

  def getScore(self, scoreDictionary):
    initialTime = scoreDictionary['baseline_performance']['inference_elapsed_time_per_1000_in_s']
    totalTime = scoreDictionary['defender_performance']['inference_elapsed_time_per_1000_in_s'] + initialTime

    naturalAccuracyWithoutDefense = scoreDictionary['baseline_performance']['natural_accuracy']
    robustAccuracyWithoutDefense = scoreDictionary['attacker_performance']['robust_accuracy']

    naturalAccuracyWithDefense = scoreDictionary['defender_performance']['natural_accuracy']
    robustAccuracyWithDefense = scoreDictionary['defender_performance']['robust_accuracy']

    timeTradeOff = self.alpha * ((initialTime - totalTime) / initialTime)
    naturalAccTradeOff = self.beta * ((naturalAccuracyWithDefense - naturalAccuracyWithoutDefense) / naturalAccuracyWithoutDefense)
    robustAccImprove = self.gamma * ((robustAccuracyWithDefense - robustAccuracyWithoutDefense) / robustAccuracyWithoutDefense)

    CS01_score = ( timeTradeOff + \
       naturalAccTradeOff + \
         robustAccImprove)

    result = {
      "denoiser_name": scoreDictionary['nameOfDefender'],
      "score_name": "CS01_score", # required from users
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
  