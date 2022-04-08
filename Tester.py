from DataHandler import InputDataHandler
from Constants import DUMMY_INPUT_DATA_PATH
from customized_metrics.Metrics import CS01

class Tester:
  def testInputDataHandler(self):
    InputDataHandler().parse(jsonFilePath = DUMMY_INPUT_DATA_PATH)
  
  def testMetricsWithGivenScoreDictionary(self):
    scoreDictionary = {
      "baseline_performance": {
          "natural_accuracy": 77.75999999999999,
          "natural_precision": 80.88139004299308,
          "natural_recall": 77.76,
          "natural_f1-score": 78.33059710177753,
          "inference_elapsed_time_per_1000_in_s": 3.7206225000000024
      },
      "attacker_performance": {
          "robust_accuracy": 0.42,
          "robust_precision": 0.5333894747426183,
          "robust_recall": 0.42000000000000004,
          "robust_f1-score": 0.4570025939478894
      },
      "defender_performance": {
          "natural_accuracy": 72.45,
          "natural_precision": 75.49932450773812,
          "natural_recall": 72.45,
          "natural_f1-score": 72.7494936449291,
          "robust_accuracy": 63.349999999999994,
          "robust_precision": 67.38588176211026,
          "robust_recall": 63.349999999999994,
          "robust_f1-score": 63.74694815321189,
          "inference_elapsed_time_per_1000_in_s": 0.024218399999999963
      }
    }
    cs01ScoreCalculator = CS01(
      showDetails=True,
      alpha= 1,
      beta=3,
      gamma=1
    )
    firstScore = cs01ScoreCalculator.getScore(
      scoreDictionary=scoreDictionary
    )
    print(firstScore)

Tester().testInputDataHandler()
    