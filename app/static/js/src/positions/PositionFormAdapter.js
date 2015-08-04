/** Adapt the form model that describes a position into an object ot be passed
 * to the backend.
 *
 * @constructor
 */
function PositionFormAdapter(model) {
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
        var base = {
            name: adapter.model.positionName,
            business: adapter.model.businessId
        };

        if(typeof adapter.model.defaultPay !== 'undefined')
            base.default_pay = parseFloat(adapter.model.defaultPay);
        
        if(typeof adapter.model.defaultDuration !== 'undefined')
            base.default_duration = parseFloat(adapter.model.defaultDuration);

        if(adapter.model.defaultLanguages)
            base.default_languages = Object.keys(adapter.model.defaultLanguages)
                .filter(function(k) {
                    return adapter.model.defaultLanguages[k];
                })
                .map(function(k) {
                    return {
                        iso_name: k
                    };
                });
        if(adapter.model.defaultDetails)
            base.default_details = adapter.model.defaultDetails;

        return base;
    };

    adapter.from = function(p) {
        adapter.model.name = p.name ? p.name : undefined;
        adapter.model.defaultPay = p.default_pay ? p.default_pay : undefined;
        adapter.model.defaultDuration = p.default_duration ? p.default_duration : undefined;
        adapter.model.defaultDetails = p.default_details ? p.default_details : undefined;
        adapter.model.defaultLanguages = ! p.default_languages ? undefined : p.default_languages
            .map(function(lang) {
                var base = {};
                base[lang.iso_name] = true;
                return base;
            });
    }
}
