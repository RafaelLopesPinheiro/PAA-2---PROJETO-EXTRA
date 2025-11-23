# GUIA DE EXECUÇÃO - PROJETO VRPTW COM ALGORITMO GENÉTICO

**Autor:** Rafael Lopes Pinheiro  
**Disciplina:** PAA-2 (Projeto de Análise de Algoritmos)  
**Data:** 23 de Novembro de 2025  
**Repositório:** https://github.com/RafaelLopesPinheiro/PAA-2---PROJETO-EXTRA

---

## 📋 SUMÁRIO

1. [Como Executar o Projeto](#1-como-executar-o-projeto)
2. [Significado dos Parâmetros](#2-significado-dos-parâmetros)
3. [Significado da Saída Exibida](#3-significado-da-saída-exibida)
4. [Como Variar a Entrada](#4-como-variar-a-entrada)
5. [Estrutura do Código-Fonte](#5-estrutura-do-código-fonte)
6. [Requisitos e Dependências](#6-requisitos-e-dependências)

---

## 1. COMO EXECUTAR O PROJETO

### 1.1. Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git (opcional, para clonar o repositório)

### 1.2. Instalação

```powershell
# 1. Clone o repositório (ou baixe o ZIP)
git clone https://github.com/RafaelLopesPinheiro/PAA-2---PROJETO-EXTRA.git
cd PAA-2---PROJETO-EXTRA

# 2. Crie um ambiente virtual
python -m venv .venv

# 3. Ative o ambiente virtual
.venv\Scripts\Activate.ps1   # Windows PowerShell
# OU
.venv\Scripts\activate.bat    # Windows CMD
# OU
source .venv/bin/activate     # Linux/Mac

# 4. Atualize pip e ferramentas de build
python -m pip install --upgrade pip setuptools wheel

# 5. Instale as dependências
pip install -r requirements.txt
```

### 1.3. Download dos Dados (OBRIGATÓRIO)

O projeto usa dados reais de delivery do Kaggle:

1. Acesse: https://www.kaggle.com/datasets/ghoshsaptarshi/av-genpact-hack-dec2018
2. Faça login no Kaggle (ou crie conta gratuita)
3. Clique em "Download" para baixar o dataset
4. Extraia o arquivo `train.csv`
5. Coloque em: `data/raw/food_delivery/train.csv`

**Estrutura esperada:**
```
data/
└── raw/
    └── food_delivery/
        ├── train.csv        ← ARQUIVO NECESSÁRIO
        ├── test.csv         (opcional)
        └── sample_sub.csv   (opcional)
```

### 1.4. Execução do Programa Principal

```powershell
# Execute o programa principal
python main.py
```

**Tempo de execução esperado:** 5-15 minutos (dependendo do hardware)

### 1.5. Execução do Notebook (Alternativa Interativa)

```powershell
# Abra o Jupyter Notebook no VS Code ou Jupyter Lab
# Arquivo: VRPTW_Complete_Project.ipynb

# Execute as células sequencialmente (Shift + Enter)
```

---

## 2. SIGNIFICADO DOS PARÂMETROS

O projeto possui três grupos de parâmetros principais:

### 2.1. Parâmetros de Dados (`config['data']`)

| Parâmetro | Tipo | Descrição | Valor Padrão |
|-----------|------|-----------|--------------|
| `input_file` | string | Caminho para arquivo CSV de entrada | `'data/raw/sales_data.csv'` |
| `instance_file` | string | Arquivo para salvar instância processada | `'data/processed/vrptw_instances.json'` |
| `max_customers` | int | Número máximo de clientes a processar | `40` |
| `vehicle_capacity` | float | Capacidade de carga de cada veículo | `50.0` |

**Como variar:**
```python
config['data']['max_customers'] = 30  # Problema menor (mais rápido)
config['data']['max_customers'] = 60  # Problema maior (mais difícil)
config['data']['vehicle_capacity'] = 100.0  # Veículos com mais capacidade
```

### 2.2. Parâmetros da Heurística de Solomon (`config['solomon']`)

| Parâmetro | Tipo | Descrição | Valor Padrão | Faixa Recomendada |
|-----------|------|-----------|--------------|-------------------|
| `alpha` | float | Peso para distância no critério de inserção | `1.0` | [0.0, 2.0] |
| `mu` | float | Peso para tempo no critério de inserção | `1.0` | [0.0, 2.0] |
| `lambda_param` | float | Peso para urgência temporal | `2.0` | [1.0, 3.0] |

**Fórmula de custo de inserção:**
```
c(i,u,j) = α·c1(i,u,j) + λ·c2(i,u,j)

onde:
  c1(i,u,j) = d(i,u) + d(u,j) - μ·d(i,j)  [custo de distância]
  c2(i,u,j) = b_j - b_u                     [custo temporal/urgência]
```

**Como variar:**
```python
# Priorizar distância (soluções mais compactas)
config['solomon']['alpha'] = 2.0
config['solomon']['lambda_param'] = 1.0

# Priorizar janelas de tempo (mais factível)
config['solomon']['alpha'] = 0.5
config['solomon']['lambda_param'] = 3.0
```

### 2.3. Parâmetros do Algoritmo Genético (`config['genetic_algorithm']`)

| Parâmetro | Tipo | Descrição | Valor Padrão | Faixa Recomendada |
|-----------|------|-----------|--------------|-------------------|
| `pop_size` | int | Tamanho da população | `100` | [50, 200] |
| `elite_size` | int | Número de melhores soluções preservadas | `20` | [10, 30] |
| `generations` | int | Número de gerações | `300` | [100, 500] |
| `crossover_rate` | float | Probabilidade de crossover | `0.8` | [0.6, 0.9] |
| `mutation_rate` | float | Probabilidade de mutação | `0.2` | [0.1, 0.3] |
| `local_search_rate` | float | Probabilidade de busca local | `0.3` | [0.1, 0.5] |
| `seed` | int | Semente para reprodutibilidade | `42` | qualquer int |

**Como variar:**
```python
# Execução rápida (teste)
config['genetic_algorithm']['pop_size'] = 50
config['genetic_algorithm']['generations'] = 100

# Execução intensiva (melhor qualidade)
config['genetic_algorithm']['pop_size'] = 200
config['genetic_algorithm']['generations'] = 500
config['genetic_algorithm']['local_search_rate'] = 0.5

# Maior exploração (diversidade)
config['genetic_algorithm']['mutation_rate'] = 0.4
config['genetic_algorithm']['crossover_rate'] = 0.6

# Maior explotação (convergência)
config['genetic_algorithm']['mutation_rate'] = 0.1
config['genetic_algorithm']['elite_size'] = 30
```

---

## 3. SIGNIFICADO DA SAÍDA EXIBIDA

O programa exibe 8 passos principais:

### PASSO 1: CONFIGURAÇÃO DO AMBIENTE
```
✓ Configuração concluída
```
**Significado:** Diretórios criados (`results/`, `data/`)

### PASSO 2: PREPARAÇÃO DA INSTÂNCIA VRPTW
```
🍔 Usando Food Delivery Dataset (Kaggle)
⚙️ Configurações:
   Máximo de entregas: 40
   Capacidade por veículo: 50.0 unidades

✓ Instância carregada com sucesso
   Clientes: 40
   Veículos disponíveis: 8
   Demanda total: 178.45 unidades
```

**Significado:**
- `Clientes`: Número de entregas a realizar
- `Veículos disponíveis`: Calculado como `⌈demanda_total / capacidade⌉`
- `Demanda total`: Soma de todas as demandas dos clientes

### PASSO 3: SOLUÇÃO INICIAL (HEURÍSTICA DE SOLOMON)
```
📊 Resultados da Heurística de Solomon:
   • Fitness: 1234.56
   • Distância Total: 1234.56
   • Tempo Total: 456.78
   • Número de Veículos: 5
   • Factível: True
```

**Significado:**
- `Fitness`: Função objetivo = distância total + penalidades
- `Distância Total`: Soma das distâncias percorridas (km ou unidades)
- `Tempo Total`: Soma dos tempos de todas as rotas (minutos)
- `Número de Veículos`: Veículos efetivamente usados na solução
- `Factível`: True = todas as restrições são respeitadas

### PASSO 4: OTIMIZAÇÃO COM ALGORITMO GENÉTICO
```
🧬 Algoritmo Genético - Geração 0/300
   Melhor Fitness: 1234.56 | Fitness Médio: 1456.78

🧬 Algoritmo Genético - Geração 50/300
   Melhor Fitness: 1050.23 | Fitness Médio: 1234.56 | Melhoria: 14.93%

...

🧬 Algoritmo Genético - Geração 300/300
   Melhor Fitness: 950.12 | Fitness Médio: 1023.45 | Melhoria: 23.04%

✅ Algoritmo finalizado!
   Melhor Fitness: 950.12
   Gerações: 300
   Tempo de execução: 245.67 s
```

**Significado:**
- `Melhor Fitness`: Menor valor de fitness encontrado até o momento
- `Fitness Médio`: Média da população atual
- `Melhoria`: Percentual de melhoria em relação à solução inicial
- `Tempo de execução`: Tempo total do algoritmo genético

### PASSO 5: ANÁLISE DE RESULTADOS
```
📈 COMPARAÇÃO: SOLOMON vs ALGORITMO GENÉTICO
Métrica                       Solomon         AG Híbrido      Melhoria
--------------------------------------------------------------------------------
Distância Total               1234.56         950.12          23.04%
Tempo Total                   456.78          398.23          N/A
Número de Veículos            5               4               -1
Fitness                       1234.56         950.12          23.04%
Factível                      True            True            N/A
```

**Significado:**
- Valores positivos em "Melhoria" = o AG melhorou a solução
- Valores negativos em "Número de Veículos" = menos veículos usados (melhor)
- `N/A` = métrica não comparável diretamente

### PASSO 6: GERAÇÃO DE VISUALIZAÇÕES
```
📊 Plotando solução inicial (Solomon)...
📊 Plotando solução otimizada (AG)...
📊 Plotando convergência do AG...
📊 Plotando comparação de soluções...
📊 Plotando cumprimento de janelas de tempo...

✓ Todas as visualizações salvas em: results/plots/
```

**Arquivos gerados:**
- `solution_solomon.png`: Mapa de rotas da solução inicial
- `solution_genetic_algorithm.png`: Mapa de rotas otimizadas
- `convergence.png`: Gráfico de convergência do AG
- `comparison.png`: Comparação lado a lado
- `time_windows.png`: Gráfico de cumprimento de janelas de tempo

### PASSO 7: SALVAMENTO DE SOLUÇÕES
```
✓ Solução Solomon salva: results/solutions/solution_solomon.json
✓ Solução AG salva: results/solutions/solution_genetic_algorithm.json
```

**Formato JSON das soluções:**
```json
{
  "method": "Hybrid Genetic Algorithm",
  "fitness": 950.12,
  "total_distance": 950.12,
  "total_time": 398.23,
  "num_vehicles": 4,
  "feasible": true,
  "routes": [
    {
      "vehicle_id": 0,
      "customers": [0, 5, 12, 8, 0],
      "load": 45.2,
      "distance": 245.67,
      "time": 98.45
    },
    ...
  ]
}
```

### PASSO 8: GERAÇÃO DO RELATÓRIO TÉCNICO
```
✓ Relatório técnico salvo: results/report.txt
  Páginas: ~10 (estimativa)
```

**Conteúdo do relatório:**
1. Referência do artigo científico
2. Descrição do problema VRPTW
3. Algoritmos implementados (Solomon + AG)
4. Análise de complexidade computacional
5. Instância do problema
6. Parâmetros utilizados
7. Resultados experimentais detalhados
8. Conclusões e trabalhos futuros
9. Referências bibliográficas

---

## 4. COMO VARIAR A ENTRADA

### 4.1. Modificar Parâmetros no Código

Edite o arquivo `main.py` na função `_default_config()`:

```python
def _default_config(self) -> dict:
    return {
        'data': {
            'max_customers': 60,  # ← ALTERE AQUI
            'vehicle_capacity': 75.0  # ← ALTERE AQUI
        },
        'genetic_algorithm': {
            'pop_size': 150,  # ← ALTERE AQUI
            'generations': 400,  # ← ALTERE AQUI
            # ...
        }
    }
```

### 4.2. Usar Diferentes Datasets

**Opção 1: Usar arquivo CSV próprio**

Prepare um CSV com as colunas:
```csv
market_id,created_at,lat,lng,total_items
```

E carregue no código:
```python
data_path='caminho/para/seu/arquivo.csv'
```

**Opção 2: Usar instâncias benchmark de Solomon**

Baixe instâncias clássicas do VRPTW:
- http://web.cba.neu.edu/~msolomon/problems.htm

E adapte o loader em `src/solomon_loader.py`

### 4.3. Variar Número de Clientes

```python
# Problema pequeno (rápido, ~2 min)
config['data']['max_customers'] = 20

# Problema médio (moderado, ~5-10 min)
config['data']['max_customers'] = 40

# Problema grande (lento, ~20-30 min)
config['data']['max_customers'] = 80
```

### 4.4. Ajustar Capacidade dos Veículos

```python
# Veículos pequenos (mais veículos necessários)
vehicle_capacity = 30.0

# Veículos grandes (menos veículos necessários)
vehicle_capacity = 100.0
```

### 4.5. Testar Diferentes Estratégias do AG

```python
# Estratégia 1: Exploração Intensiva
config['genetic_algorithm']['mutation_rate'] = 0.4
config['genetic_algorithm']['crossover_rate'] = 0.6
config['genetic_algorithm']['pop_size'] = 150

# Estratégia 2: Convergência Rápida
config['genetic_algorithm']['mutation_rate'] = 0.1
config['genetic_algorithm']['elite_size'] = 40
config['genetic_algorithm']['local_search_rate'] = 0.5

# Estratégia 3: Balanceada (Padrão)
config['genetic_algorithm']['mutation_rate'] = 0.2
config['genetic_algorithm']['crossover_rate'] = 0.8
config['genetic_algorithm']['elite_size'] = 20
```

---

## 5. ESTRUTURA DO CÓDIGO-FONTE

```
PAA-2---PROJETO-EXTRA/
│
├── main.py                          # ← PROGRAMA PRINCIPAL (EXECUTAR ESTE)
│
├── src/                             # Código-fonte modular
│   ├── __init__.py
│   ├── utils.py                     # Funções auxiliares
│   ├── food_delivery_loader.py      # Carregador de dados
│   ├── solomon_loader.py            # Carregador Solomon
│   ├── heuristics.py                # Heurística de Solomon (I1)
│   ├── genetic_algorithm.py         # Algoritmo Genético Híbrido
│   └── visualization.py             # Geração de gráficos
│
├── data/                            # Dados de entrada
│   ├── raw/
│   │   └── food_delivery/
│   │       └── train.csv            # ← DATASET NECESSÁRIO
│   └── processed/
│       └── vrptw_instances.json     # Instâncias processadas
│
├── results/                         # Saídas geradas
│   ├── solutions/                   # Soluções em JSON
│   ├── plots/                       # Gráficos PNG
│   └── report.txt                   # Relatório técnico
│
├── requirements.txt                 # Dependências Python
├── README.MD                        # Documentação do projeto
└── VRPTW_Complete_Project.ipynb     # Notebook interativo (alternativa)
```

---

## 6. REQUISITOS E DEPENDÊNCIAS

### 6.1. Dependências Python

| Pacote | Versão | Finalidade |
|--------|--------|------------|
| `numpy` | 1.24.3 | Operações numéricas e matrizes |
| `pandas` | 2.0.3 | Manipulação de dados CSV |
| `matplotlib` | 3.7.2 | Geração de gráficos |
| `scipy` | 1.11.1 | Cálculos científicos |

**Instalação:**
```powershell
pip install -r requirements.txt
```

### 6.2. Requisitos de Sistema

- **Python:** 3.8 ou superior
- **RAM:** Mínimo 2GB (recomendado 4GB+)
- **Espaço em disco:** ~500MB (inclui dados e resultados)
- **Sistema Operacional:** Windows, Linux, ou macOS

### 6.3. Tempo de Execução Estimado

| Configuração | Clientes | Gerações | Tempo Aprox. |
|--------------|----------|----------|--------------|
| Rápida       | 20       | 100      | 2-3 min      |
| Padrão       | 40       | 300      | 8-12 min     |
| Intensiva    | 80       | 500      | 30-45 min    |

---

## 7. TROUBLESHOOTING (RESOLUÇÃO DE PROBLEMAS)

### Erro: `FileNotFoundError: train.csv not found`

**Solução:** Baixe o dataset do Kaggle (seção 1.3)

### Erro: `ModuleNotFoundError: No module named 'numpy'`

**Solução:** 
```powershell
pip install -r requirements.txt
```

### Erro: `BackendUnavailable: Cannot import 'setuptools.build_meta'`

**Solução:**
```powershell
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Programa muito lento

**Solução:** Reduza os parâmetros:
```python
config['data']['max_customers'] = 20
config['genetic_algorithm']['pop_size'] = 50
config['genetic_algorithm']['generations'] = 100
```

---

## 8. CONTATO E SUPORTE

**Autor:** Rafael Lopes Pinheiro  
**GitHub:** [@RafaelLopesPinheiro](https://github.com/RafaelLopesPinheiro)  
**Repositório:** https://github.com/RafaelLopesPinheiro/PAA-2---PROJETO-EXTRA

Para dúvidas ou problemas, abra uma **Issue** no GitHub do projeto.

---

**Última atualização:** 23/11/2025
