function businessAppConfig($stateProvider, $urlRouterProvider) {
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
                                        bserv.getPositions(b.id)
                                            .then(function(ps) {
                                                b.positions = ps;
                                                return ps;
                                            }),
                                        bserv.getListings(b)
                                            .then(function(ls) {
                                                b.listings = ls.map(function(l) {
                                                    l.delete = function() {
                                                        bserv.deleteListing(b.id, l.id)
                                                            .then(function() {
                                                                for(var i = 0; i < b.listings.length; i++) {
                                                                    var q = b.listings[i];
                                                                    if(q.id === l.id) {
                                                                        b.listings.splice(i, 1);
                                                                        return;
                                                                    }
                                                                }
                                                            });
                                                    };
                                                    return l;
                                                });
                                                return b.listings;
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
                                        bserv.getPositions(b.id)
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
                        return bserv.getPositions(business.id);
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
                'BusinessService',
                'ListingFormService',
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
                        return bserv.getPositions(business.id);
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
        })
        .state('edit-listing', {
            url: '/edit-listing/:businessId?listingId',
            templateUrl: '/static/views/edit-listing.html',
            resolve: {
                business: [
                    '$stateParams',
                    'BusinessService',
                    function($stateParams, bserv) {
                        return bserv.getBusiness($stateParams.businessId)
                    }
                ],
                positions: [
                    'BusinessService',
                    'business',
                    function(bserv, b) {
                        return bserv.getPositions(b.id);
                    }
                ],
                listing: [
                    '$stateParams',
                    'BusinessService',
                    'business',
                    function($stateParams, bserv, b) {
                        return bserv.getListing(b.id, $stateParams.listingId);
                    }
                ]
            },
            controller: [
                'BusinessService',
                'ListingFormService',
                'business',
                'listing',
                'positions',
                ListingEditCtrl
            ],
            controllerAs: 'vm'
        });
}
