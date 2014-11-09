//{% load filters %}
var url = '';
var $counter = null;
var segundos = 5;
$(function() {
    var $redeMensagem = $(".rede-mensagem");

    function iniciaContador() {
        $counter = $redeMensagem.find(".segundos");
        setInterval('if (segundos > 0) { $counter.text(--segundos); }', 1000);
    }

    function enviaPagamento() {
        $redeMensagem.find(".msg-danger").hide();
        $redeMensagem.find(".msg-success").hide();
        $redeMensagem.find(".msg-warning").show();
        $redeMensagem.removeClass("alert-message-success");
        $redeMensagem.removeClass("alert-message-danger");
        $redeMensagem.addClass("alert-message-warning");
        var url_pagar = '{% url_loja "checkout_pagador" pedido.numero pagamento.id %}?passo=fulfill';
        $.getJSON(url_pagar)
            .fail(function (data) {
                exibeMensagemErro(data.status, data.content);
            })
            .done(function (data) {
                console.log(data);
                if (data.sucesso) {
                    $("#aguarde").hide();
                    exibeMensagemSucesso("pago");
                }
                else {
                    if (data.status == 400 || data.status == 401) {
                        exibeMensagemErro(data.status, "Ocorreu um erro ao enviar os dados para o Rede. Por favor, tente de novo");
                    }
                    else if (data.status == 404) {
                        var fatal = false;
                        if (data.content.hasOwnProperty("fatal")) {
                            fatal = data.content.fatal;
                        }
                        exibeMensagemErro(data.status, data.content.mensagem, fatal);
                    }
                    else {
                        if ('{{ settings.DEBUG }}' == 'True') {
                            exibeMensagemErro(data.status, data.content);
                        }
                        else {
                            exibeMensagemErro(data.status, "Ocorreu um erro ao enviar sua solicitação. Se o erro persistir, contate nosso SAC.");
                        }
                    }
                }
            });
    }

    $(".msg-danger").on("click", ".pagar", function() {
        enviaPagamento();
    });

    $(".msg-success").on("click", ".ir-mp", function() {
        window.location = url;
    });

    function exibeMensagemErro(status, mensagem, fatal) {
        $redeMensagem.find(".msg-warning").hide();
        $redeMensagem.toggleClass("alert-message-warning alert-message-danger");
        var $errorMessage = $("#errorMessage");
        $errorMessage.text(status + ": " + mensagem);
        $redeMensagem.find(".msg-danger").show();
        if (fatal) {
            $(".pagar").remove();
            $(".click").remove();
        }
    }

    function exibeMensagemSucesso(situacao) {
        $redeMensagem.find(".msg-warning").hide();
        $redeMensagem.toggleClass("alert-message-warning alert-message-success");
        var $success = $redeMensagem.find(".msg-success");
        $success.find("#redirecting").hide();
        if (situacao == "pago") {
            $success.find("#successMessage").show();
        }
        else {
            $success.find("#pendingMessage").show();
        }
        $success.show();
    }

    var pedidoPago = '{{ pedido.situacao_id }}' == '4';
    var pedidoAguardandoPagamento = '{{ pedido.situacao_id }}' == '2';

    if (window.location.search != "" && window.location.search.indexOf("failure") > -1) {
        exibeMensagemErro(500, "Pagamento cancelado no Rede!");
    }
    else if (window.location.search != "" && window.location.search.indexOf("success") > -1 || pedidoPago) {
        exibeMensagemSucesso("pago");
    }
    else if (window.location.search != "" && window.location.search.indexOf("pending") > -1 || pedidoAguardandoPagamento) {
        exibeMensagemSucesso("aguardando");
    }
    else {
        enviaPagamento();
    }
});