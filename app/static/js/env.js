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

$(document).ready(function() {
    $('input#position-new-text').focus(function() {
        $('input#position-new').prop('checked', true);
    });
});
