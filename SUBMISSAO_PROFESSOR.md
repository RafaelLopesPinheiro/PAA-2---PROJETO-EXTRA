# SUBMISSÃO - PROJETO EXTRA PAA-2

**Disciplina:** Projeto de Análise de Algoritmos (PAA-2)  
**Aluno:** Rafael Lopes Pinheiro  
**Projeto:** Vehicle Routing Problem with Time Windows - Algoritmo Genético Híbrido  
**Repositório:** https://github.com/RafaelLopesPinheiro/PAA-2---PROJETO-EXTRA  
**Data:** 23/11/2025

---

## ✅ INFORMAÇÕES SOLICITADAS PELO PROFESSOR

### 1. COMO EXECUTAR

#### Passo 1: Preparação do Ambiente

```powershell
# Clone o repositório
git clone https://github.com/RafaelLopesPinheiro/PAA-2---PROJETO-EXTRA.git
cd PAA-2---PROJETO-EXTRA

# Crie ambiente virtual
python -m venv .venv

# Ative o ambiente (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Atualize pip e ferramentas
python -m pip install --upgrade pip setuptools wheel

# Instale dependências
pip install -r requirements.txt
```

#### Passo 2: Download dos Dados (OBRIGATÓRIO)

O projeto usa dados reais de entregas do Kaggle:

1. Acesse: https://www.kaggle.com/datasets/ghoshsaptarshi/av-genpact-hack-dec2018
2. Faça login no Kaggle (ou crie conta gratuita)
3. Clique em "Download" e extraia o arquivo `train.csv`
4. Coloque em: `data/raw/food_delivery/train.csv`

**Estrutura esperada:**
```
data/
└── raw/
    └── food_delivery/
        └── train.csv  ← Este arquivo é necessário
```

#### Passo 3: Execução

```powershell
# Execute o programa principal
python main.py
```

**Tempo de execução:** Aproximadamente 8-12 minutos

**Arquivo a executar:** `main.py` (este é o arquivo principal do projeto)

---

### 2. SIGNIFICADO DOS PARÂMETROS

O programa possui três grupos de parâmetros configuráveis:

#### 2.1. Parâmetros de Dados (`config['data']`)

| Parâmetro | Tipo | Valor Padrão | Descrição |
|-----------|------|--------------|-----------|
| `max_customers` | int | 40 | Número máximo de clientes (entregas) a processar do dataset. Valores maiores = problema mais difícil |
| `vehicle_capacity` | float | 50.0 | Capacidade de carga de cada veículo em unidades. Determina quantos pedidos cada veículo pode transportar |

**Exemplo de variação:**
```python
# Problema pequeno (mais rápido)
config['data']['max_customers'] = 20
config['data']['vehicle_capacity'] = 30.0

# Problema grande (mais desafiador)
config['data']['max_customers'] = 60
config['data']['vehicle_capacity'] = 100.0
```

#### 2.2. Parâmetros da Heurística de Solomon (`config['solomon']`)

| Parâmetro | Tipo | Valor Padrão | Descrição |
|-----------|------|--------------|-----------|
| `alpha` | float | 1.0 | Peso para o componente de distância no critério de inserção. Maior valor = prioriza minimizar distância |
| `mu` | float | 1.0 | Fator de redução do custo de distância quando há sobreposição temporal |
| `lambda_param` | float | 2.0 | Peso para o componente temporal (urgência). Maior valor = prioriza cumprir janelas de tempo |

**Fórmula usada:**
```
c(i,u,j) = α × c1(i,u,j) + λ × c2(i,u,j)

onde:
  c1(i,u,j) = d(i,u) + d(u,j) - μ × d(i,j)  [custo de distância]
  c2(i,u,j) = b_j - b_u                      [custo temporal/urgência]
  
  i = cliente anterior
  u = cliente candidato a inserção
  j = cliente posterior
  d(x,y) = distância entre x e y
  b_x = início da janela de tempo de x
```

