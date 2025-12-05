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
def recommend():
    """Provides intelligent financial recommendations."""
    try:
        # --- Data Aggregation ---
        total_income_paisa = 0
        total_expense_paisa = 0
        current_month_expenses_by_category_paisa = {}
        budgets_data_paisa = {}

        now = datetime.now()
        current_month_start, current_month_end = get_month_range(now)

        # Read transactions
        with open("database/transactions.txt", "r") as f:
            for line in f:
                try:
                    _, timestamp_str, type, category, amount_paisa_str, _ = line.strip().split(",", 5)
                    transaction_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    amount_paisa = int(amount_paisa_str)

                    if current_month_start <= transaction_date <= current_month_end:
                        if type == "income":
                            total_income_paisa += amount_paisa
                        else:
                            total_expense_paisa += amount_paisa
                            current_month_expenses_by_category_paisa[category] = current_month_expenses_by_category_paisa.get(category, 0) + amount_paisa
                except ValueError:
                    pass # Skip malformed lines

        # Read budgets
        try:
            with open("database/budgets.txt", "r") as f:
                for line in f:
                    category, budget_paisa_str = line.strip().split(",")
                    budgets_data_paisa[category] = int(budget_paisa_str)
        except FileNotFoundError:
            pass # No budgets set

        console.print("[bold green]--- Financial Recommendations ---[/bold green]")

        # --- Spending Recommendations ---
        console.print("\n[bold blue]1. Spending Recommendations:[/bold blue]")
        if total_expense_paisa > 0:
            overspent_categories = []
            for category, budget_paisa in budgets_data_paisa.items():
                spent_paisa = current_month_expenses_by_category_paisa.get(category, 0)
                if spent_paisa > budget_paisa:
                    overspent_categories.append((category, (spent_paisa - budget_paisa) / 100))
            
            if overspent_categories:
                console.print("[yellow]   You've overspent in the following categories this month:[/yellow]")
                for category, over_amount in overspent_categories:
                    console.print(f"   - [red]{category}[/red]: Over by {over_amount:.2f}. Consider reducing spending here.")
                console.print("   [tip]Tip: Review your transactions in these categories to identify areas for cutbacks.[/tip]")
            else:
                console.print("[green]   Good job! You are within your budgets for all categories.[/green]")

            # Identify highest spending categories (regardless of budget)
            if current_month_expenses_by_category_paisa:
                sorted_expenses = sorted(current_month_expenses_by_category_paisa.items(), key=lambda item: item[1], reverse=True)
                console.print("\n   [blue]Your top spending categories this month are:[/blue]")
                for category, amount_paisa in sorted_expenses[:3]:
                    console.print(f"   - {category}: {(amount_paisa / 100):.2f}. Could you reduce spending here by, say, 10%?")
        else:
            console.print("   No expenses recorded this month yet. Start tracking to get insights!")


        # --- Saving Recommendations ---
        console.print("\n[bold blue]2. Saving Recommendations:[/bold blue]")
        net_balance_paisa = total_income_paisa - total_expense_paisa
        if total_income_paisa > 0:
            savings_rate = (net_balance_paisa / total_income_paisa) * 100
            console.print(f"   Your current monthly savings rate is [bold]{savings_rate:.2f}%[/bold].")
            if savings_rate < 15:
                console.print("   [yellow]Consider increasing your savings rate. A common goal is 15-20% of your income.[/yellow]")
                potential_savings_needed = (0.15 * total_income_paisa - net_balance_paisa) / 100
                if potential_savings_needed > 0:
                    console.print(f"   [tip]Tip: Try to save an additional {potential_savings_needed:.2f} this month to reach 15%.[/tip]")
            else:
                console.print("[green]   Excellent! Your savings rate is healthy.[/green]")
        else:
            console.print("   No income recorded this month. Cannot calculate savings rate.")


        # --- Budget Optimization ---
        console.print("\n[bold blue]3. Budget Optimization:[/bold blue]")
        if budgets_data_paisa:
            under_budget_categories = []
            for category, budget_paisa in budgets_data_paisa.items():
                spent_paisa = current_month_expenses_by_category_paisa.get(category, 0)
                if spent_paisa < budget_paisa * 0.5: # Significantly under budget
                    under_budget_categories.append((category, (budget_paisa - spent_paisa) / 100))
            
            if under_budget_categories:
                console.print("[blue]   You have significant remaining budget in these categories:[/blue]")
                for category, remaining_amount in under_budget_categories:
                    console.print(f"   - {category}: {remaining_amount:.2f} remaining. [tip]Consider reallocating some of this to savings or other goals.[/tip]")
            else:
                console.print("   Your budgets seem well-aligned with your spending this month.")
        else:
            console.print("   No budgets set. Set budgets to get optimization tips!")

        # --- Financial Health Tips (Simplified based on previous health score logic) ---
        console.print("\n[bold blue]4. Financial Health Tips:[/bold blue]")
        if total_income_paisa > 0:
            # Simplified score logic from analytics, just for interpretation
            savings_rate_score = 0
            if total_income_paisa > 0:
                net_balance_paisa = total_income_paisa - total_expense_paisa
                savings_rate = (net_balance_paisa / total_income_paisa) * 100
                if savings_rate >= 20: savings_rate_score = 30
                elif savings_rate > 0: savings_rate_score = int(savings_rate / 20 * 30)

            budget_adherence_score = 25
            for category, budget_paisa in budgets_data_paisa.items():
                spent_paisa = current_month_expenses_by_category_paisa.get(category, 0)
                if budget_paisa > 0 and spent_paisa > budget_paisa:
                    budget_adherence_score = 0
                    break
            
            income_vs_expense_score = 25 if total_income_paisa > total_expense_paisa else 0

            overall_score = savings_rate_score + budget_adherence_score + income_vs_expense_score + 10 # Placeholder for debt

            if overall_score < 50:
                console.print("   [red]Your financial health needs attention.[/red] Focus on reducing expenses and increasing savings.")
                console.print("   [tip]Tip: Create a strict budget and stick to it, even for small purchases.[/tip]")
            elif overall_score < 70:
                console.print("   [yellow]Your financial health is fair.[/yellow] Look for small areas to save and optimize your budget.")
                console.print("   [tip]Tip: Automate a portion of your income to go directly into savings.[/tip]")
            else:
                console.print("   [green]Your financial health is good![/green] Keep up the great work and consider long-term investment goals.")
                console.print("   [tip]Tip: Regularly review your financial goals and adjust your plans as needed.[/tip]")
        else:
            console.print("   No income recorded this month. Focus on increasing your income streams.")


    except FileNotFoundError:
        console.print("[bold yellow]No financial data found. Please add transactions and budgets to get recommendations.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    app()