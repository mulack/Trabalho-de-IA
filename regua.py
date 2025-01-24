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

# A* recebendo qualquer heuristic
def A_star(estado_inicial, n, heuristic):
    final = ['B'] * n + ['-'] + ['A'] * n  # GOAL
    start = estado_inicial  # INICIAL
    open_list = [(0, start, 0)]  # Lista com (custo, estado, custo heuristica)
    dicionario_caminho = {}
    g_costs = {tuple(start): 0}  # Dicionario de custos g (Tupla como chave)
    f_costs = {tuple(start): heuristic(start, final)}  # Dicionario de custos f (g + h)

    while open_list:
        open_list.sort(key=lambda x: x[0])  # Ordena pelo custo f (x[0])
        f, current_state, g = open_list.pop(0)  # Pega o estado com menor custo f
        if estado_meta(current_state, n):
            path = []
            while tuple(current_state) in dicionario_caminho:  # Usando tupla como chave no caminho
                path.append(current_state)
                current_state = dicionario_caminho[tuple(current_state)]  # Usando a tupla como chave
            path.append(estado_inicial)
            path.reverse()
            return path  # Retorna o caminho para o objetivo

        posicao_vazia = current_state.index('-')  # Pega a posição do espaço vazio
        movimentos = movimentos_possiveis(current_state, posicao_vazia, n)  #* Pega TODOS os movimentos possiveis

        for movimento in movimentos:  # Realiza os movimentos 
            g_new = g_costs[tuple(current_state)] + 1  # Custo g (movimento de custo 1)
            h_new = heuristic(movimento, final)  # Pega o heurístico
            f_new = g_new + h_new  # Custo f

            if (tuple(movimento) not in g_costs) or (g_new < g_costs[tuple(movimento)]):
                dicionario_caminho[tuple(movimento)] = current_state
                g_costs[tuple(movimento)] = g_new
                f_costs[tuple(movimento)] = f_new
                open_list.append((f_new, movimento, g_new))  # adiciona o novo estado

    return None  # Caso não encontre solução

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
        return None, nos, nos_fronteira, nao_folha  # Para não repetir estados que ja foram visitados

    nos += 1 #adciona 1 no contador de nos
    visitados.add(estado_str) #adciona o estado atual no conjunto de visitados

    if estado_meta(estado, n):
        return estado, nos, nos_fronteira, nao_folha # Verirfica se é meta

    if profundidade_maxima == 0: 
        return None, nos, nos_fronteira, nao_folha  # Profundidade atingida
    
    posicao_vazia = estado.index('-')
    movimentos = movimentos_possiveis(estado, posicao_vazia, n) #pega os movimentos possiveis
    if movimentos and profundidade_maxima > 0:
        nao_folha += 1 #adciona 1 no contador de nao_folha

    nos_fronteira += len(movimentos) if profundidade_maxima > 0 else 0 #adciona 1 no contador de nos_fronteira

    for movimento in movimentos:
        #chama recursivamente a função para cada movimento possivel, garantindo que não vai passar do limite de profundidade
        resultado, nos, nos_fronteira, nao_folha = busca_profundidade(nos, movimento, profundidade_maxima - 1, n, nos_fronteira, nao_folha, visitados)
        if resultado is not None:
            return resultado, nos, nos_fronteira, nao_folha

    return None, nos, nos_fronteira, nao_folha

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


#como usar
n = int(input("Digite a quantidade de blocos azuis e brancos (N): "))
estado = estado_inicial(n)
print("Estado Inicial:", estado)

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



#busca em largura
inicio1 = time.time()
tracemalloc.start()
resultado, profundidade, passos = busca_largura(estado, n)
fim1 = time.time()
memoria_usada1 = tracemalloc.get_traced_memory()
tracemalloc.stop()
print("------------------BUSCA EM LARGURA--------------------------------")
print("Solução encontrada:", resultado)
print("Profundidade:", profundidade)
print("Número de passos:", passos)
print("Tempo de execução:", round(fim1 - inicio1, 4), "segundos")
print(f"Memória usada: {memoria_usada1[1] / 1024:.2f} KB")

#busca A*
inicio2 = time.time()
tracemalloc.start()
resultado_heuristic1 = A_star(estado, n, heuristic_1)
fim2 = time.time()
memoria_usada2 = tracemalloc.get_traced_memory()
tracemalloc.stop()

# Início da medição de tempo e memória
inicio3 = time.time()
tracemalloc.start()
resultado_heuristica_2 = A_star(estado, n, heuristic_2)#* Algoritmo A* com a Heurística 2 (Distância Manhattan)
fim3 = time.time()
memoria_usada3 = tracemalloc.get_traced_memory()
tracemalloc.stop();# Fim da medição de tempo e memória

print("------------------BUSCA A*--------------------------------")
print("Solução encontrada Heuristic 1:", resultado_heuristic1)
print("Tempo de execução Heuristic 1:", round(fim2 - inicio2, 4), "segundos")
print(f"Memória usada Heuristic 1: {memoria_usada2[1] / 1024:.2f} KB")

print("\nSolução encontrada Heuristic 2:", resultado_heuristica_2)
print("Tempo de execução Heuristic 2:", round(fim3 - inicio3, 4), "segundos")
print(f"Memória usada Heuristic 2: {memoria_usada3[1] / 1024:.2f} KB")
