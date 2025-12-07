import os
from dotenv import load_dotenv


CONFIG_PATH = os.path.expanduser(
        os.path.join('~', '.local', 'share', 'aoc_cli', 'config'))
if os.path.exists(CONFIG_PATH):
    load_dotenv(CONFIG_PATH)

SESSION = os.getenv('AOC_CLI_SESSION')
COMMAND_PREFIX = os.getenv('AOC_CLI_COMMAND_PREFIX')
if len(COMMAND_PREFIX) == 0:
    COMMAND_PREFIX = None
COMMAND = os.getenv('AOC_CLI_COMMAND')
