import json
import os

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from Driver import Driver

_ML_Model_Data_JSON_File_Path = ''
_ML_Model_Data_JSON = {}
_Settings_JSON_File_Path = ''
_Settings_JSON = {}

_Chosen_Setting_File_Path = ''

_Constraint_Options = ['min', 'max', '>', '>=', '==', '<=', '<']

_Missing_Field = False

TEST_SUGGESTIONS = [
    'aaa', 'aab', 'aac', 'aad', 'aae',
    'aba', 'abb', 'abc', 'abd', 'abe',
    'aca', 'acb', 'acc', 'acd', 'ace',
]

# FUTURE WORK: suggestion lists should be dynamically created with all appropriate suggestions

MODEL_PERFORMANCE_SUGGESTIONS = ['natural_accuracy', 'natural_precision', 'natural_recall', 'natural_f1-score',
                                 'inference_elapsed_time_per_1000_in_s']

ATTACKER_PERFORMANCE_SUGGESTIONS = ['robust_accuracy', 'robust_precision', 'robust_recall', 'robust_f1-score']

DEFENDER_PERFORMANCE_SUGGESTIONS = ['natural_accuracy', 'natural_precision', 'natural_recall', 'natural_f1-score',
                                    'robust_accuracy', 'robust_precision', 'robust_recall', 'robust_f1-score',
                                    'inference_elapsed_time_per_1000_in_s']

CONSTRAINT_SUGGESTIONS = DEFENDER_PERFORMANCE_SUGGESTIONS


# return the string cast to a float if possible
# otherwise, returns the string as-is
def cast_if_float(s):
    try:
        return float(s)
    except ValueError:
        return s


# return the user's value in the value_input field
# returns as a float if a float, string if a string, or bool if a bool
def get_value_input(parameter):
    value_input = parameter.ids.value_input.text
    if value_input != 'true' and value_input != 'True' and value_input != 'false' and value_input != 'False':
        return cast_if_float(value_input)
    elif value_input == 'true' or value_input == 'True':
        return True
    elif value_input == 'false' or value_input == 'False':
        return False


# returns a dictionary of all the parameters found in the parameter_container
def save_parameter_fields(parameter_container):
    params_dictionary = {}
    for parameter in parameter_container.children:
        # if the parameter is empty then it is not stored
        if len(parameter.ids.key_input.text) != 0:
            params_dictionary[parameter.ids.key_input.text] = get_value_input(parameter)

    return params_dictionary


# matches the number of fields in the UI to the number given in the dictionary
def trim_field_number(number_of_keys, container, add_child):
    while number_of_keys > len(container.children):
        add_child()

    while number_of_keys < len(container.children):
        container.remove_widget(container.children[0])


# populates the given parameter_container using the given dictionary
def fill_parameter_fields(parameter_container, loaded_dictionary):
    parameter_keys = list(loaded_dictionary.keys())
    parameter_values = list(loaded_dictionary.values())

    # matches the number of parameter fields in the UI to the number given in the dictionary
    trim_field_number(len(parameter_keys), parameter_container, parameter_container.add_parameter)

    index = 0
    # parameter information is added to the appropriate fields in the UI
    for key in parameter_keys:
        parameter_container.children[index].ids.key_input.text = key
        parameter_container.children[index].ids.value_input.text = str(parameter_values[index])
        parameter_container.children[index].ids.key_input.dropdown.dismiss()
        parameter_container.children[index].ids.value_input.dropdown.dismiss()
        index += 1


# checks if the given name basename is valid
# returns true if it is valid, or the message indicating what is wrong with the save name
def valid_save_name(filename):
    if len(filename) == 0:
        return True
    elif filename.count('.') > 1:
        return "Cannot have multiple '.'"
    elif filename.count('.') == 1:
        if filename.endswith(".json"):
            return True
        else:
            return "Save name must end with '.json'"
    elif filename.count('.') == 0:
        return True


# open the file explorer for loading
def show_load_explorer(widget):
    content = LoadDialog(load=widget.load, cancel=widget.dismiss_popup)
    widget._popup = Popup(title="Load file", content=content,
                          size_hint=(0.9, 0.9))

    widget._popup.open()


# opens the file explorer for saving
def show_save_explorer(widget, hint_text):
    content = SaveDialog(save=widget.save, cancel=widget.dismiss_popup)
    widget._popup = Popup(title="Save file", content=content,
                          size_hint=(0.9, 0.9))

    widget._popup.content.ids.text_input.hint_text = hint_text
    widget._popup.open()
    widget._popup.content.ids.text_input.focus = True


class WindowManager(ScreenManager):
    pass


