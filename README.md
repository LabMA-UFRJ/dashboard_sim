# dashboard_sim
Dashboard desenvolvido para consultas e comparativos do Sistema de Informação sobre Mortalidade (SIM)

## **Projeto: Comparativo de Mortalidade (LabMA / DataSUS / IBGE)**

**Objetivo e Escopo:**
Investigar a motivação por trás da mortalidade acentuada residual no período pós-COVID-19, buscando determinar se este fenômeno é decorrente diretamente da própria doença.

**Plano de Trabalho:**

1. **Paralelos:** Traçar paralelos comparativos entre as diferentes bases de dados para identificar correlações de padrão da distribuição de mortes BR-EMS x MS (DATASUS).
2. **Definição Metodológica e Inferência:** Consulta como definir a abordagem técnica mais adequada e, a partir disso, realizar as inferências necessárias para o encaminhamento do estudo. Busca e uso de artigos e trabalhos similares.

## Análise

**Microdados** 


Microdados do Sistema de Informações sobre Mortalidade (SIM) do Ministério da Saúde. Os valores para o ano de 2022 representam uma prévia dos dados. 

- Tamanho: (5.83 GB)
 

| | Nome | Precisa de tradução | Descrição | Tipo No BigQuery | Cobertura Temporal | Unidade De Medida | Contém Dados Sensíveis (LGPD) | Observações |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | ano | Não | Ano | INT64 | 1996 - 2022 | yearyearyear | Não informado | Não informado |
| | sigla_uf | Sim | Sigla da Unidade da Federação | STRING | 1996 - 2022 | Não informado | Não informado | Não informado |
| | sequencial_obito | Não | Sequencial do Óbito | STRING | 1996 - 2022 | Não informado | Não informado | Não informado |
| | tipo_obito | Sim | Tipo do Óbito | STRING | 1996 - 2022 | Não informado | Não informado | Não informado |
| | causa_basica | Sim | Causa Básica (CID-10) | STRING | 1996 - 2022 | Não informado | Não informado | Não informado |
| | data_obito | Não | Data do Óbito | DATE | 1996 - 2022 | Não informado | Não informado | Não informado |
| | hora_obito | Não | Hora do Óbito | TIME | Não informado | Não informado | Não informado | Não informado |
| | naturalidade | Sim | Naturalidade | STRING | 1996 - 2022 | Não informado | Não informado | Não informado |
| | data_nascimento | Não | Data de Nascimento | DATE | 1996 - 2022 | Não informado | Não informado | Não informado |
| | idade | Não | Idade | FLOAT64 | 1996 - 2022 | Não informado | Não informado | Não informado |
| | sexo | Sim | Sexo | STRING | 1996 - 2022 | Não informado | Não informado | Não informado |
| | raca_cor | Sim | Raça ou Cor | STRING | 1996 - 2022 | Não informado | Não informado | Não informado |
| | estado_civil | Sim | Estado Civil | STRING | 1996 - 2022 | Não informado | Não informado | Não informado |
| | escolaridade | Sim | Escolaridade | STRING | 1996 - 2022 | Não informado | Não informado | Não informado |
| | ocupacao | Não | Ocupação Habitual e Ramo de Atividade | STRING | 1996 - 2022 | Não informado | Não informado | Não informado |
| | codigo_bairro_residencia | Não | Código do Bairro de Residência | STRING | Não informado | Não informado | Não informado | Não informado |
| | id_municipio_residencia | Sim | ID Município de Residência - IBGE 7 Dígitos | STRING | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | local_ocorrencia | Sim | Local de Ocorrência | STRING | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | codigo_bairro_ocorrencia | Não | Código do Bairro de Ocorrência | STRING | 2006 - 2010 | Não informado | Não informado | Não informado | Não informado |
| | id_municipio_ocorrencia | Sim | ID Município de Ocorrência - IBGE 7 Dígitos | STRING | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | idade_mae | Não | Idade da Mãe | INT64 | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | escolaridade_mae | Sim | Escolaridade da Mãe | STRING | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | ocupacao_mae | Não | Ocupação da Mãe | STRING | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | quantidade_filhos_vivos | Não | Quantidade de Filhos Vivos | INT64 | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | quantidade_filhos_mortos | Não | Quantidade de Filhos Mortos | INT64 | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | gravidez | Sim | Tipo da Gravidez | STRING | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | gestacao | Sim | Faixa de Semanas de Gestação | STRING | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | parto | Sim | Tipo de Parto | STRING | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | obito_parto | Sim | Como Foi a Morte em Relação ao Parto | STRING | Não informado | Não informado | Não informado | Não informado |
| | morte_parto | Sim | Morte no Parto | STRING | Não informado | Não informado | Não informado | Não informado |
| | peso | Não | Peso (g) | INT64 | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | obito_gravidez | Sim | Óbito na Gravidez | STRING | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | obito_puerperio | Sim | Óbito no Puerperio | STRING | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | assistencia_medica | Sim | Assistência Médica | STRING | Não informado | Não informado | Não informado | Não informado |
| | exame | Sim | Exame | STRING | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | cirurgia | Sim | Cirurgia | STRING | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | necropsia | Sim | Necrópsia | STRING | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | linha_a | Não | CIDs informados na Linha A da DO | STRING | Não informado | Não informado | Não informado | Não informado |
| | linha_b | Não | CIDs informados na Linha B da DO | STRING | Não informado | Não informado | Não informado | Não informado |
| | linha_c | Não | CIDs informados na Linha C da DO | STRING | Não informado | Não informado | Não informado | Não informado |
| | linha_d | Não | CIDs informados na Linha D da DO | STRING | Não informado | Não informado | Não informado | Não informado |
| | linha_ii | Não | CIDs informados na Parte II da DO | STRING | Não informado | Não informado | Não informado | Não informado |
| | circunstancia_obito | Sim | Circunstância do Óbito | STRING | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | acidente_trabalho | Sim | Acidente de Trabalho | STRING | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | fonte | Sim | Fonte da Informação | STRING | 1996 - 2022 | Não informado | Não informado | Não informado | Não informado |
| | codigo_estabelecimento | Não | Código do Estabelecimento | STRING | Não informado | Não informado | Não informado | Não informado |
| | atestante | Sim | Indica se o médico que assina atendeu o paciente | STRING | Não informado | Não informado | Não informado | Não informado |
| | data_atestado | Não | Data do Atestado | DATE | Não informado | Não informado | Não informado | Não informado |
| | tipo_pos | Sim | Óbito Investigado | STRING | Não informado | Não informado | Não informado | Não informado |
| | data_investigacao | Não | Data da Investigação | DATE | Não informado | Não informado | Não informado | Não informado |
| | causa_basica_original | Sim | Causa Básica Original | STRING | Não informado | Não informado | Não informado | Não informado |
| | data_cadastro | Não | Data do Cadastro | DATE | Não informado | Não informado | Não informado | Não informado |
| | fonte_investigacao | Sim | Fonte de Investigação | STRING | Não informado | Não informado | Não informado | Não informado |
| | data_recebimento | Não | Data do Recebimento | DATE | Não informado | Não informado | Não informado | Não informado |
| | causa_basica_pre | Sim | Causa Básica Informada Antes da Resseleção | STRING | 2006 - 2010 | Não informado | Não informado | Não informado | Não informado |
| | tipo_obito_ocorrencia | Sim | Tipo de Ocorrência do Óbito | STRING | Não informado | Não informado | Não informado | Não informado |
| | tipo_morte_ocorrencia | Sim | Tipo de Ocorrência da Morte | STRING | Não informado | Não informado | Não informado | Não informado |
| | data_cadastro_informacao | Não | Data do Cadastro da Informação | DATE | Não informado | Não informado | Não informado | Não informado |
| | data_cadastro_investigacao | Não | Data do Cadastro da Investigação | DATE | Não informado | Não informado | Não informado | Não informado |
| | id_municipio_svo_iml | Sim | ID Município SVO ou IML - IBGE 7 Dígitos | STRING | Não informado | Não informado | Não informado | Não informado |
| | data_recebimento_original | Não | Data de Recebimento do Original | DATE | Não informado | Não informado | Não informado | Não informado |
| | data_recebimento_original_a | Não | Data de Recebimento do Original A | DATE | 2011 - 2011 | Não informado | Não informado | Não informado | Não informado |
| | causa_materna | Sim | Causa Externa Associada a uma Causa Materna | STRING | Não informado | Não informado | Não informado | Não informado |
| | status_do_epidem | Sim | Status de DO Epidemiológica | STRING | Não informado | Não informado | Não informado | Não informado |
| | status_do_nova | Sim | Status de DO Nova | STRING | Não informado | Não informado | Não informado | Não informado |
| | serie_escolar_falecido | Não | Série Escolar do Falecido | INT64 | Não informado | Não informado | Não informado | Não informado |
| | serie_escolar_mae | Não | Série Escolar da Mãe | INT64 | Não informado | Não informado | Não informado | Não informado |
| | escolaridade_2010 | Sim | Escolaridade 2010 | STRING | Não informado | Não informado | Não informado | Não informado |
| | escolaridade_mae_2010 | Sim | Escolaridade 2010 da Mãe | STRING | Não informado | Não informado | Não informado | Não informado |
| | escolaridade_falecido_2010_agr | Sim | Escolaridade 2010 Agregada do(a) Falecido(a) | STRING | 2012 - 2012 | Não informado | Não informado | Não informado | Não informado |
| | escolaridade_mae_2010_agr | Sim | Escolaridade 2010 Agregada da Mãe | STRING | 2012 - 2012 | Não informado | Não informado | Não informado | Não informado |
| | semanas_gestacao | Não | Semanas de Gestação | INT64 | Não informado | Não informado | Não informado | Não informado |
| | diferenca_data | Não | Diferença Entre a Data de Óbito e Data do Recebimento Original da DO | INT64 | Não informado | Não informado | Não informado | Não informado |
| | data_conclusao_investigacao | Não | Data de Conclusão da Investigação | DATE | Não informado | Não informado | Não informado | Não informado |
| | data_conclusao_caso | Não | Data de Conclusão do Caso | DATE | 2012 - 2012 | Não informado | Não informado | Não informado | Não informado |
| | numero_dias_obito_investigacao | Não | Número de Dias Entre a Data do Óbito e a Data Declarada para a Conclusão da Investigação | INT64 | 2012 - 2015 | Não informado | Não informado | Não informado | Não informado |
| | id_municipio_naturalidade | Sim | ID Município Naturalidade - IBGE 7 Dígitos | STRING | Não informado | Não informado | Não informado | Não informado |
| | descricao_estabelecimento | Não | Descrição do Estabelecimento | STRING | 2014 - 2014 | Não informado | Não informado | Não informado | Não informado |
| | crm | Não | Número no Conselho Regional de Medicina (CRM) | STRING | 2014 - 2018 | Não informado | Não informado | Não informado | Não informado |
| | numero_lote | Não | Número do Lote | STRING | Não informado | Não informado | Não informado | Não informado |
| | status_codificadora | Sim | Status de Instalação de Codificadora | STRING | Não informado | Não informado | Não informado | Não informado |
| | codificado | Sim | Codificado | STRING | Não informado | Não informado | Não informado | Não informado |
| | versao_sistema | Não | Versão do Sistema | STRING | Não informado | Não informado | Não informado | Não informado |
| | versao_scb | Não | Versão do Seletor de Causa Básica | STRING | Não informado | Não informado | Não informado | Não informado |
| | atestado | Não | CIDs Informados no Atestado | STRING | Não informado | Não informado | Não informado | Não informado |
| | numero_dias_obito_ficha | Não | Número de Dias Entre a Data do Óbito e a Data do Cadastro da Ficha Síntese de Investigação no Módulo | INT64 | Não informado | Não informado | Não informado | Não informado |
| | fontes | Não | Fontes | STRING | Não informado | Não informado | Não informado | Não informado |
| | tipo_resgate_informacao | Sim | A Investigação Permitiu o Resgate de Alguma Causa de Óbito Não Informado, ou a Correção de Alguma Antes Informada? | STRING | Não informado | Não informado | Não informado | Não informado |
| | tipo_nivel_investigador | Sim | Tipo de Nível Investigador | STRING | Não informado | Não informado | Não informado | Não informado |
| | numero_dias_informacao | Não | Número de Dias Informação | INT64 | 2014 - 2014 | Não informado | Não informado | Não informado | Não informado |
| | fontes_informacao | Não | Fontes Informação | STRING | 2014 - 2014 | Não informado | Não informado | Não informado | Não informado |
| | alt_causa | Sim | Alt. Causa | STRING | Não informado | Não informado | Não informado | Não informado |



**Notas**
- **U09.9 (Condição pós-COVID-19):** É o código principal da Organização Mundial da Saúde (OMS) para identificar estados que ocorrem após a fase aguda. No Brasil, o Ministério da Saúde utiliza este código ou o B94.8 (sequelas de outras doenças infecciosas) para monitorar óbitos tardios.
- **U10.9 (Síndrome Inflamatória Multissistêmica):** Usado principalmente quando a morte decorre de uma resposta inflamatória grave tardia associada ao vírus.

**Dúvidas:**
1. Quais CID's são relevantes para se considerar uma morte decorrente de complicações da COVID?

**Links:**

1. Website: https://basedosdados.org/dataset/br-ms-sim
2. Github: https://github.com/basedosdados/mais/tree/master/bases/br_ms_sim
