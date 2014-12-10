# -*- coding: utf-8 -*-
from pagador import settings
from pagador.acesso.externo import FormatoDeEnvio
from pagador.envio.models import SituacaoPedido
from pagador.envio.requisicao import Enviar
from pagador.envio.serializacao import ValorComAtributos
from pagador_rede.extensao.envio import (Request, Authentication, AcquirerCode, Transaction, CardTxn, Card, Cv2Avs, TxnDetails, Instalments,
                                         HistoricTxn, Risk, Action, MerchantConfiguration, CallbackConfiguration, CustomerDetails, RiskDetails, PersonalDetails, AddressDetails,
                                         PaymentDetails, OrderDetails, BillingDetails, LineItems, Item, ShippingDetails)


class PassosDeEnvio(object):
    auth = "auth"
    pre = "pre"
    accept_review = "accept_review"
    fulfill = "fulfill"


class StatusDeRetorno(object):
    sucesso = "1"
    revisao = "1127"
    rejeitada = "1126"
    comunicacao_interrompida = "2"
    timeout = "3"
    erro_nos_dados = "5"
    erro_na_comunicacao = "6"
    nao_autorizado = "7"
    tipo_de_cartao_invalido = "21"
    data_expiracao_invalida = "23"
    cartao_expirado = "24"
    numero_cartao_invalido = "25"


class ResultadoAntiFraude(object):
    aceita = "00"
    rejeitada = "01"
    revisao = "02"


class ChannelValues(object):
    web = "W"


class CallbackFormat(object):
    http = "HTTP"
    xml = "XML"
    soap = "SOAP"


class CallbackOptions(object):
    imediato = "00"
    cliente = "01"
    padrao = "02"
    ambos = "03"
    monitorado = "04"


class MeiosDePagamento(object):
    credito = "CC"
    debito = "DB"


class TipoEndereco(object):
    cliente = 1
    entrega = 2
    pagamento = 3


class TipoDeCartao(object):
    credito = "credit"
    debito = "debit"


class MetodoDeCaptura(object):
    ecomm = "ecomm"
    cont_auth = "cont_auth"


class TipoDeParcelamento(object):
    com_juros = "interest_bearing"
    sem_juros = "zero_interest"


