import json
from Constants import DEFAULT_OUTPUT_LOCATION
class OutputHandler:
  def __init__(self, setting = {}, outputFp = None):
    self.outputFp = outputFp
    self.outputPath = (setting['output']['output_file_path'] if ('output' in setting and 'output_file_path' in setting['output']) else DEFAULT_OUTPUT_LOCATION)

  def saveOutput(self, output):
    self._checkOutput(output = output)
    if self.outputPath.lower() == "terminal":
      self._saveOutputToTerminal(output = output)
    else:
      self._saveOutputToJSON(output = output)

  def _checkOutput(self, output):
    if not isinstance(output, dict):
      raise Exception("Output must be a dictionary")
    if output == {}:
      raise Exception("Output must not be an empty dictionary")

  def _saveOutputToTerminal(self, output):
    if isinstance(output, dict):
      print(json.dumps(output, indent=4))
    else:
      raise Exception("output must be a dictionary")
  
  def _saveOutputToJSON(self, output):
    if not isinstance(output, dict):
      raise Exception("output must be a dictionary for JSON")
    if self.outputFp is not None:
      json.dump(output, self.outputFp, indent=4)
    else:
      with open(self.outputPath, 'w') as fp:
        json.dump(output, fp, indent=4)