# Korupnesia

Korupnesia is a Python application that extracts corruption data from saved HTML pages.
The application writes the results to a CSV file.
A Dash dashboard shows the data with charts and filters.
> The data was last updated in 2022. This project servers as a learning purpose for me to demonstrate and explroe ETL pipeline.

## What Korupnesia Does

Korupnesia reads HTML files from the `data/` directory.
Each file contains data about one corruption case in Indonesia.
The application extracts the following data from each file:

- Name of the corruptor
- Job title and profession
- Description of the corruption case
- Year of corruption
- Amount of money involved
- Prison sentence and fine
- Court decision details

## How It Works

Korupnesia processes files in three steps:

1. Read all HTML files from the `data/` directory.
2. Parse each file and extract corruption data.
3. Write all collected data to a CSV file.

The application uses multiple threads to process files in parallel.
It divides the files into batches based on the CPU count.
Each batch runs in its own thread.

The parser uses BeautifulSoup to read HTML content.
It extracts data from CSS selectors in the page structure.
If a file cannot be read or parsed, the application logs the error and continues.

## Installation

### 1. Install uv

uv is the GOAT of Python package manager.
Install it with this command:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or refer to https://docs.astral.sh/uv/getting-started/installation/

### 2. Clone the repository

```
git clone https://github.com/nekraut/korupnesia.git
cd korupnesia
```

### 3. Install Python and dependencies

uv installs the correct Python version and all dependencies:

```
uv sync
```

This command reads `pyproject.toml` and creates a `.venv/` directory.
It installs Python 3.12 and all required packages.

## How to Run

### ETL Pipeline

Run the ETL pipeline to extract data from HTML files and write a CSV:

```
make run
```

Or run directly with uv:

```
uv run python -Xgil=0 ./src/main.py
```

The application writes the CSV file to `database/data.csv`.
Log files are written to the `logs/` directory.

### Dashboard

Run the Dash dashboard to view the data:

```
make dashboard
```

Or run directly with uv:

```
uv run python ./src/dashboard.py
```

Open `http://localhost:8050` in a browser.
The dashboard shows:

- KPI cards with summary statistics
- Charts for corruption amounts, cases per year, and sentence distribution
- A searchable and sortable data table
- A detail panel for each case

## Project Structure

```
src/
  main.py                    - Entry point for the ETL pipeline
  parser.py                  - Parses HTML files and extracts data
  dispatcher.py              - Manages batch processing and threading
  dashboard.py               - Dash dashboard for data visualization
  shared/
    configured_logger.py     - Configures the logging system
data/                        - Contains saved HTML files from Korupedia
database/                    - Output directory for the CSV file
logs/                        - Directory for log files
```

## Acknowledgment

Data source: https://korupedia.transparansi.id
