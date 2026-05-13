# 🚀 GUIA DE EXECUÇÃO - SIM-DATASUS Analysis

## ⚡ Quick Start (Rápido)

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar app
streamlit run app.py
```

O app abrirá automaticamente em `http://localhost:8501`

---

## 📋 Opções de Execução

### Opção 1: Streamlit Direto ⭐ (Recomendado)
```bash
streamlit run app.py
```

**Vantagens**:
- ✅ Rápido e simples
- ✅ Reload automático ao editar código
- ✅ Dashboard interativo completo

**Resultado**: Abre navegador em `http://localhost:8501`

---

### Opção 2: Script Python
```bash
python run_sim_analysis.py --app
```

**Características**:
- ✅ Verifica dependências automaticamente
- ✅ Mensagens de erro mais descritivas
- ✅ Suporte a argumentos de linha de comando

**Argumentos disponíveis**:
```bash
python run_sim_analysis.py --help
```

Exemplos:
```bash
# Verificar dependências
python run_sim_analysis.py --check

# Instalar dependências
python run_sim_analysis.py --install

# Abrir notebook
python run_sim_analysis.py --notebook

# Executar app
python run_sim_analysis.py --app
```

---

### Opção 3: Jupyter Notebook (Desenvolvimento)
```bash
jupyter notebook main.ipynb
```

**Uso**: Para desenvolver e testar funções

---

## 📦 Gestão de Dependências

### Instalar Tudo
```bash
pip install -r requirements.txt
```

### Instalar Apenas Essencial
```bash
pip install pandas streamlit plotly
```

### Verificar Instalação
```bash
python run_sim_analysis.py --check
```

### Resultado esperado:
```
✅ Verificando dependências...

  ✓ pandas          - Manipulação de dados
  ✓ streamlit       - Framework web
  ✓ plotly          - Gráficos interativos

✅ Todas as dependências estão instaladas!
```

---

## 🎯 Fluxo de Execução Completo

```
$ streamlit run app.py

  Welcome to Streamlit!

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501

         ↓
    App Loaded
         ↓
    Sidebar: "Configurações"
    └─ Input: Caminho do arquivo
         ↓
    Arquivo Carregado: ✅ X,XXX registros
         ↓
    Sidebar: "Tipo de Visualização"
    ├─ Resumo Geral
    ├─ Por Categoria
    ├─ Por Idade
    ├─ Comparações
    └─ Detalhes
         ↓
    Visualização Renderizada
```

---

## 🔧 Troubleshooting

### ❌ "streamlit: command not found"
```bash
pip install streamlit
```

### ❌ "No module named 'pandas'"
```bash
pip install pandas
```

### ❌ "Arquivo não encontrado"
1. Verificar caminho no sidebar
2. Usar caminho absoluto: `C:\Users\...\arquivo.csv`
3. Verificar permissões de acesso

### ❌ App abre mas fica vazio
1. Verificar se arquivo CSV é válido
2. Verificar se tem as colunas esperadas
3. Consultar console para erros

### ❌ Porta 8501 já em uso
```bash
streamlit run app.py --logger.level=debug --server.port 8502
```

---

## 💻 Ambiente Recomendado

### Sistema Operacional
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 18.04+)

### Python
```bash
python --version
# Esperado: Python 3.8 ou superior
```

### Verificar Python
```bash
python -m streamlit --version
```

### Atualizar pip
```bash
pip install --upgrade pip
```

---

## 📝 Estrutura de Dados Esperada

Arquivo CSV com colunas:

```csv
sexo,raca_cor,escolaridade,estado_civil,idade
1,1,1,1,45
2,2,2,2,67
1,3,3,3,52
...
```

**Colunas Obrigatórias** (mínimo):
- `sexo`: 1-2
- `raca_cor`: 1-5
- `escolaridade`: 1-5
- `estado_civil`: 1-5
- `idade`: número

---

## 📊 Arquivos Importantes

```
dashboard_sim/
├── app.py                    ← Main app (EXECUTE ESTE)
├── main.ipynb               ← Notebook desenvolvimento
├── requirements.txt         ← Dependências
├── run_sim_analysis.py      ← Script runner
├── src/
│   └── core/
│       └── sim_visualizer.py ← Funções de visualização
├── INSTRUCOES_SIM.md        ← Documentação completa
├── RESUMO_ALTERACOES.md     ← O que foi alterado
└── GUIA_EXECUCAO.md         ← Este arquivo
```

---

## 🎓 Exemplos de Uso

### Exemplo 1: Executar com arquivo padrão
```bash
streamlit run app.py
```
Será usado o caminho padrão do sidebar

### Exemplo 2: Mudar arquivo na interface
1. Abrir app
2. No sidebar, editar "Caminho do arquivo SIM-DATASUS"
3. Colocar novo caminho
4. App recarrega automaticamente

### Exemplo 3: Usar em produção
```bash
streamlit run app.py --logger.level=error --server.headless true
```

---

## 🔐 Segurança

### Proteger Caminho do Arquivo
```python
# Em app.py, modificar:
sim_data_path = st.sidebar.text_input(
    "Arquivo",
    value="C:\\Dados\\SIM-2020.csv",
    disabled=True  # ← Deixa imutável
)
```

### Validar Caminho
```python
from pathlib import Path
if not Path(sim_data_path).exists():
    st.error("Arquivo inválido")
```

---

## 📈 Performance

### Para arquivos > 100MB
1. Filtrar por período antes de carregar
2. Usar subsample dos dados
3. Implementar cache:

```python
@st.cache_data
def load_sim_data(file_path):
    return pd.read_csv(file_path)
```

### Monitorar consumo
```bash
# Terminal
streamlit run app.py --logger.level=debug
```

---

## 🆘 Suporte

Se encontrar problemas:

1. **Verificar logs**:
   ```bash
   # No terminal onde app foi executado
   # Procurar por mensagens de erro
   ```

2. **Consultar documentação**:
   - `INSTRUCOES_SIM.md` - Funcionalidades completas
   - `RESUMO_ALTERACOES.md` - Estrutura do código

3. **Testar componentes**:
   ```bash
   python -c "import pandas; print(pandas.__version__)"
   python -c "import streamlit; print(streamlit.__version__)"
   ```

---

## 📞 Contato & Documentação

- **Código Principal**: `app.py`
- **Visualizações**: `src/core/sim_visualizer.py`
- **Desenvolvimento**: `main.ipynb`
- **Dados Exemplo**: Consultar README.md

---

**Última Atualização**: 2026-05-13  
**Versão**: 1.0  
**Status**: ✅ Pronto para Usar
