from estoque import retirar_produto, mostrar_retirados

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