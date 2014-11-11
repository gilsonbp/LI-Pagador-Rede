# -*- coding: utf-8 -*-
import mox
from pagador.configuracao.models import FormaDePagamento, FormaDePagamentoConfiguracao
from pagador.envio.requisicao import EnviarPedido
from pagador_rede.extensao.envio import TipoDeParcelamento


class TesteFusoHorario(mox.MoxTestBase):
    def setUp(self):
        super(TesteFusoHorario, self).setUp()
        self.conta_id = 8
        self.meio_pagamento = FormaDePagamento.objects.get(codigo='rede')
        self.configuracao = FormaDePagamentoConfiguracao.objects.get(forma_pagamento_id=self.meio_pagamento, conta_id=self.conta_id)
        self.dados = {
            "parcelamento_tipo": TipoDeParcelamento.sem_juros, "parcelamento_numero": 5,
            "cartao_cvv": 123, "cartao_numero": "1234567890123456", "cartao_data_expiracao": "08/22"
        }
        self.pedido = 590

    def test_fuso_horario_resto(self):
        enviar_pedido = EnviarPedido(self.pedido, self.dados, self.conta_id, self.configuracao)
        enviar_pedido.requisicao.fuso_horario.should.be.equal("-03:00")

    def test_fuso_horario_am_municipios(self):
        enviar_pedido = EnviarPedido(self.pedido, self.dados, self.conta_id, self.configuracao)
        enviar_pedido.pedido.cliente.endereco.estado = "AM"
        enviar_pedido.pedido.cliente.endereco.cidade = u"São Paulo de Olivença"
        enviar_pedido.requisicao.fuso_horario.should.be.equal("-05:00")

    def test_fuso_horario_am_resto(self):
        enviar_pedido = EnviarPedido(self.pedido, self.dados, self.conta_id, self.configuracao)
        enviar_pedido.pedido.cliente.endereco.estado = "AM"
        enviar_pedido.pedido.cliente.endereco.cidade = u"Tefé"
        enviar_pedido.requisicao.fuso_horario.should.be.equal("-04:00")

    def test_fuso_horario_ms(self):
        enviar_pedido = EnviarPedido(self.pedido, self.dados, self.conta_id, self.configuracao)
        enviar_pedido.pedido.cliente.endereco.estado = "MS"
        enviar_pedido.requisicao.fuso_horario.should.be.equal("-04:00")
