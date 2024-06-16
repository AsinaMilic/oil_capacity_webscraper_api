from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox') #for Linux
    options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})
    driver = webdriver.Chrome(options=options) #chromedriver.exe is in the root folder (same locations as the script)
    return driver

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
 
    # Extract the page source after JavaScript has run
    soup = BeautifulSoup(driver.page_source, 'html.parser')
        
    # Extract car information based on the HTML structure provided
    car_info_div = soup.find('div', {'class': 'flex flex-col'})
    make = car_info_div.find('span', {'class': 'font-bold text-3xl'}).text.strip()
    model = car_info_div.find('span', {'class': 'font-semibold text-2xl'}).text.strip()
    year = car_info_div.find('span', {'class': 'text-xl'}).text.strip()
        
    # Find all <dt> elements
    dt_elements = soup.find_all('dt', class_='mt-2 text-sm opacity-90 font-light whitespace-pre-wrap')
        
    trim = ''  # Default value in case the trim is not found
    for dt in dt_elements:
        if dt.text.strip() == 'Trim':
            # Get the next sibling <dd> element
            dd = dt.find_next_sibling('dd')
            if dd:
                trim = dd.text.strip()
                break
        
    return make, model, year, trim


def button_click(driver, button, make, model, year):
    button.click()
    # Wait for the expanded content to be visible
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div/main/article/div/div[1]/div/div'))
    )

    # Refetch the HTML content after clicking the button
    soup = BeautifulSoup(driver.page_source, 'html.parser')
                
    # Find the <p> element with 'Service fill' text
    oil_capacity_p = soup.find('p', class_='mb-2', string=lambda x: x and 'litre' in x)

    return oil_capacity_p.text          


def get_oil_capacity(make, model, year, trim, driver):
    # Construct the URL
    url = f"https://oiltype.co/cars/{make}/{model}/{year}/"
    
    # Open the URL
    driver.get(url)
        
    # Wait for the buttons to load
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div/main/article/div/div[1]/div/div'))
    )
        
    # Find all the button elements for different models
    buttons = driver.find_elements(By.CLASS_NAME, 'trimCollapse')
    exact_capacity_found = False
    button_model_match = ()
    # Loop through the buttons to find the first match
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


# Initialize WebDriver
driver = initialize_driver()

# Example usage
nr_plates = "FK207PD"  
make, model, year, trim = get_car_model_info(nr_plates, driver)
oil_capacity_info = get_oil_capacity(make, model, year, trim, driver)

if len(oil_capacity_info) > 1:
    print(f"Oil Capacity for {make.capitalize()} {model.capitalize()} {year}:\n{oil_capacity_info}")
else:
    print(f"Oil capacity information not found for {make.capitalize()} {model.capitalize()} {year}.")

driver.quit()