**Exemplo de variação:**
```python
# Priorizar distância (rotas mais compactas)
config['solomon']['alpha'] = 2.0
config['solomon']['lambda_param'] = 1.0

# Priorizar janelas de tempo (maior viabilidade)
config['solomon']['alpha'] = 0.5
config['solomon']['lambda_param'] = 3.0
```

#### 2.3. Parâmetros do Algoritmo Genético (`config['genetic_algorithm']`)

| Parâmetro | Tipo | Valor Padrão | Descrição |
|-----------|------|--------------|-----------|
| `pop_size` | int | 100 | Tamanho da população (número de soluções simultâneas). Maior = mais diversidade, mas mais lento |
| `elite_size` | int | 20 | Número de melhores soluções preservadas sem alteração a cada geração (elitismo) |
| `generations` | int | 300 | Número de iterações do algoritmo. Mais gerações = potencial de melhor solução |
| `crossover_rate` | float | 0.8 | Probabilidade de aplicar crossover (80%). Controla explotação vs. exploração |
| `mutation_rate` | float | 0.2 | Probabilidade de aplicar mutação (20%). Maior = mais exploração, menor = mais convergência |
| `local_search_rate` | float | 0.3 | Probabilidade de aplicar busca local 2-opt (30%). Refina soluções localmente |
| `seed` | int | 42 | Semente aleatória para reprodutibilidade dos resultados |

**Exemplo de variação:**
```python
# Execução rápida (teste)
config['genetic_algorithm']['pop_size'] = 50
config['genetic_algorithm']['generations'] = 100

# Execução intensiva (melhor qualidade)
config['genetic_algorithm']['pop_size'] = 200
config['genetic_algorithm']['generations'] = 500
config['genetic_algorithm']['local_search_rate'] = 0.5

# Maior exploração (evitar mínimos locais)
config['genetic_algorithm']['mutation_rate'] = 0.4
config['genetic_algorithm']['crossover_rate'] = 0.6

# Maior convergência (refinamento)
config['genetic_algorithm']['mutation_rate'] = 0.1
config['genetic_algorithm']['elite_size'] = 30
```

---

### 3. SIGNIFICADO DA SAÍDA EXIBIDA

O programa exibe 8 passos sequenciais com informações específicas:

#### PASSO 1: Configuração do Ambiente
```
PASSO 1: CONFIGURAÇÃO DO AMBIENTE
--------------------------------------------------------------------------------
✓ Configuração concluída
```

**Significado:** Diretórios `results/`, `data/processed/` foram criados com sucesso.

---

#### PASSO 2: Preparação da Instância VRPTW
```
PASSO 2: PREPARAÇÃO DA INSTÂNCIA VRPTW
--------------------------------------------------------------------------------
🍔 Usando Food Delivery Dataset (Kaggle)
⚙️ Configurações:
   Máximo de entregas: 40
   Capacidade por veículo: 50.0 unidades

✓ Instância carregada com sucesso
   Clientes: 40
   Veículos disponíveis: 8
   Demanda total: 178.45 unidades
   Janela de tempo global: [0.0, 480.0]
```

**Significado dos valores:**
- **Clientes:** Número de entregas (pontos de entrega) carregados do dataset
- **Veículos disponíveis:** Calculado automaticamente como `⌈demanda_total / capacidade⌉`
- **Demanda total:** Soma de todos os pedidos (itens) dos clientes
- **Janela de tempo:** Intervalo operacional (0-480 minutos = 8 horas)

---

#### PASSO 3: Solução Inicial (Heurística de Solomon)
```
PASSO 3: SOLUÇÃO INICIAL (HEURÍSTICA DE SOLOMON)
--------------------------------------------------------------------------------
📊 Resultados da Heurística de Solomon:
   • Fitness: 1234.56
   • Distância Total: 1234.56
   • Tempo Total: 456.78
   • Número de Veículos: 5
   • Factível: True
```

