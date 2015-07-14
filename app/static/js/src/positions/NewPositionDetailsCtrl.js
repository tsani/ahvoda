function NewPositionDetailsCtrl($state, business, positions, bserv) {
    var vm = this;

    vm.business = business;
    vm.positionId = undefined;

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
        },
        {
            key: 'defaultPay',
            type: 'input',
            templateOptions: {
                label: 'Default hourly pay',
                type: 'number',
                placeholder: 'This pay can be adjusted on a per-job basis.',
                required: true
            }
        },
        {
            key: 'defaultDetails',
            type: 'textarea',
            templateOptions: {
                label: 'Default job description',
                placeholder: 'The job details can be adjusted on a per-job basis.',
                required: true
            }
        },
        {
            key: 'defaultLanguages',
            type: 'multicheckbox',
            templateOptions: {
                choices: business.languages.map(function(e) {
                    return {
                        name: e.name,
                        value: e.iso_name
                    };
                }),
                label: 'Default languages',
                minimumRequired: 1
            }
        }
    ];

    vm.submit = function() {
        bserv.createPosition(business, {
            name: vm.data.positionName,
            default_pay: vm.data.defaultPay,
            default_details: vm.data.defaultDetails,
            default_languages:
                Object.keys(vm.data.defaultLanguages)
                    .filter(function(k) {
                        return vm.data.defaultLanguages[k];
                    })
                    .map(function(k) {
                        return {
                            iso_name: k
                        };
                    })
        }).then(function(position) {
            vm.form.$setSubmitted();
            vm.positionId = vm.data.position;
            vm.position = position;
        });
    };
}