class EnviarPedido(Enviar):
    def __init__(self, pedido, dados, configuracao_pagamento):
        super(EnviarPedido, self).__init__(pedido, dados, configuracao_pagamento)
        self.exige_autenticacao = False
        self.processa_resposta = True
        self.deve_gravar_dados_de_pagamento = True
        self.formato_de_envio = FormatoDeEnvio.xml
        self.passo_atual = PassosDeEnvio.pre
        self.headers = {'Content-Type': 'application/xml'}
        self._pedido_pagamento = None

    def obter_situacao_do_pedido(self, status_requisicao):
        if self.passo_atual == PassosDeEnvio.pre and status_requisicao == 200:
            return SituacaoPedido.SITUACAO_PEDIDO_EFETUADO
        if self.passo_atual == PassosDeEnvio.accept_review and status_requisicao == 200:
            return SituacaoPedido.SITUACAO_PAGTO_EM_ANALISE
        if self.passo_atual == PassosDeEnvio.fulfill and status_requisicao == 200:
            return SituacaoPedido.SITUACAO_PEDIDO_PAGO
        return None

    @property
    def url(self):
        if self.sandbox:
            return "https://scommerce.redecard.com.br/Beta/wsTransaction"
        return "https://ecommerce.userede.com.br/Transaction/wsTransaction"

    @property
    def sandbox(self):
        return settings.ENVIRONMENT in ["local", "development"]

    @property
    def pedido_pagamento(self):
        if self._pedido_pagamento:
            return self._pedido_pagamento
        self._pedido_pagamento = self.pedido.pedido_pagamentos.get(pagamento=self.pedido.pagamento)
        return self._pedido_pagamento

    def gerar_dados_de_envio(self, passo=None):
        self.passo_atual = self.dados["passo"]
        if self.pedido_pagamento.identificador_id == StatusDeRetorno.revisao:
            self.passo_atual = PassosDeEnvio.accept_review
        return self.request.to_xml(top=True)

    @property
    def valores_de_pagamento(self):
        txn_key = "CardTxn" if self.passo_atual == PassosDeEnvio.pre else "HistoricTxn"
        valores = {
            "transacao_id": self.dados["Response"]["gateway_reference"],
            "identificador_id": self.dados["Response"][txn_key]["authcode"],
            "valor_pago": self.pedido.valor_total,
        }
        if self.tem_parcelas:
            valores["conteudo_json"] = {
                "numero_parcelas": int(self.dados["cartao_parcelas"]),
                "valor_parcela": float(self.dados["cartao_valor_parcela"]),
                "sem_juros": self.dados["cartao_parcelas_sem_juros"] == "true"
            }
        return valores

    def processar_resposta(self, resposta):
        retorno = self.formatador.xml_para_dict(resposta.content)
        self.dados.update(retorno)
        if resposta.status_code != 200:
            return {"content": retorno, "status": resposta.status_code, "reenviar": False}
        sucesso = retorno["Response"]["status"] in [StatusDeRetorno.sucesso, StatusDeRetorno.revisao]
        retorno["sucesso"] = sucesso
        if retorno["Response"]["status"] == StatusDeRetorno.revisao:
            retorno["Response"]["CardTxn"]["authcode"] = StatusDeRetorno.revisao
        return {"content": retorno, "status": (200 if sucesso else 500), "reenviar": False}

    @property
    def tem_parcelas(self):
        parcelas = self.dados.get("cartao_parcelas", 1)
        return int(parcelas) > 1

    @property
    def request(self):
        transaction = None
        if self.passo_atual == PassosDeEnvio.pre:
            card = Card(
                cv2_avs=Cv2Avs(cv2=self.dados["cartao_cvv"]),
                pan=self.dados["cartao_numero"].replace(" ", ""),
                expirydate=self.dados["cartao_data_expiracao"],
                card_account_type=TipoDeCartao.credito
            )
            card_txn = CardTxn(card=card, method=self.passo_atual)
            txn_details = TxnDetails(
                dba=self.configuracao_pagamento.usuario,
                merchantreference="{:06d}".format(self.pedido.numero),
                capturemethod=MetodoDeCaptura.ecomm,
                amount=ValorComAtributos(self.formatador.formata_decimal(self.pedido.valor_total), {"currency": "BRL"})
            )
            if self.configuracao_pagamento.usar_antifraude:
                txn_details.define_valor_de_atributo("Risk", {"risk": self.anti_fraude})
            if self.tem_parcelas:
                tipo = TipoDeParcelamento.sem_juros if self.dados["cartao_parcelas_sem_juros"] == "true" else TipoDeParcelamento.com_juros
                instalments = Instalments(type=tipo, number=self.dados["cartao_parcelas"])
                txn_details.define_valor_de_atributo("Instalments", {"instalments": instalments})
            transaction = Transaction(card_txn=card_txn, txn_details=txn_details)
        if self.passo_atual == PassosDeEnvio.accept_review:
            historic_txn = HistoricTxn(reference=self.pedido_pagamento.transacao_id, method=self.passo_atual)
            transaction = Transaction(historic_txn=historic_txn)
        if self.passo_atual == PassosDeEnvio.fulfill:
            txn_details = TxnDetails(amount=ValorComAtributos(self.formatador.formata_decimal(self.pedido.valor_total), {"currency": "BRL"}))
            historic_txn = HistoricTxn(reference=self.pedido_pagamento.transacao_id, authcode=self.pedido_pagamento.identificador_id, method=self.passo_atual)
            transaction = Transaction(historic_txn=historic_txn, txn_details=txn_details)

        request = Request(
            authentication=Authentication(
                acquirer_code=AcquirerCode(rdcd_pv=self.configuracao_pagamento.token),
                password=self.configuracao_pagamento.senha
            ),
            transaction=transaction
        )
        return request

    @property
    def anti_fraude(self):
        risco = Risk(
            action=ValorComAtributos(
                Action(
                    merchant_configuration=self.merchant_configuration,
                    customer_details=self.customer_details
                ),
                {"service": "1"}
            )
        )
        return risco

    def endereco(self, tipo=TipoEndereco.cliente):
        if tipo == TipoEndereco.cliente:
            return "{}, {}, {}".format(
                self.formatador.trata_unicode_com_limite(self.pedido.cliente.endereco.endereco, limite=30),
                self.pedido.cliente.endereco.numero,
                self.formatador.trata_unicode_com_limite(self.pedido.cliente.endereco.bairro, limite=20)
            )
        if tipo == TipoEndereco.entrega:
            return "{}, {}, {}".format(
                self.formatador.trata_unicode_com_limite(self.pedido.endereco_entrega.endereco, limite=30),
                self.pedido.endereco_entrega.numero,
                self.formatador.trata_unicode_com_limite(self.pedido.endereco_entrega.bairro, limite=20)
            )
        if tipo == TipoEndereco.pagamento:
            return "{}, {}, {}".format(
                self.formatador.trata_unicode_com_limite(self.pedido.endereco_pagamento.endereco, limite=30),
                self.pedido.endereco_pagamento.numero,
                self.formatador.trata_unicode_com_limite(self.pedido.endereco_pagamento.bairro, limite=20)
            )
        return ""

    @property
    def billing_details(self):
        return BillingDetails(
            name=self.dados["cartao_nome"],
            address_line1=self.endereco(TipoEndereco.pagamento),
            address_line2=self.formatador.trata_unicode_com_limite(self.pedido.endereco_pagamento.complemento, limite=60),
            city=self.formatador.trata_unicode_com_limite(self.pedido.endereco_pagamento.cidade, limite=25),
            state_province=self.formatador.trata_unicode_com_limite(self.pedido.endereco_pagamento.estado, limite=25),
            country="BR",
            zip_code=self.pedido.endereco_pagamento.cep
        )

    @property
    def order_details(self):
        return OrderDetails(
            discount_value=self.formatador.formata_decimal(self.valor_desconto, em_centavos=True),
            #FIXME: entrar em contato com o e-rede pra saber o formato correto para esse campo
            # time_zone=self.fuso_horario,
            proposition_date=self.formatador.formata_data(self.pedido.provavel_data_envio, hora=False),
            billing_details=self.billing_details,
            line_items=LineItems(
                item=self.items
            )
        )

    @property
    def address_details(self):
        return AddressDetails(
            address_line1=self.endereco(),
            address_line2=self.formatador.trata_unicode_com_limite(self.pedido.cliente.endereco.complemento, limite=60),
            city=self.formatador.trata_unicode_com_limite(self.pedido.cliente.endereco.cidade, limite=25),
            state_province=self.formatador.trata_unicode_com_limite(self.pedido.cliente.endereco.estado, limite=25),
            country="BR",
            zip_code=self.pedido.cliente.endereco.cep
        )

    @property
    def shipping_details(self):
        return ShippingDetails(
            first_name=self.formatador.trata_unicode_com_limite(self.nome_para_entrega.split(" ")[0], limite=50),
            surname=self.formatador.trata_unicode_com_limite(self.nome_para_entrega.split(" ")[1], limite=50),
            address_line1=self.endereco(TipoEndereco.entrega),
            address_line2=self.formatador.trata_unicode_com_limite(self.pedido.endereco_entrega.complemento, limite=60),
            city=self.formatador.trata_unicode_com_limite(self.pedido.endereco_entrega.cidade, limite=25),
            state_province=self.formatador.trata_unicode_com_limite(self.pedido.endereco_entrega.estado, limite=25),
            country="BR",
            zip_code=self.pedido.endereco_entrega.cep,
            delivery_date=self.formatador.formata_data(self.pedido.provavel_data_entrega, hora=False),
            delivery_method=self.pedido.pedido_envio.envio.nome,
        )

    @property
    def personal_details(self):
        return PersonalDetails(
            first_name=self.formatador.trata_unicode_com_limite(self.nome_do_cliente.split(" ")[0], limite=32),
            surname=self.formatador.trata_unicode_com_limite(self.nome_do_cliente.split(" ")[1], limite=32),
            telephone="{}{}".format(*self.telefone_do_cliente),
            date_of_birth=self.formatador.formata_data(self.pedido.cliente.data_nascimento, hora=False),
            id_number=self.documento_de_cliente,
        )

    @property
    def risk_details(self):
        return RiskDetails(
            account_number=self.pedido.cliente_id,
            email_address=self.formatador.trata_email_com_mais(self.pedido.cliente.email),
            session_id=self.dados["session_id"],
            ip_address=self.dados["ip_address"]
        )

    @property
    def callback_configuration(self):
        return CallbackConfiguration(
            callback_format=CallbackFormat.http,
            callback_url=settings.REDE_NOTIFICATION_URL.format(self.conta_id)
        )

    @property
    def customer_details(self):
        return CustomerDetails(
            shipping_details=self.shipping_details,
            risk_details=self.risk_details,
            personal_details=self.personal_details,
            address_details=self.address_details,
            payment_details=PaymentDetails(payment_method=MeiosDePagamento.credito),
            order_details=self.order_details
        )

    @property
    def merchant_configuration(self):
        return MerchantConfiguration(
            channel=ChannelValues.web,
            merchant_location="Loja Integrada",
            callback_configuration=self.callback_configuration
        )

    @property
    def fuso_horario(self):
        estado, municipio = self.pedido.cliente.endereco.estado, self.pedido.cliente.endereco.cidade
        if estado == "AM":
            if municipio and municipio.lower() in [u"atalaia do norte", u"benjamin constant", u"boca do acre", u"eirunepé", u"envira", u"guajará", u"ipixuna", u"itamarati", u"jutaí", u"lábrea", u"pauini", u"são paulo de olivença", u"tabatinga"]:
                return "-05:00"
        if estado == "AC":
            return "-05:00"
        if estado in ["AM", "MT", "MS", "RO", "RR"]:
            return "-04:00"
        return "-03:00"

    @property
    def items(self):
        return [
            Item(
                product_code=self.formatador.trata_unicode_com_limite(item.sku, limite=50),
                product_description=self.formatador.trata_unicode_com_limite(item.nome, limite=50),
                order_quantity=self.formatador.formata_decimal(item.quantidade, como_int=True),
                unit_price=self.formatador.formata_decimal(item.preco_venda, em_centavos=True)
            )
            for item in self.pedido.itens.all()
        ]
