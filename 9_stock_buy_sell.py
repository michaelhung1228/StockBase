import os, sys, re, shutil, requests, bs4, subprocess, requests, math, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from datetime import datetime
from datetime import timedelta
import sqlite3

DateSearch = re.compile(r'(\d\d\d\d)/(\d\d)/(\d\d)')
f = open('last_date_of_buy_sell.log',"r", encoding="utf-8")
start_date = f.readline()
start_date = start_date.replace('Last update of buy and sell: ','')
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

url1_0 = 'http://www.twse.com.tw/fund/TWT38U?response=html&date=---date---'
url1_1 = 'http://www.twse.com.tw/fund/TWT44U?response=html&date=---date---'
url2_0 = 'https://www.tpex.org.tw/web/stock/3insti/qfii_trading/forgtr_result.php?l=zh-tw&t=D&type=buy&d=---date---&s=0,asc&o=htm'
url2_1 = 'https://www.tpex.org.tw/web/stock/3insti/qfii_trading/forgtr_result.php?l=zh-tw&t=D&type=sell&d=---date---&s=0,asc&o=htm'
url2_2 = 'https://www.tpex.org.tw/web/stock/3insti/sitc_trading/sitctr_result.php?l=zh-tw&t=D&type=buy&d=---date---&o=htm'
url2_3 = 'https://www.tpex.org.tw/web/stock/3insti/sitc_trading/sitctr_result.php?l=zh-tw&t=D&type=sell&d=---date---&o=htm'
keystring = '很抱歉，沒有符合條件的資料!'

delta_1day = timedelta(days = 1) #delta_1day
Start_date_ptr = Start_date
End_date = datetime.today()

