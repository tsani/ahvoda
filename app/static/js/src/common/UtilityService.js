function UtilityService() {
    var srv = this;

    srv.formatAddress = function(location) {
        return [
            location.address,
            location.city.name,
            location.city.state.name,
            location.city.state.country.name
        ].join(', ');
    };
}
