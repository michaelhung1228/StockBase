import requests, os, bs4, sys
import re, time
from datetime import datetime
from datetime import timedelta
import sqlite3

f= open('log_stock_volume_validation.txt',"a", encoding="utf-8")

DateSearch = re.compile(r'(\d\d\d\d)/(\d\d)/(\d\d)')

conn = sqlite3.connect('stock_list.db')
c = conn.cursor()

path = os.getcwd()
path = path + '\\stock_db'
os.chdir(path)
print(os.getcwd())

current_last_date = datetime.today()

cursor = c.execute("SELECT stock_id, start_date, stock_type, business  from stock_list")
#find oldest data in the stock by stock list
for current_entry in cursor:
    if ((current_entry[2] == '上櫃') or (current_entry[2] == '上市')) and (current_entry[3] != 'ETF'):
        db_name = current_entry[0] + '.db'
        conn_stock = sqlite3.connect(db_name)
        c_stock = conn_stock.cursor()
        cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_day')
        data_ID_str = cursor_stock.fetchone()[0]
        if data_ID_str == None:
            continue
        latest_date = datetime.strptime(data_ID_str, "%Y-%m-%d")
        if latest_date < current_last_date:
            current_last_date = latest_date
            print(db_name)
        #print(current_last_date)
        conn_stock.close()

f.close()


stock_url1_0 = 'http://www.twse.com.tw/exchangeReport/MI_INDEX?response=html&date='
stock_url1_1 = '&type=ALLBUT0999'
stock_url2_0 = 'https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw&o=htm&d='
stock_url2_1 = '&s=0,asc,0'

delta_1day = timedelta(days = 1) #delta_1day
print(current_last_date)
Start_date_ptr = current_last_date + delta_1day
End_date = datetime.today()

while Start_date_ptr <= End_date:

    print('Cool down for requesting web content')
    time.sleep(5)
    url = stock_url1_0 + Start_date_ptr.strftime("%Y") + Start_date_ptr.strftime("%m") + Start_date_ptr.strftime("%d") + stock_url1_1
    print(url)
    res_1 = requests.get(url)
    url = stock_url2_0 + str(Start_date_ptr.year - 1911) + '/' + Start_date_ptr.strftime("%m") + '/' + Start_date_ptr.strftime("%d") + stock_url2_1
    print(url)
    res_2 = requests.get(url)
    soup1 = bs4.BeautifulSoup(res_1.text, "lxml")
    soup2 = bs4.BeautifulSoup(res_2.text, "lxml")
    text_search = re.compile(r'大盤統計資訊')
    err_text = text_search.search(res_1.text)
    print(err_text)
    if err_text == None:
        Start_date_ptr = Start_date_ptr + delta_1day
        continue

    #cursor = c.execute("SELECT stock_id, start_date, stock_type, business  from stock_list")
    #for current_entry in cursor:
    cursor = c.execute("SELECT stock_id, stock_name, start_date, stock_type, business  from stock_list")
    for current_entry in cursor:
        if ((current_entry[3] == '上櫃') or (current_entry[3] == '上市')) and (current_entry[4] != 'ETF'):
            db_name = current_entry[0] + '.db'
            conn_stock = sqlite3.connect(db_name)
            c_stock = conn_stock.cursor()
            cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_day')
            data_ID_str = cursor_stock.fetchone()[0]
            if data_ID_str == None:
                conn_stock.close()
                continue
            latest_date_inDB = datetime.strptime(data_ID_str, "%Y-%m-%d")
            if latest_date_inDB >= Start_date_ptr:
                conn_stock.close()
                continue
            if (current_entry[3] == '上市'):
                td = soup1.find(string=str(current_entry[0]))
                soup_temp = bs4.BeautifulSoup(str(td.parent.parent), "lxml")
                tds = soup_temp.find_all('td')
                if (tds[2].getText().strip().replace(',','') == '0') or (tds[5].getText().strip().replace(',','') == '--'):
                    continue
                sql_cmd = 'INSERT INTO stock_day (date_ID, open_price, highest_price, lowest_price, close_price, volume, Total) VALUES (\'' + str(Start_date_ptr.year) + '-' + \
                Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d") + '\',' + tds[5].getText().strip().replace(',','') + ',' \
                                                                                            + tds[6].getText().strip().replace(',','') + ',' \
                                                                                            + tds[7].getText().strip().replace(',','') + ',' \
                                                                                            + tds[8].getText().strip().replace(',','') + ',' \
                                                                                            + tds[2].getText().strip().replace(',','') + ',' \
                                                                                            + str(float(tds[8].getText().replace(',','')) - float(tds[5].getText().replace(',',''))).strip().replace(',','').replace('X','').replace('+','') + ')'
                c_stock.execute(sql_cmd)
                conn_stock.commit()
                print(Start_date_ptr)
                print(db_name + ' ' + str(td.parent))
                #print(td.parent.parent)
            elif (current_entry[3] == '上櫃'):
                td = soup2.find(string=str(current_entry[0]))
                soup_temp = bs4.BeautifulSoup(str(td.parent.parent), "lxml")
                tds = soup_temp.find_all('td')
                if (tds[8].getText().strip().replace(',','') == '0') or (tds[2].getText().strip().replace(',','') == '---'):
                    continue
                sql_cmd = 'INSERT INTO stock_day (date_ID, open_price, highest_price, lowest_price, close_price, volume, Total) VALUES (\'' + str(Start_date_ptr.year) + '-' + \
                Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d") + '\',' + tds[4].getText().strip().replace(',','') + ',' \
                                                                                            + tds[5].getText().strip().replace(',','') + ',' \
                                                                                            + tds[6].getText().strip().replace(',','') + ',' \
                                                                                            + tds[2].getText().strip().replace(',','') + ',' \
                                                                                            + tds[8].getText().strip().replace(',','') + ',' \
                                                                                            + str(float(tds[2].getText().replace(',','')) - float(tds[4].getText().replace(',',''))).strip().replace(',','').replace('X','').replace('+','') + ')'
                c_stock.execute(sql_cmd)
                conn_stock.commit()
                print(Start_date_ptr)
                print(db_name + ' ' + str(td.parent))
                #print(td.parent.parent)
            conn_stock.close()
    Start_date_ptr = Start_date_ptr + delta_1day


conn.close()