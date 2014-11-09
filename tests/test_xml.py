# -*- coding: utf-8 -*-

import mox
from pagador.envio.serializacao import ValorComAtributos
from pagador_rede.extensao.envio import Cv2Avs, Card, CardTxn, TxnDetails, Instalments, Transaction, Authentication, AcquirerCode, Request, Item, LineItems, BillingDetails, OrderDetails, PaymentDetails, AddressDetails, PersonalDetails, RiskDetails, CustomerDetails, CallbackConfiguration, MerchantConfiguration, Action, Risk


class Gerador(object):
    def gera_line_items(self):
        atributos1 = {"product_code": "CODIGO1", "product_description": "Decricao 1", "product_category": "Categoria 1", "order_quantity": 1, "unit_price": 100}
        atributos2 = {"product_code": "CODIGO2", "product_description": "Decricao 2", "product_category": "Categoria 2", "order_quantity": 2, "unit_price": 200}
        item1 = Item(**atributos1)
        item2 = Item(**atributos2)
        line_items = LineItems(
            item=[item1, item2]
        )
        return line_items

    def gera_billing_details(self):
        billing_details = BillingDetails(
            name="Nome cartao",
            address_line1="Endereco 1",
            address_line2="Endereco 2",
            city="Cidade",
            state_province="ET",
            country="BR",
            zip_code="CEP"
        )
        return billing_details

    def gera_order_details(self):
        order_details = OrderDetails(
            discount_value=1234,
            time_zone="-03:00",
            proposition_date="2014-05-12",
            billing_details=self.gera_billing_details(),
            line_items=self.gera_line_items()
        )
        return order_details

    def gera_address_details(self):
        address_details = AddressDetails(
            address_line1="Endereco 1",
            address_line2="Endereco 2",
            city="Cidade",
            state_province="ET",
            country="BR",
            zip_code="CEP"
        )
        return address_details

    def gera_personal_details(self):
        personal_details = PersonalDetails(
            first_name="Nome",
            surname="Sobrenome",
            telephone="11999999999",
            date_of_birth="1965-12-25",
            id_number="12345678911",
        )
        return personal_details

    def gera_risk_details(self):
        risk_details = RiskDetails(
            account_number="123456",
            email_address="cliente@bom.com",
            session_id="123123123",
            ip_address="127.0.0.1"
        )
        return risk_details

    def gera_customer_details(self):
        customer_details = CustomerDetails(
            first_name="Nome",
            surname="Sobrenome",
            address_line1="Endereco 1",
            address_line2="Endereco 2",
            city="Cidade",
            state_province="ET",
            country="BR",
            zip_code="CEP",
            delivery_date="2014-15-11",
            delivery_method="PAC",
            risk_details=self.gera_risk_details(),
            personal_details=self.gera_personal_details(),
            address_details=self.gera_address_details(),
            payment_details=PaymentDetails(payment_method="CC"),
            order_details=self.gera_order_details()
        )
        return customer_details

    def gera_merchant_configuration(self):
        merchant_configuration = MerchantConfiguration(
            channel="WEB",
            merchant_location="Loja Integrada",
            callback_configuration=CallbackConfiguration(callback_format="HTTP", callback_url="URL")
        )
        return merchant_configuration

    def gera_action(self):
        action = Action(
            merchant_configuration=self.gera_merchant_configuration(),
            customer_details=self.gera_customer_details()
        )
        return action

    def gera_risk(self):
        risk = Risk(
            action=ValorComAtributos(
                Action(
                    merchant_configuration=self.gera_merchant_configuration(),
                    customer_details=self.gera_customer_details()
                ),
                {"service": 1}
            )
        )
        return risk

    def gera_card(self):
        return Card(cv2_avs=Cv2Avs(cv2="codigo"), pan="1234", expirydate="Data", card_account_type="credit")

    def gera_card_txn(self):
        card = self.gera_card()
        card_txn = CardTxn(card=card, method="auth")
        return card_txn

    def gera_instalments(self):
        return Instalments(type="zero_interest", number=5)

    def gera_txn_details(self, antifraude=False):
        if antifraude:
            return TxnDetails(instalments=self.gera_instalments(), risk=self.gera_risk(), dba="dba-value", merchantreference="123445", capturemethod="ecomm", amount=ValorComAtributos("23.45", {"currency": "BRL"}))
        return TxnDetails(instalments=self.gera_instalments(), dba="dba-value", merchantreference="123445", capturemethod="ecomm", amount=ValorComAtributos("23.45", {"currency": "BRL"}))

    def gera_transaction(self, antifraude=False):
        card_txn = self.gera_card_txn()
        txn_details = self.gera_txn_details(antifraude)
        transaction = Transaction(card_txn=card_txn, txn_details=txn_details)
        return transaction

    def gera_authentication(self):
        return Authentication(
            acquirer_code=AcquirerCode(rdcd_pv="123456789"),
            password="123456"
        )

    def expectativa_cv2_avs(self):
        return "<Cv2Avs><cv2>codigo</cv2></Cv2Avs>"

    def expectativa_card(self):
        return "<Card><card_account_type>credit</card_account_type>{}<expirydate>Data</expirydate><pan>1234</pan></Card>".format(self.expectativa_cv2_avs())

    def expectativa_card_txn(self):
        return "<CardTxn>{}<method>auth</method></CardTxn>".format(self.expectativa_card())

    def expectativa_instalments(self):
        return "<Instalments><number>5</number><type>zero_interest</type></Instalments>"

    def expectativa_txn_details(self, antifraude=False):
        if antifraude:
            return '<TxnDetails><amount currency="BRL">23.45</amount><capturemethod>ecomm</capturemethod><dba>dba-value</dba>{}<merchantreference>123445</merchantreference>{}</TxnDetails>'.format(self.expectativa_instalments(), self.expectativa_risk())
        return '<TxnDetails><amount currency="BRL">23.45</amount><capturemethod>ecomm</capturemethod><dba>dba-value</dba>{}<merchantreference>123445</merchantreference></TxnDetails>'.format(self.expectativa_instalments())

    def expectativa_transaction(self, antifraude=False):
        return '<Transaction>{}{}</Transaction>'.format(self.expectativa_card_txn(), self.expectativa_txn_details(antifraude=antifraude))

    def expectativa_authentication(self):
        return "<Authentication><AcquirerCode><rdcd_pv>123456789</rdcd_pv></AcquirerCode><password>123456</password></Authentication>"

    def expectativa_request(self, antifraude=False):
        return '<Request version="2">{}{}</Request>'.format(self.expectativa_authentication(), self.expectativa_transaction(antifraude=antifraude))

    def expectativa_item(self, indice=0):
        return '<Item><order_quantity>{}</order_quantity><product_category>Categoria {}</product_category><product_code>CODIGO{}</product_code><product_description>Decricao {}</product_description><unit_price>{}</unit_price></Item>'.format(
            indice, indice, indice, indice, indice * 100
        )

    def expectativa_line_items(self):
        return '<LineItems>{}{}</LineItems>'.format(self.expectativa_item(1), self.expectativa_item(2))

    def expectativa_billing_details(self):
        return '<BillingDetails><address_line1>Endereco 1</address_line1><address_line2>Endereco 2</address_line2><city>Cidade</city><country>BR</country><name>Nome cartao</name><state_province>ET</state_province><zip_code>CEP</zip_code></BillingDetails>'

    def expectativa_order_details(self):
        return '<OrderDetails>{}{}{}{}</OrderDetails>'.format(
            self.expectativa_billing_details(),
            '<discount_value>1234</discount_value>',
            self.expectativa_line_items(),
            '<proposition_date>2014-05-12</proposition_date><time_zone>-03:00</time_zone>'
        )

    def expectativa_payment_details(self):
        return '<PaymentDetails><payment_method>CC</payment_method></PaymentDetails>'

    def expectativa_address_details(self):
        return '<AddressDetails><address_line1>Endereco 1</address_line1><address_line2>Endereco 2</address_line2><city>Cidade</city><country>BR</country><state_province>ET</state_province><zip_code>CEP</zip_code></AddressDetails>'

    def expectativa_personal_details(self):
        return '<PersonalDetails><date_of_birth>1965-12-25</date_of_birth><first_name>Nome</first_name><id_number>12345678911</id_number><surname>Sobrenome</surname><telephone>11999999999</telephone></PersonalDetails>'

    def expectativa_risk_details(self):
        return '<RiskDetails><account_number>123456</account_number><email_address>cliente@bom.com</email_address><ip_address>127.0.0.1</ip_address><session_id>123123123</session_id></RiskDetails>'

    def expectativa_customer_details(self):
        return '<CustomerDetails>{}{}{}{}{}{}{}</CustomerDetails>'.format(
            self.expectativa_address_details(),
            "<address_line1>Endereco 1</address_line1><address_line2>Endereco 2</address_line2><city>Cidade</city><country>BR</country><delivery_date>2014-15-11</delivery_date><delivery_method>PAC</delivery_method><first_name>Nome</first_name>",
            self.expectativa_order_details(),
            self.expectativa_payment_details(),
            self.expectativa_personal_details(),
            self.expectativa_risk_details(),
            "<state_province>ET</state_province><surname>Sobrenome</surname><zip_code>CEP</zip_code>"
        )

    def expectativa_callback_configuration(self):
        return '<CallbackConfiguration><callback_format>HTTP</callback_format><callback_url>URL</callback_url></CallbackConfiguration>'

    def expectativa_merchant_configuration(self):
        return '<MerchantConfiguration>{}{}</MerchantConfiguration>'.format(
            self.expectativa_callback_configuration(),
            '<channel>WEB</channel><merchant_location>Loja Integrada</merchant_location>'
        )

    def expectativa_action(self):
        return '<Action service="1">{}{}</Action>'.format(self.expectativa_customer_details(), self.expectativa_merchant_configuration())

    def expectativa_risk(self):
        return '<Risk>{}</Risk>'.format(self.expectativa_action())


