import os
import subprocess
from datetime import datetime
from typing_extensions import Annotated

from typer import Typer, Option, Argument
from rich import print

from .config import SESSION, COMMAND_PREFIX
from . import aoc_api


today = datetime.today()


def get_day(day):
    if day is None:
        if today.month != 12:
            return 24
        else:
            return today.day
    else:
        return day


def get_year(year):
    if year is None:
        if today.month != 12:
            return today.year - 1
        else:
            return today.year
    else:
        return year


app = Typer()


@app.command()
def pull(
        year: Annotated[int, Option(
            help='Year to pull task for',
            callback=get_year)] = None,
        day: Annotated[int, Option(
            help='Day to pull task for',
            callback=get_day)] = None,
        path: Annotated[str, Option(
            help='Path where task will be stored,'
            ' default is \'./year_<year>/day_<day>\'')] = None):
    '''
    Pulls a task from adventofcode.com
    '''

    if path is None:
        path = os.path.join(os.path.curdir, f'year_{year}', f'day_{day}')

    os.makedirs(path, exist_ok=True)

    aoc_api.pull_task(year, day, path, session=SESSION)
    print(os.path.abspath(path))


@app.command()
def run(
        command: Annotated[str, Argument(
            help='Command to run to get result')],
        input: Annotated[str, Option(
            help='Path to input file')] = os.path.join(os.curdir, 'test'),
        no_print: Annotated[bool, Option(
            hidden=True)] = False):
    '''
    Run code with input file.
    '''
    if input is None:
        input = os.path.join(os.curdir, 'test')

    args = [command, input]
    if COMMAND_PREFIX is not None:
        args.insert(0, COMMAND_PREFIX)

    completed = subprocess.run(args, text=True, capture_output=True)
    if completed.returncode != 0:
        print(f'[{" ".join(args)}] has exited with code {completed.returncode}')
        print(completed.stderr)
        exit(1)

    stdout = completed.stdout.split('\n')[:-1]
    result = stdout[-1]
    if not no_print:
        print(f'Result: {result}')
    return result, stdout


@app.command()
def test(
        expected: Annotated[str, Argument(
            help='Expected value')],
        command: Annotated[str, Argument(
            help='Command to run to get result',
            envvar='AOC_CLI_COMMAND')],
        input: Annotated[str, Option(
            help='Path to input file')] = os.path.join(os.curdir, 'test'),):
    '''
    Run code with input file and test agains expected value.
    '''

    expected = expected.strip()
    actual, stdout = run(command, input, no_print=True)
    if actual == expected:
        print('Passed [bold green]:heavy_check_mark:[/bold green]')
        print(f'  Result: [green italic]{actual}[/green italic]')
    else:
        print('Passed [bold red]:cross_mark:[/bold red]')
        print(f'  Expected: [green italic]{expected}[/green italic]')
        print(f'  Actual  : [red italic]{actual}[/red italic]')
        if len(stdout) > 1:
            print('Complete stdout:')
            print('\n'.join([f'  {i}' for i in stdout]))


if __name__ == '__main__':
    app()
