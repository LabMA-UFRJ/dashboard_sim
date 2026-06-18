create view cnis_sisobi_dt_obito as

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
from 
CNIS_SISOBI.CNIS_SISOBI_AGRUPADO_2019_V2_1 t;