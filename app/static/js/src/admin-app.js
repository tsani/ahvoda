angular
    .module('AdminApp', ['ui.router', 'formly'])
    .config(['$stateProvider', '$urlRouterProvider',
            function($stateProvider, $urlRouterProvider) {
                $urlRouterProvider.otherwise('/overview');
                $stateProvider
                    .state('overview', {
                        url: '/overview',
                        templateUrl: '/static/views/admin/overview.html',
                        resolve: {
                            businesses: [
                                'BusinessService',
                                function(bserv) {
                                    return bserv.getBusinesses();
                                }
                            ],
                            managers: [
                                'BusinessService',
                                function(bserv) {
                                    return bserv.getManagers();
                                }
                            ],
                            listings: [
                                'BusinessService',
                                function(bserv) {
                                    return bserv.getListings();
                                }
                            ],
                            employees: [
                                'BusinessService',
                                function(bserv) {
                                    return bserv.getEmployees();
                                }
                            ]
                        },
                        controller: [
                            'businesses',
                            'listings',
                            'employees',
                            'managers',
                            AdminOverviewCtrl
                        ],
                        controllerAs: 'vm'
                    })
                    .state('managers', {
                        url: '/managers',
                        templateUrl: '/static/views/admin/managers.html',
                        resolve: {
                            businesses: [
                                'BusinessService',
                                function(bserv) {
                                    return bserv.getBusinesses();
                                }
                            ],
                            genders: [
                                'BusinessService',
                                function(bserv) {
                                    return bserv.getGenders()
                                        .then(function(gs) {
                                            console.log(JSON.stringify(gs));
                                            return gs;
                                        });
                                }
                            ],
                            managers: [
                                'BusinessService',
                                function(bserv) {
                                    return bserv.getManagers();
                                }
                            ]
                        },
                        controller: [
                            'UtilityService',
                            'BusinessService',
                            'genders',
                            'businesses',
                            'managers',
                            AdminManagersListCtrl
                        ],
                        controllerAs: 'vm'
                    })
                    .state('employees', {
                        url: '/contractors',
                        templateUrl: '/static/views/admin/employees.html',
                        resolve: {
                            languages: [
                                'BusinessService',
                                function(bserv) {
                                    return bserv.getLanguages()
                                        .then(function(r) {
                                            console.log(JSON.stringify(r));
                                            return r;
                                        });
                                }
                            ],
                            locationData: [
                                '$q',
                                'BusinessService',
                                function($q, bserv) {
                                    return $q.all({
                                        countries: bserv.getCountries(),
                                        states: bserv.getStates(),
                                        cities: bserv.getCities()
                                    }).then(function(r) {
                                        console.log(JSON.stringify(r));
                                        return r;
                                    });
                                }
                            ],
                            genders: [
                                'BusinessService',
                                function(bserv) {
                                    return bserv.getGenders()
                                        .then(function(r) {
                                            console.log(JSON.stringify(r));
                                            return r;
                                        });
                                }
                            ],
                            employees: [
                                'BusinessService',
                                function(bserv) {
                                    return bserv.getEmployees()
                                        .then(function(r) {
                                            console.log(JSON.stringify(r));
                                            return r;
                                        });
                                }
                            ]
                        },
                        controller: [
                            '$timeout',
                            'BusinessService',
                            'UtilityService',
                            'languages',
                            'genders',
                            'locationData',
                            'employees',
                            AdminEmployeesListCtrl
                        ],
                        controllerAs: 'vm'
                    })
                    .state('listings', {
                        url: '/listings',
                        templateUrl: '/static/views/admin/listings.html',
                        resolve: {
                            employees: [
                                'BusinessService',
                                function(bserv) {
                                    return bserv.getEmployees();
                                }
                            ],
                            listings: [
                                'BusinessService',
                                function(bserv) {
                                    return bserv.getListings();
                                }
                            ]
                        },
                        controller: [
                            'BusinessService',
                            'UtilityService',
                            'employees',
                            'listings',
                            AdminListingsListCtrl
                        ],
                        controllerAs: 'vm'
                    });
            }
    ])
    .service('BusinessService', ['$q', '$http', BusinessService])
    .service('UtilityService', UtilityService)
    .controller('NavCtrl', ['BusinessService', NavCtrl])
    .directive('ahMulticheckbox', ahMulticheckbox)
    .directive('ahManager', ahManager)
    .run(['formlyConfig', function(formlyConfig) {
        configureFormly(formlyConfig);
    }]);
