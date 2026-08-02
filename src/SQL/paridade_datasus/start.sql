-- ============================================================================
-- Pipeline de paridade DATASUS x CNIS/SA, reunido em um unico procedimento.
--
-- Cria, na ordem de dependencia:
--   1. sa_mor_sob                  (view)  <- dados.sa_mor / dados.sa_sob
--   2. cnis_sisobi_dt_obito        (view)  <- CNIS25.CNIS_2025_UNIFICADO
--   3. cnis_sa_cpf_sexo_datanasc   (view)  \
--      cnis_sa_cpf_sexo            (view)   > join de (1) e (2)
--      cnis_sa_only_cpf            (view)  /
--   4. MICRODADOS_RESUMIDO         (table) <- MICRODADOS
--   5. cnis_sa_datasus_comUF       (view)  \  join de cnis_sa_cpf_sexo_datanasc
--      cnis_sa_datasus_semUF       (view)  /  com MICRODADOS_RESUMIDO
--
-- Formatos das fontes (conferidos no banco):
--   SA        cpf VARCHAR2(11) com zeros a esquerda; data_nasc 'YYYYMM' (sem dia);
--             sexo 'M'/'F'
--   CNIS25    cpf NUMBER; dt_nascimento/dt_obito VARCHAR2 'DD/MM/YYYY';
--             cs_sexo NUMBER (1=M, 3=F); uf_residencia sigla
--   MICRODADOS data_nascimento/data_obito VARCHAR2 'YYYY-MM-DD'; sexo '1'=M, '2'=F
-- As datas sao normalizadas para 'YYYYMMDD' (ou 'YYMM', quando o SA so tem
-- ano+mes) antes de comparar, e o cpf do CNIS e formatado com LPAD para casar
-- com o VARCHAR2 do SA.
--
-- DDL dentro de PL/SQL exige SQL dinamico (EXECUTE IMMEDIATE). As views usam
-- CREATE OR REPLACE e a tabela e recriada, entao o procedimento e re-executavel.
-- Rodar com:  SET SERVEROUTPUT ON;  EXEC cnis_sa_datasus;
-- ============================================================================
CREATE OR REPLACE PROCEDURE cnis_sa_datasus AS

    -- Drop silencioso (ignora ORA-00942: objeto inexistente)
    PROCEDURE drop_table_if_exists(p_tabela IN VARCHAR2) IS
    BEGIN
        EXECUTE IMMEDIATE 'DROP TABLE ' || p_tabela || ' PURGE';
    EXCEPTION
        WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
    END;

