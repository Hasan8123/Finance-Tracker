# Day 6: Data Management

## Today's Goal
Implement robust data management features including importing, exporting, and clearing financial records.

## Learning Focus
- File I/O for structured data (CSV, JSON)
- Data serialization/deserialization
- Error handling during file operations
- User confirmation for destructive actions

## Fintech Concepts
- **Data Portability**: Ability to move data between systems
- **Data Integrity**: Ensuring data is accurate and consistent
- **Backup & Restore**: Safeguarding financial records
- **Audit Trail**: Tracking changes to data (though not full implementation here)

## Features to Build

### 1. Export Data
- Command: `export`
- Options:
    - `type`: `transactions` or `budgets`
    - `format`: `csv` or `json`
    - `path`: Output file path (default to `export_transactions.csv`/`export_budgets.csv` etc. in current directory)
- Flow:
    1. Read data from `transactions.txt` or `budgets.txt`.
    2. Convert to specified format (CSV/JSON).
    3. Write to the output file.
    4. Confirm export success.

### 2. Import Data
- Command: `import`
- Options:
    - `type`: `transactions` or `budgets`
    - `format`: `csv` or `json`
    - `path`: Input file path
    - `overwrite`: Boolean (default: `False`). If `True`, existing data is cleared before import.
- Flow:
    1. Read data from input file.
    2. Validate data format and content.
    3. Convert to internal format.
    4. If `overwrite` is true, clear existing `transactions.txt`/`budgets.txt`.
    5. Append imported data to `transactions.txt` or `budgets.txt`.
    6. Confirm import success.

### 3. Clear Data
- Command: `clear`
- Options:
    - `type`: `transactions` or `budgets` or `all`
- Flow:
    1. Ask for user confirmation (critical for destructive action).
    2. Clear the contents of `transactions.txt` / `budgets.txt` / both.
    3. Confirm data cleared.

## Success Criteria

✅ Can export transaction data to CSV and JSON.
✅ Can export budget data to CSV and JSON.
✅ Can import transaction data from CSV and JSON.
✅ Can import budget data from CSV and JSON.
✅ Imports handle overwriting existing data.
✅ Clearing data requires user confirmation.
✅ All file operations are robust with error handling.