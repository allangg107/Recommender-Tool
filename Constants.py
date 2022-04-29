SUPPORT_PULP_OPS = ['max', '>=', '<=', 'min', '==']

BASELINE_PERFORMANCE = 'baseline_performance'
ATTACKER_PERFORMANCE = 'attacker_performance'
DEFENDER_PERFORMANCE = 'defender_performance'
DEFENDERS = 'defenders'
THREAT_MODELS = ['white-box_setting', 'grey-box_setting', 'black-box_setting']
DUMMY_INPUT_DATA_PATH = "dummyInputs/input_01.json"

DEFAULT_OUTPUT_LOCATION = "TERMINAL"

STATUS_DICT = {
  -1: "Optimal solution NOT found",
  0: "Not solved",
  1: "Optimal solution found"
}