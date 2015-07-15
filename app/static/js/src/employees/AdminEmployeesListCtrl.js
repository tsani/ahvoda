function AdminEmployeesListCtrl($timeout, bserv, util, languages, genders, locationData, employees) {
    var vm = this;
    vm.util = util;

    vm.employees = employees;

    vm.newEmployeeFormModel = {};
    vm.newEmployeeFormFields = [
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
        },
        {
            key: 'address',
            type: 'input',
            templateOptions: {
                type: 'text',
                label: 'Street address',
                required: true
            }
        },
        {
            key: 'postalCode',
            type: 'input',
            templateOptions: {
                type: 'text',
                label: 'Postal code',
                required: true
            }
        },
        {
            key: 'country',
            type: 'select',
            templateOptions: {
                choices: locationData.countries,
                label: 'Country'
            }
        },
        {
            key: 'province',
            type: 'select',
            templateOptions: {
                choices: locationData.states,
                label: 'State/Province'
            }
        },
        {
            key: 'city',
            type: 'select',
            templateOptions: {
                choices: locationData.cities,
                label: 'City'
            }
        },
        {
            key: 'languages',
            type: 'multicheckbox',
            templateOptions: {
                choices: languages.map(function(lang) {
                    return {
                        name: lang.name,
                        value: lang.iso_name
                    };
                }),
                label: 'Languages',
                minimumRequired: 1
            }
        }
    ];

    vm.createEmployee = function() {
        var m = vm.newEmployeeFormModel;
        if(typeof(m.languages) === 'undefined') {
            m.languages = {};
        }
        bserv.createEmployee({
            username: m.username,
            password: m.password,
            email_address: m.emailAddress,
            phone_number: m.phoneNumber,
            postal_code: m.postalCode,
            first_name: m.firstName,
            last_name: m.lastName,
            gender_id: m.gender.id,
            birth_date: m.birthDate + 'T00:00:00Z',
            address: m.address,
            city_id: m.city.id,
            languages:
                Object.keys(m.languages)
                    .filter(function(k) {
                        return m.languages[k];
                    })
                    .map(function(k) {
                        return {
                            iso_name: k
                        };
                    })
        }).then(function(employee) {
            vm.employees.unshift(employee);
            vm.newEmployeeFormData.$setSubmitted();
            $timeout(function() {
                vm.options.resetModel();
            }, 750);
        }, function(failureResponse) {
            console.log("failed.");
        });
    };
}
