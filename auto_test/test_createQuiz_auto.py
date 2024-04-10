import sqlite3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 启动浏览器
driver = webdriver.Edge()

# 打开创建 Quiz 页面
driver.get("http://127.0.0.1:5000/createQuiz")

# 输入表单数据
quiz_name_input = driver.find_element(By.ID, "quizName")
quiz_name_input.send_keys("Test Quiz")  # 输入 Quiz 名称

# 添加第一道题目
question_input = driver.find_element(By.NAME, "question_1")
question_input.send_keys("What is the capital of France?")  # 输入题目

option_a_input = driver.find_element(By.NAME, "optionA_1")
option_a_input.send_keys("London")  # 输入选项 A

option_b_input = driver.find_element(By.NAME, "optionB_1")
option_b_input.send_keys("Paris")  # 输入选项 B

option_c_input = driver.find_element(By.NAME, "optionC_1")
option_c_input.send_keys("Berlin")  # 输入选项 C

option_d_input = driver.find_element(By.NAME, "optionD_1")
option_d_input.send_keys("Rome")  # 输入选项 D

answer_input = driver.find_element(By.NAME, "answer_1")
answer_input.send_keys("Paris")  # 输入答案

# 添加第二道题目
driver.find_element(By.XPATH, "//button[text()='Add Question']").click()  # 点击添加题目按钮

question_input = driver.find_element(By.NAME, "question_2")
question_input.send_keys("What is the capital of Germany?")  # 输入题目

option_a_input = driver.find_element(By.NAME, "optionA_2")
option_a_input.send_keys("London")  # 输入选项 A

option_b_input = driver.find_element(By.NAME, "optionB_2")
option_b_input.send_keys("Paris")  # 输入选项 B

option_c_input = driver.find_element(By.NAME, "optionC_2")
option_c_input.send_keys("Berlin")  # 输入选项 C

option_d_input = driver.find_element(By.NAME, "optionD_2")
option_d_input.send_keys("Rome")  # 输入选项 D

answer_input = driver.find_element(By.NAME, "answer_2")
answer_input.send_keys("Berlin")  # 输入答案

# 提交表单
driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

# 等待页面跳转
WebDriverWait(driver, 10).until(EC.url_to_be("http://127.0.0.1:5000/createQuiz"))

# 检查数据库中是否存在新的 Quiz
conn = sqlite3.connect('tutorial.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM quiz WHERE QuizName=?", ("Test Quiz",))
quiz = cursor.fetchone()
conn.close()

# 验证新的 Quiz 是否成功添加到数据库中
assert quiz is not None

# 关闭浏览器
driver.quit()