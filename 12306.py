import os
import argparse
import _thread
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime
from tqdm import tqdm

key_list = ['商务座', '一等座', '二等座', '高级软卧', '软卧', '动卧', '硬卧', '软座', '硬座', '无座']

class transmit:
    def __init__(self):
        self.end = []

    def set_start(self, start):
        self.start = start

    def add_end(self, end_route):
        self.end.append(end_route)


class tran:
    def set_number(self, number):
        self.number = number

    def set_start_end(self, start_end):
        self.start = start_end[0].get_attribute('textContent')
        self.end = start_end[1].get_attribute('textContent')

    def set_start_end_t(self, start_end_t):
        self.start_t = start_end_t[0].get_attribute('textContent')
        self.end_t = start_end_t[1].get_attribute('textContent')

    def set_period(self, period):
        self.period = period.get_attribute('textContent')

    def set_seats(self, seats):
        self.seats = {}
        no_ticket_num = 0
        for i in range(10):
            if (seats[i].get_attribute('textContent') != '--'
            and seats[i].get_attribute('textContent') != '候补'
            and seats[i].get_attribute('textContent') != '无'
            and seats[i].get_attribute('textContent') != '*'
            ):
                if (seats[i].get_attribute('textContent') != '有'
                and len(seats[i].get_attribute('textContent')) == 1
                ):
                    self.seats[key_list[i]] = seats[i].get_attribute('textContent')+' '
                else:
                    self.seats[key_list[i]] = seats[i].get_attribute('textContent')
            else:
                no_ticket_num += 1
                self.seats[key_list[i]] = '--'

        if no_ticket_num == 10:
            return True
        else:
            return False


def input_start_end(driver, start, end, time):
    driver.execute_script('document.querySelector("#fromStation").value=' + "'" + station_dict[start] + "'")
    driver.execute_script('document.querySelector("#fromStationText").value=' + "'" + start + "'")
    driver.execute_script('document.querySelector("#toStation").value=' + "'" + station_dict[end] + "'")
    driver.execute_script('document.querySelector("#toStationText").value=' + "'" + end + "'")
    driver.execute_script('document.querySelector("#train_date").value=' + "'" + time + "'")
    driver.find_element_by_css_selector("#search_one").click()

def get_trains(driver, start, end, route):
    trs = driver.find_elements_by_tag_name('tr')
    del trs[0:7]
    del trs[-3:]
    train = tran()
    for index in tqdm(enumerate(trs),total=len(trs)):
        tr = index[1]
        if index[0] % 2 == 0:
            passed = False
            train = tran()

            start_end = tr.find_element_by_class_name('cdz').find_elements_by_tag_name('strong')
            if start_end[0].get_attribute('textContent') == start and start_end[1].get_attribute('textContent') == end:
                train.set_start_end(start_end)
            else:
                passed = True

            start_end_t = tr.find_element_by_class_name('cds').find_elements_by_tag_name('strong')
            train.set_start_end_t(start_end_t)

            period = tr.find_element_by_class_name('ls').find_element_by_tag_name('strong')
            train.set_period(period)

            seats = tr.find_elements_by_tag_name('td')[1:11]
            passed = train.set_seats(seats) if passed == False else True

        else:
            if passed:
                continue
            train.set_number(tr.get_attribute('datatran'))
            route.append(train)
        
    driver.close()
    return route

def switch_to_newest_window(driver):
    windows = driver.window_handles
    driver.switch_to.window(windows[-1])

def print_all_tickets(station_name, routes):
    print('车票情况'.center(os.get_terminal_size().columns-4, '-'))
    for index in enumerate(routes):
        route = index[1]
        print('从 {} 到 {} 可购票的车次共有 {} 趟:\n'.format(station_name[index[0]], station_name[index[0] + 1], len(route)))
        for t in route:
            print('\t车次: {:5}, 时间: {}-{}, 历时: {}'.format(t.number, t.start_t, t.end_t, t.period), end='')
            for i in range(10):
                print(', {}: {}'.format(key_list[i], t.seats[key_list[i]]), end='')
            print()
        print()
    print(''.center(os.get_terminal_size().columns, '-'))
    print()

def print_transmit(station_name, interval_routes, transmit_time_min, transmit_time_max):
    print('换乘方案'.center(os.get_terminal_size().columns-4, '-'))
    deep = len(interval_routes) - 1
    print('换乘方案 ', end='')
    for i in range(len(station_name)):
        if i != len(station_name) - 1:
            print('{} -> '.format(station_name[i]), end='')
        else:
            print('{} :\n'.format(station_name[i]))

    transmit_routes = []
    for r in interval_routes[0]:
        passed = False
        transmit_route, passed = search_transmit(interval_routes, r, deep, 0, passed, transmit_time_min, transmit_time_max)
        if passed:
            transmit_routes.append(transmit_route)

    print_recursion(transmit_routes, deep, 0)
    print(''.center(os.get_terminal_size().columns, '-'))

