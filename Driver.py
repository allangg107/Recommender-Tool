from DataHandler import InputDataHandler
from Constants import DEFAULT_OUTPUT_LOCATION
import json

class Driver:
  def __init__(self, settingPath = None):
    self.settingPath = settingPath
  
  def drive(self):
    setting = {}
    outputPath = DEFAULT_OUTPUT_LOCATION
    with open(self.settingPath, 'r') as fp:
        setting = json.load(fp)
    # TODO:dynamically import formula
    scoreCalculatorParam = setting['scoreCalculatorParam']
    from customized_metrics.Metrics import CS01
    scoreCalculator = CS01(
      showDetails = scoreCalculatorParam['showDetails'],
      alpha= scoreCalculatorParam['alpha'], 
      beta=scoreCalculatorParam['beta'],   
      gamma=scoreCalculatorParam['gamma']   
    )

    # handle data
    recommendation_result = InputDataHandler(
      kwargs = setting,
      scoreCalculatorFunc = scoreCalculator.getScore
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
    