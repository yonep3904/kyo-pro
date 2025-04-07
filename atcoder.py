import sys
import os
# Add packages directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "packages"))

import re
from datetime import datetime, timedelta
import requests
import string
import json
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Callable, Iterable

import questionary
from bs4 import BeautifulSoup

URL = 'https://atcoder.jp/'
DIR = Path(__file__).resolve().parent

# Load config
with open(DIR / 'config.yml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)['atcoder']

if str(config['save_dir']).startswith('./'):
    PROBLEM_DIR = DIR / str(config['save_dir']).lstrip('./')
elif str(config['save_dir']).startswith('/'):
    PROBLEM_DIR = Path(str(config['save_dir']))
else:
    raise ValueError(f'Invalid save_dir: {config["save_dir"]}')

TEMPLATE_CODE = {}
for ext in config['templates']:
    ext = str(ext).lstrip('.')
    with open(DIR / 'templates' / f'template.{ext}', 'r', encoding='utf-8') as f:
        TEMPLATE_CODE[ext] = f.read()

PROBLEM_LEVEL = str(config['problem_level']).lower()

def get_start(text: str) -> datetime:
    """Get start datetime from start string."""

    # 2025-04-06 21:00:00+0900
    start_pattern = re.compile(r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})([+-]\d{4})')

    if hit := start_pattern.fullmatch(text):
        year, month, day, hour, minute, second, timezone = map(int, hit.groups())
        return datetime(year, month, day, hour, minute, second)
    else:
        raise ValueError(f'Invalid start format: {text}')

def get_link(text: str) -> str:
    """Get link from text."""

    global URL
    return URL + text.lstrip('/')

def get_category_number(name: str) -> tuple[str, int]:
    """Get category and number from contest name."""

    category_patterns = [
        ('ABC', re.compile(r'AtCoder Beginner Contest (\d{3})')),
        ('ARC', re.compile(r'AtCoder Regular Contest (\d{3})')),
        ('AGC', re.compile(r'AtCoder Grand Contest (\d{3})')),
        ('AHC', re.compile(r'AtCoder Heuristic Contest (\d{3})')),
    ]

    for category, pattern in category_patterns:
        if hit := pattern.search(name):
            return category, int(hit.group(1))
    else:
        return 'other', None

def get_duration(text: str) -> timedelta:
    """Get duration from duration string."""

    # 01:40 | 240:00
    duration_pattern = re.compile(r'(\d{2,3}):(\d{2})')

    if hit := duration_pattern.fullmatch(text):
        hour, minute = map(int, hit.groups())
        return timedelta(hours=hour, minutes=minute)
    else:
        raise ValueError(f'Invalid duration format: {text}')

def get_rated(text: str) -> tuple[str, int | None, int | None]:
    """Get rated from rated string."""

    # - | all | 2000 ~ | ~ 1999 | 1200 ~ 2399
    rated_patterns = [
        ('none', re.compile(r'-')),
        ('all', re.compile(r'All')),
        ('upper', re.compile(r'(\d{3,4}) ~ ')),
        ('lower', re.compile(r' ~ (\d{3,4})')),
        ('both', re.compile(r'(\d{3,4}) ~ (\d{3,4})')),
    ]

    for rated, pattern in rated_patterns:
        if hit := pattern.fullmatch(text):
            match rated:
                case 'none':
                    return rated, None, None
                case 'all':
                    return rated, None, None
                case 'upper':
                    return rated, int(hit.group(1)), None
                case 'lower':
                    return rated, None, int(hit.group(1))
                case 'both':
                    return rated, int(hit.group(1)), int(hit.group(2))
    else:
        raise ValueError(f'Invalid rated format: {text}')


