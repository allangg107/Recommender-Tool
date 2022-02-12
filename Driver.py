from DataHandler import InputDataHandler
from Constants import DEFAULT_OUTPUT_LOCATION
from Loader import CustomizedMetricScoreClassLoader
import json

class Driver:
  def __init__(self, settingPath = None):
    self.settingPath = settingPath
  
  def drive(self):
    setting = {}
    outputPath = DEFAULT_OUTPUT_LOCATION
    with open(self.settingPath, 'r') as fp:
        setting = json.load(fp)
    
    # load customized metric score calculators
    customizedScoresDict = {}
    for scoreCalculatorParam in setting['customized_metric_score']:
      customizedMetricScoreClassLoader = CustomizedMetricScoreClassLoader(
        path = scoreCalculatorParam['path'],
        name = scoreCalculatorParam['name'],
        kwargs = scoreCalculatorParam['scoreCalculatorParam']
      )
      scoreCalculator = customizedMetricScoreClassLoader.loadScore()
      customizedScoresDict[scoreCalculatorParam['name']] = scoreCalculator.getScore

    # handle data
    recommendation_result = InputDataHandler(
      kwargs = setting,
      scoreCalculatorFuncDict = customizedScoresDict
    ).handle(jsonFilePath = setting['input_data_path'])

    # output
    outputDict = {
      "setting": setting,
      "recommendation_result": recommendation_result
    }
    if 'output' in setting and 'outputFilePath' in setting['output']:
      outputPath = setting['output']['outputFilePath']
    
    if outputPath.lower() == "terminal":
      print(json.dumps(outputDict, indent=4))
    else:
      with open(outputPath, 'w') as fp:
        json.dump(outputDict, fp, indent=4)
    