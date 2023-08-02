import datetime

from selenium import webdriver
import time
from bs4 import BeautifulSoup
import gspread


def get_kata(user):
    # set up the driver
    driver = webdriver.Chrome()
    url = "https://www.codewars.com/users/" + user + "/completed"

    driver.get(url)

    # scroll down to the bottom of the page
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # wait for the page to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # get the full HTML data
    html = driver.page_source

    # Create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')

    kata_list = []
    for kata in \
            soup.contents[0].contents[1].contents[0].contents[0].contents[3].contents[4].contents[1].contents[
                0].contents[
                1].contents:
        kata_list.append(kata.contents[0].contents[0].contents[0].contents[1].contents[0])

    # close the driver
    driver.quit()

    return kata_list


if __name__ == '__main__':
    gc = gspread.service_account(filename="my-drive-575757-6d5fe30b79ac.json")

    sh = gc.open("GS200_spring_2023")
    codewars_worksheet = sh.worksheet("codewars")

    users_list = codewars_worksheet.row_values(2)

    now = datetime.datetime.now()
    for j, user in enumerate(users_list):
        if user != "":

            try:
                kata_list = get_kata(user)
            except IndexError:
                print(f"{user} not a valid user")
                continue
            except AttributeError:
                print(f"{user} zero questions")
                continue

            i = j + 1

            if i <= 26:
                codewars_worksheet.update(chr(ord("@") + i) + "3", now.strftime('%m/%d/%y %H:%M:%S'))
                codewars_worksheet.update(
                    chr(ord("@") + i) + "5:" + chr(ord("@") + i) + str(5 + len(kata_list)),
                    [[x] for x in kata_list])

            else:
                codewars_worksheet.update(chr((ord("@") + i - ord("A")) // 26 + ord("@")) + chr(
                    (ord("@") + i - ord("A")) % 26 + ord("A")) + "3", now.strftime('%m/%d/%y %H:%M:%S'))
                codewars_worksheet.update(
                    chr((ord("@") + i - ord("A")) // 26 + ord("@")) + chr(
                        (ord("@") + i - ord("A")) % 26 + ord("A")) + "5:" + chr(
                        (ord("@") + i - ord("A")) // 26 + ord("@")) + chr(
                        (ord("@") + i - ord("A")) % 26 + ord("A")) + str(5 + len(kata_list)),
                    [[x] for x in kata_list])
            print(f"{user} updated")
