# -*- coding: utf-8 -*-
import mox
from pagador.acesso import externo
from pagador.configuracao.models import FormaDePagamento, FormaDePagamentoConfiguracao
from pagador.envio.requisicao import EnviarPedido
from pagador_rede.extensao.requisicao import PassosDeEnvio, TipoDeParcelamento
from repositories.pedido.models import PedidoVenda


class ResponseOk(object):
    def __init__(self):
        self.status_code = 200
        self.content = """<?xml version="1.0" encoding="UTF-8"?>
<Response version="2">
<CardTxn>
<authcode>100000</authcode>
<card_scheme>VISA</card_scheme>
<country>United Kingdom</country>
</CardTxn>
<acquirer>Rede</acquirer>
<auth_host_reference>3</auth_host_reference>
<gateway_reference>4600903000000002</gateway_reference>
<extended_response_message>Sucesso</extended_response_message>
<extended_status>00</extended_status>
<merchantreference>123403</merchantreference>
<mid>456732145</mid>
<mode>TEST</mode>
<reason>ACCEPTED</reason>
<status>1</status>
<time>1372847996</time>
</Response>
"""


ERROS = {
    "51": "Produto ou serviço não habilitado para o estabelecimento. Entre em contato com a Rede",
    "53": "Transação não permitida para o emissor. Entre em contato com a Rede",
    "56": "Erro nos dados informados. Tente novamente. Ao receber este erro na transação de confirmação da pré (fulfill), importante reenviar a transação diariamente durante 3 dias e caso persista o erro entrar em contato com nosso suporte técnico",
    "57": "Estabelecimento inválido",
    "58": "Transação não autorizada. Contate o emissor",
    "65": "Senha inválida. Tente novamente",
    "69": "Transação não permitida para este produto ou serviço",
    "72": "Contate o emissor",
    "74": "Falha na comunicação. Tente novamente",
    "79": "Cartão expirado. Transação não pode ser resubmetida. Contate o emissor",
    "80": "Transação não autorizada. Contate o emissor. (Saldo Insuficiente)",
    "81": "Produto ou serviço não habilitado para o emissor (AVS)",
    "82": "Transação não autorizada para cartão de débito",
    "83": "Transação não autorizada. Problemas com cartão. Contate o emissor",
    "84": "Transação não autorizada. Transação não pode ser resubmetida. Contate o emissor",
}

class ResponseErro(object):
    def __init__(self, status="58"):
        self.status_code = 500
        self.content = """<?xml version="1.0" encoding="UTF-8"?>
<Response version="2">
<CardTxn>
<card_scheme>VISA</card_scheme>
<country>United Kingdom</country>
</CardTxn>
<acquirer>Rede</acquirer>
<auth_host_reference>13</auth_host_reference>
<gateway_reference>4500903000000007</gateway_reference>
<extended_response_message>{}</extended_response_message>
<extended_status>{}</extended_status>
<information>DECLINE</information>
<merchantreference>123408</merchantreference>
<mid>456732145</mid>
<mode>TEST</mode>
<reason>DECLINED</reason>
<status>7</status>
<time>1372852207</time>
</Response>
""".format(ERROS[status], status)


