# -*- coding: utf-8 -*-

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
        script.adiciona_linha(u'<a href="https://services.redecard.com.br/Novoportal/portals/servico/autocredenciamento.aspx" title="Criar credenciamento no Rede" class="btn btn-info btn-xs" target="_blank">credenciamento</a>')
        return script

    @property
    def descricao(self):
        return Script(tipo=TipoScript.html, nome="descricao", eh_template=True, caminho_arquivo=caminho_do_arquivo_de_template("painel_descricao.html"))

    def to_dict(self):
        return {
            "html": [
                self.registro.to_dict(),
                self.descricao.to_dict(),
            ]
        }

PARCELAS = [(x, x) for x in range(1, 13)]
PARCELAS.insert(0, (12, "Todas"))


class Formulario(FormularioBase):
    ambiente = CampoFormulario("aplicacao", u"Ambiente", tipo=TipoDeCampo.escolha, requerido=True, opcoes=(('H', u'Homologação'), ('P', u'Produção')), ordem=1, texto_ajuda=u"Use Homologação para testar seu credenciamento junto à Rede. Use Produção quando a Rede autorizar seu credenciamento.")
    nome_da_loja = CampoFormulario("usuario", u"Nome do Estabelecimento", requerido=True, tamanho_max=13, ordem=2, texto_ajuda=u"O nome do estabelecimento junto à Rede. Máx de 13 caracteres")
    numero_estabelecimento = CampoFormulario("token", u"Número do Estabelecimento", requerido=True, tamanho_max=128, ordem=3, texto_ajuda=u"Número de identificação junto à Rede, fornecido após adesão do serviço.")
    senha = CampoFormulario("senha", u"Senha", requerido=True, tamanho_max=128, ordem=4, texto_ajuda=u"Senha fornecido pela Rede.")
    usar_antifraude = CampoFormulario("usar_antifraude", u"Usar o serviço de Anti Fraude", tipo=TipoDeCampo.boleano, requerido=False, ordem=5, texto_ajuda=u"Consulte mais informações junto à <a href='https://www.userede.com.br/pt-BR/produtosservicos/Paginas/ecommerce-antifraude.aspx' target='_blank'>Rede</a>")
    juros_valor = CampoFormulario("juros_valor", u"Taxa de Juros", requerido=False, decimais=2, ordem=6, tipo=TipoDeCampo.decimal, texto_ajuda=u"Informe a taxa de juros para sua loja na Rede")
    valor_minimo_aceitado = CampoFormulario("valor_minimo_aceitado", u"Valor mínimo", requerido=False, decimais=2, ordem=7, tipo=TipoDeCampo.decimal, texto_ajuda=u"Informe o valor mínimo para exibir esta forma de pagamento.")
    valor_minimo_parcela = CampoFormulario("valor_minimo_parcela", u"Valor mínimo da parcela", requerido=False, decimais=2, ordem=8, tipo=TipoDeCampo.decimal)
    mostrar_parcelamento = CampoFormulario("mostrar_parcelamento", "Marque para mostrar o parcelamento na listagem e na página do produto.", invisivel=True, valor_padrao=True, tipo=TipoDeCampo.boleano, requerido=False, ordem=9)
    maximo_parcelas = CampoFormulario("maximo_parcelas", "Máximo de parcelas", tipo=TipoDeCampo.escolha, requerido=False, ordem=10, texto_ajuda=u"Quantidade máxima de parcelas para esta forma de pagamento.", opcoes=PARCELAS)
    parcelas_sem_juros = CampoFormulario("parcelas_sem_juros", "Parcelas sem juros", tipo=TipoDeCampo.escolha, requerido=False, ordem=11, texto_ajuda=u"Número de parcelas sem juros para esta forma de pagamento.", opcoes=PARCELAS)


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
    script_cartao = Script(tipo=TipoScript.javascript, nome="cartao", caminho_arquivo=caminho_do_arquivo_de_template("script_cartao.js"))

    def to_dict(self):
        if not self.aceita_pagamento_no_valor():
            return []
        return [
            self.script_cartao.to_dict(),
            self.selecao.to_dict(),
        ]
