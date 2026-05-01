from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Sum
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


class EPIModelTests(BaseAuthenticatedTestCase):
    def test_epi_sem_validade_ca_e_valido(self):
        epi = EPI.objects.create(ca="CA999", descricao="Teste")
        self.assertTrue(epi.is_ca_valido)

    def test_epi_com_validade_futura_e_valido(self):
        from datetime import date, timedelta
        epi = EPI.objects.create(
            ca="CA888",
            descricao="Teste",
            validade_ca=date.today() + timedelta(days=30),
        )
        self.assertTrue(epi.is_ca_valido)

    def test_epi_com_validade_vencida_nao_e_valido(self):
        from datetime import date, timedelta
        epi = EPI.objects.create(
            ca="CA777",
            descricao="Teste",
            validade_ca=date.today() - timedelta(days=1),
        )
        self.assertFalse(epi.is_ca_valido)

    def test_epi_com_estoque_e_suficiente(self):
        epi = EPI.objects.create(ca="CA666", descricao="Teste", quantidade_em_estoque=5)
        self.assertTrue(epi.estoque_suficiente)

    def test_epi_com_estoque_zero_nao_e_suficiente(self):
        epi = EPI.objects.create(ca="CA555", descricao="Teste", quantidade_em_estoque=0)
        self.assertFalse(epi.estoque_suficiente)


class EstoqueTests(BaseAuthenticatedTestCase):
    def test_registrar_retirada_decrementa_estoque(self):
        self.epi.quantidade_em_estoque = 10
        self.epi.save()

        response = self.client.post(
            reverse("registrar_retirada"),
            {"colaborador": self.colaborador.id, "epi": self.epi.id, "quantidade": 3},
        )

        self.epi.refresh_from_db()
        self.assertEqual(self.epi.quantidade_em_estoque, 7)

    def test_registrar_retirada_sem_estoque_retorna_erro(self):
        self.epi.quantidade_em_estoque = 0
        self.epi.save()

        response = self.client.post(
            reverse("registrar_retirada"),
            {"colaborador": self.colaborador.id, "epi": self.epi.id, "quantidade": 1},
        )

        self.assertContains(response, "Estoque insuficiente")
        self.assertEqual(RegistroEPI.objects.count(), 0)


class ValidadeCATests(BaseAuthenticatedTestCase):
    def test_registrar_retirada_com_ca_vencido_retorna_erro(self):
        from datetime import date, timedelta
        self.epi.validade_ca = date.today() - timedelta(days=1)
        self.epi.quantidade_em_estoque = 10
        self.epi.save()

        response = self.client.post(
            reverse("registrar_retirada"),
            {"colaborador": self.colaborador.id, "epi": self.epi.id, "quantidade": 1},
        )

        self.assertContains(response, "vencido")
        self.assertEqual(RegistroEPI.objects.count(), 0)


class LimiteMensalTests(BaseAuthenticatedTestCase):
    def test_registrar_retirada_excede_limite_mensal(self):
        self.epi.quantidade_em_estoque = 100
        self.epi.save()

        for i in range(3):
            RegistroEPI.objects.create(
                colaborador=self.colaborador,
                epi=self.epi,
                quantidade=1,
                created_by=self.user,
            )

        self.assertEqual(RegistroEPI.objects.filter(colaborador=self.colaborador).count(), 3)


class DevolucaoTests(BaseAuthenticatedTestCase):
    def test_devolucao_incrementa_estoque(self):
        from datetime import date, timedelta
        self.epi.quantidade_em_estoque = 10
        self.epi.save()
        registro = RegistroEPI.objects.create(
            colaborador=self.colaborador,
            epi=self.epi,
            quantidade=5,
        )

        response = self.client.post(
            reverse("registrar_devolucao", args=[registro.id]),
            {"quantidade_devolvida": 3, "observacao": "Devolvido"},
        )

        self.epi.refresh_from_db()
        self.assertEqual(self.epi.quantidade_em_estoque, 13)
        self.assertTrue(hasattr(registro, "devolucao"))

    def test_devolucao_maior_que_retirada_retorna_erro(self):
        self.epi.quantidade_em_estoque = 10
        self.epi.save()
        registro = RegistroEPI.objects.create(
            colaborador=self.colaborador,
            epi=self.epi,
            quantidade=2,
        )

        response = self.client.post(
            reverse("registrar_devolucao", args=[registro.id]),
            {"quantidade_devolvida": 5, "observacao": ""},
        )

        self.assertContains(response, "não pode exceder")


class AuditoriaTests(BaseAuthenticatedTestCase):
    def test_epi_criado_por_usuario_autenticado(self):
        response = self.client.post(
            reverse("cadastrar_epi"),
            {"ca": "CA-TEST", "descricao": "Teste", "quantidade_em_estoque": 5},
        )

        epi = EPI.objects.get(ca="CA-TEST")
        self.assertEqual(epi.created_by, self.user)

    def test_colaborador_criado_por_usuario_autenticado(self):
        response = self.client.post(
            reverse("cadastrar_colaborador"),
            {"nome_completo": "Teste", "matricula": "TEST-001", "funcao": "Teste", "setor": "Teste"},
        )

        colaborador = Colaborador.objects.get(matricula="TEST-001")
        self.assertEqual(colaborador.created_by, self.user)
