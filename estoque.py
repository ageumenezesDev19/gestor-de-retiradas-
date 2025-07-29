from db_utils import (
    carregar_dados_html, tratar_dados, atualizar_estoque_html, salvar_retirado, CAMINHO_PRODUTOS
)
from busca import buscar_produto_proximo, buscar_combinacao_gulosa
import pandas as pd
import os

CAMINHO_RETIRADOS = "retirados.csv"

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