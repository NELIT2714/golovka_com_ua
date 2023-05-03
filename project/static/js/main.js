$("#register-form").bind("change", function() {
    let password = $("#password").val();
    let confirmPassword = $("#confirm-password").val();

    if (password != confirmPassword) {
        $("#message").text("Пароли не совпадают");
        $("#reg-btn").attr("disabled", true);
        return;
    } else {
        $("#message").text("");
        $("#reg-btn").attr("disabled", false);
        return;
    }
});

if ($("#amount-btns").length) {
    let amount = parseInt($("#amount").val());
    let amount_add_btn = $("#amount-add");
    let amount_minus_btn = $("#amount-minus");

    amount_add_btn.on("click", () => {
        if (amount < 100) {
            amount += 1;
            $("#amount").attr("value", amount);
        } else {
            $("#amount").attr("value", 100);
        };
    });

    amount_minus_btn.on("click", () => {
        if (amount > 1) {
            amount -= 1;
            $("#amount").attr("value", amount);
        }
    });

    $("#amount").on("blur", () => {
        if (amount <= 100) {
            $("#amount").attr("value", amount);
        } else if (amount > 100) {
            $("#amount").attr("value", 100);
        } else if (amount < 1) {
            $("#amount").attr("value", 1);
        };
    });
};

if ($(".add-product").length) {
    $("#to_cart_btn").click(function(){
        $(".modal, .overlay").addClass("active")
        $("body").css("overflow", "hidden");
    });

    $("#continue_shopping").click(function(){
        $(".modal, .overlay").removeClass("active")
        $("body").css("overflow", "");
    });
};

if ($(".profile-links").length) {
    $("ul.profile-links li").click(function() {
        $("ul.profile-links li").removeClass("active");
        $(this).addClass("active");

        let targetUrl = $(this).data("target");
        
        $.ajax({
            type: "POST",
            url: `/${targetUrl}/`,
            success: function(response) {
                $(".profile-content").html(response);
            },
            error: function(xhr, status, error) {
                console.error(error);
            }
        });
    });
};