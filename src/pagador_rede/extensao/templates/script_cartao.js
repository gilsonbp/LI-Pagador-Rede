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
    $("#cartao_numero").mask("9999 9999 9999 9999");
    $("#cartao_data_expiracao").mask("99/99");
    $("#cartao_cvv").mask("999");
    if ($("#radio-rede").is(":checked")) {
        $("#escolha-rede").addClass("in");
    }
});
