Constantin Fedenko, [19.01.2022 18:03]
import re
import threading

import pyautogui
import json
import requests
import csv
from threading import Thread

chk = pyautogui.confirm(text="Укажите имя файла или URL\n\np.s. файл должен лежать рядом со скрипт файлом.",
                        title="Enter", buttons=['Файл', 'URL'])
srv = 'https://some_link'


def progon(file_open1):

    coll_chk = 0

    with open(file_open1, encoding='utf-8') as file, open("source_out.csv", "a", newline="", encoding='utf-8') as fileCSV:
        for line in file:

            url = line.strip()

            response1 = requests.get(srv + url)

            try:
                answer1 = json.loads(response1.text)
            except json.decoder.JSONDecodeError:
                with open("errors_json.txt", "a", newline="", encoding='utf-8') as fileErr:
                    m = '{}\n'
                    mess = m.format(url)
                    fileErr.write(mess)

            if 'data' in answer1 and 'regexpSignatures' in answer1['data'] and 'domainInCI' in answer1['data'] and\
                    'urlInCI' in answer1['data'] and 'result' in answer1['data']['whitelist']['source']:

                if answer1['data']['regexpSignatures'] and not answer1['data']['whitelist']['source']['result'] and\
                        answer1['data']['domainInCI'][0]['type'] != "Ложно положительный":

                    mess = [url, 'Phish']
                    writer = csv.writer(fileCSV, delimiter='^')
                    writer.writerow(mess)

                else:
                    mess = [url, 'Clear']
                    writer = csv.writer(fileCSV, delimiter='^')
                    writer.writerow(mess)

            else:
                mess = [url, 'Clear']
                writer = csv.writer(fileCSV, delimiter='^')
                writer.writerow(mess)

                with open("errors.txt", "a", newline="", encoding='utf-8') as fileErr:
                    fileErr.write(line)

            coll_chk = coll_chk + 1

            if coll_chk % 5 == 0:
                print('Done ', coll_chk)


def post_progon(open_file):

    coll = 0

    with open(open_file, encoding='utf-8') as file, open("source_out_post_err.csv", "a", newline="",
                                                          encoding='utf-8') as fileCSV:
        for line in file:

            url = line.strip()

            response1 = requests.get(srv + url)

            try:
                answer1 = json.loads(response1.text)
            except json.decoder.JSONDecodeError:
                with open("errors_json_post.txt", "a", newline="", encoding='utf-8') as fileErr:
                    m = '{}\n'
                    mess = m.format(url)
                    fileErr.write(mess)
                    continue

            try:
                type_of_domain = answer1['data']['domainInCI'][0]
            except IndexError:
                with open("errors_post_data.txt", "a", newline="", encoding='utf-8') as fileErr:
                    m = '{}\n'
                    mess = m.format(url)
                    fileErr.write(mess)
                    continue

            if 'data' in answer1 and 'status' in answer1['data']['whitelist']['source']:
                
		if answer1['data']['whitelist']['source']['status'] == 'BAD':
                    with open("errors_post.txt", "a", newline="", encoding='utf-8') as fileErr:
                        fileErr.write(line)
                else:
                    if type_of_domain['type'] == 'Phishing':
                        mess = [url, 'Phishing']
                        writer = csv.writer(fileCSV, delimiter='^')
                        writer.writerow(mess)
                    else:
                        mess = [url, 'Not valid']
                        writer = csv.writer(fileCSV, delimiter='^')
                        writer.writerow(mess)

            else:
                with open("errors_post.txt", "a", newline="", encoding='utf-8') as fileErr:
                    fileErr.write(line)

            coll = coll + 1

            if coll % 5 == 0:
                print('Done ', coll)


