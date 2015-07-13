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
                            businesses: [
                                'BusinessService',
                                function(bserv) {
                                    return bserv.getManagerBusinesses();
                                }
                            ],
                            listingGroups: [
                                'businesses',
                                'BusinessService',
                                function(businesses, bserv) {
                                    return bserv.getListingGroups(businesses);
                                }
                            ]
                        },
                        controller: [
                            'UtilityService',
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
                            businesses: [
                                'BusinessService',
                                function(bserv) {
                                    return bserv.getManagerBusinesses();
                                }
                            ],
                            positionGroups: [
                                'BusinessService',
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
                            locserv: 'LocationSelectService',
                            businesses: [
                                'BusinessService',
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
                            business: [
                                'LocationSelectService',
                                'BusinessService',
                                function(locserv, bserv) {
                                    return bserv.getBusiness(
                                            locserv.locations.pop().location);
                                }
                            ],
                            positions: [
                                'BusinessService',
                                'business',
                                function(bserv, business) {
                                    return bserv.getPositions(business);
                                }
                            ]
                        },
                        controller: [
                            '$state',
                            'ListingCreatorService',
                            'BusinessService',
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
                            businesses: [
                                'BusinessService',
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
                            'LocationSelectService',
                            'businesses',
                            makeLocationSelectCtrl('new-position.details')
                        ],
                        controllerAs: 'locationSelect'
                    })
                    .state('new-position.details', {
                        url: '/details',
                        templateUrl: '/static/views/new-position/details.html',
                        resolve: {
                            business: [
                                'LocationSelectService',
                                'BusinessService',
                                function(locserv, bserv) {
                                    return bserv.getBusiness(
                                            locserv.locations.pop().location);
                                }
                            ],
                            positions: [
                                'business',
                                'BusinessService',
                                function(business, bserv) {
                                    return bserv.getPositions(business);
                                }
                            ]
                        },
                        controller: [
                            '$state',
                            'business',
                            'positions',
                            'BusinessService',
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
    .directive('ahMulticheckbox', ahMulticheckbox)
    .run(['formlyConfig', function(formlyConfig) {
        configureFormly(formlyConfig);
    }]);
