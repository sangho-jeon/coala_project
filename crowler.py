from selenium import webdriver
import time
import csv

'''
100개씩 두번
appID, 이름, rating, 24peak, tags
누락될 수 있는 요소: rating -> app type 으로 필터
'''

start_num = 664
max_num = 750


def csv2list(filename):
    file = open(filename, 'r')
    csv_file = csv.reader(file)
    lists = list()
    for item in csv_file:
        lists.append(item)
    file.close()
    return lists


all_tags = csv2list('form.csv')
all_tags[0] = all_tags[0][5:]
all_tags = all_tags[0]

f = open('train_.csv', 'a', encoding='utf-8', newline='')
# wr = csv.writer(f)

driver = webdriver.Chrome("./chromedriver")
driver.implicitly_wait(10)
driver.get("https://steamdb.info/graph/")

show_count = driver.find_element_by_css_selector("div#table-apps_length select")
for option in show_count.find_elements_by_tag_name('option'):
    if option.text == 'All':
        option.click()
        break
time.sleep(2)

'''
container1(app type, name): div.span8 tr[]1,2
container2 (24-hour player peak): ul.app-chart-numbers li[1] strong
rating: div.header-thing-number.header-thing-good 하나만
tags: div#prices a.btn-tag
'''

for i in range(start_num, max_num):
    app_ids = driver.find_elements_by_css_selector("tr.app a")
    driver.implicitly_wait(10)
    id = app_ids[i].text
    url = "app/" + app_ids[i].text + "/graphs/"
    driver.get("https://steamdb.info/" + url)
    time.sleep(1)
    con1 = driver.find_elements_by_css_selector("div.span8 tr")
    app_type = con1[1].text
    app_type = app_type[9:]
    if app_type != 'Game':
        # wr.writerow(i, 'NULL')
        # 뒤로가기 후 show All
        print(i, ' NULL')
        back = driver.find_elements_by_css_selector("ul.header-navbar li")
        back_to = back[7]
        back_to.click()
        show_count = driver.find_element_by_css_selector("div#table-apps_length select")
        for option in show_count.find_elements_by_tag_name('option'):
            if option.text == 'All':
                option.click()
                break
        time.sleep(2)
        continue
    name = con1[2].text
    name = name.replace('Name ', '')

    rat = driver.find_element_by_css_selector("div.header-thing-number").text
    rat = rat[-3:-1]
    con2 = driver.find_elements_by_css_selector("ul.app-chart-numbers li")
    peak = con2[1].find_element_by_css_selector("strong").text
    peak = peak.replace(',', '')
    try:
        contact2 = driver.find_element_by_css_selector("a#tab-prices")
        contact2.click()
        tags = driver.find_elements_by_css_selector("div#prices a.btn-tag")
        temp_tag = [0]*408
        for t in tags:
            for j in range(408):
                if all_tags[j] == t.text:
                    temp_tag[j] = 1
                    break
    except BaseException:
        temp_tag = ['NULL']

    # print("###", i)
    # print(id)
    # print(name)
    # print(rat+'%')
    # print(peak)
    # print(temp_tag)


    # 한 게임에 대한 정보를 리스트에 추가후 csv 파일에 한 행씩 추가
    temp_lst = list()
    temp_lst.append(i)
    temp_lst.append(id)
    temp_lst.append(name)
    temp_lst.append(rat)
    temp_lst.append(peak)
    temp_lst = temp_lst+temp_tag
    print(temp_lst)

    # wr.writerow(temp_lst)

    # 뒤로가기 후 show All
    time.sleep(0.5)
    back = driver.find_elements_by_css_selector("ul.header-navbar li")
    back_to = back[7]
    back_to.click()
    show_count = driver.find_element_by_css_selector("div#table-apps_length select")
    for option in show_count.find_elements_by_tag_name('option'):
        if option.text == 'All':
            option.click()
            break
    time.sleep(2)

driver.close()
f.close()
