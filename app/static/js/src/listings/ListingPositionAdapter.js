/** Adapter to extract a {@link Position} from a {@link Listing}.
 *
 * The resulting Position is such that if it is used as a default for creating
 * a new Listing, then that new Listing will be an effective clone of the
 * adapted Listing.
 *
 * Note that the resulting Position is not registered in the backend; it will
 * have the same id and name as the position for which the provided listing is
 * registered.
 *
 * @constructor
 * @param {object} listing - The Listing from which to extract a Position.
 */
function ListingPositionAdapter(listing) {
    var adapter = this;

    /** The underlying model to adapt.
     */
    adapter.model = listing;

    /** Adapt the underlying model into a {@link Position} that can in turn be
     * used to create listings that are clones of this one.
     *
     * @returns {object} The adapted {@link Position}.
     */
    adapter.adapt = function() {
        return {
            id: adapter.model.position.id,
            name: adapter.model.position.name,
            default_pay: adapter.model.pay,
            default_details: adapter.model.details,
            default_languages: adapter.model.languages,
            default_duration: adapter.model.duration
        };
    }
}