while Start_date_ptr <= End_date:

    url = url1_0.replace('---date---', Start_date_ptr.strftime("%Y") + Start_date_ptr.strftime("%m") + Start_date_ptr.strftime("%d"))
    print(url)
    res_1_0 = requests.get(url)
    print('Cool down for requesting web content')
    time.sleep(5)
    url = url1_1.replace('---date---', Start_date_ptr.strftime("%Y") + Start_date_ptr.strftime("%m") + Start_date_ptr.strftime("%d"))
    print(url)
    res_1_1 = requests.get(url)
    print('Cool down for requesting web content')
    time.sleep(5)
    url = url2_0.replace( '---date---', str(Start_date_ptr.year - 1911) + '/' + Start_date_ptr.strftime("%m") + '/' + Start_date_ptr.strftime("%d"))
    print(url)
    res_2_0 = requests.get(url)
    print('Cool down for requesting web content')
    time.sleep(5)
    url = url2_1.replace('---date---', str(Start_date_ptr.year - 1911) + '/' + Start_date_ptr.strftime("%m") + '/' + Start_date_ptr.strftime("%d"))
    print(url)
    res_2_1 = requests.get(url)
    print('Cool down for requesting web content')
    time.sleep(5)
    url = url2_2.replace('---date---', str(Start_date_ptr.year - 1911) + '/' + Start_date_ptr.strftime("%m") + '/' + Start_date_ptr.strftime("%d"))
    print(url)
    res_2_2 = requests.get(url)
    print('Cool down for requesting web content')
    time.sleep(5)
    url = url2_3.replace('---date---', str(Start_date_ptr.year - 1911) + '/' + Start_date_ptr.strftime("%m") + '/' + Start_date_ptr.strftime("%d"))
    print(url)
    res_2_3 = requests.get(url)
    print('Cool down for requesting web content')
    time.sleep(5)

    soup1_0 = bs4.BeautifulSoup(res_1_0.text, "lxml") #上市外資
    soup1_1 = bs4.BeautifulSoup(res_1_1.text, "lxml") #上市投信
    soup2_0 = bs4.BeautifulSoup(res_2_0.text, "lxml") #上櫃外資
    soup2_1 = bs4.BeautifulSoup(res_2_1.text, "lxml")
    soup2_2 = bs4.BeautifulSoup(res_2_2.text, "lxml") #上櫃投信
    soup2_3 = bs4.BeautifulSoup(res_2_3.text, "lxml")
    
    table_keystring = res_1_0.text.find('很抱歉，沒有符合條件的資料!')
    if table_keystring != -1:
        if ((End_date - Start_date_ptr) > delta_1day):
            Start_date_ptr = Start_date_ptr + delta_1day
            path = os.getcwd()
            path = path.replace('\\stock_db','')
            os.chdir(path)
            f= open('last_date_of_buy_sell.log',"w", encoding="utf-8")
            f.write('Last update of buy and sell: ' + str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d"))
            f.close()
            path = os.getcwd()
            path = path + '\\stock_db'
            os.chdir(path)
            continue
        else:
            break
    n = 0
    cursor = c.execute("SELECT stock_id, stock_name, start_date, stock_type, business  from stock_list")
    for current_entry in cursor:
        if ((current_entry[3] == '上櫃') or (current_entry[3] == '上市')) and (current_entry[4] != 'ETF'):
            
            if (current_entry[3] == '上櫃'):
                soup0 = soup2_0
                soup1 = soup2_1
                soup2 = soup2_2
                soup3 = soup2_3
            elif (current_entry[3] == '上市'):
                soup0 = soup1_0
                soup1 = soup1_1

            db_name = current_entry[0] + '.db'
            print(db_name)
            conn_stock = sqlite3.connect(db_name)
            c_stock = conn_stock.cursor()
            date_ID = str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d")
            sql_cmd = 'UPDATE or IGNORE stock_day set foreign_buy = 0, foreign_sell = 0, foreign_total = 0, invest_trust_buy = 0, invest_trust_sell = 0, invest_trust_total = 0 WHERE date_ID =\'' + date_ID + '\''
            print(sql_cmd)
            cursor_stock = c_stock.execute(sql_cmd)
            conn_stock.commit()
            if (current_entry[3] == '上市'):
                td = soup0.find(string=str(current_entry[0]) + '  ')
            elif (current_entry[3] == '上櫃'):
                td = soup0.find(string=str(current_entry[0]))
                if td == None:
                    td = soup1.find(string=str(current_entry[0]))
            print(td)
            """
            if td == None:
                conn_stock.close()
                continue
            """
            if td != None:
                print(td.parent.parent)
                n = n + 1
                soup_tmp = bs4.BeautifulSoup(str(td.parent.parent), "lxml")
                tds = soup_tmp.find_all('td')
                if (current_entry[3] == '上市'):
                    buyin = tds[3].getText().strip().replace(',','')
                    sellout = tds[4].getText().strip().replace(',','')
                    total = int(buyin) - int(sellout)
                    sql_cmd = 'UPDATE or IGNORE stock_day set foreign_buy =' + buyin + ', foreign_sell = ' + sellout + ', foreign_total =' + str(total) + ' WHERE date_ID =\'' + date_ID + '\''
                elif (current_entry[3] == '上櫃'):
                    buyin = tds[3].getText().strip().replace(',','')
                    buyin = buyin + '000'
                    sellout = tds[4].getText().strip().replace(',','')
                    sellout = sellout + '000'
                    total = int(buyin) - int(sellout)
                    sql_cmd = 'UPDATE or IGNORE stock_day set foreign_buy =' + buyin + ', foreign_sell = ' + sellout + ', foreign_total =' + str(total) + ' WHERE date_ID =\'' + date_ID + '\''
                print(sql_cmd)
                cursor_stock = c_stock.execute(sql_cmd)
                conn_stock.commit()
            if (current_entry[3] == '上市'):
                td = soup1.find(string=str(current_entry[0]) + '  ')
            elif (current_entry[3] == '上櫃'):
                td = soup2.find(string=str(current_entry[0]))
                if td == None:
                    td = soup3.find(string=str(current_entry[0]))
            print(td)
            """
            if td == None:
                conn_stock.close()
                continue
            """
            if td != None:
                print(td.parent.parent)
                n = n + 1
                soup_tmp = bs4.BeautifulSoup(str(td.parent.parent), "lxml")
                tds = soup_tmp.find_all('td')
                if (current_entry[3] == '上市'):
                    buyin = tds[3].getText().strip().replace(',','')
                    sellout = tds[4].getText().strip().replace(',','')
                    total = int(buyin) - int(sellout)
                    sql_cmd = 'UPDATE or IGNORE stock_day set invest_trust_buy =' + buyin + ', invest_trust_sell = ' + sellout + ', invest_trust_total =' + str(total) + ' WHERE date_ID =\'' + date_ID + '\''
                elif (current_entry[3] == '上櫃'):
                    buyin = tds[3].getText().strip().replace(',','')
                    buyin = buyin + '000'
                    sellout = tds[4].getText().strip().replace(',','')
                    sellout = sellout + '000'
                    total = int(buyin) - int(sellout)
                    sql_cmd = 'UPDATE or IGNORE stock_day set invest_trust_buy =' + buyin + ', invest_trust_sell = ' + sellout + ', invest_trust_total =' + str(total) + ' WHERE date_ID =\'' + date_ID + '\''
                print(sql_cmd)
                cursor_stock = c_stock.execute(sql_cmd)
                conn_stock.commit()
                conn_stock.close()
    if n != 0:
        Start_date_ptr = Start_date_ptr + delta_1day
        path = os.getcwd()
        path = path.replace('\\stock_db','')
        os.chdir(path)
        f= open('last_date_of_buy_sell.log',"w", encoding="utf-8")
        f.write('Last update of buy and sell: ' + str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d"))
        f.close()
        path = os.getcwd()
        path = path + '\\stock_db'
        os.chdir(path)
    else:
        break
conn.close()

