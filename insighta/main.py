import typer
import sys
from insighta import auth, profiles

app = typer.Typer(help="Insighta Labs+ CLI")

app.add_typer(profiles.app, name="profiles")
app.command()(auth.login)
app.command()(auth.logout)
app.command()(auth.whoami)

if __name__ == "__main__":
    try:
        app()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)