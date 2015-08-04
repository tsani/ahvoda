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
    .service('PositionFormService', [
        'BusinessService',
        PositionFormService
    ])
    .controller('NavCtrl', [
        'BusinessService',
        NavCtrl
    ])
    .controller('MasterViewCtrl', [
        '$rootScope',
        MasterViewCtrl
    ])
    .directive('ahMulticheckbox', [
        ahMulticheckbox
    ])
    .run(['formlyConfig', function(formlyConfig) {
        commonConfig(formlyConfig);
    }]);
