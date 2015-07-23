function AdminManagersListCtrl(util, bserv, genders, businesses, managers) {
    var vm = this;
    vm.managers = managers;

    vm.util = util;

    vm.newManagerFormModel = {};
    vm.newManagerFormFields = [
        {
            key: 'username',
            type: 'input',
            templateOptions: {
                type: 'text',
                label: 'Username',
                required: true
            }
        },
        {
            key: 'password',
            type: 'input',
            templateOptions: {
                type: 'password',
                label: 'Password',
                required: true
            }
        },
        {
            key: 'firstName',
            type: 'input',
            templateOptions: {
                type: 'text',
                label: 'First name',
                required: true
            }
        },
        {
            key: 'lastName',
            type: 'input',
            templateOptions: {
                type: 'text',
                label: 'Last name',
                required: true
            }
        },
        {
            key: 'emailAddress',
            type: 'input',
            templateOptions: {
                type: 'email',
                label: 'Email address',
                required: true
            }
        },
        {
            key: 'phoneNumber',
            type: 'input',
            templateOptions: {
                type: 'tel',
                label: 'Phone number',
                required: true
            }
        },
        {
            key: 'gender',
            type: 'select',
            templateOptions: {
                choices: genders,
                label: 'Gender',
                required: true
            }
        },
        {
            key: 'birthDate',
            type: 'input',
            templateOptions: {
                type: 'text',
                label: 'Date of birth (yyyy-mm-dd)',
                required: true
            }
        }
    ];

    function registerManager(manager) {
        if(typeof(manager.businesses) === 'undefined')
            manager.businesses = [];

        var bs = businesses.map(function(b) {
            return {
                name: b.name + ' (' +
                          vm.util.formatAddress(b.fixed_location) +
                          ')',
                id: b.id
            };
        });

        manager.formModel = {};
        manager.formFields = [
            {
                key: 'business',
                type: 'select',
                templateOptions: {
                    choices: bs,
                    required: true
                }
            }
        ];

        manager.dissociateBusiness = function(businessId) {
            bserv.removeManagerFromBusiness(manager.username, businessId)
                .then(function(response) {
                    if(response.status == 204) {
                        for(var i = 0; i < manager.businesses.length; i++) {
                            var business = manager.businesses[i];
                            if(business.id === businessId) {
                                manager.businesses.splice(i, 1);
                                return;
                            }
                        }
                        console.log('wtf');
                    }
                    else
                        console.log('Delete failed.');
                });
        };

        manager.associateBusiness = function() {
            bserv.addManagerToBusiness(
                manager.username,
                manager.formModel.business.id)
                .then(function(business) {
                    manager.businesses.push(business);
                });
        };

        manager.delete = function() {
            bserv.deleteManager(manager.username)
                .then(function(response) {
                    if(response.status == 204) {
                        for(var i = 0; i < vm.managers.length; i++) {
                            if(vm.managers[i].username === manager.username) {
                                vm.managers.splice(i, 1);
                                return;
                            }
                        }
                        console.log('wtf!');
                    }
                    else
                        console.log('failed to delete manager');
                });
        }
    }

    vm.updateManagers = function() {
        for(var i = 0; i < vm.managers.length; i++) {
            (function(manager) {
                bserv.getManagerBusinesses(manager.username)
                    .then(function(businesses) {
                        manager.businesses = businesses;
                        registerManager(manager);
                    });
            })(vm.managers[i]);
        }
    };

    vm.createManager = function() {
        var m = vm.newManagerFormModel;
        bserv.createManager({
            username: m.username,
            password: m.password,
            first_name: m.firstName,
            last_name: m.lastName,
            gender_id: m.gender.id,
            birth_date: m.birthDate + 'T00:00:00Z',
            email_address: m.emailAddress,
            phone_number: m.phoneNumber
        }).then(function(manager) {
            vm.managers.push(manager);
            registerManager(manager);
        });
    }

    vm.updateManagers();
}
