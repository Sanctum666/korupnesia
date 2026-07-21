# Korupnesia
Korupnesia is a Python application that extracts corruption data from saved HTML pages.
The application writes the results to databases (currently CSV files, planned to have MySQL/PgSQL db backend soon)  
The source data comes from Korupedia, an Indonesian corruption database.

> data is being cutoff as of 2022, so this project serves as a purpose for me to demonstrate ETL pipeline
## What Korupnesia Does

Korupnesia reads HTML files from the `data/` directory.
Each file contains information about one corruption case in Indonesia.
The application extracts the following data from each file:

- Name of the corruptor
- Job title and profession
- Description of the corruption case
- Year of corruption
- Amount of money involved
- Prison sentence and fine
- Court decision details

```json
{
  "nama": "Syamsu Ridhuan",
  "deskripsi": "Syamsu Ridhuan merupakan Pria kelahiran Lahat, Sumatera Selatan, 12 November 1962. Ia pernah menjadi PNS di BNP Bengkulu dengan Jabatan Kepala Pelaksana Harian",
  "profesi": "PNS BNP Bengkulu",
  "rekam_jejak_pekerjaan": "",
  "tahun_korupsi": "2010",
  "jumlah_korupsi": "Rp 210.000.000",
  "hukuman_penjara": "3 Tahun",
  "hukuman_denda": "Rp 50.000.000",
  "uang_pengganti": "Rp 210.000.000",
  "nomor_putusan_akhir": "Nomor: 1256 K/Pid.Sus/2012",
  "tahun_putusan": "2012",
  "uraian_perkara": "Terdakwa melakukan tindak pidana korupsi..."
}

```

The application writes all extracted data to a single CSV file in the `database/` directory.

## How It Works

Korupnesia processes files in three steps:

1. Read all HTML files from the `data/` directory.
2. Parse each file and extract corruption data.
3. Write all collected data to a CSV file.

The application uses multiple threads to process files in parallel.
It divides the files into batches based on the CPU count of the machine.
Each batch runs in its own thread.

The parser uses BeautifulSoup to read HTML content.
It extracts data from CSS selectors in the page structure.
If a file cannot be read or parsed, the application logs the error and continues.

## Installation

### 1. Install uv

uv is a GOATed python package manager, without it this language sucks.  
Install it with this command:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```
or refer to https://docs.astral.sh/uv/getting-started/installation/

### 2. Clone the repository

```
git clone https://github.com/nekraut/korupnesia.git
cd korupnesia
```

### 3. Install Python and dependencies

uv installs the correct Python version and all dependencies automatically:

```
uv sync
```

This command reads `pyproject.toml` and creates a `.venv/` directory.
It installs Python 3.12 and all required packages.

## How to Run

Run the application with:

```
make run
```

Or run directly with uv:

```
uv run python -Xgil=0 ./src/main.py
```

The application writes the CSV file to `database/data.csv`.
Log files are written to the `logs/` directory.

## Project Structure

```
src/
  main.py                    - Entry point for the application
  parser.py                  - Parses HTML files and extracts data
  dispatcher.py              - Manages batch processing and threading
  shared/
    configured_logger.py     - Configures the logging system
data/                        - Contains saved HTML files from Korupedia
database/                    - Output directory for the CSV file
logs/                        - Directory for log files
```

## Acknowledgment

Data source: https://korupedia.transparansi.id

## Data Status

The data was last updated in 2022 from Korupedia.
