import typer
from rich.console import Console
import csv
import json
import os
from datetime import datetime
import questionary

app = typer.Typer()
console = Console()

def read_data(data_type: str):
    """Reads data from the specified text file."""
    file_path = f"database/{data_type}.txt"
    data = []
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                data.append(parts)
    return data

def write_data(data_type: str, data: list, mode: str = "w"):
    """Writes data to the specified text file."""
    file_path = f"database/{data_type}.txt"
    with open(file_path, mode) as f:
        for item in data:
            f.write(",".join(map(str, item)) + "\n")

@app.command()
def export(
    data_type: str = typer.Argument(..., help="Type of data to export (transactions or budgets)."),
    format: str = typer.Argument(..., help="Export format (csv or json)."),
    path: str = typer.Option(None, "--path", "-p", help="Output file path.")
):
    """Export transactions or budgets to CSV or JSON."""
    if data_type not in ["transactions", "budgets"]:
        console.print("[bold red]Error:[/bold red] data_type must be 'transactions' or 'budgets'.")
        raise typer.Exit(1)
    if format not in ["csv", "json"]:
        console.print("[bold red]Error:[/bold red] format must be 'csv' or 'json'.")
        raise typer.Exit(1)

    data = read_data(data_type)
    if not data:
        console.print(f"[bold yellow]No {data_type} found to export.[/bold yellow]")
        raise typer.Exit()

    # Define headers based on data_type
    if data_type == "transactions":
        headers = ["ID", "Timestamp", "Type", "Category", "Amount", "Description"]
    else: # budgets
        headers = ["Category", "Amount"]

    if path is None:
        path = f"export_{data_type}.{format}"

    try:
        if format == "csv":
            with open(path, "w", newline="") as outfile:
                writer = csv.writer(outfile)
                writer.writerow(headers)
                writer.writerows(data)
        elif format == "json":
            # Convert list of lists to list of dicts for JSON
            json_data = []
            for row in data:
                json_data.append(dict(zip(headers, row)))
            with open(path, "w") as outfile:
                json.dump(json_data, outfile, indent=4)
        
        console.print(f"[bold green]{data_type.capitalize()} exported successfully to {path}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error during export:[/bold red] {e}")
        raise typer.Exit(1)

@app.command()
def import_data(
    data_type: str = typer.Argument(..., help="Type of data to import (transactions or budgets)."),
    format: str = typer.Argument(..., help="Import format (csv or json)."),
    path: str = typer.Option(..., "--path", "-p", help="Input file path."),
    overwrite: bool = typer.Option(False, "--overwrite", "-o", help="Overwrite existing data.")
):
    """Import transactions or budgets from CSV or JSON."""
    if data_type not in ["transactions", "budgets"]:
        console.print("[bold red]Error:[/bold red] data_type must be 'transactions' or 'budgets'.")
        raise typer.Exit(1)
    if format not in ["csv", "json"]:
        console.print("[bold red]Error:[/bold red] format must be 'csv' or 'json'.")
        raise typer.Exit(1)
    if not os.path.exists(path):
        console.print(f"[bold red]Error:[/bold red] Input file not found: {path}")
        raise typer.Exit(1)

    imported_data = []
    try:
        if format == "csv":
            with open(path, "r", newline="") as infile:
                reader = csv.reader(infile)
                headers = next(reader) # Skip header row
                for row in reader:
                    imported_data.append(row)
        elif format == "json":
            with open(path, "r") as infile:
                json_data = json.load(infile)
                # Convert list of dicts to list of lists
                if json_data:
                    headers = list(json_data[0].keys()) # Assuming all dicts have same keys
                    for item in json_data:
                        imported_data.append([item[key] for key in headers])
                
        if not imported_data:
            console.print(f"[bold yellow]No data found in {path} to import.[/bold yellow]")
            raise typer.Exit()
        
        if overwrite:
            confirm = questionary.confirm(f"Are you sure you want to overwrite existing {data_type} data? This action cannot be undone.").ask()
            if not confirm:
                console.print("Import cancelled.")
                raise typer.Exit()
            write_data(data_type, imported_data, mode="w") # Overwrite
        else:
            write_data(data_type, imported_data, mode="a") # Append
        
        console.print(f"[bold green]{len(imported_data)} {data_type.capitalize()} imported successfully from {path}[/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error during import:[/bold red] {e}")
        raise typer.Exit(1)

    except Exception as e:
        console.print(f"[bold red]Error during import:[/bold red] {e}")
        raise typer.Exit(1)

@app.command()
def clear(
    data_type: str = typer.Argument(..., help="Type of data to clear (transactions, budgets, or all).")
):
    """Clear all transactions or budgets data."""
    if data_type not in ["transactions", "budgets", "all"]:
        console.print("[bold red]Error:[/bold red] data_type must be 'transactions', 'budgets', or 'all'.")
        raise typer.Exit(1)
    
    confirm = questionary.confirm(f"Are you sure you want to clear ALL {data_type} data? This action cannot be undone.").ask()
    if not confirm:
        console.print("Clear operation cancelled.")
        raise typer.Exit()

    try:
        if data_type == "transactions" or data_type == "all":
            with open("database/transactions.txt", "w") as f:
                f.write("")
            console.print("[bold green]All transactions data cleared.[/bold green]")
        
        if data_type == "budgets" or data_type == "all":
            with open("database/budgets.txt", "w") as f:
                f.write("")
            console.print("[bold green]All budgets data cleared.[/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error during clear operation:[/bold red] {e}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()