class TesteMontaXml(mox.MoxTestBase):
    def setUp(self):
        super(TesteMontaXml, self).setUp()
        self.conta_id = 8
        self.meio_pagamento = FormaDePagamento.objects.get(codigo='rede')
        self.configuracao = FormaDePagamentoConfiguracao.objects.get(forma_pagamento_id=self.meio_pagamento, conta_id=self.conta_id)
        self.configuracao.usar_antifraude = False
        self.dados = {
            "session_id": "Session ID", "ip_address": "127.0.0.1",
            "cartao_parcelas_sem_juros": 'true',
            "cartao_nome": "Nome no cartão", "cartao_parcelas": 5,
            "cartao_cvv": 123, "cartao_numero": "1234567890123456", "cartao_data_expiracao": "08/22"
        }
        self.pedido_numero = 590
        self.pedido = PedidoVenda.objects.get(conta_id=self.conta_id, numero=self.pedido_numero)

    def _request(self, fill=False):
        request = [
            '<Request version="2">',
                '<Authentication>',
                    '<AcquirerCode><rdcd_pv>{}</rdcd_pv></AcquirerCode>'.format(self.configuracao.token),
                    '<password>{}</password>'.format(self.configuracao.senha),
                '</Authentication>',
                '<Transaction>'
            ]
        if fill:
            request.extend(
                [
                    '<HistoricTxn><authcode>100000</authcode><method>fulfill</method><reference>4600903000000002</reference></HistoricTxn>',
                    '<TxnDetails>',
                        '<amount currency="BRL">{}</amount>'.format(self.pedido.valor_total),
                    '</TxnDetails>',
                ]
            )
        else:
            request.extend(
                [
                    '<CardTxn>',
                        '<Card><card_account_type>credit</card_account_type><Cv2Avs><cv2>123</cv2></Cv2Avs><expirydate>08/22</expirydate><pan>1234567890123456</pan></Card>',
                        '<method>pre</method>',
                    '</CardTxn>'
                    '<TxnDetails>',
                        '<amount currency="BRL">{}</amount>'.format(self.pedido.valor_total),
                        '<capturemethod>ecomm</capturemethod>',
                        '<dba>{}</dba>'.format(self.configuracao.usuario),
                        '<Instalments>',
                            '<number>5</number>',
                            '<type>zero_interest</type>',
                        '</Instalments>',
                        '<merchantreference>{}</merchantreference>'.format(self.pedido_numero),
                    '</TxnDetails>',
                ]
            )
        request.extend(
            [
                '</Transaction>',
            '</Request>'])
        return "".join(request)

    def test_envio_pre_sucesso(self):
        self.dados["passo"] = PassosDeEnvio.pre
        enviar_pedido = EnviarPedido(self.pedido_numero, self.dados, self.conta_id, self.configuracao)
        self.mox.StubOutWithMock(externo, "request_mock")
        externo.request_mock.post(
            enviar_pedido.requisicao.url,
            data=self._request(),
            headers=enviar_pedido.requisicao.headers,
            timeout=(10, 20)
        ).AndReturn(ResponseOk())
        self.mox.ReplayAll()
        resultado = enviar_pedido.enviar()
        resultado.should.be.equal({'content': {'Response': {'CardTxn': {'authcode': '100000', 'card_scheme': 'VISA', 'country': 'United Kingdom'}, 'acquirer': 'Rede', 'auth_host_reference': '3', 'extended_response_message': 'Sucesso', 'extended_status': '00', 'gateway_reference': '4600903000000002', 'merchantreference': '123403', 'mid': '456732145', 'mode': 'TEST', 'reason': 'ACCEPTED', 'status': '1', 'time': '1372847996'}, 'sucesso': True}, 'reenviar': False, 'status': 200})

    def test_envio_fulfill_sucesso(self):
        self.dados["passo"] = PassosDeEnvio.fulfill
        enviar_pedido = EnviarPedido(self.pedido_numero, self.dados, self.conta_id, self.configuracao)
        self.mox.StubOutWithMock(externo, "request_mock")
        externo.request_mock.post(
            enviar_pedido.requisicao.url,
            data=self._request(fill=True),
            headers=enviar_pedido.requisicao.headers,
            timeout=(10, 20)
        ).AndReturn(ResponseOk())
        self.mox.ReplayAll()
        resultado = enviar_pedido.enviar()
        resultado.should.be.equal({'content': {'Response': {'CardTxn': {'authcode': '100000', 'card_scheme': 'VISA', 'country': 'United Kingdom'}, 'acquirer': 'Rede', 'auth_host_reference': '3', 'extended_response_message': 'Sucesso', 'extended_status': '00', 'gateway_reference': '4600903000000002', 'merchantreference': '123403', 'mid': '456732145', 'mode': 'TEST', 'reason': 'ACCEPTED', 'status': '1', 'time': '1372847996'}, 'sucesso': True}, 'reenviar': False, 'status': 200})

    def test_envio_falha(self):
        self.dados["passo"] = PassosDeEnvio.pre
        enviar_pedido = EnviarPedido(self.pedido_numero, self.dados, self.conta_id, self.configuracao)
        self.mox.StubOutWithMock(externo, "request_mock")
        externo.request_mock.post(
            enviar_pedido.requisicao.url,
            data=self._request(),
            headers=enviar_pedido.requisicao.headers,
            timeout=(10, 20)
        ).AndReturn(ResponseErro(status="80"))
        self.mox.ReplayAll()
        resultado = enviar_pedido.enviar()
        resultado.should.be.equal({'content': {'Response': {'CardTxn': {'card_scheme': 'VISA', 'country': 'United Kingdom'}, 'acquirer': 'Rede', 'auth_host_reference': '13', 'extended_response_message': u'Transa\xe7\xe3o n\xe3o autorizada. Contate o emissor. (Saldo Insuficiente)', 'extended_status': '80', 'gateway_reference': '4500903000000007', 'information': 'DECLINE', 'merchantreference': '123408', 'mid': '456732145', 'mode': 'TEST', 'reason': 'DECLINED', 'status': '7', 'time': '1372852207'}}, 'reenviar': False, 'status': 500})
