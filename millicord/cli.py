import click
import traceback

from millicord.idol_builder import IdolBuilder
from millicord.idol import generate_idol_folder
from millicord import modules as M


@click.group()
def cmd():
    pass


@cmd.command()
@click.option("--debug", help="debug mode", is_flag=True)
@click.argument("folder", type=click.Path(exists=True))
def launch(debug, folder):
    try:
        IdolBuilder.load_from_folder(folder).build_and_run()
    except KeyboardInterrupt:
        if debug:
            click.echo(traceback.format_exc())
        click.echo('Terminated.')


@cmd.command()
@click.option("--debug", help="debug mode", is_flag=True)
@click.option(
    "--force",
    "-f",
    help="Force create (overwrite if exists).",
    is_flag=True)
@click.argument("folder", type=click.Path())
@click.argument("token")
@click.argument("modules", nargs=-1)
def generate_template(debug, force, folder, token, modules):
    try:
        generate_idol_folder(
            path=folder,
            token=token,
            module_list=[getattr(M, m) for m in modules],
            overwrite=force)
        print("Idol creation done!")
    except FileExistsError:
        click.echo(f"ERROR: Path {folder} exists.")
    except KeyboardInterrupt:
        if debug:
            click.echo(traceback.format_exc())
        click.echo('Terminated.')

@cmd.command()
@click.option("-a", "--all", help="Show all modules.", is_flag=True)
@click.option("-d", "--detail", help="Show detailed description.", is_flag=True)
def list_modules(all, detail):


def main():
    cmd()


if __name__ == "__main__":
    main()
