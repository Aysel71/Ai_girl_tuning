import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import requests

# Create folder
folder_name = "model_images"
abs_path = os.path.abspath(folder_name)
os.makedirs(folder_name, exist_ok=True)
print(f"Created folder: {folder_name}")

# Setup WebDriver
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Set download preferences
prefs = {
    "download.default_directory": abs_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 15)
actions = ActionChains(driver)

try:
    # Open Google Image Search
    search_url = "https://www.google.com/search?q=gorgeous+models+full+body&tbm=isch"
    driver.get(search_url)
    print("Page loaded, waiting for elements...")
    time.sleep(3)

    # Find images using exact class structure
    print("Looking for images...")
    image_elements = wait.until(EC.presence_of_all_elements_located((
        By.CSS_SELECTOR,
        "div.eA0Zlc.WghbWd.FnEtTd.mkpRId.m3LIae.RLdvSe.qyKxnc.ivg-i.PZPZlf.GMCzAd"
    )))[:5]  # Limit to first 5 images
    
    print(f"Found {len(image_elements)} image elements")

    for index, image_element in enumerate(image_elements):
        try:
            print(f"\nProcessing image {index + 1}/5")
            
            # Scroll and click
            driver.execute_script("arguments[0].scrollIntoView(true);", image_element)
            time.sleep(1)
            
            try:
                image_element.click()
            except:
                driver.execute_script("arguments[0].click();", image_element)
            
            print("Waiting 3 seconds...")
            time.sleep(3)
            
            # Find the large image
            large_image = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "img[src][jsname='kn3ccd']"
            )))
            high_quality_url = large_image.get_attribute("src")

            # Download the image using requests
            if high_quality_url and high_quality_url.startswith("http"):
                response = requests.get(high_quality_url, stream=True)
                if response.status_code == 200:
                    file_path = os.path.join(folder_name, f"model_{index + 1}.jpg")
                    with open(file_path, "wb") as file:
                        for chunk in response.iter_content(1024):
                            file.write(chunk)
                    print(f"Saved image {index + 1} to {file_path}")
                else:
                    print(f"Failed to download image {index + 1}: HTTP {response.status_code}")
            else:
                print(f"No valid URL found for image {index + 1}")

            # Close the image viewer
            close_button = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "button[jsname='tJiF1e']"
            )))
            close_button.click()
            time.sleep(1)

        except Exception as e:
            print(f"Error processing image {index + 1}: {str(e)}")
            # Try to close viewer if open
            try:
                driver.find_element(By.CSS_SELECTOR, "button[jsname='tJiF1e']").click()
            except:
                pass

except Exception as e:
    print(f"An error occurred:")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")

finally:
    time.sleep(2)
    driver.quit()
    print(f"\nProcess complete! Check the '{folder_name}' folder for your images.")

