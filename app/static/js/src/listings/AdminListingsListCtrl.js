function AdminListingsListCtrl(bserv, util, employees, listings) {
    var vm = this;
    vm.util = util;

    vm.listings = listings;

    function decorateEmployee(e) {
        e.name = e.human.first_name + ' ' + e.human.last_name;
    }

    for(var i = 0; i < employees.length; i++) {
        decorateEmployee(employees[i]);
    }

    function registerListing(listing) {
        listing.employeeFormModel = {};
        listing.employeeFormFields = [
            {
                key: 'employee',
                type: 'select',
                templateOptions: {
                    choices: employees,
                    required: true
                }
            }
        ];

        listing.associateEmployee = function() {
            bserv.approveEmployee(listing, listing.employeeFormModel.employee.username)
                .then(function(updatedListing) {
                    listing.employee = updatedListing.employee;
                    listing.status = updatedListing.status;
                });
        };
    }

    function updateListings() {
        for(var i = 0; i < vm.listings.length; i++) {
            registerListing(vm.listings[i]);
        }
    }

    updateListings();
}
