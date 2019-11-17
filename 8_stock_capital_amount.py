import os, sys, re, shutil, requests, bs4, subprocess, requests, math, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from datetime import datetime
from datetime import timedelta
import sqlite3

chrome_path = "C:\chromedriver\chromedriver.exe"
web = webdriver.Chrome(chrome_path)
web.get('http://mops.twse.com.tw/mops/web/t05st03')

String_Search = re.compile(r'(\(.*?\))')

conn = sqlite3.connect('stock_list.db')
c = conn.cursor()
cursor = c.execute("SELECT stock_id, stock_name, start_date, stock_type, business  from stock_list")

path = os.getcwd()
path = path + '\\stock_db'
os.chdir(path)
print(os.getcwd())

for current_entry in cursor:
    cannot_find = 0
    if ((current_entry[3] == '上櫃') or (current_entry[3] == '上市')) and (current_entry[4] != 'ETF'):
        input1 = web.find_element_by_id('co_id')
        input1.clear()
        input1.send_keys(current_entry[0])
        n = 0
        while 1:
            web.find_element_by_xpath("//input [@value=' 查詢 ']").click()
            time.sleep(7)
            soup = bs4.BeautifulSoup(web.page_source, "lxml")
            table_keystring = soup.find('th', string='已發行普通股數或TDR原股發行股數')
            n = n + 1
            if table_keystring != None:
                break
            elif n == 5:
                cannot_find = 1
                break
        if cannot_find == 1:
            continue
        print(table_keystring)
        next_td_tag = table_keystring.findNext('td')
        result = String_Search.search(next_td_tag.getText())
        capital_amount = next_td_tag.getText().replace(result.group(1),'').strip().replace(',','').replace('股','')
        db_name = current_entry[0] + '.db'
        print(db_name)
        print(capital_amount)
        conn_stock = sqlite3.connect(db_name)
        c_stock = conn_stock.cursor()
        sql_cmd = 'REPLACE INTO stock_info (date_ID, capital_amount) VALUES (1,' + capital_amount + ')'
        print(sql_cmd)
        c_stock.execute(sql_cmd)
        conn_stock.commit()
        conn_stock.close()

path = os.getcwd()
path = path.replace('\\stock_db','')
os.chdir(path)

conn.close()
web.close()