# FUTURE WORK: create a settings page for the UI where the user can customize the UI, including
# changing the color of the UI (light mode, dark mode, etc.), font color, font size, default values,
# starting number of parameters, starting number of constraints, etc.
class MainWindow(Screen):
    _popup = None

    # generates the output file based on which setting file was chosen
    def generate_button(self):
        global _Chosen_Setting_File_Path
        if len(_Chosen_Setting_File_Path) != 0:
            driver = Driver(settingPath=_Chosen_Setting_File_Path)
            driver.drive()

            self.parent.ids.recommendations_window.extract_recommendations(_Chosen_Setting_File_Path)

        else:  # if no file was chosen, user is prompted to choose a file
            button = self.ids.main_menu_buttons_container.ids.choose_settings
            button.text = button.base_text + "REQUIRED TO CHOOSE FILE"

    def get_missing_field_status(self):
        global _Missing_Field
        return _Missing_Field

    def chose_setting_path(self):
        global _Chosen_Setting_File_Path
        if len(_Chosen_Setting_File_Path) != 0:
            return True
        else:
            return False

    # dismiss the file explorer
    def dismiss_popup(self):
        self._popup.dismiss()

    # open the file explorer for loading
    def show_load(self):
        show_load_explorer(self)

    # given the user's selected file, displays the selected file's name
    # and sets it as the chosen file
    def load(self, path, filename):
        if filename:
            button = self.ids.main_menu_buttons_container.ids.choose_settings
            button.text = button.base_text + os.path.basename(filename[0])

            global _Chosen_Setting_File_Path
            _Chosen_Setting_File_Path = os.path.join(path, filename[0])

            self.dismiss_popup()


class DataWindow(Screen):
    _popup = None

    # creates a dictionary using all the user's input
    # warns the user if there is missing input
    # the original to_dictionary() call is made here, which calls its children's to_dictionary()
    # and so on in order to save all fields to dictionary
    def generate_ml_model_data_json(self):
        global _Missing_Field
        _Missing_Field = False
        global _ML_Model_Data_JSON
        # all model data fields ultimately get stored in this dictionary
        # the context is currently made manually
        _ML_Model_Data_JSON = {"context": {"GPU": "dummyGPU", "image_size": [224, 224, 3]},
                               "data": self.ids.data_fields_scrollview.ids.all_datasets_container.ids.datasets_container.to_dictionary()}

        if self.get_missing_field_status() == False:
            self.show_save()
        else:
            return

    def get_missing_field_status(self):
        global _Missing_Field
        return _Missing_Field

    # closes the file explorer
    def dismiss_popup(self):
        self._popup.dismiss()

    # opens the file explorer for loading
    def show_load(self):
        show_load_explorer(self)

    # populates the fields in the UI based on the given file
    # the original fill_fields() call is made here, which calls its children's fill_fields()
    # and so on in order to fill all the fields based on the given JSON file
    # FUTURE WORK: the information in the file should be verified to some level. currently,
    # there is no error handling and works assuming that the user is using intended formatting
    def load(self, path, filename):
        f = open(os.path.join(path, filename[0]))
        loaded_dictionary = json.load(f)
        f.close()

        self.ids.data_fields_scrollview.ids.all_datasets_container.ids.datasets_container.fill_fields(
            loaded_dictionary["data"])

        self.dismiss_popup()

    # opens the file explorer for saving
    def show_save(self):
        show_save_explorer(self, 'ml_model_data_default_save.json')

    # saves the dictionary that was created to JSON at the location given
    def save(self, path, filename):
        global _ML_Model_Data_JSON_File_Path
        if valid_save_name(filename) == True:
            if filename.count('.') == 0:
                filename += ".json"
            _ML_Model_Data_JSON_File_Path = os.path.join(path, filename)

            if filename == ".json":
                _ML_Model_Data_JSON_File_Path = 'ml_model_data_default_save.json'

            with open(_ML_Model_Data_JSON_File_Path, 'w') as f:
                json.dump(_ML_Model_Data_JSON, f, indent=2)

            self.dismiss_popup()

        else:  # prints the error message to the user if the save name was not valid
            self._popup.content.ids.label.text = valid_save_name(filename)


# contains a 'DatasetsContainer'
class AllDatasetsContainer(BoxLayout):
    pass


# contains a list of 'DatasetContainer's ( <- Dataset is not plural)
class DatasetsContainer(BoxLayout):
    def add_dataset(self):
        dc = DatasetContainer()
        self.add_widget(dc)

    # the first to_dictionary() to be called, which calls its children to_dictionary() and so on
    # the fields that the class has the closest access to are stored in the dictionary
    # if there is a missing field, the user is warned about that field
    def to_dictionary(self):
        global _Missing_Field
        datasets_dictionary = {}

        for dataset in self.children:
            dataset_dictionary = dataset.ids.all_data_models_container.ids.data_models_container.to_dictionary()
            if len(dataset.ids.dataset_name_input.text) != 0:
                datasets_dictionary[dataset.ids.dataset_name_input.text] = dataset_dictionary
            else:
                dataset.ids.dataset_name_input.hint_text = "REQUIRED FIELD"
                _Missing_Field = True

        return datasets_dictionary

    # the first fill_fields() to be called, which calls its children fill_fields() and so on
    # the fields that the class has the closest access to are fill based on the given dictionary
    def fill_fields(self, loaded_dictionary):
        dataset_keys = list(loaded_dictionary.keys())

        # matches the number of datasets in the UI to the number given in the dictionary
        trim_field_number(len(dataset_keys), self, self.add_dataset)

        index = 0
        # dataset information is added to the appropriate fields in the UI
        for key in dataset_keys:
            self.children[index].ids.dataset_name_input.text = key
            self.children[index].ids.all_data_models_container.ids.data_models_container.fill_fields(
                loaded_dictionary[key])
            index += 1


