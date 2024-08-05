from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import threading
import time
import os

app = Flask(__name__)
driver = None
is_running = False
remaining_users = 0
current_user = "None"
estimated_time = "0h 0m 0s"
start_time = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start():
    global driver, is_running, remaining_users, current_user, estimated_time, start_time

    username = request.form["username"]
    password = request.form["password"]
    file = request.files["file"]

    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)

    is_running = True
    start_time = time.time()

    def unfollow_users():
        global remaining_users, current_user, estimated_time

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.get("https://www.instagram.com/accounts/login/")

        # Login
        time.sleep(2)
        username_input = driver.find_element(By.NAME, 'username')
        password_input = driver.find_element(By.NAME, 'password')
        username_input.send_keys(username)
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)

        df = pd.read_csv(file_path)
        remaining_users = len(df)
        initial_users = remaining_users

        if remaining_users == 0:
            driver.quit()
            return

        usernames = df['Not Following Back'].tolist()
        for user in usernames:
            if not is_running:
                driver.quit()
                return

            current_user = user
            driver.get(f"https://www.instagram.com/{user}/")
            time.sleep(5)

            try:
                unfollow_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "_acan") and contains(@class, "_acap") and contains(@class, "_acat")]'))
                )
                unfollow_button.click()
                time.sleep(2)

                unfollow_confirm_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div/div[8]'))
                )
                unfollow_confirm_button.click()
                time.sleep(2)

                df = df[df['Not Following Back'] != user]
                df.to_csv(file_path, index=False)
                remaining_users -= 1

                elapsed_time = time.time() - start_time
                estimated_seconds = remaining_users * (elapsed_time / (initial_users - remaining_users + 1))
                estimated_time = time.strftime("%Hh %Mm %Ss", time.gmtime(estimated_seconds))

                time.sleep(10)  # Adjust the time gap between unfollow actions as needed
            except Exception as e:
                print(f"Failed to unfollow {user}: {e}")
                continue

    threading.Thread(target=unfollow_users).start()
    return jsonify(status="Started", remaining_users=remaining_users, current_user=current_user, estimated_time=estimated_time)

@app.route("/stop", methods=["POST"])
def stop():
    global is_running
    is_running = False
    return jsonify(status="Stopped")

if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True)
