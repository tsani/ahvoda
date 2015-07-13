function ahManager() {
    return {
        restrict: 'AE',
        isolate: true,
        scope: {
            manager: '=ahManager'
        },
        templateUrl: '/static/widgets/directives/ahManager.html'
    };
}
