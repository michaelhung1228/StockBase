import os, sys, re, shutil, requests, bs4, subprocess, requests, math, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from datetime import datetime
from datetime import timedelta
import sqlite3

chrome_path = "C:\chromedriver\chromedriver.exe"
web = webdriver.Chrome(chrome_path)
web.get('http://mops.twse.com.tw/mops/web/t163sb04')

DateSearch = re.compile(r'(\d\d\d\d)/(\d\d)/(\d\d)')
end_date = datetime.today()
f = open('last_date_of_eps.log',"r", encoding="utf-8")
start_date = f.readline()
start_date = start_date.replace('Last update of EPS: ','')
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
keystring0 = ['上市公司第一季資料', '上市公司第二季資料', '上市公司第三季資料', '上市公司第四季資料']
keystring1 = ['上櫃公司第一季資料', '上櫃公司第二季資料', '上櫃公司第三季資料', '上櫃公司第四季資料']

start_date_ptr = Start_date

end_season_num = int(math.ceil(float(end_date.month)/3))
end_date = end_date.replace(month = (end_season_num - 1)*3 + 1, day = 1)
while start_date_ptr < end_date:
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

    table_keystring = soup.find_all(string=keystring0[season_num - 1])
    print(table_keystring)
    if table_keystring == []:
        break

    table_sons = soup.find_all(string='基本每股盈餘（元）')
    for table_son in table_sons:
        soup_cur_table = bs4.BeautifulSoup(str(table_son.parent.parent.parent), "lxml")
        n = 0
        ths = soup_cur_table.find_all('th')
        for th in ths:
            if th.getText().strip() == '基本每股盈餘（元）':
                break
            else:
                n = n + 1
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
            cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_quarter')
            date_ID_str = cursor_stock.fetchone()[0]
            if date_ID_str == None:
                date_ID_str = '2012-4'
            date_ID_str = date_ID_str.replace('-','-0')
            latest_date_inDB = datetime.strptime(date_ID_str, "%Y-%m")
            Start_date_tmp = datetime.strptime(str(start_date_ptr.year) + '-0' + str(season_num), "%Y-%m")
            if latest_date_inDB > Start_date_tmp:
                print('Skip')
                conn_stock.close()
                continue

            if season_num == 1:
                EPS_result = float(tds[n].getText().strip())
            elif season_num == 2:
                cursor_EPS = c_stock.execute('select EPS from stock_quarter where date_ID =\'' + str(start_date_ptr.year) + '-1\'')
                EPS_s1_float = cursor_EPS.fetchone()
                if EPS_s1_float == None:
                    EPS_s1_float = 0
                else:
                    EPS_s1_float = EPS_s1_float[0]
                print(EPS_s1_float)
                EPS_result = float(tds[n].getText().strip()) - EPS_s1_float
            elif season_num == 3:
                cursor_EPS = c_stock.execute('select EPS from stock_quarter where date_ID =\'' + str(start_date_ptr.year) + '-1\'')
                EPS_s1_float = cursor_EPS.fetchone()
                if EPS_s1_float == None:
                    EPS_s1_float = 0
                else:
                    EPS_s1_float = EPS_s1_float[0]
                cursor_EPS = c_stock.execute('select EPS from stock_quarter where date_ID =\'' + str(start_date_ptr.year) + '-2\'')
                EPS_s2_float = cursor_EPS.fetchone()
                if EPS_s2_float == None:
                    EPS_s2_float = 0
                else:
                    EPS_s2_float = EPS_s2_float[0]
                print(EPS_s1_float)
                print(EPS_s2_float)
                EPS_result = float(tds[n].getText().strip()) - EPS_s1_float - EPS_s2_float
            elif season_num == 4:
                cursor_EPS = c_stock.execute('select EPS from stock_quarter where date_ID =\'' + str(start_date_ptr.year) + '-1\'')
                EPS_s1_float = cursor_EPS.fetchone()
                if EPS_s1_float == None:
                    EPS_s1_float = 0
                else:
                    EPS_s1_float = EPS_s1_float[0]
                cursor_EPS = c_stock.execute('select EPS from stock_quarter where date_ID =\'' + str(start_date_ptr.year) + '-2\'')
                EPS_s2_float = cursor_EPS.fetchone()
                if EPS_s2_float == None:
                    EPS_s2_float = 0
                else:
                    EPS_s2_float = EPS_s2_float[0]
                cursor_EPS = c_stock.execute('select EPS from stock_quarter where date_ID =\'' + str(start_date_ptr.year) + '-3\'')
                EPS_s3_float = cursor_EPS.fetchone()
                if EPS_s3_float == None:
                    EPS_s3_float = 0
                else:
                    EPS_s3_float = EPS_s3_float[0]
                print(EPS_s1_float)
                print(EPS_s2_float)
                print(EPS_s3_float)
                EPS_result = float(tds[n].getText().strip()) - EPS_s1_float - EPS_s2_float - EPS_s3_float
            
            EPS_result = round(EPS_result, 2)
            sql_cmd = 'INSERT or IGNORE INTO stock_quarter (date_ID, EPS) VALUES (\'' + str(start_date_ptr.year) + '-' + str(season_num) + '\',' +\
                       str(EPS_result) + ')'
            print(sql_cmd)
            c_stock.execute(sql_cmd)
            conn_stock.commit()
            sql_cmd = 'UPDATE stock_quarter set EPS =' + str(EPS_result) + ' where date_ID =\'' + str(start_date_ptr.year) + '-' + str(season_num) + '\''
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

    table_keystring = soup.find_all(string=keystring1[season_num - 1])
    print(table_keystring)
    if table_keystring == []:
        break
    table_sons = soup.find_all(string='基本每股盈餘（元）')
    for table_son in table_sons:
        soup_cur_table = bs4.BeautifulSoup(str(table_son.parent.parent.parent), "lxml")
        n = 0
        ths = soup_cur_table.find_all('th')
        for th in ths:
            if th.getText().strip() == '基本每股盈餘（元）':
                break
            else:
                n = n + 1
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
            cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_quarter')
            date_ID_str = cursor_stock.fetchone()[0]
            if date_ID_str == None:
                date_ID_str = '2012-4'
            date_ID_str = date_ID_str.replace('-','-0')
            latest_date_inDB = datetime.strptime(date_ID_str, "%Y-%m")
            Start_date_tmp = datetime.strptime(str(start_date_ptr.year) + '-0' + str(season_num), "%Y-%m")
            if latest_date_inDB > Start_date_tmp:
                print('Skip')
                conn_stock.close()
                continue

            if season_num == 1:
                EPS_result = float(tds[n].getText().strip())
            elif season_num == 2:
                cursor_EPS = c_stock.execute('select EPS from stock_quarter where date_ID =\'' + str(start_date_ptr.year) + '-1\'')
                EPS_s1_float = cursor_EPS.fetchone()
                if EPS_s1_float == None:
                    EPS_s1_float = 0
                else:
                    EPS_s1_float = EPS_s1_float[0]
                print(EPS_s1_float)
                EPS_result = float(tds[n].getText().strip()) - EPS_s1_float
            elif season_num == 3:
                cursor_EPS = c_stock.execute('select EPS from stock_quarter where date_ID =\'' + str(start_date_ptr.year) + '-1\'')
                EPS_s1_float = cursor_EPS.fetchone()
                if EPS_s1_float == None:
                    EPS_s1_float = 0
                else:
                    EPS_s1_float = EPS_s1_float[0]
                cursor_EPS = c_stock.execute('select EPS from stock_quarter where date_ID =\'' + str(start_date_ptr.year) + '-2\'')
                EPS_s2_float = cursor_EPS.fetchone()
                if EPS_s2_float == None:
                    EPS_s2_float = 0
                else:
                    EPS_s2_float = EPS_s2_float[0]
                print(EPS_s1_float)
                print(EPS_s2_float)
                EPS_result = float(tds[n].getText().strip()) - EPS_s1_float - EPS_s2_float
            elif season_num == 4:
                cursor_EPS = c_stock.execute('select EPS from stock_quarter where date_ID =\'' + str(start_date_ptr.year) + '-1\'')
                EPS_s1_float = cursor_EPS.fetchone()
                if EPS_s1_float == None:
                    EPS_s1_float = 0
                else:
                    EPS_s1_float = EPS_s1_float[0]
                cursor_EPS = c_stock.execute('select EPS from stock_quarter where date_ID =\'' + str(start_date_ptr.year) + '-2\'')
                EPS_s2_float = cursor_EPS.fetchone()
                if EPS_s2_float == None:
                    EPS_s2_float = 0
                else:
                    EPS_s2_float = EPS_s2_float[0]
                cursor_EPS = c_stock.execute('select EPS from stock_quarter where date_ID =\'' + str(start_date_ptr.year) + '-3\'')
                EPS_s3_float = cursor_EPS.fetchone()
                if EPS_s3_float == None:
                    EPS_s3_float = 0
                else:
                    EPS_s3_float = EPS_s3_float[0]
                print(EPS_s1_float)
                print(EPS_s2_float)
                print(EPS_s3_float)
                EPS_result = float(tds[n].getText().strip()) - EPS_s1_float - EPS_s2_float - EPS_s3_float
            
            EPS_result = round(EPS_result, 2)
            sql_cmd = 'INSERT or IGNORE INTO stock_quarter (date_ID, EPS) VALUES (\'' + str(start_date_ptr.year) + '-' + str(season_num) + '\',' +\
                       str(EPS_result) + ')'
            print(sql_cmd)
            c_stock.execute(sql_cmd)
            conn_stock.commit()
            sql_cmd = 'UPDATE stock_quarter set EPS =' + str(EPS_result) + ' where date_ID =\'' + str(start_date_ptr.year) + '-' + str(season_num) + '\''
            c_stock.execute(sql_cmd)
            conn_stock.commit()
            conn_stock.close()
    

    if find_count == 0:
        continue
    last_update_date = start_date_ptr
    if start_date_ptr.month > 9:
        start_date_ptr = start_date_ptr.replace(year = start_date_ptr.year + 1, month = 1)
    else:
        start_date_ptr = start_date_ptr.replace(month = start_date_ptr.month + 3)

web.close()
path = os.getcwd()
path = path.replace('\\stock_db','')
os.chdir(path)
f= open('last_date_of_eps.log',"w", encoding="utf-8")
f.write('Last update of EPS: ' + str(last_update_date.year) + '-' + last_update_date.strftime("%m") + '-01')
f.close()
conn.close()

