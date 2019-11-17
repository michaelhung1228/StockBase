import os, sys, re, shutil, requests, bs4, subprocess, requests, math, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from datetime import datetime
from datetime import timedelta
import sqlite3

DateSearch = re.compile(r'(\d\d\d\d)/(\d\d)/(\d\d)')
f = open('last_date_of_stock_holder.log',"r", encoding="utf-8")
start_date = f.readline()
start_date = start_date.replace('Last update of stock holder: ','')
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

chrome_path = "C:\chromedriver\chromedriver.exe"
web = webdriver.Chrome(chrome_path)
web.get('https://www.tdcc.com.tw/smWeb/QryStock.jsp')
time.sleep(10)

key_strings = ['400,001-600,000', '600,001-800,000', '800,001-1,000,000', '1,000,001以上']
key_string_total = '合　計'
holder_percentage = [0, 0, 0, 0]
print(key_strings[0])
#f= open('tmp.txt',"w", encoding="utf-8")
#f.write(web.page_source)
#f.close()

delta_7day = timedelta(days = 7) #delta_1day
delta_1day = timedelta(days = 1) #delta_1day
Start_date_ptr = Start_date
End_date = datetime.today()

while Start_date_ptr <= End_date:
    date_str = str(Start_date_ptr.year) + Start_date_ptr.strftime("%m") + Start_date_ptr.strftime("%d")
    print(date_str)
    soup = bs4.BeautifulSoup(web.page_source, "lxml")
    cursor = c.execute("SELECT stock_id, stock_name, start_date, stock_type, business  from stock_list")
    for current_entry in cursor:
        if ((current_entry[3] == '上櫃') or (current_entry[3] == '上市')) and (current_entry[4] != 'ETF'):
            db_name = current_entry[0] + '.db'
            conn_stock = sqlite3.connect(db_name)
            c_stock = conn_stock.cursor()
            print(db_name)
            date_tmp = current_entry[2]
            date_tmp = date_tmp.replace('-','/')
            Date = DateSearch.search(date_tmp)
            date_record = datetime(int(Date.group(1)), int(Date.group(2)), int(Date.group(3)))
            if Start_date_ptr <= date_record:
                continue
            cursor = c_stock.execute('SELECT max(date_ID) FROM stock_week') 
            max_id = cursor.fetchone()[0]
            if max_id != None:
                max_id = max_id.replace('-','/')
                Date = DateSearch.search(max_id)
                Start_date_cmp = datetime(int(Date.group(1)), int(Date.group(2)), int(Date.group(3)))
                if  Start_date_ptr <= Start_date_cmp:
                    continue
                #else:
                #    Start_date_ptr = Start_date_cmp + delta_7day
            #if max_id == str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d"):
            #    continue
            n = 0
            while 1:
                input1 = web.find_element_by_id('StockNo')
                input1.clear()
                if n == 0:
                    input1.send_keys(current_entry[0])
                else:
                    input1.send_keys(current_entry[0] + 'O')
                time.sleep(2)
                s1 = Select(web.find_element_by_id('scaDates'))
                s1.select_by_value(date_str)
                time.sleep(2)
                web.find_element_by_xpath("//input [@value='查詢']").click()
                time.sleep(2)
                soup = bs4.BeautifulSoup(web.page_source, "lxml")
                td = soup.find(string=key_strings[0])
                if n == 0:
                   n = 1
                else:
                   n = 0
                if td != None:
                    break
            n = 0
            for key_string in key_strings:
                td = soup.find(string=key_string)
                soup_temp = bs4.BeautifulSoup(str(td.parent.parent), "lxml")
                tds = soup_temp.find_all('td')
                #print(tds[4].getText().strip().replace(',',''))
                holder_percentage[n] = float(tds[4].getText().strip().replace(',',''))
                n = n + 1
            holder_400 = holder_percentage[0] + holder_percentage[1] + holder_percentage[2] + holder_percentage[3]
            holder_1000 = holder_percentage[3]
            holder_400 = round(holder_400, 2)
            holder_1000 = round(holder_1000, 2)
            print(holder_400)
            print(holder_1000)

            td = soup.find(string=key_string_total)
            soup_temp = bs4.BeautifulSoup(str(td.parent.parent), "lxml")
            tds = soup_temp.find_all('td')
            total_people = int(tds[2].getText().strip().replace(',',''))
            print(total_people)
            sql_cmd = 'INSERT or IGNORE INTO stock_week (date_ID, holder400_per, holder1000_per, total_people) VALUES (\'' + str(Start_date_ptr.year) + '-' + \
                  Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d") + '\',' + str(holder_400) + ',' \
                                                                                              + str(holder_1000) + ',' \
                                                                                              + str(total_people) + ')'
            print(sql_cmd)
            c_stock.execute(sql_cmd)
            conn_stock.commit()
            conn_stock.close()
    
    while 1:
        Start_date_ptr = Start_date_ptr + delta_1day
        date_str = str(Start_date_ptr.year) + Start_date_ptr.strftime("%m") + Start_date_ptr.strftime("%d")
        print(date_str)
        option_tmp = soup.find('option', value=date_str)
        if option_tmp != None:
            break
    path = os.getcwd()
    path = path.replace('\\stock_db','')
    os.chdir(path)
    f = open('last_date_of_stock_holder.log',"w", encoding="utf-8")
    f.write('Last update of stock holder: ' + str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d"))
    f.close()
    path = os.getcwd()
    path = path + '\\stock_db'
    os.chdir(path)


web.close()
conn.close()

