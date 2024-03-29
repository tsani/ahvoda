function AdminBusinessListCtrl(
    $timeout,
    $location,
    bserv,
    util,
    businesses,
    locationData,
    languages
) {
    var vm = this;

    vm.businesses = businesses;
    vm.util = util;

    function registerBusiness(business) {
        business.managers = [];
        bserv.getBusinessManagers(business.id)
            .then(function(managers) {
                business.managers = managers;
            });
    }

    for(var i = 0; i < vm.businesses.length; i++) {
        registerBusiness(vm.businesses[i]);
    }

    vm.createForm = {
        fields: [
            {
                key: 'name',
                type: 'input',
                templateOptions: {
                    type: 'text',
                    label: 'Name'
                }
            },
            {
                key: 'description',
                type: 'textarea',
                templateOptions: {
                    label: 'Description'
                }
            },
            {
                key: 'address',
                type: 'input',
                templateOptions: {
                    type: 'text',
                    label: 'Address'
                }
            },
            {
                key: 'postalCode',
                type: 'input',
                templateOptions: {
                    type: 'text',
                    label: 'Postal code'
                }
            },
            {
                key: 'country',
                type: 'select',
                templateOptions: {
                    label: 'Country',
                    choices: locationData.countries.map(function(c) {
                        return {
                            name: c.name,
                            value: c.id
                        }
                    })
                }
            },
            {
                key: 'state',
                type: 'select',
                templateOptions: {
                    label: 'State/Province',
                    choices: locationData.states.map(function(c) {
                        return {
                            name: c.name,
                            value: c.id
                        };
                    })
                }
            },
            {
                key: 'city',
                type: 'select',
                templateOptions: {
                    label: 'City',
                    choices: locationData.cities.map(function(c) {
                        return {
                            name: c.name,
                            value: c.id
                        };
                    })
                }
            },
            {
                key: 'emailAddress',
                type: 'input',
                templateOptions: {
                    type: 'email',
                    label: 'Email address'
                }
            },
            {
                key: 'phoneNumber',
                type: 'input',
                templateOptions: {
                    type: 'tel',
                    label: 'Phone number'
                }
            },
            {
                key: 'languages',
                type: 'multicheckbox',
                templateOptions: {
                    label: 'Languages',
                    choices: languages.map(function(lang) {
                        return {
                            name: lang.name,
                            value: lang.iso_name
                        };
                    })
                }
            }
        ]
    };

    vm.createBusiness = function() {
        var m = vm.createForm.model;
        bserv.createBusiness({
            name: m.name,
            description: m.description,
            location: {
                address: m.address,
                city_id: parseInt(m.city),
                postal_code: m.postalCode
            },
            contact_info: {
                email_address: m.emailAddress,
                phone_number: m.phoneNumber
            },
            languages: Object.keys(m.languages)
                .filter(function(k) {
                    return m.languages[k];
                })
                .map(function(k) {
                    return {
                        iso_name: k
                    };
                })
        }).then(function(business) {
            registerBusiness(business);
            vm.createForm.data.$setSubmitted();
            vm.businesses.push(business);
            $timeout(function() {
                $location.hash('business-li-' + business.id);
                vm.createForm.data.$reset();
            }, 2000);
        });
    }
}
