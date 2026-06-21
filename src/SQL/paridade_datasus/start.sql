-- ============================================================================
-- Pipeline de paridade DATASUS x CNIS/SA, reunido em um unico procedimento.
--
-- Cria, na ordem de dependencia:
--   1. sa_mor_sob                  (view)  <- dados.sa_mor / dados.sa_sob
--   2. cnis_sisobi_dt_obito        (view)  <- CNIS_SISOBI.*
--   3. cnis_sa_cpf_sexo_datanasc   (view)  \
--      cnis_sa_cpf_sexo            (view)   > join de (1) e (2)
--      cnis_sa_only_cpf           (view)  /
--   4. MICRODADOS_RESUMIDO         (table) <- MICRODADOS
--   5. cnis_sa_datasus_comUF       (view)  \  join de cnis_sa_cpf_sexo_datanasc
--      cnis_sa_datasus_semUF       (view)  /  com MICRODADOS_RESUMIDO
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
        select mot_saida, data_nasc, cpf, sexo
        from dados.sa_mor
        where ref_info in ('2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021','2022')
          and (mot_saida = '100' or mot_saida = '200' or mot_saida = '300')
        union
        select mot_saida, data_nasc, cpf, sexo
        from dados.sa_sob
        where ref_info in ('2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021','2022')
          and (mot_saida = '100' or mot_saida = '200' or mot_saida = '300'))
    ]';
    DBMS_OUTPUT.PUT_LINE('view sa_mor_sob criada.');

    -- 2) View CNIS/SISOBI com data de obito consolidada ----------------------
    EXECUTE IMMEDIATE q'[
        create or replace view cnis_sisobi_dt_obito as
        select t.*,
        case when t.DT_OBITO_MDM is not null then t.DT_OBITO_MDM
             when t.DT_OBITO_SISOBI is not null then t.DT_OBITO_SISOBI
             else least(
               nvl(t.DT_OBITO_SISOBI_OUTRAS,to_date('31/12/9999','DD/MM/YYYY')),
               nvl(t.DT_OBITO_SUIBE,to_date('31/12/9999','DD/MM/YYYY')),
               nvl(t.DT_OBITO_SUIBE_NIT_CNIS,to_date('31/12/9999','DD/MM/YYYY')),
               nvl(t.DT_OBITO_SUIBE_CPF_CNIS,to_date('31/12/9999','DD/MM/YYYY')),
               nvl(t.DT_OBITO_CNIS_NIT,to_date('31/12/9999','DD/MM/YYYY')),
               nvl(t.DT_OBITO_CNIS_CPF,to_date('31/12/9999','DD/MM/YYYY')),
               nvl(t.DT_OBITO_UFRJ_ANT,to_date('31/12/9999','DD/MM/YYYY')) )
        end as DT_DATA_OBITO
        from CNIS_SISOBI.CNIS_SISOBI_AGRUPADO_2019_V2_1 t
    ]';
    DBMS_OUTPUT.PUT_LINE('view cnis_sisobi_dt_obito criada.');

    -- 3a) Join SA x CNIS por cpf + sexo + data de nascimento -----------------
    EXECUTE IMMEDIATE q'[
        create or replace view cnis_sa_cpf_sexo_datanasc as
        select
            s.cpf, s.sexo, s.dat_evento, s.data_aviso, s.emp, s.produto,
            c.dt_nasc_mdm, c.dt_data_obito, c.nu_municipio, c.nu_cep, c.cs_grau_instr
        from (
                select cpf, sexo, concat(substr(data_nasc,3,2),substr(data_nasc,5,2)) as data_nasc1, data_nasc, dat_evento, data_aviso, emp, produto from sa_mor_sob
             ) s
        inner join (
                select cpf, cs_sexo, concat(substr(dt_nasc_mdm,7,2),substr(dt_nasc_mdm,4,2)) as data_nasc2, dt_nasc_mdm, dt_data_obito, nu_municipio, nu_cep, cs_grau_instr
                from cnis_sisobi_dt_obito
             ) c
        on s.cpf = c.cpf
        and s.sexo = case when c.cs_sexo = '3' then 'F' when c.cs_sexo = '1' then 'M' end
        and s.data_nasc1 = c.data_nasc2
    ]';
    DBMS_OUTPUT.PUT_LINE('view cnis_sa_cpf_sexo_datanasc criada.');

    -- 3b) Join SA x CNIS por cpf + sexo --------------------------------------
    EXECUTE IMMEDIATE q'[
        create or replace view cnis_sa_cpf_sexo as
        select
            s.cpf, s.sexo, s.dat_evento, s.data_aviso, s.emp, s.produto,
            c.dt_nasc_mdm, c.dt_data_obito, c.nu_municipio, c.nu_cep, c.cs_grau_instr
        from (
                select cpf, sexo, concat(substr(data_nasc,3,2),substr(data_nasc,5,2)) as data_nasc1, data_nasc, dat_evento, data_aviso, emp, produto from sa_mor_sob
             ) s
        inner join (
                select cpf, cs_sexo, concat(substr(dt_nasc_mdm,7,2),substr(dt_nasc_mdm,4,2)) as data_nasc2, dt_nasc_mdm, dt_data_obito, nu_municipio, nu_cep, cs_grau_instr
                from cnis_sisobi_dt_obito
             ) c
        on s.cpf = c.cpf
        and s.sexo = case when c.cs_sexo = '3' then 'F' when c.cs_sexo = '1' then 'M' end
    ]';
    DBMS_OUTPUT.PUT_LINE('view cnis_sa_cpf_sexo criada.');

    -- 3c) Join SA x CNIS apenas por cpf --------------------------------------
    EXECUTE IMMEDIATE q'[
        create or replace view cnis_sa_only_cpf as
        select
            s.cpf, s.sexo, s.dat_evento, s.data_aviso, s.emp, s.produto,
            c.dt_nasc_mdm, c.dt_data_obito, c.nu_municipio, c.nu_cep, c.cs_grau_instr
        from (
                select cpf, sexo, concat(substr(data_nasc,3,2),substr(data_nasc,5,2)) as data_nasc1, data_nasc, dat_evento, data_aviso, emp, produto from sa_mor_sob
             ) s
        inner join (
                select cpf, cs_sexo, concat(substr(dt_nasc_mdm,7,2),substr(dt_nasc_mdm,4,2)) as data_nasc2, dt_nasc_mdm, dt_data_obito, nu_municipio, nu_cep, cs_grau_instr
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
    EXECUTE IMMEDIATE q'[
        create or replace view cnis_sa_datasus_comUF as
        select
            c.cpf, c.sexo, c.nu_municipio, c.nu_cep, c.cs_grau_instr,
            c.dat_evento, c.data_aviso, c.emp, c.produto,
            b.data_nascimento, b.ocupacao, b.escolaridade_2010, b.causa_basica,
            b.naturalidade, b.estado_civil, b.raca_cor, b.id_municipio_residencia,
            b.status_do_epidem, b.sigla_uf, b.data_obito
        from (
                select cpf, sexo, dt_nasc_mdm, dt_data_obito, nu_municipio,
                    substr(nu_municipio,0,2) uf_municipio, nu_cep, cs_grau_instr,
                    concat(concat(substr(dt_nasc_mdm,0,2),substr(dt_nasc_mdm,4,2)),substr(dt_nasc_mdm,7,2)) as data_nasc2,
                    concat(concat(substr(dt_data_obito,0,2),substr(dt_data_obito,4,2)),substr(dt_data_obito,7,2)) as data_obito2,
                    dat_evento, data_aviso, emp, produto
                from cnis_sa_cpf_sexo_datanasc) c
        inner join (
                select data_nascimento, data_obito, sexo, ocupacao, escolaridade_2010, causa_basica,
                    naturalidade, estado_civil, raca_cor, id_municipio_residencia, status_do_epidem, sigla_uf,
                    concat(concat(substr(data_nascimento,0,2),substr(data_nascimento,3,2)),substr(data_nascimento,7,2)) as data_nasc1,
                    concat(concat(substr(data_obito,0,2),substr(data_obito,3,2)),substr(data_obito,7,2)) as data_obito1
                from microdados_resumido) b
        on b.sexo = case when c.sexo = 'F' then '2' when c.sexo = 'M' then '1' end
        and c.data_nasc2 = b.data_nasc1
        and c.data_obito2 = b.data_obito1
        and b.sigla_uf = case
                when c.uf_municipio = '35' then 'SP' when c.uf_municipio = '33' then 'RJ'
                when c.uf_municipio = '31' then 'MG' when c.uf_municipio = '32' then 'ES'
                when c.uf_municipio = '41' then 'PR' when c.uf_municipio = '42' then 'SC'
                when c.uf_municipio = '43' then 'RS' when c.uf_municipio = '51' then 'MT'
                when c.uf_municipio = '50' then 'MS' when c.uf_municipio = '53' then 'DF'
                when c.uf_municipio = '17' then 'TO' when c.uf_municipio = '52' then 'GO'
                when c.uf_municipio = '14' then 'RR' when c.uf_municipio = '11' then 'RO'
                when c.uf_municipio = '15' then 'PA' when c.uf_municipio = '21' then 'MA'
                when c.uf_municipio = '13' then 'AM' when c.uf_municipio = '16' then 'AP'
                when c.uf_municipio = '12' then 'AC' when c.uf_municipio = '27' then 'AL'
                when c.uf_municipio = '29' then 'BA' when c.uf_municipio = '23' then 'CE'
                when c.uf_municipio = '25' then 'PB' when c.uf_municipio = '26' then 'PE'
                when c.uf_municipio = '22' then 'PI' when c.uf_municipio = '24' then 'RN'
                when c.uf_municipio = '28' then 'SE'
            end
    ]';
    DBMS_OUTPUT.PUT_LINE('view cnis_sa_datasus_comUF criada.');

    -- 5b) Paridade DATASUS x CNIS/SA SEM filtro de UF ------------------------
    EXECUTE IMMEDIATE q'[
        create or replace view cnis_sa_datasus_semUF as
        select
            c.cpf, c.sexo, c.nu_municipio, c.nu_cep, c.cs_grau_instr,
            c.dat_evento, c.data_aviso, c.emp, c.produto,
            b.data_nascimento, b.ocupacao, b.escolaridade_2010, b.causa_basica,
            b.naturalidade, b.estado_civil, b.raca_cor, b.id_municipio_residencia,
            b.status_do_epidem, b.data_obito
        from (
                select cpf, sexo, dt_nasc_mdm, dt_data_obito, nu_municipio,
                    substr(nu_municipio,0,2) uf_municipio, nu_cep, cs_grau_instr,
                    concat(concat(substr(dt_nasc_mdm,0,2),substr(dt_nasc_mdm,4,2)),substr(dt_nasc_mdm,7,2)) as data_nasc2,
                    concat(concat(substr(dt_data_obito,0,2),substr(dt_data_obito,4,2)),substr(dt_data_obito,7,2)) as data_obito2,
                    dat_evento, data_aviso, emp, produto
                from cnis_sa_cpf_sexo_datanasc) c
        inner join (
                select data_nascimento, data_obito, sexo, ocupacao, escolaridade_2010, causa_basica,
                    estado_civil, raca_cor, naturalidade, id_municipio_residencia, status_do_epidem,
                    concat(concat(substr(data_nascimento,0,2),substr(data_nascimento,3,2)),substr(data_nascimento,7,2)) as data_nasc1,
                    concat(concat(substr(data_obito,0,2),substr(data_obito,3,2)),substr(data_obito,7,2)) as data_obito1
                from microdados_resumido) b
        on b.sexo = case when c.sexo = 'F' then '2' when c.sexo = 'M' then '1' end
        and c.data_nasc2 = b.data_nasc1
        and c.data_obito2 = b.data_obito1
    ]';
    DBMS_OUTPUT.PUT_LINE('view cnis_sa_datasus_semUF criada.');

    DBMS_OUTPUT.PUT_LINE('Pipeline paridade_datasus concluido.');
END cnis_sa_datasus;
/
