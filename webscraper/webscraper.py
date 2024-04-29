from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from datetime import datetime
import motor.motor_asyncio
from decouple import config
import asyncio


nyt_connections_url = "https://www.nytimes.com/games/connections"
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

daily_categories = {} # category: [answers]
author = ""

current_date = datetime.now()
formatted_date = current_date.strftime('%Y-%m-%d')

MONGO_DETAILS = config("MONGO_DETAILS")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.Connections
connections = database.get_collection("Connections")

def create_connections_db_entry():
    categories = []
    for c in daily_categories.keys():
        cleaned_category = {
            "category": c,
            "words": daily_categories[c]
        }
        categories.append(cleaned_category)

    data_to_insert = {
        "_id": formatted_date,
        "author": author,
        "categories": categories
    }
    return data_to_insert

async def insert_document(data):
    result = await connections.insert_one(data)
    print(f"Inserted document with ID: {result.inserted_id}")
        
def debug_element(elem):
    print("Element HTML:", elem.get_attribute('outerHTML'))

def debug_page():     
    with open('connections.html', 'w') as f:
        f.write(driver.page_source)

def print_author():
    print(author[0])

def print_categories():
    for category in daily_categories.keys():
        print(category)
        print(daily_categories[category])

def clean_author(author):
    # lol are there no more authors?
    return author.replace('By ', '')

def init_driver():
    driver.get(nyt_connections_url)
    assert "Connections:" in driver.title

# def fetch_connections():
#     # Wait for the element with the 'board' id to be present
#     board = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.ID, "board"))
#     )

#     board_html = board.get_attribute('outerHTML')

#     # parse the html
#     soup = BeautifulSoup(board_html, 'html.parser')
#     items = soup.find_all(class_='item')
#     for item in items:
#         daily_connections.append(item.text)

# def fetch_author():
#     # Wait for the author element to be present
#     author_elem = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CLASS_NAME, "pz-moment__info-editor"))
#     )
#     auth = clean_author(author_elem.text)
#     author.append(auth)

def play_connections():
    play = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "pz-moment__button")) # warning: multiple classes use this tag... but correct button is first
    )
    time.sleep(3)
    play.click()
    time.sleep(3)

    # help modal no longer pops up?
    # x = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.ID, "close-help"))
    # )
    # x.click()
    # time.sleep(3) # time increase to 3 seconds to hopefully avoid rendering issues

    board = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "default-choices"))
    )
    submit = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='submit-btn']"))
    )


    def select_row(num=0):
        for i in range(num, num+4):
            try:
                word = board.find_element(By.CSS_SELECTOR, f"[for=inner-card-{i}]")
            except:
                print("failed to find word element")
                print("must mean guessed correctly")
                return

            word.click()

    # 'play the board'
    for i in [0, 4, 8]:
        select_row(i)
        submit.click()
        time.sleep(2)
        select_row(i) # deselect guess

    select_row(12)
    submit.click()

    time.sleep(12) # wait for the puzzle to finish
    

    # grab answers again as answers have populated
    categories = board.find_elements(By.CSS_SELECTOR, "[data-testid='solved-category-container']")
    for category in categories:
        soup = BeautifulSoup(category.get_attribute('outerHTML'), 'html.parser')
        cat = soup.find('h3').text
        daily_categories[cat] = []
        answers = soup.find_all('li')
        for answer in answers:
            daily_categories[cat].append(answer.text)
     
    return

async def fetch_and_insert():
    # TODO: handle selenium errors
    play_connections()
    await insert_document(create_connections_db_entry())
    # TODO: handle insertion errors?
    driver.close()

async def main():
    await fetch_and_insert()

if __name__ == '__main__':
    init_driver()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    