class TesteMontaXmlRequest(mox.MoxTestBase, Gerador):

    def test_xml_cv2avs(self):
        cv2 = Cv2Avs(cv2="codigo")
        cv2.to_xml(top=True).should.be.equal(self.expectativa_cv2_avs())

    def test_xml_card(self):
        card = self.gera_card()
        card.to_xml(top=True).should.be.equal(self.expectativa_card())

    def test_xml_card_txn(self):
        card_txn = self.gera_card_txn()
        card_txn.to_xml(top=True).should.be.equal(self.expectativa_card_txn())

    def test_xml_instalments(self):
        instalments = self.gera_instalments()
        instalments.to_xml(top=True).should.be.equal(self.expectativa_instalments())

    def test_xml_txn_details(self):
        txn_details = self.gera_txn_details()
        txn_details.to_xml(top=True).should.be.equal(self.expectativa_txn_details())

    def test_xml_transaction(self):
        transaction = self.gera_transaction()
        transaction.to_xml(top=True).should.be.equal(self.expectativa_transaction())

    def test_xml_authentication(self):
        acquirer_code = AcquirerCode(rdcd_pv="123456789")
        authentication = Authentication(acquirer_code=acquirer_code, password="123456")
        authentication.to_xml(top=True).should.be.equal(self.expectativa_authentication())

    def test_xml_request_completo(self):
        request = Request(
            authentication=self.gera_authentication(),
            transaction=self.gera_transaction()
        )
        request.to_xml(top=True).should.be.equal(self.expectativa_request())

    def test_xml_request_completo_com_antifraude(self):
        request = Request(
            authentication=self.gera_authentication(),
            transaction=self.gera_transaction(antifraude=True)
        )
        request.to_xml(top=True).should.be.equal(self.expectativa_request(antifraude=True))


