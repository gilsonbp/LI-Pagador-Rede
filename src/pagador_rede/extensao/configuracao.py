# -*- coding: utf-8 -*-
import os

from pagador.configuracao.cadastro import CampoFormulario, FormularioBase, TipoDeCampo, CadastroBase, SelecaoBase, caminho_para_template
from pagador.configuracao.cliente import Script, TipoScript

eh_aplicacao = False


def caminho_do_arquivo_de_template(arquivo):
    return caminho_para_template(arquivo, meio_pagamento='rede')


class MeioPagamentoCadastro(CadastroBase):
    @property
    def registro(self):
        script = Script(tipo=TipoScript.html, nome="registro")
        script.adiciona_linha(u'Ainda não tem conta no Rede?')
        script.adiciona_linha(u'<a href="https://services.redecard.com.br/Novoportal/portals/servico/autocredenciamento.aspx" title="Criar credenciamento no Rede" class="btn btn-info btn-xs" target="_blank">cadastre-se</a>')
        return script

    @property
    def descricao(self):
        script = Script(tipo=TipoScript.html, nome="descricao")
        script.adiciona_linha(u'<p>Descrição e-Rede:</p>')
        return script

    def to_dict(self):
        return {
            "html": [
                self.registro.to_dict(),
                self.descricao.to_dict(),
            ]
        }

PARCELAS = [(x, x) for x in range(1, 19)]
PARCELAS.insert(0, (18, "Todas"))


class Formulario(FormularioBase):
    nome_da_loja = CampoFormulario("usuario", u"Nome do Estabelecimento", requerido=True, tamanho_max=128, ordem=1, texto_ajuda=u"O nome do estabelecimento como foi cadastrado no Rede")
    numero_estabelecimento = CampoFormulario("token", u"Número do Estabelecimento", requerido=True, tamanho_max=128, ordem=2)
    senha = CampoFormulario("senha", u"Senha", requerido=True, tamanho_max=128, ordem=3)
    usar_antifraude = CampoFormulario("usar_antifraude", u"Usar o serviço de Anti Fraude", tipo=TipoDeCampo.boleano, requerido=False, ordem=4)
    mostrar_parcelamento = CampoFormulario("mostrar_parcelamento", "Marque para mostrar o parcelamento na listagem dos produtos e na página do produto.", tipo=TipoDeCampo.boleano, requerido=False, ordem=5)
    maximo_parcelas = CampoFormulario("maximo_parcelas", "Máximo de parcelas", tipo=TipoDeCampo.escolha, requerido=False, ordem=6, texto_ajuda=u"Quantidade máxima de parcelas para esta forma de pagamento.", opcoes=PARCELAS)
    parcelas_sem_juros = CampoFormulario("parcelas_sem_juros", "Parcelas sem juros", tipo=TipoDeCampo.escolha, requerido=False, ordem=7, texto_ajuda=u"Número de parcelas sem juros para esta forma de pagamento.", opcoes=PARCELAS)


class MeioPagamentoEnvio(object):
    @property
    def css(self):
        return Script(tipo=TipoScript.css, caminho_arquivo=caminho_do_arquivo_de_template("style.css"))

    @property
    def function_enviar(self):
        return Script(tipo=TipoScript.javascript, eh_template=True, caminho_arquivo=caminho_do_arquivo_de_template("javascript.js"))

    @property
    def mensagens(self):
        return Script(tipo=TipoScript.html, caminho_arquivo=caminho_do_arquivo_de_template("mensagens.html"), eh_template=True)

    def to_dict(self):
        return [
            self.css.to_dict(),
            self.function_enviar.to_dict(),
            self.mensagens.to_dict()
        ]


class MeioPagamentoSelecao(SelecaoBase):
    selecao = Script(tipo=TipoScript.html, nome="selecao", caminho_arquivo=caminho_do_arquivo_de_template("selecao.html"), eh_template=True)
    script_cartao = Script(tipo=TipoScript.javascript, nome="cartao", caminho_arquivo=caminho_do_arquivo_de_template("script_cartao.js"), eh_template=True)

    def to_dict(self):
        return [
            self.selecao.to_dict(),
            self.script_cartao.to_dict()
        ]
