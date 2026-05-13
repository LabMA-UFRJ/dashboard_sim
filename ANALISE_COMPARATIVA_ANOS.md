# 📊 ANÁLISE COMPARATIVA POR ANO (2004-2022)

## 🎯 Novo Recurso

Agora você pode fazer análises comparativas entre múltiplos anos de dados SIM-DATASUS (2004 a 2022)!

---

## ✨ O Que Foi Adicionado

### 1. **Modo de Análise Dual**
O app agora oferece dois modos:
- **Ano Único**: Análise de um arquivo específico (comportamento anterior)
- **Comparativo (2004-2022)**: Análise temporal de múltiplos anos

### 2. **8 Novas Funções**

| Função | Propósito |
|--------|-----------|
| `load_sim_data_by_year()` | Carrega arquivo de um ano específico |
| `load_sim_data_range()` | Carrega múltiplos anos (intervalo) |
| `combine_sim_data()` | Combina DataFrames de vários anos |
| `plot_deaths_by_year()` | Gráfico de tendência geral |
| `plot_category_comparison_by_year()` | Evolução de categoria ao longo dos anos |
| `plot_category_heatmap_by_year()` | Mapa de calor categoria vs ano |
| `plot_age_distribution_by_year()` | Distribuição etária comparativa |
| `get_statistics_by_year()` | Estatísticas agregadas por ano |

---

## 🚀 Como Usar

### Passo 1: Abrir o App
```bash
streamlit run app.py
```

### Passo 2: Selecionar Modo
No sidebar, escolher: **"Comparativo (2004-2022)"**

### Passo 3: Definir Intervalo
- Deslizar **Ano Inicial** (2004-2022)
- Deslizar **Ano Final** (2004-2022)

### Passo 4: Selecionar Tipo de Análise
Escolher um dos 5 tipos:

1. **Evolução Geral de Óbitos**
   - Mostra tendência de óbitos totais
   - Útil para ver crescimento/redução geral

2. **Evolução por Categoria**
   - Selecione uma categoria (Sexo, Raça/Cor, etc)
   - Veja como cada subcategoria mudou
   - Ex: Óbitos em Mulheres vs Homens ao longo dos anos

3. **Heatmap de Categoria**
   - Visualização em cores (mapa de calor)
   - Eixo X: Anos
   - Eixo Y: Subcategorias
   - Cores: Intensidade de óbitos

4. **Distribuição Etária**
   - Compara como a idade dos óbitos evoluiu
   - Várias linhas (uma por ano)
   - Identifica mudanças na pirâmide etária

5. **Estatísticas Gerais**
   - Tabela completa com todas as métricas
   - Opção de detalhar por categoria
   - Download em CSV

---

## 📊 Exemplos de Uso

### Exemplo 1: Ver Tendência Geral (2004-2022)

```
1. Modo: "Comparativo (2004-2022)"
2. Ano Inicial: 2004
3. Ano Final: 2022
4. Tipo: "Evolução Geral de Óbitos"

Resultado:
- Gráfico em linha mostrando se óbitos aumentaram ou diminuíram
- Útil para políticas de saúde pública
```

### Exemplo 2: Comparar Sexos ao Longo do Tempo

```
1. Modo: "Comparativo (2004-2022)"
2. Ano Inicial: 2010
3. Ano Final: 2022
4. Tipo: "Evolução por Categoria"
5. Categoria: "Sexo"

Resultado:
- 2 linhas (Masculino e Feminino)
- Mostra se houve mudança no padrão de óbitos por sexo
- Pode indicar mudanças demográficas
```

### Exemplo 3: Visualizar Intensidade de Raça/Cor

```
1. Modo: "Comparativo (2004-2022)"
2. Ano Inicial: 2004
3. Ano Final: 2022
4. Tipo: "Heatmap de Categoria"
5. Categoria: "Raça/Cor"

Resultado:
- Matriz de cores: Anos (colunas) vs Raça/Cor (linhas)
- Cores mais vermelhas = mais óbitos
- Rápida identificação de padrões
```

### Exemplo 4: Análise de Idade

```
1. Modo: "Comparativo (2004-2022)"
2. Ano Inicial: 2004
3. Ano Final: 2022
4. Tipo: "Distribuição Etária"

Resultado:
- Múltiplas linhas (uma por ano)
- Mostra se população de óbitos está envelhecendo
- Picos de idade podem indicar eventos/epidemias
```

### Exemplo 5: Exportar Dados

```
1. Modo: "Comparativo (2004-2022)"
2. Ano Inicial: 2015
3. Ano Final: 2022
4. Tipo: "Estatísticas Gerais"
5. Marcar "Detalhar por categoria"
6. Selecionar categoria desejada

Resultado:
- Tabela com todas as métricas
- Botão "Baixar Estatísticas (CSV)"
- Arquivo para análise em Excel/Python
```

---

## 📁 Estrutura de Arquivos Esperada

```
//Projetos2/Wrk/SIM-DATASUS/MICRODADOS/
├── SIM-DATASUS-2004.csv
├── SIM-DATASUS-2005.csv
├── SIM-DATASUS-2006.csv
├── ...
├── SIM-DATASUS-2021.csv
└── SIM-DATASUS-2022.csv
```

**Formato esperado de cada arquivo**:
```csv
sexo,raca_cor,escolaridade,estado_civil,idade,...
1,1,1,1,45
2,2,2,2,67
...
```

---

## 🎨 Visualizações

