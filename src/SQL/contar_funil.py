"""Conta o funil de paridade DATASUS x CNIS/SA para medir a populacao encontrada.

Para cada nivel do funil que alimenta as joins finais, reporta linhas brutas
(count(*)) e pessoas distintas (count(distinct cpf)) numa unica varredura.
MICRODADOS e anonimizado (sem CPF), entao so tem contagem de registros.

Resultado impresso no stdout E anexado a contagem.txt (raiz do repo), com
progresso incremental -- as varreduras somadas levam dezenas de minutos a horas.

Uso:  python src/SQL/contar_funil.py

Conexao reaproveitada de run_pipeline.py: .env + Instant Client (modo thick,
obrigatorio no Oracle 11.2).
"""

import os
import sys
import time
from datetime import datetime

import oracledb
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAIDA = os.path.join(ROOT, "contagem.txt")
CLIENT_PADRAO = r"C:\oracle\instantclient_21_19"

# Niveis do funil, do mais barato ao mais caro. com_cpf=False -> so count(*).
NIVEIS = [
    ("microdados_resumido", "DATASUS (base)", False),
    ("cnis_sa_datasus_comUF", "SA cap CNIS cap DATASUS (comUF)", True),
    ("cnis_sa_datasus_semUF", "SA cap CNIS cap DATASUS (semUF)", True),
    ("cnis_sa_cpf_sexo_datanasc", "SA cap CNIS (intermediario)", True),
    ("sa_mor_sob", "SA (base)", True),
    ("cnis_sisobi_dt_obito", "CNIS (base ~126M)", True),
]


def _env(nome):
    valor = os.getenv(nome)
    if valor is None:
        sys.exit(f"variavel {nome} ausente no .env")
    return valor.strip().strip('"').strip("'")


def conectar():
    load_dotenv(os.path.join(ROOT, ".env"))
    oracledb.init_oracle_client(lib_dir=os.getenv("ORACLE_CLIENT_LIB", CLIENT_PADRAO))
    dsn = oracledb.makedsn(
        _env("DB_HOST"), int(_env("DB_PORT")), service_name=_env("DB_SERVICE")
    )
    return oracledb.connect(user=_env("DB_USER"), password=_env("DB_PASS"), dsn=dsn)


def emitir(linha, fh):
    """Imprime no stdout e anexa ao arquivo, com flush para progresso ao vivo."""
    print(linha, flush=True)
    fh.write(linha + "\n")
    fh.flush()


def pct(parte, total):
    return f"{100.0 * parte / total:.2f}%" if total else "n/a"


def main():
    conn = conectar()
    cur = conn.cursor()

    resultados = {}  # view -> (linhas, cpf_distintos|None)
    with open(SAIDA, "a", encoding="utf-8") as fh:
        emitir("", fh)
        emitir("=" * 64, fh)
        emitir(f"Funil de paridade DATASUS x CNIS/SA  -  {datetime.now():%Y-%m-%d %H:%M}", fh)
        emitir("=" * 64, fh)
        emitir(f"{'NIVEL':34} {'LINHAS':>14} {'CPF DISTINTOS':>14}", fh)

        for view, rotulo, com_cpf in NIVEIS:
            t0 = time.time()
            if com_cpf:
                cur.execute(f"select count(*), count(distinct cpf) from {view}")
                linhas, cpfs = cur.fetchone()
            else:
                cur.execute(f"select count(*) from {view}")
                linhas, cpfs = cur.fetchone()[0], None
            resultados[view] = (linhas, cpfs)
            cpf_txt = f"{cpfs:,}" if cpfs is not None else "-"
            emitir(
                f"{rotulo:34} {linhas:>14,} {cpf_txt:>14}"
                f"   ({time.time() - t0:.0f}s)  [{view}]",
                fh,
            )

        # ----- tabela de retencao do funil -----------------------------------
        sa = resultados["sa_mor_sob"]
        inter = resultados["cnis_sa_cpf_sexo_datanasc"]
        final = resultados["cnis_sa_datasus_semUF"]

        emitir("", fh)
        emitir("Retencao do funil (subconjunto encontrado):", fh)
        emitir("-" * 64, fh)

        # Pessoas (CPF distintos)
        sa_p, inter_p, final_p = sa[1], inter[1], final[1]
        emitir("  PESSOAS (CPF distintos)", fh)
        emitir(f"    SA base ................... {sa_p:>14,}", fh)
        emitir(f"    -> SA cap CNIS ........... {inter_p:>14,}   ({pct(inter_p, sa_p)} do SA base)", fh)
        emitir(f"    -> cap DATASUS (final) ... {final_p:>14,}   ({pct(final_p, inter_p)} do intermediario)", fh)
        emitir(f"    FRACAO FINAL / SA base ... {pct(final_p, sa_p)}", fh)

        # Linhas brutas (expoe duplicacao dos joins)
        sa_l, inter_l, final_l = sa[0], inter[0], final[0]
        emitir("", fh)
        emitir("  LINHAS (brutas, com duplicacao de join)", fh)
        emitir(f"    SA base ................... {sa_l:>14,}", fh)
        emitir(f"    -> SA cap CNIS ........... {inter_l:>14,}   ({pct(inter_l, sa_l)} do SA base)", fh)
        emitir(f"    -> cap DATASUS (final) ... {final_l:>14,}   ({pct(final_l, inter_l)} do intermediario)", fh)
        emitir("=" * 64, fh)

    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
