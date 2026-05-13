# 📊 Análise de Mortalidade SIM-DATASUS

## Descrição
Aplicação Streamlit para análise interativa de dados de mortalidade do **Sistema de Informação sobre Mortalidade (SIM-DATASUS)**.

## 🎯 Funcionalidades

### 1. **Resumo Geral**
- Métricas principais: Total de óbitos, distribuição por sexo, idade média
- Gráficos de todas as categorias em um painel

### 2. **Análise por Categoria**
- Visualizar óbitos por:
  - 🔴 Raça/Cor
  - 👥 Sexo
  - 📚 Escolaridade
  - 💍 Estado Civil
- Tabela com estatísticas e percentuais

### 3. **Análise por Idade**
- Gráfico geral de óbitos por idade
- Análise desagregada por:
  - Sexo
  - Raça/Cor
  - Escolaridade
  - Estado Civil

### 4. **Comparações**
- Comparar distribuição entre duas categorias diferentes
- Gráficos lado-a-lado

### 5. **Detalhes**
- Visualizar colunas do dataset
- Dimensões dos dados
- Amostra dos primeiros registros
- Estatísticas descritivas

## 🚀 Como Executar

### Pré-requisitos
```bash
pip install streamlit pandas plotly
```

### Executar o App
```bash
streamlit run app.py
```

O aplicativo abrirá em `http://localhost:8501`

## 📝 Arquivo de Dados

O app espera um arquivo CSV com as seguintes colunas (mínimo):
- `sexo`: 1 (Masculino), 2 (Feminino)
- `raca_cor`: 1-5 (Branca, Preta, Amarela, Parda, Indígena)
- `escolaridade`: 1-5 (Nenhuma, 1-3 anos, 4-7 anos, 8-11 anos, 12+)
- `estado_civil`: 1-5 (Solteiro, Casado, Viúvo, Divorciado, União Consensual)
- `idade`: Idade em anos

## 🏗️ Estrutura do Código

### Funções Principais

#### `load_sim_data(file_path: str) -> Optional[pd.DataFrame]`
- Carrega dados do arquivo SIM-DATASUS
- Tratamento de erros integrado

#### `render_summary_metrics(data: pd.DataFrame) -> None`
- Renderiza 4 métricas principais
- Adapta-se aos dados disponíveis

#### `render_category_view(data: pd.DataFrame) -> None`
- Visualização por categoria selecionada
- Inclui gráfico e tabela de estatísticas

#### `render_age_view(data: pd.DataFrame) -> None`
- 5 visualizações diferentes por idade
- Usa mapa de função para elegância

#### `render_comparison_view(data: pd.DataFrame) -> None`
- Compara duas categorias selecionadas
- Seletores independentes com keys

#### `render_details_view(data: pd.DataFrame) -> None`
- Análise exploratória completa
- Amostra de dados e estatísticas

#### `render_sim_dashboard(sim_data_path: str) -> None`
- Orquestra todo o dashboard
- Seleção de tipo de visualização
- Tratamento de erros centralizado

### Dicionários

**DICTIONARY_COLORS**: Cores em hexadecimal para cada categoria
```python
{
    'sexo': {'1': '#00FFFF', '2': '#FF00FF'},
    'raca_cor': {'1': '#006400', '2': '#000080', ...},
    ...
}
```

**DICTIONARY_LABELS**: Rótulos em português para cada código
```python
{
    'sexo': {'1': 'Masculino', '2': 'Feminino'},
    'raca_cor': {'1': 'Branca', '2': 'Preta', ...},
    ...
}
```

## 📊 Visualizações Utilizadas

- **Plotly Express**: Gráficos interativos
  - `px.bar()`: Gráficos de barras
  - `px.line()`: Gráficos de linhas
- **Streamlit Components**:
  - `st.metric()`: Métricas principais
  - `st.columns()`: Layout em colunas
  - `st.dataframe()`: Tabelas interativas

## 🔧 Customização

### Alterar Caminho Padrão do Arquivo
Editar em `app.py`, função `main()`:
```python
sim_data_path = st.sidebar.text_input(
    "Caminho do arquivo SIM-DATASUS",
    value="SEU_CAMINHO_AQUI",  # ← Alterar aqui
    help="Insira o caminho completo do arquivo CSV..."
)
```

### Adicionar Novas Categorias
1. Atualizar `DICTIONARY_COLORS` em `sim_visualizer.py`
2. Atualizar `DICTIONARY_LABELS` em `sim_visualizer.py`
3. Adicionar à lista de seletores nas funções

## 📱 Interface

- **Largura**: Layout wide para melhor aproveitamento de espaço
- **Ícone**: 📊 (emoji de gráfico)
- **Sidebar**: Configurações e seleção de visualização
- **Responsividade**: Adapta-se a diferentes tamanhos de tela

## ⚠️ Tratamento de Erros

- Arquivo não encontrado: Mensagem de erro clara
- Dados inválidos: Métrica exibe "N/A"
- Colunas ausentes: Validação antes de processamento

## 📈 Performance

- Cache de dados com `st.cache_data` (quando necessário)
- Lazy loading de visualizações
- Processamento eficiente com pandas/plotly

## 🔗 Relacionado

- **Notebook**: `main.ipynb` - Desenvolvimento e testes
- **Módulo**: `src/core/sim_visualizer.py` - Funções de visualização
- **Config**: `DICTIONARY_COLORS` e `DICTIONARY_LABELS` - Dicionários centralizados

## 💡 Dicas

1. **Performance**: Para arquivos grandes (>1M registros), considere filtrar por período
2. **Cores**: Personalize `DICTIONARY_COLORS` para seu esquema visual
3. **Rótulos**: Atualize `DICTIONARY_LABELS` conforme necessário
4. **Temas**: Streamlit suporta dark mode (configuração do browser)

---

**Última atualização**: 2026-05-13
