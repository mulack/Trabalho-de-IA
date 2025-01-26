import random
import time
from collections import deque
import tracemalloc 

#pega um valor n e cria n A'd e n B's, dps embaralha
def estado_inicial(n):
    estado = ['B'] * n + ['A'] * n + ['-']
    random.shuffle(estado)  
    return estado

#verifica se o estado é o estado meta
def estado_meta(estado, n):
    estado_aux = [x for x in estado if x != '-'] #para verificar se o estado é meta sem o "-" interferir
    return estado_aux == ['B'] * n + ['A'] * n

#retorna os movimentos possiveis
def movimentos_possiveis(estado, posicao_vazia, n):
    movimentos = []
    for i in range(len(estado)): #percorre o vetor
        # se o i não for a posicão do "-" e a distancia entre o i e a vazia (valor abs(positivo)) 
        # não for maior que n, então o movimento de troca é possivel
        if i != posicao_vazia and abs(i - posicao_vazia) <= n: 
            novo_estado = estado[:]
            novo_estado[posicao_vazia], novo_estado[i] = novo_estado[i], '-' #faz a troca
            movimentos.append(novo_estado) #adciona na lista dos movimentos
    return movimentos


#BUSCA A ESTRELA
# Heurística 1 - Mede quantas pecas estão incorretos em relação ao objetivo, penalidade +3 para distâncias > 2, punindo movimentos longos
def heuristic_1(state, final):
    count = 0
    for i in range(len(state)):
        if state[i] != final[i] and state[i] != '-':
            # Distância da peça em relação ao seu objetivo
            target_index = final.index(state[i])
            distance = abs(i - target_index)
            
            # o "-" se mover no maximo 2 casas
            if distance > 2:
                count += 3  # Penaliza com +3
            else:
                count += distance  # Movimento normal (1 ou 2 casas)
    return count

# Heurística 2 - Distância Manhattan dos elementos incorretos
def heuristic_2(state, final):
    total_dist = 0
    for i, element in enumerate(state):
        if element != final[i] and element != '-':
            target_index = final.index(element)
            total_dist += abs(i - target_index)
    return total_dist

#BUSCA EM LARGURA
def busca_largura(estado_inicial, n):
    if estado_meta(estado_inicial, n):
        return estado_inicial, 0, [estado_inicial]

    fila = deque([(estado_inicial, 0, [estado_inicial])]) 
    visitados = set()
    visitados.add(''.join(estado_inicial))  

    while fila:
        estado_atual, profundidade, caminho = fila.popleft()

        posicao_vazia = estado_atual.index('-')  
        movimentos = movimentos_possiveis(estado_atual, posicao_vazia, n)  # Gera movimentos possíveis

        for movimento in movimentos:
            movimento_str = ''.join(movimento)
            if movimento_str not in visitados:
                # Se encontrar o estado meta, retorna o resultado e a profundidade
                if estado_meta(movimento, n):
                    return movimento, profundidade + 1, caminho + [movimento]
                fila.append((movimento, profundidade + 1, caminho + [movimento]))  # Adiciona na fila com profundidade aumentada
                visitados.add(movimento_str)  

    return None, -1, []  

#BUSCA EM PROFUNDIDADE ITERATIVA
def busca_profundidade(nos, estado, profundidade_maxima, n, nos_fronteira, nao_folha, visitados=None):
    #print("Visitando: ", estado)
    if visitados is None: #primeira vez que a função é chamada, cria o conjunto de visitados
        visitados = set()

    estado_str = ''.join(estado)
    if estado_str in visitados:
        return None, len(visitados), nos_fronteira, nao_folha  # Para não repetir estados que ja foram visitados

    nos += 1 #adciona 1 no contador de nos
    visitados.add(estado_str) #adciona o estado atual no conjunto de visitados

    if estado_meta(estado, n):
        return estado, len(visitados), nos_fronteira, nao_folha # Verirfica se é meta

    if profundidade_maxima == 0: 
        return None, len(visitados), nos_fronteira, nao_folha  # Profundidade atingida
    
    posicao_vazia = estado.index('-')
    movimentos = movimentos_possiveis(estado, posicao_vazia, n) #pega os movimentos possiveis
    if movimentos and profundidade_maxima > 0:
        nao_folha += 1 #adciona 1 no contador de nao_folha

    nos_fronteira += len(movimentos) if profundidade_maxima > 0 else 0 #adciona 1 no contador de nos_fronteira

    for movimento in movimentos:
        #chama recursivamente a função para cada movimento possivel, garantindo que não vai passar do limite de profundidade
        resultado, nos, nos_fronteira, nao_folha = busca_profundidade(nos, movimento, profundidade_maxima - 1, n, nos_fronteira, nao_folha, visitados)
        if resultado is not None:
            return resultado, len(visitados), nos_fronteira, nao_folha

    return None, len(visitados), nos_fronteira, nao_folha

