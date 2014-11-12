//{% load filters %}

var camposObrigatorios = ["#cartao_nome", "#cartao_numero", "#cartao_data_expiracao", "#cartao_cvv"];
$(function() //noinspection JSUnresolvedVariable,JSUnresolvedVariable
{
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

    var pagamento = {% autoescape off %}{{ pagamento|to_json }}{% endautoescape %};

    function preencheParcelas() {
        var valor = $(".pagamento-valor").text().replace("R$", "").trim();
        if (valor) {
            if (valor.indexOf(",") > -1) {
                valor = valor.replace(/[\.|\,]/g, "");
            }
            valor = parseInt(valor) / 100;
        }
        var listaParcelas = [];
        var todas_parcelas = [];
        if (pagamento["maximo_parcelas"]) {
            todas_parcelas = pagamento["parcelas"].slice(0, pagamento["maximo_parcelas"]);
        }
        else if (pagamento["parcelas_sem_juros"]) {
            todas_parcelas = pagamento["parcelas"].slice(0, pagamento["parcelas_sem_juros"]);
        }
        else {
            todas_parcelas = pagamento["parcelas"];
        }

        for (var indiceParcela = 0; indiceParcela < todas_parcelas.length; indiceParcela++) {
            var parcela = todas_parcelas[indiceParcela];
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
                listaParcelas.push(parcela)
            }
        }
        var options = ['<option value="1">A Vista</option>'];
        for (var i = 1; i < listaParcelas.length; i++) {
            var parcela = listaParcelas[i];
            options.push('<option value="' + parcela["numero_parcelas"] + '">' + parcela["numero_parcelas"] + 'x de R$ ' + parcela["valor_parcelado"] + (parcela["sem_juros"] ? " sem juros": "") + '</option>');
        }
        $("#cartao_parcelas").html(options.join());
    }
    $('.rede .preco-carrinho-total').on("carrinho.valor_alterado", function() {
        preencheParcelas();
    });
    preencheParcelas();
});