# contains Dataset information and an 'AllDataModelsContainer'
class DatasetContainer(BoxLayout):
    pass


# contains a 'DataModelsContainer'
class AllDataModelsContainer(BoxLayout):
    pass


# contains a list of 'ModelContainer's ( <- Model is not plural)
class DataModelsContainer(BoxLayout):
    def add_model(self):
        mc = ModelContainer()
        self.add_widget(mc)

    def to_dictionary(self):
        global _Missing_Field
        models_dictionary = {}

        for model in self.children:
            model_dictionary = model.to_dictionary()
            if len(model.ids.model_fields.ids.model_classifier_input.text) != 0:
                models_dictionary[model.ids.model_fields.ids.model_classifier_input.text] = model_dictionary
            else:
                model.ids.model_fields.ids.model_classifier_input.hint_text = "REQUIRED FIELD"
                _Missing_Field = True

        return models_dictionary

    def fill_fields(self, loaded_dictionary):
        model_keys = list(loaded_dictionary.keys())
        trim_field_number(len(model_keys), self, self.add_model)

        index = 0
        for key in model_keys:
            self.children[index].ids.model_fields.ids.model_classifier_input.text = key
            self.children[index].fill_fields(loaded_dictionary[key])
            index += 1


# contains 'ModelFields', 'ModelPerformance' and a 'ThreatModelsContainer'
class ModelContainer(BoxLayout):
    def to_dictionary(self):
        global _Missing_Field
        model_dictionary = {"baseline_performance": self.ids.model_performance.to_dictionary()}

        for threat_model in self.ids.threat_models_container.children:
            if len(threat_model.ids.threat_model_name_input.text) != 0:
                model_dictionary[
                    threat_model.ids.threat_model_name_input.text] = threat_model.ids.attackers_container.to_dictionary()
            else:
                model_dictionary[
                    threat_model.ids.threat_model_name_input.text] = threat_model.ids.attackers_container.to_dictionary()
                threat_model.ids.threat_model_name_input.hint_text = "REQUIRED FIELD"
                _Missing_Field = True

        return model_dictionary

    def fill_fields(self, loaded_dictionary):
        self.ids.model_performance.fill_fields(loaded_dictionary["baseline_performance"])

        threat_model_keys = list(loaded_dictionary.keys())
        threat_model_keys.remove("baseline_performance")
        trim_field_number(len(threat_model_keys), self.ids.threat_models_container, self.ids.threat_models_container.add_threat_model)

        index = 0
        for key in threat_model_keys:
            self.ids.threat_models_container.children[index].ids.threat_model_name_input.text = key
            self.ids.threat_models_container.children[index].ids.attackers_container.fill_fields(loaded_dictionary[key])
            index += 1


# contains Model performance information
class ModelPerformance(BoxLayout):
    def __init__(self, **kwargs):
        super(ModelPerformance, self).__init__(**kwargs)

        for number in range(0, 2):
            self.add_parameter()

    def add_parameter(self):
        parameter = ParameterLayout()
        parameter.ids.key_name.text = "         ParameterName:"
        parameter.ids.key_input.suggestions_source = "model_performance_suggestions"
        parameter.ids.value_input.input_filter = "float"

        self.add_widget(parameter)

    def to_dictionary(self):
        return save_parameter_fields(self)

    def fill_fields(self, loaded_dictionary):
        fill_parameter_fields(self, loaded_dictionary)


# contains a list of 'ThreatModelContainer's ( <- ThreatModel is not plural)
class ThreatModelsContainer(BoxLayout):
    def add_threat_model(self):
        tmc = ThreatModelContainer()
        self.add_widget(tmc)


# contains ThreatModel information and an 'AttackersContainer'
class ThreatModelContainer(BoxLayout):
    pass


# contains a list of 'AttackerContainer's ( <- Attacker is not plural)
class AttackersContainer(BoxLayout):
    def add_attacker(self):
        ac = AttackerContainer()
        self.add_widget(ac)

    def to_dictionary(self):
        global _Missing_Field
        attackers_dictionary = {}

        for attacker in self.children:
            if len(attacker.ids.attacker_fields.ids.attacker_name_input.text) != 0:
                attackers_dictionary[
                    attacker.ids.attacker_fields.ids.attacker_name_input.text] = attacker.to_dictionary()
            else:
                attackers_dictionary[
                    attacker.ids.attacker_fields.ids.attacker_name_input.text] = attacker.to_dictionary()
                attacker.ids.attacker_fields.ids.attacker_name_input.hint_text = "REQUIRED FIELD"
                _Missing_Field = True

        return attackers_dictionary

    def fill_fields(self, loaded_dictionary):
        attacker_keys = list(loaded_dictionary.keys())
        trim_field_number(len(attacker_keys), self, self.add_attacker)

        index = 0
        for key in attacker_keys:
            self.children[index].ids.attacker_fields.ids.attacker_name_input.text = key
            self.children[index].fill_fields(loaded_dictionary[key])
            index += 1


