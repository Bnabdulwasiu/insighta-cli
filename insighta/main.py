import typer

app = typer.Typer()

@app.command()
def login():
    """Authenticate with GitHub"""
    typer.echo("Login flow — coming soon")

if __name__ == "__main__":
    app()