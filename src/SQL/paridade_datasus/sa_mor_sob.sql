create view sa_mor_sob as (
select mot_saida, data_nasc, cpf, sexo
from dados.sa_mor 
where ref_info in ('2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022') and (mot_saida = '100' or mot_saida = '200' or mot_saida = '300' )
union 
select  mot_saida, data_nasc, cpf, sexo
from dados.sa_sob 
where ref_info in ('2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022') and (mot_saida = '100' or mot_saida = '200' or mot_saida = '300' ));