# contains 'AttackerFields', 'AttackParameters', 'AttackerPerformance' and a 'DefendersContainer'
class AttackerContainer(BoxLayout):
    def to_dictionary(self):
        global _Missing_Field
        attacker_dictionary = {"attackParams": self.ids.attack_parameters.to_dictionary(),
                               "attacker_performance": self.ids.attacker_performance.to_dictionary(),
                               "defenders": self.ids.defenders_container.to_dictionary()}

        if len(self.ids.attacker_fields.ids.attacker_type_input.text) != 0:
            attacker_dictionary["type_of_attack"] = self.ids.attacker_fields.ids.attacker_type_input.text
        else:
            self.ids.attacker_fields.ids.attacker_type_input.hint_text = "REQUIRED FIELD"
            _Missing_Field = True

        return attacker_dictionary

    def fill_fields(self, loaded_dictionary):
        self.ids.attacker_fields.ids.attacker_type_input.text = loaded_dictionary["type_of_attack"]
        self.ids.attack_parameters.fill_fields(loaded_dictionary["attackParams"])
        self.ids.attacker_performance.fill_fields(loaded_dictionary["attacker_performance"])
        self.ids.defenders_container.fill_fields(loaded_dictionary["defenders"])


# contains Attack parameter information
class AttackParameters(BoxLayout):
    def __init__(self, **kwargs):
        super(AttackParameters, self).__init__(**kwargs)

        for number in range(0, 2):
            self.add_parameter()

    def add_parameter(self):
        parameter = ParameterLayout()
        parameter.ids.key_name.text = "                 ParameterName:"

        self.add_widget(parameter)

    def to_dictionary(self):
        return save_parameter_fields(self)

    def fill_fields(self, loaded_dictionary):
        fill_parameter_fields(self, loaded_dictionary)


# contains Attacker performance information
class AttackerPerformance(BoxLayout):
    def __init__(self, **kwargs):
        super(AttackerPerformance, self).__init__(**kwargs)

        for number in range(0, 2):
            self.add_parameter()

    def add_parameter(self):
        parameter = ParameterLayout()
        parameter.ids.key_name.text = "                 ParameterName:"
        parameter.ids.key_input.suggestions_source = "attacker_performance_suggestions"
        parameter.ids.value_input.input_filter = "float"

        self.add_widget(parameter)

    def to_dictionary(self):
        return save_parameter_fields(self)

    def fill_fields(self, loaded_dictionary):
        fill_parameter_fields(self, loaded_dictionary)


# contains a list of 'DefenderContainer's ( <- Defender is not plural)
class DefendersContainer(BoxLayout):
    def add_defender(self):
        dc = DefenderContainer()
        self.add_widget(dc)

    def to_dictionary(self):
        defenders_list = []

        for defender in self.children:
            defenders_list.append(defender.to_dictionary())

        return defenders_list

    def fill_fields(self, loaded_dictionary):
        trim_field_number(len(loaded_dictionary), self, self.add_defender)

        index = 0
        for key in loaded_dictionary:
            self.children[index].fill_fields(key)
            index += 1


# contains 'DefenderFields', 'DefenseParameters', and 'DefenderPerformance'
class DefenderContainer(BoxLayout):
    def to_dictionary(self):
        global _Missing_Field
        defender_dictionary = {"defense_params": self.ids.defense_parameters.to_dictionary(),
                               "defender_performance": self.ids.defender_performance.to_dictionary()}

        if len(self.ids.defender_fields.ids.defender_name_input.text) != 0:
            defender_dictionary["nameOfDefender"] = self.ids.defender_fields.ids.defender_name_input.text
        else:
            self.ids.defender_fields.ids.defender_name_input.hint_text = "REQUIRED FIELD"
            _Missing_Field = True

        if len(self.ids.defender_fields.ids.defender_type_input.text) != 0:
            defender_dictionary["type"] = self.ids.defender_fields.ids.defender_type_input.text
        else:
            self.ids.defender_fields.ids.defender_type_input.hint_text = "REQUIRED FIELD"
            _Missing_Field = True

        return defender_dictionary

    def fill_fields(self, loaded_dictionary):
        self.ids.defender_fields.ids.defender_name_input.text = loaded_dictionary["nameOfDefender"]
        self.ids.defender_fields.ids.defender_type_input.text = loaded_dictionary["type"]
        self.ids.defense_parameters.fill_fields(loaded_dictionary["defense_params"])
        self.ids.defender_performance.fill_fields(loaded_dictionary["defender_performance"])


# contains Defense parameter information
class DefenseParameters(BoxLayout):
    def __init__(self, **kwargs):
        super(DefenseParameters, self).__init__(**kwargs)

        for number in range(0, 2):
            self.add_parameter()

    def add_parameter(self):
        parameter = ParameterLayout()
        parameter.ids.key_name.text = "                         ParameterName:"

        self.add_widget(parameter)

    def to_dictionary(self):
        return save_parameter_fields(self)

    def fill_fields(self, loaded_dictionary):
        fill_parameter_fields(self, loaded_dictionary)


