import typer
from features.transactions import transactions
from features.budgets import budgets
from features.analytics import analytics

app = typer.Typer()

app.add_typer(transactions.app, name="transactions")
app.add_typer(budgets.app, name="budgets")
app.add_typer(analytics.app, name="analytics")

if __name__ == "__main__":
    app()