import requests
from bs4 import BeautifulSoup
import json
import csv
from urllib.parse import urljoin

data_to_save = []
try:
    for i in range(1, 450):
        try:
            print(f"Page no: {i}")
            initial_link = f"https://bikroy.com/en/ads/bangladesh/cars?sort=date&order=desc&buy_now=0&urgent=0&page={i}"
            print(initial_link)
            response = requests.get(initial_link)
            response.raise_for_status()  # Check for request errors

            soup = BeautifulSoup(response.content, 'html.parser')

            target_ul = soup.find('ul', attrs={'data-testid': 'list'})

            li_elements = target_ul.find_all('li')
            for li in li_elements:
                a = li.find('a', href=True)
                if a:
                    href = a['href']
                    complete_href = urljoin(initial_link, href)

                    link_response = requests.get(complete_href)
                    link_response.raise_for_status()  # Check for request errors
                    link_soup = BeautifulSoup(link_response.content, 'html.parser')

                    data_map = {}
                    heading_elements = link_soup.find_all(class_='label--3oVZK')
                    value_elements = link_soup.find_all(class_='value--1lKHt')

                    try:
                        price_element = link_soup.find(
                            'div', class_='amount--3NTpl')
                        if price_element:
                            
                            price = price_element.text.strip()
                        else:
                            price = "NaN"
                            raise ValueError("Price element not found")
                    except (ValueError, AttributeError) as e:
                        price = "NaN"
                        print(f"Error while extracting price: {e}")

                    for heading_element, value_element in zip(heading_elements, value_elements):
                        try:
                            if heading_elements and value_element:
                                heading = heading_element.text.strip()
                                value = value_element.text.strip()
                                data_map[heading] = value

                            else:
                                raise ValueError("Price element not found")

                        except (ValueError, AttributeError) as e:
                            heading = "NaN"
                            value = 'NaN'
                            data_map[heading] = value
                            print(f"Error while extracting price: {e}")

                    data_map["Price"] = price[3:]
                    data_to_save.append(data_map.copy())
        except requests.exceptions.RequestException as re:
            # print(f"Request error occurred: {re}")
            # Save data to JSON
            json_filename = "scraped_data.json"
            with open(json_filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data_to_save, jsonfile, ensure_ascii=False, indent=4)
            
            csv_filename = "scraped_data.csv"
            csv_columns = data_to_save[0].keys() if data_to_save else [
            ]  # Ensure there's data
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                csv_writer.writeheader()
                csv_writer.writerows(data_to_save)
                print(f"Data saved to {csv_filename}")
                print("Network failed!")
            break

        except Exception as e:
            # Save data to JSON
            json_filename = "scraped_data2.json"
            with open(json_filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data_to_save, jsonfile, ensure_ascii=False, indent=4)
            # print(f"An unexpected error occurred: {e}")
            continue

except KeyboardInterrupt as keyboard:
    print("Keyboard interrupt detected. Saving data and exiting...")

finally:
    # Save data to JSON
    json_filename = "scraped_data2.json"
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data_to_save, jsonfile, ensure_ascii=False, indent=4)

    # Save data to CSV
    csv_filename = "scraped_data2.csv"
    csv_columns = data_to_save[0].keys() if data_to_save else []  # Ensure there's data

    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        csv_writer.writeheader()
        csv_writer.writerows(data_to_save)

    print("Data saved to JSON and CSV files.")