# contains Defender performance information
class DefenderPerformance(BoxLayout):
    def __init__(self, **kwargs):
        super(DefenderPerformance, self).__init__(**kwargs)

        for number in range(0, 2):
            self.add_parameter()

    def add_parameter(self):
        parameter = ParameterLayout()
        parameter.ids.key_name.text = "                         ParameterName:"
        parameter.ids.key_input.suggestions_source = "defender_performance_suggestions"
        parameter.ids.value_input.input_filter = "float"

        self.add_widget(parameter)

    def to_dictionary(self):
        return save_parameter_fields(self)

    def fill_fields(self, loaded_dictionary):
        fill_parameter_fields(self, loaded_dictionary)


class SettingsWindow(Screen):
    _popup = None

    def generate_settings_json(self):
        global _Missing_Field
        _Missing_Field = False
        global _Settings_JSON
        _Settings_JSON = self.ids.all_setting_fields_scrollview.ids.all_setting_fields_container.to_dictionary()

        if self.get_missing_field_status() == False:
            self.show_save()
        else:
            return

    def get_missing_field_status(self):
        global _Missing_Field
        return _Missing_Field

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        show_load_explorer(self)

    def load(self, path, filename):
        f = open(os.path.join(path, filename[0]))
        loaded_dictionary = json.load(f)
        f.close()

        self.ids.all_setting_fields_scrollview.ids.all_setting_fields_container.fill_fields(loaded_dictionary)

        self.dismiss_popup()

    def show_save(self):
        show_save_explorer(self, 'settings_default_save.json')

    def save(self, path, filename):
        global _Settings_JSON_File_Path
        if valid_save_name(filename) == True:
            if filename.count('.') == 0:
                filename += ".json"
            _Settings_JSON_File_Path = os.path.join(path, filename)

            if filename == ".json":
                _Settings_JSON_File_Path = 'settings_default_save.json'

            with open(_Settings_JSON_File_Path, 'w') as f:
                json.dump(_Settings_JSON, f, indent=2)

            self.dismiss_popup()

        else:
            self._popup.content.ids.label.text = valid_save_name(filename)


# contains 'DefaultSettingFieldsContainer', 'CustomScoresContainer', and 'ConstraintsContainer'
class AllSettingFieldsContainer(BoxLayout):
    def to_dictionary(self):
        global _Missing_Field
        setting_dict = {}

        if len(self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.input_data_path_input.text) != 0:
            setting_dict[
                "input_data_path"] = self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.input_data_path_input.text
        else:
            self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.input_data_path_input.hint_text = "REQUIRED FIELD"
            _Missing_Field = True

        scores_list = self.ids.custom_scores_container.ids.formulas_container.to_dictionary()
        setting_dict["customized_metric_score"] = scores_list

        solver_dict = {"constraints": self.ids.constraints_container.ids.constraints.to_dictionary()}
        if len(self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.solver_name_input.text) != 0:
            solver_dict[
                "name"] = self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.solver_name_input.text
        else:
            self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.solver_name_input.hint_text = "REQUIRED FIELD"
            _Missing_Field = True
        if len(self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.solver_file_path_input.text) != 0:
            solver_dict[
                "path"] = self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.solver_file_path_input.text
        else:
            self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.solver_file_path_input.hint_text = "REQUIRED FIELD"
            _Missing_Field = True

        setting_dict["solver"] = solver_dict

        output_dict = {}
        output_file_path = self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.output_file_path_input.text
        if len(output_file_path) != 0:
            output_dict[
                "output_file_path"] = output_file_path
        else:
            self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.output_file_path_input.hint_text = "REQUIRED FIELD"
            _Missing_Field = True

        setting_dict["output"] = output_dict

        return setting_dict

    def fill_fields(self, loaded_dictionary):
        # input path
        self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.input_data_path_input.text = \
            loaded_dictionary["input_data_path"]
        # output path
        self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.output_file_path_input.text = \
            loaded_dictionary["output"]["output_file_path"]

        # solver name
        self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.solver_name_input.text = \
            loaded_dictionary["solver"]["name"]
        # solver path
        self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.solver_file_path_input.text = \
            loaded_dictionary["solver"]["path"]
        # solver constraints
        self.ids.constraints_container.ids.constraints.fill_fields(loaded_dictionary["solver"]["constraints"])

        # formulas
        self.ids.custom_scores_container.ids.formulas_container.fill_fields(
            loaded_dictionary["customized_metric_score"])


# contains 'DefaultSettingFieldsGrid'
class DefaultSettingFieldsGrid(GridLayout):
    _popup = None

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        show_load_explorer(self)

    def load(self, path, filename):
        if filename:
            self.ids.input_data_path_input.text = filename[0]

            self.dismiss_popup()

    def show_save(self):
        show_save_explorer(self, 'output_file_name.json')

    def save(self, path, filename):
        if valid_save_name(filename) == True:
            if filename.count('.') == 0:
                filename += ".json"
            self.ids.output_file_path_input.text = os.path.join(path, filename)

            if filename == ".json":
                self.ids.output_file_path_input.text = 'output_file_name.json'

            self.dismiss_popup()

        else:  # prints the error message to the user if the save name was not valid
            self._popup.content.ids.label.text = valid_save_name(filename)


