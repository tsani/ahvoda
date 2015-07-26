/** Adapt the form model that describes a listing into an object to be
 * passed to the backend.
 *
 * @constructor
*/
function ListingFormAdapter(model) {
    var adapter = this;

    /** The underlying model to adapt.
    */
    adapter.model = model;

    /** Adapt the underlying model to a form suitable for consumption by the
     * backend.
     *
     * @returns {object} An object that can be used directly with the API.
     */
    adapter.adapt = function() {
        return {
            business: adapter.model.businessId,
            details: this.model.details,
            pay: parseFloat(this.model.pay),
            duration: parseFloat(adapter.model.duration),
            languages: Object.keys(adapter.model.languages)
                .filter(function(k) {
                    return adapter.model.languages[k];
                })
                .map(function(k) {
                    return {
                        iso_name: k
                    };
                }),
            position: adapter.model.position.id
        };
    }
}
