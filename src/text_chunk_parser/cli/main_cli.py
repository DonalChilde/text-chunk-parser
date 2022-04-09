"""Console script entry point for text_chunk_parser."""


from logging import Logger

import click

from ..cli.file_hash_cli import hash_, validate_
from .cli_app import App

logger = logger = Logger(__name__)


@click.group()
@click.option("-v", "--verbose", count=True)
@click.pass_context
def main(ctx: click.Context, verbose):
    """Console script for text_chunk_parser."""
    # NOTE: as written, this code only runs when hello is called,
    # not when <entry point> --help is called. This is a group to
    # hold other commands and groups.
    init_ctx_obj(ctx, verbose)
    # Hello message
    # TODO make an About message
    click.echo("Cli Program v1.0")
    # click.echo(args)
    click.echo("See click documentation at https://click.palletsprojects.com/")
    logger.error("Just checking!")
    return 0


def init_ctx_obj(context: click.Context, verbose):
    """Init the context.obj custom object."""
    context.obj = App({}, verbose)
    context.obj.config = {"key": "oh so important"}


main.add_command(hash_)
main.add_command(validate_)
