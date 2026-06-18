import os
import re
import unicodedata

import pandas as pd

# ============================================================
# Converte os CSVs "largos" de data/pre/csv/<ano>/ para o
# formato de consulta de data/processed/<ano>/<categoria>/mx_<label>.csv
# (mesmo layout de data/processed_old/, consumido pelo app.py).
# ============================================================

PATH_PRE_CSV = "./data/pre/csv"
PATH_PROCESSED = "./data/processed"

# Origem -> destino das colunas
RENAME_COLS = {
    "idade_num": "idade",
    "obitos": "deaths",
    "exposicao": "population",
    "Mx": "mx",
}
OUT_COLS = ["idade", "deaths", "population", "mx"]

# (sufixo do arquivo de origem, coluna de categoria, pasta de destino)
# sufixo/coluna None => arquivo de idade total, sem split.
DIMENSOES = [
    (None, None, "total"),
    ("sexo", "sexo", "genero"),
    ("uf", "uf", "uf"),
    ("estado_civil", "estado_civil", "estado_civil"),
    ("escolaridade", "escolaridade", "escolaridade"),
]


def slugify(valor):
    """Normaliza um valor de categoria para nome de arquivo.

    Ex.: 'NÃO INFORMADO' -> 'nao_informado', 'SEPARADO/DIVORCIADO' ->
    'separado_divorciado', 'SP' -> 'sp'.
    """
    texto = str(valor).strip().lower()
    # Remove acentos
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    # Troca qualquer sequência de não-alfanuméricos por '_'
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")


def to_processed(df):
    """Renomeia/seleciona as 4 colunas finais e ordena por idade."""
    out = df.rename(columns=RENAME_COLS)
    out = out[OUT_COLS].sort_values("idade").reset_index(drop=True)
    return out


def caminho_origem(ano, sufixo):
    nome = f"mx_idade_{ano}.csv" if sufixo is None else f"mx_idade_{sufixo}_{ano}.csv"
    return os.path.join(PATH_PRE_CSV, str(ano), nome)


def processar_ano(ano):
    """Gera todos os CSVs de consulta de um ano. Retorna nº de arquivos gerados."""
    print(f"\n  ANO {ano}")
    gerados = 0

    for sufixo, coluna, pasta in DIMENSOES:
        origem = caminho_origem(ano, sufixo)
        if not os.path.exists(origem):
            print(f"    AVISO: {origem} não encontrado, pulando '{pasta}'.")
            continue

        df = pd.read_csv(origem, encoding="utf-8-sig")
        destino_dir = os.path.join(PATH_PROCESSED, str(ano), pasta)
        os.makedirs(destino_dir, exist_ok=True)

        if coluna is None:
            # Idade total: um único arquivo mx_total.csv
            to_processed(df).to_csv(
                os.path.join(destino_dir, "mx_total.csv"),
                index=False, encoding="utf-8-sig")
            gerados += 1
        else:
            # Um arquivo por valor de categoria
            for valor, grupo in df.groupby(coluna):
                nome = f"mx_{slugify(valor)}.csv"
                to_processed(grupo).to_csv(
                    os.path.join(destino_dir, nome),
                    index=False, encoding="utf-8-sig")
                gerados += 1

        print(f"    {pasta}: ok")

    return gerados


if __name__ == "__main__":
    if not os.path.isdir(PATH_PRE_CSV):
        raise SystemExit(f"Pasta de origem não encontrada: {PATH_PRE_CSV}")

    anos = sorted(
        int(d) for d in os.listdir(PATH_PRE_CSV)
        if d.isdigit() and os.path.isdir(os.path.join(PATH_PRE_CSV, d))
    )


    print(f"{'='*60}")
    print(f"  GERANDO data/processed A PARTIR DE {PATH_PRE_CSV}")
    print(f"  Anos encontrados: {anos}")
    print(f"{'='*60}")

    total_arquivos = 0
    for ano in anos:
        total_arquivos += processar_ano(ano)

    print(f"\n{'='*60}")
    print(f"  CONCLUÍDO! {total_arquivos} arquivos gerados em {PATH_PROCESSED}")
    print(f"{'='*60}")
