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

    var pad = function(s) {
        var p = s.toString();
        var q = p.length === 1 ? '0' + p : p;
        return q;
    };

    srv.formatDate = function(dateString) {
        var d = new Date(dateString);
        return [
            d.getFullYear(),
            pad(d.getMonth()),
            pad(d.getDay())
        ].join('-');
    };

    srv.formatTime = function(dateString) {
        var d = new Date(dateString);
        return [
            pad(d.getHours()),
            pad(d.getMinutes())
        ].join(':');
    };
}
