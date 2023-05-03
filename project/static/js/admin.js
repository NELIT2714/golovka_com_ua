$(document).ready(function() {
    // Добавление категории
    $("#add-category").submit(function(event) {
        event.preventDefault();
        let form_data = new FormData($(this)[0]);
        form_data.append("category-name", $("#category-name").val());
        form_data.append("category-image", $("#category-image").val());
    
        $.ajax({
            url: "/add-category/",
            type: "POST",
            data: form_data,
            processData: false,
            contentType: false,
            success: function(response) {
                $("body").html(response["html"])
                $("#add-category").trigger('reset');
                add_modal("Повідомлення", response["message"], "Продовжити")
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    // Добавление продукта
    $("#add-product").submit(function(event) {
        event.preventDefault();
        let form_data = new FormData($(this)[0]);
        form_data.append("name", $("#name").val());
        form_data.append("price", $("#price").val());
        form_data.append("category", $("#category").val());
        form_data.append("product_image", $("#product-image").val());
        form_data.append("short_description", $("#short-description").val());
        form_data.append("html_description", $("#html-description").val());
    
        $.ajax({
            url: "/add-product/",
            type: "POST",
            data: form_data,
            processData: false,
            contentType: false,
            success: function(response) {
                $("body").html(response["html"])
                $("#add-product").trigger('reset');
                add_modal("Повідомлення", response["message"], "Продовжити")
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    // Удаление категории
    $(".categories-table").on("click", "button:contains('Видалити')", function() {
        let categoryId = $(this).closest("tr").attr("id");
        $.ajax({
            url: "/remove-category/" + categoryId + "/",
            method: "POST",
            success: function(response) {
                $("body").html(response["html"])
                add_modal("Повідомлення", response["message"], "Продовжити")
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    // Удаление продукта
    $(".product-table").on("click", "button:contains('Видалити')", function() {
        let productId = $(this).closest("tr").attr("id");
        $.ajax({
            url: "/remove-product/" + productId + "/",
            method: "POST",
            success: function(response) {
                $("body").html(response["html"])
                add_modal("Повідомлення", response["message"], "Продовжити")
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    
    if ($(".desc-container").length) {
        $(".format").click(function() {
            let button = $(this);
            let textarea = $("#html-description");
            let tag = button.attr("class").split(" ")[1];
            let selectedText = textarea.val().substring(textarea[0].selectionStart, textarea[0].selectionEnd);
            let textBeforeSelection = textarea.val().substring(0, textarea[0].selectionStart);
            let textAfterSelection = textarea.val().substring(textarea[0].selectionEnd, textarea.val().length);
    
            let formattedText = "<" + tag + "> " + selectedText + " </" + tag + ">";
            textarea.val(textBeforeSelection + formattedText + textAfterSelection);
        });
    };
});

function add_modal(title, content, btn_text) {
    let modal_content = $('#modal-template').contents().clone();

    let modal_title = modal_content.find('.modal-title');
    modal_title.text(title);

    let modal_text = modal_content.find('.modal-text');
    modal_text.text(content);

    let btn = modal_content.find('.btn');

    btn.text(btn_text);

    btn.on('click', function() {
        modal_section.hide();
        overlay.removeClass("active");
    });

    let modal_section = $('<div class="modal-section"></div>');
    let overlay = $(".js-overlay-modal")

    modal_section.on('click', function(event) {
        if (event.target === this) {
        $(this).hide();
        }
    });

    overlay.addClass("active");
    modal_section.append(modal_content);

    $('body').append(modal_section);
}