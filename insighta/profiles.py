import typer
from typing import Optional

from insighta.api import request
from insighta.display import (
    print_profiles_table, print_profile_detail,
    print_error, print_success, print_pagination, console
)

app = typer.Typer()


@app.command("list")
def list_profiles(
    gender: Optional[str] = typer.Option(None, "--gender"),
    country: Optional[str] = typer.Option(None, "--country"),
    age_group: Optional[str] = typer.Option(None, "--age-group"),
    min_age: Optional[int] = typer.Option(None, "--min-age"),
    max_age: Optional[int] = typer.Option(None, "--max-age"),
    sort_by: Optional[str] = typer.Option(None, "--sort-by"),
    order: Optional[str] = typer.Option("asc", "--order"),
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(10, "--limit"),
):
    """List profiles with optional filters."""
    params = {"page": page, "limit": limit, "order": order}
    if gender:
        params["gender"] = gender
    if country:
        params["country_id"] = country
    if age_group:
        params["age_group"] = age_group
    if min_age is not None:
        params["min_age"] = min_age
    if max_age is not None:
        params["max_age"] = max_age
    if sort_by:
        params["sort_by"] = sort_by

    with console.status("[cyan]Fetching profiles...[/cyan]"):
        res = request("GET", "/api/profiles", params=params)

    if res.status_code != 200:
        print_error(res.json().get("message", "Failed to fetch profiles."))
        raise typer.Exit(1)

    data = res.json()
    print_profiles_table(data["data"])
    print_pagination(data["page"], data["total_pages"], data["total"])


@app.command("get")
def get_profile(profile_id: str = typer.Argument(..., help="Profile UUID")):
    """Get a single profile by ID."""
    with console.status("[cyan]Fetching profile...[/cyan]"):
        res = request("GET", f"/api/profiles/{profile_id}")

    if res.status_code == 404:
        print_error("Profile not found.")
        raise typer.Exit(1)
    if res.status_code != 200:
        print_error(res.json().get("message", "Failed to fetch profile."))
        raise typer.Exit(1)

    print_profile_detail(res.json()["data"])


@app.command("search")
def search_profiles(
    query: str = typer.Argument(..., help='e.g. "young males from nigeria"'),
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(10, "--limit"),
):
    """Search profiles using natural language."""
    with console.status("[cyan]Searching...[/cyan]"):
        res = request("GET", "/api/profiles/search", params={
            "q": query, "page": page, "limit": limit
        })

    if res.status_code != 200:
        print_error(res.json().get("message", "Search failed."))
        raise typer.Exit(1)

    data = res.json()
    print_profiles_table(data["data"])
    print_pagination(data["page"], data["total_pages"], data["total"])


@app.command("create")
def create_profile(
    name: str = typer.Option(..., "--name", help="Full name to create profile for"),
):
    """Create a new profile (admin only)."""
    with console.status(f"[cyan]Creating profile for {name}...[/cyan]"):
        res = request("POST", "/api/profiles", json={"name": name})

    if res.status_code in (200, 201):
        data = res.json()
        print_success(
            f"Profile {'created' if res.status_code == 201 else 'already exists'}: "
            f"{data['data']['name']}"
        )
        print_profile_detail(data["data"])
    else:
        print_error(res.json().get("message", "Failed to create profile."))
        raise typer.Exit(1)


@app.command("export")
def export_profiles(
    format: str = typer.Option("csv", "--format"),
    gender: Optional[str] = typer.Option(None, "--gender"),
    country: Optional[str] = typer.Option(None, "--country"),
    age_group: Optional[str] = typer.Option(None, "--age-group"),
):
    """Export profiles to CSV."""
    params = {"format": format}
    if gender:
        params["gender"] = gender
    if country:
        params["country_id"] = country
    if age_group:
        params["age_group"] = age_group

    with console.status("[cyan]Exporting profiles...[/cyan]"):
        res = request("GET", "/api/profiles/export", params=params)

    if res.status_code != 200:
        print_error("Export failed.")
        raise typer.Exit(1)

    from datetime import datetime
    filename = f"profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, "w") as f:
        f.write(res.text)

    print_success(f"Exported to {filename}")