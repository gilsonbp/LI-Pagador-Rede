# -*- coding: utf-8 -*-

import mox
from pagador.envio.serializacao import ValorComAtributos
from pagador_rede.extensao.envio import Cv2Avs, Card, CardTxn, TxnDetails, Instalments, Transaction, Authentication, AcquirerCode, Request


class TesteMontaXml(mox.MoxTestBase):
    def test_xml_cv2avs(self):
        cv2 = Cv2Avs(cv2="codigo")
        cv2.to_xml(top=True).should.be.equal("<Cv2Avs><cv2>codigo</cv2></Cv2Avs>")

    def test_xml_card(self):
        card = Card(cv2_avs=Cv2Avs(cv2="codigo"), pan="1234", expirydate="Data", card_account_type="credit")
        card.to_xml(top=True).should.be.equal("<Card><card_account_type>credit</card_account_type><Cv2Avs><cv2>codigo</cv2></Cv2Avs><expirydate>Data</expirydate><pan>1234</pan></Card>")

    def test_xml_card_txn(self):
        card = Card(cv2_avs=Cv2Avs(cv2="codigo"), pan="1234", expirydate="Data", card_account_type="credit")
        card_txn = CardTxn(card=card, method="auth")
        card_txn.to_xml(top=True).should.be.equal("<CardTxn><Card><card_account_type>credit</card_account_type><Cv2Avs><cv2>codigo</cv2></Cv2Avs><expirydate>Data</expirydate><pan>1234</pan></Card><method>auth</method></CardTxn>")

    def test_xml_instalments(self):
        instalments = Instalments(instalment_type="zero_interest", instalment_number=5)
        instalments.to_xml(top=True).should.be.equal("<Instalments><instalment_number>5</instalment_number><instalment_type>zero_interest</instalment_type></Instalments>")

    def test_xml_txn_details(self):
        instalments = Instalments(instalment_type="zero_interest", instalment_number=5)
        txn_details = TxnDetails(instalments=instalments, dba="dba-value", merchantreference="123445", capturemethod="ecomm", amount=ValorComAtributos("23.45", {"currency": "BRL"}))
        txn_details.to_xml(top=True).should.be.equal('<TxnDetails><amount currency="BRL">23.45</amount><capturemethod>ecomm</capturemethod><dba>dba-value</dba><Instalments><instalment_number>5</instalment_number><instalment_type>zero_interest</instalment_type></Instalments><merchantreference>123445</merchantreference></TxnDetails>')

    def test_xml_transaction(self):
        card = Card(cv2_avs=Cv2Avs(cv2="codigo"), pan="1234", expirydate="Data", card_account_type="credit")
        card_txn = CardTxn(card=card, method="auth")
        instalments = Instalments(instalment_type="zero_interest", instalment_number=5)
        txn_details = TxnDetails(instalments=instalments, dba="dba-value", merchantreference="123445", capturemethod="ecomm", amount=ValorComAtributos("23.45", {"currency": "BRL"}))
        transaction = Transaction(card_txn=card_txn, txn_details=txn_details)
        transaction.to_xml(top=True).should.be.equal('<Transaction><CardTxn><Card><card_account_type>credit</card_account_type><Cv2Avs><cv2>codigo</cv2></Cv2Avs><expirydate>Data</expirydate><pan>1234</pan></Card><method>auth</method></CardTxn><TxnDetails><amount currency="BRL">23.45</amount><capturemethod>ecomm</capturemethod><dba>dba-value</dba><Instalments><instalment_number>5</instalment_number><instalment_type>zero_interest</instalment_type></Instalments><merchantreference>123445</merchantreference></TxnDetails></Transaction>')

    def test_xml_authentication(self):
        acquirer_code = AcquirerCode(rdcd_pv="123456789")
        authentication = Authentication(acquirer_code=acquirer_code, password="123456")
        authentication.to_xml(top=True).should.be.equal("<Authentication><AcquirerCode><rdcd_pv>123456789</rdcd_pv></AcquirerCode><password>123456</password></Authentication>")

    def test_xml_request_completo(self):
        request = Request(
            authentication=Authentication(
                acquirer_code=AcquirerCode(rdcd_pv="123456789"),
                password="123456"
            ),
            transaction=Transaction(
                card_txn=CardTxn(
                    card=Card(
                        cv2_avs=Cv2Avs(cv2="codigo"),
                        pan="1234",
                        expirydate="Data",
                        card_account_type="credit"
                    ),
                    method="auth"
                ),
                txn_details=TxnDetails(
                    instalments=Instalments(
                        instalment_type="zero_interest",
                        instalment_number=5
                    ),
                    dba="dba-value",
                    merchantreference="123445",
                    capturemethod="ecomm",
                    amount=ValorComAtributos("23.45", {"currency": "BRL"})
                )
            )
        )
        request.to_xml(top=True).should.be.equal('<Request version="2"><Authentication><AcquirerCode><rdcd_pv>123456789</rdcd_pv></AcquirerCode><password>123456</password></Authentication><Transaction><CardTxn><Card><card_account_type>credit</card_account_type><Cv2Avs><cv2>codigo</cv2></Cv2Avs><expirydate>Data</expirydate><pan>1234</pan></Card><method>auth</method></CardTxn><TxnDetails><amount currency="BRL">23.45</amount><capturemethod>ecomm</capturemethod><dba>dba-value</dba><Instalments><instalment_number>5</instalment_number><instalment_type>zero_interest</instalment_type></Instalments><merchantreference>123445</merchantreference></TxnDetails></Transaction></Request>')
