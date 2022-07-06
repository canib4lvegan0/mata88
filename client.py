import socket
import time
import threading
from threading import Thread

TAB = ' -' * 5 + ' '
STATE_TAB = ' .. ' * 5 + ' '

# Configurando sockets
HOST = socket.gethostname()
PORT = 5002
BUFFER_SIZE = 2048

# Relógio lógico do cliente
LOGIC_CLOCK = 0

class SocketError(BaseException):
    def __str__(self):
        return 'SocketError: algum error acorreu na conexão com servidor'


SOCKET_ERROR = SocketError

''' Classe que representa uma Thread do cliente.
Mantem a Thread em atividade, atualiza estado, enviar e recebe requisição do servidor. '''
class RecvThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.waiting_response = False
        self.saved_state = False
        self.messages = []
        self.last_message = 'WAITING COMMAND'

    ''' Mantém a thread em atividade enquanto o cliente estiver ativo '''
    def run(self):
        global LOGIC_CLOCK

        # Aguardando comunicação do servidor
        while True:
            try:
                resp = socketClient.recv(BUFFER_SIZE).decode("utf-8").split(' ')

                # Captura valor do relógio lógico do Servidor e atualizando o local
                if resp:
                    LOGIC_CLOCK = resp.pop()
                    print(f'\n{STATE_TAB}Estado do relógio lógico: {LOGIC_CLOCK}{STATE_TAB}\n')

                if resp[0] != "save":           # Finaliza a comunicação/operação corrente
                    self.last_message = data
                    self.waiting_response = False
                if resp[0] == 'QUERY':          # Finaliza operação de saldo
                    queryResponse(resp)
                elif resp[0] == 'WITHDRAWING':  # Finaliza operação de saque
                    withdrawResponse(resp)
                elif resp[0] == 'DEPOSITING':   # Finaliza operação de depósito
                    depositResponse(resp)
                elif resp[0] == 'TRANSFER':     # Finaliza operação de transferência
                    transferResponse(resp)
                elif resp[0] == 'LOGOUT':       # Finaliza operação de logout, liberando o socket
                    socketClient.setblocking(True)
                    break
                elif resp[0] == "save":         # Mantém a comunicação/operação corrente
                    self.recvMark()

                self.sendMark()

            except:
                pass

    ''' Atualiza estado da Thread '''
    def resetState(self):
        time.sleep(10)
        self.saved_state = False

    ''' Enviar requisição ao servidor o estado do cliente '''
    def sendMark(self):
        if not self.saved_state:
            self.messages = []
            socketClient.send(bytes('save', 'utf-8'))

            print(f'\n{STATE_TAB}Estado do Cliente: {self.last_message}{STATE_TAB}\n')

            self.saved_state = True
            reset = threading.Thread(target=self.resetState)
            reset.start()

    ''' Recebe do servidor estado do cliente '''
    def recvMark(self):
        if not self.saved_state:
            self.sendMark()
        # else:
        #     print(f'\nMensagens no Canal: {self.messages}')


''' Manipula o cadastro de um usuário '''
def handleRegister(code):
    if code == 0:
        print(f'\n{TAB}Usuário cadastrado com sucesso!{TAB}\n')
        return True
    elif code == 1:
        print(f'\n{TAB}Já existe um usuário com este RG.{TAB}\n')

    return False


''' Manipula login de um usuário '''
def handleAuth(code):
    if code == 0:
        print(f'\n{TAB}Login realizado com sucesso!{TAB}\n')
        return True
    elif code == 1:
        print(f'\n{TAB}Senha incorreta.{TAB}\n')
    elif code == 2:
        print(f'\n{TAB}Usuário inexistente.{TAB}\n')

    return False


''' Exibe menu da Home do sistema bancário '''
def showMenu():
    print('\nOpções: \n1 - Login\n2 - Cadastrar\n3 - Sair\n')


''' Exibe operações disponíveis ao cliente '''
def showOperations():
    print('*-*-*' * 10)
    print('Operações: \n0 - Saldo\n1 - Saque\n2 - Depósito\n3 - Transferência\n4 - Logout\n')


''' Exibe resultado da operação saldo '''
def queryResponse(_data):
    print(f'\n{TAB}Saldo atual: R${int(_data[1])}{TAB}\n')


''' Exibe mensagem sobre operação de saque '''
def withdrawResponse(_data):
    if (code := int(_data[1])) == 0:
        print(f'\n{TAB}Saque efetuado com sucesso.{TAB}\n')
    elif code == 1:
        print(f'\n{TAB}Saldo insuficiente.{TAB}\n')
    else:
        print(f'\n{TAB}Erro ao sacar.{TAB}\n')


''' Exibe mensagem sobre operação de depósito '''
def depositResponse(_data):
    if int(_data[1]) == 0:
        print(f'\n{TAB}Depósito efetuado com sucesso!\n')
    else:
        print(f'\n{TAB}Erro ao depositar.\n')