### 1. Gráfico de Linha (Evolução Geral)
```
Total de Óbitos
    |     ╱╲
    |    ╱  ╲___╱╲
    |___╱        ╲___
    └─────────────────
      2004        2022
```

### 2. Multi-linha (Por Categoria)
```
Óbitos
    | ─── Masculino
    | ─── Feminino
    |
    └──────────────
      2004    2022
```

### 3. Heatmap
```
       2004 2005 2006 ... 2022
Branca  🔴  🟠  🟡 ... 🟢
Preta   🟠  🟡  🟡 ... 🟢
Amarela 🟡  🟡  🟡 ... 🟢
Parda   🔴  🔴  🟠 ... 🟡
```

### 4. Distribuição Etária
```
Óbitos
    |   ╱╲
    |  ╱  ╲___
    | ╱        ╲___
    |╱_____________
    └─────────────
      10 20 30 40 50 60 70 80+
```

---

## 💾 Download de Dados

A aba "Estatísticas Gerais" oferece:

**Colunas disponíveis no CSV**:
- `ano`: Ano do dado
- `total_obitos`: Total geral
- `masculino`: Óbitos homens (se disponível)
- `feminino`: Óbitos mulheres (se disponível)
- `idade_media`: Idade média dos óbitos
- `idade_mediana`: Idade mediana dos óbitos
- `categoria_subcategoria`: Para cada categoria selecionada

**Exemplo de CSV**:
```csv
ano,total_obitos,masculino,feminino,idade_media,idade_mediana
2004,123456,78901,44555,67.45,70
2005,125432,79123,46309,67.89,71
2006,128945,80234,48711,68.12,72
...
2022,145678,92345,53333,70.34,75
```

---

## 🔍 Insights Que Você Pode Descobrir

### 1. Tendências Gerais
- "Óbitos aumentaram 25% entre 2004-2022?"
- "Há aceleração ou desaceleração?"

### 2. Padrões por Sexo
- "Mulheres têm mais óbitos que homens?"
- "A proporção mudou ao longo dos anos?"

### 3. Padrões por Raça/Cor
- "Há disparidades entre raças/cores?"
- "A situação melhorou com o tempo?"

### 4. Envelhecimento Populacional
- "A idade média dos óbitos aumentou?"
- "População ficou mais envelhecida?"

### 5. Mudanças por Educação
- "Pessoas mais educadas têm menos óbitos?"
- "A educação reduziu disparidades?"

---

## ⚠️ Observações Importantes

### Requisitos
- Arquivo SIM-DATASUS para cada ano (2004-2022)
- Formato CSV com colunas esperadas
- Caminho: `//Projetos2/Wrk/SIM-DATASUS/MICRODADOS/SIM-DATASUS-[ano].csv`

### Performance
- Carregamento: ~5-10 segundos para 2004-2022
- Primeira execução: pode ser mais lenta
- Depois: cache automático (próximas 5 min)

### Se Arquivo Não Existir
- Aviso em amarelo: "⚠️ Não encontrados: 2008, 2009..."
- Dados carregados normalmente para outros anos
- Gráficos adaptam-se aos dados disponíveis

---

## 🛠️ Customização

### Mudar Intervalo de Anos
No `app.py`, função `render_comparative_analysis()`:

```python
year_start = st.slider("Ano Inicial", 
                       min_value=2000,  # ← mude aqui
                       max_value=2025,  # ← e aqui
                       value=2010)
```

### Mudar Caminho Base
Em `render_comparative_analysis()`:

```python
base_path = "seu/novo/caminho/aqui"
```

### Adicionar Novo Tipo de Análise
1. Criar nova função em `sim_visualizer.py`
2. Adicionar opção em `st.radio()`
3. Adicionar `elif` em `render_comparative_analysis()`

---

## 📈 Casos de Uso

| Caso | Análise | Função |
|------|---------|--------|
| **Política Pública** | Ver tendências gerais | "Evolução Geral" |
| **Pesquisa** | Analisar disparidades | "Evolução por Categoria" |
| **Visualização** | Identificar padrões | "Heatmap" |
| **Epidemiologia** | Entender grupos etários | "Distribuição Etária" |
| **Relatório** | Exportar dados | "Estatísticas Gerais" + CSV |

---

## ✅ Checklist de Uso

- [ ] Arquivo(s) SIM-DATASUS disponível(is)
- [ ] Executar: `streamlit run app.py`
- [ ] Selecionar modo: "Comparativo (2004-2022)"
- [ ] Definir intervalo de anos
- [ ] Escolher tipo de análise
- [ ] Explorar visualizações
- [ ] (Opcional) Baixar CSV

---

## 🎓 Exemplos de Perguntas que Pode Responder

1. "Quantas pessoas morreram em cada ano?"
2. "Há mais homens ou mulheres nos óbitos?"
3. "A idade média mudou ao longo dos anos?"
4. "Qual raça/cor teve mais óbitos?"
5. "Como a educação se relaciona com óbitos?"
6. "Qual foi a tendência geral 2004-2022?"
7. "Houve mudanças drásticas em algum ano?"
8. "Como os padrões etários evoluíram?"

---

## 📞 Suporte

Se encontrar problemas:
1. Verificar se arquivos existem
2. Verificar caminho correto
3. Verificar permissões de leitura
4. Ver console do Streamlit para mensagens de erro

---

**Última atualização**: 2026-05-13  
**Versão**: 2.0 com Análise Comparativa  
**Status**: ✅ Pronto para Usar
