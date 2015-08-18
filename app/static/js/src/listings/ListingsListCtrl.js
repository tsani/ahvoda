function ListingsListCtrl(bserv, util, businesses) {
    var vm = this;

    vm.businesses = businesses;

    vm.util = util;

    vm.approveApplicant = function(listing, applicant) {
        bserv.approveEmployee(listing.id, applicant.username)
            .then(function(applicant) {
                listing.employee = applicant;
            });
    }
}
