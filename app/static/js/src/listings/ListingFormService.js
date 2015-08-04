/** A form describing a listing.
 *
 * @constructor
 * @param {object} data - The static data to populate certain form elements
 * with.
 * @param {object} data.languages[] - The {@link Language}s to include in the
 * form.
 * @param {object} data.positions[] - The {@link Position}s to include in the
 * form.
 * @param {int} data.businessId - Identifies the business under which to create
 * the position.
 * @param {object} [defaultPosition] - The {@link Position} to start the form
 * pre-filled with. This SHOULD be an item from `data.positions`, although this
 * is not enforced.
 */
function ListingForm(data, defaultPosition) {
    var form = this;

    form.defaultPosition = defaultPosition;

    /** The form's model, which is to be provided to formly.
     */
    form.data = {
        businessId: data.businessId
    };

    /** The {@link ListingFormAdapter} to convert this form's model into a
     * format suitable for consumption by the backend.
     */
    form.adapter = new ListingFormAdapter(form.data);

    if(typeof(defaultPosition) !== 'undefined') {
        console.log('setting default position to', defaultPosition.id);
        form.data.position = defaultPosition;
    }

    /** Set the form's fields to match the defaults represented in a given
     * position.
     *
     * @param {object} p - {@link Position} whose defaults the form fields are
     * to be set to.
     */
    function matchFieldsToPosition(p) {
        console.log(JSON.stringify(p));

        if(p.default_pay) {
            form.data.pay = p.default_pay;
        }
        else
            form.data.pay = undefined;

        if(p.default_details) {
            form.data.details = p.default_details;
        }
        else
            form.data.details = undefined;

        if(p.default_duration) {
            console.log('setting duration', p.default_duration);
            form.data.duration = p.default_duration;
        }
        else
            form.data.duration = undefined;

        if(p.default_languages) {
            form.data.languages = form.data.languages || {};
            for(var j = 0; j < p.default_languages.length; j++) {
                form.data.languages[p.default_languages[j].iso_name] = true;
            }
        }
    }

    /** Updates the fields of the form to match any defaults associated
     * with the currently selected position.
     */
    form.updatePositionDefaults = function() {
        matchFieldsToPosition(form.data.position);
    };

    /** The form's fields, which are to be provided to formly.
     */
    form.fields = [
        {
            key: 'position',
            type: 'select',
            templateOptions: {
                choices: data.positions,
                label: 'Position',
                required: true,
                onChange: form.updatePositionDefaults
            }
        },
        {
            key: 'pay',
            type: 'input',
            templateOptions: {
                type: 'number',
                label: 'Hourly pay',
                placeholder: '11',
                required: true
            }
        },
        {
            key: 'details',
            type: 'textarea',
            templateOptions: {
                rows: 7,
                label: 'Details',
                placeholder: 'Describe the duties of the worker.',
                required: true
            }
        },
        {
            key: 'duration',
            type: 'input',
            templateOptions: {
                label: 'Duration (hours)',
                type: 'number',
                placeholder: '3.5',
                required: true
            }
        },
        {
            key: 'languages',
            type: 'multicheckbox',
            templateOptions: {
                label: 'Languages',
                choices: data.languages.map(function(lang) {
                    return {
                        name: lang.name,
                        value: lang.iso_name
                    };
                })
            }
        }
    ];

    matchFieldsToPosition(form.defaultPosition);
}

/** A service for creating forms that describe a listing, either for the
 * purposes of creating new listings or for updating existing ones.
 *
 * @constructor
 * @param {object} bserv - The {@link BusinessService}
 */
function ListingFormService(bserv) {
    var srv = this;

    /** {@link ListingForm }
     *
     * @constructor 
     */
    srv.ListingForm = ListingForm;

    /** Create a new listing or update an existing listing from a form.
     *
     * @param {object} lf - The {@link ListingForm} to submit.
     * @param {int} [listingId] - If provided, the submission will update an
     * existing listing rather than create a new one.
     * @returns {promise} A promise yielding the created/updated {@link
     * Listing} object.
     */
    srv.submit = function(lf, listingId) {
        var data = lf.adapter.adapt();

        if(typeof(listingId) === 'undefined')
            return bserv.createListing(data);
        else {
            return bserv.patchListing(listingId, data)
                .then(function() {
                    return bserv.getListing(listingId);
                })
                .then(function(l) {
                    return l;
                });
        }
    }
}
