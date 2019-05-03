
$(document).ready(function(event) {
    // Reset input text fields and give focus to main put field
    // Do NOT use $('input') to reset all fields with one single command 
    //  as it would also reset hidden fields used for CSRF protection
    $('#text').val('');
    $('#textnav').val('');
    $('#text').focus();
});


// On submit form, checks if input field is empty before sendinf the request
// No request sent if input field is empty
$('#form').on('submit', function(event) {
    $('.error-msg').remove();
    if ($('#text').val() === '') {
        event.preventDefault();
        $('#form').before("<p class='error-msg'>Veuillez entrer le nom d'un produit !</p>");
    };
});

$('#formnav').on('submit', function(event) {
    $('.error-msg').remove();
    if ($('#textnav').val() === '') {
        event.preventDefault();
        $('#form').before("<p class='error-msg'>Veuillez entrer le nom d'un produit !</p>");
    };
});

$('#back').on('click', function(event) {
    event.preventDefault();
    history.back();
});

$('#contact').on('click', function(event) {
    event.preventDefault();
    $('html, body').animate({
        scrollTop: $('/#contact'.data('scroll')).offset().top
    }, 1000); 
})