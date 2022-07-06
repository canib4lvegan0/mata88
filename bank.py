# ----- CLASS REPRESENTING THE DATABASE -----
class Banco:
    @staticmethod
    def openFile(): # METHOD TO OPEN FILE 
        f = open("db.txt", 'a')
        f.close()

        return open("db.txt", 'r+')

    @staticmethod
    def checkClient(rgClient): # CHECKS IF A CLIENT EXIST
        file = Banco.openFile()

        with file:
            line = file.readline() # GET A LINE OF FILE
            while line: 
                [username, rg, password, cash] = line.split('|') # GET DATA OF A CLIENT
                if rg == rgClient: # VERIFY IF RG IS EQUAL
                    file.close()
                    return 0

                line = file.readline()

        file.close()
        return 1
    
    @staticmethod
    def login(rgClient, pwdClient): # LOGIN A CLIENT
        file = Banco.openFile()

        with file:
            line = file.readline() # GET A LINE OF FILE

            while line:
                [username, rg, password, cash] = line.split('|') # GET DATA OF A CLIENT

                # VERIFY IF CLIENT EXIST IN FILE
                if rg == rgClient:
                    print("Usuário encontrado")
                    if password == pwdClient:
                        print("Acesso permitido")
                        file.close()
                        return 0
                    else:
                        print("Senha incorreta")
                        file.close()
                        return 1

                line = file.readline()

            print("Usuário não encontrado")
            file.close()
            return 2
    
    @staticmethod
    def register(name, rg, pwd):
        file = Banco.openFile()
        file.seek(0, 2)
        if Banco.checkClient(rg) == 0:
            print('RG já cadastrado')
            return 1

        file.seek(file.tell()-1, 0)
        c = file.read(1)
        if c != '\n':
            file.write('\n')

        file.write("|".join([name, rg, pwd, "0\n"]))
        file.close()
        print('Usuário ' + name + ' cadastrado')
        return 0

    @staticmethod
    def queryCash(rg):
        file = Banco.openFile()

        cash = Banco.getCash(file, rg) 

        file.close()

        return cash

    @staticmethod
    def getCash(file, rgClient): # GET CASH OF A CLIENT
        for line in file:
            [username, rg, password, cash] = line.split('|')
            if rg == rgClient:
                return int(cash)
        
        return 0

    @staticmethod
    def withdraw(rgClient, value): # WITHDRAW MONEY OF A CLIENT
        file = Banco.openFile()

        cash = Banco.getCash(file, rgClient) 
        if cash < value: # IF CASH IS LESS THAN VALUE, RETURNS
            print('Saldo insuficiente')
            file.close()
            return 1
        
        cash -= value # ELSE TAKE VALUE OF CASH

        # ----- REWRITE FILE WITH NEW CASH OF CLIENT ----
        lines = []
        file.seek(0,0)
        for line in file:
            [username, rg, password, oldCash] = line.split('|')
            if rg != rgClient:
                lines.append(line)
            else:
                lines.append("|".join([username, rg, password, str(cash)+"\n"]))

        file.seek(0, 0)
        file.truncate()
        file.writelines(lines)
        file.close()
        print('Saque efetuado')

        return 0
    
    @staticmethod
    def deposit(rgClient, value): # DEPOSIT MONEY OF A CLIENT
        file = Banco.openFile()

        cash = Banco.getCash(file, rgClient)
        cash += value # INCREMENTS VALUE IN CASH

        # ----- REWRITE FILE WITH NEW CASH OF CLIENT ----

        lines = []
        file.seek(0, 0)
        for line in file:
            [username, rg, password, oldCash] = line.split('|')
            if rg != rgClient:
                lines.append(line)
            else:
                lines.append("|".join([username, rg, password, str(cash)+"\n"]))

        file.seek(0, 0)
        file.truncate()
        file.writelines(lines)
        file.close()
        print('Depósito efetuado')

        return 0

    @staticmethod
    def transfer(rg, value, rgDest): # DEPOSIT MONEY FROM A CLIENT TO ANOTHER CLIENT
        if Banco.checkClient(rgDest) == 0: # CHECKS IF RG OF RECIPIENT EXIST
            if Banco.withdraw(rg, value) == 0: # WITHDRAW MONEY
                if Banco.deposit(rgDest, value) == 0: # DEPOSIT MONEY TO RECIPIENT
                    print("Transferência efetuada")
                    return 0
            else:
                return 1
        else:
            print("Correntista não encontrado")
            return 2