@dataclass(frozen=True)
class Contest:
    status: str
    category: str
    number: int | None
    name: str
    start: datetime
    duration: timedelta
    rated: str
    link: str

    def __str__(self) -> str:
        return f'{self.status}: {self.category} {self.number} {self.name} {self.start} {self.duration} {self.rated} {self.link}'

    def json_text(self) -> str:
        """Get contest info in JSON format."""

        return json.dumps({
            'status': self.status,
            'category': self.category,
            'number': self.number,
            'name': self.name,
            'start': self.start.isoformat(),
            'duration': str(self.duration),
            'rated': {
                'type': self.rated[0],
                'from': self.rated[1],
                'to': self.rated[2],
            },
            'link': self.link,
        }, ensure_ascii=False, indent=4)

    def code_info(self, ext: str) -> str:
        """Get contest info in code comment format."""

        symbol_dict = {
            'c': '//',
            'cpp': '//',
            'java': '//',
            'go': '//',
            'rs': '//',
            'js': '//',
            'ts': '//',
            'py': '#',
            'rb': '#',
        }
        symbol = symbol_dict.get(ext, '//')
        return '\n'.join([
            f'{symbol} Contest Name: {self.name}',
            f'{symbol} Start at: {self.start.isoformat()}',
            f'{symbol} Duration: {self.duration}',
            f'{symbol} Link: {self.link}',
            ]) + '\n'

    def dir_name(self) -> str:
        """Get directory name for contest."""
        if self.category == 'other':
            return self.name
        else:
            # return f'{self.start.strftime("%y%m%d")}_{self.category.lower()}{self.number:03}'
            return f'{self.category.lower()}{self.number:03}'

    def display(self) -> str:
        status_dict = {
            'action': '開催',
            'permanent': '常設',
            'upcoming': '予定',
            'recent': '終了',
        }

        return f'{status_dict[self.status]} {self.start.strftime("%m/%d %H:%M")} {self.name}'

    def make_dir(self) -> Path:
        """Make directory for contest."""

        global PROBLEM_DIR, PROBLEM_LEVEL

        dir = PROBLEM_DIR / self.dir_name()
        dir.mkdir(parents=True, exist_ok=False)

        alphabet = string.ascii_lowercase
        problems = alphabet[:alphabet.index(PROBLEM_LEVEL) + 1]
        for problem in problems:

            for ext, code in TEMPLATE_CODE.items():
                with open(dir / f'problem_{problem}.{ext}', 'w', encoding='utf-8') as f:
                    f.write(self.code_info(ext))
                    f.write('\n')
                    f.write(code)

        with open(dir / f'info.json', 'w', encoding='utf-8') as f:
            f.write(self.json_text())
            f.write('\n')

        return dir

class ContestList:
    def __init__(self) -> None:
        self.contests: list[Contest] = []

    def add(self, contest: Contest) -> None:
        self.contests.append(contest)

    def sort(self, key:Callable =lambda x: x.start) -> None:
        self.contests.sort(key=key)

    def __iter__(self) -> Iterable[Contest]:
        return iter(self.contests)

    def __len__(self) -> int:
        return len(self.contests)

    def __getitem__(self, index) -> Contest:
        return self.contests[index]

    def __setitem__(self, index, value) -> None:
        self.contests[index] = value

    def print(self) -> None:
        for contest in self.contests:
            print(contest.display())

    def ask(self) -> int:
        """Get contest number from questionary."""
        return questionary.select(
            f'Select contest',
            choices=[questionary.Choice(title=contest.display(), value=i) for i, contest in enumerate(self.contests)],
            use_shortcuts=True,
            qmark='?',
        ).ask()


def parse(html: str) -> ContestList:
    statuses = [
        ('action', 'contest-table-action', '開催'),
        # ('permanent', 'contest-table-permanent', '常設'),
        ('upcoming', 'contest-table-upcoming', '予定'),
        # ('recent', 'contest-table-recent', '終了'),
    ]

    contests = ContestList()
    soup = BeautifulSoup(html, 'html.parser')

    # <tr>
    #     <td class="text-center"><a href='http://www.timeanddate.com/worldclock/fixedtime.html?iso=20250406T2100&p1=248' target='blank'><time class='fixtime fixtime-full'>2025-04-06 21:00:00+0900</time></a></td>
    #     <td >
    #         <span aria-hidden='true' data-toggle='tooltip' data-placement='top' title="Algorithm">Ⓐ</span>
    #         <span class="user-red">◉</span>
    #         <a href="/contests/arc196">AtCoder Regular Contest 196 (Div. 1)</a>
    #     </td>
    #     <td class="text-center">02:30</td>
    #     <td class="text-center">1600 ~ 2999</td>
    # </tr>

    for stats, id_name, _ in statuses:
        category = soup.find(id=id_name)
        if category is None:
            continue

        table = category.find('table').find('tbody')
        for row in table.find_all('tr'):
            cols = row.find_all('td')

            start = get_start(cols[0].find('a').find('time').text)
            link = get_link(cols[1].find('a').get('href'))
            name = cols[1].find('a').text
            category, number = get_category_number(name)
            duration = get_duration(cols[2].text)
            rated = get_rated(cols[3].text)

            contests.add(
                Contest(
                    status=stats,
                    category=category,
                    number=number,
                    name=name,
                    start=start,
                    duration=duration,
                    rated=rated,
                    link=link,
                )
            )
    return contests

def main() -> None:
    global URL

    res = requests.get(
        URL + 'contests/',
        headers={
            'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7'
        },
    )
    if res.status_code != 200:
        raise Exception(f'Failed to get {URL}')

    contests = parse(res.text)
    contests.sort(key=lambda x: x.start)

    contest_num = contests.ask()
    if contest_num is None:
        print('No contest selected.')
        return
    else:
        contest = contests[contest_num]
        print(f'Contest selected: {contest.make_dir()}')

if __name__ == '__main__':
    main()
