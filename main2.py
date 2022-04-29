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

_Missing_Field = False

TEST_SUGGESTIONS = [
    'aaa', 'aab', 'aac', 'aad', 'aae',
    'aba', 'abb', 'abc', 'abd', 'abe',
    'aca', 'acb', 'acc', 'acd', 'ace',
]

MODEL_PERFORMANCE_SUGGESTIONS = ['natural_accuracy', 'natural_precision', 'natural_recall', 'natural_f1-score',
                                 'inference_elapsed_time_per_1000_in_s']

ATTACKER_PERFORMANCE_SUGGESTIONS = ['robust_accuracy', 'robust_precision', 'robust_recall', 'robust_f1-score']

DEFENDER_PERFORMANCE_SUGGESTIONS = ['natural_accuracy', 'natural_precision', 'natural_recall', 'natural_f1-score',
                                    'robust_accuracy', 'robust_precision', 'robust_recall', 'robust_f1-score',
                                    'inference_elapsed_time_per_1000_in_s']

CONSTRAINT_SUGGESTIONS = DEFENDER_PERFORMANCE_SUGGESTIONS


def cast_if_float(s):
    try:
        return float(s)
    except ValueError:
        return s


def get_value_input(parameter):
    value_input = parameter.ids.value_input.text
    if value_input != 'true' and value_input != 'True' and value_input != 'false' and value_input != 'False':
        return cast_if_float(value_input)
    elif value_input == 'true' or value_input == 'True':
        return True
    elif value_input == 'false' or value_input == 'False':
        return False


def save_parameter_fields(parameter_container):
    params_dictionary = {}
    for parameter in parameter_container.children:
        if len(parameter.ids.key_input.text) != 0:
            params_dictionary[parameter.ids.key_input.text] = get_value_input(parameter)

    return params_dictionary


def fill_parameter_fields(parameter_container, loaded_dictionary):
    parameter_keys = list(loaded_dictionary.keys())
    parameter_values = list(loaded_dictionary.values())

    while len(parameter_keys) > len(parameter_container.children):
        parameter_container.add_parameter()

    while len(parameter_keys) < len(parameter_container.children):
        parameter_container.remove_widget(parameter_container.children[0])

    index = 0
    for key in parameter_keys:
        parameter_container.children[index].ids.key_input.text = key
        parameter_container.children[index].ids.value_input.text = str(parameter_values[index])
        parameter_container.children[index].ids.key_input.dropdown.dismiss()
        parameter_container.children[index].ids.value_input.dropdown.dismiss()
        index += 1


def valid_save_name(path, filename):
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


class MainWindow(Screen):
    def generate_button(self):
        global _Settings_JSON_File_Path
        if len(_Settings_JSON_File_Path) != 0:
            driver = Driver(settingPath=_Settings_JSON_File_Path)
            driver.drive()
        else:
            driver = Driver(settingPath="gen_setting02.json")
            driver.drive()



class DataWindow(Screen):
    def generate_ml_model_data_json(self):
        global _Missing_Field
        _Missing_Field = False
        global _ML_Model_Data_JSON
        _ML_Model_Data_JSON = {"context": {"GPU": "dummyGPU", "image_size": [224, 224, 3]},
                               "data": self.ids.data_fields_scrollview.ids.all_datasets_container.ids.datasets_container.to_dictionary()}

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
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        f = open(os.path.join(path, filename[0]))
        loaded_dictionary = json.load(f)
        f.close()

        self.ids.data_fields_scrollview.ids.all_datasets_container.ids.datasets_container.fill_fields(
            loaded_dictionary["data"])

        self.dismiss_popup()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.content.ids.text_input.hint_text = 'ml_model_data_default_save.json'
        self._popup.open()
        self._popup.content.ids.text_input.focus = True

    def save(self, path, filename):
        global _ML_Model_Data_JSON_File_Path
        if valid_save_name(path, filename) == True:
            if filename.count('.') == 0:
                filename += ".json"
            _ML_Model_Data_JSON_File_Path = os.path.join(path, filename)

            if filename == ".json":
                _ML_Model_Data_JSON_File_Path = 'ml_model_data_default_save.json'

            with open(_ML_Model_Data_JSON_File_Path, 'w') as f:
                json.dump(_ML_Model_Data_JSON, f, indent=2)

                self.dismiss_popup()
        else:
            self._popup.content.ids.label.text = valid_save_name(path, filename)


