from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Edge()

driver.get("http://127.0.0.1:5000/login")

username_input = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "username")))

#input the username & password
password_input = driver.find_element(By.NAME, "password")
username_input.send_keys("haozhe xu")
password_input.send_keys("111")

# click the button
login_button = driver.find_element(By.ID, "btn_login")
login_button.click() 


WebDriverWait(driver, 10).until(EC.url_to_be("http://127.0.0.1:5000/adminHomePage"))
#check
assert driver.current_url == "http://127.0.0.1:5000/adminHomePage"

driver.quit()