# contains a list of 'FormulaFieldsContainer's
class FormulasContainer(BoxLayout):
    def __init__(self, **kwargs):
        super(FormulasContainer, self).__init__(**kwargs)

        # add formula fields by default
        for number in range(0, 1):
            self.add_formula()

    def add_formula(self):
        formula = FormulaFieldsContainer()
        self.add_widget(formula)

    def to_dictionary(self):
        formulas_list = []

        for formula in self.children:
            formula_dictionary = formula.to_dictionary()

            formulas_list.append(formula_dictionary)

        return formulas_list

    def fill_fields(self, loaded_dictionary):
        trim_field_number(len(loaded_dictionary), self, self.add_formula)

        index = 0
        for key in loaded_dictionary:
            self.children[index].fill_fields(key)
            index += 1


# contains 'FormulaFields' and 'FormulaParameters'
class FormulaFieldsContainer(BoxLayout):
    def to_dictionary(self):
        global _Missing_Field
        formula_dictionary = {}

        if len(self.ids.formula_fields.ids.formula_name_input.text) != 0:
            formula_dictionary["name"] = self.ids.formula_fields.ids.formula_name_input.text
        else:
            self.ids.formula_fields.ids.formula_name_input.hint_text = "REQUIRED FIELD"
            _Missing_Field = True

        if len(self.ids.formula_fields.ids.formula_path_input.text) != 0:
            formula_dictionary["path"] = self.ids.formula_fields.ids.formula_path_input.text
        else:
            self.ids.formula_fields.ids.formula_path_input.hint_text = "REQUIRED FIELD"
            _Missing_Field = True

        params_dictionary = save_parameter_fields(self.ids.formula_parameters)
        params_dictionary["showDetails"] = True

        formula_dictionary["scoreCalculatorParam"] = params_dictionary

        return formula_dictionary

    def fill_fields(self, loaded_dictionary):
        self.ids.formula_fields.ids.formula_name_input.text = loaded_dictionary["name"]
        self.ids.formula_fields.ids.formula_path_input.text = loaded_dictionary["path"]
        self.ids.formula_parameters.fill_fields(loaded_dictionary["scoreCalculatorParam"])


# contains Formula information
class FormulaFields(GridLayout):
    pass


# contains Formula parameter information
class FormulaParameters(BoxLayout):
    def __init__(self, **kwargs):
        super(FormulaParameters, self).__init__(**kwargs)

        # add metric fields by default
        for number in range(0, 2):
            self.add_parameter()

    def add_parameter(self):
        parameter = ParameterLayout()
        parameter.ids.key_name.text = "         ParameterName:"
        self.add_widget(parameter)

    def fill_fields(self, loaded_dictionary):
        fill_parameter_fields(self, loaded_dictionary)


# contains a list of 'ConstraintLayout's
class Constraints(BoxLayout):
    def __init__(self, **kwargs):
        super(Constraints, self).__init__(**kwargs)

        # add metric fields by default
        for number in range(0, 3):
            self.add_constraint()

    def add_constraint(self):
        constraint = ConstraintLayout()
        self.add_widget(constraint)

    def to_dictionary(self):
        constraints_list = []

        for constraint in self.children:
            constraint_dictionary = constraint.to_dictionary()

            if len(constraint_dictionary) != 0:
                constraints_list.append(constraint_dictionary)

        if len(constraints_list) == 0:
            global _Missing_Field
            _Missing_Field = True

            self.children[-1].ids.key_input.hint_text = "AT LEAST 1 CONSTRAINT REQUIRED"

        return constraints_list

    def fill_fields(self, loaded_dictionary):
        trim_field_number(len(loaded_dictionary), self, self.add_constraint)

        index = 0
        for constraint in loaded_dictionary:
            self.children[index].fill_fields(constraint)
            index += 1


# contains Parameter information
class ParameterLayout(BoxLayout):
    pass


# contains Constraint information
class ConstraintLayout(BoxLayout):
    def to_dictionary(self):
        constraint_dictionary = {}

        if self.ids.constraint_spinner.text != 'constraint':
            constraint_dictionary["constraint"] = self.ids.constraint_spinner.text

        # ignore if min or max
        if self.ids.constraint_spinner.text != 'min' and self.ids.constraint_spinner.text != 'max' and len(
                self.ids.value_input.text) != 0:
            value = self.ids.value_input.text
            constraint_dictionary["constraint_value"] = int(value)

        if len(self.ids.key_input.text) != 0:
            constraint_dictionary["metric_name"] = self.ids.key_input.text

        return constraint_dictionary

    def fill_fields(self, loaded_dictionary):
        if "metric_name" in loaded_dictionary:
            self.ids.key_input.text = loaded_dictionary["metric_name"]
            self.ids.key_input.dropdown.dismiss()
        if "constraint_value" in loaded_dictionary:
            self.ids.value_input.text = str(loaded_dictionary["constraint_value"])
            self.ids.value_input.dropdown.dismiss()
        if "constraint" in loaded_dictionary:
            self.ids.constraint_spinner.text = loaded_dictionary["constraint"]
            self.ids.constraint_spinner.min_max_clear(self.ids.value_input)