''' Exibe mensagem sobre operação de transferência '''
def transferResponse(_data):
    if (code := int(_data[1])) == 0:
        print(f'\n{TAB}Transferência realizada com sucesso.{TAB}\n')
    elif code == 1:
        print(f'\n{TAB}Saldo insuficiente.{TAB}\n')
    else:
        print(f'\n{TAB}Correntista não encontrado.{TAB}\n')


''' Formulário o registro de usuário '''
def register():
    while True:
        print(TAB)
        name = input('Digite seu nome: ')
        rg = input('Digite seu RG: ')
        password = input('Digite uma senha: ')

        # Enviando dados de cadastro ao servidor
        socketClient.send(bytes('2 ' + name + ' ' + rg + ' ' + password, 'utf-8'))

        # Recebendo status de cadastro do servidor
        resp = socketClient.recv(BUFFER_SIZE)
        if not resp:
            raise SocketError

        # Validando registro do usuário
        code = int.from_bytes(resp, byteorder="big")
        if not handleRegister(code):
            try_again = input('Deseja tentar novamente? (y/n) ')
            if try_again.lower() == 'y':
                continue
            else:
                break
        else:
            break


''' Formulário de login do usuário, em seguida gerencia a interação dele com as operações bancárias'''
def login():
    while True:
        rg = input('Digite o RG: ')
        password = input('Digite a senha: ')

        # Enviando dados de login ao servidor
        socketClient.send(bytes('1 ' + rg + ' ' + password, 'utf-8'))

        # Recebendo status de login do servidor
        resp = socketClient.recv(BUFFER_SIZE)
        if not resp:
            raise SocketError

        # Autentificando login do usuário
        code = int.from_bytes(resp, byteorder="big")
        if not handleAuth(code):
            try_again = input('Deseja tentar novamente? (y/n) ')
            if try_again.lower() == 'y':
                continue
            else:
                return
        else:
            break

    # Criando/inicializando thread do cliente
    socketClient.setblocking(False)
    recv = RecvThread()
    recv.start()

    # Disponibilizando a interação do usuário com o menu de operações
    while True:
        showOperations()
        option = input('Digite o número de uma operação: ')

        # Operação de saldo
        if option == '0':

            # Enviando requisição de "saldo" ao servidor
            socketClient.send(bytes(' '.join([option, rg]), 'utf-8'))
            # resp = socketClient.recv(BUFFER_SIZE)

            # Aguardando resposta do servidor
            recv.waiting_response = True
            while recv.waiting_response:
                pass

        # Operação de saque
        elif option == '1':
            value = input('Digite o valor a ser sacado: ')

            # Enviando requisição de "saque" ao servidor
            socketClient.send(bytes(' '.join([option, rg, value]), 'utf-8'))
            # resp = socketClient.recv(BUFFER_SIZE)

            # Aguardando resposta do servidor
            recv.waiting_response = True
            while recv.waiting_response:
                pass

        # Operação de depósito
        elif option == '2':
            value = input('Digite o valor a ser depositado: ')

            # Enviando requisição de "depósito" ao servidor
            socketClient.send(bytes(" ".join([option, rg, value]), 'utf-8'))
            # resp = socketClient.recv(BUFFER_SIZE)

            # Aguardando resposta do servidor
            recv.waiting_response = True
            while recv.waiting_response:
                pass

        # Operação de transferência
        elif option == '3':
            dest = input('Digite o RG do titular da conta destino: ')
            value = input('Digite o valor da transferência: ')

            # Enviando requisição de "transferência" ao servidor
            socketClient.send(bytes(' '.join([option, rg, value, dest]), 'utf-8'))
            # resp = socketClient.recv(BUFFER_SIZE)

            # Aguardando resposta do servidor
            recv.waiting_response = True
            while recv.waiting_response:
                pass

        # Operação de logout
        elif option == '4':

            # Enviando requisição de "transferência" ao servidor
            socketClient.send(bytes(option, 'utf-8'))

            print(f'\n{TAB}Logout feito com sucesso!{TAB}\n')
            break

        # Sinaliza servidor do estado do cliente
        elif data == 'save':
            recv.recvMark()
            recv.waiting_response = True
            while recv.waiting_response:
                pass

        else:
            print(f'\n{TAB}Operação inválida.{TAB}\n')


''' -------------------------------------------------------- 
Iniciando sockets e iniciando conexão com servidor '''
try:
    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketClient.connect((HOST, PORT))
except:
    raise SocketError


''' --------------------------------------------------------
Home do sistema bancário '''
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
    raise SocketError


''' --------------------------------------------------------
Encerrando a conexão com o servidor e fechando socket '''
socketClient.send(bytes('3', 'utf-8'))
socketClient.close()
print('\nAté logo!')
