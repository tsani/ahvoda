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

function unfold(element, height, complete) {
    // Make the element visible
    element.show();

    if(typeof(complete) === 'undefined')
        complete = function() {};

    if(typeof(height) === 'undefined' || height === null) {
        // Get its initial height
        var initialHeight = element.height();
        // Set its height to auto; the browser will now compute its height.
        element.css('height', 'auto');
        // Get the height computed by the browser
        height = element.outerHeight();
        // Reset the height to its initial height.
        element.css('height', initialHeight);
    }

    element.animate({
            "height": height
    }, 500, function() {
        element.css('height', 'auto');
        complete();
    });
}

function foldup(element, complete) {
    if(typeof(complete) === 'undefined')
        complete = function() {};

    element.animate({
        "height": 0
    }, 500, function() {
        element.hide();
        complete();
    });
}

function formToObject(formElement) {
    formElement = $(formElement);

    var formData = {};

    $.each(formElement.serializeArray(), function(i, e) {
        if(!e.name) {
            // TODO exception
        }
        formData[e.name] = e.value;
    });

    return formData;
}

function subscribeUser() {
    var data = formToObject($('#signup-form'));
    console.log(JSON.stringify(data));
    $.ajax({
        url: "/api/subscribe",
        type: "POST",
        contentType: "application/json",
        dataType: "json",
        data: JSON.stringify(data),
        success: function(data) {
            foldup($('#signup-form'), function() {
                unfold($('#signup-result'));
            });
            $('html, body').animate({
                scrollTop: 0
            }, 500);
        },
        error: function(data) {
            if(typeof(data.responseJSON) !== 'undefined') {
                data = data.responseJSON;
                if(typeof(data.offendingName) !== 'undefined') {
                    $('#signup-container .errors').remove();
                    var badField = $(
                        '#signup-container *[name="' +
                        data.offendingName +
                        '"]');
                    badField.after(
                        "<p class='errors'>" + data.message + "</p>");
                }
                else {
                    console.log("no offending name; ", data.message);
                }
            }
            else {
                console.log("no response json");
            }
        }
    });
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

    // Smooth scrolling for same-page anchors.
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

    // Register event handlers for any foldout forms.
    // Get a jQuery object of the signup form and activate button
    var signupForm = $('#signup-container');
    var signupActivateButton = $('#signup-activate');

    signupActivateButton.click(function() {
        var signupFormInitialMinHeight = signupForm.parent().css('min-height');
        // Ensure that when we're doing any fading in and out / hiding elements
        // that the parent container doesn't shrink (bad UX !)
        signupForm.parent().css(
            'min-height', signupForm.parent().outerHeight());

        // Animate the height "unfolding".
        signupActivateButton.fadeOut(500, function() {
            unfold(signupForm);

            signupForm.css('opacity', 0);
            signupForm.animate({
                opacity: 1
            },
            500, function() {
                signupForm.parent().css(
                    'min-height', signupFormInitialMinHeight);
            });
        });
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
