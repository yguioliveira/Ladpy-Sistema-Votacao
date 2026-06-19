# Sistema de Votacao Digital

Sistema de votacao em terminal desenvolvido em Python com integracao ao MySQL. O projeto possui gerenciamento de eleitores, abertura e encerramento de votacao, registro de votos, auditoria, criptografia de dados sensiveis e apuracao de resultados.

> Projeto academico desenvolvido para a disciplina de Projeto Integrador I, adaptado para apresentacao em portfolio.

## Funcionalidades

- Cadastro, edicao, remocao, busca e listagem de eleitores.
- Listagem de candidatos cadastrados.
- Validacao de CPF e titulo de eleitor.
- Criptografia de CPF, chave de acesso e protocolo usando Cifra de Hill.
- Autenticacao de mesario para abertura e encerramento da votacao.
- Execucao da zerezima antes da abertura da urna.
- Controle de status da votacao: aberta ou fechada.
- Autenticacao de eleitor por titulo, CPF parcial e chave de acesso.
- Registro de voto em banco de dados MySQL.
- Bloqueio de voto duplicado.
- Registro de voto nulo para numero de candidato inexistente.
- Geracao de protocolo de votacao.
- Auditoria com logs de ocorrencias e protocolos.
- Resultados com boletim de urna, comparecimento, votos por partido e validacao de integridade.

## Tecnologias

- Python
- MySQL
- mysql-connector-python
- python-dotenv
- Git e GitHub

## Estrutura do projeto

```text
LADPY---Sistema-de-Votacao/
|-- database/
|   |-- candidato_db.py
|   |-- conexao.py
|   |-- eleitor_db.py
|   |-- resultado_db.py
|   `-- votacao_db.py
|-- menus/
|   |-- menu_gerenciamento.py
|   |-- menu_principal.py
|   `-- menu_votacao.py
|-- utils/
|   |-- criptografia.py
|   |-- documentos.py
|   |-- geral.py
|   |-- input_utils.py
|   |-- logs.py
|   `-- tela.py
|-- banco_de_dados.sql
|-- main.py
|-- requirements.txt
|-- .env.example
`-- README.md
```

## Como executar

### 1. Clone o repositorio

```bash
git clone https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git
cd NOME_DO_REPOSITORIO
```

### 2. Crie e ative um ambiente virtual

No Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

No Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instale as dependencias

```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados

Crie o banco e as tabelas executando o arquivo:

```text
banco_de_dados.sql
```

Esse script cria o banco `projetointegrador_db`, as tabelas principais e alguns dados iniciais para teste.

### 5. Configure as variaveis de ambiente

Copie o arquivo `.env.example` para `.env` e preencha com os dados do seu MySQL:

```env
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=sua_senha_mysql
DB_NAME=projetointegrador_db
```

O arquivo `.env` nao deve ser enviado ao GitHub.

### 6. Execute o sistema

```bash
python main.py
```

## Fluxo principal

1. O sistema inicia pelo `main.py`.
2. O menu principal permite acessar gerenciamento ou votacao.
3. No gerenciamento, e possivel administrar eleitores e consultar candidatos.
4. Na votacao, um mesario autenticado abre a urna.
5. A zerezima limpa votos anteriores e redefine os eleitores para `NAO_VOTOU`.
6. O eleitor se autentica e registra seu voto.
7. O sistema gera protocolo, salva o voto e marca o eleitor como `JA_VOTOU`.
8. O mesario encerra a votacao.
9. O sistema libera auditoria e resultados.

## Banco de dados

Principais tabelas:

- `eleitores`: armazena dados dos eleitores, CPF criptografado, chave criptografada e status do voto.
- `candidatos`: armazena candidatos disponiveis para votacao.
- `votos`: registra votos, data/hora e protocolo criptografado.
- `logs`: registra ocorrencias de auditoria.
- `controle_votacao`: controla se a votacao esta aberta ou fechada.

## Dados de teste

O arquivo `banco_de_dados.sql` inclui eleitores e candidatos iniciais. As chaves de acesso de teste estao comentadas no proprio script SQL.

## Observacoes de seguranca

- CPFs nao sao armazenados em texto puro.
- Chaves de acesso e protocolos sao criptografados.
- A senha do banco deve ficar apenas no arquivo `.env`.
- O arquivo `.env` esta protegido pelo `.gitignore`.

## Licenca

Este projeto esta licenciado sob a licenca MIT.
