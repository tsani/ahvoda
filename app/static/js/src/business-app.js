angular
    .module('BusinessApp', ['ui.router', 'formly'])
    .config([
        '$stateProvider',
        '$urlRouterProvider',
        businessAppConfig
    ])
    .service('BusinessService', [
        '$q',
        '$http',
        BusinessService
    ])
    .service('UtilityService', [
        UtilityService
    ])
    .service('ListingFormService', [
        'BusinessService',
        ListingFormService
    ])
    .controller('NavCtrl', [
        'BusinessService',
        NavCtrl
    ])
    .directive('ahMulticheckbox', [
        ahMulticheckbox
    ])
    .run(['formlyConfig', function(formlyConfig) {
        commonConfig(formlyConfig);
    }]);
