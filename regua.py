import random

#pega um valor n e cria n A'd e n B's, dps embaralha
def estado_inicial(n):
    estado = ['B'] * n + ['A'] * n + ['-']
    random.shuffle(estado)  
    return estado

#verifica se o estado é o estado meta
def estado_meta(estado, n):
    return estado == ['B'] * n + ['-'] + ['A'] * n

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

#como usar
n = 3
estado = estado_inicial(n)
print("Estado Inicial:", estado)

posicao_vazia = estado.index('-')
movimentos = movimentos_possiveis(estado, posicao_vazia, n)
print("Movimentos Possíveis:")
for s in movimentos:
    print(s)


