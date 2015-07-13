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
                        url: '/employees',
                        templateUrl: '/static/views/admin/employees.html',
                        resolve: {
                            bserv: 'BusinessService',
                            employees: function(bserv) {
                                return bserv.getEmployees();
                            }
                        },
                        controller: [
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
    .run(['formlyConfig', function(formlyConfig) {
        console.log('starting admin app');
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
