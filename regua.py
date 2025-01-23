import random
import time
import tracemalloc #talvez ?

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


#IDDFS

def busca_profundidade_l(nos, estado, profundidade_maxima, n, visitados=None):
    print("Visitando: ", estado)
    if visitados is None: #primeira vez que a função é chamada, cria o conjunto de visitados
        visitados = set()

    estado_str = ''.join(estado)
    if estado_str in visitados:
        return None, nos  # Para não repetir estados que ja foram visitados
    
    nos += 1 #adciona 1 no contador de nos
    visitados.add(estado_str) #adciona o estado atual no conjunto de visitados
    if estado_meta(estado, n):
        return estado, nos # Verirfica se é meta

    if profundidade_maxima == 0:
        return None, nos  # Profundidade atingida
    
    posicao_vazia = estado.index('-')
    movimentos = movimentos_possiveis(estado, posicao_vazia, n) #pega os movimentos possiveis

    for movimento in movimentos:
        #chama recursivamente a função para cada movimento possivel, garantindo que não vai passar do limite de profundidade
        resultado, nos = busca_profundidade_l(nos, movimento, profundidade_maxima - 1, n, visitados)
        if resultado is not None:
            return resultado, nos

    return None, nos

def busca_profundidade_iterativa(estado_inicial, n):
    #profundidade inicial do loop, para setar valores
    profundidade = 0
    while True:
        print(f"Tentando profundidade: {profundidade}")
        total_nos = 0
        resultado, total_nos = busca_profundidade_l(total_nos, estado_inicial, profundidade, n)
        if resultado is not None:
            print(f"Solução encontrada na profundidade: {profundidade}")
            return resultado, total_nos, profundidade
        profundidade += 1


#como usar
n = 10
estado = estado_inicial(n)
print("Estado Inicial:", estado)

inicio = time.time()
tracemalloc.start()
resposta, quantia_nos, passos = busca_profundidade_iterativa(estado, n)
fim = time.time()
memoria_usada = tracemalloc.get_traced_memory()
tracemalloc.stop()

print("Solução encontrada:", resposta)
print("Quantidade de nós visitados:", quantia_nos)
print("Número de passos:", passos)
print("Tempo de execução:", round(fim - inicio, 4), "segundos")
print(f"Memória usada: {memoria_usada[1] / 1024:.2f} KB")

