import itertools
import random
import pandas as pd

def buscar_produtos_proximos(df, preco_desejado, n=3):
    df_filtrado = df[(df["Margem Lucro"] > 0) & (df["Quantidade"] >= 1)].copy()
    if df_filtrado.empty:
        return None
    df_filtrado["Diferenca"] = (df_filtrado["Preço Venda"] - preco_desejado).abs()
    return df_filtrado.sort_values("Diferenca").head(n)

def buscar_produto_proximo(df, preco_desejado):
    df_filtrado = df[(df["Margem Lucro"] > 0) & (df["Quantidade"] >= 1)].copy()
    if df_filtrado.empty:
        return None
    df_filtrado["Diferenca"] = (df_filtrado["Preço Venda"] - preco_desejado).abs()
    return df_filtrado.sort_values("Diferenca").iloc[0]

def buscar_combinacao_gulosa(df, preco_desejado, tolerancia=0.4, max_produtos=10, usados=set()):
    df_filtrado = df[(df["Margem Lucro"] > 0) & (df["Quantidade"] >= 1)].copy()
    df_filtrado = df_filtrado[~df_filtrado["Código"].isin(usados)]
    df_filtrado = df_filtrado.sample(frac=1).reset_index(drop=True)
    combinacao = []
    valor_restante = preco_desejado

    for _ in range(max_produtos):
        candidatos = df_filtrado[df_filtrado["Preço Venda"] <= valor_restante + tolerancia].copy()
        if candidatos.empty:
            break
        candidatos["Diferenca"] = (candidatos["Preço Venda"] - valor_restante).abs()
        produto = candidatos.sort_values("Diferenca").iloc[0]
        combinacao.append(produto)
        valor_restante -= produto["Preço Venda"]
        df_filtrado = df_filtrado[df_filtrado["Código"] != produto["Código"]]
        if abs(valor_restante) <= tolerancia:
            break

    total = sum(prod["Preço Venda"] for prod in combinacao)
    if abs(preco_desejado - total) <= tolerancia and len(combinacao) > 0:
        return pd.DataFrame(combinacao)
    return None