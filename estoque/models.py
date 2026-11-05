"""Regras de negócio do estoque (RF03 e RF06).

Este módulo concentra a integridade do estoque da associação:
- ItemEstoque representa cada item e o saldo atual.
- MovimentacaoEstoque registra entradas e saídas e mantém o saldo.

Notas de qualidade e segurança (MVP):
- O saldo é derivado das movimentações. Toda alteração deve passar por
  MovimentacaoEstoque.save() para manter o histórico coerente.
- As validações deste módulo protegem a integridade dos dados, mas não
  substituem autorização/permissões: o controle de quem pode acessar deve
  ser feito nas views (login_required) e no admin do Django.
- O ORM do Django parametriza as consultas, evitando injeção de SQL nos
  acessos feitos por este módulo.
"""

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction


class ItemEstoque(models.Model):
    """Item controlado no estoque da associação.

    Campos:
    - nome_item: identificador único do item.
    - saldo: quantidade disponível (valor derivado das movimentações).
    - minimo: limite que dispara o alerta de estoque baixo (RF06).

    Qualidade e segurança (MVP):
    - `saldo` é denormalizado para leitura rápida; a fonte da verdade é o
      histórico de MovimentacaoEstoque.
    - O campo `saldo` não possui validador de mínimo, portanto edições
      diretas no admin/ORM podem deixá-lo negativo. A regra é aplicada em
      MovimentacaoEstoque.save(); não existe constraint no banco.
    """

    # Identificador único: evita duplicar o mesmo item no estoque.
    nome_item = models.CharField("Nome do item", max_length=200, unique=True)
    # Saldo atual. Mantido exclusivamente por MovimentacaoEstoque.save().
    saldo = models.IntegerField("Saldo", default=0)
    # Limite para o alerta de estoque baixo (RF06).
    minimo = models.IntegerField("Estoque mínimo", default=5)

    class Meta:
        # Nomes exibidos no admin e ordenação alfabética nas listagens.
        verbose_name = "Item de estoque"
        verbose_name_plural = "Itens de estoque"
        ordering = ["nome_item"]

    def abaixo_do_minimo(self):
        """Indica se o saldo está abaixo do mínimo (RF06).

        Retorna:
            bool: True quando `saldo` < `minimo`.

        Qualidade: usado apenas para exibição/alertas; não bloqueia
        movimentações de estoque.
        """
        return self.saldo < self.minimo

    def __str__(self):
        """Representação legível usada no admin e em mensagens."""
        return self.nome_item


