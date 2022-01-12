from rich.panel import Panel
from rich.columns import Columns
from datetime import date, timedelta

from ..vars import console, logger
from ..vars import squirrel_art
from ..xml import get_data_from_project_file, get_watches_data


def overview(args):
    logger.debug(args)
    data = get_data_from_project_file()
    watches = get_watches_data()

    if args.graph:
        _barchart(watches)
    else:
        _overview(data, watches)


def _overview(project_data, watches):
    total = 0
    today = 0
    if len(watches):
        _, prev, total = watches[-1]
        today = int(total) - int(prev)

    goal_reached = True if total > project_data['goal'] else False
    total_and_goal = f'{total}/{project_data["goal"]}'
    if goal_reached:
        total_and_goal = f'[green]{total_and_goal}[/]'

    texts = [
        f'[cyan bold underline]{project_data["name"]}[/]',
        f'[italic]{project_data["description"]}[/]',
        f'[hot_pink3]Today:[/] {today}[italic] words[/]',
        f'[hot_pink3]Goal:[/] {total_and_goal}',
        f'[hot_pink3]Due Data:[/] {project_data["due-date"]}',
        f'[hot_pink3]Project Type:[/] {project_data["project-type"]}',
    ]

    console.print(Columns([squirrel_art, Panel('\n'.join(texts))]))


def _barchart(watches):
    def make_dict(watches):
        d = {}
        for watch in watches:
            d[watch[0]] = int(watch[2]) - int(watch[1])
        return d

    def format(stats):
        return '\n'.join([f'• {dates[i]} : {stat} [italic]words[/]' for i, stat in enumerate(stats)])

    def normalize(stats):
        _max = max(stats)
        _min = min(stats)
        for i, j in enumerate(stats):
            stats[i] = int((j - _min) / (_max - _min) * 5)
        return stats

    def plot(stats):
        lines = max(stats)
        output = ''
        line = ''
        for i in reversed(range(1, lines+1)):
            for x, y in enumerate(stats):
                if y == i:
                    stats[x] -= 1
                    line += '[hot_pink2]██[/] '
                else:
                    line += '   '
            line += '\n'
            output += line
            line = ''
        output += '[green]--[/] ' * len(stats)
        return output

    logger.debug(f'_barchart: {watches}')
    watches_d = make_dict(watches)
    today = date.today()
    dates = [(today - timedelta(i)).strftime('%d/%m/%Y')
             for i in reversed(range(0, 5))]
    stats = [watches_d.get(d, 0) for d in dates]

    stats_normalized = normalize(list(stats))
    logger.debug(stats_normalized)
    output = plot(stats_normalized)

    console.print(
        Columns([Panel(output), format(stats)], expand=False, padding=5))
