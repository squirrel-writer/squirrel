from rich.panel import Panel
from rich.columns import Columns

from ..vars import console, logger
from ..vars import squirrel_art
from ..xml import get_data_from_project_file

def overview(args):

    data = get_data_from_project_file()
    logger.debug(data)

    texts = [
        f'[cyan bold underline]{data["name"]}[/]',
        f'[italic]{data["description"]}[/]',
        f'[hot_pink3]Goal:[/] 0/{data["goal"]}',
        f'[hot_pink3]Due Data:[/] {data["due-date"]}',
        f'[hot_pink3]Project Type:[/] {data["project-type"]}',
    ]

    console.print(Columns([squirrel_art, Panel('\n'.join(texts))]))
