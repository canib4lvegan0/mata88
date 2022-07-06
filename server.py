import socket
import threading
import time
from threading import Thread

from database import DB

TAB = ' -' * 5 + ' '
STATE_TAB = ' .. ' * 5 + ' '

''' Configurações iniciais do socket '''
HOST = '0.0.0.0'
PORT = 5002

BUFFER_SIZE = 2048      # Definindo buffer de dados
threads = 0             # Contator de threads
LIST_CLIENTS = []       # Lista de clientes
LOCKS = dict()
saved_state = False


''' Relógio lógico do servidor '''
LOGIC_CLOCK = 0


''' Classe que representa uma Thread de um novo cliente conectado.'''
class ClientThread(Thread):

    def __init__(self, _id, ip, _port, connection):
        Thread.__init__(self)

        self.id = _id
        self.ip = ip
        self.port = _port
        self.connection = connection
        self.messages = []
        self.last_message = ''

        print(f'\n{TAB}Thread Cliente {str(_id)} criada.{TAB}\n')

    ''' Reseta estado da Thread '''
    def resetState(self):
        global saved_state
        
        time.sleep(10)
        saved_state = False

    ''' Envia requisição do servidor aos clientes '''
    def sendMark(self):
        for conn in LIST_CLIENTS:
            # conn.send(bytes('save', 'utf-8'))
            conn.send(bytes(" ".join(['save', str(LOGIC_CLOCK)]), "utf-8"))
        self.messages = []

        print(f'\n{STATE_TAB}Estado do Servidor: {self.last_message}{STATE_TAB}\n')

        reset = threading.Thread(target=self.resetState)
        reset.start()

    ''' Bloqueia a thread do cliente em operação '''
    def lock_threads(self, rgs):
        for rg in rgs:
            if not (rg in LOCKS):
                LOCKS[rg] = threading.Lock()

            LOCKS[rg].acquire()
            print('Bloqueando RG', rg)
        time.sleep(2)

    ''' Libera a thread do cliente em operação '''
    def release_threads(self, rgs):
        for rg in rgs:
            print('Liberando RG', rg)
            LOCKS[rg].release()

    ''' Recebe do servidor estado do cliente '''
    def recvMark(self):
        global saved_state
        if not saved_state:
            saved_state = True
            self.sendMark()
        else:
            print(f'\n{STATE_TAB}Mensagens no Canal do Cliente {self.id}: {self.messages}{STATE_TAB}\n')

    ''' Mantém a thread em execução enquanto o servidor estiver ativo '''
    def run(self):

        # Aguardando comunicação dos clientes
        while True:
            # Captura dados para a solicitação de autentificação enviados pelos clientes
            data = ''
            while True:
                # Captura dados enviados pelo correntista
                data = self.connection.recv(BUFFER_SIZE).decode('utf-8').split(' ')

                if data[0] == '1':      # Opção de login
                    # faz consulta pelo correntista no banco de dados
                    res = DB.login(data[1], data[2])

                    # Enviar uma resposta ao cliente
                    self.connection.send(bytes([res]))
                    if res == 0:   # Encontrou um correntista
                        break

                elif data[0] == '2':    # Opção de registrar correntista

                    # Registra um novo correntista no banco de dados
                    res = DB.register(data[1], data[2], data[3])
                    # Enviar uma resposta ao cliente
                    self.connection.send(bytes([res]))

                else:
                    # Encerra conexão e mata a thread
                    print(f'Thread Cliente {str(self.id)} fechada.')
                    self.connection.close()
                    return

            # Disponibilizando a interação do menu de operações para os clientes
            data = ''
            self.messages = []
            lock = threading.Lock()

            while True:
                global LOCKS
                global LOGIC_CLOCK

                # Captura a opção de operação enviada pelo cliente
                data = self.connection.recv(BUFFER_SIZE).decode('utf-8').split(' ')

                # Incrementando relógio lógico do servidor
                LOGIC_CLOCK += 1
                print(f'\n{STATE_TAB}Estado do relógio do servidor: {LOGIC_CLOCK}{STATE_TAB}\n')

                if data[0] != 'save' and not saved_state:   # Finaliza a comunicação/operação corrente
                    self.last_message = data

                elif data[0] != 'save' and saved_state:
                    self.messages.append(data)
                    print(f'\n{STATE_TAB}Mensagens no Canal do Cliente {self.id}: {self.messages}{STATE_TAB}\n')

                # Operação de saldo
                if data[0] == '0':
                    self.lock_threads([data[1]])        # Bloqueia correntista para movimentações
                    res = DB.query_cash(data[1])         # Busca saldo do correntista
                    self.release_threads([data[1]])     # Desbloqueia correntista para movimentações

                    # Enviando resposta ao cliente
                    self.connection.send(bytes(' '.join(['QUERY', str(res), str(LOGIC_CLOCK +1)]), 'utf-8'))

                # Operação de saque
                elif data[0] == '1':
                    self.lock_threads([data[1]])                # Bloqueia cliente
                    res = DB.withdraw(data[1], int(data[2]))    # Busca saldo do correntista
                    self.release_threads([data[1]])             # Desbloqueia cliente

                    # Enviando resposta ao cliente
                    self.connection.send(bytes(' '.join(['WITHDRAWING', str(res), str(LOGIC_CLOCK)]), 'utf-8'))

                # Operação de depósito
                elif data[0] == '2':
                    self.lock_threads([data[1]])                # Bloqueia cliente
                    res = DB.deposit(data[1], int(data[2]))     # Deposita valor
                    self.release_threads([data[1]])             # Desbloqueia cliente

                    # Enviando resposta ao cliente
                    self.connection.send(bytes(' '.join(['DEPOSITING', str(res), str(LOGIC_CLOCK)]), 'utf-8'))

                # Operação de transferência
                elif data[0] == '3':
                    self.lock_threads([data[1], data[3]])               # Bloqueia cliente
                    res = DB.transfer(data[1], int(data[2]), data[3])   # Transfere valores
                    self.release_threads([data[1], data[3]])            # Desbloqueia cliente

                    # Enviando resposta ao cliente
                    self.connection.send(bytes(' '.join(['TRANSFER', str(res), str(LOGIC_CLOCK)]), 'utf-8'))

                # Operação de logout
                elif data[0] == '4':
                    # Enviando resposta ao cliente
                    self.connection.send(bytes('LOGOUT', 'utf-8'))
                    break

                # Sinaliza servidor do estado do cliente
                elif data[0] == 'save':
                    self.recvMark()

                # Encerra a conexão
                else:
                    print(f'Thread Cliente {str(self.id)} fechada')
                    self.connection.close()
                    LIST_CLIENTS.remove(self.connection)

                    return


''' -------------------------------------------------------- 
Iniciando sockets e iniciando-os '''
socketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socketServer.bind((HOST, PORT))
socketServer.listen(1)

while True:
    conn, (host, port) = socketServer.accept()      # Aguardando conexão de um correntistas
    LIST_CLIENTS.append(conn)                       # Atualiza lista correntistas conectados
    threads += 1                                    # Incrementa número de threads

    # Cria uma thread paar o novo cliente
    newThread = ClientThread(threads, host, port, conn)
    newThread.start()       # Executa a nova thread


