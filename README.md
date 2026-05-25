# dashboard_sim
Dashboard desenvolvido para consultas e comparativos do Sistema de Informação sobre Mortalidade (SIM)




## **Projeto: Desenvolvimento Streamlit**

**Objetivo e Escopo:**

### Desenvolvimento de Visualização agrupada dos seguintes:

#### Cálculo de mX pelos subgrupos e pop. geral
#### Visualização geral das curvas dos subgrupos
#### subgrupos de interesse: sexo, raça, escolaridade, estado_civil


**Questões:**
1. Consumo via API (SIM)? R: Apenas baixar os dados referentes por recortes (limite de 100MB)
2. Trabalhar em cima dos dados do Censo ou das estimativas?
3. Não foram encontradas estimativas de raça por faixa etária (pesquisar)


| Fonte | Descrição | Nota | Website | 
| :--- | :--- | :--- | :--- |
| BR MS | Estimativas de dados da população por município, sexo, idade | População dividida por recortes de 4 anos | basedosdados.br_ms_populacao.municipio |
| BR MS SIM | Dados referentes à mortalidade (DATASUS) | Boa granularidade | https://basedosdados.org/dataset/br-ms-sim |
| Sidra | Recorte por raça | Boa granularidade, porém somente possui os censos 2022/2010 como ref. | https://sidra.ibge.gov.br/tabela/9606 |


Relatório:

- Até agora temos estimativas que já são suficientes para o calculo mx por sexo e população geral para cada ano. Porém, são retornadas faixas de idade.
- Não foram encontradas estimativas raciais, somente censo especifíco
- Visualizações dos dados DATASUS já foram geradas, igualmente calculo mX. Falta tratar como será determinado o denominador (pop geral) para cada subgrupo
