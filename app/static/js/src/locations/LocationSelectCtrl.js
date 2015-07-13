function makeLocationSelectCtrl(successState) {
    function LocationSelectCtrl($state, locationSelectServ, businesses) {
        var vm = this;

        vm.data = {};

        vm.fields = [
            {
                key: 'location',
                type: 'select',
                templateOptions: {
                    label: 'Location',
                    choices: businesses.map(function(b) {
                        return {
                            name: b.name,
                            value: b.id
                        };
                    }),
                    label: 'Location',
                    required: true 
                }
            }
        ];

        vm.next = function() {
            locationSelectServ.locations.push(angular.copy(vm.data));
            $state.go(successState);
        }
    }

    console.log('make location select controller');

    return LocationSelectCtrl;
}
