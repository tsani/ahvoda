angular
    .module('BusinessApp', ['ui.router', 'formly'])
    .config(['$stateProvider', '$urlRouterProvider',
            function($stateProvider, $urlRouterProvider) {
                $urlRouterProvider.otherwise('/listings');
                $stateProvider
                    .state('help', {
                        url: '/help',
                        templateUrl: '/static/views/help.html'
                    })
                    .state('listings', {
                        url: '/listings',
                        templateUrl: '/static/views/listings.html',
                        resolve: {
                            util: 'UtilityService',
                            bserv: 'BusinessService',
                            businesses: function(bserv) {
                                return bserv.getManagerBusinesses();
                            },
                            listingGroups: [
                                'businesses',
                                'bserv',
                                function(businesses, bserv) {
                                    return bserv.getListingGroups(businesses);
                                }
                            ]
                        },
                        controller: [
                            'util',
                            'listingGroups',
                            'businesses',
                            ListingsListCtrl
                        ],
                        controllerAs: 'vm'
                    })
                    .state('positions', {
                        url: '/positions',
                        templateUrl: '/static/views/positions.html',
                        resolve: {
                            bserv: 'BusinessService',
                            businesses: [
                                'bserv',
                                function(bserv) {
                                    return bserv.getManagerBusinesses();
                                }
                            ],
                            positionGroups: [
                                'bserv',
                                'businesses',
                                function(bserv, businesses) {
                                    return bserv.getPositionGroups(businesses)
                                        .then(function(positionGroups) {
                                            return positionGroups;
                                        });
                                }
                            ]
                        },
                        controller: [
                            'positionGroups',
                            'businesses',
                            PositionsListCtrl
                        ],
                        controllerAs: 'vm'
                    })
                    // State for creating a new listing
                    .state('new-listing', {
                        url: '/new-listing',
                        templateUrl: '/static/views/new-listing.html',
                        controller: [
                            '$state',
                            function($state) {
                                $state.go('new-listing.select-location');
                            }
                        ]
                    })
                    .state('new-listing.select-location', {
                        url: '/select-location',
                        templateUrl: '/static/views/select-location.html',
                        resolve: {
                            bserv: 'BusinessService',
                            locserv: 'LocationSelectService',
                            businesses: [
                                'bserv', 
                                function(bserv) {
                                    return bserv.getManagerBusinesses()
                                        .then(function(data) {
                                            return data;
                                        });
                                }
                            ]
                        },
                        controller: [
                            '$state',
                            'locserv',
                            'businesses',
                            makeLocationSelectCtrl('new-listing.details')
                        ],
                        controllerAs: 'locationSelect'
                    })
                    .state('new-listing.details', {
                        url: '/:businessId',
                        templateUrl: '/static/views/new-listing/details.html',
                        resolve: {
                            bserv: 'BusinessService',
                            lserv: 'ListingCreatorService',
                            locserv: 'LocationSelectService',
                            business: [
                                'locserv',
                                'bserv',
                                function(locserv, bserv) {
                                    return bserv.getBusiness(
                                            locserv.locations.pop().location);
                                }
                            ],
                            positions: [
                                'bserv',
                                'business',
                                function(bserv, business) {
                                    return bserv.getPositions(business);
                                }
                            ]
                        },
                        controller: [
                            '$state',
                            'lserv',
                            'bserv',
                            'business',
                            'positions',
                            NewListingDetailsCtrl,
                        ],
                        controllerAs: 'vm'
                    })
                    .state('new-position', {
                        url: '/new-position',
                        templateUrl: '/static/views/new-position.html',
                        controller: [
                            '$state',
                            function($state) {
                                $state.go('new-position.select-location');
                            }
                        ]
                    })
                    .state('new-position.select-location', {
                        url: '/select-location',
                        templateUrl: '/static/views/select-location.html',
                        resolve: {
                            bserv: 'BusinessService',
                            locserv: 'LocationSelectService',
                            businesses: [
                                'bserv',
                                function(bserv) {
                                    return bserv.getManagerBusinesses()
                                        .then(function(data) {
                                            return data;
                                        });
                                }
                            ]
                        },
                        controller: [
                            '$state',
                            'locserv',
                            'businesses',
                            makeLocationSelectCtrl('new-position.details')
                        ],
                        controllerAs: 'locationSelect'
                    })
                    .state('new-position.details', {
                        url: '/details',
                        templateUrl: '/static/views/new-position/details.html',
                        resolve: {
                            locserv: 'LocationSelectService',
                            bserv: 'BusinessService',
                            business: [
                                'locserv',
                                'bserv',
                                function(locserv, bserv) {
                                    return bserv.getBusiness(
                                            locserv.locations.pop().location);
                                }
                            ],
                            positions: [
                                'business',
                                'bserv',
                                function(business, bserv) {
                                    return bserv.getPositions(business);
                                }
                            ]
                        },
                        controller: [
                            '$state',
                            'business',
                            'positions',
                            'bserv',
                            NewPositionDetailsCtrl
                        ],
                        controllerAs: 'vm'
                    });
            }
    ])
    .service('BusinessService', ['$q', '$http', BusinessService])
    .service('UtilityService', UtilityService)
    .service('LocationSelectService', LocationSelectService)
    .service('ListingCreatorService', ListingCreatorService)
    .controller('NavCtrl', ['BusinessService', NavCtrl])
    .run(['formlyConfig', function(formlyConfig) {
        // Configure all form types.
        [
            {
                name: 'input',
                templateUrl: '/static/widgets/form/basic-input.html'
            },
            {
                name: 'textarea',
                templateUrl: '/static/widgets/form/textarea-input.html'
            },
            {
                name: 'select',
                templateUrl: '/static/widgets/form/select.html'
            },
            {
                name: 'checkbox',
                templateUrl: '/static/widgets/form/checkbox.html'
            }
        ].forEach(function(e) {
            formlyConfig.setType(e);
        });
    }]);
