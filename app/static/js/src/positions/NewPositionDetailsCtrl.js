function NewPositionDetailsCtrl($state, business, positions, bserv) {
    var vm = this;

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
        }
    ];

    vm.submit = function() {
        bserv.createPosition(business, vm.data.positionName)
            .then(function(data) {
                vm.form.$setSubmitted();
            });
    };
}
