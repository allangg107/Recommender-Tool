import json

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from Driver import Driver

_ML_Model_Data_JSON = {}
_Settings_JSON_File_Path = ''
_Settings_JSON = {}

_required_fields = []


class MainWindow(Screen):
    def generate_button(self):
        driver = Driver(
            # global _Settings_JSON_File_Path
            # if len(_Setting_JSON_File_Path) != 0:
            #   settingPath = _Setting_JSON_File_Path
            settingPath='user_setting_01.json'
        )
        driver.drive()


class DataWindow(Screen):
    def generate_ml_model_data_json(self):
        global _ML_Model_Data_JSON
        _ML_Model_Data_JSON = {"context": {"GPU": "dummyGPU", "image_size": [224, 224, 3]},
                               "data": self.ids.data_fields_scrollview.ids.all_datasets_container.ids.datasets_container.to_dictionary()}

        save_name = self.ids.data_fields_scrollview.ids.all_datasets_container.ids.save_path_input.text

        if len(save_name) == 0:
            save_name = 'ml_model_data_default_save.json'

        with open(save_name, 'w') as f:
            json.dump(_ML_Model_Data_JSON, f, indent=2)


class AllDatasetsContainer(BoxLayout):
    pass


class DatasetsContainer(BoxLayout):
    def add_dataset(self):
        dc = DatasetContainer()
        self.add_widget(dc)

    def to_dictionary(self):
        datasets_dictionary = {}

        for dataset in self.children:
            dataset_dictionary = dataset.ids.all_data_models_container.ids.data_models_container.to_dictionary()
            datasets_dictionary[dataset.ids.dataset_name_input.text] = dataset_dictionary

        return datasets_dictionary


class DatasetContainer(BoxLayout):
    pass


class AllDataModelsContainer(BoxLayout):
    pass


class DataModelsContainer(BoxLayout):
    def add_model(self):
        mc = ModelContainer()
        self.add_widget(mc)

    def to_dictionary(self):
        models_dictionary = {}

        for model in self.children:
            model_dictionary = model.to_dictionary()
            models_dictionary[model.ids.model_fields.ids.model_classifier_input.text] = model_dictionary

        return models_dictionary


class ModelContainer(BoxLayout):
    def to_dictionary(self):
        model_dictionary = self.ids.model_performance.to_dictionary()

        for threat_model in self.ids.threat_models_container.children:
            model_dictionary[threat_model.ids.threat_model_name_input.text] = threat_model.ids.attackers_container.to_dictionary()

        return model_dictionary


class ModelPerformance(BoxLayout):
    def __init__(self, **kwargs):
        super(ModelPerformance, self).__init__(**kwargs)

        for number in range(0, 2):
            self.add_parameter()

    def add_parameter(self):
        parameter = ParameterLayout()
        parameter.ids.key_name.text = "         ParameterName:"

        self.add_widget(parameter)

    def to_dictionary(self):
        performances = {}
        for performance in self.children:
            performances[performance.ids.key_input.text] = performance.ids.value_input.text

        performance_dictionary = {"baseline_performance": performances}

        return performance_dictionary


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
        attackers_dictionary = {}

        for attacker in self.children:
            attackers_dictionary[attacker.ids.attacker_fields.ids.attacker_name_input.text] = attacker.to_dictionary()

        return attackers_dictionary


class AttackerContainer(BoxLayout):
    def to_dictionary(self):
        attacker_dictionary = {"type_of_attack": self.ids.attacker_fields.ids.attacker_type_input.text,
                               "attackParams": self.ids.attack_parameters.to_dictionary(),
                               "attacker_performance": self.ids.attacker_performance.to_dictionary(),
                               "defenders": self.ids.defenders_container.to_dictionary()}

        return attacker_dictionary


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
        parameters = {}
        for parameter in self.children:
            parameters[parameter.ids.key_input.text] = parameter.ids.value_input.text

        return parameters


