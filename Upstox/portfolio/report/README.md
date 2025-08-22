# Upstox Portfolio Report

This is an interactive report page for visualizing your Upstox holdings data.

## How to Use

1. **Generate the Report Data**
   - Run the `generate_report.py` script to fetch the latest holdings data from your Upstox account:
   ```
   python generate_report.py
   ```
   - This will create/update the data file in the `report` folder.

2. **View the Report**
   - Open the `report/index.html` file in a web browser to view your portfolio report.
   - The report includes:
     - Summary cards with key portfolio metrics
     - Portfolio allocation chart
     - Performance breakdown chart
     - Detailed holdings table

3. **Refresh the Data**
   - To get the latest holdings data, simply run the `generate_report.py` script again.
   - The report will be updated with the new data.

## Features

- **Summary Cards**: Quick overview of your total investment, current value, P&L, and number of holdings.
- **Portfolio Allocation Chart**: Visual representation of how your portfolio is distributed across different securities.
- **Performance Chart**: Comparison of investment value and P&L for each holding.
- **Holdings Table**: Detailed view of all your holdings with key metrics.

## Notes

- The report uses local JavaScript and does not send any data to external servers.
- All the portfolio data is stored locally in the `holdings_data.js` file.
- The report is designed to work offline after the data is generated.

## Requirements

- Python 3.6 or higher
- `requests` library for Python
- Modern web browser for viewing the report