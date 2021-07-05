import asyncio
import random

import click

from api.models import User


def run_async(coro):
    asyncio.run(coro)


@click.group()
def cli():
    ...


async def _adduser(**kwargs):
    try:
        pass
    except Exception as e:
        print(e)
        click.echo(str(e))
    else:
        click.echo(f'User {1} created!!! ID: {2}')


async def fake_user(**kwargs):
    """
    制造用户新增数和第二天用户留存
    Args:
        **kwargs:

    Returns:

    """
    try:
        while 1:
            result = await User.rank_register_or_login()
            await asyncio.sleep(random.randrange(1, 20))
            click.echo(str(result))
    except Exception as e:
        click.echo(str(e))


@cli.command()
@click.option('--name', required=True, prompt=True)
@click.option('--email', required=False, default=None, prompt=True)
@click.option('--password', required=True, prompt=True, hide_input=True,
              confirmation_prompt=True)
def export_data(name, email, password):
    run_async(_adduser(name=name, password=password, email=email))


@cli.command()
def rank_data():
    run_async(fake_user())


if __name__ == '__main__':
    cli()
