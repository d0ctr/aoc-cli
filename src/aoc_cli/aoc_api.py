import os
import sys
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify


def to_md(text):
    return markdownify(
            text,
            heading_style='ATX',
            bulletts='-',
            strong_em_symbol='*')


def pull_input(year, day, path, session):
    cookies = dict()
    if session is not None:
        cookies['session'] = session

    url = f'https://adventofcode.com/{year}/day/{day}/input'
    response = requests.get(url, cookies=cookies)
    if response.status_code != 200:
        print(
                f'Request to {url} failed with'
                f' status code {response.status_code}:'
                f'\n{response.text}', file=sys.stderr)
        raise RuntimeError(
                f'Request failed with status code: {response.status_code}')
    with open(os.path.join(path, 'input'), 'w', encoding='utf-8') as f:
        f.write(response.text)


def pull_task(year, day, path, session=None):
    '''
    Pull Advent of Code task and save to local files.
    '''
    cookies = dict()
    if session is not None:
        cookies['session'] = session
        pull_input(year, day, path, session)

    url = f'https://adventofcode.com/{year}/day/{day}'
    response = requests.get(url, cookies=cookies)
    if response.status_code != 200:
        print(
                f'Request to {url} failed with'
                f' status code {response.status_code}:'
                f'\n{response.text}', file=sys.stderr)
        raise RuntimeError(
                f'Request failed with status code: {response.status_code}')

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')
    if not articles:
        raise ValueError('No <article> tags found in the response')

    task_1 = to_md(str(articles[0]))

    with open(os.path.join(path, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(task_1)

    if len(articles) > 1:
        task_2 = to_md(str(articles[1]))

        part_2_path = os.path.join(path, 'part_2')
        os.makedirs(part_2_path, exist_ok=True)

        with open(os.path.join(part_2_path, 'README.md'), 'w', encoding='utf-8') as f:
            f.write(task_2)

    test = articles[0].find('pre')
    if test:
        test_text = test.get_text()
        with open(os.path.join(path, 'test'), 'w', encoding='utf-8') as f:
            f.write(test_text)
