from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox') #for Linux
    options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})
    driver = webdriver.Chrome(options=options) #chromedriver.exe is in the root folder (same locations as the script)
    return driver

def clean_nr_plates(nr_plates):
    return re.sub(r'\W+', '', nr_plates)

def get_car_model_info(nr_plates, driver):
    url = f"https://immatriculation-auto.info/en/vehicle/{nr_plates}"
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '/html/body/main/astro-island/div[3]/div[4]/dl/dd[3]'))
        )
    except Exception as e1:
        print(f"First element not found: {e1}")
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '/html/body/main/astro-island/div[3]/div[5]/dl/dd[3]'))
            )
        except Exception as e2:
            print(f"Second element not found: {e2}")

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    car_info_div = soup.find('div', {'class': 'flex flex-col'})
    make = car_info_div.find('span', {'class': 'font-bold text-3xl'}).text.strip()
    model = car_info_div.find('span', {'class': 'font-semibold text-2xl'}).text.strip()
    year = car_info_div.find('span', {'class': 'text-xl'}).text.strip()

    dt_elements = soup.find_all('dt', class_='mt-2 text-sm opacity-90 font-light whitespace-pre-wrap')

    trim = ''
    for dt in dt_elements:
        if dt.text.strip() == 'Trim':
            dd = dt.find_next_sibling('dd')
            if dd:
                trim = dd.text.strip()
                break

    return make, model, year, trim

def button_click(driver, button, make, model, year):
    button.click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div/main/article/div/div[1]/div/div'))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    oil_capacity_p = soup.find('p', class_='mb-2', string=lambda x: x and 'litre' in x)

    return oil_capacity_p.text

def get_oil_capacity(make, model, year, trim, driver):
    url = f"https://oiltype.co/cars/{make}/{model}/{year}/"
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div/main/article/div/div[1]/div/div'))
    )

    buttons = driver.find_elements(By.CLASS_NAME, 'trimCollapse')
    exact_capacity_found = False
    button_model_match = ()

    for button in buttons:
        if model.lower() in button.text.lower() and trim.lower() in button.text.lower():
            exact_capacity_found = True
            return button_click(driver, button, make, model, year)
        elif model.lower() in button.text.lower() and not exact_capacity_found:
            button_model_match = (button, model)

    if not exact_capacity_found and len(button_model_match) == 0:
        return f"Oil capacity information not found for {model.capitalize()}"
    else:
        return button_click(driver, button_model_match[0], button_model_match[1], model, year)

@app.route('/get_oil_capacity', methods=['GET'])
def get_oil_capacity_route():
    nr_plates = request.args.get('nr_plates')
    clean_nr = clean_nr_plates(nr_plates)
    driver = initialize_driver()

    try:
        make, model, year, trim = get_car_model_info(clean_nr, driver)
        oil_capacity_info = get_oil_capacity(make, model, year, trim, driver)

        response = {
            'make': make.capitalize(),
            'model': model.capitalize(),
            'year': year,
            'trim': trim,
            'oil_capacity': oil_capacity_info
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
    # uUsage: open a web browser and navigate to:
    # http://127.0.0.1:5000/get_oil_capacity?nr_plates=FK207PD