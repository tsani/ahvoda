function configureFormly(formlyConfig) {
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
        },
        {
            name: 'multicheckbox',
            template: '<ah-multicheckbox/>'
        }
    ].forEach(function(e) {
        formlyConfig.setType(e);
    });
}
