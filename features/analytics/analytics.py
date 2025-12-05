import typer
from rich.console import Console
from rich.table import Table
from datetime import datetime, timedelta
import calendar

app = typer.Typer()
console = Console()

def get_month_range(date: datetime):
    first_day = date.replace(day=1)
    last_day = date.replace(day=calendar.monthrange(date.year, date.month)[1])
    return first_day, last_day

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

        # Initialize expense data for current and previous month
        current_month_expenses = {}
        previous_month_expenses = {}
        total_current_month_expense_paisa = 0
        total_previous_month_expense_paisa = 0

        now = datetime.now()
        current_month_start, current_month_end = get_month_range(now)
        
        previous_month_date = now.replace(day=1) - timedelta(days=1)
        previous_month_start, previous_month_end = get_month_range(previous_month_date)


        with open("database/transactions.txt", "r") as f:
            for line in f:
                try:
                    _, timestamp_str, type, category, amount_paisa, _ = line.strip().split(",", 5)
                    transaction_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    amount = int(amount_paisa)

                    if type == "expense":
                        if current_month_start <= transaction_date <= current_month_end:
                            current_month_expenses[category] = current_month_expenses.get(category, 0) + amount
                            total_current_month_expense_paisa += amount
                        elif previous_month_start <= transaction_date <= previous_month_end:
                            previous_month_expenses[category] = previous_month_expenses.get(category, 0) + amount
                            total_previous_month_expense_paisa += amount
                except ValueError:
                    console.print(f"[bold yellow]Skipping malformed transaction line: {line.strip()}[/bold yellow]")
        
        # --- Expense Report Table (existing logic) ---
        table = Table(title="Expense Report (Current Month)")
        table.add_column("Category")
        table.add_column("Budget")
        table.add_column("Spent")
        table.add_column("Remaining")

        for category, budget_paisa in budgets.items():
            spent_paisa = current_month_expenses.get(category, 0)
            remaining_paisa = budget_paisa - spent_paisa
            
            budget = budget_paisa / 100
            spent = spent_paisa / 100
            remaining = remaining_paisa / 100

            table.add_row(category, f"{budget:.2f}", f"{spent:.2f}", f"{remaining:.2f}")

        console.print(table)

        # --- New Spending Analysis Insights ---
        console.print("\n[bold]Spending Analysis (Current Month):[/bold]")

        # Top 3 spending categories
        sorted_current_expenses = sorted(current_month_expenses.items(), key=lambda item: item[1], reverse=True)
        console.print("[bold]Top 3 Spending Categories:[/bold]")
        for i, (category, amount_paisa) in enumerate(sorted_current_expenses[:3]):
            console.print(f"{i+1}. {category}: {amount_paisa / 100:.2f}")
        
        # Average daily expense
        days_in_current_month = (now - current_month_start).days + 1
        if days_in_current_month > 0:
            avg_daily_expense = (total_current_month_expense_paisa / days_in_current_month) / 100
            console.print(f"\n[bold]Average Daily Expense:[/bold] {avg_daily_expense:.2f}")
        else:
            console.print("\n[bold]Average Daily Expense:[/bold] N/A (no days passed in current month)")

        # Comparison with last month
        console.print("\n[bold]Month-over-Month Expense Comparison:[/bold]")
        current_month_total = total_current_month_expense_paisa / 100
        previous_month_total = total_previous_month_expense_paisa / 100
        
        console.print(f"Current Month ({now.strftime('%B')}): {current_month_total:.2f}")
        console.print(f"Previous Month ({previous_month_date.strftime('%B')}): {previous_month_total:.2f}")

        if previous_month_total > 0:
            change_percent = ((current_month_total - previous_month_total) / previous_month_total) * 100
            if change_percent > 0:
                console.print(f"Change: [red]+{change_percent:.2f}%[/red]")
            else:
                console.print(f"Change: [green]{change_percent:.2f}%[/green]")
        else:
            console.print("Change: N/A (no expenses last month)")

        # ASCII Pie Chart
        console.print("\n[bold]Spending by Category (Current Month - Pie Chart):[/bold]")
        if total_current_month_expense_paisa > 0:
            chart_data = []
            for category, amount_paisa in current_month_expenses.items():
                percentage = (amount_paisa / total_current_month_expense_paisa) * 100
                chart_data.append((category, percentage))
            
            # Sort for better visualization
            chart_data.sort(key=lambda item: item[1], reverse=True)

            for category, percentage in chart_data:
                num_blocks = max(1, int(percentage // 5)) # Each block represents 5%
                if percentage > 0 and num_blocks == 0: # Ensure at least one block for non-zero percentages
                    num_blocks = 1
                console.print(f"{category.ljust(12)} {'█' * num_blocks} {percentage:.2f}%")
        else:
            console.print("No expenses recorded this month.")


    except FileNotFoundError:
        console.print("[bold yellow]No budgets or transactions found.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def income_report():
    """Generate a report of income by source and compare with previous month."""
    try:
        current_month_income = {}
        previous_month_income = {}
        total_current_month_income_paisa = 0
        total_previous_month_income_paisa = 0

        now = datetime.now()
        current_month_start, current_month_end = get_month_range(now)
        
        previous_month_date = now.replace(day=1) - timedelta(days=1)
        previous_month_start, previous_month_end = get_month_range(previous_month_date)

        with open("database/transactions.txt", "r") as f:
            for line in f:
                try:
                    _, timestamp_str, type, category, amount_paisa, _ = line.strip().split(",", 5)
                    transaction_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    amount = int(amount_paisa)

                    if type == "income":
                        if current_month_start <= transaction_date <= current_month_end:
                            current_month_income[category] = current_month_income.get(category, 0) + amount
                            total_current_month_income_paisa += amount
                        elif previous_month_start <= transaction_date <= previous_month_end:
                            previous_month_income[category] = previous_month_income.get(category, 0) + amount
                            total_previous_month_income_paisa += amount
                except ValueError:
                    console.print(f"[bold yellow]Skipping malformed transaction line: {line.strip()}[/bold yellow]")
        
        console.print("\n[bold]Income Analysis (Current Month):[/bold]")
        income_table = Table(title="Income by Source")
        income_table.add_column("Source", style="cyan")
        income_table.add_column("Amount", style="green")

        for source, amount_paisa in current_month_income.items():
            income_table.add_row(source, f"{amount_paisa / 100:.2f}")
        console.print(income_table)
        console.print(f"\nTotal Income This Month: [green]{total_current_month_income_paisa / 100:.2f}[/green]")

        console.print("\n[bold]Month-over-Month Income Comparison:[/bold]")
        current_month_total = total_current_month_income_paisa / 100
        previous_month_total = total_previous_month_income_paisa / 100
        
        console.print(f"Current Month ({now.strftime('%B')}): {current_month_total:.2f}")
        console.print(f"Previous Month ({previous_month_date.strftime('%B')}): {previous_month_total:.2f}")

        if previous_month_total > 0:
            change_percent = ((current_month_total - previous_month_total) / previous_month_total) * 100
            if change_percent > 0:
                console.print(f"Change: [green]+{change_percent:.2f}%[/green]")
            else:
                console.print(f"Change: [red]{change_percent:.2f}%[/red]")
        else:
            console.print("Change: N/A (no income last month)")


    except FileNotFoundError:
        console.print("[bold yellow]No transactions found.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def health_score():
    """Calculate and display a financial health score."""
    try:
        total_income_paisa = 0
        total_expense_paisa = 0
        now = datetime.now()
        current_month_start, current_month_end = get_month_range(now)

        # Read transactions
        with open("database/transactions.txt", "r") as f:
            for line in f:
                try:
                    _, timestamp_str, type, _, amount_paisa, _ = line.strip().split(",", 5)
                    transaction_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    amount = int(amount_paisa)

                    if current_month_start <= transaction_date <= current_month_end:
                        if type == "income":
                            total_income_paisa += amount
                        else:
                            total_expense_paisa += amount
                except ValueError:
                    console.print(f"[bold yellow]Skipping malformed transaction line: {line.strip()}[/bold yellow]")

        # Read budgets and calculate adherence
        budgets_data = {}
        with open("database/budgets.txt", "r") as f:
            for line in f:
                category, budget_paisa = line.strip().split(",")
                budgets_data[category] = int(budget_paisa)
        
        # Calculate expenses for current month, grouped by category for budget adherence
        expenses_by_category_paisa = {}
        try:
            with open("database/transactions.txt", "r") as f:
                for line in f:
                    try:
                        _, timestamp_str, type, category, amount_paisa, _ = line.strip().split(",", 5)
                        transaction_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

                        if transaction_date.year == now.year and transaction_date.month == now.month:
                            if type == "expense":
                                expenses_by_category_paisa[category] = expenses_by_category_paisa.get(category, 0) + int(amount_paisa)
                    except ValueError:
                        pass
        except FileNotFoundError:
            pass

        # Score Calculation
        score = 0
        score_breakdown = {}

        # 1. Savings Rate (30 points)
        savings_paisa = total_income_paisa - total_expense_paisa
        if total_income_paisa > 0:
            savings_rate = (savings_paisa / total_income_paisa) * 100
            if savings_rate >= 20:
                score_breakdown["Savings Rate"] = 30
            elif savings_rate > 0:
                score_breakdown["Savings Rate"] = min(30, int(savings_rate / 20 * 30)) # Scale points
            else:
                score_breakdown["Savings Rate"] = 0
        else:
            score_breakdown["Savings Rate"] = 0 # No income, no savings score possible
        score += score_breakdown["Savings Rate"]

        # 2. Budget Adherence (25 points)
        budget_adherence_score = 25
        for category, budget_paisa in budgets_data.items():
            spent_paisa = expenses_by_category_paisa.get(category, 0)
            if budget_paisa > 0 and spent_paisa > budget_paisa:
                budget_adherence_score = 0 # Penalize heavily if any budget is overspent
                break
        score_breakdown["Budget Adherence"] = budget_adherence_score
        score += score_breakdown["Budget Adherence"]

        # 3. Income vs Expenses (25 points)
        if total_income_paisa > total_expense_paisa:
            score_breakdown["Income vs Expenses"] = 25
        else:
            score_breakdown["Income vs Expenses"] = 0
        score += score_breakdown["Income vs Expenses"]

        # 4. Debt Management (20 points) - Placeholder
        score_breakdown["Debt Management (Placeholder)"] = 10 # Default score as not implemented
        score += score_breakdown["Debt Management (Placeholder)"]


        # Interpretation
        if score >= 90:
            interpretation = "[bold green]Excellent![/bold green] Your finances are in great shape."
        elif score >= 70:
            interpretation = "[bold green]Good.[/bold green] You're doing well, but there's room for improvement."
        elif score >= 50:
            interpretation = "[bold yellow]Fair.[/bold yellow] You might want to review your spending and saving habits."
        else:
            interpretation = "[bold red]Needs Improvement.[/bold red] It's time to take a closer look at your financial habits."

        console.print("\n[bold]Financial Health Score:[/bold]")
        console.print(f"Overall Score: [bold]{score}/100[/bold]")
        console.print(f"Interpretation: {interpretation}")

        console.print("\n[bold]Score Breakdown:[/bold]")
        for factor, factor_score in score_breakdown.items():
            console.print(f"- {factor}: {factor_score} points")


    except FileNotFoundError:
        console.print("[bold yellow]No transactions or budgets found. Cannot calculate health score.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    app()

