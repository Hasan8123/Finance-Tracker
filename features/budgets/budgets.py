import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

@app.command()
def add(category: str, amount: float):
    """Add a new budget for a category."""
    if amount <= 0:
        console.print("[bold red]Error:[/bold red] Amount must be positive.")
        raise typer.Exit()
    try:
        with open("database/budgets.txt", "a") as f:
            amount_paisa = int(amount * 100)
            f.write(f"{category},{amount_paisa}\n")
        console.print(f"Added budget for {category}: {amount:.2f}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def list():
    """List all budgets."""
    try:
        with open("database/budgets.txt", "r") as f:
            table = Table(title="Budgets")
            table.add_column("Category")
            table.add_column("Amount")

            for line in f:
                category, amount_paisa = line.strip().split(",")
                amount = int(amount_paisa) / 100
                table.add_row(category, f"{amount:.2f}")
            
            console.print(table)
    except FileNotFoundError:
        console.print("[bold yellow]No budgets found.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    app()
