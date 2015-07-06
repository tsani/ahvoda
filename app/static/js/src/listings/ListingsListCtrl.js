function ListingsListCtrl(listingGroups, businesses) {
    var vm = this;

    vm.listingGroups = listingGroups;
    vm.businesses = businesses;

    vm.formatAddress = function(location) {
        return [
            location.address,
            location.city.name,
            location.city.state.name,
            location.city.state.country.name
        ].join(', ');
    };
}
