import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Edge()
driver.get("http://127.0.0.1:5000/quizPage_student")
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "form")))
# get all optinons
options = driver.find_elements(By.XPATH, "//form/div[@class='question']")
#auto_answer
#correct 1 $ incorrect 1
student_answers = {}
for index, option in enumerate(options):
    question_number = index + 1
    options_list = option.find_elements(By.XPATH, ".//input[@type='radio']")
    if question_number % 2 != 0:
        options_list[1].click()
        student_answers[question_number] = options_list[0].get_attribute("value")
    else:
        options_list[1].click()
        student_answers[question_number] = options_list[1].get_attribute("value")

#submit
submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
submit_button.click()


WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "results")))
#result
result_elements = driver.find_elements(By.XPATH, "//div[@class='results']/ul/li")
#check the result
result = {}
for result_element in result_elements:
    question_number = result_element.text.split(":")[0].split(" ")[1]
    answer_status = result_element.text.split(":")[1].strip()
    result[int(question_number)] = answer_status

expected_result = {1: "Correct", 2: "Incorrect"}
assert result == expected_result, "Test failed: Expected result doesn't match the actual result"


driver.quit()