setInterval(function() {
    $('.carousel :first-child').fadeOut()
                               .next('img')
                               .fadeIn()
                               .end()
                               .appendTo('.carousel');
}, 4000);

$(function() {
    $('a[href*=#]:not([href=#])').click(function() {
        if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
            if (target.length) {
                $('html,body').animate({
                    scrollTop: target.offset().top
                }, 1000);
                return false;
            }
        }
    });
});

var emailSent = false;

function registerEmail() {
    if(emailSent) {
        return false;
    }

    var email = $('#email-field').val();
    $.post('/api/addemail', JSON.stringify({email: email}), function(data) {
        emailSent = true;
        $('#register-result-message').text("Gotcha! We'll keep you posted.");
    }, 'json').fail(function(data) {
        data = JSON.parse(data.responseText);
        console.log(JSON.stringify(data));
        if(data.message === 'email too long') {
            $('#register-result-message').text(
                "Looks like the email address you gave is a bit too long!");
        }
        else if(data.message === 'user already exists') {
            $('#register-result-message').text(
                "Looks like you've already given us your email. Thanks!");
        }
        else {
            $('#register-result-message').html([
                "Something went wrong adding your email address;",
                "try again later, or if this keeps happening, contact",
                "<a href='mailto:jake@mail.ahvoda.com'>Jake</a>"].join(' '));
        }
    });
}
