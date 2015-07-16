function BusinessService($q, $http) {
    var srv = this;

    srv.username = window.username;
    srv.accountType = window.accountType;

    srv.getCities = function() {
        return $http.get('/api/data/cities')
            .then(function(response) {
                return response.data.cities;
            });
    };

    srv.getStates = function() {
        return $http.get('/api/data/states')
            .then(function(response) {
                return response.data.states;
            });
    };

    srv.getCountries = function() {
        return $http.get('/api/data/countries')
            .then(function(response) {
                return response.data.countries;
            });
    };

    srv.getLanguages = function() {
        return $http.get('/api/data/languages')
            .then(function(response) {
                return response.data.languages;
            });
    };

    srv.getGenders = function() {
        return $http.get('/api/data/genders')
            .then(function(response) {
                return response.data.genders;
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
                return response.data.businesses;
            });
    };

    srv.getBusinessManagers = function(businessId) {
        return $http.get('/api/businesses/' + businessId + '/managers')
            .then(function(response) {
                return response.data.managers;
            });
    };

    srv.getListingGroups = function(businesses) {
        return $q.all(businesses.map(function(b) {
            return srv.getListings(b)
                .then(function(listings) {
                    return {
                        business: b,
                        listings: listings
                    };
                });
        })).then(function(listingGroups) {
            var ret = {};
            for(var i = 0; i < listingGroups.length; i++)
                ret[listingGroups[i].business.name] = listingGroups[i].listings;
            return ret;
        });
    };

    srv.getPositionGroups = function(businesses) {
        return $q.all(businesses.map(function(b) {
            return srv.getPositions(b)
                .then(function(positions) {
                    return {
                        business: b,
                        positions: positions
                    };
                });
        })).then(function(positionGroups) {
            var ret = {};
            for(var i = 0; i < positionGroups.length; i++)
                ret[positionGroups[i].business.name] = positionGroups[i].positions;
            return ret;
        });
    };

    srv.getEmployees = function() {
        return $http.get('/api/employees')
            .then(function(response) {
                return response.data.employees;
            });
    };

    srv.getManagers = function() {
        return $http.get('/api/managers')
            .then(function(response) {
                return response.data.managers;
            });
    };

    srv.getBusinesses = function() {
        return $http.get('/api/businesses')
            .then(function(response) {
                return response.data.businesses;
            });
    };

    srv.getBusiness = function(businessId) {
        return $http.get('/api/businesses/' + businessId)
            .then(function(response) {
                return response.data;
            });
    }

    srv.getListings = function(business) {
        var qs = {}
        if(typeof(business) !== 'undefined')
            qs.business = business.id;

        return $http.get('/api/listings', {
            params: qs
        }).then(function(response) {
            return response.data.listings;
        });
    }

    srv.createBusiness = function(data) {
        return $http.post('/api/businesses', data)
            .then(function(response) {
                return response.data;
            });
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

    srv.approveEmployee = function(listing, employeeUsername) {
        return $http.post('/api/businesses/' + listing.business.id +
                '/listings/' + listing.id + '/employee', {
                    name: employeeUsername
                }).then(function(response) {
                    return response.data;
                });
    };

    srv.createListing = function(business, listing) {
        return $http.post(
                '/api/businesses/' + business.id + '/listings', listing)
            .then(function(response) {
                return response.data;
            });
    }

    srv.deleteListing = function(businessId, listingId) {
        return $http.delete(
                '/api/businesses/' + businessId + '/listings/' + listingId);
    };

    srv.getPositions = function(business) {
        return $http.get('/api/businesses/' + business.id + '/positions')
            .then(function(response) {
                return response.data.positions;
            });
    }

    srv.getPosition = function(business, positionId) {
        return $http.get(
                '/api/businesses/' + business.id + '/positions/' + positionId)
            .then(function(response) {
                return response.data;
            });
    }

    srv.createPosition = function(business, position) {
        return $http.post(
                '/api/businesses/' + business.id + '/positions',
                position)
            .then(function(response) {
                return response.data;
            });
    }

    srv.patchPosition = function(business, positionId, name) {
        return $http.patch(
                '/api/businesses/' + business.id + '/positions/' + positionId, {
                    name: name
                });
    }

    srv.deletePosition = function(businessId, positionId) {
        return $http.delete(
                '/api/businesses/' + businessId + '/positions/' + positionId);
    }

    srv.getManager = function() {
        return $http.get('/api/managers/' + srv.username)
            .then(function(response) {
                return response.data;
            });
    }

    srv.getEmployee = function() {
        return $http.get('/api/employees/' + srv.username)
            .then(function(response) {
                return response.data;
            });
    };
}
