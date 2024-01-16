import json
import requests
import telebot
import time
import csv
from datetime import datetime
import pytz
from telebot import types


class Roleta:

    def __init__(self):
        
        self.numeros = {
    'P': ['2', '4', '6', '8', '10', '11', '13', '15', '17', '20', '22', '24', '26', '28', '29', '31', '33', '35'],
    'NB': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18'],
    'NA': ['19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36'],
    'C1': ['1', '4', '7', '10', '13', '16', '19', '22', '25', '28', '31', '34'],
    'C2': ['2', '5', '8', '11', '14', '17', '20', '23', '26', '29', '32', '35'],
    'C3': ['3', '6', '9', '12', '15', '18', '21', '24', '27', '30', '33', '36'],
    'D1': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
    'D2': ['13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24'],
    'D3': ['25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36'],
    'V': ['1', '3', '5', '7', '9', '12', '14', '16', '18', '19', '21', '23', '25', '27', '30', '32', '34', '36']
}
       
        try:
            with open('config.json', 'r') as file:
                data = json.load(file)
                self.game = data['game']
                self.chat_id = data['chat']
                self.link = data['link']
                self.token = data['token']
                self.gales = data['gales']
                self.url_API = data['url_API']

        except FileNotFoundError:
            print("Erro: Arquivo de configuração não encontrado.")
            

        self.cont_gale = 0
        self.analisar = True
        self.cont_sinal = 0
        self.message_delete = False
        self.bot = telebot.TeleBot(token=self.token, parse_mode='MARKDOWN',disable_web_page_preview=True)
        self.sessao = False
        self.cont_gale_sessao = 0
        self.date = str(datetime.now(pytz.timezone('America/Sao_Paulo')).date().strftime("%d/%m/%Y"))

    def enviar_mensagem_sem_botao(self, message):
      
        try:
            self.message_ids = self.bot.send_message(chat_id=self.chat_id, text= message).message_id
            
        except Exception as e:
            print(f"O chat id {self.chat_id} esta incorreto ou ", e)
                
    
    def enviar_mensagem_com_botao(self, message):
        

        markup = types.InlineKeyboardMarkup()
        button2 = types.InlineKeyboardButton('Cadastre-se Aqui', url=self.link)
        markup.add(button2)
        try:
            self.message_ids = self.bot.send_message(chat_id=self.chat_id, text=message, reply_markup=markup).message_id
            
        except Exception as e:
            print(f"O chat id {self.chat_id} esta incorreto/ ",e)
            
    def abrir_mensagem(self,caminho,modo):

        with open(caminho, modo, encoding='utf-8') as f:
            return f
    
    def abrir_sessao(self):
        with open("sessoes.json", 'r') as file:
            return json.load(file)

    def salvar_sessao(self,data):
        with open("sessoes.json", 'w') as file:
            json.dump(data, file, indent=4)

    def delete_messages(self):
        
        try:
            self.bot.delete_message(self.chat_id, self.message_ids)
        except:
            pass

    def relatorio(self):

        dia = str(datetime.now(pytz.timezone('America/Sao_Paulo')).date().strftime("%d/%m/%Y"))
        
        data = self.abrir_sessao()
        win = data["win"] 
        loss = data["loss"] 
        assertividade = data['assertividade']

        with open('mensagens/mensagemPlacar.txt', 'r', encoding='utf-8') as arquivo:
            msgPlacar = arquivo.read().format(win=win,loss=loss,assertividade=assertividade)
            self.enviar_mensagem_sem_botao(msgPlacar)
        
        if self.date != dia:
            self.date = dia

            data["win"] = 0
            data["loss"] = 0
            data["assertividade"] = 0
            self.salvar_sessao(data)
                

            


    def alerta_sinal(self):
        with open('mensagens/mensagemAnalisando.txt', 'r', encoding='utf-8') as file:
            msgAnalisando = file.read()
     
        self.enviar_mensagem_sem_botao(msgAnalisando)
        
        self.message_delete = True

    
    def alert_gale(self):
        with open('mensagens/mensagemGale.txt', 'r', encoding='utf-8') as file:
            msgGale=file.read().format(count=self.cont_gale)
            
        self.enviar_mensagem_sem_botao(msgGale)
        self.message_delete = True

    def delete(self):
        if self.message_delete == True:
            self.delete_messages()
            self.message_delete = False


    def enviar_sinal(self, results):
        
        if '/' in self.res:
            duzia = self.res.find("D")
            coluna = self.res.find("C")

            if duzia:
                d1, d2 = self.res.split('/')

                with open('mensagens/mensagemDuzia.txt', 'r', encoding='utf-8') as file:
                    msgDuzia = file.read().format(
                        game=self.game, d1=d1[1], d2=d2[1], results=results[0])
                    
                self.analisar = False
                self.enviar_mensagem_com_botao(msgDuzia)
                
                return

            elif coluna:
                c1, c2 = self.res.split('/')

                with open('mensagens/mensagemColuna.txt', 'r', encoding='utf-8') as file:
                    msgColuna = file.read().format(
                        game=self.game, c1=c1[1], c2=c2[1], results=results[0])
                  
                self.analisar = False
                self.enviar_mensagem_com_botao(msgColuna)
                
                return


    def checar_resultado(self, result,results):

        
        
        data = self.abrir_sessao()

        with open('mensagens/mensagemWin.txt', 'r', encoding='utf-8') as file:
            msgWin=file.read().format(results=results)
            
        with open('mensagens/mensagemLoss.txt', 'r', encoding='utf-8') as file:
            msgLoss=file.read()
            

        if result == "WIN":

            print(f"WIN")
            data["win"] +=1
            self.enviar_mensagem_sem_botao(msgWin)
            
        elif result == "LOSS":
            self.cont_gale += 1

            if self.cont_gale > self.gales:
                print(f"LOSS")
                data["loss"] += 1
                self.enviar_mensagem_sem_botao(msgLoss)

            else:
                print(f"Vamos para o {self.cont_gale}ª Gale 🍀")
                
                #self.alert_gale()
                return
            
        assertividade = round(100 / (data['win'] + data['loss']) * (data['win']),2)
        data['assertividade'] = (f'{assertividade}%')
        self.salvar_sessao(data)
        self.cont_gale = 0
        self.analisar = True
        self.relatorio()

        return
    
    # CHECAR SE DEU WIN OU LOSS
    def checar_numero(self, results):

        if self.res in self.numeros.keys():

            self.checar_resultado('WIN',results[0]) if results[0] in self.numeros[self.res] or results[0] == '0' else self.checar_resultado('LOSS', results[0])

        elif '/' in self.res:
            res = self.res.split('/')

            self.checar_resultado('WIN',results[0]) if (results[0] in self.numeros[res[0]] or results[0] in self.numeros[res[1]]) or results[0] == '0' else self.checar_resultado('LOSS', results[0])


    
    def start(self):
        check = []
        
        while True:
            try:
                                
                results = []
                time.sleep(1)
                response = requests.get(self.url_API)
                json_data = json.loads(response.text)
                results = [str(result) for result in json_data["results"] ]

                if check != results:
                    check = results
                    self.delete()
                    self.estrategia(results)  

            except Exception as e:
                print('Erro ',e)
                continue
           

    def estrategia(self, results):

        print(results[0:10])

        if not self.analisar:
            self.checar_numero(results)
            return
        
        elif self.analisar:
            
            with open('estrategias.csv', newline='') as f:
                arquivo = csv.reader(f)

                ESTRATEGIAS = []

                for linha in arquivo:
                    res = str(linha[0])

                    saida = res.split('=')
                    padroes = saida[0].split('-')

                    estrategia = []
                    [estrategia.append(i) for i in padroes]
                    ESTRATEGIAS.append({'ESTRATEGIA': estrategia, 'SAIDA': saida[1]})

                for i in ESTRATEGIAS:
                    lista = results[0:len(i['ESTRATEGIA'])]
                    self.res = i['SAIDA']
                    padrao = i['ESTRATEGIA']
                    
                    
                    sinal = True

                    for i, valor in enumerate(lista):
                        if valor not in self.numeros[padrao[i]]:
                            sinal = False

                    if sinal:
                        print(f"\nRESULTADOS: {lista}")
                        print(
                            f"SINAL ENCONTRADO\nPADRÃO:{padrao}\nENTRADA:{self.res}\n")
                        
                        self.enviar_sinal(results)
                        return

                for i in ESTRATEGIAS:
                    lista = results[0:len(i['ESTRATEGIA'])-1]
                    res = i['SAIDA']
                    padrao = i['ESTRATEGIA'][1:len(i['ESTRATEGIA'])]


                    sinal = True

                    for i, valor in enumerate(lista):
                        if valor not in self.numeros[padrao[i]]:
                            sinal = False

                    if sinal:
                        print("ALERTA DE POSSÍVEL SINAL")
                        
                        self.alerta_sinal()
                        return
               

bot = Roleta()
bot.start()
