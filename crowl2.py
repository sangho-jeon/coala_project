from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import csv

start = 1170
end = 2000


def csv2list(filename):
    file = open(filename, 'r', encoding='utf-8')
    csv_file = csv.reader(file)
    lists = list()
    for item in csv_file:
        lists.append(item)
    file.close()
    return lists


all_names = csv2list('twitch_games.csv')
id_lst = []


f = open('twitch_game_ids.csv', 'w', encoding='utf-8', newline='')
wr = csv.writer(f)

driver = webdriver.Chrome("./chromedriver")
driver.implicitly_wait(10)
driver.get("https://steamdb.info/graph/")

for j in range(start, end):
    print('#', j)
    search = driver.find_element_by_css_selector('input#js-header-search')
    key = all_names[j][0]
    search.send_keys(key)
    search.send_keys(Keys.RETURN)
    driver.implicitly_wait(10)
    app_id = driver.find_element_by_css_selector('tr.app a').text
    print(app_id)
    id_lst.append(app_id)
    back = driver.find_elements_by_css_selector("ul.header-navbar li")
    back_to = back[7]
    back_to.click()
    driver.implicitly_wait(10)
wr.writerow(id_lst)
driver.close()
f.close()