class AllDatasetsContainer(BoxLayout):
    pass


class DatasetsContainer(BoxLayout):
    def add_dataset(self):
        dc = DatasetContainer()
        self.add_widget(dc)

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

    def fill_fields(self, loaded_dictionary):
        dataset_keys = list(loaded_dictionary.keys())

        while len(dataset_keys) > len(self.children):
            self.add_dataset()

        index = 0
        for key in dataset_keys:
            self.children[index].ids.dataset_name_input.text = key
            self.children[index].ids.all_data_models_container.ids.data_models_container.fill_fields(
                loaded_dictionary[key])
            index += 1


class DatasetContainer(BoxLayout):
    pass


class AllDataModelsContainer(BoxLayout):
    pass


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

        while len(model_keys) > len(self.children):
            self.add_model()

        index = 0
        for key in model_keys:
            self.children[index].ids.model_fields.ids.model_classifier_input.text = key
            self.children[index].fill_fields(loaded_dictionary[key])
            index += 1


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

        while len(threat_model_keys) > len(self.ids.threat_models_container.children):
            self.ids.threat_models_container.add_threat_model()

        index = 0
        for key in threat_model_keys:
            self.ids.threat_models_container.children[index].ids.threat_model_name_input.text = key
            self.ids.threat_models_container.children[index].ids.attackers_container.fill_fields(loaded_dictionary[key])
            index += 1


class ModelPerformance(BoxLayout):
    def __init__(self, **kwargs):
        super(ModelPerformance, self).__init__(**kwargs)

        for number in range(0, 2):
            self.add_parameter()

    def add_parameter(self):
        parameter = ParameterLayout()
        parameter.ids.key_name.text = "         ParameterName:"
        parameter.ids.key_input.suggestions_source = "model_performance_suggestions"

        self.add_widget(parameter)

    def to_dictionary(self):
        return save_parameter_fields(self)

    def fill_fields(self, loaded_dictionary):
        fill_parameter_fields(self, loaded_dictionary)


class ThreatModelsContainer(BoxLayout):
    def add_threat_model(self):
        tmc = ThreatModelContainer()
        self.add_widget(tmc)


class ThreatModelContainer(BoxLayout):
    pass


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

        while len(attacker_keys) > len(self.children):
            self.add_attacker()

        index = 0
        for key in attacker_keys:
            self.children[index].ids.attacker_fields.ids.attacker_name_input.text = key
            self.children[index].fill_fields(loaded_dictionary[key])
            index += 1


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


class AttackerPerformance(BoxLayout):
    def __init__(self, **kwargs):
        super(AttackerPerformance, self).__init__(**kwargs)

        for number in range(0, 2):
            self.add_parameter()

    def add_parameter(self):
        parameter = ParameterLayout()
        parameter.ids.key_name.text = "                 ParameterName:"
        parameter.ids.key_input.suggestions_source = "attacker_performance_suggestions"

        self.add_widget(parameter)

    def to_dictionary(self):
        return save_parameter_fields(self)

    def fill_fields(self, loaded_dictionary):
        fill_parameter_fields(self, loaded_dictionary)


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
        while len(loaded_dictionary) > len(self.children):
            self.add_defender()

        index = 0
        for key in loaded_dictionary:
            self.children[index].fill_fields(key)
            index += 1


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


class DefenderPerformance(BoxLayout):
    def __init__(self, **kwargs):
        super(DefenderPerformance, self).__init__(**kwargs)

        for number in range(0, 2):
            self.add_parameter()

    def add_parameter(self):
        parameter = ParameterLayout()
        parameter.ids.key_name.text = "                         ParameterName:"
        parameter.ids.key_input.suggestions_source = "defender_performance_suggestions"

        self.add_widget(parameter)

    def to_dictionary(self):
        return save_parameter_fields(self)

    def fill_fields(self, loaded_dictionary):
        fill_parameter_fields(self, loaded_dictionary)