class TesteMontaXmlRisk(mox.MoxTestBase, Gerador):
    def test_item(self):
        atributos = {"product_code": "CODIGO0", "product_description": "Decricao 0", "product_category": "Categoria 0", "order_quantity": 0, "unit_price": 0}
        item = Item(**atributos)
        item.to_xml(top=True).should.be.equal(self.expectativa_item())

    def test_line_items(self):
        line_items = self.gera_line_items()
        line_items.to_xml(top=True).should.be.equal(self.expectativa_line_items())

    def test_billing_details(self):
        billing_details = self.gera_billing_details()
        billing_details.to_xml(top=True).should.be.equal(self.expectativa_billing_details())

    def test_order_details(self):
        order_details = self.gera_order_details()
        order_details.to_xml(top=True).should.be.equal(self.expectativa_order_details())

    def test_payments_details(self):
        payment_details = PaymentDetails(payment_method="CC")
        payment_details.to_xml(top=True).should.be.equal(self.expectativa_payment_details())

    def test_address_details(self):
        address_details = self.gera_address_details()
        address_details.to_xml(top=True).should.be.equal(self.expectativa_address_details())

    def test_personal_details(self):
        personal_details = self.gera_personal_details()
        personal_details.to_xml(top=True).should.be.equal(self.expectativa_personal_details())

    def test_risk_details(self):
        risk_details = self.gera_risk_details()
        risk_details.to_xml(top=True).should.be.equal(self.expectativa_risk_details())

    def test_customer_details(self):
        customer_details = self.gera_customer_details()
        customer_details.to_xml(top=True).should.be.equal(self.expectativa_customer_details())

    def test_callbak_configuration(self):
        callback_configuration = CallbackConfiguration(callback_format="HTTP", callback_url="URL")
        callback_configuration.to_xml(top=True).should.be.equal(self.expectativa_callback_configuration())

    def test_merchant_configuration(self):
        merchant_configuration = self.gera_merchant_configuration()
        merchant_configuration.to_xml(top=True).should.be.equal(self.expectativa_merchant_configuration())

    def test_action(self):
        action = self.gera_action()
        action.to_xml(top=True).should.be.equal(self.expectativa_action())

    def test_risk(self):
        risk = self.gera_risk()
        risk.to_xml(top=True).should.be.equal(self.expectativa_risk())
