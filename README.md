# Gestor-de-retiradas

Sistema simples para identificar e retirar produtos do estoque a partir de um arquivo de banco de dados HTML.

## Como usar

1. Copie `produtos.example.html` para `produtos.html` e preencha com seus dados, ou adquira um `produtos.html` já pronto e coloque na raiz do projeto.

2. Instale as dependências:

   ```sh
   pip install -r requirements.txt
   ```

3. Execute:

   ```sh
   python main.py
   ```
   ou
   ```sh
   python3 main.py
   ```


## Estrutura dos arquivos

- **main.py**: Responsável pelo menu principal e inicialização do sistema.
- **db_utils.py**: Funções para manipulação de arquivos, leitura e escrita de dados (HTML e CSV).
- **busca.py**: Lógica de busca e combinação de produtos para atingir o valor desejado.
- **estoque.py**: Fluxo principal de interação com o usuário, retirada de produtos e exibição de retiradas.