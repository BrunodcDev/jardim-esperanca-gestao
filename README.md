# Jardim Esperança — Sistema de Gestão Comunitária

Sistema web para centralizar a gestão de uma associação sem fins lucrativos:
cadastro de beneficiários, controle de doações, estoque e relatórios de prestação de contas.

## Tecnologias

- Python 3.13 (compatível com 3.12+)
- Django 5.2 LTS
- SQLite (desenvolvimento) / PostgreSQL (produção, via `DATABASE_URL`)
- Bootstrap 5.3 (CDN)
- django-allauth (autenticação)
- django-environ (variáveis de ambiente)
- pytest + pytest-django (testes)

## Pré-requisitos

- Python 3.12 ou superior (com a opção **"Add python.exe to PATH"** marcada na instalação).
- (Opcional, produção) PostgreSQL.

> Se o comando `python` não for reconhecido no terminal, abra um terminal **novo** ou use o caminho completo,
> ex.: `C:\Users\seupc\AppData\Local\Programs\Python\Python313\python.exe`.

## Instalação

```powershell
# 1. Crie e ative o ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Instale as dependências
python -m pip install -r requirements.txt

# 3. (Opcional) Configure as variáveis de ambiente
Copy-Item .env.example .env

# 4. Aplique as migrações
python manage.py migrate

# 5. Crie um usuário administrador (se ainda não existir)
python manage.py createsuperuser

# 6. Inicie o servidor
python manage.py runserver
```

Acesse **http://127.0.0.1:8000** no navegador.

> O painel administrativo fica em **http://127.0.0.1:8000/admin/**.

## Usuário de teste (dados fictícios)

**Instruções de login:** usuário `admin` / senha `Admin123!`.

Se você rodou a carga de dados de exemplo, existe o usuário:

- **Usuário:** `admin`
- **Senha:** `Admin123!`
- **Perfil:** coordenadora

Dados fictícios incluídos: beneficiária "Ana P." (Centro, 4 pessoas), doação "Leite em pó" (12 latas)
e item "Cesta básica" (saldo 3, mínimo 5) para demonstrar o alerta de estoque baixo.

## Testes

```powershell
python -m pytest
```

Os testes em `tests/test_estoque.py` cobrem:

- RF02: registrar doação aumenta o saldo do item.
- RF03: saída maior que o saldo levanta `ValidationError` e mantém o saldo inalterado.
- RF06: item abaixo do mínimo é sinalizado.

## Configuração do banco (SQLite → PostgreSQL)

Por padrão o projeto usa **SQLite** (arquivo `db.sqlite3`), sem configuração extra.

Para usar **PostgreSQL**, defina a variável `DATABASE_URL` no arquivo `.env`:

```
DATABASE_URL=postgres://usuario:senha@localhost:5432/jardim_esperanca
```

O driver `psycopg[binary]` já está no `requirements.txt`.

## Estrutura de pastas

```text
jardim-esperanca-gestao/
├── manage.py
├── requirements.txt
├── .env.example
├── pytest.ini
├── config/            # settings, urls e views do dashboard
├── accounts/          # modelo Usuario (perfil coordenadora/voluntario)
├── beneficiarios/     # RF01 — cadastro e busca de beneficiários
├── doacoes/           # RF02 — registro de doações
├── estoque/           # RF03/RF06 — estoque e saídas
├── relatorios/        # RF04 — relatório por período + CSV
├── templates/         # base.html, dashboard.html e templates dos apps
└── tests/             # test_estoque.py
```

> Nota: a autenticação usa o django-allauth, cujo template de login fica em
> `templates/account/login.html` (equivalente ao `registration/login.html` citado no escopo).
