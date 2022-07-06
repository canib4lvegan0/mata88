import socket
import time
import threading
from threading import Thread

# Configurando sockets
HOST = socket.gethostname()
PORT = 5002
BUFFER_SIZE = 2048

# Relógio lógico do cliente
LOGIC_CLOCK = 0


# Classe que representa... todo
class RecvThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.waiting_response = False
        self.saved_state = False
        self.messages = []
        self.last_message = 'WAITING COMMAND'

    # todo
    def run(self):
        global LOGIC_CLOCK

        while True:
            try:
                resp = socketClient.recv(BUFFER_SIZE).decode("utf-8").split(' ')

                # Capturando valor do relógio lógico do Servidor e atualizando relógio local
                if resp:
                    LOGIC_CLOCK = resp.pop()
                    print(f'Estado do relógio lógico: {LOGIC_CLOCK}')

                if resp[0] != "save":
                    self.last_message = data
                    self.waiting_response = False

                if resp[0] == 'QUERY':
                    queryResponse(resp)
                elif resp[0] == 'WITHDRAWING':
                    withdrawResponse(resp)
                elif resp[0] == 'DEPOSITING':
                    depositResponse(resp)
                elif resp[0] == 'TRANSFER':
                    transferResponse(resp)
                elif resp[0] == 'LOGOUT':
                    socketClient.setblocking(True)
                    break
                elif resp[0] == "save":
                    self.recvMark()

                self.sendMark()

            except:
                pass

    # todo
    def resetState(self):
        time.sleep(10)
        self.saved_state = False

    # todo
    def sendMark(self):
        if not self.saved_state:
            self.messages = []
            socketClient.send(bytes('save', 'utf-8'))
            print(f'\nEstado do Cliente: {self.last_message}\n')

            self.saved_state = True
            reset = threading.Thread(target=self.resetState)
            reset.start()

    # todo
    def recvMark(self):
        if not self.saved_state:
            self.sendMark()
        # else:
        #     print(f'\nMensagens no Canal: {self.messages}')


# Exibe mensagem apropriada sobre cadastro de usuário
def handleRegister(code):
    if code == 0:
        print('\nUsuário cadastrado com sucesso!\n')
        return True
    elif code == 1:
        print('\nJá existe um usuário com este RG.\n')

    return False


# Exibe mensagem apropriada sobre login
def handleAuth(code):
    if code == 0:
        print('\nLogin realizado com sucesso!\n')
        return True
    elif code == 1:
        print('\nSenha incorreta.\n')
    elif code == 2:
        print('\nUsuário inexistente.\n')

    return False


# Exibe menu inicial
def showMenu():
    print('\nOpções: \n1 - Login\n2 - Cadastrar\n3 - Sair\n')


# Exibe operações disponiveis ao cliente
def showOperations():
    print('***' * 10)
    print('Operações: \n0 - Saldo\n1 - Saque\n2 - Depósito\n3 - Transferência\n4 - Logout\n')


# Exibe saldo do cliente
def queryResponse(data):
    print(f'\t\tSaldo atual: R${int(data[1])}')


# Exibe mensagem apropriada sobre operação de saque
def withdrawResponse(data):
    if (code := int(data[1])) == 0:
        print('\nSaque efetuado com sucesso.\n')
    elif code == 1:
        print('\nSaldo insuficiente.\n')
    else:
        print('\nErro ao sacar.\n')


# Exibe mensagem apropriada sobre operação de depósito
def depositResponse(data):
    if int(data[1]) == 0:
        print('\nDepósito efetuado com sucesso!\n')
    else:
        print('\nErro ao depositar.\n')


# Exibe mensagem apropriada sobre operação de transferência
def transferResponse(data):
    if (code := int(data[1])) == 0:
        print('\nTransferência realizada com sucesso.\n')
    elif code == 1:
        print('\nSaldo insuficiente.\n')
    else:
        print('\nCorrentista não encontrado.\n')


# Opera o registro de um novo usuário
def register():
    while True:
        name = input("Digite seu nome: ")
        rg = input("Digite seu RG: ")
        password = input("Digite uma senha: ")

        # Enviando dados de cadastro ao servidor
        socketClient.send(bytes('2 ' + name + ' ' + rg + ' ' + password, 'utf-8'))

        # Recebendo status de cadastro do servidor
        resp = socketClient.recv(BUFFER_SIZE)

        if not resp:
            raise

        code = int.from_bytes(resp, byteorder="big")
        if not handleRegister(code):
            try_again = input('Deseja tentar novamente? (y/n) ')

            if try_again.lower() == 'y':
                continue
            else:
                break
        else:
            break


# todo
def login():
    while True:
        rg = input("Digite o RG: ")
        password = input("Digite a senha: ")

        # Enviando dados de login ao servidor
        socketClient.send(bytes('1 ' + rg + ' ' + password, 'utf-8'))

        # Recebendo status de login do servidor
        resp = socketClient.recv(BUFFER_SIZE)  # RECEIVE DATA FROM SERVER

        if not resp:
            raise

        code = int.from_bytes(resp, byteorder="big")
        if not handleAuth(code):
            try_again = input('Deseja tentar novamente? (y/n) ')
            if try_again == 'y':
                continue
            else:
                return
        else:
            break

    # todo
    socketClient.setblocking(False)
    recv = RecvThread()
    recv.start()

    while True:
        showOperations()
        option = input("Digite o número de uma operação: ")

        # Operação de exibir saldo
        if option == '0':
            socketClient.send(bytes(" ".join([option, rg]), 'utf-8'))
            # resp = socketClient.recv(BUFFER_SIZE)

            recv.waiting_response = True
            while recv.waiting_response:
                pass

        # Operação de saque
        elif option == '1':
            value = input("Digite o valor a ser sacado: ")
            socketClient.send(bytes(" ".join([option, rg, value]), 'utf-8'))
            # resp = socketClient.recv(BUFFER_SIZE)

            recv.waiting_response = True
            while recv.waiting_response:
                pass

        # Operação de depósito
        elif option == '2':
            value = input("Digite o valor a ser depositado: ")
            socketClient.send(bytes(" ".join([option, rg, value]), 'utf-8'))
            # resp = socketClient.recv(BUFFER_SIZE)

            recv.waiting_response = True
            while recv.waiting_response:
                pass

        # Operação de transferência
        elif option == '3':
            dest = input("Digite o RG do titular da conta destino: ")
            value = input("Digite o valor da transferência: ")
            socketClient.send(bytes(" ".join([option, rg, value, dest]), 'utf-8'))
            # resp = socketClient.recv(BUFFER_SIZE)

            recv.waiting_response = True
            while recv.waiting_response:
                pass

        # Operacao de logout
        elif option == '4':
            socketClient.send(bytes(option, 'utf-8'))
            print('\nLogout feito com sucesso!\n')
            break

        elif data == 'save':
            recv.recvMark()
            recv.waiting_response = True
            while recv.waiting_response:
                pass

        else:
            print('\nOperação inválida.\n')


# Iniciando sockets
try:
    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketClient.connect((HOST, PORT))
except:
    print('Erro ao conectar ao servidor.')
    exit(0)


# Iniciando login
data = ''
try:
    while True:
        showMenu()
        option = input("Digite a opção desejada: ")

        if option == '1':
            login()
        elif option == '2':
            register()
        elif option == '3':
            break
        else:
            print('Opção inválida.')
except:
    raise 'Algum erro ocorreu na comunicação com o servidor.'


# Encerrando a conexão com o servidor
socketClient.send(bytes('3', 'utf-8'))
socketClient.close()
print('\nAté logo!')
