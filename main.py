import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import os

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
    produtos = buscar_produtos_proximos(df, preco, n=3)
    if produtos is None or produtos.empty:
        print("Nenhum produto com margem > 0 e estoque > 0 foi encontrado.")
        return

    print("\nProdutos mais próximos encontrados:\n")
    for idx, (_, produto) in enumerate(produtos.iterrows(), 1):
        print(f"[{idx}] Código: {produto['Código']} | Descrição: {produto['Descrição']} | Preço Venda: R$ {produto['Preço Venda']:.2f} | Estoque: {produto['Quantidade']}")

    try:
        escolha = int(input("\nQual produto deseja selecionar? (1, 2 ou 3): ").strip())
        if escolha not in [1, 2, 3] or escolha > len(produtos):
            print("Opção inválida.")
            return
        produto = produtos.iloc[escolha - 1]
    except ValueError:
        print("Opção inválida.")
        return

    print(f"\nProduto selecionado:\n")
    print(f"Código       : {produto['Código']}")
    print(f"Descrição    : {produto['Descrição']}")
    print(f"Preço Venda  : R$ {produto['Preço Venda']:.2f}")
    print(f"Margem Lucro : {produto['Margem Lucro']}%")
    print(f"Estoque      : {produto['Quantidade']}")
    print("\nDeseja retirar este produto do estoque?")
    print("[1] Sim")
    print("[2] Não")
    escolha = input("Escolha (1 ou 2): ").strip()
    if escolha != "1":
        print("Produto não retirado.")
        return
    try:
        qtd = float(input("Quantos deseja retirar? "))
        if qtd <= 0:
            print("Quantidade inválida.")
            return
        if qtd > produto["Quantidade"]:
            print("Quantidade maior que o estoque disponível.")
            return
        novo_estoque = produto["Quantidade"] - qtd
        atualizar_estoque_html(soup, produto["Código"], novo_estoque)
        salvar_retirado(produto, qtd)
        print(f"{qtd} unidade(s) de '{produto['Descrição']}' retirada(s) com sucesso.")
    except ValueError:
        print("Erro: valor inválido.")

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