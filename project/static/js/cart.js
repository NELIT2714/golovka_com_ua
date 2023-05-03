$(document).on('click', '#amount-add', function() {
    let $form = $(this).closest('form');
    let product_id = $form.find('input[name="product_id"]').val();
    let amount = parseInt($form.find('input[name="amount"]').val()) + 1;
    if (amount > 100) amount = 100;
    updateCart(product_id, amount, $form);
});

$(document).on('click', '#amount-minus', function() {
    let $form = $(this).closest('form');
    let product_id = $form.find('input[name="product_id"]').val();
    let amount = parseInt($form.find('input[name="amount"]').val()) - 1;
    if (amount < 1) amount = 1;
    updateCart(product_id, amount, $form);
});

$(document).on('change', '#amount', function() {
    let $form = $(this).closest('form');
    let product_id = $form.find('input[name="product_id"]').val();
    let amount = parseInt($(this).val());
    if (amount < 1) amount = 1;
    if (amount > 100) amount = 100;
    updateCart(product_id, amount, $form);
});

function updateCart(product_id, amount, $form) {
    $.ajax({
        url: "/update-cart/",
        type: "POST",
        data: {
            "product_id": product_id,
            "amount": amount
        },
        success: function(response) {
            $form.find('input[name="amount"]').val(amount);
            $form.find('.price-cart').text(response["finall_price"]);
            
            $('.total-price-cart').text(response["total_price"]);
            $('.total-amount').text(response["total_amount"]);
        },
        error: function(error) {
            console.log(error);
        }
    });
}