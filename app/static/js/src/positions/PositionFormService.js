/**
 * A form describing a listing.
 *
 * @constructor
 * @param {object} data - The static data to populate certain form elements.
 * @param {int} data.business - The business that owns this position.
 * @param {object} [initial] - An initial model for the form's contents.
 */
function PositionForm(data, initial) {
    var form = this;

    form.initial = initial;

    form.data = {
        businessId: data.business.id
    };

    form.fields = [
        {
            key: 'positionName',
            type: 'input',
            templateOptions: {
                label: 'Position name',
                type: 'text',
                placeholder: 'A name applicants will see when searching for listings.',
                required: true
            }
        },
        {
            key: 'defaultDuration',
            type: 'input',
            templateOptions: {
                label: 'Default duration',
                type: 'number',
                placeholder: 'The duration can be adjusted on a per-job basis.',
                required: true
            }
        },
        {
            key: 'defaultPay',
            type: 'input',
            templateOptions: {
                label: 'Default hourly pay',
                type: 'number',
                placeholder: 'This pay can be adjusted on a per-job basis.',
                required: true
            }
        },
        {
            key: 'defaultDetails',
            type: 'textarea',
            templateOptions: {
                label: 'Default job description',
                placeholder: 'The job details can be adjusted on a per-job basis.',
                required: true
            }
        },
        {
            key: 'defaultLanguages',
            type: 'multicheckbox',
            templateOptions: {
                choices: data.business.languages.map(function(e) {
                    return {
                        name: e.name,
                        value: e.iso_name
                    };
                }),
                label: 'Default languages',
                minimumRequired: 1
            }
        }
    ];

    form.adapter = new PositionFormAdapter(form.data);

    if(typeof initial !== 'undefined')
        form.adapter.from(initial); 
}

/**
 * Creates forms that describe positions, either to record new positions or
 * update existing ones.
 *
 * @constructor
 * @param {object} bserv - The {@link BusinessService} used to communicate with
 * the backend.
 */
function PositionFormService(bserv) {
    var srv = this;

    /**
     * Creates a new {@link PositionForm}.
     */
    srv.create = function(data, initial) {
        return new PositionForm(data, initial);
    };

    /**
     * Creates or updates a listing from a form.
     *
     * @param {object} form - The {@link PositionForm} to submit.
     * @param {int} [positionId] - If provided, the submission will update an
     * existing position rather than create a new one.
     * @returns {promise} A promise that yields the created or updated {@link
     * Position} object.
     */
    srv.submit = function(form, positionId) {
        var data = form.adapter.adapt();

        if(typeof positionId === 'undefined')
            return bserv.createPosition(data);
        else 
            return bserv.patchPosition(positionId, data)
                .then(function() {
                    return bserv.getPosition(positionId);
                })
                .then(function(p) {
                    return p;
                });
    }
}
