import random
import time
import tracemalloc
import heapq  # Usado para manter a lista de nós abertos ordenada

# Função para gerar um estado inicial aleatório
def estado_inicial(n):
    estado = ['B'] * n + ['A'] * n + ['-']  # Cria n 'A's, n 'B's e o espaço vazio '-'
    random.shuffle(estado)  # Embaralha o estado
    return estado


# Função para verificar se o estado é o estado meta
def estado_meta(estado, n):
    estado_aux = [x for x in estado if x != '-']  # Ignora o '-'
    return estado_aux == ['B'] * n + ['A'] * n  # Verifica se o estado é o meta


# Função que retorna os movimentos possíveis
def movimentos_possiveis(estado, posicao_vazia, n):
    movimentos = []
    for i in range(len(estado)):  # Percorre o vetor
        # Se a posição i não for a do "-", e a distância entre i e a posição vazia não for maior que n, o movimento é possível
        if i != posicao_vazia and abs(i - posicao_vazia) <= n:
            novo_estado = estado[:]
            novo_estado[posicao_vazia], novo_estado[i] = novo_estado[i], '-'  # Troca as posições
            movimentos.append(novo_estado)  # Adiciona o novo estado à lista
    return movimentos


# Heurística 1 - Mede quantas pecas estão incorretos em relação ao objetivo, penalidade +3 para distâncias > 2, punindo movimentos longos
def heuristic_1(state, goal):
    count = 0
    for i in range(len(state)):
        if state[i] != goal[i] and state[i] != '-':
            # Distância da peça em relação ao seu objetivo
            target_index = goal.index(state[i])
            distance = abs(i - target_index)
            
            # o "-" se mover no maximo 2 casas
            if distance > 2:
                count += 3  # Penaliza com +3
            else:
                count += distance  # Movimento normal (1 ou 2 casas)
    return count


# Heurística 2 - Distância Manhattan dos elementos incorretos
def heuristic_2(state, goal):
    total_dist = 0
    for i, element in enumerate(state):
        if element != goal[i] and element != '-':
            target_index = goal.index(element)
            total_dist += abs(i - target_index)
    return total_dist


# A* recebendo qualquer heuristic
def A_star(estado_inicial, n, heuristic):
    goal = ['B'] * n + ['-'] + ['A'] * n  # GOAL
    start = estado_inicial # INICIAL
    open_list = [] # Lista com prioridade
    heapq.heappush(open_list, (0, start, 0))  # (custo, estado, custo heuristica)
    dicionario_caminho = {}
    g_costs = {tuple(start): 0}  # Dicionario de custos g (Tupla como chave)
    f_costs = {tuple(start): heuristic(start, goal)}  # Dicionario de custos f (g + h)

    while open_list:
        f, current_state, g = heapq.heappop(open_list)  # Pega o estado atual
        if estado_meta(current_state, n):
            path = []
            while tuple(current_state) in dicionario_caminho:  # Usando tupla como chave no caminho
                path.append(current_state)
                current_state = dicionario_caminho[tuple(current_state)]  # Usando a tupla como chave
            path.append(estado_inicial)
            path.reverse()
            return path  # Retorna o caminho para o objetivo

        posicao_vazia = current_state.index('-')  # Pega a posição do espaço vazio
        movimentos = movimentos_possiveis(current_state, posicao_vazia, n)  # Pega TODOS os movimentos possiveis

        for movimento in movimentos: #* Realiza os movimentos 
            g_new = g_costs[tuple(current_state)] + 1  # Custo g (movimento de custo 1)
            h_new = heuristic(movimento, goal)  # Pega os heuristico
            f_new = g_new + h_new  # Custo f

            if tuple(movimento) not in g_costs or g_new < g_costs[tuple(movimento)]:
                dicionario_caminho[tuple(movimento)] = current_state
                g_costs[tuple(movimento)] = g_new
                f_costs[tuple(movimento)] = f_new
                heapq.heappush(open_list, (f_new, movimento, g_new))  # Adiciona o novo estado a LISTA

    return None  # Caso não encontre solução


# Como usar
n = 30  # Número de A's e B's
estado = estado_inicial(n)

# Exemplo de estado de teste
teste = ['B', 'A', 'B', 'A', 'A', '-', 'A', 'B', 'B']  # Estado de teste
teste = estado
print("Estado Inicial:", estado)

###############

# Início da medição de tempo e memória
inicio = time.time()
tracemalloc.start()

# Algoritmo A* com a Heurística 1 (quantidade de peças fora de posição)
resposta_heuristica_1 = A_star(teste, n, heuristic_1)
print("\nSolução com Heurística 1 (Quantidade de peças fora de posição):")
print(len(resposta_heuristica_1))

# Fim da medição de tempo e memória
fim = time.time()
memoria_usada = tracemalloc.get_traced_memory()
tracemalloc.stop()

# Exibe os resultados
print("Tempo de execução:", round(fim - inicio, 4), "segundos")
print(f"Memória usada: {memoria_usada[1] / 1024:.2f} KB")

###############

# Início da medição de tempo e memória
inicio = time.time()
tracemalloc.start()

# Algoritmo A* com a Heurística 2 (Distância Manhattan)
resposta_heuristica_2 = A_star(teste, n, heuristic_2)
print("\nSolução com Heurística 2 (Distância Manhattan):")
print(len(resposta_heuristica_2))

# Fim da medição de tempo e memória
fim = time.time()
memoria_usada = tracemalloc.get_traced_memory()
tracemalloc.stop()

# Exibe os resultados
print("Tempo de execução:", round(fim - inicio, 4), "segundos")
print(f"Memória usada: {memoria_usada[1] / 1024:.2f} KB")

###############