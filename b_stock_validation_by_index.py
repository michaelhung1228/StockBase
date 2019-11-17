import requests, os, bs4, sys
import re, time
from datetime import datetime
from datetime import timedelta
import sqlite3

stock_url1_0 = 'http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=html&date='
stock_url1_1 = '&stockNo='
stock_url2_0 = 'http://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43_print.php?l=zh-tw&d='
stock_url2_1 = '&stkno='
stock_url2_3 = '&s=0,asc,0'

delta_1day = timedelta(days = 1) #delta_1day
DateSearch = re.compile(r'(\d\d\d\d)/(\d\d)/(\d\d)')

conn = sqlite3.connect('stock_list.db')
c = conn.cursor()

path = os.getcwd()
path = path + '\\stock_db'
os.chdir(path)
print(os.getcwd())

cursor = c.execute("SELECT stock_id, start_date, stock_type, business  from stock_list")
#current_entry = cursor.fetchone()
#print(current_entry)
for current_entry in cursor:
    if (current_entry[2] == '上櫃') and (current_entry[3] != 'ETF'):
        db_name = current_entry[0] + '.db'
        Date = DateSearch.search(current_entry[1])
        print(Date.group(1) + Date.group(2)+ Date.group(3))
        Start_date = datetime(int(Date.group(1)), int(Date.group(2)), int(Date.group(3)))
        start_record_date = datetime(1996, 1, 1)
        if Start_date < start_record_date:
            Start_date_ptr = start_record_date
        else:
            Start_date_ptr = Start_date
        End_date = datetime.today()
        """
        former_url = None
        conn_stock = sqlite3.connect(db_name)
        c_stock = conn_stock.cursor()
        cursor = c_stock.execute('SELECT max(date_ID) FROM stock_day')
        max_id = cursor.fetchone()[0]
        if max_id != None:
            max_id = max_id.replace('-','/')
            Date = DateSearch.search(max_id)
            Start_date = datetime(int(Date.group(1)), int(Date.group(2)), int(Date.group(3)))
            Start_date = Start_date + delta_1day
            Start_date_ptr = Start_date
        """
        while Start_date_ptr <= End_date:
            url = stock_url2_0 + str(Start_date_ptr.year) + Start_date_ptr.strftime("%m") + stock_url2_1 + current_entry[0]
            if former_url != url:
                url = stock_url2_0 + str(Start_date_ptr.year - 1911) + '/' + Start_date_ptr.strftime("%m") + stock_url2_1 + current_entry[0]
                print('Cool down for requesting web content')
                time.sleep(3)
                print(url)
                res = requests.get(url)
                if res.raise_for_status() != None:
                    continue
                former_url = stock_url2_0 + str(Start_date_ptr.year) + Start_date_ptr.strftime("%m") + stock_url2_1 + current_entry[0]
            soup = bs4.BeautifulSoup(res.text, "lxml")
            trs = soup.find_all('tr')
            for tr in trs:
                soup1 = bs4.BeautifulSoup(str(tr), "lxml")
                tds = soup1.find_all('td')
                if tds == []:
                    continue
                date_str_from_table = tds[0].getText().strip()
                date_str = str(Start_date_ptr.year - 1911) + '/' + Start_date_ptr.strftime("%m") + '/' + Start_date_ptr.strftime("%d")
                if date_str == date_str_from_table:
                    if (tds[1].getText().strip().replace(',','') == '0') or (tds[3].getText().strip().replace(',','') == '--') or (tds[6].getText().strip().replace(',','') == '--'):
                        break
                    sql_cmd = 'INSERT INTO stock_day (date_ID, open_price, highest_price, lowest_price, close_price, volume, Total) VALUES (\'' + str(Start_date_ptr.year) + '-' + \
                    Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d") + '\',' + tds[3].getText().strip().replace(',','') + ',' \
                                                                                    + tds[4].getText().strip().replace(',','') + ',' \
                                                                                    + tds[5].getText().strip().replace(',','') + ',' \
                                                                                    + tds[6].getText().strip().replace(',','') + ',' \
                                                                                    + tds[1].getText().strip().replace(',','') + '000' + ',' \
                                                                                    + tds[7].getText().strip().replace(',','').replace('X','') + ')'
                    #print(sql_cmd)
                    c_stock.execute(sql_cmd)
                    conn_stock.commit()
                    print(date_str_from_table)
                    break
            Start_date_ptr = Start_date_ptr + delta_1day
        #conn_stock.commit()
        conn_stock.close()
"""
for row in cursor:
    if row[1] != 'ETF':
        db_name = row[0] + '.db'
        conn_stock = sqlite3.connect(db_name)
        c_stock = conn_stock.cursor()



        #conn_stock.commit()
        conn_stock.close()
"""
conn.close()