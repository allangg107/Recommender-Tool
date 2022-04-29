RANDOM_STRING = "def foo(): \nreturn None"
RANDOM_DICT = {"random_key_1": {"random_key_2": "random_value_2"}}

def test_Utils_createTemp_with_string():
  import sys
  sys.path.append("..") # Adds higher directory to python modules path.
  from Utils import CreateTemp
  createTemp = CreateTemp(tempPath=".", suffix = ".py")
  createTemp.createTempFile(contentToWrite=RANDOM_STRING)
  assert(createTemp.tempFileContent == RANDOM_STRING)
  assert(createTemp.tempFileName[-3:] == ".py")
  createTemp.closeTempFile()

def test_Utils_createTemp_with_json():
  import sys
  sys.path.append("..") # Adds higher directory to python modules path.
  from Utils import CreateTemp
  createTemp = CreateTemp(tempPath=".", suffix = ".json")
  createTemp.createTempFile(contentToWrite=RANDOM_DICT)
  assert(createTemp.tempFileContent == RANDOM_DICT)
  assert(createTemp.tempFileName[-5:] == ".json")
  createTemp.closeTempFile()