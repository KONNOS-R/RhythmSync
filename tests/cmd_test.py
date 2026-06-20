#print("meow")

import typer

app = typer.Typer(help="help")

@app.command()
def meow(yes: bool = typer.Option(False, "-y", "-Y"),
        no: bool = typer.Option(False, "-n", "-N")
        ):
    """meow meow meow"""

    if yes:
        print("meow :3")
    elif no:
        print("no meow :(")
    else:
        print("grrr")


if __name__ == "__main__":
    app()