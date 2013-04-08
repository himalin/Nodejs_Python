import socket
import time
import random

if __name__ == '__main__':
 sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 sock.connect(('127.0.0.1', 8153))
 
 map = {}
 ibm = {}
 baidu = {}
 ms = {}

 ibm["name"] = "ibm"
 ibm["high"] = 9.2
 ibm["low"] = 8.7
 ibm["total_account"] = 56

 baidu["name"] = "baidu"
 baidu["high"] = 9.3
 baidu["low"] = 8.6
 baidu["total_account"] = 45

 ms["name"] = "ms"
 ms["high"] = 9.1
 ms["low"] = 8.8
 ms["total_account"] = 67

 map[1] = ibm
 map[2] = baidu
 map[3] = ms

 for key in map:
    msg = "{\"Name\":\"%s\",\"High\":\"%.2f\",\"Low\":\"%.2f\",\"Total_account\":\"%d\"}" %(map[key]["name"],map[key]["high"],map[key]["low"],map[key]["total_account"])
    sock.send(msg)

 while True:
    time.sleep(2)
    #??????
    index = random.randint(1,3)
    #???
    price = random.uniform(8, 10)
    #???
    account = random.randint(1, 10)

    #????????
    if price > map[index]["high"]:
       map[index]["high"] = price;
    elif price < map[index]["low"]:
       map[index]["low"] = price;

    map[index]["total_account"] +=  account;

    msg = "{\"Name\":\"%s\",\"High\":\"%.2f\",\"Low\":\"%.2f\",\"Total_account\":\"%d\"}" %(map[index]["name"],map[index]["high"],map[index]["low"],map[index]["total_account"])
    sock.send(msg)

 sock.close()