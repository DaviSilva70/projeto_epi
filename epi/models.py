from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class EPI(models.Model):
    ca = models.CharField(max_length=50, unique=True, verbose_name="CA")
    descricao = models.TextField(verbose_name="Descrição Completa")
    foto = models.ImageField(upload_to="epi_fotos/", blank=True, null=True)
    quantidade_em_estoque = models.PositiveIntegerField(
        default=0, verbose_name="Quantidade em Estoque"
    )
    validade_ca = models.DateField(
        blank=True, null=True, verbose_name="Validade do CA"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="epis_criados"
    )

    def __str__(self):
        return f"{self.ca} - {self.descricao[:50]}"

    @property
    def is_ca_valido(self):
        if self.validade_ca is None:
            return True
        from django.utils import timezone
        return self.validade_ca >= timezone.now().date()

    @property
    def estoque_suficiente(self):
        return self.quantidade_em_estoque > 0


class Colaborador(models.Model):
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    matricula = models.CharField(max_length=50, unique=True, verbose_name="Matrícula")
    funcao = models.CharField(max_length=100, verbose_name="Função")
    setor = models.CharField(max_length=100, verbose_name="Setor")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="colaboradores_criados"
    )

    def __str__(self):
        return f"{self.nome_completo} - {self.matricula}"


class RegistroEPI(models.Model):
    colaborador = models.ForeignKey(
        Colaborador, on_delete=models.CASCADE, related_name="registros"
    )
    epi = models.ForeignKey(EPI, on_delete=models.CASCADE, related_name="registros")
    data_retirada = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Retirada"
    )
    quantidade = models.PositiveIntegerField(default=1, verbose_name="Quantidade")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="registros_criados"
    )

    def __str__(self):
        return f"{self.colaborador.nome_completo} - {self.epi.ca} - {self.data_retirada.date()}"


class DevolucaoEPI(models.Model):
    registro = models.OneToOneField(
        RegistroEPI, on_delete=models.CASCADE, related_name="devolucao"
    )
    data_devolucao = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Devolução"
    )
    quantidade_devolvida = models.PositiveIntegerField(
        default=1, verbose_name="Quantidade Devolvida"
    )
    observacao = models.TextField(blank=True, verbose_name="Observação")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="devolucoes_criadas"
    )

    def __str__(self):
        return f"Devolução {self.registro.colaborador.nome_completo} - {self.registro.epi.ca}"
