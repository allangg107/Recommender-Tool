import sys
sys.path.append("..") # Adds higher directory to python modules path.
from customized_metrics.Metrics import CS01

ALPHA = 1
BETA = 1
GAMMA = 1

BASELINE_TIME = 10
BASELINE_NATURAL_ACCURACY = 100
BASELINE_ROBUST_ACCURACY = 20

ADDED_TIME = 1
DENOISED_NATURAL_ACCURACY = 80
DENOISED_ROBUST_ACCURACY = 40

def test_CS01():
  cs01 = CS01(kwargs={
    "alpha": ALPHA,
    "beta": BETA,
    "gamma": GAMMA,
    "showDetails": False
  })
  scoreDictionary = {
    "nameOfDefender": "CS01",
    "baseline_performance":{
      "inference_elapsed_time_per_1000_in_s": BASELINE_TIME,
      "natural_accuracy": BASELINE_NATURAL_ACCURACY
    },
    "attacker_performance": {
      "robust_accuracy": BASELINE_ROBUST_ACCURACY
    },
    "defender_performance":{
      "inference_elapsed_time_per_1000_in_s": ADDED_TIME,
      "natural_accuracy": DENOISED_NATURAL_ACCURACY,
      "robust_accuracy": DENOISED_ROBUST_ACCURACY
    }
  }
  predictedResult = 0
  predictedResult -= ALPHA * ((ADDED_TIME)/BASELINE_TIME) 
  predictedResult -= BETA * ((BASELINE_NATURAL_ACCURACY - DENOISED_NATURAL_ACCURACY) / BASELINE_NATURAL_ACCURACY) 
  predictedResult += GAMMA * ((DENOISED_ROBUST_ACCURACY - BASELINE_ROBUST_ACCURACY) / BASELINE_ROBUST_ACCURACY)
  actualResult = cs01.getScore(scoreDictionary=scoreDictionary)
  assert(predictedResult == actualResult['score'])
  