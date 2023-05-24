import os
import time
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import urlparse

# add to run perfectly
chrome_options = Options()
chrome_options.add_argument('--disable-site-isolation-trials')

chromedriver_path = "D:/Software/chromedriver_win32/chromedriver.exe"
service = ChromeService(executable_path=chromedriver_path, chrome_options=chrome_options)
service.start()

# Chrome
driver = webdriver.Chrome(service=service)
# Safari
# driver = webdriver.Safari()

wait = WebDriverWait(driver, 10)

keyword = "giàn phơi thông minh"
search_url = f"https://www.google.com/search?q={keyword}"
driver.get(search_url)

page = 1
position = 1
for page in range(1, 6):
    for number in range(1, 11):
        result_data = {}
        result = driver.find_element(By.XPATH, f'//*[@id="rso"]/div[{number}]/div/div')
        element = result.find_element(By.CSS_SELECTOR, 'h3')

        ActionChains(driver).key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()

        # Switch to the new tab
        wait.until(lambda dr: len(dr.window_handles) > 1)
        driver.switch_to.window(driver.window_handles[1])
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        result_data['position'] = str(position)
        # print(f'Position: {position}')

        link = driver.current_url
        result_data['link'] = link
        print(f"{position} - link: {link}")

        title = driver.title
        result_data['title'] = title
        # print(f"title: {title}")
        try:
            created_date = driver.find_element(By.CSS_SELECTOR, 'time').text
            result_data['created_date'] = created_date
            # print(f"created_date: {created_date}")
        except:
            result_data['created_date'] = 'created date not found'
            # print('created date not found')
        try:
            description = driver.find_element(By.NAME, 'description').get_attribute('content')
            result_data['description'] = description
            # print(f"description: {description}")
        except:
            result_data['description'] = 'description not found'
            # print('description not found')

        if not link.__contains__('shopee' or 'lazada' or 'tiki'):
            # Find all the elements on the page
            elements = driver.find_elements(By.XPATH, '//body//*[self::p or self::img or self::table]')
            list_data = []
            for element in elements:
                if element.tag_name == 'p':
                    data = element.text
                    if data:
                        dict_data = {'data_type': 'paragraph', 'value': data}
                        list_data.append(dict_data)
                        # print("Paragraph:", data)

                if element.tag_name == "img" and not element.get_attribute('src').__contains__('w3.org'):
                    dict_data = {'data_type': 'image', 'value': element.get_attribute('src')}
                    list_data.append(dict_data)
                    # print("Image:", element.get_attribute('src'))

                if element.tag_name == "table":
                    dict_data = {'data_type': 'table'}
                    table_value = []
                    # print("Table:")
                    rows = element.find_elements(By.CSS_SELECTOR, 'tr')
                    for row in rows:
                        datas = row.find_elements(By.CSS_SELECTOR, 'td')
                        row_datas = {}
                        column_number = 1
                        for data in datas:
                            row_datas[f'column{column_number}'] = data.text
                            column_number += 1
                            # print(data.text)
                        table_value.append(row_datas)
                    dict_data['value'] = table_value
                    list_data.append(dict_data)
            result_data['content'] = list_data

        file_path = f'{str(position)}-{urlparse(link).netloc}.json'
        if os.path.exists(file_path):
            print("File already exists. Skip.")
        else:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(result_data, file, ensure_ascii=False, indent=4)
        # print(result_data)

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        position += 1
        time.sleep(1)

    driver.find_element(By.XPATH, '//*[@id="pnnext"]/span[2]').click()
input("Press any key to exit...")
driver.quit()
service.stop()