def busca_profundidade_iterativa(estado_inicial, n):
    #profundidade inicial do loop, para setar valores
    profundidade = 0
    while True:
        #print(f"Tentando profundidade: {profundidade}")
        total_nos = 0
        nos_fronteira = 1
        nao_folha = 0
        resultado, total_nos, nos_fronteira, nao_folha = busca_profundidade(total_nos, estado_inicial, profundidade, n, nos_fronteira, nao_folha)
        if resultado is not None:
            #print(f"Solução encontrada na profundidade: {profundidade}")
            fator_ramificacao = (total_nos - 1) / nao_folha if nao_folha > 0 else 0 #calcula o fator de ramificação medio 
            return resultado, total_nos, profundidade, fator_ramificacao, nos_fronteira
        profundidade += 1

# A* 
def A_star(estado_inicial, n, heuristic):
    final = ['B'] * n + ['-'] + ['A'] * n  # Estado objetivo
    start = estado_inicial  # Estado inicial
    open_list = [(0, start, 0)]  # Lista de nós abertos (f, estado, g)
    dicionario_caminho = {}
    g_costs = {tuple(start): 0}  # Custos g
    f_costs = {tuple(start): heuristic(start, final)}  # Custos f

    # Contadores
    nos_expandidos = 0
    total_sucessores = 0

    while open_list:
        open_list.sort(key=lambda x: x[0])  # Ordena pelo custo f
        f, current_state, g = open_list.pop(0)  # Remove o nó com menor custo f
        nos_expandidos += 1  # Incrementa o contador de nós expandidos

        if estado_meta(current_state, n):
            path = []
            while tuple(current_state) in dicionario_caminho:
                path.append(current_state)
                current_state = dicionario_caminho[tuple(current_state)]
            path.append(estado_inicial)
            path.reverse()
            fator_ramificacao_medio = total_sucessores / nos_expandidos if nos_expandidos > 0 else 0
            return path, nos_expandidos, fator_ramificacao_medio  # Retorna o caminho, nós expandidos e fator de ramificação médio

        posicao_vazia = current_state.index('-')  # Posição do espaço vazio
        movimentos = movimentos_possiveis(current_state, posicao_vazia, n)  # Sucessores
        total_sucessores += len(movimentos)  # Conta os sucessores gerados

        for movimento in movimentos:
            g_new = g_costs[tuple(current_state)] + 1
            h_new = heuristic(movimento, final)
            f_new = g_new + h_new

            if (tuple(movimento) not in g_costs) or (g_new < g_costs[tuple(movimento)]):
                dicionario_caminho[tuple(movimento)] = current_state
                g_costs[tuple(movimento)] = g_new
                f_costs[tuple(movimento)] = f_new
                open_list.append((f_new, movimento, g_new))

    return None, nos_expandidos, 0  # Caso não encontre solução

