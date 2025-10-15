from playwright.sync_api import sync_playwright # Used playwright to open a headless browser.
from selectolax.parser import HTMLParser # Used selectolax to parse html content of the website.
from time import sleep # Used sleep to add wait between browser page transitions.
import requests # Used requests to get the pdf content from the pdf url.
from io import BytesIO # Used BytesIO to keep pdfs in our RAM as a temporary file to not download all pdfs to our disk.
from pypdf import PdfReader # Used pypdf to get the text content from the pdf files to filter.
from concurrent.futures import ThreadPoolExecutor, as_completed # Used concurrent to analyzse more than one pdf at thme same time to make our program faster.
import csv # Used csv to save the founded links as a csv folder.
import math

############# FUNCTION TO GET PDF LINKS FROM THE WEBSITE
def parse_links():
    links = []
    with sync_playwright() as p:

        ############# OPENING OUR MAIN HEADLESS BROWSER WITH PLAYWRIGHT #############
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0"
        })
        url = "https://www.sec.gov/enforcement-litigation/administrative-proceedings"
        page.goto(url)
        
        ############# WHILE LOOP TO KEEP PARSING UNTIL THE END OF THE PAGINATON #############
        while (True):
            sleep(2)
            # page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_selector("table.usa-table tbody")

            ############# SENDING HTML TEXT TO SELECTOLAX TO PARSE #############
            html = page.content()
            tree = HTMLParser(html)

            all_files = tree.css("table.usa-table tbody tr.pr-list-page-row")

            for file in all_files:
                link_tag = file.css_first("a").attributes.get('href')
                links.append(link_tag)
                print(link_tag)
            
            next_button = tree.css_first("a[aria-label='Next page']")
            if next_button:
                page.click("a[aria-label='Next page']")
            else:
                break

    return links


############# FUNCTION TO FILTER PDF FILES WITH THE TARGET KEYWORD #############
def filter_links_by_content_PARALLEL(links: list, max_workers: int = 8, batch_size: int = 1000):
    
    target_keyword = "pay-to-play"
    found_links = []
    total_links = len(links)
    total_batches = math.ceil(total_links / batch_size)
    
    print(f"\n--- Total {total_links} {max_workers} processing with workers... ---\n")

    # Dividing our links list to batches to prevent overload on cpu
    for index, batch_index in enumerate(range(total_batches)):
        start = batch_index * batch_size
        end = min(start + batch_size, total_links)
        batch_links = links[start:end]

        print(f"\n--- Processing batch {batch_index + 1}/{total_batches} ({len(batch_links)} links) ---")

        # Starting thread pool executer to process 25 pdf files at the same time. 
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Giving tasks to the workers.
            # Each task runs the "extract_text_from_pdf()" function with a worker.
            task_to_url = {executor.submit(extract_text_from_pdf, url): url for url in batch_links} ### IMPORTANT!!
            # as_completed, returns the tasks as they complete respectively.
            for index, task in enumerate(as_completed(task_to_url)):
                url = task_to_url[task]
                try:
                    pdf_text = task.result() # Get the pdf text content
                    
                    print(f"[{index + 1}/{batch_size}] Processed: {url[:80]}...") 
                    
                    if pdf_text:
                        
                        if target_keyword in pdf_text.lower():
                            
                            print(f"   FOUND! includes '{target_keyword}'.")
                            found_links.append(url)
                    
                except Exception as exc:
                    print(f'{url} created an exception: {exc}')
        
        sleep(2)

    return found_links

def extract_text_from_pdf(url: str) -> str | None:
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 OPR/121.0.0.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        pdf_file = BytesIO(response.content)
        reader = PdfReader(pdf_file)

        full_text = []
        for page in reader.pages:
            full_text.append(page.extract_text())

        return "\n".join(full_text)

    except requests.exceptions.RequestException as e:
        print(f"Error: Data could not be retrieved from URL {url}. Error: {e}")
        return None
    
    except Exception as e:
        print(f"Error: PDF could not be processed {url}. Error: {e}")
        return None


############# Main function that runs the workflow #############
if __name__ == "__main__":
    # Collect the links
    all_pdf_links = parse_links()
    
    # Filter the collected links
    filtered_links = filter_links_by_content_PARALLEL(all_pdf_links, max_workers=8)
    
    # Show the results
    print("\n=============================================")
    print(f"Total link count: {len(all_pdf_links)}")
    print(f"'{filter_links_by_content_PARALLEL.__defaults__[0]}' included links: {len(filtered_links)}")
    print("=============================================")
    
    print("Proceeding links that includes the keyword: 'pay-to-play'")
    
    if filtered_links:
        for link in filtered_links:
            print(f"- {link}")

    # Saving the founded links to our computer as a csv folder.
    with open("links.csv", "w", newline="", encoding= "utf-8") as file:
        writer = csv.writer(file)
        for link in filtered_links:
            writer.writerow([link])