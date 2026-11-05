# Excel Processing Common Patterns

## Reading Excel Files

### Read Single Sheet
```python
import pandas as pd
from openpyxl import load_workbook

# Method 1: pandas (recommended for data analysis)
df = pd.read_excel('file.xlsx', sheet_name='Sheet1')

# Method 2: openpyxl (for formatting preservation)
wb = load_workbook('file.xlsx')
ws = wb.active
```

### Read Multiple Sheets
```python
# All sheets as dictionary of DataFrames
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)

# Specific sheets
sheets = pd.read_excel('file.xlsx', sheet_name=['Sales', 'Inventory'])
```

### Read with Custom Headers
```python
df = pd.read_excel('file.xlsx', header=2)  # Use row 2 as header
df = pd.read_excel('file.xlsx', header=None)  # No header
```

## Writing Excel Files

### Write DataFrame to Excel
```python
df.to_excel('output.xlsx', sheet_name='Data', index=False)
```

### Write Multiple DataFrames
```python
with pd.ExcelWriter('output.xlsx') as writer:
    df1.to_excel(writer, sheet_name='Sheet1', index=False)
    df2.to_excel(writer, sheet_name='Sheet2', index=False)
```

### Write with Formulas
```python
from openpyxl import Workbook
wb = Workbook()
ws = wb.active
ws['A1'] = 'Value'
ws['A2'] = 100
ws['A3'] = '=SUM(A2)'  # Formula
wb.save('output.xlsx')
```

## Data Transformation

### Filter Data
```python
# Filter rows
filtered = df[df['Column'] > 100]

# Multiple conditions
filtered = df[(df['A'] > 10) & (df['B'] == 'X')]
```

### Sort Data
```python
sorted_df = df.sort_values(by=['Column1', 'Column2'], ascending=[True, False])
```

### Group and Aggregate
```python
grouped = df.groupby('Category')['Value'].sum()
grouped = df.groupby('Category').agg({'Value': 'mean', 'Count': 'sum'})
```

### Handle Missing Values
```python
# Fill missing values
df.fillna(0, inplace=True)
df['Column'].fillna(df['Column'].mean(), inplace=True)

# Drop rows with missing values
df.dropna(inplace=True)
```

## Formatting

### Style a Single Cell
```python
from openpyxl.styles import Font, PatternFill, Alignment, Border

cell = ws['A1']
cell.font = Font(bold=True, color='FF0000')
cell.fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
cell.alignment = Alignment(horizontal='center', vertical='center')
```

### Format Columns
```python
# Set column width
ws.column_dimensions['A'].width = 20

# Format number
ws['A1'].number_format = '#,##0.00'

# Date format
ws['A1'].number_format = 'YYYY-MM-DD'
```

### Apply Table Style
```python
from openpyxl.worksheet.table import Table, TableStyleInfo

tab = Table(ref='A1:E10', displayName='DataTable')
style = TableStyleInfo(name='TableStyleMedium9', showFirstColumn=False,
                       showLastColumn=False, showRowStripes=True, showColumnStripes=False)
tab.tableStyleInfo = style
ws.add_table(tab)
```

## Charts

### Create Chart
```python
from openpyxl.chart import BarChart, Reference

chart = BarChart()
chart.type = 'col'
chart.title = 'Sales Chart'
data = Reference(ws, min_col=2, min_row=1, max_col=3, max_row=10)
cats = Reference(ws, min_col=1, min_row=2, max_row=10)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
ws.add_chart(chart, 'E2')
```
