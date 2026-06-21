create OR REPLACE view cnis_sa_datasus_comUF as
select 
        c.cpf,
        c.sexo,
        c.nu_municipio,
        c.nu_cep,
        c.cs_grau_instr,
        c.dat_evento,
        c.data_aviso,
        c.emp,
        c.produto,
        b.data_nascimento,
        b.ocupacao,
        b.escolaridade_2010,
        b.causa_basica,
        b.naturalidade,
        b.estado_civil,
        b.raca_cor,
        b.id_municipio_residencia,
        b.status_do_epidem,
        B.sigla_uf,
        b.data_obito
        
    from (
            select cpf,
            sexo,
            dt_nasc_mdm,
            dt_data_obito,
            nu_municipio,
            substr(nu_municipio,0,2) uf_municipio,
            nu_cep,
            cs_grau_instr,
            concat (concat(substr(dt_nasc_mdm,0,2),substr(dt_nasc_mdm,4,2)),substr(dt_nasc_mdm,7,2)) as data_nasc2,
            concat (concat(substr(dt_data_obito,0,2),substr(dt_data_obito,4,2)),substr(dt_data_obito,7,2)) as data_obito2,
            dat_evento,
            data_aviso,
            emp,
            produto
            
                from cnis_sa_cpf_sexo_datanasc) c
    inner join 
                (select data_nascimento, 
                data_obito,
                sexo, 
                ocupacao,
                escolaridade_2010,
                causa_basica,

                naturalidade,
                estado_civil,
                raca_cor,
                id_municipio_residencia,
                status_do_epidem,
                sigla_uf,
                concat(concat(substr(data_nascimento,0,2),substr(data_nascimento,3,2)),substr(data_nascimento,7,2)) as data_nasc1,
                concat(concat(substr(data_obito,0,2),substr(data_obito,3,2)),substr(data_obito,7,2)) as data_obito1
                from microdados_resumido
                )b
    on b.sexo = case
                    WHEN c.sexo = 'F' then '2'
                    WHEN c.sexo ='M' then '1'
                    end
    and c.data_nasc2 = b.data_nasc1
    and c.data_obito2 = b.data_obito1
    and b.sigla_uf = case
                    WHEN c.uf_municipio = '35' then 'SP'
                    WHEN c.uf_municipio = '33' then 'RJ'
                    WHEN c.uf_municipio = '31' then 'MG'
                    WHEN c.uf_municipio = '32' then 'ES'
                    WHEN c.uf_municipio = '41' then 'PR'
                    WHEN c.uf_municipio = '42' then 'SC'
                    WHEN c.uf_municipio = '43' then 'RS'
                    WHEN c.uf_municipio = '51' then 'MT'
                    WHEN c.uf_municipio = '50' then 'MS'
                    WHEN c.uf_municipio = '53' then 'DF'
                    WHEN c.uf_municipio = '17' then 'TO'
                    WHEN c.uf_municipio = '52' then 'GO'
                    WHEN c.uf_municipio = '14' then 'RR'
                    WHEN c.uf_municipio = '11' then 'RO'
                    WHEN c.uf_municipio = '15' then 'PA'
                    WHEN c.uf_municipio = '21' then 'MA'
                    WHEN c.uf_municipio = '13' then 'AM'
                    WHEN c.uf_municipio = '16' then 'AP'
                    WHEN c.uf_municipio = '12' then 'AC'
                    WHEN c.uf_municipio = '27' then 'AL'
                    WHEN c.uf_municipio = '29' then 'BA'
                    WHEN c.uf_municipio = '23' then 'CE'
                    WHEN c.uf_municipio = '25' then 'PB'
                    WHEN c.uf_municipio = '26' then 'PE'
                    WHEN c.uf_municipio = '22' then 'PI'
                    WHEN c.uf_municipio = '24' then 'RN'
                  WHEN c.uf_municipio = '28' then 'SE'
                end;
                

create OR REPLACE view cnis_sa_datasus_semUF as
select 
        c.cpf,
        c.sexo,
        c.nu_municipio,
        c.nu_cep,
        c.cs_grau_instr,
        c.dat_evento,
        c.data_aviso,
        c.emp,
        c.produto,
        b.data_nascimento,
        b.ocupacao,
        b.escolaridade_2010,
        b.causa_basica,
        b.naturalidade,
        b.estado_civil,
        b.raca_cor,
        b.id_municipio_residencia,
        b.status_do_epidem,
        b.data_obito
        
    from (
            select cpf,
            sexo,
            dt_nasc_mdm,
            dt_data_obito,
            nu_municipio,
            substr(nu_municipio,0,2) uf_municipio,
            nu_cep,
            cs_grau_instr,
            concat (concat(substr(dt_nasc_mdm,0,2),substr(dt_nasc_mdm,4,2)),substr(dt_nasc_mdm,7,2)) as data_nasc2,
            concat (concat(substr(dt_data_obito,0,2),substr(dt_data_obito,4,2)),substr(dt_data_obito,7,2)) as data_obito2,
            dat_evento,
            data_aviso,
            emp,
            produto
            
                from cnis_sa_cpf_sexo_datanasc) c
    inner join 
                (select data_nascimento, 
                data_obito,
                sexo, 
                ocupacao,
                escolaridade_2010,
                causa_basica,
                estado_civil,
                raca_cor,
                naturalidade,
                id_municipio_residencia,
                status_do_epidem,
                concat(concat(substr(data_nascimento,0,2),substr(data_nascimento,3,2)),substr(data_nascimento,7,2)) as data_nasc1,
                concat(concat(substr(data_obito,0,2),substr(data_obito,3,2)),substr(data_obito,7,2)) as data_obito1
                from microdados_resumido
                )b
    on b.sexo = case
                    WHEN c.sexo = 'F' then '2'
                    WHEN c.sexo ='M' then '1'
                    end
    and c.data_nasc2 = b.data_nasc1
    and c.data_obito2 = b.data_obito1;