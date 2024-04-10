import sqlite3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Edge()

driver.get("http://127.0.0.1:5000/signup")

# input information
role_select = driver.find_element(By.ID, "roles")
role_select.send_keys("Administrator")  # role
first_name_input = driver.find_element(By.ID, "new-userFirstName")
first_name_input.send_keys("haozhe")  # first name
last_name_input = driver.find_element(By.ID, "new-userLastName")
last_name_input.send_keys("xu")  # last name
password_input = driver.find_element(By.ID, "password")
password_input.send_keys("111")  # password

signup_button = driver.find_element(By.CLASS_NAME, "button1")
signup_button.click()


WebDriverWait(driver, 10).until(EC.url_to_be("http://127.0.0.1:5000/login"))

# check the url
assert "login" in driver.current_url

#check the database
conn = sqlite3.connect('tutorial.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM users WHERE name=?", ("John Doe",))
user = cursor.fetchone()
conn.close()
assert user is not None


driver.quit()