class SettingsWindow(Screen):
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
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        f = open(os.path.join(path, filename[0]))
        loaded_dictionary = json.load(f)
        f.close()

        self.ids.all_setting_fields_scrollview.ids.all_setting_fields_container.fill_fields(loaded_dictionary)

        self.dismiss_popup()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.content.ids.text_input.hint_text = 'settings_default_save.json'
        self._popup.open()
        self._popup.content.ids.text_input.focus = True

    def save(self, path, filename):
        global _Settings_JSON_File_Path
        if valid_save_name(path, filename) == True:
            if filename.count('.') == 0:
                filename += ".json"
            _Settings_JSON_File_Path = os.path.join(path, filename)

            if filename == ".json":
                _Settings_JSON_File_Path = 'settings_default_save.json'

            with open(_Settings_JSON_File_Path, 'w') as f:
                json.dump(_Settings_JSON, f, indent=2)

            self.dismiss_popup()

        else:
            self._popup.content.ids.label.text = valid_save_name(path, filename)


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
        if len(self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.output_file_path_input.text) != 0:
            output_dict[
                "output_file_path"] = self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.output_file_path_input.text
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
            loaded_dictionary["output"]["outputFilePath"]

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


class DefaultSettingFieldsGrid(GridLayout):
    pass


class WindowManager(ScreenManager):
    pass


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
        while len(loaded_dictionary) > len(self.children):
            self.add_formula()

        index = 0
        for key in loaded_dictionary:
            self.children[index].fill_fields(key)
            index += 1


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


class FormulaFields(GridLayout):
    pass


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
        while len(loaded_dictionary) > len(self.children):
            self.add_constraint()

        index = 0
        for constraint in loaded_dictionary:
            self.children[index].fill_fields(constraint)
            index += 1


class ParameterLayout(BoxLayout):
    pass


class ConstraintLayout(BoxLayout):
    def to_dictionary(self):
        constraint_dictionary = {}

        if self.ids.constraint_spinner.text != 'constraint':
            constraint_dictionary["constraint"] = self.ids.constraint_spinner.text

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


class ConstraintSpinner(Spinner):
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


class AddCustomConstraints(BoxLayout):
    def add_custom_constraint(self):
        if len(self.ids.custom_constraint_input.text) != 0:
            values_list = self.parent.ids.constraints.children[0].ids.constraint_spinner.values

            values_list.append(self.ids.custom_constraint_input.text)

            for constraint_spinner in self.parent.ids.constraints.children:
                constraint_spinner.ids.constraint_spinner.values = values_list

            self.ids.custom_constraint_text.text = " Added '" + self.ids.custom_constraint_input.text + "'"


class FieldName(Label):
    pass


class FieldInput(TextInput):
    suggestion_index = -404
    dropdown = DropDown()
    suggestions_source = ''

    def dropdown_set_text(self, text):
        self.text = text
        self.dropdown.dismiss()

    def determine_suggestions_source(self):
        if self.suggestions_source == "":
            return ['no suggestion source']
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
            return ['unintended suggestion source']

    def give_suggestions(self):
        self.dropdown.dismiss()
        self.dropdown = DropDown()

        user_input = self.text

        suggestions = []

        all_suggestions = self.determine_suggestions_source()

        for word in all_suggestions:
            if user_input in word:
                suggestions.append(word)

        for option in suggestions:
            btn = Button(size_hint=(1, None), height="30dp")
            btn.text = option
            btn.bind(on_release=lambda the_btn: self.dropdown_set_text(the_btn.text))
            self.dropdown.add_widget(btn)

        if len(self.dropdown.children[0].children) > 0:
            self.suggestion_index = len(self.dropdown.children[0].children) - 1
            self.dropdown.open(self)
            self.dropdown.children[0].children[self.suggestion_index].background_color = (2, 2, 2, 2)

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

        return super().keyboard_on_key_down(window, keycode, text, modifiers)


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def get_the_path(self):
        return os.getcwd()


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def get_the_path(self):
        return os.getcwd()


class SaveTextInput(TextInput):
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] == 'enter':
            self.parent.parent.save(self.parent.parent.ids.filechooser.path, self.parent.parent.ids.text_input.text)
        return super().keyboard_on_key_down(window, keycode, text, modifiers)


_kv = Builder.load_file("kivy.kv")


class RecommenderTool(App):
    def build(self):
        return _kv


RecommenderTool().run()
