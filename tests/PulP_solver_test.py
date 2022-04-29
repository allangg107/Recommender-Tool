import sys
sys.path.append("..") # Adds higher directory to python modules path.
from Loader import ConstraintSolverClassLoader

DEFENDER_DICT = {
  "random_defender_name_01": {
        "nameOfDefender": "random_defender_name_01",
        "type": "PREPROCESSOR",
        "defense_params": {},
        "defender_performance": {
            "CS01": 98,
            "CS02": 5,
            "natural_accuracy": 85,
            "natural_precision": 85,
            "natural_recall": 85,
            "natural_f1-score": 85,
            "robust_accuracy": 77,
            "robust_precision": 77,
            "robust_recall": 77,
            "robust_f1-score": 77,
            "inference_elapsed_time_per_1000_in_s": 0.02
        }
  },
  "random_defender_name_02": {
        "nameOfDefender": "random_defender_name_02",
        "type": "PREPROCESSOR",
        "defense_params": {},
        "defender_performance": {
            "CS01": 100,
            "CS02": 8,
            "natural_accuracy": 84,
            "natural_precision": 84,
            "natural_recall": 84,
            "natural_f1-score": 84,
            "robust_accuracy": 76,
            "robust_precision": 76,
            "robust_recall": 76,
            "robust_f1-score": 76,
            "inference_elapsed_time_per_1000_in_s": 0.04
        }
  },
  "random_defender_name_03": {
        "nameOfDefender": "random_defender_name_03",
        "type": "PREPROCESSOR",
        "defense_params": {},
        "defender_performance": {
            "CS01": 97,
            "CS02": 2,
            "natural_accuracy": 89,
            "natural_precision": 89,
            "natural_recall": 89,
            "natural_f1-score": 89,
            "robust_accuracy": 80,
            "robust_precision": 80,
            "robust_recall": 80,
            "robust_f1-score": 80,
            "inference_elapsed_time_per_1000_in_s": 0.4
        }
  },
}

def test_PUlP_solver_maximum_CS01():
  constraintObjectList = [
    {
      "constraint": "LpMaximize",
      "problem_statement": "best_defender_problem"
    },
    {
      "constraint": "max",
      "metric_name": "CS01"
    }
  ]
  trueRecommendations = ["Defenders_random_defender_name_02"]
  recommendations = []
  solverClassLoader = ConstraintSolverClassLoader(path="Solvers.ConstraintHandler", name="PulP",kwargs={
      "defenderNames": list(DEFENDER_DICT.keys()),
      "defenderDict": DEFENDER_DICT,
      "constraintObjectList": constraintObjectList
  })
  constraintSolver = solverClassLoader.loadSolver()
  constraintSolver.buildConstraint()
  statusCode = constraintSolver.solve()
  for v in constraintSolver.getVariables():
    if v.varValue > 0:
      recommendations.append(v.name)
  assert(trueRecommendations == recommendations)

def test_PUlP_solver_maximum_CS01_with_natural_accuracy_conditions():
  constraintObjectList = [
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
    }
  ]
  trueRecommendations = ["Defenders_random_defender_name_01"]
  recommendations = []
  solverClassLoader = ConstraintSolverClassLoader(path="Solvers.ConstraintHandler", name="PulP",kwargs={
      "defenderNames": list(DEFENDER_DICT.keys()),
      "defenderDict": DEFENDER_DICT,
      "constraintObjectList": constraintObjectList
  })
  constraintSolver = solverClassLoader.loadSolver()
  constraintSolver.buildConstraint()
  statusCode = constraintSolver.solve()
  for v in constraintSolver.getVariables():
    if v.varValue > 0:
      recommendations.append(v.name)
  assert(trueRecommendations == recommendations)

def test_PUlP_solver_maximum_CS01_with_natural_accuracy_and_time_conditions():
  constraintObjectList = [
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
      "constraint_value": 0.03,
      "metric_name": "inference_elapsed_time_per_1000_in_s"
    }
  ]
  trueRecommendations = ["Defenders_random_defender_name_01"]
  recommendations = []
  solverClassLoader = ConstraintSolverClassLoader(path="Solvers.ConstraintHandler", name="PulP",kwargs={
      "defenderNames": list(DEFENDER_DICT.keys()),
      "defenderDict": DEFENDER_DICT,
      "constraintObjectList": constraintObjectList
  })
  constraintSolver = solverClassLoader.loadSolver()
  constraintSolver.buildConstraint()
  statusCode = constraintSolver.solve()
  for v in constraintSolver.getVariables():
    if v.varValue > 0:
      recommendations.append(v.name)
  assert(trueRecommendations == recommendations)

