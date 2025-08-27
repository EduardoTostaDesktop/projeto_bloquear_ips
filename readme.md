# Sistema de Gerenciamento de Bloqueio e Desbloqueio de Endereços IP

## Descrição do Projeto

Este projeto é uma **aplicação web desenvolvida em Django** que permite gerenciar solicitações de bloqueio e desbloqueio de endereços IP.

O sistema possibilita:

* Criar listas de endereços IP (manual ou via arquivo XLSX);
* Registrar solicitações de bloqueio ou desbloqueio;
* Controlar o status de cada endereço (bloqueado ou desbloqueado);
* Consultar e detalhar solicitações;
* Realizar exclusão individual ou em massa de solicitações.

O sistema foi pensado para **profissionais de redes** que precisam automatizar o controle de acessos e endereços IP em sua infraestrutura.

---

## Tecnologias Utilizadas

* Python 3.13
* Django 5.2
* SQLite (pode ser adaptado para PostgreSQL, MySQL, etc.)
* OpenPyXL (para leitura de arquivos XLSX)
* Tailwind CSS (para o frontend, se houver templates customizados)

---

## Estrutura do Projeto

* `solicitacoes/`: módulo responsável pelo gerenciamento das solicitações.
* `listas/`: módulo de listas de endereços IP.
* `enderecos/`: módulo que armazena os endereços IP e seus status.
* `solicitantes/`: módulo de solicitantes (usuários que requisitam bloqueios).
* `usuarios/`: gerenciamento de usuários e permissões.

---

## Pré-requisitos

Antes de começar, você precisará ter instalado:

* Python 3.13 ou superior
* pip
* Virtualenv (recomendado)

---

## Instalação

1. **Clone o repositório:**

```bash
git clone <URL_DO_REPOSITORIO>
cd <NOME_DO_PROJETO>
```

2. **Crie e ative um ambiente virtual:**

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

4. **Execute as migrações do banco de dados:**

```bash
python manage.py migrate
```

5. **Crie um superusuário para acessar o sistema:**

```bash
python manage.py createsuperuser
```

6. **Inicie o servidor de desenvolvimento:**

```bash
python manage.py runserver
```

O sistema estará disponível em `http://127.0.0.1:8000/`.

---

## Manual de Uso

### 1. Listar Solicitações

* Acesse a página **"Solicitações"** para ver todas as solicitações cadastradas.
* Cada solicitação exibe o tipo (BLOQUEIO ou DESBLOQUEIO), a lista associada, e o solicitante.

### 2. Criar Solicitação

* Clique em **"Criar Solicitação"**.
* Selecione o **tipo**: BLOQUEIO ou DESBLOQUEIO.
* Escolha um **solicitante**.
* Selecione uma **lista existente** ou crie uma **nova lista**:

  * Para uma lista nova, informe um nome e, opcionalmente, uma data de desbloqueio futura.
* Adicione endereços **manual ou via arquivo XLSX**.
* Clique em **"Salvar"** para criar a solicitação.
* O sistema só alterará o status de endereços que precisem de atualização (ex.: não tentará bloquear um endereço já bloqueado).

### 3. Detalhar Solicitação

* Clique em uma solicitação na lista para visualizar os detalhes.
* É possível conferir todos os endereços e o status atual.

### 4. Excluir Solicitação

* Para remover uma solicitação, clique em **"Excluir"**.
* É possível excluir **uma ou várias solicitações em massa**.

---

## Observações

* O sistema utiliza **timezone-aware datetime** para controlar datas de desbloqueio.
* Endereços IP podem ser bloqueados/desbloqueados parcialmente, garantindo que apenas os endereços que precisam de alteração sejam processados.