# contains list of Constraints for user to choose from
# FUTURE WORK: currently has awkward sizing and spacing that should be fixed
class ConstraintSpinner(Spinner):
    # determines value_input status for the constraint
    # if default operator is chosen, only float values can be input
    # if min or max is chosen, value is set to min or max and becomes readonly
    # if using a custom constraint, there are no restrictions to what value can be input
    def min_max_clear(self, value_input):
        operators = ['>', '>=', '==', '<=', '<']
        if self.text == 'min':
            value_input.text = "min"
            value_input.readonly = True
        elif self.text == 'max':
            value_input.text = "max"
            value_input.readonly = True
        elif self.text in operators:
            value_input.readonly = False
            if value_input.text == 'min':
                value_input.text = ''
            if value_input.text == 'max':
                value_input.text = ''
            value_input.input_filter = "float"
        else:
            value_input.readonly = False
            value_input.input_filter = None

    def get_values(self):
        global _Constraint_Options
        return _Constraint_Options


# contains field for custom constraint and the button to add it
class AddCustomConstraints(BoxLayout):
    # adds the custom constraint as an option to the constraint spinners
    # notifies the user when the constraint is added
    def add_custom_constraint(self):
        if len(self.ids.custom_constraint_input.text) != 0:
            values_list = self.parent.ids.constraints.children[0].ids.constraint_spinner.values

            values_list.append(self.ids.custom_constraint_input.text)

            # update constraint options
            global _Constraint_Options
            _Constraint_Options = values_list

            # update constraint options of previously added spinners
            for constraint_spinner in self.parent.ids.constraints.children:
                constraint_spinner.ids.constraint_spinner.values = values_list

            self.ids.custom_constraint_text.text = " Added '" + self.ids.custom_constraint_input.text + "'"


class RecommendationsWindow(Screen):
    # extract the recommendations into dictionary form from the given settings file
    def extract_recommendations(self, settings_filename):
        settings_file = open(settings_filename)
        settings_dictionary = json.load(settings_file)
        settings_file.close()

        output_path = settings_dictionary["output"]["output_file_path"]
        output_file = open(output_path)
        output_dictionary = json.load(output_file)
        output_file.close()

        self.present_recommendations(output_dictionary)

    # present the recommendations in the given dictionary
    def present_recommendations(self, output_dictionary):
        # add a recommendation container containing the information of each dataset, model classifier, threat model,
        # and attacker
        # a recommendation container has a button to expand/collapse each section as well as a label to display
        # the content
        for dataset in output_dictionary["recommendation_result"]:
            # each level of the loop is creating a container in the given parent container with the given text
            dataset_rc = self.add_recommendation_container(self.ids.recommendations_scrollview, " Dataset: " + dataset)

            for model_classifier in output_dictionary["recommendation_result"][dataset]:
                model_classifier_rc = self.add_recommendation_container(dataset_rc, "    Model Classifier: " + model_classifier)

                for threat_model in output_dictionary["recommendation_result"][dataset][model_classifier]:
                    threat_model_rc = self.add_recommendation_container(model_classifier_rc, "        Threat Model: " + threat_model)

                    for attack in output_dictionary["recommendation_result"][dataset][model_classifier][threat_model]:
                        attack_rc = self.add_recommendation_container(threat_model_rc, "            Attacker Model: " + attack)

                        solver_status = RecommendationLabel(text="                        Solver Status: " + output_dictionary["recommendation_result"][dataset][model_classifier][threat_model][attack]["solver_status"])
                        recommended_defender = RecommendationLabel(text="                        Recommended Defender: " +output_dictionary["recommendation_result"][dataset][model_classifier][threat_model][attack]["recommendation"])
                        attack_rc.ids.sub_layer_container.add_widget(solver_status)
                        attack_rc.ids.sub_layer_container.add_widget(recommended_defender)

    # creates a container in the given parent container with the given text and returns the created container
    def add_recommendation_container(self, parent_container, layer_label_text):
        rc = RecommendationContainer()
        rc.ids.layer_label.text = layer_label_text
        parent_container.ids.sub_layer_container.add_widget(rc)
        return rc


# contains an expand/collapse button, a label for the layer (dataset or model classifier or threat model etc.)
# and contains a BoxLayout to store its nested layer (ex: dataset would store model classifiers)
class RecommendationContainer(BoxLayout):
    pass


# a Label with defined attributes regularly used to have consistent Recommendation Labels
class RecommendationLabel(Label):
    pass


# a Label with defined attributes regularly used to have consistent Labels for fields
class FieldName(Label):
    pass


