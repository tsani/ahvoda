function NewListingDetailsCtrl(
    $state,
    bserv,
    business,
    positions,
    defaultPosition
) {
    var vm = this;

    vm.business = business;

    vm.defaultPosition = defaultPosition;

    vm.data = {
        position: defaultPosition.id
    };

    vm.updateFieldDefaults = function() {
        for(var i = 0; i < positions.length; i++) {
            var p = positions[i];

            if(p.id === vm.data.position) {
                if(p.default_pay) {
                    vm.data.pay = p.default_pay;
                }

                if(p.default_details) {
                    vm.data.details = p.default_details;
                }

                if(p.default_duration) {
                    vm.data.duration = p.default_duration;
                }

                if(p.default_languages) {
                    vm.data.languages = vm.data.languages || {};
                    for(var j = 0; j < p.default_languages.length; j++) {
                        vm.data.languages[p.default_languages[j].iso_name] = true;
                    }
                }
                break;
            }
        }
    }

    vm.fields = [
        {
            key: 'position',
            type: 'select',
            templateOptions: {
                choices: positions.map(function(p) {
                    return {
                        value: p.id,
                        name: p.name,
                        selected: p.id === vm.defaultPosition.id
                    };
                }),
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
        },
        {
            key: 'languages',
            type: 'multicheckbox',
            templateOptions: {
                label: 'Languages',
                choices: business.languages.map(function(lang) {
                    return {
                        name: lang.name,
                        value: lang.iso_name
                    };
                })
            }
        }
    ];

    vm.submit = function() {
        var listingData = {
            details: vm.data.details,
            pay: parseFloat(vm.data.pay),
            duration: parseFloat(vm.data.duration),
            languages: Object.keys(vm.data.languages)
                .filter(function(k) {
                    return vm.data.languages[k];
                })
                .map(function(k) {
                    return {
                        iso_name: k
                    };
                }),
            position: parseInt(vm.data.position)
        };

        bserv.createListing(business, listingData)
            .then(function(response) {
                vm.form.$setSubmitted();
                vm.success = true;
            }, function(response) {
                vm.form.$setSubmitted();
                vm.success = false;
            });
    }

    vm.updateFieldDefaults();
}
