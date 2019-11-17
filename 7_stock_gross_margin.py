import os, sys, re, shutil, requests, bs4, subprocess, requests, math, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from datetime import datetime
from datetime import timedelta
import sqlite3

chrome_path = "C:\chromedriver\chromedriver.exe"
web = webdriver.Chrome(chrome_path)
web.get('http://mops.twse.com.tw/mops/web/t163sb06')

DateSearch = re.compile(r'(\d\d\d\d)/(\d\d)/(\d\d)')
end_date = datetime.today()
f = open('last_date_of_gross_margin.log',"r", encoding="utf-8")
start_date = f.readline()
start_date = start_date.replace('Last update of gross margin: ','')
start_date = start_date.replace('-','/')
Date = DateSearch.search(start_date)
Start_date = datetime(int(Date.group(1)), int(Date.group(2)), int(Date.group(3)))
f.close()

conn = sqlite3.connect('stock_list.db')
c = conn.cursor()

path = os.getcwd()
path = path + '\\stock_db'
os.chdir(path)
print(os.getcwd())

db_list = os.listdir(os.getcwd())

keystring0 = ['年度第一季', '年度第二季', '年度第三季', '年度第四季']
keystring1 = ['上市公司', '上櫃公司']

start_date_ptr = Start_date

end_season_num = int(math.ceil(float(end_date.month)/3))
end_date = end_date.replace(month = (end_season_num - 1)*3 + 1, day = 1)
while start_date_ptr < end_date:

    last_update_date = start_date_ptr
    input1 = web.find_element_by_id('year')
    input1.clear()
    input1.send_keys(str(start_date_ptr.year - 1911))

    s2 = Select(web.find_element_by_id('season'))
    season_num = int(math.ceil(float(start_date_ptr.month)/3))
    s2.select_by_value('0' + str(season_num))    
    
    s1 = Select(web.find_element_by_xpath("//select [@id='TYPEK']"))
    s1.select_by_value("sii")
    web.find_element_by_xpath("//input [@value=' 查詢 ']").click()
    time.sleep(30)
    soup = bs4.BeautifulSoup(web.page_source, "lxml")
    
    find_count = 0

    page_key_string = '\n' + keystring1[0] + str(start_date_ptr.year - 1911) + keystring0[season_num - 1] + '\n'
    table_keystring = soup.find_all(string=page_key_string)

    print(table_keystring)
    if table_keystring == []:
        break

    table_sons = soup.find('td', text = '公司代號')

    soup_cur_table = bs4.BeautifulSoup(str(table_sons.parent.parent), "lxml")
    trs = soup_cur_table.find_all('tr')
    for tr in trs:
        soup_cur_tr = bs4.BeautifulSoup(str(tr), "lxml")
        tds = soup_cur_tr.find_all('td')
        if len(tds) == 0:
            continue
        find_count = find_count + 1
        db_name = tds[0].getText().strip() + '.db'
        if db_name not in db_list:
            continue
        print(db_name)
        conn_stock = sqlite3.connect(db_name)
        c_stock = conn_stock.cursor()

        print(tds[3])
        if (tds[3].getText().strip().replace(',','') != '') and (tds[4].getText().strip().replace(',','') != '') and (tds[6].getText().strip().replace(',','') != ''):
            sql_cmd = 'UPDATE stock_quarter set gross_margin = ' + tds[3].getText().strip().replace(',','') + ', '\
                                                'operating_profit_margin = ' + tds[4].getText().strip().replace(',','') + ', '\
                                                'net_profit_margin =' + tds[6].getText().strip().replace(',','') +\
                        ' where date_ID =\'' + str(start_date_ptr.year) + '-' + str(season_num) + '\''
            print(sql_cmd)
            c_stock.execute(sql_cmd)
            conn_stock.commit()
        conn_stock.close()
    if find_count == 0:
        continue 

    s1 = Select(web.find_element_by_xpath("//select [@id='TYPEK']"))
    s1.select_by_value("otc")
    web.find_element_by_xpath("//input [@value=' 查詢 ']").click()
    time.sleep(30)
    soup = bs4.BeautifulSoup(web.page_source, "lxml")

    page_key_string = '\n' + keystring1[1] + str(start_date_ptr.year - 1911) + keystring0[season_num - 1] + '\n'
    table_keystring = soup.find_all(string=page_key_string)
    print(table_keystring)
    if table_keystring == []:
        break
    table_sons = soup.find('td', text = '公司代號')

    soup_cur_table = bs4.BeautifulSoup(str(table_sons.parent.parent), "lxml")
    trs = soup_cur_table.find_all('tr')
    for tr in trs:
        soup_cur_tr = bs4.BeautifulSoup(str(tr), "lxml")
        tds = soup_cur_tr.find_all('td')
        if len(tds) == 0:
            continue
        find_count = find_count + 1
        db_name = tds[0].getText().strip() + '.db'
        if db_name not in db_list:
            continue
        print(db_name)
        conn_stock = sqlite3.connect(db_name)
        c_stock = conn_stock.cursor()

        print(tds[3])
        if (tds[3].getText().strip().replace(',','') != '') and (tds[4].getText().strip().replace(',','') != '') and (tds[6].getText().strip().replace(',','') != ''):
            sql_cmd = 'UPDATE stock_quarter set gross_margin = ' + tds[3].getText().strip().replace(',','') + ', '\
                                                'operating_profit_margin = ' + tds[4].getText().strip().replace(',','') + ', '\
                                                'net_profit_margin =' + tds[6].getText().strip().replace(',','') +\
                        ' where date_ID =\'' + str(start_date_ptr.year) + '-' + str(season_num) + '\''
            print(sql_cmd)
            c_stock.execute(sql_cmd)
            conn_stock.commit()
        conn_stock.close()
    if find_count == 0:
        continue 

    if start_date_ptr.month > 9:
        start_date_ptr = start_date_ptr.replace(year = start_date_ptr.year + 1, month = 1)
    else:
        start_date_ptr = start_date_ptr.replace(month = start_date_ptr.month + 3)

path = os.getcwd()
path = path.replace('\\stock_db','')
os.chdir(path)
f= open('last_date_of_gross_margin.log',"w", encoding="utf-8")
f.write('Last update of gross margin: ' + str(last_update_date.year) + '-' + last_update_date.strftime("%m") + '-01')
f.close()
conn.close()
web.close()
