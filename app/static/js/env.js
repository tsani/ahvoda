$.fn.exists = function () {
    return this.length !== 0;
}

var cycleStrategy = {
    serial: function(container, period) {
        var e = container.find(':first-child');
        var next = e.next();
        e.fadeOut(period/4, function() {
            next.fadeIn(period/4, function() {
                e.appendTo(container);
            });
        });
    },
    parallel: function(container, period) {
        var e = container.find(':first-child');
        e.fadeOut(period/4)
         .next()
         .fadeIn(period/4, function() {
             e.appendTo(container);
         });
    }
};

/* Cycles children of a given container by fading them in and out, *serially*.
 * This is as opposed to fading them in and out in parallel.
 */
function cycle(container, strategy) {
    container = $(container);
    var speed = container.attr('data-cycle-period');
    var delay = container.attr('data-cycle-delay');

    if(typeof(speed) === 'undefined') {
        speed = 2000;
    }

    if(typeof(speed) === 'undefined') {
        delay = 0;
    }

    var update = function() {
        strategy(container, speed);
    };

    setTimeout(function() {
        if(delay > 0)
            update();

        setInterval(function() {
            strategy(container, speed)
        }, speed);
    }, delay);
}

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

    $('.cycle-serial').each(function(i, e) {
        cycle(e, cycleStrategy.serial);
    });

    $('.cycle-parallel').each(function(i ,e) {
        cycle(e, cycleStrategy.parallel);
    });
});

$(document).ready(function() {
    $('input#position-new-text').focus(function() {
        $('input#position-new').prop('checked', true);
    });
});
