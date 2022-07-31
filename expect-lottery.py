from lib2to3.pgen2 import driver
from re import A
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import shutil

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('chromedriver',options=options)
driver.implicitly_wait(10)

# # 全ての要素が読み込まれるまで待つ。タイムアウトは15秒
# WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)

# ----------------------------------------------------------------------------
# 当選番号のURLを取得
# ナンバーズ 1年以内の当選番号（A表）
def past_one_year_page_urls():
    past_winning_numbers_list_page_url = "https://www.mizuhobank.co.jp/retail/takarakuji/check/numbers/backnumber/index.html"
    driver.get(past_winning_numbers_list_page_url)
    html = driver.page_source.encode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    tr_tags = soup.find_all("tr", class_="js-backnumber-temp-a")
    # print(tr_tags)

    page_urls = []
    for tr_tag in tr_tags:
        td_tags = tr_tag.find_all("td")
        number3_page_url = td_tags[0].find("a").get("href")
        if number3_page_url != "":
            page_urls.append(number3_page_url)
    return page_urls


# 当選番号のURLを取得
# ナンバーズ 1年以上前の当選番号（B表）
def get_long_time_ago_page_urls():
    past_winning_numbers_list_page_url = "https://www.mizuhobank.co.jp/retail/takarakuji/check/numbers/backnumber/index.html"
    driver.get(past_winning_numbers_list_page_url)
    html = driver.page_source.encode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    page_urls = []
    tr_tags = soup.find_all("tr", class_="js-backnumber-temp-b")

    for tr_tag in tr_tags:
        for td_tag in tr_tag.find_all("td"):
            number3_page_url = td_tag.find("a").get("href")
            if number3_page_url != "":
                page_urls.append(number3_page_url)
            # page_urls.append(number3_page_url)
    return page_urls

# ----------------------------------------------------------------------------
# 当選番号をスクレイピング
# 1年以内の当選番号
def scrape_one_year_ago_winning_numbers(page_url):
    driver.get(page_url)

    # 最長で10秒待つ
    wait = WebDriverWait(driver,10)
    # # 全ての要素が読み込まれるまで待つ。タイムアウトは15秒
    # WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)
    time.sleep(3)
    # # 指定した要素が見えなくなるまで待機（display:noneが適用されるまで）
    # wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'js-now-loading')))

    html = driver.page_source.encode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    data = []

    table_tags = soup.find_all("table", class_="typeTK")
    for table_tag in table_tags:
        # 連想配列にデータを入れる
        item = {}

        tr_tags = table_tag.find_all("tr")
        item["name"] = tr_tags[0].find_all("th")[1].text
        item["date"] = tr_tags[1].find("td").text
        item["number3_lottery_number"] = tr_tags[2].find("td").text
        item["number4_lottery_number"] = None

        data.append(item)

    return data

# 当選番号をスクレイピング
# 1年以上前の当選番号
def scrape_long_year_ago_winning_numbers(page_url):
    driver.get(page_url)

    # 最長で10秒待つ
    wait = WebDriverWait(driver,10)
    # 全ての要素が読み込まれるまで待機。タイムアウトは15秒
    # WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)
    time.sleep(3)
    # 指定した要素が見えなくなるまで待機（display:noneが適用されるまで）
    # wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'js-now-loading')))

    html = driver.page_source.encode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    table_tag = soup.find("table", class_="typeTK")
    tr_tags = table_tag.find_all("tr")

    data = []
    for tr_tag in tr_tags[1:]:
        # 連想配列にデータを入れる
        item = {}
        th_tag = tr_tag.find("th")
        td_tags = tr_tag.find_all("td")

        item["name"] = th_tag.text
        item["date"] = td_tags[0].text
        item["number3_lottery_number"] = td_tags[1].text
        item["number4_lottery_number"] = td_tags[1].text

        data.append(item)

    return data

# ----------------------------------------------------------------------------
# 全ての当選番号をスクレイピング
# スクレイピングした結果をdata.jsonに出力する 
def scrape_all_winning_numbers(data_path):
    all_scraped_data = []
    for info_url in past_one_year_page_urls():
        time.sleep(1)
        scraped_data_one_year_ago = scrape_one_year_ago_winning_numbers(page_url="https://www.mizuhobank.co.jp{}".format(info_url))
        all_scraped_data = all_scraped_data + scraped_data_one_year_ago
        print(len(all_scraped_data))

    for info_url in get_long_time_ago_page_urls():
        time.sleep(1)
        scraped_data_long_year_ago = scrape_long_year_ago_winning_numbers(page_url="https://www.mizuhobank.co.jp{}".format(info_url))
        all_scraped_data = all_scraped_data + scraped_data_long_year_ago
        print(len(all_scraped_data))

    my_dict =  {}
    my_dict["items"] = all_scraped_data

    with open(data_path,mode='w', encoding="utf-8") as f:
        json.dump(my_dict,f, indent=2, ensure_ascii=False)
# ----------------------------------------------------------------------------
# json_dataにある当選番号を分析する
# ・下3桁で当選番号が少ない順に出力する
# ・下2桁で当選番号が多い順に出力する
def analysis_data(json_data_path):
    with open(json_data_path, "r", encoding="utf-8") as f:
        backup_data = json.load(f)

    analysis = {}
    for i in range(1000):
        # 3桁で0埋め
        key = str(i).zfill(3)
        analysis[key] = 0

    print("---------------------------------------------------------------")
    print("予想される平均当選回数（下3桁）=")
    print(len(backup_data["items"])/1000)
    print("---------------------------------------------------------------")
    for d in backup_data["items"]:
        nlm = d["number3_lottery_number"]
        tmp = analysis[nlm]
        analysis[nlm] = tmp + 1

    sorted_analysis = sorted(analysis.items(), key=lambda x:x[1])
    print("当選回数の少ない順で並び替え結果（下3桁）")
    print(sorted_analysis)
    print("---------------------------------------------------------------")
    numbers_mini_analysis = {}
    for i in range(100):
        # 2桁で0埋め
        key = str(i).zfill(2)
        numbers_mini_analysis[key] = 0

    print("---------------------------------------------------------------")
    print("予想される平均当選回数（下2桁）=")
    print(len(backup_data["items"]) / 100)
    print("---------------------------------------------------------------")
    for d in backup_data["items"]:
        nlm = d["number3_lottery_number"]
        # 下2桁だけを抽出
        key = nlm[-2:]
        numbers_mini_analysis[key] = numbers_mini_analysis[key] + 1
    print("---------------------------------------------------------------")
    sorted_numbers_mini_analysis= sorted(numbers_mini_analysis.items(), key=lambda x:x[1], reverse=True)
    print("当選回数の多い順で並び替え結果（下2桁）")
    print(sorted_numbers_mini_analysis)
    print("---------------------------------------------------------------")

# ----------------------------------------------------------------------------
if __name__ == "__main__":
    data_path = '.\data.json'
    # scrape_all_winning_numbers(data_path=data_path)
    analysis_data(json_data_path=data_path)
