--- Cria uma View do inner join da SA_SOB com o Cnis_sisobi comparando cpf, sexo e data_nasc
create or replace view cnis_sa_cpf_sexo_datanasc as 
select     
    s.cpf,
    s.sexo,
    s.dat_evento,
    s.data_aviso,
    s.emp,
    s.produto,
    c.dt_nasc_mdm,
    c.dt_data_obito,
    c.nu_municipio,
    c.nu_cep,
    c.cs_grau_instr 
    

from (
        select cpf, sexo, concat(substr(data_nasc,3,2),substr(data_nasc,5,2)) as data_nasc1, data_nasc, dat_evento,data_aviso,emp,produto from sa_mor_sob
        ) s
inner join (
        select cpf, cs_sexo, concat(substr(dt_nasc_mdm,7,2),substr(dt_nasc_mdm,4,2)) as data_nasc2, dt_nasc_mdm, dt_data_obito, nu_municipio,nu_cep,cs_grau_instr
        from cnis_sisobi_dt_obito
        ) c
on s.cpf = c.cpf

and s.sexo = case
                when c.cs_sexo = '3' then 'F'
                when c.cs_sexo = '1' then 'M'
                END
and  s.data_nasc1 = c.data_nasc2;





--- Cria uma View do inner join da SA_SOB com o Cnis_sisobi comparando cpf e sexo
create or replace view cnis_sa_cpf_sexo as 
select     
    s.cpf,
    s.sexo,
    s.dat_evento,
    s.data_aviso,
    s.emp,
    s.produto,
    c.dt_nasc_mdm,
    c.dt_data_obito,
    c.nu_municipio,
    c.nu_cep,
    c.cs_grau_instr
    

from (
        select cpf, sexo, concat(substr(data_nasc,3,2),substr(data_nasc,5,2)) as data_nasc1, data_nasc, dat_evento,data_aviso,emp,produto from sa_mor_sob
        ) s
inner join (
        select cpf, cs_sexo, concat(substr(dt_nasc_mdm,7,2),substr(dt_nasc_mdm,4,2)) as data_nasc2, dt_nasc_mdm, dt_data_obito, nu_municipio,nu_cep,cs_grau_instr
        from cnis_sisobi_dt_obito
        ) c
on s.cpf = c.cpf

and s.sexo = case
                when c.cs_sexo = '3' then 'F'
                when c.cs_sexo = '1' then 'M'
                END;


--- Cria uma View do inner join da SA_SOB com o Cnis_sisobi comparando apenas cpf 
create or replace view cnis_sa_only_cpf as 
select     
    s.cpf,
    s.sexo,
    s.dat_evento,
    s.data_aviso,
    s.emp,
    s.produto,
    c.dt_nasc_mdm,
    c.dt_data_obito,
    c.nu_municipio,
    c.nu_cep,
    c.cs_grau_instr
    

from (
        select cpf, sexo, concat(substr(data_nasc,3,2),substr(data_nasc,5,2)) as data_nasc1, data_nasc, dat_evento,data_aviso,emp,produto from sa_mor_sob
        ) s
inner join (
        select cpf, cs_sexo, concat(substr(dt_nasc_mdm,7,2),substr(dt_nasc_mdm,4,2)) as data_nasc2, dt_nasc_mdm, dt_data_obito, nu_municipio,nu_cep,cs_grau_instr
        from cnis_sisobi_dt_obito
        ) c
on s.cpf = c.cpf;