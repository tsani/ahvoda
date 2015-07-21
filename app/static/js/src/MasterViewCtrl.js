function MasterViewCtrl($rootScope) {
    var vm = this;

    // These indicators affect how the view is shown/hidden in the template,
    // and affect the presence of the spinner.
    vm.loading = true;
    vm.error = null;

    function changeStart(
        event,
        toState,
        toParams,
        fromState,
        fromParams
    ) {
        vm.loading = true;
        vm.error = null;
    }

    function changeSuccess(
        event,
        toState,
        toParams,
        fromState,
        fromParams
    ) {
        vm.loading = false;
        vm.error = null;
    }

    function changeError(
        event,
        toState,
        toParams,
        fromState,
        fromParams,
        error
    ) {
        // Save the error to the controller, to show it in the template.
        vm.error = error;
    }

    $rootScope.$on('$stateChangeStart', changeStart);
    $rootScope.$on('$stateChangeSuccess', changeSuccess);
    $rootScope.$on('$stateChangeError', changeError);
}
