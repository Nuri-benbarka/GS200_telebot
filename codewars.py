from selenium import webdriver
import time
from bs4 import BeautifulSoup


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
    user = "Nuri-benbarka"
    katas = get_kata(user)
    # do something with the HTML data
    print(len(katas))
    print(katas)
