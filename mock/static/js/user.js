var app = angular.module('app', []);

app.controller('SwipeController', function($scope) {
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
        },
        {
            name: "Brigade",
            address: "651 Stanley",
            distance: "About 0.9km",
            position: "Kitchen helper",
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
        },
        {
            name: "Peel Pub",
            address: "404 Peel",
            distance: "About 0.8km",
            position: "Bartender",
            industry: "Food & Drink",
            duties: [
                "Process transactions fast",
                "Keep tabs on the customers",
            ],
            qualities: [
                "Friendly",
                "Quick on your feet",
                "Fast learner"
            ],
            extra: []
        }
    ];
});

user = (function() {
    function shift(direction) {
        cards = $('#card-list');
        topCard = cards.find('> :first-child');
        nextCard = cards.children().eq(1);

        if(topCard.attr('id') === 'last-card') {
            return false;
        }

        options = {
            'opacity': 0.0,
        };

        if(direction === 'left') {
            options.left = 0 - topCard.width();
        }
        else if(direction === 'right') {
            options.left = window.innerWidth;
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
    }

    $(document).keydown(function(e) {
        switch(e.which) {
            case 37:
                shift('left');
                break;
            case 39:
                shift('right');
                break;
            default:
                return;
        }

        e.preventDefault();
    });

    return {
        'shift': shift
    };
})();

