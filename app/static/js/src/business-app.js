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
                                '$q',
                                'BusinessService',
                                function($q, bserv) {
                                    return bserv.getManagerBusinesses()
                                        .then(function(bs) {
                                            return $q.all(bs.map(function(b) {
                                                return $q.all([
                                                    bserv.getPositions(b)
                                                        .then(function(ps) {
                                                            b.positions = ps;
                                                            return ps;
                                                        }),
                                                    bserv.getListings(b)
                                                        .then(function(ls) {
                                                            b.listings = ls;
                                                            return ls;
                                                        })
                                                ])
                                                .then(function(bss) {
                                                    return b;
                                                });
                                            }))
                                            .then(function(bs) {
                                                return bs;
                                            });
                                        })
                                        .then(function(bs) {
                                            return bs;
                                        })
                                }
                            ]
                        },
                        controller: [
                            'UtilityService',
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
                                '$q',
                                'BusinessService',
                                function($q, bserv) {
                                    return bserv.getManagerBusinesses()
                                        .then(function(bs) {
                                            return $q.all(bs.map(function(b) {
                                                return $q.all([
                                                    bserv.getPositions(b)
                                                        .then(function(ps) {
                                                            b.positions = ps;
                                                            return ps;
                                                        })
                                                ])
                                                .then(function(bss) {
                                                    return b;
                                                });
                                            }))
                                            .then(function(bs) {
                                                return bs;
                                            });
                                        })
                                        .then(function(bs) {
                                            return bs;
                                        })
                                }
                            ]
                        },
                        controller: [
                            'BusinessService',
                            'UtilityService',
                            'businesses',
                            PositionsListCtrl
                        ],
                        controllerAs: 'vm'
                    })
                    .state('new-listing', {
                        url: '/new-listing/:businessId?positionId',
                        templateUrl: '/static/views/new-listing.html',
                        resolve: {
                            business: [
                                '$stateParams',
                                'BusinessService',
                                function($stateParams, bserv) {
                                    return bserv.getBusiness(
                                        $stateParams.businessId);
                                }
                            ],
                            positions: [
                                'BusinessService',
                                'business',
                                function(bserv, business) {
                                    return bserv.getPositions(business);
                                }
                            ],
                            defaultPosition: [
                                '$stateParams',
                                'positions',
                                function($stateParams, positions) {
                                    if(typeof($stateParams.positionId) === 'undefined') {
                                        return null;
                                    }
                                    var id = parseInt($stateParams.positionId);
                                    for(var i = 0; i < positions.length; i++) {
                                        if(positions[i].id === id)
                                            return positions[i];
                                    }
                                    return null;
                                }
                            ]
                        },
                        controller: [
                            '$state',
                            'BusinessService',
                            'business',
                            'positions',
                            'defaultPosition',
                            NewListingDetailsCtrl,
                        ],
                        controllerAs: 'vm'
                    })
                    .state('new-position', {
                        url: '/new-position?businessId',
                        templateUrl: '/static/views/new-position.html',
                        resolve: {
                            business: [
                                '$stateParams',
                                'BusinessService',
                                function($stateParams, bserv) {
                                    return bserv.getBusiness(
                                        $stateParams.businessId);
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
    .controller('NavCtrl', ['BusinessService', NavCtrl])
    .directive('ahMulticheckbox', ahMulticheckbox)
    .run(['formlyConfig', function(formlyConfig) {
        configureFormly(formlyConfig);
    }]);
