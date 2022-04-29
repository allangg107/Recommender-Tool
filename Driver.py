from DataHandler import InputDataHandler
from Constants import DEFAULT_OUTPUT_LOCATION
from Loader import CustomizedMetricScoreClassLoader
from OutputHandler import OutputHandler
from UserDefinedMetricHandler import CustomizedScoreDictionaryBuilder
import json

class Driver:
  def __init__(self, settingPath = None):
    self.settingPath = settingPath
  
  def drive(self):
    setting = {}
    # loading the user setting JSON file
    with open(self.settingPath, 'r') as fp:
        setting = json.load(fp)
    
    # load customized metric score calculators
    customizedScoreDictBuilder = CustomizedScoreDictionaryBuilder(setting=setting)
    customizedScoresDict = customizedScoreDictBuilder.buildCustomizedDict()

    # handle/process data
    recommendation_result = InputDataHandler(
      settingKwargs = setting,
      scoreCalculatorFuncDict = customizedScoresDict
    ).handle(jsonFilePath = setting['input_data_path'])

    # output
    outputHandler = OutputHandler(
      setting=setting
    )
    outputHandler.saveOutput(output={
        "setting": setting,
        "recommendation_result": recommendation_result
      })
    