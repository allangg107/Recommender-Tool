import sys

from Driver import Driver


if __name__ == '__main__':
    # TODO: improve CLI
    args = sys.argv[1:]
    settingPath = args[0]
    driver = Driver(
        settingPath = settingPath
    )
    driver.drive()