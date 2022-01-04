from rich.panel import Panel
from rich.columns import Columns

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

    texts = [
        f'[cyan bold underline]{project_data["name"]}[/]',
        f'[italic]{project_data["description"]}[/]',
        f'[hot_pink3]Today:[/] {today}[italic] words[/]',
        f'[hot_pink3]Goal:[/] {total}/{project_data["goal"]}',
        f'[hot_pink3]Due Data:[/] {project_data["due-date"]}',
        f'[hot_pink3]Project Type:[/] {project_data["project-type"]}',
    ]

    console.print(Columns([squirrel_art, Panel('\n'.join(texts))]))


def _barchart(watches):
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
        console.print(Panel(output))

    logger.debug(f'_barchart: {watches}')
    stats = list(map(lambda w: int(w[2]) - int(w[1]), watches[-5:]))
    if len(stats) < 5:
        stats = [8] * (5 - len(stats)) + stats
    stats = normalize(stats)
    logger.debug(stats)
    plot(stats)


