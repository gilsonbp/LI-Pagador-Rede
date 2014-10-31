//{% load filters %}
var url = '';
var $counter = null;
var segundos = 5;
$(function() {
    var $pagSeguroMensagem = $(".pagseguro-mensagem");

    function iniciaContador() {
        $counter = $pagSeguroMensagem.find(".segundos");
        setInterval('if (segundos > 0) { $counter.text(--segundos); }', 1000);
    }

    function enviaPagamento() {
        $pagSeguroMensagem.find(".msg-danger").hide();
        $pagSeguroMensagem.find(".msg-success").hide();
        $pagSeguroMensagem.find(".msg-warning").show();
        $pagSeguroMensagem.removeClass("alert-message-success");
        $pagSeguroMensagem.removeClass("alert-message-danger");
        $pagSeguroMensagem.addClass("alert-message-warning");
        var url_pagar = '{% url_loja "checkout_pagador" pedido.numero pagamento.id %}?next_url=' + window.location.href.split("?")[0];
        $.getJSON(url_pagar)
            .fail(function (data) {
                exibeMensagemErro(data.status, data.content);
            })
            .done(function (data) {
                if (data.sucesso) {
                    $("#aguarde").hide();
                    $("#redirecting").show();
                    url = data.content.url;
                    iniciaContador();
                    setTimeout('window.location = url;', 5000);
                }
                else {
                    if (data.status == 400 || data.status == 401) {
                        exibeMensagemErro(data.status, "Ocorreu um erro ao enviar os dados para o PagSeguro. Por favor, tente de novo");
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
        $pagSeguroMensagem.find(".msg-warning").hide();
        $pagSeguroMensagem.toggleClass("alert-message-warning alert-message-danger");
        var $errorMessage = $("#errorMessage");
        $errorMessage.text(status + ": " + mensagem);
        $pagSeguroMensagem.find(".msg-danger").show();
        if (fatal) {
            $(".pagar").remove();
            $(".click").remove();
        }
    }

    function exibeMensagemSucesso(situacao) {
        $pagSeguroMensagem.find(".msg-warning").hide();
        $pagSeguroMensagem.toggleClass("alert-message-warning alert-message-success");
        var $success = $pagSeguroMensagem.find(".msg-success");
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
        exibeMensagemErro(500, "Pagamento cancelado no PagSeguro!");
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
