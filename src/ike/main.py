import typer

app = typer.Typer()


@app.command()
def init():
    print("Prepare yourself!")


@app.command()
def dev():
    print("You'll get no sympathy from me")


@app.command()
def deploy():
    print("I fight for my friends")


def main():
    app()


if __name__ == "__main__":
    main()