def test_PUlP_solver_minimum_CS02():
  constraintObjectList = [
    {
      "constraint": "LpMinimize",
      "problem_statement": "best_defender_problem"
    },
    {
      "constraint": "min",
      "metric_name": "CS02"
    }
  ]
  trueRecommendations = ["Defenders_random_defender_name_03"]
  recommendations = []
  solverClassLoader = ConstraintSolverClassLoader(path="Solvers.ConstraintHandler", name="PulP",kwargs={
      "defenderNames": list(DEFENDER_DICT.keys()),
      "defenderDict": DEFENDER_DICT,
      "constraintObjectList": constraintObjectList
  })
  constraintSolver = solverClassLoader.loadSolver()
  constraintSolver.buildConstraint()
  statusCode = constraintSolver.solve()
  for v in constraintSolver.getVariables():
    if v.varValue > 0:
      recommendations.append(v.name)
  assert(trueRecommendations == recommendations)

def test_PUlP_solver_minimum_CS02_and_CS01_inequality():
  constraintObjectList = [
    {
      "constraint": "LpMinimize",
      "problem_statement": "best_defender_problem"
    },
    {
      "constraint": "min",
      "metric_name": "CS02"
    },
    {
      "constraint": ">=",
      "constraint_value": 97.5,
      "metric_name": "CS01"
    },
  ]
  trueRecommendations = ["Defenders_random_defender_name_01"]
  recommendations = []
  solverClassLoader = ConstraintSolverClassLoader(path="Solvers.ConstraintHandler", name="PulP",kwargs={
      "defenderNames": list(DEFENDER_DICT.keys()),
      "defenderDict": DEFENDER_DICT,
      "constraintObjectList": constraintObjectList
  })
  constraintSolver = solverClassLoader.loadSolver()
  constraintSolver.buildConstraint()
  statusCode = constraintSolver.solve()
  for v in constraintSolver.getVariables():
    if v.varValue > 0:
      recommendations.append(v.name)
  assert(trueRecommendations == recommendations)

def test_PUlP_solver_minimum_CS02_and_CS01_inequality_no_constraint_value():
  import pytest
  with pytest.raises(Exception):
    constraintObjectList = [
      {
        "constraint": "LpMinimize",
        "problem_statement": "best_defender_problem"
      },
      {
        "constraint": "min",
        "metric_name": "CS02"
      },
      {
        "constraint": "max",
        "metric_name": "CS01"
      },
    ]
    trueRecommendations = ["Defenders_random_defender_name_01"]
    recommendations = []
    solverClassLoader = ConstraintSolverClassLoader(path="Solvers.ConstraintHandler", name="PulP",kwargs={
        "defenderNames": list(DEFENDER_DICT.keys()),
        "defenderDict": DEFENDER_DICT,
        "constraintObjectList": constraintObjectList
    })
    constraintSolver = solverClassLoader.loadSolver()
    constraintSolver.buildConstraint()
    statusCode = constraintSolver.solve()

def test_PUlP_solver_no_min_max():
  import pytest
  with pytest.raises(Exception):
    constraintObjectList = [
      {
        "constraint": "LpMinimize",
        "problem_statement": "best_defender_problem"
      },
      {
        "constraint": ">=",
        "constraint_value":2,
        "metric_name": "CS02"
      }
    ]
    trueRecommendations = ["Defenders_random_defender_name_01"]
    recommendations = []
    solverClassLoader = ConstraintSolverClassLoader(path="Solvers.ConstraintHandler", name="PulP",kwargs={
        "defenderNames": list(DEFENDER_DICT.keys()),
        "defenderDict": DEFENDER_DICT,
        "constraintObjectList": constraintObjectList
    })
    constraintSolver = solverClassLoader.loadSolver()
    totalScore = constraintSolver.buildConstraint()
    statusCode = totalScore.solve()

def test_PUlP_solver_empty_constraintObjectList():
  import pytest
  with pytest.raises(Exception):
    constraintObjectList = []
    trueRecommendations = ["Defenders_random_defender_name_01"]
    recommendations = []
    solverClassLoader = ConstraintSolverClassLoader(path="Solvers.ConstraintHandler", name="PulP",kwargs={
        "defenderNames": list(DEFENDER_DICT.keys()),
        "defenderDict": DEFENDER_DICT,
        "constraintObjectList": constraintObjectList
    })
    constraintSolver = solverClassLoader.loadSolver()
    totalScore = constraintSolver.buildConstraint()
    statusCode = totalScore.solve()
  