def search_transmit(interval_routes, route, deep, level, passed_old, transmit_time_min, transmit_time_max):
    next_route = interval_routes[level + 1]
    transmit_route = transmit()
    transmit_route.set_start(route)
    for nt in next_route:
        p = (datetime.strptime(nt.start_t, '%H:%M') - datetime.strptime(route.end_t, '%H:%M')).seconds / 60
        if p > transmit_time_min and p < transmit_time_max:
            if level + 1 != deep:
                passed = False
                nr, passed = search_transmit(interval_routes, nt, deep, level + 1, passed, transmit_time_min, transmit_time_max)
                if passed:
                    transmit_route.add_end(nr)
                passed_old = passed_old if passed_old else passed
            else:
                transmit_route.add_end(nt)
                passed_old = True
    return transmit_route, passed_old

def print_recursion(routes, deep, level):
    if len(routes) == 0:
        print('找不到符合要求的车次')
        return
    for t in routes:
        for i in range(level):
            print('  ', end='')
        if level != deep:
            if level == 0:
                print()
            print('车次: {:5}, 时间: {}-{}, 历时: {}'.format(t.start.number, t.start.start_t, t.start.end_t, t.start.period), end='')
            for i in range(10):
                print(', {}: {}'.format(key_list[i], t.start.seats[key_list[i]]), end='')
            print()
            print_recursion(t.end, deep, level + 1)
        else:
            print('车次: {:5}, 时间: {}-{}, 历时: {}'.format(t.number, t.start_t, t.end_t, t.period), end='')
            for i in range(10):
                print(', {}: {}'.format(key_list[i], t.seats[key_list[i]]), end='')
            print('')

def start_chrome(port):
    os.system('chrome --remote-debugging-port='+str(port))


if __name__ == '__main__':
    now = datetime.now()
    cur_date = '-'.join([str(now.year), "{:0>2d}".format(now.month), "{:0>2d}".format(now.day)])
    parser = argparse.ArgumentParser(description='示例: python 12306.py --min-transmit-period 30 --max-transmit-period 90 --stations 深圳北 广州南 长沙南 武汉 郑州东 石家庄 北京西 --time 2022-01-22')
    parser.add_argument('--min-transmit-period', type=int, default=20, help='最小中转间隔时间(分钟)')
    parser.add_argument('--max-transmit-period', type=int, default=60, help='最大中转间隔时间(分钟)')
    parser.add_argument('--stations', type=str, nargs='+', help='中转换乘站点')
    parser.add_argument('--time', type=str, default=cur_date, help='乘车日期(YYYY-MM-DD)')
    parser.add_argument('--port', type=int, default=9221, help='远程打开chrome浏览器的端口')
    args = parser.parse_args()
    transmit_time_min = args.min_transmit_period
    transmit_time_max = args.max_transmit_period
    station_name = args.stations
    time = args.time
    port = args.port
    _thread.start_new_thread(start_chrome, (port,))
    print('等待浏览器启动')
    sleep(5)
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:"+str(port))
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.12306.cn/index/')
    routes = []

    terminal_width = os.get_terminal_size().columns-4

    f = open('station_name.txt', encoding='utf-8')
    stationName = f.read()
    stations = stationName.split('@')
    del stations[0]
    station_dict = {}
    for station in stations:
        station_dict[station.split('|')[1]] = station.split('|')[2]

    print()
    print('中转参数'.center(os.get_terminal_size().columns-4, '-'))
    print('乘车日期: {}'.format(time))
    print('中转站点: {}'.format(' -> '.join(station_name)))
    print('最小中转间隔: {} 分钟'.format(transmit_time_min))
    print('最大中转间隔: {} 分钟'.format(transmit_time_max))
    print(''.center(os.get_terminal_size().columns, '-'))
    print()

    print('查询路线'.center(os.get_terminal_size().columns-4, '-'))
    for index in enumerate(station_name):
        route = []
        if index[0] + 1 == len(station_name):
            break
        start = index[1]
        end = station_name[index[0] + 1]

        try:
            print('从 {},{} 到 {},{}'.format(start, station_dict[start], end, station_dict[end]))
        except KeyError:
            print('找不到车站代码')
        
        input_start_end(driver, start, end, time)
        switch_to_newest_window(driver)
        get_trains(driver, start, end, route)

        routes.append(route)

        switch_to_newest_window(driver)
    print(''.center(os.get_terminal_size().columns, '-'))
    print()

    print_all_tickets(station_name, routes)
    print_transmit(station_name, routes, transmit_time_min, transmit_time_max)

    print('查询完毕')