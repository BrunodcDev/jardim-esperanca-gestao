# PLANO.md — Ordem de implementação

Plano de implementação do MVP **Jardim Esperança — Sistema de Gestão Comunitária**.

## Fase 0 — Ambiente

1. Instalar Python (3.12+), criar `venv` e instalar dependências.
2. `requirements.txt` com versões fixas; `.env.example`; `.gitignore`.
3. Configuração de banco: SQLite por padrão, PostgreSQL pronto via `DATABASE_URL`.

## Fase 1 — Esqueleto do projeto

4. `manage.py` + pacote `config/` (settings, urls, wsgi) com `django-environ`,
   Bootstrap 5.3 (CDN) e `django-allauth`.

## Fase 2 — Accounts

5. `Usuario(AbstractUser)` com campo `perfil` (`coordenadora`/`voluntario`).
6. Login por email ou nome de usuário (allauth, `ACCOUNT_LOGIN_METHODS`).
7. Template de login (`templates/account/login.html`).

## Fase 3 — Beneficiários (RF01)

8. Modelo `Beneficiario`, `BeneficiarioForm`.
9. Views: listagem com busca por nome, cadastro e edição. Templates.

## Fase 4 — Doações (RF02)

10. Modelo `Doacao`, `DoacaoForm`.
11. View que salva a doação + cria `MovimentacaoEstoque(entrada)` + atualiza o saldo,
    criando o item se necessário, dentro de `transaction.atomic()`.

## Fase 5 — Estoque (RF03)

12. `ItemEstoque` (com `abaixo_do_minimo()`) e `MovimentacaoEstoque` com `save()`
    que valida o saldo nas saídas e preenche `saldo_apos` automaticamente.
13. Views: listagem do estoque e registro de saída (com mensagem de erro clara).

## Fase 6 — Relatórios (RF04)

14. Relatório por período (data inicial/final), com totais e exportação CSV.

## Fase 7 — Dashboard (RF06)

15. Página inicial pós-login com alerta de estoque baixo
    ("Abaixo do mínimo" + ícone + cor vermelha).

## Fase 8 — Testes

16. `tests/test_estoque.py` cobrindo RF02, RF03 e RF06.

## Fase 9 — Finalização

17. `README.md`, `migrate`, `runserver` e validação com os dados fictícios.

## Decisões registradas

- **Banco:** SQLite no desenvolvimento, PostgreSQL em produção (via `DATABASE_URL`).
- **Python:** 3.13 (o escopo citava 3.12; 3.13 é totalmente compatível com Django 5.2 LTS).
- **Login:** template em `account/login.html` (convenção do allauth), equivalente ao
  `registration/login.html` citado no escopo.
- **Acesso:** todas as views usam `@login_required`; o campo `perfil` fica disponível
  para futuras regras de permissão.
