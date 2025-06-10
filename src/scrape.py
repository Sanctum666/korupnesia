from bs4 import BeautifulSoup
from selenium import webdriver

# API HIT: GET https://korupedia.transparansi.id/detail-koruptor/?key=6&no=267
#
# KEY: 6
# NO: 11 MIN
# NO: 360 MAX

# h1 .entry-title nama-hakim untuk nama koruptor
# .tbl-clean->tbody->tr->td widht='20%' foto koruptor
# .content-body parse aja nnti datanya di pick lagi

# CSR LMFAOO GIMME SSR PAGE THIS STUFF DONT NEED TO BE DYNAMIC ITS NOT EVEN UP-TO-DATE
URL = "https://korupedia.transparansi.id/detail-koruptor/?key=6&no=155" 
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

options = Options()
# options.add_argument("--headless")
options.binary_location = "/usr/bin/firefox"
service = FirefoxService("./geckodriver")  
driver = webdriver.Firefox(service=service, options=options)



for i in range(11, 360):
    url = f"https://korupedia.transparansi.id/detail-koruptor/?key=6&no={i}"
    driver.get(url)
    
    # Wait for the page to load completely
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    
    # Get the page source (HTML content)
    page_source = driver.page_source
    
    # Save to a file
    with open(f"data/data_{i}.html", "w", encoding="utf-8") as file:
        file.write(page_source)
        print("HTML saved successfully.")
    

driver.quit()
