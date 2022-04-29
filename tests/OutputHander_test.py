import sys
sys.path.append("..") # Adds higher directory to python modules path.
from OutputHandler import OutputHandler
from Utils import CreateTemp
import json

def test_saveOutputJSON_empty_output():
  import pytest
  with pytest.raises(Exception):
    setting = {}
    output={}
    outputHandler = OutputHandler(
      setting=setting,
      output=output
    )
def test_saveOutputJSON_normal_output():
  import tempfile
  tempFileFp = tempfile.NamedTemporaryFile(dir="..", suffix=".json", mode="w+")
  setting = {"output":{"output_file_path": tempFileFp.name}}
  output = {
    "random_key_01":[
      {
        "random_key_02": "random_value_02"
      },
      {
        "random_key_03": "random_value_03"
      }
    ]
  }
  outputHandler = OutputHandler(
      setting=setting,
      outputFp=tempFileFp
    )
  outputHandler.saveOutput(output=output)
  actualOutput = {}
  tempFileFp.seek(0)
  with open(tempFileFp.name, "r") as fp:
    actualOutput = json.load(fp)
  assert(output == actualOutput)
  tempFileFp.close()
