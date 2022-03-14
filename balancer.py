#!/usr/bin/python3

import socket
import configparser
import datetime
import random

# читаем конфиг
config = configparser.ConfigParser()
config.read("./balancer.ini")
b_log, n_count = config["balancer"]["log"], int(config["balancer"]["nodescount"])

# функция записи в лог с выводом на экран
def Filelog(s):
    print(s)
    with open(b_log, 'a') as fd:
         fd.write("{} {}\n".format(datetime.datetime.now(), s))
 
 
Filelog("Starting fucking balancer ({} nodes)...".format(n_count))

# Делаем список узлов с параметрами и объектами соединений.
# Каждый элемент списка - словарь, где N - номер узла (ключ), ip - ip-адрес, port - порт на котором слушает узел
# conn - объект-сокет (сначала None, потом устанавливается), name - имя узла (получаем при инициализации соединния)
nodes = []

# Делаем список привязок клиент-узел.
# Каждый элемент - словарь, где 'client' - номер клиента, 'idx' - номер узла, назначенного клиенту
sticky_list = []

# Считываем из инишника информацию о заданных узлах
for i in range(n_count):
    n_idx = "node{}".format(i)
    nodes.append({'N' : i, 'ip' : config[n_idx ]["ip"], 'port' : int(config[n_idx ]["port"]), 'conn' : None, 'name' : None })

# Функция передает данные в соединение (если оно существует) и возвращает ответ сервера
def Sendrecv(conn, msg):
    try:
        if (conn):
            conn.sendall(msg.encode())
            data = conn.recv(1024)
            return data.decode()
        else:
            return None
    except Exception:
            return None

# Первичная инициализация соединений
# Для каждого узла создаем соединение и делаем первичный запрос - получаем имя узла
for n in nodes:
    Filelog("Node {} ({}:{})".format(n['N'], n['ip'], n['port']))
    try:
        # Создаем сокет и привязываемся к нужному ip и порту
        n['conn'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        n['conn'].connect((n['ip'], n['port']))       
        # Первое сообщение - запрашиваем имя узла
        n['name'] = Sendrecv(n['conn'], 'init');
        Filelog('Connected to {}:{}  Get node name: {}'.format(n['ip'], n['port'], n['name']));
    except Exception:
        n['conn'] = None;
        Filelog('Connection error to {}:{}'.format(n['ip'], n['port']));
        
# Функция возвращает номер очередного узла, к которому установлено активное соединение,
# без привязки к клиенту. Можно использовать только ее - получится round robin
def getNextConn(curridx):
    idx = curridx
    result = False
    while not result:
        idx += 1
        if (idx >= len(nodes)):
            idx = 0
        if (not result) and (nodes[idx]['conn'] != None):
            result = True
        if (not result) and (idx == curridx):
            result = True
    return idx

# Функция проверяет, назначен ли данному клиенту какой-нибудь узел, если назначен - возвращает его номер
# Если не назначен - назначает по round robin, делает запись в список привязок, возвращает назначенный номер узла
def getStickyNode(client_id, curridx):
    for s in sticky_list:
        if s['client'] == client_id:
            return s['idx']
    newidx = getNextConn(curridx)
    sticky_list.append({'client' : client_id, 'idx' : newidx})
    return newidx  

# Основной цикл программы. Считываем сообщения из консоли, генерируем случайный id клиента,
# находим (или назначаем новый) узел по sticky session
# Отправляем данные в соответствующий узел, получаем ответ
try:
    idx = 0
    mess = 'Fuck'
    while mess != 'quit':
        mess = input('Message?')
        cl_id = random.randint(1, 10)
        idx = getStickyNode(cl_id, idx)
        Filelog('Sending message {} (Client {}) to node {} '.format(mess, cl_id, idx))
        answer = Sendrecv(nodes[idx]['conn'], mess)
        Filelog('Get answer {}'.format(answer))          
finally:
# Закрываем все активные соединения
    for n in nodes:
        if (n['conn'] != None):
            n['conn'].close()




