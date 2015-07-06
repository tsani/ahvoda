function BusinessService($q, $http) {
    var srv = this;

    srv.username = window.username;

    srv.getBusinesses = function() {
        return $http.get('/api/manager/' + this.username + '/businesses')
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
        return $http.get('/api/business/' + businessId)
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
                '/api/business/' + business.id + '/listings', listing)
            .then(function(response) {
                return response.data;
            });
    }

    srv.getPositions = function(business) {
        return $http.get('/api/business/' + business.id + '/positions')
            .then(function(response) {
                return response.data.positions;
            });
    }

    srv.createPosition = function(business, name) {
        return $http.post('/api/business/' + business.id + '/positions', {
            name: name
        }).then(function(response) {
            return response.data;
        });
    }

    srv.patchPosition = function(business, positionId, name) {
        return $http.patch(
                '/api/business/' + business.id + '/positions/' + positionId, {
                    name: name
                });
    }

    srv.deletePosition = function(business, positionId) {
        return $http.delete(
                '/api/business/' + business.id + '/positions/' + positionId);
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

