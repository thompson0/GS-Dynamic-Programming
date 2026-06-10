# GS Dynamic Programming — Space Route Planner

## 📋 Descrição do Projeto

**Space Route Planner** é uma aplicação em Python para planejamento otimizado de rotas espaciais entre corpos celestes do sistema solar. O sistema utiliza algoritmos de grafos com critérios múltiplos para encontrar a melhor trajetória considerando distância, tempo de viagem, custo de combustível e características gravitacionais dos destinos.

O projeto demonstra a aplicação prática de estruturas de dados e algoritmos fundamentais estudados em **Estruturas de Dados**, integrando dados reais obtidos via API pública com interface interativa em terminal.

---

## 🎯 Objetivo da Solução

Desenvolver um sistema de otimização de rotas espaciais que:

- **Integra dados reais** do sistema solar via API Solar System OpenData
- **Aplica critérios multicritério** (distância, tempo, combustível, gravidade) ponderados por perfil de missão
- **Implementa estruturas de dados fundamentais** (pilhas, filas, listas ligadas, grafos)
- **Oferece múltiplas operações** de busca, ordenação e análise de rotas
- **Visualiza rotas** em mapas orbitais interativos
- **Demonstra como a solução auxilia na tomada de decisão** para planejamento de missões espaciais

---

## 🌍 Tema Escolhido

**Planejamento de Missões Espaciais — Otimização de Rotas Interplanetárias**

O projeto aborda um problema real da economia espacial: como determinar a melhor rota entre dois corpos celestes considerando múltiplas restrições técnicas e operacionais. Empresas como SpaceX, Blue Origin e agências como NASA enfrentam diariamente esse problema ao planejar lançamentos, sondas e missões interplanetárias.

---

## 📊 Fonte dos Dados Utilizados

