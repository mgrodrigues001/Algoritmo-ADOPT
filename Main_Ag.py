# Imports
import pandas as pd
import folium
import webbrowser
import json


'''_______ Criação dos Agentes _______'''
# Classe para criação dos agentes
class Agente:
    # Cria os agentes com suas respectivas variáveis
    def __init__(self, nome):
        self.nome = nome
        self.D = [0, 1, 2, 3]
        self.di = 0  # COR QUE O AGENTE ESCOLHEU
        self.cd = {0: 0, 1: 0, 2: 0, 3: 0}
        self.currentvw = {}  # CONTEXTO ATUAL DO AGENTE
        self.pai = None
        self.filhos = []
        self.msg_value_recebida = []
        self.flag_value = False
        self.msg_view_recebida = []
        self.flag_view = False

    '''_______ Calculo da função Sigma ________'''
    # Calcula o e(d)
    def sigma(self):
        ed_aux =[]
        ed = []
        minimo = []
        aux = []
        sigma_aux = self.currentvw.copy()
        sigma_aux[self] = self.di  # união do vw com (xi, di)
        for d in self.D:  # Para cada cor do domínio
            for x in sigma_aux.values():
                custo = cal_custo(x, d)  # chama a função para calculo do custo
                aux.append(custo)
            ed_aux.append([d, sum(aux)])  # soma os custos por cor
            aux = []
        # soma c(d) ao cálculo dos custos de cada cor
        for i in ed_aux:
            ed.append([i[0], i[1] + self.cd[i[0]]])
            minimo.append(i[1] + self.cd[i[0]])  # essa lista é usada para encontrar o index com o menor valor
        # escolhendo a cor com menor custo de e(d)
        cor_custo = ed[minimo.index(min(minimo))]  # add ao di a cor do menor indice da lista de minimo
        self.di = cor_custo[0]  # ALTERA O VALOR DO AGENTE
        return cor_custo

    """________ Recebimento e invio de mensagens _______VALUE"""
    # Recebe Mensagem de Value
    def checar_value(self):
        controle = self.currentvw.copy()  # Variável será utilizada para comparação com a currentvw
        for c in self.msg_value_recebida:
            self.currentvw[c[0]] = c[1]
        if controle == self.currentvw:  # Compara com a variavel de controle pra saber se houve alteração
            return
        else:
            self.cd = {0: 0, 1: 0, 2: 0, 3: 0}  # Se houve alteração, c(d) <- 0
            return

    """ _______ Recebimento e invio de mensagens VIEW _______"""
    def checar_view(self):
        flag = False
        for v in self.msg_view_recebida:
            vw = v[0]
            cost = v[1]
            if vw == self.currentvw:  # Se a vw do filho for compativel com a currentve
                if cost[1] > self.cd[cost[0]]:  # E se o valor do custo da cor d enviado pelo filho for mairo que o custo em c(d)
                    flag = True
                    self.cd[cost[0]] = cost[1]  # Add o valor de d maior ao c(d)
                    print(f'c(d): {self.cd}')
        if flag:
            self.hill_climb()
        self.msg_view_recebida = []
        return

    '''_______ Procedimento Hill_Climb _____'''
    def hill_climb(self):
        # calcula o Sigma
        edi = self.sigma()

        # Envia msg de Value para os Filhos
        if self.filhos != None:
            for ag_filho in self.filhos:
                ag_filho.msg_value_recebida.append([self, self.di])
                ag_filho.flag_value = True

        # Envia msg de View para o Pai
        if self.pai != None:
            self.msg_view_recebida.append([self.currentvw, edi])
            self.flag_view = True
        return


'''_______ Cálculo do Custo _______'''
# Função de custo
def cal_custo(cor1, cor2):
    if cor1 == cor2:
        return 1
    return 0


'''_______ Plotando o Resultado _______'''
def plot_resultado(df):
    br_estados = "br_states.json"
    geo_json_data = json.load(open(br_estados))

    output_file = "map2.html"
    mapa = folium.Map(location=[-8.732364, -41.868445], zoom_start=5.25)

    # Criar a camada Choroplet
    folium.Choropleth(
        geo_data=geo_json_data,
        name='Agentes',
        data=df,
        columns=['state', 'Cor'],
        key_on='feature.id',
        fill_color='Reds',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Cor Agentes'
    ).add_to(mapa)

    mapa.save(output_file)
    webbrowser.open(output_file, new=2)


'''_______Definição dos Agentes_______'''
# Criando os Agentes
MA = Agente('MA')  # Agente do estado do Maranhão
PI = Agente('PI')  # Agente do estado do Piauí
BA = Agente('BA')  # Agente do estado do Bahia
SE = Agente('SE')  # Agente do estado do Sergipe
AL = Agente('AL')  # Agente do estado do Alagoas
PE = Agente('PE')  # Agente do estado do Pernambuco
PB = Agente('PB')  # Agente do estado do Paraiba
RN = Agente('RN')  # Agente do estado do Rio Grande do Norte
CE = Agente('CE')  # Agente do estado do Ceará

PE.pai = None
PI.pai = PE
CE.pai = PI
RN.pai = CE
PB.pai = RN
MA.pai = PI
BA.pai = PI
SE.pai = BA
AL.pai = SE

# Configurando os filhos e pseudo-filhos dos agentes
PE.filhos = [PI, CE, PB, BA, AL]
PI.filhos = [CE, MA, BA]
CE.filhos = [RN, PB]
RN.filhos = [PB]
PB.filhos = None
MA.filhos = None
BA.filhos = [SE, AL]
SE.filhos = [AL]
AL.filhos = None

td_ag = [PE, PI, CE, RN, PB, MA, BA, SE, AL]


'''_________ Inicio do Algoritmo________'''
contador = 10
while contador > 0:
    for ag in td_ag:

        # Checando msg de VALUE recebida
        if ag.flag_value:
            ag.checar_value()

        # Checando msg de VIEW recebida
        if ag.flag_view:
            ag.checar_view()

        # Hill_Climb
        ag.hill_climb()

    contador -= 1


'''______ Apresentação Resultados ______'''
nome_ag = []
cor_ag = []

for i in td_ag:
    print(f'Agente: {i.nome} --> Cor: {i.di}')
    nome_ag.append(i.nome)
    cor_ag.append(i.di)

print('_'*30)

df = pd.DataFrame(list(zip(nome_ag, cor_ag)), columns=['state', 'Cor'])
plot_resultado(df)
