import socket
import struct
import time
from _thread import *
import threading
from threading import Thread 
from socketserver import ThreadingMixIn 
from database import DB

# ----- START INITIAL SETTINGS -----
HOST = '0.0.0.0'
PORT = 5002
BUFFER_SIZE = 2048
threads = 0
LIST_CLIENTS = []
LOCKS = dict()
saved_state = False
# ----------

LOGIC_CLOCK = 0


class ClientThread(Thread): # ----- THREAD FOR A NEW CLIENT -----

    def __init__(self, id, ip, port, connection):
        Thread.__init__(self)

        # SET IP, PORT AND HANDLE CONNECTION TO CLIENT THREAD
        self.id = id
        self.ip = ip
        self.port = port
        self.connection = connection
        self.messages = []
        self.last_message = ''

        print("Thread Cliente "+str(id)+" criada")

    def resetState(self):
        global saved_state
        
        time.sleep(10)
        saved_state = False

    def sendMark(self):
        for conn in LIST_CLIENTS:
            # conn.send(bytes('save', 'utf-8'))
            conn.send(bytes(" ".join(['save', str(LOGIC_CLOCK)]), "utf-8"))
        self.messages = []
        print('Estado do Servidor:', self.last_message, '\n')

        reset = threading.Thread(target=self.resetState)
        reset.start()
        
    def lock_threads(self, rgs):
        for rg in rgs:
            if not (rg in LOCKS):
                LOCKS[rg] = threading.Lock()

            LOCKS[rg].acquire()
            print('Bloqueando RG', rg)
        time.sleep(2)

    def release_threads(self, rgs):
        for rg in rgs:
            print('Liberando RG', rg)
            LOCKS[rg].release()

    def recvMark(self):
        global saved_state
        if not saved_state:
            saved_state = True
            self.sendMark()
        else:
            print('\nMessagens no Canal do Cliente', self.id, ': ', self.messages, '\n')

    def run(self): # ----- EXECUTION OF EACH CLIENT THREAD -----

        while True:
            # ----- LOOP TO GET DATA TO AUTHENTICATION SENDED OF CLIENT -----
            data = ''
            while True:

                data = self.connection.recv(BUFFER_SIZE).decode("utf-8").split(' ') # GET DATA SENDED BY CLIENT

                if data[0] == '1': # LOGIN OPTION
                    res = DB.login(data[1], data[2]) # QUERY BY A USER IN DATABASE

                    self.connection.send(bytes([res])) # SEND RESPONSE OF DATABASE TO CLIENT
                    if res == 0:
                        break # IF FIND A USER, LEAVE LOOP

                elif data[0] == '2': # REGISTER OPTION
                    res = DB.register(data[1], data[2], data[3]) # REGISTER A USER IN DATABASE

                    self.connection.send(bytes([res])) # SEND RESPONSE OF DATABASE TO CLIENT

                else: # ANOTHER OPTION
                    print("Thread Cliente "+str(self.id)+" fechada")
                    self.connection.close()
                    return

            # ----- LOOP TO HANDLE OPERATIONS OF CLIENT -----
            data = ''
            self.messages = []
            lock = threading.Lock()

            while True:
                global LOCKS
                global LOGIC_CLOCK
                data = self.connection.recv(BUFFER_SIZE).decode("utf-8").split(' ') # GET OPERATION SENDED BY CLIENT

                LOGIC_CLOCK += 1
                print(f'Estado do relógio lógico: {LOGIC_CLOCK}')

                if data[0] != 'save' and not saved_state:
                    self.last_message = data

                elif data[0] != 'save' and saved_state:
                    self.messages.append(data)
                    print('\nMessagens no Canal do Cliente', self.id, ': ', self.messages, '\n')

                if data[0] == '0': # OPERATION QUERY CASH
                    self.lock_threads([data[1]])
                    res = DB.queryCash(data[1]) # QUERY CASH MONEY
                    self.release_threads([data[1]])

                    self.connection.send(bytes(" ".join(["QUERY", str(res), str(LOGIC_CLOCK)]), "utf-8")) # SEND RESPONSE OF DATABASE TO CLIENT

                elif data[0] == '1': # OPERATION WITHDRAW
                    self.lock_threads([data[1]])
                    res = DB.withdraw(data[1], int(data[2])) # WITHDRAWING MONEY
                    self.release_threads([data[1]])

                    self.connection.send(bytes(" ".join(["WITHDRAWING", str(res), str(LOGIC_CLOCK)]), "utf-8")) # SEND RESPONSE OF DATABASE TO CLIENT

                elif data[0] == '2': # OPERATION DEPOSIT
                    self.lock_threads([data[1]])
                    res = DB.deposit(data[1], int(data[2])) # DEPOSITING MONEY
                    self.release_threads([data[1]])

                    self.connection.send(bytes(" ".join(["DEPOSITING", str(res), str(LOGIC_CLOCK)]), "utf-8")) # SEND RESPONSE OF DATABASE TO CLIENT

                elif data[0] == '3': # OPERATION TRANSFER
                    self.lock_threads([data[1], data[3]])
                    res = DB.transfer(data[1], int(data[2]), data[3])# TRANSFERING MONEY TO ANOTHER CLIENT
                    self.release_threads([data[1], data[3]])

                    self.connection.send(bytes(" ".join(["TRANSFER", str(res), str(LOGIC_CLOCK)]), "utf-8")) # SEND RESPONSE OF DATABASE TO CLIENT

                elif data[0] == '4': # OPERATION LOGOUT
                    self.connection.send(bytes("LOGOUT", "utf-8"))
                    break

                elif data[0] == 'save':
                    self.recvMark()

                else: # ANOTHER OPERATION CLOSES THE CONNECTION
                    print("Thread Cliente "+str(self.id)+" fechada")
                    self.connection.close()
                    LIST_CLIENTS.remove(self.connection)

                    return


# ----- INITIALIZES SOCKET CONFIGURATION -----
socketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socketServer.bind((HOST, PORT))
socketServer.listen(1)
# ----------

while True:    
    conn, (host, port) = socketServer.accept() # WAITING A CONNECTION OF CLIENT
    LIST_CLIENTS.append(conn)
    threads += 1 # INCREMENTS NUMBER OF THREAD
    newThread = ClientThread(threads, host, port, conn) # CREATES THREAD TO NEW CLIENT
    newThread.start() # RUN THREAD


