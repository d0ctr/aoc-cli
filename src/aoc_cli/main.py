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
        part_2: Annotated[int, Option(
            help='Whether to pull part 2. This appends \'/part_2\' to default path.', )] = False,
        path: Annotated[str, Option(
            help='Path where task will be stored,'
            ' default is \'./year_<year>/day_<day>\'')] = None,
        session: Annotated[str, Option(
            help='Session cookie to use with request',
            envvar='AOC_CLI_SESSION')] = None):
    '''
    Pulls a task from adventofcode.com
    '''

    if path is None:
        path = os.path.join(os.path.curdir, f'year_{year}', f'day_{day}')

    os.makedirs(path, exist_ok=True)

    aoc_api.pull_task(year, day, path, part_2=part_2, session=SESSION)
    if part_2:
        print(os.path.abspath(path))
    else:
        print(os.path.abspath(path))


@app.command()
def run(
        command: Annotated[str, Argument(
            help='Command to run to get result',
            envvar='AOC_CLI_COMMAND')],
        input_file: Annotated[str, Option(
            '--input',
            help='Path to input file')] = os.path.join(os.curdir, 'test'),
        no_print: Annotated[bool, Option(
            hidden=True)] = False):
    '''
    Run code with input file.
    '''
    args = list()
    if COMMAND_PREFIX is not None:
        [args.append(i) for i in COMMAND_PREFIX.split()]
    [args.append(i) for i in command.split()]
    args.append(input_file)

    completed = subprocess.run(args, text=True, capture_output=True)
    if completed.returncode != 0:
        print(f'[{" ".join(args)}] has exited with code {completed.returncode}')
        print(completed.stderr)
        exit(1)

    stdout = completed.stdout.split('\n')[:-1]
    result = stdout[-1]
    if not no_print:
        if len(stdout) > 1:
            print('Complete stdout:')
            print('\n'.join([f'  {i}' for i in stdout]))
        print(f'Result: {result}')
    return result, stdout


@app.command()
def test(
        expected: Annotated[str, Argument(
            help='Expected value')],
        command: Annotated[str, Argument(
            help='Command to run to get result',
            envvar='AOC_CLI_COMMAND')],
        input_file: Annotated[str, Option(
            '--input',
            help='Path to input file')] = os.path.join(os.curdir, 'test'),):
    '''
    Run code with input file and test agains expected value.
    '''

    expected = expected.strip()
    actual, stdout = run(command, input_file=input_file, no_print=True)
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


@app.command()
def submit(
        command: Annotated[str, Argument(
            help='Command to run to get result',
            envvar='AOC_CLI_COMMAND')],
        input_file: Annotated[str, Option(
            '--input',
            help='Path to input file')] = os.path.join(os.curdir, 'input'),
        year: Annotated[int, Option(
            help='Year to pull task for',
            callback=get_year)] = None,
        day: Annotated[int, Option(
            help='Day to pull task for',
            callback=get_day)] = None,
        part_2: Annotated[bool, Option(
            help='Whether to submit part 2.')] = False,
        session: Annotated[str, Option(
            help='Session cookie to submit result',
            envvar='AOC_CLI_SESSION')] = None):
    '''
    Run code, get results and submit it.
    '''

    result, _ = run(command=command, input_file=input_file, no_print=True)
    print(f'Submitting result: {result}')

    passed = aoc_api.submit(year, day, result, session, part_2=part_2)
    if not passed:
        print('Passed [bold red]:cross_mark:[/bold red]')
    else:
        print('Passed [bold yellow]*[/bold yellow]', end='')
        if part_2:
            print('[bold yellow]*[/bold yellow]')
        else:
            print()
            print(f'Run [italic]aoc-cli pull --year {year} --day {day} --part-2 --path \'.\'[/italic]?')
            print('This will repull the same task in attempt to get part 2.', end=' ')
            proceed = input('Proceed? (Y/n) ')
            if not proceed.lower().startswith('n'):
                pull(year=year, day=day, session=session, part_2=True, path='.')


if __name__ == '__main__':
    app()
