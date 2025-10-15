# PDF Keyword Filter & Downloader

- This Python script automatically **scrapes PDF links from a target website using Playwright**, then **downloads and scans each PDF** to find those that contain a specific keyword.  
- All matching PDFs are then **saved to a CSV file** for later use.

---

## Features

- **Dynamic web scraping with Playwright + Selectolax**  
  Automatically navigates through paginated content and extracts all PDF URLs.

- **Parallel processing with ThreadPoolExecutor**  
  Analyzes multiple PDFs simultaneously to significantly speed up execution.

- **In-memory PDF reading with pypdf**  
  PDFs are loaded into RAM using `BytesIO` — no temporary disk writes.

- **Keyword-based filtering**  
  Finds only PDFs that include your chosen keyword (default: `pay-to-play`).

- **CSV export**  
  Saves all matching PDF URLs to `links.csv`.

---

## Requirements

Make sure you have **Python 3.10+** installed.  
Then install the required dependencies:

```bash
pip install playwright selectolax requests pypdf

playwright install
```
---

## Usage

- Clone or download this repository.

- Open a terminal in the project folder.

- Run the script:


```bash
python main.py
```

- **The script will**

- Launch a headless Firefox browser.

- Scrape all available PDF links.

- Download and analyze them in parallel.

- Print and save all matches containing the keyword to links.csv.

---

## Configuration

You can modify the following variables in the script:

**Variable**	            **Description**	                                **Default**
url	                    Target page to scrape	                    https://www.sec.gov/enforcement-litigation/administrative-proceedings

target_keyword	        The keyword to search inside PDF content	"pay-to-play"

max_workers	            Number of parallel threads	                8

batch_size	            Number of links processed per batch         1000

---

## Output

- links.csv — contains all URLs of PDFs that matched the keyword.

- Console output includes progress updates, exceptions, and keyword hits.

**Example:**

```bash
--- Processing batch 2/10 (1000 links) ---
[34/1000] Processed: https://www.sec.gov/.../ap-12345.pdf
   FOUND! includes 'pay-to-play'.
```

---

## Project Structure
```bash
.
├── main.py              # Main script file
├── links.csv            # Output file containing found links
└── README.md            # Project documentation
```

---

### Notes

- !!! This script is designed for educational and research purposes only.

- !!! Always ensure scraping complies with the target site’s robots.txt and terms of service.

- !!! For very large datasets, adjust batch_size and max_workers to match your CPU and memory limits.

---

### Author

- Developed by: [Your Name]
- Language: Python 3.11
- Purpose: Automated document filtering and analysis pipeline