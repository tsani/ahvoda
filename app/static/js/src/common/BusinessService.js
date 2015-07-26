function BusinessService($q, $http) {
    var srv = this;

    srv.username = window.username;
    srv.accountType = window.accountType;

    srv.getCities = function() {
        return $http.get('/api/data/cities')
            .then(function(response) {
                return response.data;
            });
    };

    srv.getStates = function() {
        return $http.get('/api/data/states')
            .then(function(response) {
                return response.data;
            });
    };

    srv.getCountries = function() {
        return $http.get('/api/data/countries')
            .then(function(response) {
                return response.data;
            });
    };

    srv.getLanguages = function() {
        return $http.get('/api/data/languages')
            .then(function(response) {
                return response.data;
            });
    };

    srv.getGenders = function() {
        return $http.get('/api/data/genders')
            .then(function(response) {
                return response.data;
            });
    };

    srv.addManagerToBusiness = function(managerUsername, businessId) {
        return $http.post('/api/businesses/' + businessId + '/managers', {
            name: managerUsername
        }).then(function(response) {
            return response.data;
        });
    };

    srv.removeManagerFromBusiness = function(managerUsername, businessId) {
        return $http.delete('/api/businesses/' + businessId
                + '/managers/' + managerUsername);
    };

    srv.getManagerBusinesses = function(username) {
        if(typeof(username) === 'undefined')
            username = this.username;

        return $http.get('/api/managers/' + username + '/businesses')
            .then(function(response) {
                return response.data;
            });
    };

    srv.getBusinessManagers = function(businessId) {
        return $http.get('/api/businesses/' + businessId + '/managers')
            .then(function(response) {
                return response.data;
            });
    };

    srv.getEmployees = function() {
        return $http.get('/api/employees')
            .then(function(response) {
                return response.data;
            });
    };

    srv.getManagers = function() {
        return $http.get('/api/managers')
            .then(function(response) {
                return response.data;
            });
    };

    srv.getBusinesses = function() {
        return $http.get('/api/businesses')
            .then(function(response) {
                return response.data;
            });
    };

    srv.getBusiness = function(businessId) {
        return $http.get('/api/businesses/' + businessId)
            .then(function(response) {
                return response.data;
            });
    }

    srv.getListing = function(listingId) {
        return $http.get(
                '/api/listings/' + listingId)
            .then(function(response) {
                return response.data;
            });
    };

    srv.getListings = function(businessId) {
        var qs = {}
        if(typeof businessId !== 'undefined')
            qs.business = businessId;

        return $http.get('/api/listings', { params: qs })
            .then(function(response) {
                return response.data;
            });
    }

    srv.createBusiness = function(data) {
        return $http.post('/api/businesses', data)
            .then(function(response) {
                return response.data;
            });
    };

    srv.deleteBusiness = function(businessId) {
        return $http.delete('/api/businesses/' + businessId);
    };

    srv.createManager = function(data) {
        return $http.post('/api/managers', data)
            .then(function(response) {
                return response.data;
            });
    };

    srv.deleteManager = function(username) {
        return $http.delete('/api/managers/' + username);
    }

    srv.createEmployee = function(data) {
        return $http.post('/api/employees', data)
            .then(function(response) {
                return response.data;
            });
    };

    srv.approveEmployee = function(listingId, employeeUsername) {
        return $http.post('/api/listings/' + listingId + '/employee', {
                    name: employeeUsername
                }).then(function(response) {
                    return response.data;
                });
    };

    srv.createListing = function(data) {
        return $http.post('/api/listings', data)
            .then(function(response) {
                return response.data;
            });
    }

    /** Update an existing listing.
     *
     * @param {int} listingId - The id of the listing to update.
     * @param {object} data - The listing data to update.
     * @see {@link API_SPEC}
     */
    srv.patchListing = function(listingId, data) {
        return $http.patch('/api/listings/' + listingId, data);
    };

    srv.deleteListing = function(listingId) {
        return $http.delete('/api/listings/' + listingId);
    };

    srv.getPositions = function(businessId) {
        var qs = {};

        if(typeof businessId !== 'undefined')
            qs.business = businessId

        return $http.get('/api/positions', { params: qs })
            .then(function(response) {
                return response.data;
            });
    }

    srv.getPosition = function(positionId) {
        return $http.get('/api/positions/' + positionId)
            .then(function(response) {
                return response.data;
            });
    }

    srv.createPosition = function(data) {
        return $http.post('/api/positions', data)
            .then(function(response) {
                return response.data;
            });
    }

    srv.patchPosition = function(positionId, data) {
        return $http.patch('/api/positions/' + positionId, data);
    }

    srv.deletePosition = function(positionId) {
        return $http.delete('/api/positions/' + positionId);
    }

    srv.getManager = function(name) {
        if(typeof name === 'undefined')
            name = srv.username;

        return $http.get('/api/managers/' + name)
            .then(function(response) {
                return response.data;
            });
    }

    srv.getEmployee = function(name) {
        if(typeof name === 'undefined')
            name = srv.username

        return $http.get('/api/employees/' + name)
            .then(function(response) {
                return response.data;
            });
    };
}
