import sys
sys.path.append("..") # Adds higher directory to python modules path.
from customized_metrics.Metrics import CS01

ALPHA = 1
BETA = 1
GAMMA = 1

BASELINE_TIME = 10
BASELINE_NATURAL_F1 = 100
BASELINE_ROBUST_F1 = 20

ADDED_TIME = 1
DENOISED_NATURAL_F1 = 80
DENOISED_ROBUST_F1 = 40

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
      "natural_f1-score": BASELINE_NATURAL_F1
    },
    "attacker_performance": {
      "robust_f1-score": BASELINE_ROBUST_F1
    },
    "defender_performance":{
      "inference_elapsed_time_per_1000_in_s": ADDED_TIME,
      "natural_f1-score": DENOISED_NATURAL_F1,
      "robust_f1-score": DENOISED_ROBUST_F1
    }
  }
  predictedResult = 0
  predictedResult -= ALPHA * ((ADDED_TIME)/BASELINE_TIME) 
  predictedResult -= BETA * ((BASELINE_NATURAL_F1 - DENOISED_NATURAL_F1) / BASELINE_NATURAL_F1) 
  predictedResult += GAMMA * ((DENOISED_ROBUST_F1 - BASELINE_ROBUST_F1) / BASELINE_ROBUST_F1)
  actualResult = cs01.getScore(scoreDictionary=scoreDictionary)
  assert(predictedResult == actualResult['score'])
  