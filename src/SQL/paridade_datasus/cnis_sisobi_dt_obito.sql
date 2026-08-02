create or replace view cnis_sisobi_dt_obito as
select t.*, t.DT_OBITO as dt_data_obito
from CNIS25.CNIS_2025_UNIFICADO t;