# a TextInput with defined attributes regularly used to have consistent TextInputs
# can be given a suggestions_source to use its custom-made autocomplete feature
class FieldInput(TextInput):
    suggestion_index = -404
    dropdown = DropDown()
    suggestions_source = ''

    # sets the FieldInput's text to the given text
    def dropdown_set_text(self, text):
        self.text = text
        self.dropdown.dismiss()

    # determine the suggestion source to use
    # FUTURE WORK: create a page where the user can manage each list of suggestions, including
    # adding suggestions and deleting suggestions from the lists
    def determine_suggestions_source(self):
        if self.suggestions_source == "":
            return []
        elif self.suggestions_source == "test_suggestions":
            return TEST_SUGGESTIONS
        elif self.suggestions_source == "model_performance_suggestions":
            return MODEL_PERFORMANCE_SUGGESTIONS
        elif self.suggestions_source == "attacker_performance_suggestions":
            return ATTACKER_PERFORMANCE_SUGGESTIONS
        elif self.suggestions_source == "defender_performance_suggestions":
            return DEFENDER_PERFORMANCE_SUGGESTIONS
        elif self.suggestions_source == "constraint_suggestions":
            return CONSTRAINT_SUGGESTIONS
        else:
            # if this appears in the UI, there is likely a typo in the suggestion source used
            return ['unintended suggestion source']

    # determines the suggestions to show the user based on their current input and displays them
    def give_suggestions(self):
        self.dropdown.dismiss()
        self.dropdown = DropDown()

        user_input = self.text

        all_suggestions = self.determine_suggestions_source()

        suggestions = []

        # populates suggestions by comparing the user input to the list of all-suggestions
        # FUTURE WORK: the suggestions list should be populated in a smarter and more efficient manner
        # currently takes a brute force approach that just checks if the user input is in each suggestion
        # currently presents suggestions in the order of the original all_suggestions list
        for word in all_suggestions:
            if user_input in word:
                suggestions.append(word)

        # each suggestion that matches the user input is added as an option to select in the dropdown of suggestions
        # FUTURE WORK: only the top k suggestions should be shown, where k is some number that the user chooses
        for option in suggestions:
            btn = Button(size_hint=(1, None), height="30dp")
            btn.text = option
            btn.bind(on_release=lambda the_btn: self.dropdown_set_text(the_btn.text))
            self.dropdown.add_widget(btn)

        # if there is at least 1 suggestion, the suggestion_index is set and the first suggestion is highlighted
        if len(self.dropdown.children[0].children) > 0:
            self.suggestion_index = len(self.dropdown.children[0].children) - 1
            self.dropdown.open(self)
            self.dropdown.children[0].children[self.suggestion_index].background_color = (2, 2, 2, 2)

    # overrides the keyboard_on_key_down method
    # enables the user to use the up and down arrow keys to navigate the list of suggestions
    # the enter key can be used to select a suggestion
    # the tab key can be used to select a suggestion and move to the next field
    # FUTURE WORK: when using the up and down arrow keys to navigate, if the user tries to navigate
    # beyond what is visible on the scrollbar of suggestions, the scrollbar does not move with the user
    # in order to see what they are selecting, the user would have to use their mouse to scroll to their
    # current selection. to fix this, when using the arrow keys we should check if we need to move the scrollbar
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if len(self.dropdown.children[0].children) > 0:
            if keycode[1] == 'up':
                if self.suggestion_index < len(self.dropdown.children[0].children) - 1:
                    self.suggestion_index = self.suggestion_index + 1
                    self.dropdown.children[0].children[self.suggestion_index].background_color = (2, 2, 2, 2)
                    self.dropdown.children[0].children[self.suggestion_index - 1].background_color = (1, 1, 1, 1)
                    return True

            elif keycode[1] == 'down':
                if self.suggestion_index > 0:
                    self.suggestion_index = self.suggestion_index - 1
                    self.dropdown.children[0].children[self.suggestion_index].background_color = (2, 2, 2, 2)
                    self.dropdown.children[0].children[self.suggestion_index + 1].background_color = (1, 1, 1, 1)
                    return True

            elif keycode[1] == 'enter':
                self.dropdown_set_text(self.dropdown.children[0].children[self.suggestion_index].text)
                return True

            elif keycode[1] == 'tab':
                self.dropdown_set_text(self.dropdown.children[0].children[self.suggestion_index].text)
                # does not return True in order to keep default tab behavior of moving to next field

        return super().keyboard_on_key_down(window, keycode, text, modifiers)


# to be used to create a file explorer for choosing a file to load
class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def get_the_path(self):
        return os.getcwd()


# to be used to create a file explorer for saving a file
class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def get_the_path(self):
        return os.getcwd()


# TextInput used specifically by 'SaveDialog'
class SaveTextInput(TextInput):
    # overrides the keyboard_on_key_down method so enter key is a shortcut to save
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] == 'enter':
            self.parent.parent.save(self.parent.parent.ids.filechooser.path, self.parent.parent.ids.text_input.text)
        return super().keyboard_on_key_down(window, keycode, text, modifiers)


_kv = Builder.load_file("kivy.kv")


class RecommenderTool(App):
    def build(self):
        return _kv


RecommenderTool().run()
