import typer
from rich.console import Console
from rich.table import Table
from datetime import datetime
import questionary
import uuid

app = typer.Typer()
console = Console()

@app.command()
def add(type: str, category: str, amount: float, description: str, date: str = typer.Option(None, help="Date of the transaction in YYYY-MM-DD format.")):
    """Add a new transaction (income or expense)."""
    if amount <= 0:
        console.print("[bold red]Error:[/bold red] Amount must be positive.")
        raise typer.Exit()

    try:
        with open("database/transactions.txt", "a") as f:
            transaction_id = uuid.uuid4()
            if date:
                try:
                    timestamp = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    console.print("[bold red]Error:[/bold red] Invalid date format. Please use YYYY-MM-DD.")
                    raise typer.Exit()
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            amount_paisa = int(amount * 100)
            f.write(f"{transaction_id},{timestamp},{type},{category},{amount_paisa},{description}\n")
        console.print(f"Added {type}: {description} ({amount:.2f})")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def list(last_days: int = typer.Option(None, help="List transactions from the last N days."),
         type_filter: str = typer.Option(None, help="Filter by transaction type (income or expense).")):
    """List all transactions."""
    try:
        with open("database/transactions.txt", "r") as f:
            lines = f.readlines()

        table = Table(title="Transactions")
        table.add_column("ID")
        table.add_column("Timestamp")
        table.add_column("Type")
        table.add_column("Category")
        table.add_column("Amount")
        table.add_column("Description")

        transactions = []
        for line in lines:
            id, timestamp, type, category, amount_paisa, description = line.strip().split(",")
            transactions.append((id, timestamp, type, category, int(amount_paisa), description))

        # Sort by date
        transactions.sort(key=lambda t: t[1], reverse=True)

        now = datetime.now()

        for id, timestamp, type, category, amount_paisa, description in transactions:
            
            # Filtering
            if last_days:
                transaction_date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                if (now - transaction_date).days > last_days:
                    continue
            
            if type_filter and type_filter.lower() != type.lower():
                continue

            amount = amount_paisa / 100
            color = "green" if type == "income" else "red"
            table.add_row(id, timestamp, type, category, f"[{color}]{amount:.2f}[/{color}]", description)
        
        console.print(table)
    except FileNotFoundError:
        console.print("[bold yellow]No transactions found.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def delete(transaction_id: str):
    """Delete a transaction by its ID."""
    try:
        with open("database/transactions.txt", "r") as f:
            lines = f.readlines()

        transaction_to_delete = None
        for line in lines:
            if line.startswith(transaction_id):
                transaction_to_delete = line
                break

        if transaction_to_delete is None:
            console.print(f"[bold yellow]Transaction {transaction_id} not found.[/bold yellow]")
            return

        _, timestamp, type, category, amount_paisa, description = transaction_to_delete.strip().split(',')
        amount = int(amount_paisa) / 100
        
        confirm = questionary.confirm(f"Are you sure you want to delete this transaction?\n"
                                      f"ID: {transaction_id}\n"
                                      f"Timestamp: {timestamp}\n"
                                      f"Type: {type}\n"
                                      f"Category: {category}\n"
                                      f"Amount: {amount:.2f}\n"
                                      f"Description: {description}").ask()

        if confirm:
            with open("database/transactions.txt", "w") as f:
                for line in lines:
                    if not line.startswith(transaction_id):
                        f.write(line)
            console.print(f"Deleted transaction {transaction_id}")
        else:
            console.print("Deletion cancelled.")

    except FileNotFoundError:
        console.print("[bold yellow]No transactions found.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    app()

@app.command()
def balance():
    """Display the current balance for the current month."""
    try:
        with open("database/transactions.txt", "r") as f:
            lines = f.readlines()

        total_income = 0
        total_expense = 0
        now = datetime.now()

        for line in lines:
            _, timestamp, type, _, amount_paisa, _ = line.strip().split(",")
            transaction_date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

            if transaction_date.year == now.year and transaction_date.month == now.month:
                if type == "income":
                    total_income += int(amount_paisa)
                else:
                    total_expense += int(amount_paisa)

        balance = total_income - total_expense
        
        total_income /= 100
        total_expense /= 100
        balance /= 100

        console.print(f"Total Income: [green]{total_income:.2f}[/green]")
        console.print(f"Total Expense: [red]{total_expense:.2f}[/red]")
        
        balance_color = "green" if balance >= 0 else "red"
        console.print(f"Balance: [{balance_color}]{balance:.2f}[/{balance_color}]")

    except FileNotFoundError:
        console.print("[bold yellow]No transactions found.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
