function BusinessService($q, $http) {
    var srv = this;

    srv.username = window.username;

    console.log("Account type " + srv.accountType);

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
            }, failureLogger);
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

    srv.getBusiness = function(businessId) {
        return $http.get('/api/businesses/' + businessId)
            .then(function(response) {
                return response.data;
            });
    }

    srv.getListings = function(business) {
        return $http.get('/api/listings', {
            business: business.id
        }).then(function(response) {
            return response.data.listings;
        });
    }

    srv.createListing = function(business, listing) {
        return $http.post(
                '/api/businesses/' + business.id + '/listings', listing)
            .then(function(response) {
                return response.data;
            });
    }

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

    srv.deletePosition = function(business, positionId) {
        return $http.delete(
                '/api/businesses/' + business.id + '/positions/' + positionId);
    }

    srv.getManager = function() {
        return $http.get('/api/manager/' + srv.username)
            .then(function(response) {
                return response.data;
            });
    }

    srv.businesses = [];
    srv.positions = {};
    srv.manager = {};

    srv.loadAll = function() {
        srv.getManager()
            .then(function(data) {
                srv.manager = data;
            });
        return srv.getBusinesses()
            .then(function(businesses) {
                srv.getListingGroups(businesses)
                    .then(function(listingGroups) {
                        srv.listingGroups = listingGroups;
                    });

                srv.getPositionGroups(businesses)
                // Clear the businesses array.
                srv.businesses.splice(0, srv.businesses.length);
                // Populate it with the businesses obtained in the response
                businesses.forEach(function(b) {
                    srv.businesses.push(b);
                });
            });
    };

    srv.loadAll();

    console.log('Initialized BusinessService.');
}

