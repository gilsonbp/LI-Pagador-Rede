# -*- coding: utf-8 -*-
from pagador.envio.serializacao import EntidadeSerializavel


class Request(EntidadeSerializavel):
    parametros = {"version": "2"}
    _atributos_serializaveis = ["Authentication", "Transaction"]


class Authentication(EntidadeSerializavel):
    _atributos_serializaveis = ["AcquirerCode"]
    _atributos = ["password"]


class AcquirerCode(EntidadeSerializavel):
    _atributos = ["rdcd_pv"]


class Transaction(EntidadeSerializavel):
    _atributos_serializaveis = ["CardTxn", "TxnDetails", "HistoricTxn"]


class CardTxn(EntidadeSerializavel):
    _atributos_serializaveis = ["Card"]
    _atributos = ["method"]


class HistoricTxn(EntidadeSerializavel):
    _atributos_serializaveis = ["Card"]
    _atributos = ["reference", "method", "authcode"]


class Card(EntidadeSerializavel):
    _atributos_serializaveis = ["Cv2Avs"]
    _atributos = ["pan", "expirydate", "card_account_type"]


class Cv2Avs(EntidadeSerializavel):
    _atributos = ["cv2"]


class TxnDetails(EntidadeSerializavel):
    _atributos_serializaveis = ["Instalments", "Risk"]
    _atributos = ["dba", "merchantreference", "capturemethod", "amount"]


class Instalments(EntidadeSerializavel):
    _atributos = ["type", "number"]


class Risk(EntidadeSerializavel):
    _atributos_serializaveis = ["Action"]


class Action(EntidadeSerializavel):
    parametros = {"service": "1"}
    _atributos_serializaveis = ["MerchantConfiguration", "CustomerDetails"]


class MerchantConfiguration(EntidadeSerializavel):
    _atributos_serializaveis = ["CallbackConfiguration"]
    _atributos = ["merchant_location", "channel"]


class CallbackConfiguration(EntidadeSerializavel):
    _atributos = ["callback_format", "callback_url", "callback_options"]


class CustomerDetails(EntidadeSerializavel):
    _atributos = ["title", "first_name", "surname", "address_line1", "address_line2", "city", "state_province", "country", "zip_code", "delivery_date", "delivery_method"]
    _atributos_serializaveis = ["RiskDetails", "PersonalDetails", "AddressDetails", "PaymentDetails", "OrderDetails"]


class RiskDetails(EntidadeSerializavel):
    _atributos = ["account_number", "email_address", "session_id", "ip_address", "user_id", "usermachine_id", "user_profile"]


class PersonalDetails(EntidadeSerializavel):
    _atributos = ["first_name", "surname", "telephone", "telephone_2", "date_of_birth", "nationality", "id_number", "id_type", "ssn"]


class AddressDetails(EntidadeSerializavel):
    _atributos = ["address_line1", "address_line2", "city", "state_province", "country", "zip_code"]


class PaymentDetails(EntidadeSerializavel):
    _atributos = ["payment_method"]


class OrderDetails(EntidadeSerializavel):
    _atributos = ["discount_value", "time_zone", "proposition_date"]
    _atributos_serializaveis = ["BillingDetails", "LineItems"]


class BillingDetails(EntidadeSerializavel):
    _atributos = ["name", "address_line1", "address_line2", "city", "state_province", "country", "zip_code"]


class LineItems(EntidadeSerializavel):
    _atributos_lista = ["Item"]


class Item(EntidadeSerializavel):
    _atributos = ["product_code", "product_description", "product_category", "order_quantity", "unit_price"]
