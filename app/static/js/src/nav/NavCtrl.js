function NavCtrl(bserv) {
    var vm = this;
    vm.manager = {};
    bserv.getManager()
        .then(function(manager) {
            vm.manager = manager;
        });
}
