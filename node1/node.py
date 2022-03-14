#!/usr/bin/python3

import socket
import configparser
import datetime
import random
import hashlib
import time

# читаем конфиг
config = configparser.ConfigParser()
config.read("./node.ini")
n_log, n_port, n_name = config["node"]["log"], config["node"]["port"], config["node"]["name"]

# функция записи в лог с выводом на экран
def Filelog(s):
    print(s)
    with open(n_log, 'a') as fd:
         fd.write("{} {}\n".format(datetime.datetime.now(), s))
         
Filelog("Starting {}  port {}... oh, shi...".format(n_name, n_port))

# Создаем сокет, привязываем его к порту и начинаем слушать подключения
srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
srv_socket.bind(('', int(n_port)))
srv_socket.listen(100)

while True:
    # принимаем соединение от клиента
    clnt_sock, clnt_addr = srv_socket.accept()
    Filelog('Connection from {}'.format(clnt_addr))
    try:
        # начинаем получать данные от клиента
        while True:
            data = clnt_sock.recv(1024)
            if not data:
                break
            dataget = data.decode()
            Filelog('Get {}'.format(dataget))
            datasend = n_name
            # по запросу init - возвращаем имя сервера
            # в противном случае возвращаем имя и хэш полученного сообщения
            if (dataget != 'init'):
                # вычисляем md5-хэш и изображаем занятость
                datasend = '{} {}'.format(n_name, hashlib.md5(datasend.encode("utf-8")).hexdigest())
                time.sleep(random.randint(10, 200)/ 1000)
            clnt_sock.sendall(datasend.encode())
    finally:
        clnt_sock.close()
    break
    
srv_socket.close()

