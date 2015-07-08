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
                            bserv: 'BusinessService',
                            businesses: [
                                'bserv',
                                function(bserv) {
                                    return bserv.getBusinesses();
                                }
                            ],
                            managers: [
                                'bserv',
                                function(bserv) {
                                    return bserv.getManagers();
                                }
                            ],
                            listings: [
                                'bserv',
                                function(bserv) {
                                    return bserv.getListings();
                                }
                            ],
                            employees: [
                                'bserv',
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
                            util: 'UtilityService',
                            bserv: 'BusinessService',
                            businesses: [
                                'bserv', 
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
                                'bserv',
                                function(bserv) {
                                    return bserv.getManagers();
                                }
                            ]
                        },
                        controller: [
                            'util',
                            'bserv',
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
                            bserv: 'BusinessService',
                            util: 'UtilityService',
                            employees: [
                                'bserv',
                                function(bserv) {
                                    return bserv.getEmployees();
                                }
                            ],
                            listings: [
                                'bserv',
                                function(bserv) {
                                    return bserv.getListings();
                                }
                            ]
                        },
                        controller: [
                            'bserv',
                            'util',
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
