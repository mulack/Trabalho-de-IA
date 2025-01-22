import random

def estado_inicial(n):
    estado = ['B'] * n + ['A'] * n + ['-']
    random.shuffle(estado)  
    return estado

def estado_meta(estado, n):
    return estado == ['B'] * n + ['-'] + ['A'] * n

def movimentos_possiveis(estado, posicao_vazia, n):
    sucessores = []
    for i in range(len(estado)):
        if i != posicao_vazia and abs(i - posicao_vazia) <= n:
            novo_estado = estado[:]
            novo_estado[posicao_vazia], novo_estado[i] = novo_estado[i], '-'
            sucessores.append(novo_estado)
    return sucessores


n = 3
estado = estado_inicial(n)
print("Estado Inicial:", estado)

posicao_vazia = estado.index('-')
sucessores = movimentos_possiveis(estado, posicao_vazia, n)
print("Movimentos Possíveis:")
for s in sucessores:
    print(s)


