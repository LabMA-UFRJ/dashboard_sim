"""Compila e executa a procedure de paridade DATASUS x CNIS/SA.

Uso:
    python src/SQL/run_pipeline.py                      # roda paridade_datasus/start.sql
    python src/SQL/run_pipeline.py caminho/outro.sql    # roda outro arquivo

O arquivo deve conter um unico CREATE OR REPLACE PROCEDURE; o terminador '/'
do SQL*Plus e removido antes do envio (a API OCI aceita um comando por vez).

Conexao: credenciais no .env da raiz do repositorio
(DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_SERVICE).

Modo thick e obrigatorio: o servidor e Oracle 11.2, que o python-oracledb
recusa em modo thin (DPY-3010). Aponte ORACLE_CLIENT_LIB para o Instant
Client caso ele nao esteja no caminho padrao abaixo.
"""

import os
import sys

import oracledb
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SQL_PADRAO = os.path.join(ROOT, "src", "SQL", "paridade_datasus", "start.sql")
CLIENT_PADRAO = r"C:\oracle\instantclient_21_19"

# nome da procedure = nome do arquivo compilado, usado para checar user_errors
PROCEDURE = "CNIS_SA_DATASUS"


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


def compilar(cur, caminho_sql):
    """Compila o DDL. Erros de compilacao nao levantam excecao: checar user_errors."""
    with open(caminho_sql, encoding="utf-8") as fh:
        ddl = fh.read().rstrip().rstrip("/").rstrip()
    cur.execute(ddl)

    cur.execute(
        "select line, position, text from user_errors where name = :n order by sequence",
        n=PROCEDURE,
    )
    erros = cur.fetchall()
    if erros:
        print("ERROS DE COMPILACAO:")
        for linha, pos, texto in erros:
            print(f"  L{linha}:{pos} {texto.strip()}")
        return False
    return True


def despejar_output(cur):
    """Imprime o DBMS_OUTPUT acumulado.

    get_line devolve um BOOLEAN, que nao trafega pela rede no 11.2 (ORA-03115),
    entao a leitura vai em lote via get_lines.
    """
    linhas = cur.arrayvar(str, 200, 4000)
    quantidade = cur.var(int)
    while True:
        cur.execute(
            """
            declare
                t dbms_output.chararr;
                n integer := 200;
            begin
                dbms_output.get_lines(t, n);
                :cnt := n;
                for i in 1 .. n loop :arr(i) := t(i); end loop;
            end;
            """,
            arr=linhas, cnt=quantidade,
        )
        n = quantidade.getvalue()
        for linha in linhas.getvalue()[:n]:
            print("  [db]", linha)
        if n < 200:
            break


def main():
    caminho_sql = sys.argv[1] if len(sys.argv) > 1 else SQL_PADRAO

    conn = conectar()
    print("conectado:", conn.version)
    cur = conn.cursor()
    cur.callproc("dbms_output.enable", (None,))

    print(f"compilando {os.path.basename(caminho_sql)}...")
    if not compilar(cur, caminho_sql):
        conn.close()
        return 1
    print("procedure compilada sem erros.")

    print(f"executando {PROCEDURE.lower()}...")
    try:
        cur.callproc(PROCEDURE.lower())
        conn.commit()
        status = 0
    except oracledb.DatabaseError as erro:
        print("FALHA NA EXECUCAO:", erro)
        status = 1

    despejar_output(cur)
    conn.close()
    return status


if __name__ == "__main__":
    sys.exit(main())
