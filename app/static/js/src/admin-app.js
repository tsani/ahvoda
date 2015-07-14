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
                                    return bserv.getGenders();
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
                                    return bserv.getLanguages();
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
                                        return r;
                                    });
                                }
                            ],
                            genders: [
                                'BusinessService',
                                function(bserv) {
                                    return bserv.getGenders()
                                        .then(function(r) {
                                            return r;
                                        });
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
                    .state('businesses', {
                        url: '/businesses',
                        templateUrl: '/static/views/admin/businesses.html',
                        resolve: {
                            locationData: [
                                '$q',
                                'BusinessService',
                                function($q, bs) {
                                    return $q.all([
                                        bs.getCities(),
                                        bs.getStates(),
                                        bs.getCountries()
                                    ]).then(function(data) {
                                        return {
                                            cities: data[0],
                                            states: data[1],
                                            countries: data[2]
                                        };
                                    });
                                }
                            ],
                            businesses: [
                                'BusinessService',
                                function(bserv) {
                                    return bserv.getBusinesses();
                                }
                            ],
                            languages: [
                                'BusinessService',
                                function(bs) {
                                    return bs.getLanguages();
                                }
                            ]
                        },
                        controller: [
                            '$timeout',
                            '$location',
                            'BusinessService',
                            'UtilityService',
                            'businesses',
                            'locationData',
                            'languages',
                            AdminBusinessListCtrl
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
