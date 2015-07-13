function AdminListingsListCtrl(bserv, util, employees, listings) {
    var vm = this;
    vm.util = util;

    vm.listings = listings;

    function registerListing(listing) {
        listing.employeeFormModel = {};
        listing.employeeFormFields = [
            {
                key: 'employee',
                type: 'select',
                templateOptions: {
                    choices: employees.map(function(e) {
                        return {
                            name: e.human.first_name + ' ' + e.human.last_name,
                            value: e.username
                        };
                    }),
                    required: true
                }
            }
        ];

        listing.associateEmployee = function() {
            bserv.approveEmployee(listing, listing.employeeFormModel.employee)
                .then(function(updatedListing) {
                    // TODO check that a more sophisticated merging isn't
                    // required.
                    listing.employee = updatedListing.employee;
                });
        };

        console.log("Registered listing for postion " + listing.position.name);
    }

    function updateListings() {
        for(var i = 0; i < vm.listings.length; i++) {
            registerListing(vm.listings[i]);
        }
    }

    updateListings();
}
