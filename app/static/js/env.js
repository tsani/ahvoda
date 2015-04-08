setInterval(function() {
    $('.carousel :first-child').fadeOut()
                               .next('img')
                               .fadeIn()
                               .end()
                               .appendTo('.carousel');
}, 4000);

$(function() {
    function scrollFadeCheck() {
        // Check the location of each desired element
        $('.scrollfade').each( function(i) {
            var top_of_object = $(this).offset().top;
            var bottom_of_window = $(window).scrollTop() + $(window).height();

            // If the object is completely visible in the window, fade it it
            if( bottom_of_window > top_of_object ) {
                $(this).animate({
                    opacity: 1,
                }, 500);

                $(this).removeClass('scrollfade');
            }
        });
    }

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
    /* Every time the window is scrolled ... */
    $(window).scroll(scrollFadeCheck);

    scrollFadeCheck();
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
        $('#survey-request').show();
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
        else if(data.message === 'invalid email address') {
            $('#register-result-message').text(
                "Uh oh, that email address doesn't look valid!");
        }
        else {
            $('#register-result-message').html([
                "Something went wrong adding your email address;",
                "try again later, or if this keeps happening, contact",
                "<a href='mailto:jake@mail.ahvoda.com'>Jake</a>"].join(' '));
        }
    });
}
