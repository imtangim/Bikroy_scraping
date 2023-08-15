import requests
import concurrent.futures
from bs4 import BeautifulSoup
import json
import csv
from urllib.parse import urljoin
import time
import random

def scrape_page(url, max_retries=1):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            data_map = {}  # Store data for this page

            for item in soup.select('ul[data-testid="list"] li'):
                a = item.find('a', href=True)
                if a:
                    href = a['href']
                    complete_href = urljoin(url, href)

                    link_response = requests.get(complete_href)
                    link_response.raise_for_status()
                    link_soup = BeautifulSoup(link_response.content, 'html.parser')

                    # Extract price
                    price_element = link_soup.find('div', class_='amount--3NTpl')
                    if price_element:
                        price = price_element.text.strip()
                    else:
                        price = "NaN"

                    # Extract other data
                    for heading_element, value_element in zip(
                            link_soup.select('.label--3oVZK'), link_soup.select('.value--1lKHt')):
                        heading = heading_element.get_text(strip=True)
                        value = value_element.get_text(strip=True)
                        data_map[heading] = value

                    data_map["Price"] = price[3:]  # Removing currency symbol

                    # Introduce a random delay between 1 and 3 seconds
                    delay = random.uniform(1, 3)
                    time.sleep(delay)

            return data_map

        except Exception as e:
            print(f"An error occurred: {e}")
            retries += 1
            delay = 2 ** retries  # Exponential backoff
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)
            continue
        else:
            break
    else:
        print("Max retries reached. Skipping this page.")
        return {}

def main():
    base_url = "https://bikroy.com/en/ads/bangladesh/cars?sort=date&order=desc&buy_now=0&urgent=0&page={}"
    max_pages = 400  # Adjust this as needed for testing

    all_data = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        page_urls = [base_url.format(i) for i in range(1, max_pages + 1)]
        results = executor.map(scrape_page, page_urls)
        all_data.extend(results)

        # Print scraped data (for demonstration purposes)
        for data in all_data:
            if data:
                print(data)

    # Save data to JSON
    json_filename = "scraped_data.json"
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(all_data, jsonfile, ensure_ascii=False, indent=4)

    # Save data to CSV
    csv_filename = "scraped_data.csv"
    csv_columns = set(item for data_map in all_data for item in data_map.keys())
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        csv_writer.writeheader()
        csv_writer.writerows(all_data)

    print("Data saved to JSON and CSV files.")

if __name__ == "__main__":
    main()
