import tempfile

"""
This component is responsible for creating and deleting temporary files, which are mainly
used in testing.
"""
class CreateTemp:
  def __init__(self, tempPath = None, suffix = None):
    self.tempFileName = None
    self.tempFileNameSuffix = suffix
    self.tempFileFp = None
    self.tempPath = tempPath
    self.tempFileContent = None

  """
  This function creates state temporary file
  @param contentToWrite user content, which can be string or dictionary, 
          would be written into the state temp. file
  @return None
  """
  def createTempFile(self, contentToWrite):
    if contentToWrite is None:
      raise Exception("contentToWrite is None")
    
    if isinstance(contentToWrite, str):
      self.tempFileFp = tempfile.NamedTemporaryFile(dir=self.tempPath, suffix=self.tempFileNameSuffix)
      b = bytes(contentToWrite, 'utf-8')
      (self.tempFileFp).write(b)
      (self.tempFileFp).seek(0)
      self.tempFileContent = ((self.tempFileFp).read()).decode("utf-8")

    elif isinstance(contentToWrite, dict):
      self.tempFileFp = tempfile.NamedTemporaryFile(dir=self.tempPath, suffix=self.tempFileNameSuffix, mode="w+")
      import json
      json.dump(contentToWrite, self.tempFileFp)
      (self.tempFileFp).seek(0)
      self.tempFileContent = json.load(self.tempFileFp)
    
    self.tempFileName = (self.tempFileFp).name
    return None
  
  """
  This function cleans up its state temporary file
  @param None
  @return None
  """
  def closeTempFile(self):
    if self.tempFileFp is not None:
      (self.tempFileFp).close()