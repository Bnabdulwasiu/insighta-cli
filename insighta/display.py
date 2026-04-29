from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def print_profiles_table(profiles: list):
    if not profiles:
        console.print("[yellow]No profiles found.[/yellow]")
        return

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Name", style="bold")
    table.add_column("Gender")
    table.add_column("Age")
    table.add_column("Age Group")
    table.add_column("Country")
    table.add_column("ID", style="dim")

    for p in profiles:
        table.add_row(
            p.get("name", ""),
            p.get("gender", ""),
            str(p.get("age", "")),
            p.get("age_group", ""),
            f'{p.get("country_name", "")} ({p.get("country_id", "")})',
            p.get("id", ""),
        )

    console.print(table)


def print_profile_detail(p: dict):
    table = Table(box=box.SIMPLE, show_header=False)
    table.add_column("Field", style="bold cyan")
    table.add_column("Value")

    fields = [
        ("ID", p.get("id")),
        ("Name", p.get("name")),
        ("Gender", p.get("gender")),
        ("Gender Probability", str(p.get("gender_probability"))),
        ("Age", str(p.get("age"))),
        ("Age Group", p.get("age_group")),
        ("Country", f'{p.get("country_name")} ({p.get("country_id")})'),
        ("Country Probability", str(p.get("country_probability"))),
        ("Created At", p.get("created_at")),
    ]
    for field, value in fields:
        table.add_row(field, value or "")

    console.print(table)


def print_error(message: str):
    console.print(f"[red]Error:[/red] {message}")


def print_success(message: str):
    console.print(f"[green]✓[/green] {message}")


def print_pagination(page: int, total_pages: int, total: int):
    console.print(
        f"\n[dim]Page {page} of {total_pages} "
        f"({total} total results)[/dim]"
    )