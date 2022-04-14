import json
from Constants import BASELINE_PERFORMANCE, ATTACKER_PERFORMANCE, DEFENDER_PERFORMANCE, DEFENDERS
"""
This component extracts list of keyword names of a performance object. This helps autofill feature.
Assumption: at least 1 data instance exists and every data instance is consistent in naming key
"""
class JSONKeysExtractor:
  def __init__(self, jsonFilePath = ''):
    self.jsonFilePath = jsonFilePath
    self._checkParams()
  
  """
  This public method extract keywords from a JSON file path
  """
  def provideKeyList(self):
    inputData = None
    result = {
      BASELINE_PERFORMANCE: [],
      ATTACKER_PERFORMANCE: [],
      DEFENDER_PERFORMANCE: []
    }
    with open(self.jsonFilePath, 'r') as fp:
        inputData = json.load(fp)
    if inputData == {}:
      raise Exception("Empty JSON file")
    # extract list of names for base performance
    data = inputData['data']
    if list(data.keys()) == []:
      raise Exception("empty first dataset object")
    firstDatasetName = list(data.keys())[0]
    firstDatasetObject = data[firstDatasetName]
    firstModelName = list(firstDatasetObject.keys())[0]
    firstModelNameObject = firstDatasetObject[firstModelName]
    result[BASELINE_PERFORMANCE] = list(firstModelNameObject[BASELINE_PERFORMANCE].keys())

    # extract list of names for attacker performance
    firstThreatModelName = list(firstModelNameObject.keys())[1]
    firstThreatModelObject = firstModelNameObject[firstThreatModelName]
    firstAttackerName = list(firstThreatModelObject.keys())[0]
    firstAttackerObject = firstThreatModelObject[firstAttackerName]
    result[ATTACKER_PERFORMANCE] = list(firstAttackerObject[ATTACKER_PERFORMANCE].keys())
    
    # extract list of names for defender performance
    firstDefenderObject = firstAttackerObject[DEFENDERS][0]
    result[DEFENDER_PERFORMANCE] = list(firstDefenderObject[DEFENDER_PERFORMANCE].keys())

    return result

  def _checkParams(self):
    if self.jsonFilePath == '':
      raise Exception("jsonFilePath is None")
