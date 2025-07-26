import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import os
import itertools
import random

CAMINHO_PRODUTOS = "produtos.html"
CAMINHO_RETIRADOS = "retirados.csv"

def carregar_dados_html(caminho_arquivo):
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    todas_td = soup.find_all("td")
    colunas = [td.get_text(strip=True) for td in todas_td[:11]]
    dados = [td.get_text(strip=True) for td in todas_td[11:]]
    linhas = [dados[i:i+11] for i in range(0, len(dados), 11)]
    df = pd.DataFrame(linhas, columns=colunas)
    return soup, df

def tratar_dados(df):
    campos_numericos = ["Quantidade", "Preço Custo", "Margem Lucro", "Preço Venda"]
    for campo in campos_numericos:
        df[campo] = (
            df[campo]
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )
    return df

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

def buscar_combinacao_produtos(df, preco_desejado, tolerancia=0.4, max_produtos=4, usados=set()):
    # Considere até 40 produtos mais próximos do valor desejado
    df_filtrado = df[(df["Margem Lucro"] > 0) & (df["Quantidade"] >= 1)].copy()
    df_filtrado = df_filtrado[~df_filtrado["Código"].isin(usados)]
    df_filtrado["Diferenca"] = (df_filtrado["Preço Venda"] - preco_desejado).abs()
    df_filtrado = df_filtrado.sort_values("Diferenca").head(40)
    indices = list(df_filtrado.index)
    for n in range(2, max_produtos+1):  # Comece de 2 produtos para evitar solução trivial
        for comb in itertools.combinations(indices, n):
            total = df_filtrado.loc[list(comb), "Preço Venda"].sum()
            dif = abs(total - preco_desejado)
            if dif <= tolerancia:
                return df_filtrado.loc[list(comb)]
    return None

def buscar_combinacao_gulosa(df, preco_desejado, tolerancia=0.4, max_produtos=10, usados=set()):
    # Embaralha os produtos para tentar combinações diferentes a cada chamada
    df_filtrado = df[(df["Margem Lucro"] > 0) & (df["Quantidade"] >= 1)].copy()
    df_filtrado = df_filtrado[~df_filtrado["Código"].isin(usados)]
    df_filtrado = df_filtrado.sample(frac=1).reset_index(drop=True)  # embaralha
    combinacao = []
    valor_restante = preco_desejado

    for _ in range(max_produtos):
        # Só considera produtos com preço menor ou igual ao valor restante + tolerancia
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

def atualizar_estoque_html(soup, codigo, nova_quantidade):
    for linha in soup.find_all("tr"):
        colunas = linha.find_all("td")
        if colunas and colunas[0].get_text(strip=True) == str(codigo):
            colunas[5].string = str(nova_quantidade).replace('.', ',')  # Mantém padrão do HTML
            break
    with open(CAMINHO_PRODUTOS, "w", encoding="utf-8") as f:
        f.write(str(soup))

def salvar_retirado(produto, quantidade):
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    registro = pd.DataFrame([{
        "Código": produto["Código"],
        "Descrição": produto["Descrição"],
        "Quantidade Retirada": quantidade,
        "Preço Venda": produto["Preço Venda"],
        "Data": data
    }])
    if os.path.exists(CAMINHO_RETIRADOS):
        registro.to_csv(CAMINHO_RETIRADOS, mode="a", header=False, index=False)
    else:
        registro.to_csv(CAMINHO_RETIRADOS, index=False)

def mostrar_retirados():
    if not os.path.exists(CAMINHO_RETIRADOS) or os.path.getsize(CAMINHO_RETIRADOS) == 0:
        print("\nNenhum produto foi retirado ainda.")
        return
    try:
        df = pd.read_csv(
            CAMINHO_RETIRADOS,
            names=["Código", "Descrição", "Quantidade Retirada", "Preço Venda", "Data"],
            header=0 if pd.read_csv(CAMINHO_RETIRADOS, nrows=1).columns[0] == "Código" else None
        )
        if df.empty:
            print("\nNenhum produto foi retirado ainda.")
        else:
            print("\n--- Produtos já retirados ---")
            print(df.to_string(index=False))
    except Exception as e:
        print("\nErro ao ler produtos retirados:", e)

def retirar_produto():
    soup, df = carregar_dados_html(CAMINHO_PRODUTOS)
    df = tratar_dados(df)
    try:
        preco = float(input("Digite o preço desejado: R$ ").replace(",", "."))
    except ValueError:
        print("Entrada inválida.")
        return

    usados = set()
    while True:
        produto = buscar_produto_proximo(df, preco)
        if produto is not None and abs(produto["Preço Venda"] - preco) <= 0.4:
            print(f"\nProduto encontrado próximo ao valor desejado:")
            print(f"Código: {produto['Código']} | Descrição: {produto['Descrição']} | Preço Venda: R$ {produto['Preço Venda']:.2f} | Estoque: {produto['Quantidade']}")
            escolha = input("\nDeseja retirar este produto? [1] Sim [0] Buscar combinação [2] Cancelar: ").strip()
            if escolha == "1":
                try:
                    qtd = float(input("Quantos deseja retirar? "))
                    if qtd <= 0 or qtd > produto["Quantidade"]:
                        print("Quantidade inválida.")
                        return
                    novo_estoque = produto["Quantidade"] - qtd
                    atualizar_estoque_html(soup, produto["Código"], novo_estoque)
                    salvar_retirado(produto, qtd)
                    print(f"{qtd} unidade(s) de '{produto['Descrição']}' retirada(s) com sucesso.")
                except ValueError:
                    print("Quantidade inválida.")
                return
            elif escolha == "0":
                usados.add(produto["Código"])
            else:
                print("Operação cancelada.")
                return

        # Busca combinação gulosa
        combinacao = buscar_combinacao_gulosa(df, preco, tolerancia=0.4, usados=usados)
        if combinacao is None or combinacao.empty:
            print("Nenhuma combinação encontrada para o valor desejado.")
            return
        print("\nCombinação de produtos encontrada próxima ao valor desejado:")
        total = 0
        for idx, (_, prod) in enumerate(combinacao.iterrows(), 1):
            print(f"[{idx}] Código: {prod['Código']} | Descrição: {prod['Descrição']} | Preço Venda: R$ {prod['Preço Venda']:.2f} | Estoque: {prod['Quantidade']}")
            total += prod["Preço Venda"]
        print(f"Total: R$ {total:.2f} (Diferença: R$ {abs(total-preco):.2f})")
        print("\n[1] Retirar todos\n[0] Buscar outra combinação\n[2] Cancelar")
        escolha = input("Escolha: ").strip()
        if escolha == "1":
            for _, prod in combinacao.iterrows():
                qtd_retirar = 1
                if prod["Quantidade"] < 1:
                    print(f"Estoque insuficiente para '{prod['Descrição']}'. Operação cancelada.")
                    return
                novo_estoque = prod["Quantidade"] - qtd_retirar
                atualizar_estoque_html(soup, prod["Código"], novo_estoque)
                salvar_retirado(prod, qtd_retirar)
            print("Produtos retirados com sucesso.")
            return
        elif escolha == "0":
            usados.update(combinacao["Código"])
            continue
        else:
            print("Operação cancelada.")
            return

def main():
    print("O que deseja fazer?")
    print("[1] Retirar produto do estoque")
    print("[2] Ver produtos já retirados")
    escolha = input("Escolha uma opção (1 ou 2): ").strip()
    if escolha == "1":
        retirar_produto()
    elif escolha == "2":
        mostrar_retirados()
    else:
        print("Opção inválida.")

if __name__ == "__main__":
    main()