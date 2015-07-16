/** Controller for the view to create a new listing.
 *
 * @constructor
 * @param {object} bserv - The {@link BusinessService}.
 * @param {object} lfserv - The {@link ListingFormService}.
 * @param {object} business - The {@link Business} under which the listing will
 * be registered.
 * @param {object} positions - The {@link Position}s that this listing can
 * choose from.
 * @param {object} [defaultPosition] - The {@link Position} that the form
 * starts pre-filled with. This SHOULD be an item from `positions`, but this is
 * not enforced.
 */
function NewListingDetailsCtrl(
    $state,
    bserv,
    lfserv,
    business,
    positions,
    defaultPosition
) {
    var vm = this;

    vm.form = new lfserv.ListingForm({
        positions: positions,
        languages: business.languages
    }, defaultPosition);

    vm.submit = function() {
        lfserv.submit(vm.form, business.id)
            .then(function(newListing) {
                vm.form.ctrl.$setSubmitted();
                vm.success = true;
            }, function(response) {
                vm.form.ctrl.$setSubmitted();
                vm.success = false;
            });
    };
}
