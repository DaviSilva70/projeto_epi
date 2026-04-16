from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Colaborador, EPI, RegistroEPI
from .services import get_registros_filtrados


class BaseAuthenticatedTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="SenhaForte123")
        self.client.login(username="tester", password="SenhaForte123")
        self.colaborador = Colaborador.objects.create(
            nome_completo="Maria da Silva",
            matricula="12345",
            funcao="Auxiliar",
            setor="Patrimonio",
        )
        self.epi = EPI.objects.create(ca="CA123", descricao="Luva nitrilica")


class BuscarEPIsTests(BaseAuthenticatedTestCase):
    def test_busca_por_matricula_exibe_colaborador(self):
        RegistroEPI.objects.create(colaborador=self.colaborador, epi=self.epi, quantidade=2)

        response = self.client.get(reverse("buscar_epis"), {"matricula": "12345"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maria da Silva")
        self.assertContains(response, "CA123")

    def test_busca_com_data_invalida_exibe_mensagem(self):
        response = self.client.get(
            reverse("buscar_epis"),
            {"matricula": "12345", "data_inicio": "2026-99-99"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Informe uma data válida")


class ExportacaoTests(BaseAuthenticatedTestCase):
    def test_exportacao_csv_retorna_arquivo(self):
        RegistroEPI.objects.create(colaborador=self.colaborador, epi=self.epi, quantidade=3)

        response = self.client.get(reverse("exportar_excel"), {"matricula": "12345"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("epis_12345.csv", response["Content-Disposition"])
        self.assertContains(response, "Luva nitrilica")

    def test_exportacao_csv_com_intervalo_invalido_retorna_400(self):
        response = self.client.get(
            reverse("exportar_excel"),
            {"matricula": "12345", "data_inicio": "2026-04-20", "data_fim": "2026-04-10"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "data inicial", status_code=400)


class LogoutTests(BaseAuthenticatedTestCase):
    def test_logout_exige_post(self):
        response = self.client.get(reverse("logout"))

        self.assertEqual(response.status_code, 405)

    def test_logout_via_post_redireciona_para_login(self):
        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, reverse("login"))


class RegistrationTests(TestCase):
    @override_settings(ALLOW_SELF_REGISTRATION=False)
    def test_register_redirects_when_public_registration_disabled(self):
        response = self.client.get(reverse("register"), follow=True)

        self.assertRedirects(response, reverse("login"))
        self.assertContains(response, "cadastro público está desativado")


class PaginationTests(BaseAuthenticatedTestCase):
    @override_settings(LIST_PAGE_SIZE=5)
    def test_colaborador_list_is_paginated(self):
        for index in range(8):
            Colaborador.objects.create(
                nome_completo=f"Colaborador {index}",
                matricula=f"MAT-{index}",
                funcao="Auxiliar",
                setor="Patrimonio",
            )

        response = self.client.get(reverse("cadastrar_colaborador"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["page_obj"].paginator.num_pages >= 2)
        self.assertEqual(len(response.context["colaboradores"]), settings.LIST_PAGE_SIZE)


class ServiceTests(BaseAuthenticatedTestCase):
    def test_filtro_de_registros_ordena_do_mais_recente_para_o_mais_antigo(self):
        primeiro = RegistroEPI.objects.create(
            colaborador=self.colaborador,
            epi=self.epi,
            quantidade=1,
        )
        segundo = RegistroEPI.objects.create(
            colaborador=self.colaborador,
            epi=self.epi,
            quantidade=5,
        )
        RegistroEPI.objects.filter(pk=primeiro.pk).update(
            data_retirada=timezone.datetime(2026, 4, 10, 8, 0, tzinfo=timezone.get_current_timezone())
        )
        RegistroEPI.objects.filter(pk=segundo.pk).update(
            data_retirada=timezone.datetime(2026, 4, 12, 8, 0, tzinfo=timezone.get_current_timezone())
        )

        registros = list(get_registros_filtrados(self.colaborador))

        self.assertEqual([registro.pk for registro in registros], [segundo.pk, primeiro.pk])