- **API Principal:** [Solar System OpenData](https://api.le-systeme-solaire.net/)
  - Dados em tempo real dos 8 planetas do sistema solar
  - Campos: nome, tipo de corpo, distância ao sol, gravidade
  - Atualizado regularmente com dados astronômicos precisos

- **Dados Coletados:**
  - Mercúrio, Vênus, Terra, Marte, Júpiter, Saturno, Urano, Netuno
  - Distância em milhões de km (Mkm) do semieixo maior orbital
  - Gravidade superficial em m/s²

**Método de Carregamento:**
- Lazy loading: dados puxados somente quando necessário
- Requisição HTTP com tratamento de timeout
- Sincronização com API obrigatória (sem fallback local)

---

## 🔧 Estruturas de Dados Implementadas

### 1. **Lista Ligada Simples** (`LinkedList`)
   - Nós encadeados com ponteiro `next`
   - Iteração eficiente por `__iter__`
   - Uso: armazenar sequência de corpos na rota calculada
   - Arquivo: `data_structures.py`

### 2. **Pilha (Stack - LIFO)**
   - Operações: `push()`, `pop()`, `peek()`, `empty()`
   - Método de armazenamento: lista interna
   - Uso: histórico de rotas calculadas com operação de "desfazer"
   - Arquivo: `data_structures.py`

### 3. **Fila (Queue - FIFO)**
   - Operações: `enqueue()`, `dequeue()`, `empty()`
   - Método de armazenamento: lista interna
   - Uso: enfileiramento de missões para processamento em lote
   - Arquivo: `data_structures.py`

### 4. **Grafo Ponderado Direcionado**
   - Representação: dicionário de adjacência `dict[Body, list[GraphEdge]]`
   - Peso das arestas: score multicritério
   - Vértices: corpos celestes
   - Arestas: rotas viáveis entre corpos
   - Uso: busca de melhor rota entre dois corpos
   - Arquivo: `graph.py`

### 5. **Modelos de Dados** (Dataclasses)
   - `Body`: corpo celeste (nome, tipo, distância, gravidade)
   - `Mission`: missão enfileirada (origem, destino, prioridade, perfil)
   - `Route`: rota calculada (caminho, métricas, score)
   - `MissionProfile`: definição de pesos para critério multicritério
   - `GraphEdge`: aresta do grafo (distância, tempo, combustível, gravidade)
   - Arquivo: `models.py`

---

## 🔍 Algoritmos Utilizados

### **1. Busca Linear** — `linear_search()`
   - Complexidade: O(n)
   - Busca por nome de corpo celeste
   - Comparação case-insensitive
   - Arquivo: `algorithms.py`

### **2. Busca Binária** — `binary_search()`
   - Complexidade: O(log n)
   - Requer lista pré-ordenada por distância
   - Busca por distância aproximada ao sol
   - Retorna corpo com distância exata ou sugere próximos
   - Arquivo: `algorithms.py`

### **3. Ordenação — Bubble Sort** — `bubble_sort()`
   - Complexidade: O(n²) pior caso, O(n) melhor caso
   - Ordena corpos por distância ao sol
   - Otimização: break quando já está ordenado
   - Arquivo: `algorithms.py`

### **4. Busca de Caminho Mínimo — Dijkstra (adaptado)**
   - Complexidade: O((V + E) log V) com heap
   - Score ponderado por perfil de missão
   - Considera até 1 escala intermediária
   - Retorna melhor rota entre origem e destino
   - Arquivo: `graph.py` — `find_best_route()`

### **5. Cálculo de Score Multicritério**
   - Combina: distância, tempo de viagem, custo de combustível, gravidade
   - Pesos ajustáveis por perfil (Econômica, Rápida, Segura, Balanceada, Personalizada)
   - Normalização automática de pesos
   - Arquivo: `graph.py` — `_compute_score()`

---

## 💻 Tecnologias e Bibliotecas Utilizadas

### **Core**
- **Python 3.13.12** — linguagem principal
- **requests** — requisições HTTP para API
- **dataclasses** — definição de modelos

### **Visualização**
- **matplotlib** — gráficos orbitais e comparação de missões
- **numpy** — suporte matemático para visualização

### **Estrutura**
- **Venv** — ambiente virtual Python isolado
- **Git** — controle de versão

### **Arquivos de Configuração**
- `requirements.txt` — dependências do projeto

---

## 📖 Explicação do Funcionamento

### **Fluxo Principal**

1. **Inicialização**
   - App inicia rápido sem carregar dados (lazy loading)
   - Menu interativo exibido
   - Dados dos planetas só são puxados quando necessário

2. **Carregamento de Dados** (sob demanda)
   - Requisição HTTP à API Solar System OpenData
   - Parse JSON e conversão para objetos `Body`
   - Construção do grafo completo de rotas
   - Cache em memória para operações subsequentes

3. **Operações Disponíveis**
   - **Listar corpos:** exibe 8 planetas ordenados por distância
   - **Busca linear:** encontra planeta por nome
   - **Busca binária:** encontra planeta por distância exata
   - **Calcular rota:** executa Dijkstra com critérios do perfil escolhido
   - **Enfileirar/Processar missões:** operações em lote com fila
   - **Histórico:** pilha de rotas com operação "desfazer"
   - **Comparar:** gráfico de barras com últimas rotas processadas
   - **Escolher foguete:** ajusta velocidade (Falcon 9, Saturn V, Ariane 5, SLS)

4. **Cálculo de Rota**
   - Usuario seleciona origem, destino e perfil de missão
   - Sistema constrói grafo com pesos do perfil
   - Dijkstra busca melhor rota (direto + 1 escala intermediária)
   - Retorna caminho, distância, tempo, custo e score
   - Gera visualização orbital interativa

### **Perfis de Missão**

| Perfil | Foco | Pesos |
|--------|------|-------|
| **Econômica** | Minimiza combustível | dist=0.15, tempo=0.10, comb=0.60, grav=0.15 |
| **Rápida** | Minimiza tempo | dist=0.20, tempo=0.60, comb=0.10, grav=0.10 |
| **Segura** | Evita alta gravidade | dist=0.15, tempo=0.15, comb=0.20, grav=0.50 |
| **Balanceada** | Pesos iguais | dist=0.25, tempo=0.25, comb=0.25, grav=0.25 |
| **Personalizada** | Usuário define | definido em tempo de execução |

---

## 🚀 Instruções de Execução

### **Pré-requisitos**
- Python 3.10+
- pip (gerenciador de pacotes)
- Conexão com internet (para API Solar System OpenData)

### **1. Clonar Repositório**
```bash
git clone https://github.com/thompson0/GS-Dynamic-Programming.git
cd GS-Dynamic-Programming
```

### **2. Criar Ambiente Virtual**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### **3. Instalar Dependências**
```bash
pip install -r requirements.txt
```

### **4. Executar a Aplicação**
```bash
python app.py
```

### **Exemplo de Uso**
```
═══════════════════════════════════════════════════════
  1 - Listar corpos (ordenados por distância)
  2 - Buscar corpo por nome  (busca linear)
  3 - Buscar corpo por distância (busca binária)
  4 - Calcular rota  (grafo multicritério)
  5 - Enfileirar missao
  6 - Processar fila de missoes
  7 - Desfazer ultima rota  (pilha)
  8 - Comparar missoes processadas (gráfico)
  9 - Escolher foguete
  0 - Sair
═══════════════════════════════════════════════════════
  Opcao: 4
  Origem: Terra
  Destino: Marte
  
  [ROTA]        Terra → Marte
  [DISTANCIA]   78.3 Mkm
  [TEMPO]       114.72 dias
  [COMBUSTIVEL] 127.45
  [SCORE]       0.2955
```

---

## 📁 Estrutura de Arquivos

```
GS-Dynamic-Programming/
├── app.py                 # Ponto de entrada — menu principal
├── models.py              # Definição de modelos de dados
├── data_structures.py     # Pilha, Fila, Lista Ligada
├── algorithms.py          # Busca linear, binária, bubble sort
├── graph.py               # Construção de grafo e algoritmo de rota
├── api_loader.py          # Integração com API Solar System OpenData
├── visualizer.py          # Geração de gráficos orbitais
├── draw.py                # ASCII art decorativa
├── README.md              # Este arquivo
├── requirements.txt       # Dependências do projeto
└── venv/                  # Ambiente virtual Python
```

---

## 👥 Integrantes do Grupo
- Nícolas Baradel - RM: 563245 
- José Kaneto - RM: 563186
- Gabriel Thompson - RM: 563126 
- Enzo Quarelo - RM: 561503
- João Pedro Sassarrão - RM: 562499
---

## 📝 Referências

- [Solar System OpenData API](https://api.le-systeme-solaire.net/)
- Cormen, Leiserson, Rivest, Stein. "Introduction to Algorithms" (Dijkstra's algorithm)
---
