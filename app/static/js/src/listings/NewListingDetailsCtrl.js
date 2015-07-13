function NewListingDetailsCtrl($state, lserv, bserv, business, positions) {
    var vm = this;

    vm.back = function() {
        console.log('going back a step');
        lserv.reset();
        $state.go('^.select-location');
    }

    vm.data = lserv.data;

    vm.updateFieldDefaults = function() {
        console.log('updating field defaults for', vm.data.position);
        for(var i = 0; i < positions.length; i++) {
            var p = positions[i];
            if(p.id == vm.data.position) {
                if(p.name === 'Busboy') {
                    vm.data.pay = 11;
                    vm.data.details = 'Bus tables.';
                    vm.data['language-en'] = true;
                    vm.data.duration = 3;
                }
                else if(p.name == 'Dishwasher') {
                    vm.data.pay = 12;
                    vm.data.details = [
                        'Wash dishes, glassware, flatware, pots, and pans using dishwashing machine or by hand.',
                        'Place clean dishes, utensils, and cooking equipment in the appropriate storage areas.',
                        'Maintain cleanliness of kitchen work areas, equipment, and utensils.'
                    ].join('\n\n');
                    vm.data['language-en'] = true;
                    vm.data.duration = 4;
                }
                else if(p.name == 'Floor washer') {
                    vm.data.pay = 14;
                    vm.data.details = 'Wash floors';
                    vm.data['language-en'] = true;
                    vm.data.duration = 2;
                }
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
                        name: p.name
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
        }
    ].concat(business.languages.map(function(lang) {
        return {
            key: 'language-' + lang.iso_name,
            type: 'input',
            templateOptions: {
                type: 'checkbox',
                label: lang.name
            }
        };
    }));

    vm.submit = function() {
        var listingData = {
            details: vm.data.details,
            pay: parseFloat(vm.data.pay),
            duration: parseFloat(vm.data.duration),
            languages: [],
            position: parseInt(vm.data.position)
        };

        business.languages.forEach(function(lang) {
            var lang_model = vm.data['language-' + lang.iso_name];
            if(typeof(lang_model) !== 'undefined' && lang_model) {
                listingData.languages.push({
                    iso_name: lang.iso_name
                });
            }
        });

        bserv.createListing(business, listingData)
            .then(function(response) {
                vm.form.$setSubmitted();
                lserv.reset();
                vm.success = true;
            }, function(response) {
                vm.form.$setSubmitted();
                vm.success = false;
            });
    }
}
