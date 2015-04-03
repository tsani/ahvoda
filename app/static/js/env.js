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
        $('#email .contents').append("<p>Gotcha! We'll keep you posted.</p>");
    }, 'json').fail(function(data) {
        $('#email .contents').append("<p>Uh oh! Something's up. Have you already registered for updates? " +
            data.message + "</p>");
    });
}
