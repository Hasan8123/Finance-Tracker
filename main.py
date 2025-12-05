import typer
from features.transactions import transactions
from features.budgets import budgets
from features.analytics import analytics
from features.smart_assistant import smart_assistant
from features.data_management import data_management

app = typer.Typer()

app.add_typer(transactions.app, name="transactions")
app.add_typer(budgets.app, name="budgets")
app.add_typer(analytics.app, name="analytics")
app.add_typer(smart_assistant.app, name="smart-assistant")
app.add_typer(data_management.app, name="data")

if __name__ == "__main__":
    app()