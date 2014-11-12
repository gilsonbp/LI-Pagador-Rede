var camposObrigatorios = ["#cartao_nome", "#cartao_numero", "#cartao_data_expiracao", "#cartao_cvv"];
$(function() {
    $("#formas-pagamento-wrapper").on("click", "#finalizarCompra", function(event) {
        zeraValidacao();
        if (!$("#radio-rede").is(":checked")) {
            return true;
        }
        var validacao_ok = true;
        for (var i in camposObrigatorios) {
            var $campo = $(camposObrigatorios[i]);
            if ($campo.val() == "") {
                campoInvalido($campo);
                validacao_ok = false;
            }
            else if (camposObrigatorios[i] == "#cartao_data_expiracao") {
                var partes = $campo.val().split("/");
                if (partes.length != 2) {
                    campoInvalido($campo, "informe mês e ano");
                    validacao_ok = false;
                }
                if (parseInt(partes[0]) < 1 || parseInt(partes[0]) > 12) {
                    campoInvalido($campo, "mês deve ser entre 01 e 12");
                    validacao_ok = false;
                }
                var ano = parseInt(String(new Date().getFullYear()).slice(2));
                if (parseInt(partes[1]) < ano) {
                    campoInvalido($campo, "ano deve ser " + ano + " ou mais");
                    validacao_ok = false;
                }
            }
        }
        if (!validacao_ok) {
            event.preventDefault();
            return false;
        }
    });
    function zeraValidacao() {
        var $control = $(".control-group");
        $control.removeClass("error");
        $control.find(".help-block").hide();
    }
    function campoInvalido($campo, mensagem) {
        var $group = $campo.parents(".control-group");
        $group.addClass("error");
        if (!mensagem) {
            mensagem = "este campo é obrigatório";
        }
        $group.find(".help-block").text(mensagem);
        $group.find(".help-block").show();
    }
    zeraValidacao();
    $("#cartao_numero").mask("9999 9999 9999 9999", {"placeholder": "•"});
    $("#cartao_data_expiracao").mask("99/99");
    $("#cartao_cvv").mask("999");
    if ($("#radio-rede").is(":checked")) {
        $("#escolha-rede").addClass("in");
    }
    $('.rede .preco-carrinho-total').on("carrinho.valor_alterado", function() {
        Parcela.preencheParcelas();
    });
    $("#cartao_parcelas").change(function() {
        var $this = $(this);
        var $option = $this.find("option[value='" + $this.val() + "']");
        $("#cartao_parcelas_sem_juros").val($option.data("sem-juros"));
    });
});


var Parcela = {
    init: function(pagamento, seletorValor, seletorParcelas) {
        this.$campoValor = $(seletorValor);
        this.$campoParcelas = $(seletorParcelas);
        this._atualizaValor();
        this.pagamento = pagamento;
    },
    _atualizaValor: function() {
        var valor = this.$campoValor.text().replace("R$", "").trim();
        if (valor) {
            if (valor.indexOf(",") > -1) {
                valor = valor.replace(/[\.|\,]/g, "");
            }
            this.valor = parseInt(valor) / 100;
        }
        else {
            this.valor = 0.0
        }
    },
    _renderizaOption: function(parcela) {
        return [
            '<option data-sem-juros="{}"'.replace("{}", parcela["sem_juros"]),
                'value="{}">'.replace("{}", parcela["numero_parcelas"]),
                '{}x de R$ {}'.replace("{}", parcela["numero_parcelas"]).replace("{}", parcela["valor_parcelado"]),
                (parcela["sem_juros"] ? " sem juros": ""),
            '</option>'
        ].join("");
    },
    _parcelasPossiveis: function() {
        this.pagamento;
        var resultado = [];
        if (this.pagamento["maximo_parcelas"]) {
            resultado = this.pagamento["parcelas"].slice(0, this.pagamento["maximo_parcelas"]);
        }
        else if (this.pagamento["parcelas_sem_juros"]) {
            resultado = this.pagamento["parcelas"].slice(0, this.pagamento["parcelas_sem_juros"]);
        }
        else {
            resultado = this.pagamento["parcelas"];
        }
        return resultado;
    },
    _parcelasResultantes: function () {
        this._atualizaValor();
        var pagamento = this.pagamento;
        var valor = this.valor;
        var parcelasPosiveis = this._parcelasPossiveis();
        var parcelasResultantes = [];
        for (var indiceParcela = 0; indiceParcela < parcelasPosiveis.length; indiceParcela++) {
            var parcela = parcelasPosiveis[indiceParcela];
            var sem_juros = false;
            var valor_parcelado = parcela["fator"] * valor;
            if (pagamento["parcelas_sem_juros"] && pagamento["parcelas_sem_juros"] >= parcela["numero_parcelas"]) {
                sem_juros = true;
                valor_parcelado = valor / parcela["numero_parcelas"]
            }
            if (valor_parcelado > pagamento["valor_minimo_parcela"]) {
                parcela = {
                    'valor_parcelado': valor_parcelado.toFixed(2).replace(".", ",").replace(/\d(?=(\d{3})+\,)/g, '$&.'),
                    'numero_parcelas': parcela["numero_parcelas"],
                    'sem_juros': sem_juros
                };
                parcelasResultantes.push(parcela)
            }
        }
        return parcelasResultantes;
    },
    preencheParcelas: function() {
        var parcelasResultantes = this._parcelasResultantes();

        var options = ['<option data-sem-juros="false" value="1">À Vista</option>'];
        for (var i = 1; i < parcelasResultantes.length; i++) {
            options.push(this._renderizaOption(parcelasResultantes[i]));
        }
        this.$campoParcelas.html(options.join());
    }
};