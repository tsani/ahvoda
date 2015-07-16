/** Controller for the view to update an existing listing.
 *
 * @constructor
 * @param {object} bserv - The {@link BusinessService}.
 * @param {object} lfserv - The {@link ListingFormService}.
 * @param {object} business - The {@link Business} under which the listing is
 * registered.
 * @param {object} positions - The {@link Position}s that this listing can
 * choose from.
 * @param {object} listing - The {@link Listing} that is already registered in
 * the backend.
 */
function ListingEditCtrl(
    bserv,
    lfserv,
    business,
    listing,
    positions
) {
    var vm = this;

    vm.business = business;

    var lpAdapter = new ListingPositionAdapter(listing);

    vm.form = new lfserv.ListingForm({
        positions: positions,
        languages: business.languages
    }, lpAdapter.adapt());

    vm.submit = function() {
        lfserv.submit(vm.form, business.id, listing.id)
            .then(function(newListing) {
                vm.form.ctrl.$setSubmitted();
                vm.success = true;
            }, function(response) {
                vm.form.ctrl.$setSubmitted();
                vm.success = false;
            });
    };
}