class MovimentacaoEstoque(models.Model):
    """Entrada ou saída de estoque (livro-razão do inventário).

    Cada registro representa um fato já ocorrido. O campo `saldo_apos` guarda
    o saldo do item imediatamente após a movimentação, servindo como trilha
    de auditoria.

    Qualidade e segurança (MVP):
    - A entrada exige uma doação e a saída exige um beneficiário (clean()).
    - A quantidade mínima é 1 (MinValueValidator).
    - `data_movimentacao` é automática e não deve ser editada.
    - `item` usa CASCADE: excluir o item apaga o histórico. No MVP isso
      simplifica a manutenção, mas reduz a rastreabilidade.
    - `doacao` e `beneficiario` usam SET_NULL para preservar a movimentação
      mesmo que o vínculo original seja removido.
    - O model não verifica perfil/permissão do usuário; isso é
      responsabilidade das views e do admin.
    """

    # Tipos permitidos: entrada (doação) e saída (entrega ao beneficiário).
    TIPO_CHOICES = [
        ("entrada", "Entrada"),
        ("saida", "Saída"),
    ]

    # Tipo da movimentação; restringe os valores possíveis via choices.
    tipo = models.CharField("Tipo", max_length=10, choices=TIPO_CHOICES)
    # Item afetado. CASCADE remove o histórico se o item for excluído.
    item = models.ForeignKey(
        ItemEstoque,
        verbose_name="Item",
        on_delete=models.CASCADE,
        related_name="movimentacoes",
    )
    # Quantidade movimentada; precisa ser maior ou igual a 1.
    quantidade = models.IntegerField("Quantidade", validators=[MinValueValidator(1)])
    # Data/hora gerada automaticamente; protege a trilha de auditoria.
    data_movimentacao = models.DateTimeField("Data da movimentação", auto_now_add=True)
    # Doação de origem (obrigatória para entradas). SET_NULL preserva o histórico.
    doacao = models.ForeignKey(
        "doacoes.Doacao",
        verbose_name="Doação",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentacoes",
    )
    # Beneficiário atendido (obrigatório para saídas). SET_NULL preserva o histórico.
    beneficiario = models.ForeignKey(
        "beneficiarios.Beneficiario",
        verbose_name="Beneficiário",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentacoes",
    )
    # Snapshot do saldo após esta movimentação (auditoria).
    saldo_apos = models.IntegerField("Saldo após a movimentação", default=0)

    class Meta:
        # Mais recentes primeiro no histórico.
        verbose_name = "Movimentação de estoque"
        verbose_name_plural = "Movimentações de estoque"
        ordering = ["-data_movimentacao"]

    def clean(self):
        """Valida regras cruzadas entre os campos (RF02/RF03).

        - Entrada de estoque precisa estar vinculada a uma doação.
        - Saída precisa estar vinculada a um beneficiário.

        Qualidade e segurança (MVP):
        - É chamado explicitamente por save(), porque o Django não executa
          clean() automaticamente em Object.save().
        - Formulários (ModelForm) chamam full_clean(); porém operações em
          massa (QuerySet.update) ou edições diretas no banco podem ignorar
          estas regras.
        - A validação evita registros inconsistentes, mas não autoriza a
          operação: isso deve ser garantido pelas views/permissões.
        """
        if self.tipo == "entrada" and not self.doacao_id:
            raise ValidationError("Doação é obrigatória para uma entrada de estoque.")
        if self.tipo == "saida" and not self.beneficiario_id:
            raise ValidationError("Beneficiário é obrigatório para uma saída de estoque.")

    def save(self, *args, **kwargs):
        """Atualiza o saldo do item e persiste a movimentação de forma atômica.

        Fluxo:
        1. Abre uma transação (rollback automático em caso de erro).
        2. Valida as regras de clean().
        3. Soma (entrada) ou subtrai (saída) a quantidade no saldo do item.
        4. Bloqueia saída maior que o saldo disponível.
        5. Salva apenas o campo `saldo` do item.
        6. Registra `saldo_apos` e persiste a movimentação.

        Qualidade e segurança (MVP):
        - transaction.atomic() evita saldo parcialmente atualizado se algo
          falhar no meio do processo.
        - update_fields=["saldo"] evita sobrescrever outros campos do item.
        - A checagem de saldo é feita em memória; em cenários de escrita
          concorrente pode haver condição de corrida (dois pedidos leem o
          mesmo saldo). No MVP com uso baixo e SQLite isso é aceitável; em
          produção com PostgreSQL, considere select_for_update() ou
          expressões F().
        - Não há verificação de usuário/perfil aqui; a autorização deve
          estar nas views (login_required) e no admin.
        - Excluir ou editar movimentações depois não reverte o saldo; trate
          o histórico como imutável para preservar a auditoria.
        """
        with transaction.atomic():
            self.clean()
            item = self.item
            if self.tipo == "entrada":
                item.saldo += self.quantidade
            elif self.tipo == "saida":
                if self.quantidade > item.saldo:
                    raise ValidationError(
                        f"Quantidade maior que o saldo disponível. "
                        f"Informe um valor até {item.saldo}."
                    )
                item.saldo -= self.quantidade
            item.save(update_fields=["saldo"])
            self.saldo_apos = item.saldo
            super().save(*args, **kwargs)

    def __str__(self):
        """Representação legível usada no admin e em mensagens."""
        return f"{self.get_tipo_display()} — {self.item} ({self.quantidade})"
