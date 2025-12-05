import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

@app.command()
def add(category: str, amount: float):
    """Add a new budget for a category."""
    try:
        with open("database/budgets.txt", "a") as f:
            f.write(f"{category},{amount}\n")
        console.print(f"Added budget for {category}: {amount}")
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
                category, amount = line.strip().split(",")
                table.add_row(category, amount)
            
            console.print(table)
    except FileNotFoundError:
        console.print("[bold yellow]No budgets found.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    app()
