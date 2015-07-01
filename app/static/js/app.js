(function() {

function ListingCreatorService() {
    var srv = this;

    var _initialData = {
        languages: {}
    };

    srv.data = {};

    srv.reset = function reset() {
        srv.data = angular.copy(_initialData);
    }

    srv.reset();
}

function LocationSelectService() {
    var srv = this;

    console.log('initialized location select service');

    srv.locations = [];
}
    
function BusinessService($q, $http) {
    var srv = this;

    srv.username = window.username;

    srv.getBusinesses = function() {
        return $http.get('/api/manager/' + this.username + '/businesses')
            .then(function(response) {
                return response.data.businesses;
            });
    };

    // TODO refactor these two into a "groupByBusiness" helper

    srv.getListingGroups = function(businesses) {
        return $q.all(businesses.map(function(b) {
            return srv.getListings(b)
                .then(function(listings) {
                    return {
                        business: b,
                        listings: listings
                    };
                });
        })).then(function(listingGroups) {
            var ret = {};
            for(var i = 0; i < listingGroups.length; i++)
                ret[listingGroups[i].business.name] = listingGroups[i].listings;
            return ret;
        });
    };

    srv.getPositionGroups = function(businesses) {
        return $q.all(businesses.map(function(b) {
            return srv.getPositions(b)
                .then(function(positions) {
                    return {
                        business: b,
                        positions: positions
                    };
                });
        })).then(function(positionGroups) {
            var ret = {};
            for(var i = 0; i < positionGroups.length; i++)
                ret[positionGroups[i].business.name] = positionGroups[i].positions;
            return ret;
        });
    };

    srv.getBusiness = function(businessId) {
        return $http.get('/api/business/' + businessId)
            .then(function(response) {
                return response.data;
            });
    }

    srv.getListings = function(business) {
        return $http.get('/api/listings', {
            business: business.id
        }).then(function(response) {
            return response.data.listings;
        });
    }

    srv.createListing = function(business, listing) {
        return $http.post(
                '/api/business/' + business.id + '/listings', listing)
            .then(function(response) {
                return response.data;
            });
    }

    srv.getPositions = function(business) {
        return $http.get('/api/business/' + business.id + '/positions')
            .then(function(response) {
                return response.data.positions;
            });
    }

    srv.createPosition = function(business, name) {
        return $http.post('/api/business/' + business.id + '/positions', {
            name: name
        }).then(function(response) {
            return response.data;
        }, function(response) {
            console.log(JSON.stringify(response));
        });
    }

    srv.patchPosition = function(business, positionId, name) {
        return $http.patch(
                '/api/business/' + business.id + '/positions/' + positionId, {
                    name: name
                });
    }

    srv.deletePosition = function(business, positionId) {
        return $http.delete(
                '/api/business/' + business.id + '/positions/' + positionId);
    }

    srv.getManager = function() {
        return $http.get(
                '/api/manager/' + srv.username)
            .then(function(response) {
                return response.data;
            });
    }

    srv.businesses = [];
    srv.positions = {};
    srv.manager = {};

    srv.loadAll = function() {
        srv.getManager()
            .then(function(data) {
                srv.manager = data;
            });
        return srv.getBusinesses()
            .then(function(businesses) {
                srv.getListingGroups(businesses)
                    .then(function(listingGroups) {
                        srv.listingGroups = listingGroups;
                    });

                srv.getPositionGroups(businesses)
                // Clear the businesses array.
                srv.businesses.splice(0, srv.businesses.length);
                // Populate it with the businesses obtained in the response
                businesses.forEach(function(b) {
                    srv.businesses.push(b);
                });
            });
    };

    srv.loadAll();

    console.log('Initialized BusinessService.');
}

function ListingsListCtrl(listingGroups, businesses) {
    var vm = this;

    vm.listingGroups = listingGroups;
    vm.businesses = businesses;

    vm.formatAddress = function(location) {
        return [
            location.address,
            location.city.name,
            location.city.state.name,
            location.city.state.country.name
        ].join(', ');
    };
}

function PositionsListCtrl(positionGroups, businesses) {
    var vm = this;

    vm.positionGroups = positionGroups;
    vm.businesses = businesses;
}

function NewListingDetailsCtrl($state, lserv, bserv, business, positions) {
    var vm = this;

    vm.back = function() {
        console.log('going back a step');
        lserv.reset();
        $state.go('^.select-location');
    }

    vm.data = lserv.data;

    vm.updateFieldDefaults = function() {
        console.log('updating field defaults for', vm.data.position);
        for(var i = 0; i < positions.length; i++) {
            var p = positions[i];
            if(p.id == vm.data.position) {
                if(p.name === 'Busboy') {
                    vm.data.pay = 11;
                    vm.data.details = 'Bus tables.';
                    vm.data['language-en'] = true;
                    vm.data.duration = 3;
                }
                else if(p.name == 'Dishwasher') {
                    vm.data.pay = 12;
                    vm.data.details = [
                        'Wash dishes, glassware, flatware, pots, and pans using dishwashing machine or by hand.',
                        'Place clean dishes, utensils, and cooking equipment in the appropriate storage areas.',
                        'Maintain cleanliness of kitchen work areas, equipment, and utensils.'
                    ].join('\n\n');
                    vm.data['language-en'] = true;
                    vm.data.duration = 4;
                }
                else if(p.name == 'Floor washer') {
                    vm.data.pay = 14;
                    vm.data.details = 'Wash floors';
                    vm.data['language-en'] = true;
                    vm.data.duration = 2;
                }
            }
        }
    }

    vm.fields = [
        {
            key: 'position',
            type: 'select',
            templateOptions: {
                choices: positions,
                getValue: function(p) { return p.id; },
                getContent: function(p) { return p.name; },
                label: 'Position',
                required: true,
                onChange: vm.updateFieldDefaults
            }
        },
        {
            key: 'pay',
            type: 'input',
            templateOptions: {
                type: 'number',
                label: 'Hourly pay',
                placeholder: '11',
                required: true
            }
        },
        {
            key: 'details',
            type: 'textarea',
            templateOptions: {
                rows: 7,
                label: 'Details',
                placeholder: 'Describe the duties of the worker.',
                required: true
            }
        },
        {
            key: 'duration',
            type: 'input',
            templateOptions: {
                label: 'Duration (hours)',
                type: 'number',
                placeholder: '3.5',
                required: true
            }
        }
    ].concat(business.languages.map(function(lang) {
        return {
            key: 'language-' + lang.iso_name,
            type: 'input',
            templateOptions: {
                type: 'checkbox',
                label: lang.name
            }
        };
    }));

    vm.submit = function() {
        var listingData = {
            details: vm.data.details,
            pay: parseFloat(vm.data.pay),
            duration: parseFloat(vm.data.duration),
            languages: [],
            position: parseInt(vm.data.position)
        };

        business.languages.forEach(function(lang) {
            var lang_model = vm.data['language-' + lang.iso_name];
            if(typeof(lang_model) !== 'undefined' && lang_model) {
                listingData.languages.push({
                    iso_name: lang.iso_name
                });
            }
        });

        bserv.createListing(business, listingData)
            .then(function(response) {
                vm.form.$setSubmitted();
            }, function(response) {
                console.log(JSON.stringify(response))
            });
    }
}

function NewPositionDetailsCtrl($state, business, positions, bserv) {
    var vm = this;

    vm.data = {};
    vm.fields = [
        {
            key: 'positionName',
            type: 'input',
            templateOptions: {
                label: 'Position name',
                type: 'text',
                placeholder: 'A name applicants will see when searching for listings.',
                required: true
            }
        }
    ];

    vm.submit = function() {
        bserv.createPosition(business, vm.data.positionName)
            .then(function(data) {
                vm.form.$setSubmitted();
            });
    };
}

function NavCtrl(bserv) {
    var vm = this;
    vm.manager = {};
    bserv.getManager()
        .then(function(manager) {
            vm.manager = manager;
        });
}

function makeLocationSelectCtrl(successState) {
    function LocationSelectCtrl($state, locationSelectServ, businesses) {
        var vm = this;

        vm.data = {};

        vm.fields = [
            {
                key: 'location',
                type: 'select',
                templateOptions: {
                    label: 'Location',
                    choices: businesses,
                    getValue: function(b) {
                        return b.id;
                    },
                    getContent: function(b) {
                        return b.name;
                    },
                    label: 'Location',
                    required: true 
                }
            }
        ];

        vm.next = function() {
            locationSelectServ.locations.push(angular.copy(vm.data));
            $state.go(successState);
        }
    }

    console.log('make location select controller');

    return LocationSelectCtrl;
}

angular
    .module('app', ['ui.router', 'formly'])
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
                            bserv: 'BusinessService',
                            businesses: function(bserv) {
                                console.log('getting businesses');
                                return bserv.getBusinesses()
                                    .then(function(businesses) {
                                        console.log('got businesses',
                                            JSON.stringify(businesses));
                                        return businesses;
                                    });
                            },
                            listingGroups: [
                                'businesses',
                                'bserv',
                                function(businesses, bserv) {
                                    console.log('getting listing groups for', 
                                        JSON.stringify(businesses));
                                    return bserv.getListingGroups(businesses)
                                        .then(function(data) {
                                            console.log('heyhye');
                                            console.log(JSON.stringify(data));
                                            return data;
                                        });
                                }
                            ]
                        },
                        controller: [
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
                                    return bserv.getBusinesses();
                                }
                            ],
                            positionGroups: [
                                'bserv',
                                'businesses',
                                function(bserv, businesses) {
                                    console.log('getting position groups');
                                    return bserv.getPositionGroups(businesses)
                                        .then(function(positionGroups) {
                                            console.log(
                                                JSON.stringify(positionGroups));
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
                                    console.log('hi');
                                    return bserv.getBusinesses()
                                        .then(function(data) {
                                            console.log('hello');
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
                                    console.log('hi');
                                    return bserv.getBusinesses()
                                        .then(function(data) {
                                            console.log('hello');
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
                                    console.log('get positions');
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

})();