if chk == 'Файл':

    break_file = pyautogui.confirm(text="Начать с нового файла или продолжить с места обрыва?",
                                   title="Enter", buttons=['NEW', 'BREAK', 'CHECK ERR'])

    if break_file == 'NEW':

        file_open = pyautogui.prompt(text="Enter the File name:\n\np.s. use .txt format", title="File name",
                                     default="testings.txt")

        len_data = len(open(file_open, encoding='utf-8').readlines())

        with open(file_open, encoding='utf-8') as start_file:

            array_line = start_file.read().split('\n')

            count = 500

            cycles = (len_data // count)

            if len_data % count:
                cycles += 1

            for n_cycle in range(cycles):
                x = "\n".join(array_line[n_cycle * count: (n_cycle + 1) * count])
                file_name = 'newFile{}.txt'.format(n_cycle)
                with open(file_name, 'w', encoding='utf-8') as file_end:
                    file_end.write(x)

            th_list = []
            i = 0

            for n_cycle2 in range(cycles):
                
		file_name = 'newFile{}.txt'.format(n_cycle2)

                th = Thread(target=progon, args=(file_name,))

                th.start()

                th_list.append(th)

                print("Thread {} is start.".format(n_cycle2))

            for check_th in th_list:
                check_th.join()
                print('Finish Thread {}'.format(i))
                i += 1

        pyautogui.alert("good")

    elif break_file == 'BREAK':

        range_cycle = pyautogui.prompt(text="Enter the range:\np.s. need +1", title="Range", default="10")

        range_start = pyautogui.prompt(text="Enter the start range: ", title="Start Range", default="0")

        th_list = []

        for cycle in range(int(range_start), int(range_cycle)):
            
	file_name = 'newFile{}.txt'.format(cycle)

            try:
                th = Thread(target=progon, args=(file_name,))

                th.start()

                th_list.append(th)
            except Exception as e:
                logging.error('Failed.', exc_info=e)

            print("Thread {} is started.".format(range_start))

        for check_th in th_list:
            check_th.join()
            print('Finish Thread {}'.format(range_start))
            range_start += 1

    elif break_file == 'CHECK ERR':

        file_open = pyautogui.prompt(text="Enter the File name:\n", title="File name", default="errors.txt")

        len_data = len(open(file_open, encoding='utf-8').readlines())
	
	with open(file_open, encoding='utf-8') as start_file:

            array_line = start_file.read().split('\n')

            count = 100

            cycles = (len_data // count)

            if len_data % count:
                cycles += 1

            for n_cycle in range(cycles):
                x = "\n".join(array_line[n_cycle * count: (n_cycle + 1) * count])
                file_name = 'newFile{}.txt'.format(n_cycle)
                with open(file_name, 'w', encoding='utf-8') as file_end:
                    file_end.write(x)

            th_list = []
            i = 0

            for n_cycle2 in range(cycles):
                file_name = 'newFile{}.txt'.format(n_cycle2)

                th = Thread(target=post_progon, args=(file_name,))

                th.start()

                th_list.append(th)

                print("Thread {} is start.".format(n_cycle2))

            for check_th in th_list:
                check_th.join()
                print('Finish Thread {}'.format(i))
                i += 1

        pyautogui.alert("Checking finished success.")


elif chk == 'URL':

    new_url = pyautogui.prompt(text="Enter the URL:", title="URL", default="https://google.com")

    response = requests.get(srv + new_url)

    answer = json.loads(response.text)

    case_one = answer['data']['regexpSignatures']
    case_two = answer['data']['whitelist']['source']

    data_domainInCI = answer['data']['domainInCI']
    data_urlInCI = answer['data']['urlInCI']

    if case_one:
        if (data_domainInCI or data_urlInCI) and (data_domainInCI[0] or data_urlInCI[0]):
            if (data_domainInCI[0]['type'] != "Ложно положительный") or (data_urlInCI[0]['type'] != "Ложно положительный"):
                pyautogui.alert(text="False positive by url and whitelist.\nClear", title="Response")
            else:
                pyautogui.alert(text="False positive by domain and url and whitelist.\nClear.", title="Response")
        elif case_two['result']:
            pyautogui.alert(text="False positive by domain and whitelist.\nCLEAR", title="Response")
        else:
            pyautogui.alert(text="Probably consist a REGEXP.\nPHISH", title="Response")
    elif not case_two['result']:
        pyautogui.alert(text="False by whitelist.\nPHISH", title="Response")
    else:
        pyautogui.alert(text="No one of case is match.", title="Response")

else:
    pyautogui.alert(text="Ah shit, here we go again.", title="Shit happens...")