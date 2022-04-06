from Loader import CustomizedMetricScoreClassLoader

"""
This component helps create a dictionary for user-defined metric scores.
"""
class CustomizedScoreDictionaryBuilder():
  def __init__(self, setting):
    self.setting = setting # contains the user defined JSON setting file
    self._checkParams()

  """
  Make sure the state variable 'setting' is not empty
  @param None
  @return None
  """
  def _checkParams(self):
    if self.setting == {}:
      raise Exception("setting is empty")
  
  """
  Build a dictionary for user-defined metric scores given the setting provided in the user-defined
  setting.
  @param None
  @return dictionary a dictionary containing key as the name of the user-defined score
                      and value as callable objectt to calculate that score.
  """
  def buildCustomizedDict(self):
    customizedScoresDict = {}
    for scoreCalculatorParam in self.setting['customized_metric_score']:
      customizedMetricScoreClassLoader = CustomizedMetricScoreClassLoader(
        path = scoreCalculatorParam['path'],
        name = scoreCalculatorParam['name'],
        kwargs = scoreCalculatorParam['scoreCalculatorParam']
      )
      scoreCalculator = customizedMetricScoreClassLoader.loadScore()
      customizedScoresDict[scoreCalculatorParam['name']] = scoreCalculator.getScore
    
    return customizedScoresDict
    