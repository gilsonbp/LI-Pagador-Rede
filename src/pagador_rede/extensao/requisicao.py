# -*- coding: utf-8 -*-
from pagador import settings
from pagador.acesso.externo import FormatoDeEnvio
from pagador.envio.requisicao import Enviar
from pagador.envio.serializacao import ValorComAtributos
from pagador_rede.extensao.envio import (Request, Authentication, AcquirerCode, Transaction, CardTxn, Card, Cv2Avs, TxnDetails, Instalments,
                                         TipoDeCartao, MetodoDeCaptura, HistoricTxn)


class PassosDeEnvio(object):
    auth = "auth"
    pre = "pre"
    fulfill = "fulfill"


class StatusDeRetorno(object):
    sucesso = "1"
    comunicacao_interrompida = "2"
    timeout = "3"
    erro_nos_dados = "5"
    erro_na_comunicacao = "6"
    nao_autorizado = "7"
    tipo_de_cartao_invalido = "21"
    data_expiracao_invalida = "23"
    cartao_expirado = "24"
    numero_cartao_invalido = "25"


class EnviarPedido(Enviar):
    def __init__(self, pedido, dados, configuracao_pagamento):
        super(EnviarPedido, self).__init__(pedido, dados, configuracao_pagamento)
        self.exige_autenticacao = False
        self.processa_resposta = True
        self.deve_gravar_dados_de_pagamento = True
        self.formato_de_envio = FormatoDeEnvio.xml
        self.passo_atual = PassosDeEnvio.pre
        self.headers = {'Content-Type': 'application/xml'}

    @property
    def url(self):
        if self.sandbox:
            return "https://scommerce.redecard.com.br/Beta/wsTransaction"
        return "https://ecommerce.userede.com.br/Transaction/wsTransaction"

    @property
    def sandbox(self):
        return settings.ENVIRONMENT in ["local", "development"]

    @property
    def request(self):
        transaction = None
        if self.passo_atual == PassosDeEnvio.pre:
            card = Card(cv2_avs=Cv2Avs(cv2=self.dados["cartao_cvv"]), pan=self.dados["cartao_numero"], expirydate=self.dados["cartao_data_expiracao"], card_account_type=TipoDeCartao.credito)
            card_txn = CardTxn(card=card, method=self.passo_atual)
            txn_details = TxnDetails(
                dba=self.configuracao_pagamento.usuario,
                merchantreference=self.pedido.numero,
                capturemethod=MetodoDeCaptura.ecomm,
                amount=ValorComAtributos(self.formatador.formata_decimal(self.pedido.valor_total), {"currency": "BRL"})
            )
            if self.dados["parcelamento_tipo"]:
                instalments = Instalments(type=self.dados["parcelamento_tipo"], number=self.dados["parcelamento_numero"])
                txn_details.define_valor_de_atributo("instalments", {"instalments": instalments})
            transaction = Transaction(card_txn=card_txn, txn_details=txn_details)
        if self.passo_atual == PassosDeEnvio.fulfill:
            pedido_pagamento = self.pedido.pedido_pagamentos.get(pagamento=self.pedido.pagamento)
            txn_details = TxnDetails(amount=ValorComAtributos(self.formatador.formata_decimal(self.pedido.valor_total), {"currency": "BRL"}))
            historic_txn = HistoricTxn(reference=pedido_pagamento.transacao_id, authcode=pedido_pagamento.identificador_id, method=self.passo_atual)
            transaction = Transaction(historic_txn=historic_txn, txn_details=txn_details)

        request = Request(
            authentication=Authentication(
                acquirer_code=AcquirerCode(rdcd_pv=self.configuracao_pagamento.token),
                password=self.configuracao_pagamento.senha
            ),
            transaction=transaction
        )
        return request

    def gerar_dados_de_envio(self, passo=None):
        self.passo_atual = self.dados["passo"]
        return self.request.to_xml(top=True)

    @property
    def valores_de_pagamento(self):
        return {
            "transacao_id": self.dados["Response"]["gateway_reference"],
            "identificador_id": self.dados["Response"]["CardTxn"]["authcode"],
            "valor_pago": self.pedido.valor_total,
        }

    def processar_resposta(self, resposta):
        retorno = self.formatador.xml_para_dict(resposta.content)
        self.dados.update(retorno)
        return {"content": retorno, "status": resposta.status_code, "reenviar": False}

