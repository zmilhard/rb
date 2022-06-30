from multiprocessing.connection import wait
import string
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import pandas as pd


def waitPresenceAllElements(driver, locator, timeSec):
    wait = WebDriverWait(driver, timeSec)
    try: 
        wait.until(EC.presence_of_all_elements_located((By.XPATH, locator)))
    except Exception as e:
        raise e


def waitVisibilityElement(driver, locator, timeSec):
    wait = WebDriverWait(driver, timeSec)
    try: 
        wait.until(EC.visibility_of_element_located((By.XPATH, locator)))
    except Exception as e:
        raise e


def isNextButtonDisabled(driver):
    nextButtonPath = "//li[@class='next_page']/*"
    waitVisibilityElement(driver, nextButtonPath, 10)
    nextButton = driver.find_element(By.XPATH, nextButtonPath)
    return "disabled" in nextButton.get_attribute("class")

URL = "url"
ID = "id"
TITLE = "title"
TAG = "tags"
DESCRIPTION = "description"

output = {
    URL : [],
    ID : [],
    TITLE : [],
    TAG : [],
    DESCRIPTION : []
}
## Hit manage profile url. Log in. Wait for manage profile page to load
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    driver.get("https://www.redbubble.com/portfolio/manage_works")

    emailPath = "//*[text()='Email or Username']/preceding-sibling::input"
    emailInput = driver.find_element(By.XPATH, emailPath)
    emailInput.send_keys("CHANGEME")

    passwordPath = "//*[text()='Password']/preceding-sibling::input"
    passwordInput = driver.find_element(By.XPATH, passwordPath)
    passwordInput.send_keys("CHANGEME")

    loginButtonPath = "//span[text()='Log In']/ancestor::button"
    loginInput = driver.find_element(By.XPATH, loginButtonPath)
    loginInput.click()

    allWorksPath = "//div[@class='works_work']"
    waitPresenceAllElements(driver, allWorksPath, 15)

    # 20% offer popup appears
    couponPath = "//div[@aria-label='Modal Overlay Box']"
    waitVisibilityElement(driver, couponPath, 30)
    action = ActionChains(driver)
    action.send_keys(Keys.ESCAPE)
    action.perform()

    allGearsPath = "//div[@class='works_work-menu-link']"
    numGears = len(driver.find_elements(By.XPATH, allGearsPath))



    while(not(isNextButtonDisabled(driver))):#count of enabled next buttons is > 0):
        print("yo")
        for i in range(numGears):
            allGears = driver.find_elements(By.XPATH, allGearsPath)
            allGears[i].click()

            #xpath one based index - python 0
            editPath = f"(//div[@class='works_work-menu dropdown-with-arrow'])[{i+1}]//a[text()='Edit']"
            waitVisibilityElement(driver, editPath, 5)
            driver.find_element(By.XPATH, editPath).click()

            productRowPath = "//div[@class='product-row']"
            waitPresenceAllElements(driver, productRowPath, 15)

            urlPath = "//a[@class='public-url']"
            url = driver.find_element(By.XPATH, urlPath).text
            id = url[url.rfind('/') + 1:]

            englishPath = "//div[@class='add-work-details__language-inputs' and @data-language-inputs='en']"
            
            titlePath = englishPath + "//label[contains(text(),'Title (required)')]/following-sibling::input"
            titleElement = driver.find_element(By.XPATH, titlePath)
            title = driver.execute_script("return arguments[0].value", titleElement)

            tagsPath = englishPath + "//label[contains(text(),'Tags')]//following-sibling::textarea"
            tags = driver.find_element(By.XPATH, tagsPath).text

            descriptionPath = englishPath + "//label[contains(text(),'Description')]//following-sibling::textarea"
            description = driver.find_element(By.XPATH, descriptionPath).text

            output[URL].append(url)
            output[ID].append(id)
            output[TITLE].append(title)
            output[TAG].append(tags)
            output[DESCRIPTION].append(description)

            

            driver.back()
            waitPresenceAllElements(driver, allWorksPath, 15)

            print("yo")
        
        driver.find_element(By.XPATH, "//li[@class='next_page']/*").click()
        waitPresenceAllElements(driver, allWorksPath, 15)

    df = pd.DataFrame.from_dict(data=output, orient="columns")
    df.to_csv("./items.csv")




finally:
    driver.quit()


