function AdminOverviewCtrl(businesses, listings, employees, managers) {
    console.log('loaded admin overview');

    var vm = this;

    vm.businesses = businesses;
    vm.listings = listings;
    vm.employees = employees;
    vm.managers = managers;
}
