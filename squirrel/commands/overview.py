from datetime import date, timedelta

from rich.panel import Panel
from rich.columns import Columns
from rich.console import Console

from ..vars import console, logger
from ..vars import squirrel_art
from ..vars import DEFAULT_DATE_FORMAT
from ..xml import get_data_from_project_file, get_watches_data
from ..exceptions import ProjectNotSetupCorrectlyError


def overview(args):
    logger.debug(args)
    try:
        data = get_data_from_project_file()
    except FileNotFoundError:
        return False

    try:
        watches = get_watches_data()
    except (FileNotFoundError, ProjectNotSetupCorrectlyError) as e:
        console = Console(stderr=True)
        console.print(e)
        return False

    if args.graph:
        _barchart(watches, args.format)
        return True
    else:
        _overview(data, watches, args.format)
        return True
    return False


def _overview(project_data, watches, date_format):
    total = 0
    today = 0
    if len(watches):
        date_count, prev, total = watches[-1]
        today = total - prev if date_count == date.today() else 0

    formatter = Formatter(
        project_data.get('name', None),
        project_data.get('description', None),
        project_data.get('goal', None),
        project_data.get('due-date', None),
        project_data.get('project-type', None),
        total,
        today,
        format=date_format
    )
    logger.debug(project_data)
    console.print(Columns([squirrel_art, Panel(formatter.overview)]))


class Formatter:
    def __init__(self, name, description, goal, due_date, project_type, total, today, format=DEFAULT_DATE_FORMAT):
        self._name = name
        self._description = description
        self._goal = goal
        self._due_date = due_date
        self._project_type = project_type
        self.total = total
        self._today = today
        self.format = format

    @property
    def name(self):
        return f'[cyan bold underline]{self._name}[/]'

    @property
    def description(self):
        return f'[italic]{self._description}[/]'

    @property
    def today(self):
        return f'[hot_pink3]Today:[/] {format(self._today, ",")}[italic] words[/]'

    @property
    def goal(self):
        goal = self._goal
        if self._goal is None:
            goal = 0
        goal_reached = True if self.total > int(goal) else False

        formatted_goal = self._goal
        if self._goal is not None:
            formatted_goal = format(self._goal, ',')
        total_and_goal = f'{format(self.total, ",")}/{formatted_goal}'
        if goal_reached:
            total_and_goal = f'[green]{total_and_goal}[/]'

        return f'[hot_pink3]Goal:[/] {total_and_goal}'

    @property
    def due_date(self):
        due_date_formatted = self._due_date
        if self._due_date is not None:
            dd = self._due_date
            dd_formated = self._due_date.strftime(self.format)
            if date.today() <= dd:
                delta = dd - date.today()
                due_date_formatted = f'{dd_formated} [italic blue]({delta.days} days left)[/]'
            else:
                due_date_formatted = f'[blink red]{dd_formated}[/]'

        return f'[hot_pink3]Due Date:[/] {due_date_formatted}'

    @property
    def project_type(self):
        return f'[hot_pink3]Project Type:[/] {self._project_type}'

    @property
    def overview(self):
        return '\n'.join([
            self.name,
            self.description,
            self.today,
            self.goal,
            self.due_date,
            self.project_type
        ])


def _barchart(watches, date_format):
    def make_dict(watches):
        d = {}
        for watch in watches:
            d[watch[0]] = watch[2] - watch[1]
        return d

    def format_stats(stats):
        return '\n' + '\n'.join([
            f'• {dates[i].strftime(date_format)} : {format(stat, ",")} [italic]words[/]'
            for i, stat in enumerate(stats)
        ])

    def normalize(stats):
        _max = max(stats)
        _min = min(stats)
        if _max == 0:
            return stats

        for i, j in enumerate(stats):
            stats[i] = int((j - _min) / (_max - _min) * 5)
        return stats

    def plot(stats):
        lines = max(stats)
        output = ''
        line = ''
        for i in reversed(range(1, lines + 1)):
            for x, y in enumerate(stats):
                if y == i:
                    stats[x] -= 1
                    line += '[hot_pink2]██[/] '
                else:
                    line += '   '
            line += '\n'
            output += line
            line = ''
        output += '[green]——[/] ' * len(stats)
        return output

    logger.debug(f'_barchart: {watches}')
    watches_d = make_dict(watches)
    today = date.today()
    dates = [today - timedelta(i)
             for i in reversed(range(0, 5))]
    stats = [watches_d.get(d, 0) for d in dates]

    stats_normalized = normalize(list(stats))
    logger.debug(stats_normalized)
    output = plot(stats_normalized)

    console.print(
        Columns([Panel(output), format_stats(stats)], expand=False, padding=5))
