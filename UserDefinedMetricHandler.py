from Loader import CustomizedMetricScoreClassLoader
class CustomizedScoreDictionaryBuilder():
  def __init__(self, setting):
    self.setting = setting
    self._checkParams()

  def _checkParams(self):
    if self.setting == {}:
      raise Exception("setting is empty")
    
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
    