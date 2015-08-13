function NewPositionDetailsCtrl(bserv, pfserv, business) {
    var vm = this;

    vm.form = pfserv.create({
        business: business
    });

    vm.position = undefined;
    vm.business = business;

    vm.submit = function() {
        return pfserv.submit(vm.form)
            .then(function(position) {
                vm.position = position;
                vm.form.controller.$setSubmitted();
            });
    };
}