**Significado dos valores:**
- **Fitness:** Função objetivo a minimizar (neste caso = distância total + penalidades por violações)
  - Valores menores são melhores
  - Penalidades: +1000 por violação de capacidade, +500 por violação de janela de tempo
- **Distância Total:** Soma de todas as distâncias percorridas por todos os veículos (unidades do dataset)
- **Tempo Total:** Soma dos tempos de todas as rotas em minutos
- **Número de Veículos:** Quantos veículos foram efetivamente usados (≤ veículos disponíveis)
- **Factível:** 
  - `True` = Todas as restrições foram respeitadas (capacidade, janelas de tempo)
  - `False` = Alguma restrição foi violada

---

#### PASSO 4: Otimização com Algoritmo Genético
```
PASSO 4: OTIMIZAÇÃO COM ALGORITMO GENÉTICO MELHORADO
--------------------------------------------------------------------------------
🧬 Algoritmo Genético - Geração 0/300
   Melhor Fitness: 1234.56 | Fitness Médio: 1456.78

🧬 Algoritmo Genético - Geração 50/300
   Melhor Fitness: 1050.23 | Fitness Médio: 1234.56 | Melhoria: 14.93%

🧬 Algoritmo Genético - Geração 100/300
   Melhor Fitness: 980.45 | Fitness Médio: 1150.34 | Melhoria: 20.58%

...

🧬 Algoritmo Genético - Geração 300/300
   Melhor Fitness: 950.12 | Fitness Médio: 1023.45 | Melhoria: 23.04%

✅ Algoritmo finalizado!
   Melhor Fitness: 950.12
   Gerações: 300
   Tempo de execução: 245.67 s
```

**Significado dos valores:**
- **Melhor Fitness:** Menor valor encontrado até agora (melhor solução da população)
- **Fitness Médio:** Média dos fitness de toda a população atual
  - Se estiver muito acima do melhor = população diversificada
  - Se estiver próximo do melhor = população convergiu
- **Melhoria:** Percentual de redução do fitness em relação à solução inicial de Solomon
  - Valores positivos = o AG está melhorando a solução
- **Tempo de execução:** Tempo total gasto pelo algoritmo genético

---

#### PASSO 5: Análise de Resultados
```
PASSO 5: ANÁLISE DE RESULTADOS
--------------------------------------------------------------------------------
📈 COMPARAÇÃO: SOLOMON vs ALGORITMO GENÉTICO
Métrica                       Solomon         AG Híbrido      Melhoria
--------------------------------------------------------------------------------
Distância Total               1234.56         950.12          23.04%
Tempo Total                   456.78          398.23          N/A
Número de Veículos            5               4               -1
Fitness                       1234.56         950.12          23.04%
Factível                      True            True            N/A
```

**Significado das colunas:**
- **Solomon:** Resultados da heurística inicial
- **AG Híbrido:** Resultados após otimização com algoritmo genético
- **Melhoria:** 
  - Percentual positivo = AG melhorou (reduziu) o valor
  - Número negativo em "Veículos" = menos veículos usados (MELHOR)
  - `N/A` = métrica não diretamente comparável

**Interpretação:**
- Distância reduzida em 23% = rotas mais eficientes
- 1 veículo a menos = economia de custo operacional
- Ambos factíveis = todas as restrições respeitadas

---

#### PASSO 6: Geração de Visualizações
```
PASSO 6: GERAÇÃO DE VISUALIZAÇÕES
--------------------------------------------------------------------------------
📊 Plotando solução inicial (Solomon)...
📊 Plotando solução otimizada (AG)...
📊 Plotando convergência do AG...
📊 Plotando comparação de soluções...
📊 Plotando cumprimento de janelas de tempo...

✓ Todas as visualizações salvas em: results/plots/
```

