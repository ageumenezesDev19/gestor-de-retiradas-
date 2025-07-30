import os
BLACKLIST_FILE = "blacklist.txt"

def load_blacklist():
    if not os.path.exists(BLACKLIST_FILE):
        return []
    with open(BLACKLIST_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def save_blacklist(blacklist):
    with open(BLACKLIST_FILE, "w", encoding="utf-8") as f:
        for item in blacklist:
            f.write(item.strip() + "\n")

def manage_blacklist():
    while True:
        blacklist = load_blacklist()
        print("\n--- Blacklist de produtos ---")
        print("Itens na blacklist:", ", ".join(blacklist) if blacklist else "(vazia)")
        print("[1] Adicionar termo")
        print("[2] Remover termo")
        print("[3] Voltar ao menu principal")
        escolha = input("Escolha: ").strip()
        if escolha == "1":
            termo = input("Digite o termo para bloquear (ex: enxada): ").strip()
            if termo and termo not in blacklist:
                blacklist.append(termo)
                save_blacklist(blacklist)
                print(f"'{termo}' adicionado à blacklist.")
        elif escolha == "2":
            termo = input("Digite o termo para remover: ").strip()
            if termo in blacklist:
                blacklist.remove(termo)
                save_blacklist(blacklist)
                print(f"'{termo}' removido da blacklist.")
            else:
                print("Termo não encontrado.")
        elif escolha == "3":
            break
        else:
            print("Opção inválida.")