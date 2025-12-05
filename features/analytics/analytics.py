import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

@app.command()
def report():
    """Generate a report of expenses by category and compare with budget."""
    try:
        # Read budgets
        budgets = {}
        with open("database/budgets.txt", "r") as f:
            for line in f:
                category, amount = line.strip().split(",")
                budgets[category] = float(amount)

        # Read transactions and calculate expenses
        expenses = {}
        with open("database/transactions.txt", "r") as f:
            for line in f:
                _, type, category, amount, _ = line.strip().split(",")
                if type == "expense":
                    if category in expenses:
                        expenses[category] += float(amount)
                    else:
                        expenses[category] = float(amount)

        # Generate report
        table = Table(title="Expense Report")
        table.add_column("Category")
        table.add_column("Budget")
        table.add_column("Spent")
        table.add_column("Remaining")

        for category, budget in budgets.items():
            spent = expenses.get(category, 0.0)
            remaining = budget - spent
            table.add_row(category, str(budget), str(spent), str(remaining))

        console.print(table)

    except FileNotFoundError:
        console.print("[bold yellow]No budgets or transactions found.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    app()
