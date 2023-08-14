import requests
from bs4 import BeautifulSoup
import json
import csv
from urllib.parse import urljoin

data_to_save = []
k = 1
for i in range(1,450):
# Step 1: Retrieve the HTML Content
        print(f"Page no: {i}")
        initial_link = f"https://bikroy.com/en/ads/bangladesh/cars?sort=date&order=desc&buy_now=0&urgent=0&page={i}"
        print(initial_link)
        master_link = "https://bikroy.com/"
        response = requests.get(initial_link)
        html_content = response.text

        # Step 2: Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the specific <ul> element with data-testid="list"
        target_ul = soup.find('ul', attrs={'data-testid': 'list'})


        # Step 3: Find the <li> Elements within the target <ul>
        li_elements = target_ul.find_all('li')
        for li in li_elements:
            a = li.find('a', href=True)
            if a:
                href = a['href']
                complete_href = urljoin(initial_link, href)

                # Step 4: Visit Links and Scrape Data
                link_response = requests.get(complete_href)
                link_html = link_response.text

                # Step 5: Parse Inner HTML
                link_soup = BeautifulSoup(link_html, 'html.parser')

               # Step 6 and 7: Extract Desired Data
                heading_elements = link_soup.find_all(class_='label--3oVZK')
                value_elements = link_soup.find_all(class_='value--1lKHt')
                ad_meta_elements = link_soup.find_all(class_='ad-meta-mobile--3T_Ao')
                price_element = link_soup.find('div', class_='amount--3NTpl')  # Use link_soup instead of soup

                heading = None
                value = None

                data_map = {}
                price = price_element.text.strip()
                for heading_element, value_element in zip(heading_elements, value_elements):
                    heading = heading_element.text.strip()
                    value = value_element.text.strip()

                    # Step 8: Check for ad-meta-mobile--3T_Ao class
                    if any(ad_meta_element in value_element.parents for ad_meta_element in ad_meta_elements):
                        ad_meta_data = "AD META FOUND"
                    else:
                        ad_meta_data = ""

                    # Step 9: Collect and Store Data in a dictionary
                    data_map[heading] = value

                # Add the price to the data map
                data_map["Price"] = price

                data_to_save.append(data_map.copy())
                json_filename = "scraped_data.json"
                with open(json_filename, 'w', encoding='utf-8') as jsonfile:
                    json.dump(data_to_save, jsonfile, ensure_ascii=False, indent=4)


# Convert the data to CSV format
csv_filename = "scraped_data.csv"
csv_columns = data_to_save[0].keys()  # Assumes all dictionaries have the same keys

with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    csv_writer.writeheader()
    for data_map in data_to_save:
        csv_writer.writerow(data_map)

print(f"Data saved to {csv_filename}")



print("All Done!!!")
