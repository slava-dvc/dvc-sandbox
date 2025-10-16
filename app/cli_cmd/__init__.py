import typer

app = typer.Typer()

from . import pubsub


@app.command()
def main():
    """
    Just say hello
    """
    print("Hello, Typer!")