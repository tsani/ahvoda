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
        business.delete = function() {
            return bserv.deleteBusiness(business.id)
                .then(function(response) {
                    if(response.status == 204) {
                        for(var i = 0; i < vm.businesses.length; i++) {
                            if(vm.businesses[i].id === business.id) {
                                vm.businesses.splice(i, 1)
                                return;
                            }
                        }
                        console.log('wtf: business delete succeeded server-' +
                                'side, but the business could not be found' +
                                ' client-side.');
                    }
                    else {
                        // TODO show this in the UI
                        console.log('business delete failed');
                    }
                });
        }
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
                    choices: locationData.countries
                }
            },
            {
                key: 'state',
                type: 'select',
                templateOptions: {
                    label: 'State/Province',
                    choices: locationData.states
                }
            },
            {
                key: 'city',
                type: 'select',
                templateOptions: {
                    label: 'City',
                    choices: locationData.cities
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
            fixed_location: {
                address: m.address,
                city_id: m.city.id,
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