**Arquivos gerados em `results/plots/`:**
1. `solution_solomon.png` - Mapa 2D com rotas da solução inicial
2. `solution_genetic_algorithm.png` - Mapa 2D com rotas otimizadas
3. `convergence.png` - Gráfico mostrando evolução do fitness ao longo das gerações
4. `comparison.png` - Comparação lado a lado das duas soluções
5. `time_windows.png` - Gráfico de barras mostrando cumprimento de janelas de tempo

---

#### PASSO 7: Salvamento de Soluções
```
PASSO 7: SALVAMENTO DE SOLUÇÕES
--------------------------------------------------------------------------------
✓ Solução Solomon salva: results/solutions/solution_solomon.json
✓ Solução AG salva: results/solutions/solution_genetic_algorithm.json
```

**Conteúdo dos arquivos JSON:**
- Fitness, distância, tempo, número de veículos
- Detalhes de cada rota (veículo, clientes, carga, distância)
- Para o AG: histórico de convergência e parâmetros usados

**Formato:**
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
    }
  ]
}
```

---

#### PASSO 8: Geração do Relatório Técnico
```
PASSO 8: GERAÇÃO DO RELATÓRIO TÉCNICO
--------------------------------------------------------------------------------
✓ Relatório técnico salvo: results/report.txt
  Páginas: ~10 (estimativa)
```

**Conteúdo do relatório (`results/report.txt`):**
1. Referência do artigo científico base
2. Descrição detalhada do problema VRPTW
3. Algoritmos implementados (Solomon + AG)
4. Análise de complexidade computacional (O(n³) e O(G×P×n²))
5. Descrição da instância utilizada
6. Parâmetros configurados
7. Resultados experimentais completos
8. Conclusões e trabalhos futuros
9. Referências bibliográficas

**Este relatório serve como documentação técnica completa do projeto.**

---

### 4. COMO VARIAR A ENTRADA

Há várias formas de modificar os dados de entrada e parâmetros:

#### 4.1. Modificar Parâmetros no Código

Edite o arquivo `main.py` na função `_default_config()` (linha ~68):

```python
def _default_config(self) -> dict:
    return {
        'data': {
            'max_customers': 60,  # ← MUDE AQUI: 20 (rápido) a 100 (lento)
            'vehicle_capacity': 75.0  # ← MUDE AQUI: capacidade dos veículos
        },
        'solomon': {
            'alpha': 1.5,  # ← MUDE AQUI: peso de distância
            'lambda_param': 2.5  # ← MUDE AQUI: peso de tempo
        },
        'genetic_algorithm': {
            'pop_size': 150,  # ← MUDE AQUI: tamanho da população
            'generations': 400,  # ← MUDE AQUI: número de gerações
            'crossover_rate': 0.85,  # ← MUDE AQUI: taxa de crossover
            'mutation_rate': 0.25,  # ← MUDE AQUI: taxa de mutação
            # ...
        }
    }
