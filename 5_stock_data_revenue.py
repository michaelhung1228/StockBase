import requests, os, bs4, sys
import re, time
from datetime import datetime
from datetime import timedelta
import sqlite3

DateSearch = re.compile(r'(\d\d\d\d)(\d\d)')

#dir_temp = os.getcwd()
#dir_temp = dir_temp + '/DBs'
#os.chdir(dir_temp)
conn = sqlite3.connect('stock_list.db')
c = conn.cursor()

f = open('monthly_revenue_update.log',"r", encoding="utf-8")
current_last_date = f.readline()
current_last_date = current_last_date.replace('last update: ','')
#print(current_last_date)
f.close()

path = os.getcwd()
path = path + '\\stock_db'
os.chdir(path)
print(os.getcwd())

stock_url1 = 'https://mops.twse.com.tw/nas/t21/sii/t21sc03_---ROCyear---_---month---_0.html'
stock_url2 = 'https://mops.twse.com.tw/nas/t21/sii/t21sc03_---ROCyear---_---month---_1.html'
stock_url3 = 'https://mops.twse.com.tw/nas/t21/otc/t21sc03_---ROCyear---_---month---_0.html'
stock_url4 = 'https://mops.twse.com.tw/nas/t21/otc/t21sc03_---ROCyear---_---month---_1.html'
delta_1day = timedelta(days = 1) #delta_1day
skip = 0
if current_last_date == '':
    current_last_date = datetime.today()
    cursor = c.execute("SELECT stock_id, start_date, stock_type, business  from stock_list")
    #find oldest data in the stock by stock list
    for current_entry in cursor:
        if ((current_entry[2] == '上櫃') or (current_entry[2] == '上市')) and (current_entry[3] != 'ETF'):
            db_name = current_entry[0] + '.db'
            conn_stock = sqlite3.connect(db_name)
            c_stock = conn_stock.cursor()
            cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_month')
            data_ID_str = cursor_stock.fetchone()[0]
            if data_ID_str == None:
                conn_stock.close()
                continue
            data_ID_str = data_ID_str + '-01'
            latest_date = datetime.strptime(data_ID_str, "%Y-%m-%d")
            if latest_date < current_last_date:
                current_last_date = latest_date
                print(db_name + ' not up to date')
            #print(current_last_date)
            conn_stock.close()
    skip = 1
else:
    current_last_date = DateSearch.search(current_last_date)
    current_last_date = datetime(int(current_last_date.group(1)), int(current_last_date.group(2)), 1)

End_date = datetime.today()
if End_date.month == 12:
    End_date = End_date.replace(year = End_date.year - 1, month = 1)
else:
    End_date = End_date.replace(month = End_date.month - 1)
Start_date_ptr = current_last_date
if skip == 1:
    Start_date_ptr = End_date + delta_1day
while Start_date_ptr <= End_date:
    print(Start_date_ptr)
    url = stock_url1.replace('---ROCyear---',str(Start_date_ptr.year - 1911)).replace('---month---',str(Start_date_ptr.month))
    print('Cool down for requesting web content')
    time.sleep(3)
    res = requests.get(url)
    revenue_content = res.text
    soup = bs4.BeautifulSoup(revenue_content, "lxml")
    
    url = stock_url2.replace('---ROCyear---',str(Start_date_ptr.year - 1911)).replace('---month---',str(Start_date_ptr.month))
    print('Cool down for requesting web content')
    time.sleep(3)
    res = requests.get(url)
    soup1 = bs4.BeautifulSoup(res.text, "lxml")
    for element in soup1.body:
        soup.body.append(element)
    url = stock_url3.replace('---ROCyear---',str(Start_date_ptr.year - 1911)).replace('---month---',str(Start_date_ptr.month))
    print('Cool down for requesting web content')
    time.sleep(3)
    res = requests.get(url)
    soup1 = bs4.BeautifulSoup(res.text, "lxml")
    for element in soup1.body:
        soup.body.append(element)
    url = stock_url4.replace('---ROCyear---',str(Start_date_ptr.year - 1911)).replace('---month---',str(Start_date_ptr.month))
    print('Cool down for requesting web content')
    time.sleep(3)
    res = requests.get(url)
    soup1 = bs4.BeautifulSoup(res.text, "lxml")
    for element in soup1.body:
        soup.body.append(element)
    

    cursor = c.execute("SELECT stock_id, stock_name, start_date, stock_type, business  from stock_list")
    for current_entry in cursor:
        if ((current_entry[3] == '上櫃') or (current_entry[3] == '上市')) and (current_entry[4] != 'ETF'):
            db_name = current_entry[0] + '.db'
            print(db_name)

            conn_stock = sqlite3.connect(db_name)
            c_stock = conn_stock.cursor()
            cursor_stock = c_stock.execute('SELECT max(date_ID) FROM stock_month')
            date_ID_str = cursor_stock.fetchone()[0]
            if date_ID_str == None:
                date_ID_str = '2009-12'
            latest_date_inDB = datetime.strptime(date_ID_str, "%Y-%m")
            if latest_date_inDB >= Start_date_ptr:
                conn_stock.close()
                continue
            td = soup.find(string=str(current_entry[0]))
            if td == None:
                conn_stock.close()
                continue
            print(td.parent.parent)
            soup1 = bs4.BeautifulSoup(str(td.parent.parent), "lxml")
            tds = soup1.find_all('td')
            sql_cmd = 'INSERT INTO stock_month (date_ID, revenue) VALUES (\'' + str(Start_date_ptr.year) + '-' +  Start_date_ptr.strftime("%m") + '\',' +\
                             tds[2].getText().strip().replace(',','') + ')'
            print(sql_cmd)
            c_stock.execute(sql_cmd)
            conn_stock.commit()
            conn_stock.close()

    if Start_date_ptr.month == 12:
        Start_date_ptr = Start_date_ptr.replace(year = Start_date_ptr.year + 1, month = 1)
    else:
        Start_date_ptr = Start_date_ptr.replace(month = Start_date_ptr.month + 1)

    #print(revenue_content)

path = os.getcwd()
path = path.replace('\\stock_db','')
os.chdir(path)
if skip != 1:
    f= open('monthly_revenue_update.log',"w", encoding="utf-8")
    f.write('last update: ' + str(End_date.year) + End_date.strftime("%m"))
    f.close()
conn.close()