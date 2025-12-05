import typer
from rich.console import Console
from rich.table import Table
from datetime import datetime

app = typer.Typer()
console = Console()

@app.command()
def add(type: str, category: str, amount: float, description: str):
    """Add a new transaction (income or expense)."""
    try:
        with open("database/transactions.txt", "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp},{type},{category},{amount},{description}\n")
        console.print(f"Added {type}: {description} ({amount})")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def list():
    """List all transactions."""
    try:
        with open("database/transactions.txt", "r") as f:
            table = Table(title="Transactions")
            table.add_column("Timestamp")
            table.add_column("Type")
            table.add_column("Category")
            table.add_column("Amount")
            table.add_column("Description")

            for line in f:
                timestamp, type, category, amount, description = line.strip().split(",")
                table.add_row(timestamp, type, category, amount, description)
            
            console.print(table)
    except FileNotFoundError:
        console.print("[bold yellow]No transactions found.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    app()