def A_star_bidirecional(estado_inicial, n, heuristic):
    estado_final = ['B'] * n + ['-'] + ['A'] * n  # Estado objetivo
    start = estado_inicial  # Estado inicial

    # Inicializa listas abertas e fechadas para frente e trás
    open_frente = [(0, start, 0)]
    open_tras = [(0, estado_final, 0)]

    dicionario_caminho_frente = {}
    dicionario_caminho_tras = {}

    g_costs_frente = {tuple(start): 0}
    f_costs_frente = {tuple(start): heuristic(start, estado_final)}
    
    g_costs_tras = {tuple(estado_final): 0}
    f_costs_tras = {tuple(estado_final): heuristic(estado_final, start)}

    # Variáveis para análise de desempenho
    nos_expandidos = 0
    total_filhos_gerados = 0
    total_nos_internos = 0

    while open_frente and open_tras:
        # Próximo estado frente
        open_frente.sort(key=lambda x: x[0])
        f, estado_atual_frente, g = open_frente.pop(0)

        # Próximo estado trás
        open_tras.sort(key=lambda x: x[0])
        f, estado_atual_tras, g = open_tras.pop(0)

        # Incrementa nós expandidos
        nos_expandidos += 2  # Um nó de cada direção será expandido

        # Verifica se os caminhos se encontram
        movimentos_frente = movimentos_possiveis(estado_atual_frente, estado_atual_frente.index('-'), n)
        movimentos_tras = movimentos_possiveis(estado_atual_tras, estado_atual_tras.index('-'), n)

        total_filhos_gerados += len(movimentos_frente) + len(movimentos_tras)
        total_nos_internos += 2  # Estado atual frente e trás são nós internos

        # Verifica se o último caminho já foi visitado anteriormente
        visitado_frente = any(tuple(estado) in g_costs_tras for estado in movimentos_frente)
        visitado_tras = any(tuple(estado) in g_costs_frente for estado in movimentos_tras)

        if visitado_frente or visitado_tras:
            caminho = reconstruir_caminho(dicionario_caminho_frente, dicionario_caminho_tras, estado_atual_frente, estado_atual_tras)
            fator_ramificacao_media = total_filhos_gerados / total_nos_internos if total_nos_internos > 0 else 0
            return caminho, nos_expandidos, fator_ramificacao_media

        # Expande a busca para frente
        posicao_vazia_f = estado_atual_frente.index('-')
        for movimento in movimentos_possiveis(estado_atual_frente, posicao_vazia_f, n):
            g_new_frente = g_costs_frente[tuple(estado_atual_frente)] + 1
            h_new_frente = heuristic(movimento, estado_final)
            f_new_frente = g_new_frente + h_new_frente

            if (tuple(movimento) not in g_costs_frente) or (g_new_frente < g_costs_frente[tuple(movimento)]):
                dicionario_caminho_frente[tuple(movimento)] = estado_atual_frente
                g_costs_frente[tuple(movimento)] = g_new_frente
                f_costs_frente[tuple(movimento)] = f_new_frente
                open_frente.append((f_new_frente, movimento, g_new_frente))

        # Expande a busca para trás
        posicao_vazia_t = estado_atual_tras.index('-')
        for movimento in movimentos_possiveis(estado_atual_tras, posicao_vazia_t, n):
            g_new_tras = g_costs_tras[tuple(estado_atual_tras)] + 1
            h_new_tras = heuristic(movimento, start)
            f_new_tras = g_new_tras + h_new_tras

            if (tuple(movimento) not in g_costs_tras) or (g_new_tras < g_costs_tras[tuple(movimento)]):
                dicionario_caminho_tras[tuple(movimento)] = estado_atual_tras
                g_costs_tras[tuple(movimento)] = g_new_tras
                f_costs_tras[tuple(movimento)] = f_new_tras
                open_tras.append((f_new_tras, movimento, g_new_tras))

    return None, nos_expandidos, fator_ramificacao_media


def reconstruir_caminho(caminho_frente, caminho_tras, encontro_frente, encontro_tras):
    # Caminho frente
    Lista_frente = []
    while tuple(encontro_frente) in caminho_frente:
        Lista_frente.append(encontro_frente)
        encontro_frente = caminho_frente[tuple(encontro_frente)]
    Lista_frente.reverse()

    # Caminho tras
    Lista_tras = []
    while tuple(encontro_tras) in caminho_tras:
        Lista_tras.append(encontro_tras)
        encontro_tras = caminho_tras[tuple(encontro_tras)]

    # Combina os dois caminhos
    return Lista_frente + Lista_tras

# como usar
n = int(input("Digite a quantidade de blocos azuis e brancos (N): "))
estado = estado_inicial(n)
print("Estado Inicial:", estado)

