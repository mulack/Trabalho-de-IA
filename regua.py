import random
import time
import tracemalloc

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

    while open_frente and open_tras:
        # Proximo estado frente
        open_frente.sort(key=lambda x: x[0])
        f, estado_atual_frente, g = open_frente.pop(0)
        # Proximo estado tras
        open_tras.sort(key=lambda x: x[0])
        f, estado_atual_tras, g = open_tras.pop(0)


        #! Verifica se os caminhos se ENCONTRAM
        movimentos_frente = movimentos_possiveis(estado_atual_frente, estado_atual_frente.index('-'), n)
        movimentos_tras = movimentos_possiveis(estado_atual_tras, estado_atual_tras.index('-'), n)
        # Verifica se o ultimo caminho já foi visitado anteriormente
        visitado_frente = any(tuple(estado) in g_costs_tras for estado in movimentos_frente)
        visitado_tras = any(tuple(estado) in g_costs_frente for estado in movimentos_tras)
        # Se bater algum caminho 
        if visitado_frente or visitado_tras:
            return reconstruir_caminho(dicionario_caminho_frente, dicionario_caminho_tras, estado_atual_frente, estado_atual_tras)


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

    return None  # Se não houver solução

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



""" A*
Exemplo de como cada Heuristica funciona
H1
[(8, ['A', 'B', 'A', 'B', '-'], 1), 
(11, ['A', '-', 'A', 'B', 'B'], 1)]
[(7, ['A', 'B', 'B', 'A', '-'], 2),
h2
[(8, ['A', 'B', 'A', 'B', '-'], 1), 
(12, ['A', '-', 'A', 'B', 'B'], 1)]
[(7, ['A', 'B', 'B', 'A', '-'], 2), 
"""

""" A* BiDirecional: Não faz sentido usar-lo
para esse problema, pois ele se perde, são muitas opções
e se ele se perder no de baixo para cima é dificil de se recuperar.
!Quando o n é pequeno ele é bom, quando n é grande ele é horrivel
"""


# Como usar
n = 3  # Número de A's e B's
teste = estado_inicial(n)
print("Estado Inicial:", teste)



inicio = time.time();tracemalloc.start()# Início da medição de tempo e memória

resposta_heuristica_1 = A_star(teste, n, heuristic_1)#* Algoritmo A* com a Heurística 1

fim = time.time();memoria_usada = tracemalloc.get_traced_memory();tracemalloc.stop();# Fim da medição de tempo e memória
# Exibe os resultados
print("\nSolução A* com Heurística 1 (Quantidade de peças fora de posição):");print((resposta_heuristica_1))
print("Tempo de execução:", round(fim - inicio, 4), "segundos");print(f"Memória usada: {memoria_usada[1] / 1024:.2f} KB")

#!##############

inicio = time.time();tracemalloc.start()# Início da medição de tempo e memória

resposta_heuristica_2 = A_star(teste, n, heuristic_2)#* Algoritmo A* com a Heurística 2 (Distância Manhattan)

fim = time.time();memoria_usada = tracemalloc.get_traced_memory();tracemalloc.stop();# Fim da medição de tempo e memória
# Exibe os resultados
print("\nSolução A* com Heurística 2 (Distância Manhattan):");print((resposta_heuristica_2))
print("Tempo de execução:", round(fim - inicio, 4), "segundos");print(f"Memória usada: {memoria_usada[1] / 1024:.2f} KB")

#!############## Com Manhattan

inicio = time.time();tracemalloc.start()# Início da medição de tempo e memória

resposta_heuristica_3 = A_star_bidirecional(teste, n, heuristic_2)#* Algoritmo A* Bidirecional com a Heurística 2 (Distância Manhattan)

fim = time.time();memoria_usada = tracemalloc.get_traced_memory();tracemalloc.stop();# Fim da medição de tempo e memória
# Exibe os resultados
print("\nSolução A* BIDIRECIONAL com Heurística 2 (Distância Manhattan):");print((resposta_heuristica_3))
print("Tempo de execução:", round(fim - inicio, 4), "segundos");print(f"Memória usada: {memoria_usada[1] / 1024:.2f} KB")

