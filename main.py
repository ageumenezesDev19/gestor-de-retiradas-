from estoque import retirar_produto, mostrar_retirados
from blacklist_utils import manage_blacklist

def main():
    while True:
        print("O que deseja fazer?")
        print("[1] Retirar produto do estoque")
        print("[2] Ver produtos já retirados")
        print("[3] Gerenciar blacklist de produtos")
        print("[0] Sair")
        escolha = input("Escolha uma opção (0, 1, 2 ou 3): ").strip()
        if escolha == "1":
            retirar_produto()
        elif escolha == "2":
            mostrar_retirados()
        elif escolha == "3":
            manage_blacklist()
        elif escolha == "0":
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()