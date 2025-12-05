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
                category, amount_paisa = line.strip().split(",")
                budgets[category] = int(amount_paisa)

        # Read transactions and calculate expenses
        expenses = {}
        with open("database/transactions.txt", "r") as f:
            for line in f:
                _, _, type, category, amount_paisa, _ = line.strip().split(",")
                if type == "expense":
                    if category in expenses:
                        expenses[category] += int(amount_paisa)
                    else:
                        expenses[category] = int(amount_paisa)

        # Generate report
        table = Table(title="Expense Report")
        table.add_column("Category")
        table.add_column("Budget")
        table.add_column("Spent")
        table.add_column("Remaining")

        for category, budget_paisa in budgets.items():
            spent_paisa = expenses.get(category, 0)
            remaining_paisa = budget_paisa - spent_paisa
            
            budget = budget_paisa / 100
            spent = spent_paisa / 100
            remaining = remaining_paisa / 100

            table.add_row(category, f"{budget:.2f}", f"{spent:.2f}", f"{remaining:.2f}")

        console.print(table)

    except FileNotFoundError:
        console.print("[bold yellow]No budgets or transactions found.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    app()
