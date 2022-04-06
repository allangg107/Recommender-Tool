import json
from Constants import DEFAULT_OUTPUT_LOCATION
"""
This component handles where a given output would be saved.
"""
class OutputHandler:
  def __init__(self, setting = {}, outputFp = None):
    self.outputFp = outputFp # this file pointer is mostly used for testing
    self.outputPath = (setting['output']['output_file_path'] if ('output' in setting and 'output_file_path' in setting['output']) else DEFAULT_OUTPUT_LOCATION)

  """
  This public method saves the value of the paramter 'output' to
  the designated location stored in state variable 'outputPath'.
  @param output output to be saved
  @return None
  """
  def saveOutput(self, output):
    self._checkOutput(output = output)
    if self.outputPath.lower() == "terminal":
      self._saveOutputToTerminal(output = output)
    else:
      self._saveOutputToJSON(output = output)
  
  """
  This private method checks whether the given output is an
  empty dictionary or non-dictionary data type.
  @param output output to be saved
  @return None
  """
  def _checkOutput(self, output):
    if not isinstance(output, dict):
      raise Exception("Output must be a dictionary")
    if output == {}:
      raise Exception("Output must not be an empty dictionary")

  """
  This private method saves given output to the terminal
  @param output output to be saved
  @return None
  """
  def _saveOutputToTerminal(self, output):
    if isinstance(output, dict):
      print(json.dumps(output, indent=4))
    else:
      raise Exception("output must be a dictionary")
  
  """
  This private method saves the given output to a designated JSON file,
  which can be found in either the state variable 'outputFp' or 'outputPath'.
  @param output output to be saved
  @return None
  """
  def _saveOutputToJSON(self, output):
    if not isinstance(output, dict):
      raise Exception("output must be a dictionary for JSON")
    if self.outputFp is not None:
      json.dump(output, self.outputFp, indent=4)
    else:
      with open(self.outputPath, 'w') as fp:
        json.dump(output, fp, indent=4)