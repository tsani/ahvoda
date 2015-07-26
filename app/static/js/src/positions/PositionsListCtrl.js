function PositionsListCtrl(bserv, util, businesses) {
    var vm = this;

    vm.businesses = businesses;

    vm.util = util;

    vm.deletePosition = function(business, position) {
        bserv.deletePosition(position.id)
            .then(function() {
                for(var i = 0; i < business.positions.length; i++) {
                    var p = business.positions[i];
                    if(p.id === position.id) {
                        business.positions.splice(i, 1);
                    }
                }
            });
    };
}
