var app = angular.module('app', []);

function mainShift(direction) {
    cards = $('#card-list');
    topCard = cards.find('> :first-child');
    nextCard = cards.children().eq(1);

    console.log('yo');


    if(topCard.attr('id') === 'last-card') {
        return false;
    }

    options = {
        'opacity': 0.0,
    };

    if(direction === 'left') {
        options.left = 0 - topCard.width();
        response = "That's too bad! We'll let the business know.";
    }
    else if(direction === 'right') {
        options.left = window.innerWidth;
        response = "That's great! We'll let the business know.";
    }
    else {
        console.log('bad direction');
    }

    topCard.animate(options, {
        'complete': function() {
            topCard.remove();
        },
        duration: 150
    });
    nextCard.animate({
        'opacity': 1.0
    });

    return response;
}

app.controller('SwipeController', function($scope) {
    $scope.response = "";

    $scope.cards = [
        {
            name: "McDonald's",
            address: "1337 McTavish",
            distance: "About 0.4km",
            position: "Cashier",
            industry: "Food & Drink",
            duties: [
                "Quickly serve customers",
                "Keep the cash area clean",
                "Manage multiple orders simultaneously",
            ],
            qualities: [
                "Friendly",
                "Quick on your feet",
                "Fast learner"
            ],
            extra: []
        }
    ];

    $scope.shift = function(direction) {
        $scope.response = mainShift(direction);
    }
});

$(document).on('keydown', function(e) {
    switch(e.which) {
        case 37:
            direction = "left";
            break;
        case 39:
            direction = "right";
            break;
        default:
            return;
    }

    e.preventDefault();

    response = mainShift(direction);

    $('#response-header').text(response);
});


