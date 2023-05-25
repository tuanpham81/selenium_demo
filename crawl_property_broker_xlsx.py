import logging
import time
from datetime import datetime

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

chrome_options = Options()
chrome_options.add_argument('--disable-site-isolation-trials')

chromedriver_path = "D:/Software/chromedriver_win32/chromedriver.exe"

# driver = webdriver.Chrome(service=service)
driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
wait = WebDriverWait(driver, 10)

url = "https://nhadat.cafeland.vn/moi-gioi/"
driver.get(url)
driver.maximize_window()
time.sleep(1)

name_list = []
email_list = []
phone_list = []
city_list = []
district_list = []
file_data = {
    'name': name_list,
    'email': email_list,
    'phone': phone_list,
    'city': city_list,
    'district': district_list
}
city_order = 2  # skip place holder
try:
    while city_order <= 64:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div[2]/form/div[2]/div[1]/button')))
        driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[2]/form/div[2]/div[1]/button').click()
        city = driver.find_element(By.XPATH, f'//*[@id="bs-select-1"]/ul/li[{city_order}]')
        city_name = city.text
        city.click()

        driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[2]/form/div[2]/div[2]/button').click()
        time.sleep(1)
        districts = driver.find_elements(By.XPATH, '//*[@id="bs-select-2"]/ul/li')
        for element in districts[1:]:  # skip place holder
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//*[@id="bs-select-2"]/ul/li[{districts.index(element) + 1}]')))
            district = driver.find_element(By.XPATH, f'//*[@id="bs-select-2"]/ul/li[{districts.index(element) + 1}]')
            district_name = district.text
            district.click()
            driver.find_element(By.XPATH, "//button[@id='tim-moigioi']").click()

            is_last_page = False
            while not is_last_page:
                brokers = driver.find_elements(By.XPATH, f'/html/body/div[7]/div/div/div[1]/div/div[2]/div')

                for broker in brokers:
                    broker_data = {}
                    name = broker.find_element(By.CSS_SELECTOR, '.moigioi-fullname a').text
                    name_list.append(name)

                    email_element = broker.find_element(By.CLASS_NAME, "hiddenEmailBlock")
                    email = email_element.get_attribute("data-name") + "@" + email_element.get_attribute("data-dm")
                    email_list.append(email)

                    phone_element = broker.find_element(By.CSS_SELECTOR, ".phone a")
                    phone_number = phone_element.get_attribute("onclick") \
                        .split("showfullphoneMoiGioi(this,'")[1].split("')")[0]
                    phone_list.append(phone_number)

                    city_list.append(city_name)
                    district_list.append(district_name)

                try:
                    page_list = driver.find_elements(By.XPATH, '/html/body/div[7]/div/div/div[1]/div/div[3]/nav/ul/li')
                    if len(page_list) <= 1:
                        break
                    for page in page_list:
                        if 'active' in page.get_attribute('class'):
                            if page == page_list[-1] or page.text == '10':
                                is_last_page = True
                                break
                            next_page = page_list[page_list.index(page) + 1]
                            driver.get(next_page.find_element(By.CSS_SELECTOR, 'li > a').get_attribute('href'))
                            break
                except Exception as e:
                    logging.error(e)
                    break

            driver.get('https://nhadat.cafeland.vn/moi-gioi')
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div[2]/form/div[2]/div[1]/button')))
            driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[2]/form/div[2]/div[1]/button').click()
            driver.find_element(By.XPATH, f'//*[@id="bs-select-1"]/ul/li[{city_order}]').click()
            driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[2]/form/div[2]/div[2]/button').click()
        city_order += 1
except Exception as e:
    logging.error(e)
finally:
    # save to xlsx
    df = pd.DataFrame(file_data)
    file_name: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f'data/{file_name}.xlsx'
    df.to_excel(file_path, index=False)
    print(f"Save file {file_name} successfully")
input("Press any key to exit...")
driver.quit()
