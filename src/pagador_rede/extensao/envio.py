# -*- coding: utf-8 -*-
from pagador.envio.serializacao import EntidadeSerializavel, Atributo


class TipoDeCartao(object):
    credito = "credit"
    debito = "debit"


class MetodoDeCaptura(object):
    ecomm = "ecomm"
    cont_auth = "cont_auth"


class Metodo(object):
    completo = "auth"
    pre = "pre"
    captura = "fulfill"
    cancelar = "cancel"


class TipoDeParcelamento(object):
    com_juros = "interest_bearing"
    sem_juros = "zero_interest"


class Request(EntidadeSerializavel):
    parametros = {"version": "2"}
    atributos = [Atributo("Authentication", eh_serializavel=True), Atributo("Transaction", eh_serializavel=True)]


class Authentication(EntidadeSerializavel):
    atributos = [Atributo("AcquirerCode", eh_serializavel=True), Atributo("password")]


class AcquirerCode(EntidadeSerializavel):
    atributos = [Atributo("rdcd_pv")]


class Transaction(EntidadeSerializavel):
    _atributos = ["CardTxn", "TxnDetails", "HistoricTxn"]
    atributos = [
        Atributo(atributo, eh_serializavel=True)
        for atributo in _atributos
    ]


class CardTxn(EntidadeSerializavel):
    _atributos = ["Card", "method"]
    atributos = [
        Atributo(atributo, eh_serializavel=(atributo == "Card"))
        for atributo in _atributos
    ]


class HistoricTxn(EntidadeSerializavel):
    _atributos = ["Card", "reference", "method", "authcode"]
    atributos = [
        Atributo(atributo, eh_serializavel=(atributo == "Card"))
        for atributo in _atributos
    ]


class Card(EntidadeSerializavel):
    _atributos = ["pan", "expirydate", "card_account_type", "Cv2Avs"]
    atributos = [
        Atributo(atributo, eh_serializavel=(atributo == "Cv2Avs"))
        for atributo in _atributos
    ]


class Cv2Avs(EntidadeSerializavel):
    atributos = [Atributo("cv2")]


class TxnDetails(EntidadeSerializavel):
    _atributos = ["dba", "merchantreference", "capturemethod", "amount", "Instalments"]
    atributos = [
        Atributo(atributo)
        for atributo in _atributos
    ]


class Instalments(EntidadeSerializavel):
    _atributos = ["type", "number"]
    atributos = [
        Atributo(atributo)
        for atributo in _atributos
    ]