```

#### 4.2. Variar Tamanho do Problema

**Problema Pequeno (execução rápida ~2-3 min):**
```python
config['data']['max_customers'] = 20
config['genetic_algorithm']['pop_size'] = 50
config['genetic_algorithm']['generations'] = 100
```

**Problema Médio (padrão ~8-12 min):**
```python
config['data']['max_customers'] = 40
config['genetic_algorithm']['pop_size'] = 100
config['genetic_algorithm']['generations'] = 300
```

**Problema Grande (execução longa ~30-45 min):**
```python
config['data']['max_customers'] = 80
config['genetic_algorithm']['pop_size'] = 200
config['genetic_algorithm']['generations'] = 500
```

#### 4.3. Testar Diferentes Estratégias

**Estratégia 1: Exploração Intensiva (maior diversidade)**
```python
config['genetic_algorithm']['mutation_rate'] = 0.4  # mais mutações
config['genetic_algorithm']['crossover_rate'] = 0.6  # menos crossover
config['genetic_algorithm']['pop_size'] = 150  # população maior
```

**Estratégia 2: Convergência Rápida (refinamento local)**
```python
config['genetic_algorithm']['mutation_rate'] = 0.1  # menos mutações
config['genetic_algorithm']['elite_size'] = 40  # mais elitismo
config['genetic_algorithm']['local_search_rate'] = 0.5  # mais busca local
```

**Estratégia 3: Balanceada (padrão)**
```python
config['genetic_algorithm']['mutation_rate'] = 0.2
config['genetic_algorithm']['crossover_rate'] = 0.8
config['genetic_algorithm']['elite_size'] = 20
```

#### 4.4. Usar Dataset Diferente

Para usar seus próprios dados de entregas:

1. Prepare um arquivo CSV com as colunas:
   ```csv
   market_id,created_at,lat,lng,total_items
   ```

2. Modifique o caminho em `main.py` (linha ~125):
   ```python
   self.instance = load_food_delivery_instance(
       max_customers=max_customers,
       vehicle_capacity=vehicle_capacity,
       data_path='caminho/para/seu/arquivo.csv'  # ← MUDE AQUI
   )
   ```

#### 4.5. Usar Instâncias Benchmark

Para testar com instâncias clássicas de Solomon:

1. Baixe instâncias: http://web.cba.neu.edu/~msolomon/problems.htm
2. Coloque em `data/raw/solomon/`
3. Use o loader Solomon:
   ```python
   from src.solomon_loader import load_solomon_instance
   self.instance = load_solomon_instance('C101')
   ```

---

## 📊 RESUMO DOS ARTEFATOS GERADOS

Ao final da execução, o programa gera:

| Tipo | Local | Descrição |
|------|-------|-----------|
| **Soluções** | `results/solutions/*.json` | Rotas em formato JSON (Solomon e AG) |
| **Gráficos** | `results/plots/*.png` | 5 visualizações (mapas, convergência, comparação) |
| **Relatório** | `results/report.txt` | Relatório técnico completo (~10 páginas) |
| **Instância** | `data/processed/*.json` | Instância VRPTW processada (reutilizável) |

---

## ✅ CHECKLIST DE REQUISITOS ATENDIDOS

Conforme solicitado pelo professor:

- ✅ **Como executar:** Seção 1 completa com todos os passos
- ✅ **Significado dos parâmetros:** Seção 2 com descrição detalhada de todos os parâmetros
- ✅ **Significado da saída:** Seção 3 com explicação linha a linha da saída
- ✅ **Como variar a entrada:** Seção 4 com exemplos práticos de variação
- ✅ **Código-fonte executável:** Disponível no repositório GitHub
- ✅ **Repositório:** https://github.com/RafaelLopesPinheiro/PAA-2---PROJETO-EXTRA

---

## 📚 DOCUMENTAÇÃO ADICIONAL

Arquivos complementares no repositório:

1. **README.MD** - Visão geral do projeto
2. **GUIA_EXECUCAO.md** - Guia detalhado de execução (versão expandida deste documento)
3. **NOTEBOOK_USAGE.md** - Como usar o Jupyter Notebook (alternativa interativa)
4. **requirements.txt** - Lista de dependências Python

---

## 🔍 VERIFICAÇÃO DE FUNCIONAMENTO

Para garantir que o código está funcionando:

```powershell
# 1. Verifique se os módulos importam corretamente
python -c "from src.genetic_algorithm import ImprovedGeneticAlgorithm; print('OK')"

# 2. Verifique se o dataset foi baixado corretamente
python -c "import os; print('Dataset:', 'OK' if os.path.exists('data/raw/food_delivery/train.csv') else 'FALTANDO')"

# 3. Execute o programa completo
python main.py
```

---

## 📞 CONTATO

**Aluno:** Rafael Lopes Pinheiro  
**GitHub:** [@RafaelLopesPinheiro](https://github.com/RafaelLopesPinheiro)  
**Repositório:** https://github.com/RafaelLopesPinheiro/PAA-2---PROJETO-EXTRA

---

**Data de Submissão:** 23/11/2025  
**Versão do Documento:** 1.0
