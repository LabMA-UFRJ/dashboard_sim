-- ============================================================================
-- Carga dos microdados SIM-DATASUS (data/raw/MICRODADOS/SIM-DATASUS-<ano>.csv)
-- para o Oracle.
--
-- Estrategia:
--   1. DIRECTORY apontando para a pasta dos CSVs.
--   2. Uma tabela EXTERNA (MICRODADOS_EXT) que le um CSV por vez (LOCATION
--      trocado dinamicamente dentro do procedimento).
--   3. Procedimento LOAD_MICRODADOS que, para cada ano:
--        - aponta a externa para SIM-DATASUS-<ano>.csv
--        - materializa MICRODADOS_<ano> (CTAS)        -> uma tabela por ano
--      e ao final cria a VIEW unificada MICRODADOS via UNION ALL (sem duplicar
--      os dados em disco; sempre em sincronia com as tabelas por ano).
--
-- Pre-requisitos / privilegios:
--   GRANT CREATE ANY DIRECTORY, CREATE TABLE, CREATE PROCEDURE TO <usuario>;
--   O caminho do DIRECTORY deve ser acessivel pelo SERVIDOR Oracle (nao pelo
--   cliente). Ajuste o caminho abaixo se o banco roda em outra maquina.
-- ============================================================================

-- 1) Diretorio do servidor com os CSVs ---------------------------------------
CREATE OR REPLACE DIRECTORY MICRODADOS_DIR
    AS 'C:\Users\Maia\Documents\GitHub\dashboard_sim\data\raw\MICRODADOS';


-- 2) Tabela externa (landing em texto; todas as colunas como VARCHAR2) -------
--    LOCATION inicial e so um placeholder; o procedimento o substitui por ano.
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE MICRODADOS_EXT';
EXCEPTION
    WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/

CREATE TABLE MICRODADOS_EXT (
    ano                              VARCHAR2(4000),
    sigla_uf                         VARCHAR2(4000),
    sequencial_obito                 VARCHAR2(4000),
    tipo_obito                       VARCHAR2(4000),
    causa_basica                     VARCHAR2(4000),
    data_obito                       VARCHAR2(4000),
    hora_obito                       VARCHAR2(4000),
    naturalidade                     VARCHAR2(4000),
    data_nascimento                  VARCHAR2(4000),
    idade                            VARCHAR2(4000),
    sexo                             VARCHAR2(4000),
    raca_cor                         VARCHAR2(4000),
    estado_civil                     VARCHAR2(4000),
    escolaridade                     VARCHAR2(4000),
    ocupacao                         VARCHAR2(4000),
    codigo_bairro_residencia         VARCHAR2(4000),
    id_municipio_residencia          VARCHAR2(4000),
    local_ocorrencia                 VARCHAR2(4000),
    codigo_bairro_ocorrencia         VARCHAR2(4000),
    id_municipio_ocorrencia          VARCHAR2(4000),
    idade_mae                        VARCHAR2(4000),
    escolaridade_mae                 VARCHAR2(4000),
    ocupacao_mae                     VARCHAR2(4000),
    quantidade_filhos_vivos          VARCHAR2(4000),
    quantidade_filhos_mortos         VARCHAR2(4000),
    gravidez                         VARCHAR2(4000),
    gestacao                         VARCHAR2(4000),
    parto                            VARCHAR2(4000),
    obito_parto                      VARCHAR2(4000),
    morte_parto                      VARCHAR2(4000),
    peso                             VARCHAR2(4000),
    obito_gravidez                   VARCHAR2(4000),
    obito_puerperio                  VARCHAR2(4000),
    assistencia_medica               VARCHAR2(4000),
    exame                            VARCHAR2(4000),
    cirurgia                         VARCHAR2(4000),
    necropsia                        VARCHAR2(4000),
    linha_a                          VARCHAR2(4000),
    linha_b                          VARCHAR2(4000),
    linha_c                          VARCHAR2(4000),
    linha_d                          VARCHAR2(4000),
    linha_ii                         VARCHAR2(4000),
    circunstancia_obito              VARCHAR2(4000),
    acidente_trabalho                VARCHAR2(4000),
    fonte                            VARCHAR2(4000),
    codigo_estabelecimento           VARCHAR2(4000),
    atestante                        VARCHAR2(4000),
    data_atestado                    VARCHAR2(4000),
    tipo_pos                         VARCHAR2(4000),
    data_investigacao                VARCHAR2(4000),
    causa_basica_original            VARCHAR2(4000),
    data_cadastro                    VARCHAR2(4000),
    fonte_investigacao               VARCHAR2(4000),
    data_recebimento                 VARCHAR2(4000),
    causa_basica_pre                 VARCHAR2(4000),
    tipo_obito_ocorrencia            VARCHAR2(4000),
    tipo_morte_ocorrencia            VARCHAR2(4000),
    data_cadastro_informacao         VARCHAR2(4000),
    data_cadastro_investigacao       VARCHAR2(4000),
    id_municipio_svo_iml             VARCHAR2(4000),
    data_recebimento_original        VARCHAR2(4000),
    data_recebimento_original_a      VARCHAR2(4000),
    causa_materna                    VARCHAR2(4000),
    status_do_epidem                 VARCHAR2(4000),
    status_do_nova                   VARCHAR2(4000),
    serie_escolar_falecido           VARCHAR2(4000),
    serie_escolar_mae                VARCHAR2(4000),
    escolaridade_2010                VARCHAR2(4000),
    escolaridade_mae_2010            VARCHAR2(4000),
    escolaridade_falecido_2010_agr   VARCHAR2(4000),
    escolaridade_mae_2010_agr        VARCHAR2(4000),
    semanas_gestacao                 VARCHAR2(4000),
    diferenca_data                   VARCHAR2(4000),
    data_conclusao_investigacao      VARCHAR2(4000),
    data_conclusao_caso              VARCHAR2(4000),
    numero_dias_obito_investigacao   VARCHAR2(4000),
    id_municipio_naturalidade        VARCHAR2(4000),
    descricao_estabelecimento        VARCHAR2(4000),
    crm                              VARCHAR2(4000),
    numero_lote                      VARCHAR2(4000),
    status_codificadora              VARCHAR2(4000),
    codificado                       VARCHAR2(4000),
    versao_sistema                   VARCHAR2(4000),
    versao_scb                       VARCHAR2(4000),
    atestado                         VARCHAR2(4000),
    numero_dias_obito_ficha          VARCHAR2(4000),
    fontes                           VARCHAR2(4000),
    tipo_resgate_informacao          VARCHAR2(4000),
    tipo_nivel_investigador          VARCHAR2(4000),
    numero_dias_informacao           VARCHAR2(4000),
    fontes_informacao                VARCHAR2(4000),
    alt_causa                        VARCHAR2(4000)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY MICRODADOS_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY NEWLINE
        CHARACTERSET AL32UTF8
        SKIP 1                       -- pula o cabecalho
        -- BADFILE/LOGFILE sem nome fixo: o Oracle gera um por CSV de origem,
        -- evitando que o loop por ano sobrescreva o diagnostico anterior.
        FIELDS TERMINATED BY ','
            OPTIONALLY ENCLOSED BY '"'
            LRTRIM
            MISSING FIELD VALUES ARE NULL
        REJECT ROWS WITH ALL NULL FIELDS
    )
    LOCATION ('SIM-DATASUS-2004.csv')   -- placeholder; trocado por LOAD_MICRODADOS
)
REJECT LIMIT UNLIMITED;