"""
#busca em largura
inicio1 = time.time()
tracemalloc.start()
resultado, profundidade, passos = busca_largura(estado, n)
fim1 = time.time()
memoria_usada1 = tracemalloc.get_traced_memory()
tracemalloc.stop()
print("\n")
print("------------------BUSCA EM LARGURA--------------------------------")
print("Solução encontrada:", resultado)
print("Profundidade:", profundidade)
print("Número de passos:", passos)
print("Tempo de execução:", round(fim1 - inicio1, 4), "segundos")
print(f"Memória usada: {memoria_usada1[1] / 1024:.2f} KB")

"""
# busca um profundidade iterativa

inicio = time.time()
tracemalloc.start()
resposta, quantia_nos, passos, fator_ramificacao, fronteira = busca_profundidade_iterativa(estado, n)
fim = time.time()
memoria_usada = tracemalloc.get_traced_memory()
tracemalloc.stop()


print("------------------BUSCA EM PROFUNDIDADE ITERATIVA--------------------------------")
print("Solução encontrada:", resposta)
print("Quantidade de nós visitados:", quantia_nos)
print("Quantidade de nós na fronteira:", fronteira)
print("Número de passos:", passos)
print("Fator de ramificação:", fator_ramificacao)
print("Tempo de execução:", round(fim - inicio, 4), "segundos")
print(f"Memória usada: {memoria_usada[1] / 1024:.2f} KB")

#busca A*
# Euristica 1
inicio2 = time.time()
tracemalloc.start()
resultado_heuristic1, nos_expandidos1, fator_ramificacao1 = A_star(estado, n, heuristic_1)
fim2 = time.time()
memoria_usada2 = tracemalloc.get_traced_memory()
tracemalloc.stop()
# Euristica 2
inicio3 = time.time()
tracemalloc.start()
resultado_heuristic2, nos_expandidos2, fator_ramificacao2 = A_star(estado, n, heuristic_2)
fim3 = time.time()
memoria_usada3 = tracemalloc.get_traced_memory()
tracemalloc.stop()
print("\n")
print("------------------BUSCA A*--------------------------------")
print("Solução encontrada Heuristic 1:", resultado_heuristic1[-1])
print("Quantidade de passos de sua solução:", len(resultado_heuristic1))
print("Quantidade de Nos expandidos: ", nos_expandidos1)
print("Fator de ramificação: ", fator_ramificacao1)
print("Solução encontrada Heuristic 1:", resultado_heuristic1)
print("Tempo de execução Heuristic 1:", round(fim2 - inicio2, 4), "segundos")
print(f"Memória usada Heuristic 1: {memoria_usada2[1] / 1024:.2f} KB")

print("\n")
print("Solução encontrada Heuristic 2:", resultado_heuristic2[-1])
print("Quantidade de passos de sua solução:", len(resultado_heuristic2))
print("Quantidade de Nos expandidos: ", nos_expandidos2)
print("Fator de ramificação: ", fator_ramificacao2)
print("Solução encontrada Heuristic 2:", resultado_heuristic2)
print("Tempo de execução Heuristic 2:", round(fim3 - inicio3, 4), "segundos")
print(f"Memória usada Heuristic 2: {memoria_usada3[1] / 1024:.2f} KB")

#busca A* Bidirecional
# Euristica 2 Distancia Manhattan
inicio4 = time.time()
tracemalloc.start()
resultado_A_start_Bi, nos_expandidosBi, fator_ramificacaoBi = A_star_bidirecional(estado, n, heuristic_2)
fim4 = time.time()
memoria_usada4 = tracemalloc.get_traced_memory()
tracemalloc.stop()
print("\n")
print("------------------BUSCA A* Bidirecional--------------------")
print("Solução encontrada Heuristic 2::", resultado_A_start_Bi[-1])
print("Quantidade de passos de sua solução:", len(resultado_A_start_Bi))
print("Quantidade de Nos expandidos: ", nos_expandidosBi)
print("Fator de ramificação: ", fator_ramificacaoBi)
print("Solução encontrada Heuristic 2:", resultado_A_start_Bi)
print("Tempo de execução Heuristic 2:", round(fim4 - inicio4, 4), "segundos")
print(f"Memória usada Heuristic 2: {memoria_usada4[1] / 1024:.2f} KB")