class AttackerPerformance(BoxLayout):
    def __init__(self, **kwargs):
        super(AttackerPerformance, self).__init__(**kwargs)

        for number in range(0, 2):
            self.add_parameter()

    def add_parameter(self):
        parameter = ParameterLayout()
        parameter.ids.key_name.text = "                 ParameterName:"

        self.add_widget(parameter)

    def to_dictionary(self):
        performances = {}
        for performance in self.children:
            performances[performance.ids.key_input.text] = performance.ids.value_input.text

        return performances


class DefendersContainer(BoxLayout):
    def add_defender(self):
        dc = DefenderContainer()
        self.add_widget(dc)

    def to_dictionary(self):
        defenders_list = []

        for defender in self.children:
            defenders_list.append(defender.to_dictionary())

        return defenders_list


class DefenderContainer(BoxLayout):
    def to_dictionary(self):
        defender_dictionary = {"nameOfDefender": self.ids.defender_fields.ids.defender_name_input.text,
                               "type": self.ids.defender_fields.ids.defender_type_input.text,
                               "defense_params": self.ids.defense_parameters.to_dictionary(),
                               "defender_performance": self.ids.defender_performance.to_dictionary()}

        return defender_dictionary


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
        parameters = {}
        for parameter in self.children:
            parameters[parameter.ids.key_input.text] = parameter.ids.value_input.text

        return parameters


class DefenderPerformance(BoxLayout):
    def __init__(self, **kwargs):
        super(DefenderPerformance, self).__init__(**kwargs)

        for number in range(0, 2):
            self.add_parameter()

    def add_parameter(self):
        parameter = ParameterLayout()
        parameter.ids.key_name.text = "                         ParameterName:"

        self.add_widget(parameter)

    def to_dictionary(self):
        performances = {}
        for performance in self.children:
            performances[performance.ids.key_input.text] = performance.ids.value_input.text

        return performances


class SettingsWindow(Screen):
    def generate_settings_json(self):
        global _Settings_JSON
        _Settings_JSON = self.ids.all_setting_fields_scrollview.ids.all_setting_fields_container.to_dictionary()

        save_name = self.ids.all_setting_fields_scrollview.ids.all_setting_fields_container.ids.save_path_input.text

        if len(save_name) == 0:
            save_name = 'settings_default_save.json'

        global _Settings_JSON_File_Path
        _Settings_JSON_File_Path = save_name

        with open(save_name, 'w') as f:
            json.dump(_Settings_JSON, f, indent=2)


class AllSettingFieldsContainer(BoxLayout):
    def to_dictionary(self):
        setting_dict = {
            "input_data_path": self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.input_data_path_input.text}

        scores_list = self.ids.custom_scores_container.ids.formulas_container.to_dictionary()
        setting_dict["customized_metric_score"] = scores_list

        solver_dict = {
            "name": self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.solver_name_input.text,
            "path": self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.solver_file_path_input.text,
            "constraints": self.ids.constraints_container.ids.constraints.to_dictionary()}
        setting_dict["solver"] = solver_dict

        output_dict = {
            "outputFilePath": self.ids.default_setting_fields_container.ids.default_setting_fields_grid.ids.output_file_path_input.text}
        setting_dict["output"] = output_dict

        return setting_dict


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


class FormulaFieldsContainer(BoxLayout):
    def to_dictionary(self):
        formula_dictionary = {"name": self.ids.formula_fields.ids.formula_name_input.text,
                              "path": self.ids.formula_fields.ids.formula_path_input.text}

        params_dictionary = {"showDetails": True}

        for parameter in self.ids.formula_parameters.children:
            params_dictionary[parameter.ids.key_input.text] = parameter.ids.value_input.text

        formula_dictionary["scoreCalculatorParam"] = params_dictionary

        return formula_dictionary


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

            constraints_list.append(constraint_dictionary)

        return constraints_list


class ParameterLayout(BoxLayout):
    pass


class ConstraintLayout(BoxLayout):
    def to_dictionary(self):
        # if self.ids.constraint_spinner.text != 'constraint'
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
    pass


_kv = Builder.load_file("kivy.kv")


class RecommenderTool(App):
    def build(self):
        return _kv


RecommenderTool().run()
