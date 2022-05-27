# Recommender-Tool
Machine Learning Defense Recommender Tool

# Installation
See requirements.txt file for dependencies.

Install all dependencies with:

pip install -r requirements.txt

# Starting
Program is started simply by running the following command in the terminal:

python main2.py

# Using
Click 'Create Data Input File' or 'Create Settings File' to go to the respective page to create each type of file. See 'Creating Data Input File' and 'Create Settings File' below for more details.

Click 'Choose Setting File' to select the setting file you wish to use to generate the recommendations. Then Click 'Generate Recommendations' to recieve your output at the location specified in the setting file selected, as well as the terminal.

<img src="https://user-images.githubusercontent.com/76569535/167215666-3dfc5b72-2254-4553-b627-54b41ef93bb0.png" width="75%" height="75%">

# Creating Data Input File
A Data Input File can be created from scratch using this page. Or, click the 'Load' button and choose a json file (with correct formatting, see example-data-input.json file) that will be used to populate the page's fields accordingly. From there the fields can continue to be modified as needed. Click 'Save' to save the file.

The 'Remove ...', 'X', and 'add ...' buttons can be used to remove and add content.

<img src="https://user-images.githubusercontent.com/76569535/167216370-875a8be5-ec19-4917-b6f2-d882e643e16c.png" width="75%" height="75%">

Note: The 'tab' key can be used to navigate to the next field. Also, certain fields have an autocomplete feature. As you type, a list of matching suggestions will be shown in a dropdown. Select an option by clicking on one or using keys. The options can be quickly navigated by using the arrow keys. Then, use the 'enter' key to select the option or the 'tab' key to select and move to the next field. When using the Save feature, once the file explorer has been opened (by clicking 'Save) you can press the 'enter' key instead of clicking on the 'Save' button in the file explorer to save the file.

# Creating Settings File
Creating a Settings File follows a very similar process to creating a Data Input File. In addition to the features included during the creating of a Data Input File, the settings page has buttons to choose the Input Data File and Output File location via a file explorer. Also, the field next to the 'add custom constraint' button can be used to add custom contraints to the list of constraints offered in the 'constraint' button dropdown.

<img src="https://user-images.githubusercontent.com/76569535/167217226-3405197b-04d8-4980-a7b8-7d113522552a.png" width="75%" height="75%">

Check out the Wiki page for more information!