BEGIN
    -- 1) View base SA (mortos + sobreviventes) -------------------------------
    EXECUTE IMMEDIATE q'[
        create or replace view sa_mor_sob as (
        select mot_saida, data_nasc, cpf, sexo, dat_evento, data_aviso, emp, produto
        from dados.sa_mor
        where ref_info in ('2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021','2022')
          and (mot_saida = '100' or mot_saida = '200' or mot_saida = '300')
        union
        select mot_saida, data_nasc, cpf, sexo, dat_evento, data_aviso, emp, produto
        from dados.sa_sob
        where ref_info in ('2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021','2022')
          and (mot_saida = '100' or mot_saida = '200' or mot_saida = '300'))
    ]';
    DBMS_OUTPUT.PUT_LINE('view sa_mor_sob criada.');

    -- 2) View CNIS com data de obito consolidada -----------------------------
    EXECUTE IMMEDIATE q'[
        create or replace view cnis_sisobi_dt_obito as
        select t.*, t.DT_OBITO as dt_data_obito
        from CNIS25.CNIS_2025_UNIFICADO t
    ]';
    DBMS_OUTPUT.PUT_LINE('view cnis_sisobi_dt_obito criada.');

    -- 3a) Join SA x CNIS por cpf + sexo + data de nascimento -----------------
    -- O SA so tem ano+mes de nascimento, entao a chave de data e 'YYMM'.
    EXECUTE IMMEDIATE q'[
        create or replace view cnis_sa_cpf_sexo_datanasc as
        select
            s.cpf, s.sexo, s.dat_evento, s.data_aviso, s.emp, s.produto,
            c.dt_nascimento, c.dt_data_obito, c.municipio_residencia,
            c.uf_residencia, c.escolaridade
        from (
                select cpf, sexo, substr(data_nasc,3,4) as data_nasc1,
                       data_nasc, dat_evento, data_aviso, emp, produto
                from sa_mor_sob
             ) s
        inner join (
                select lpad(to_char(cpf),11,'0') as cpf, cs_sexo,
                       substr(dt_nascimento,9,2) || substr(dt_nascimento,4,2) as data_nasc2,
                       dt_nascimento, dt_data_obito, municipio_residencia,
                       uf_residencia, escolaridade
                from cnis_sisobi_dt_obito
             ) c
        on s.cpf = c.cpf
        and s.sexo = case when c.cs_sexo = 3 then 'F' when c.cs_sexo = 1 then 'M' end
        and s.data_nasc1 = c.data_nasc2
    ]';
    DBMS_OUTPUT.PUT_LINE('view cnis_sa_cpf_sexo_datanasc criada.');

    -- 3b) Join SA x CNIS por cpf + sexo --------------------------------------
    EXECUTE IMMEDIATE q'[
        create or replace view cnis_sa_cpf_sexo as
        select
            s.cpf, s.sexo, s.dat_evento, s.data_aviso, s.emp, s.produto,
            c.dt_nascimento, c.dt_data_obito, c.municipio_residencia,
            c.uf_residencia, c.escolaridade
        from (
                select cpf, sexo, data_nasc, dat_evento, data_aviso, emp, produto
                from sa_mor_sob
             ) s
        inner join (
                select lpad(to_char(cpf),11,'0') as cpf, cs_sexo, dt_nascimento,
                       dt_data_obito, municipio_residencia, uf_residencia, escolaridade
                from cnis_sisobi_dt_obito
             ) c
        on s.cpf = c.cpf
        and s.sexo = case when c.cs_sexo = 3 then 'F' when c.cs_sexo = 1 then 'M' end
    ]';
    DBMS_OUTPUT.PUT_LINE('view cnis_sa_cpf_sexo criada.');

    -- 3c) Join SA x CNIS apenas por cpf --------------------------------------
    EXECUTE IMMEDIATE q'[
        create or replace view cnis_sa_only_cpf as
        select
            s.cpf, s.sexo, s.dat_evento, s.data_aviso, s.emp, s.produto,
            c.dt_nascimento, c.dt_data_obito, c.municipio_residencia,
            c.uf_residencia, c.escolaridade
        from (
                select cpf, sexo, data_nasc, dat_evento, data_aviso, emp, produto
                from sa_mor_sob
             ) s
        inner join (
                select lpad(to_char(cpf),11,'0') as cpf, cs_sexo, dt_nascimento,
                       dt_data_obito, municipio_residencia, uf_residencia, escolaridade
                from cnis_sisobi_dt_obito
             ) c
        on s.cpf = c.cpf
    ]';
    DBMS_OUTPUT.PUT_LINE('view cnis_sa_only_cpf criada.');

    -- 4) Tabela resumida dos microdados DATASUS ------------------------------
    drop_table_if_exists('MICRODADOS_RESUMIDO');
    EXECUTE IMMEDIATE q'[
        CREATE TABLE MICRODADOS_RESUMIDO AS
        select data_nascimento, data_obito, sexo, ocupacao, escolaridade_2010, causa_basica,
               estado_civil, raca_cor, id_municipio_residencia, status_do_epidem, naturalidade, sigla_uf
        from MICRODADOS
    ]';
    DBMS_OUTPUT.PUT_LINE('tabela MICRODADOS_RESUMIDO criada.');

    -- 5a) Paridade DATASUS x CNIS/SA COM filtro de UF ------------------------
    -- Datas normalizadas para 'YYYYMMDD' dos dois lados.
    EXECUTE IMMEDIATE q'[
        create or replace view cnis_sa_datasus_comUF as
        select
            c.cpf, c.sexo, c.municipio_residencia, c.uf_residencia, c.escolaridade,
            c.dat_evento, c.data_aviso, c.emp, c.produto,
            b.data_nascimento, b.ocupacao, b.escolaridade_2010, b.causa_basica,
            b.naturalidade, b.estado_civil, b.raca_cor, b.id_municipio_residencia,
            b.status_do_epidem, b.sigla_uf, b.data_obito
        from (
                select cpf, sexo, dt_nascimento, dt_data_obito, municipio_residencia,
                    uf_residencia, escolaridade,
                    substr(dt_nascimento,7,4) || substr(dt_nascimento,4,2) || substr(dt_nascimento,1,2) as data_nasc2,
                    substr(dt_data_obito,7,4) || substr(dt_data_obito,4,2) || substr(dt_data_obito,1,2) as data_obito2,
                    dat_evento, data_aviso, emp, produto
                from cnis_sa_cpf_sexo_datanasc) c
        inner join (
                select data_nascimento, data_obito, sexo, ocupacao, escolaridade_2010, causa_basica,
                    naturalidade, estado_civil, raca_cor, id_municipio_residencia, status_do_epidem, sigla_uf,
                    substr(data_nascimento,1,4) || substr(data_nascimento,6,2) || substr(data_nascimento,9,2) as data_nasc1,
                    substr(data_obito,1,4) || substr(data_obito,6,2) || substr(data_obito,9,2) as data_obito1
                from microdados_resumido) b
        on b.sexo = case when c.sexo = 'F' then '2' when c.sexo = 'M' then '1' end
        and c.data_nasc2 = b.data_nasc1
        and c.data_obito2 = b.data_obito1
        and c.uf_residencia = b.sigla_uf
    ]';
    DBMS_OUTPUT.PUT_LINE('view cnis_sa_datasus_comUF criada.');

    -- 5b) Paridade DATASUS x CNIS/SA SEM filtro de UF ------------------------
    EXECUTE IMMEDIATE q'[
        create or replace view cnis_sa_datasus_semUF as
        select
            c.cpf, c.sexo, c.municipio_residencia, c.uf_residencia, c.escolaridade,
            c.dat_evento, c.data_aviso, c.emp, c.produto,
            b.data_nascimento, b.ocupacao, b.escolaridade_2010, b.causa_basica,
            b.naturalidade, b.estado_civil, b.raca_cor, b.id_municipio_residencia,
            b.status_do_epidem, b.data_obito
        from (
                select cpf, sexo, dt_nascimento, dt_data_obito, municipio_residencia,
                    uf_residencia, escolaridade,
                    substr(dt_nascimento,7,4) || substr(dt_nascimento,4,2) || substr(dt_nascimento,1,2) as data_nasc2,
                    substr(dt_data_obito,7,4) || substr(dt_data_obito,4,2) || substr(dt_data_obito,1,2) as data_obito2,
                    dat_evento, data_aviso, emp, produto
                from cnis_sa_cpf_sexo_datanasc) c
        inner join (
                select data_nascimento, data_obito, sexo, ocupacao, escolaridade_2010, causa_basica,
                    estado_civil, raca_cor, naturalidade, id_municipio_residencia, status_do_epidem,
                    substr(data_nascimento,1,4) || substr(data_nascimento,6,2) || substr(data_nascimento,9,2) as data_nasc1,
                    substr(data_obito,1,4) || substr(data_obito,6,2) || substr(data_obito,9,2) as data_obito1
                from microdados_resumido) b
        on b.sexo = case when c.sexo = 'F' then '2' when c.sexo = 'M' then '1' end
        and c.data_nasc2 = b.data_nasc1
        and c.data_obito2 = b.data_obito1
    ]';
    DBMS_OUTPUT.PUT_LINE('view cnis_sa_datasus_semUF criada.');

    DBMS_OUTPUT.PUT_LINE('Pipeline paridade_datasus concluido.');
END cnis_sa_datasus;

