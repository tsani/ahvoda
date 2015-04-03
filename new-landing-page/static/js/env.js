setInterval(function() {
    $('.carousel :first-child').fadeOut()
                               .next('img')
                               .fadeIn()
                               .end()
                               .appendTo('.carousel');
}, 4000);
