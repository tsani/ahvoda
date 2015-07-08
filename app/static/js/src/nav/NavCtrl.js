function NavCtrl(bserv) {
    var vm = this;
    vm.manager = false;
    vm.employee = false;
    vm.administrator = false;

    if(bserv.accountType === 'manager')
        bserv.getManager()
            .then(function(manager) {
                vm.manager = manager;
            });

    if(bserv.accountType === 'employee')
        bserv.getEmployee()
            .then(function(employee) {
                vm.employee = employee;
            });

    if(bserv.accountType === 'administrator')
        vm.administrator = true;
}
