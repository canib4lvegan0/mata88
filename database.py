
TAB = ' =' * 5 + ' '

''' Classe que representa o DB de Dados do Sistema Bancário,
gerenciando Nome, RG, Senha e saldo bancário dos correntistas '''
class DB:

    ''' Abre arquivo de db '''
    @staticmethod
    def open_file():
        f = open('db.txt', 'a')
        f.close()
        return open('db.txt', 'r+')

    ''' Verifica se o correntista existe '''
    @staticmethod
    def check_client(_rg):
        file = DB.open_file()

        with file:
            line = file.readline()
            while line:
                [_, rg, _, _] = line.split('|')     # Captura dados do cliente

                if rg == _rg:
                    file.close()
                    return 0

                line = file.readline()
        file.close()

        return 1

    ''' Autentifica login do correntista '''
    @staticmethod
    def login(_rg, _pass):
        file = DB.open_file()

        with file:
            line = file.readline()

            while line:
                # Captura dados do cliente
                [_, rg, password, _] = line.split('|')

                # Verifica se cliente existe
                if rg == _rg:
                    print(f'\n{TAB}Usuário encontrado.{TAB}\n')
                    if password == _pass:
                        print(f'\n{TAB}Acesso permitido.{TAB}\n')
                        file.close()
                        return 0
                    else:
                        print(f'\n{TAB}Senha incorreta.{TAB}\n')
                        file.close()
                        return 1

                line = file.readline()

            print(f'\n{TAB}Usuário não encontrado.{TAB}\n')
            file.close()
            return 2

    ''' Registra um correntista '''
    @staticmethod
    def register(name, rg, pwd):
        file = DB.open_file()

        file.seek(0, 2)
        if DB.check_client(rg) == 0:
            print(f'\n{TAB}RG já cadastrado.{TAB}\n')
            return 1

        file.seek(file.tell()-1, 0)
        c = file.read(1)
        if c != '\n':
            file.write('\n')

        file.write('|'.join([name, rg, pwd, '0\n']))
        file.close()
        print(f'\n{TAB}Usuário {name} cadastrado.{TAB}\n')
        return 0

    ''' Busca pelo saldo co correntista '''
    @staticmethod
    def query_cash(_rg):
        file = DB.open_file()
        cash = DB.get_cash(file, _rg)
        file.close()
        return cash

    ''' Captura saldo do correntista '''
    @staticmethod
    def get_cash(file, _rg):
        for line in file:
            [_, rg, _, cash] = line.split('|')
            if rg == _rg:
                return int(cash)

        return 0

    ''' Saca dinheiro de um correntista '''
    @staticmethod
    def withdraw(_rg, value):
        file = DB.open_file()

        cash = DB.get_cash(file, _rg)

        # Não realiza a operação de saque se o saldo for menor que o valor a solicitado
        if cash < value:
            print(f'\n{TAB}Saldo insuficiente.{TAB}\n')
            file.close()
            return 1

        # Atualizando saldo após saque
        cash -= value

        # Rescrevendo no banco de dados o novo saldo do correntista
        lines = []
        file.seek(0, 0)
        for line in file:
            [username, rg, password, _] = line.split('|')
            if rg != _rg:
                lines.append(line)
            else:
                lines.append('|'.join([username, rg, password, str(cash)+'\n']))

        file.seek(0, 0)
        file.truncate()
        file.writelines(lines)
        file.close()
        print(f'\n{TAB}Saque efetuado.{TAB}\n')

        return 0

    ''' Deposita dinheiro para um correntista '''
    @staticmethod
    def deposit(_rg, value):
        file = DB.open_file()

        cash = DB.get_cash(file, _rg)

        # Atualizando saldo após saque
        cash += value

        # Rescrevendo no banco de dados o novo saldo do correntista
        lines = []
        file.seek(0, 0)
        for line in file:
            [username, rg, password, _] = line.split('|')
            if rg != _rg:
                lines.append(line)
            else:
                lines.append('|'.join([username, rg, password, str(cash)+'\n']))

        file.seek(0, 0)
        file.truncate()
        file.writelines(lines)
        file.close()
        print(f'\n{TAB}Depósito efetuado.{TAB}\n')

        return 0

    ''' Transfere dinheiro de um correntista para outro '''
    @staticmethod
    def transfer(_rg_source, value, _rg_dest):
        if DB.check_client(_rg_dest) == 0:               # Verifica se o correntista destinatário existe
            if DB.withdraw(_rg_source, value) == 0:     # Faz um saque no valor solicitado da conta de origem
                if DB.deposit(_rg_dest, value) == 0:    # Faz um depósito no valor solicitado na conta de destino
                    print(f'\n{TAB}Transferência efetuada.{TAB}\n')
                    return 0
            else:
                return 1
        else:
            print(f'\n{TAB}Correntista não encontrado.{TAB}\n')
            return 2
