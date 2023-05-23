import json
import logging
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

chrome_options = Options()
chrome_options.add_argument('--disable-site-isolation-trials')

chromedriver_path = "D:/Software/chromedriver_win32/chromedriver.exe"
service = ChromeService(executable_path=chromedriver_path, chrome_options=chrome_options)
service.start()

driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 10)

url = "https://nhadat.cafeland.vn/moi-gioi/"
driver.get(url)
driver.maximize_window()
time.sleep(1)

city_order = 2  # skip place holder
while city_order <= 64:
    city_data = []
    driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[2]/form/div[2]/div[1]/button').click()
    city = driver.find_element(By.XPATH, f'//*[@id="bs-select-1"]/ul/li[{city_order}]')
    city_name = city.text
    city.click()

    driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[2]/form/div[2]/div[2]/button').click()
    time.sleep(1)
    districts = driver.find_elements(By.XPATH, '//*[@id="bs-select-2"]/ul/li')
    for element in districts[1:]:  # skip place holder
        district_data = {}
        time.sleep(1)
        district = driver.find_element(By.XPATH, f'//*[@id="bs-select-2"]/ul/li[{districts.index(element) + 1}]')
        district_data['district'] = district.text
        district.click()
        driver.find_element(By.XPATH, "//button[@id='tim-moigioi']").click()

        is_last_page = False
        broker_list_data = []
        while not is_last_page:
            brokers = driver.find_elements(By.XPATH, f'/html/body/div[7]/div/div/div[1]/div/div[2]/div')

            for broker in brokers:
                broker_data = {}
                name = broker.find_element(By.CSS_SELECTOR, '.moigioi-fullname a').text
                broker_data['name'] = name

                email_element = broker.find_element(By.CLASS_NAME, "hiddenEmailBlock")
                email = email_element.get_attribute("data-name") + "@" + email_element.get_attribute("data-dm")
                broker_data['email'] = email

                phone_element = broker.find_element(By.CSS_SELECTOR, ".phone a")
                phone_number = phone_element.get_attribute("onclick") \
                    .split("showfullphoneMoiGioi(this,'")[1].split("')")[0]
                broker_data['phone_number'] = phone_number

                broker_list_data.append(broker_data)

            try:
                page_list = driver.find_elements(By.XPATH, '/html/body/div[7]/div/div/div[1]/div/div[3]/nav/ul/li')
                if len(page_list) <= 1:
                    break
                for page in page_list:
                    if 'active' in page.get_attribute('class'):
                        if page == page_list[-1]:
                            is_last_page = True
                            break
                        next_page = page_list[page_list.index(page) + 1]
                        driver.get(next_page.find_element(By.CSS_SELECTOR, 'li > a').get_attribute('href'))
                        break
            except Exception as e:
                logging.error(e)
                break

        district_data['brokers'] = broker_list_data
        city_data.append(district_data)

        driver.get('https://nhadat.cafeland.vn/moi-gioi')
        time.sleep(1)
        driver.refresh()
        time.sleep(1)
        driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[2]/form/div[2]/div[1]/button').click()
        driver.find_element(By.XPATH, f'//*[@id="bs-select-1"]/ul/li[{city_order}]').click()
        driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[2]/form/div[2]/div[2]/button').click()
    city_order += 1

    # save to json
    file_data = {'city': city_name, 'data': city_data}
    file_path = f'{city_name}.json'
    if os.path.exists(file_path):
        print("File already exists. Skip.")
    else:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(file_data, file, ensure_ascii=False, indent=4)

input("Press any key to exit...")
driver.quit()
service.stop()
