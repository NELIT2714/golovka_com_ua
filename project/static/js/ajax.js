$(document).ready(function() {
    $("#register-form").submit(function(event) {
        event.preventDefault();
        let email = $("#email").val();
        let password = $("#password").val();
        let confirmPassword = $("#confirm-password").val();

        if (password != confirmPassword) {
            $("#message").text("Пароли не совпадают");
            $("#reg-btn").attr("disabled", true);
            return;
        }

        $.ajax({
            type: "POST",
            url: "/sign-up/",
            data: {
                "email": email,
                "password": password,
                "confirm_password": confirmPassword
            },
            success: function(response) {
                if (response["status"] == "success") {
                    $("#message").text("Особистий кабінет створено!");
                } else if (response["status"] == "error") {
                    $("#message").text(response["message"]);
                } else if (response["status"] == "redirect") {
                    window.location.href = response.redirect;
                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    $("#login-form").submit(function(event) {
        event.preventDefault();
        let email = $("#email").val();
        let password = $("#password").val();

        $.ajax({
            type: "POST",
            url: "/sign-in/",
            data: {
                "email": email,
                "password": password
            },
            success: function(response) {
                if (response["status"] == "success") {
                    $("#message").text(response["message"]);
                } else if (response["status"] == "error") {
                    $("#message").text(response["message"]);
                } else if (response["status"] == "redirect") {
                    window.location.href = response.redirect;
                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    $("#add-to-cart").submit(function(event) {
        event.preventDefault();
        let product_id = $("#product_id").val()
        let amount = $("#amount").val()

        $.ajax({
        url: "/add-to-cart/",
        type: "POST",
        data: {
            "product_id": product_id,
            "amount": amount
        },
        success: function(response) {
            console.log(response["message"])
        },
        error: function(error) {
            console.log(error);
        }
        });
    });

    $("form[id^='remove-from-cart']").submit(function(event) {
        event.preventDefault();
        let product_id = $(this).find("#product_id").val();
        let form_id = $(this).attr("id");
    
        $.ajax({
            url: "/remove-from-cart/",
            type: "POST",
            data: {
                "product_id": product_id
            },
            success: function(response) {
                console.log(response["message"]);
                $("body").html(response["cart_html"]);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});