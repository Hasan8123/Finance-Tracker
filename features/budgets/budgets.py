import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

@app.command()
def add(category: str, amount: float):
    """Add or update a new budget for a category."""
    if amount <= 0:
        console.print("[bold red]Error:[/bold red] Amount must be positive.")
        raise typer.Exit()
    try:
        budgets = {}
        try:
            with open("database/budgets.txt", "r") as f:
                for line in f:
                    cat, amt_paisa = line.strip().split(",")
                    budgets[cat] = int(amt_paisa)
        except FileNotFoundError:
            pass # File will be created if it doesn't exist

        amount_paisa = int(amount * 100)
        budgets[category] = amount_paisa

        with open("database/budgets.txt", "w") as f:
            for cat, amt_paisa in budgets.items():
                f.write(f"{cat},{amt_paisa}\n")
        console.print(f"Set budget for {category}: {amount:.2f}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

import typer
from rich.console import Console
from rich.table import Table
from datetime import datetime

app = typer.Typer()
console = Console()

@app.command()
def add(category: str, amount: float):
    """Add or update a new budget for a category."""
    if amount <= 0:
        console.print("[bold red]Error:[/bold red] Amount must be positive.")
        raise typer.Exit()
    try:
        budgets = {}
        try:
            with open("database/budgets.txt", "r") as f:
                for line in f:
                    cat, amt_paisa = line.strip().split(",")
                    budgets[cat] = int(amt_paisa)
        except FileNotFoundError:
            pass # File will be created if it doesn't exist

        amount_paisa = int(amount * 100)
        budgets[category] = amount_paisa

        with open("database/budgets.txt", "w") as f:
            for cat, amt_paisa in budgets.items():
                f.write(f"{cat},{amt_paisa}\n")
        console.print(f"Set budget for {category}: {amount:.2f}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def list():
    """List all budgets."""
    try:
        # Read budgets
        budgets_data = {}
        with open("database/budgets.txt", "r") as f:
            for line in f:
                category, budget_paisa = line.strip().split(",")
                budgets_data[category] = int(budget_paisa)

        # Read transactions and calculate expenses for current month
        expenses_data = {}
        total_spent_paisa_month = 0
        now = datetime.now()

        try:
            with open("database/transactions.txt", "r") as f:
                for line in f:
                    try:
                        _, timestamp_str, type, category, amount_paisa, _ = line.strip().split(",", 5)
                        transaction_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

                        if transaction_date.year == now.year and transaction_date.month == now.month:
                            if type == "expense":
                                spent_paisa = int(amount_paisa)
                                expenses_data[category] = expenses_data.get(category, 0) + spent_paisa
                                total_spent_paisa_month += spent_paisa
                    except ValueError:
                        console.print(f"[bold yellow]Skipping malformed transaction line: {line.strip()}[/bold yellow]")
        except FileNotFoundError:
            pass # No transactions yet

        # Prepare table
        table = Table(title="Monthly Budgets Overview")
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Budget", style="magenta")
        table.add_column("Spent", style="yellow")
        table.add_column("Remaining", style="green")
        table.add_column("Utilization", justify="right")
        table.add_column("Status", style="white")

        total_budget_paisa_month = sum(budgets_data.values())
        overall_utilization = 0

        for category, budget_paisa in budgets_data.items():
            spent_paisa = expenses_data.get(category, 0)
            remaining_paisa = budget_paisa - spent_paisa

            budget = budget_paisa / 100
            spent = spent_paisa / 100
            remaining = remaining_paisa / 100

            utilization_percent = (spent_paisa / budget_paisa * 100) if budget_paisa > 0 else 0

            if utilization_percent < 70:
                status_color = "green"
                status_text = "OK"
            elif utilization_percent <= 100:
                status_color = "yellow"
                status_text = "Warning"
            else:
                status_color = "red"
                status_text = "Over"
            
            utilization_str = f"[{status_color}]{utilization_percent:.2f}%[/{status_color}]"

            table.add_row(
                category,
                f"{budget:.2f}",
                f"{spent:.2f}",
                f"{remaining:.2f}",
                utilization_str,
                f"[{status_color}]{status_text}[/{status_color}]"
            )

        console.print(table)

        # Overall Summary
        console.print("\n[bold]Overall Monthly Summary:[/bold]")
        console.print(f"Total Budget: [magenta]{total_budget_paisa_month / 100:.2f}[/magenta]")
        console.print(f"Total Spent: [yellow]{total_spent_paisa_month / 100:.2f}[/yellow]")
        
        overall_remaining_paisa = total_budget_paisa_month - total_spent_paisa_month
        overall_remaining_color = "green" if overall_remaining_paisa >= 0 else "red"
        console.print(f"Total Remaining: [{overall_remaining_color}]{overall_remaining_paisa / 100:.2f}[/{overall_remaining_color}]")

        if total_budget_paisa_month > 0:
            overall_utilization = (total_spent_paisa_month / total_budget_paisa_month) * 100
        
        overall_util_color = "green"
        if overall_utilization >= 70 and overall_utilization <= 100:
            overall_util_color = "yellow"
        elif overall_utilization > 100:
            overall_util_color = "red"
        
        console.print(f"Overall Utilization: [{overall_util_color}]{overall_utilization:.2f}%[/{overall_util_color}]")


    except FileNotFoundError:
        console.print("[bold yellow]No budgets found. Please add some budgets first.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