-- 3) Procedimento de carga ----------------------------------------------------
CREATE OR REPLACE PROCEDURE LOAD_MICRODADOS (
    p_ano_ini IN PLS_INTEGER DEFAULT 2004,
    p_ano_fim IN PLS_INTEGER DEFAULT 2022
) AS
    v_union  CLOB;
    v_tab    VARCHAR2(30);

    -- Drop silencioso (ignora ORA-00942: tabela inexistente).
    -- Subprogramas locais devem ser declarados APOS as variaveis.
    PROCEDURE drop_if_exists(p_tabela IN VARCHAR2) IS
    BEGIN
        EXECUTE IMMEDIATE 'DROP TABLE ' || p_tabela || ' PURGE';
    EXCEPTION
        WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
    END;
BEGIN
    FOR ano IN p_ano_ini .. p_ano_fim LOOP
        v_tab := 'MICRODADOS_' || ano;

        -- Aponta a tabela externa para o CSV do ano
        EXECUTE IMMEDIATE
            'ALTER TABLE MICRODADOS_EXT LOCATION (''SIM-DATASUS-' || ano || '.csv'')';

        -- (Re)materializa a tabela do ano
        drop_if_exists(v_tab);
        EXECUTE IMMEDIATE
            'CREATE TABLE ' || v_tab || ' AS SELECT * FROM MICRODADOS_EXT';

        DBMS_OUTPUT.PUT_LINE('Carregado: ' || v_tab);

        -- Monta o UNION ALL da tabela unificada
        IF v_union IS NULL THEN
            v_union := 'SELECT * FROM ' || v_tab;
        ELSE
            v_union := v_union || ' UNION ALL SELECT * FROM ' || v_tab;
        END IF;
    END LOOP;

    -- 4) View unificada com todos os anos (UNION ALL das tabelas por ano).
    --    Removemos uma eventual TABLE homonima de execucoes antigas (ORA-00955)
    --    antes do CREATE OR REPLACE VIEW.
    drop_if_exists('MICRODADOS');
    EXECUTE IMMEDIATE 'CREATE OR REPLACE VIEW MICRODADOS AS ' || v_union;
    DBMS_OUTPUT.PUT_LINE('View unificada MICRODADOS criada.');
END LOAD_MICRODADOS;
/


-- 5) Executar a carga ---------------------------------------------------------
-- SET SERVEROUTPUT ON
-- EXEC LOAD_MICRODADOS;                 -- todos os anos (2004..2022)
-- EXEC LOAD_MICRODADOS(2017, 2022);     -- subconjunto de anos
