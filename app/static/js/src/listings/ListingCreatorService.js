function ListingCreatorService() {
    var srv = this;

    var _initialData = {
        languages: {}
    };

    srv.data = {};

    srv.reset = function reset() {
        srv.data = angular.copy(_initialData);
    }

    srv.reset();
}

