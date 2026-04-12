from django.db import models


class EPI(models.Model):
    ca = models.CharField(max_length=50, unique=True, verbose_name="CA")
    descricao = models.TextField(verbose_name="Descrição Completa")
    foto = models.ImageField(upload_to="epi_fotos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ca} - {self.descricao[:50]}"


class Colaborador(models.Model):
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    matricula = models.CharField(max_length=50, unique=True, verbose_name="Matrícula")
    funcao = models.CharField(max_length=100, verbose_name="Função")
    setor = models.CharField(max_length=100, verbose_name="Setor")
    created_at = models.DateTimeField(auto_now_add=True)

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

    def __str__(self):
        return f"{self.colaborador.nome_completo} - {self.epi.ca} - {self.data_retirada.date()}"
