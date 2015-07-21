angular
    .module('AdminApp', ['ui.router', 'formly'])
    .config([
        '$stateProvider',
        '$urlRouterProvider',
        adminAppConfig
    ])
    .service('BusinessService', [
        '$q',
        '$http',
        BusinessService
    ])
    .service('UtilityService', [
        UtilityService
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
    .directive('ahManager', [
        ahManager
    ])
    .run([
        'formlyConfig',
        function(formlyConfig) {
            commonConfig(formlyConfig);
        }
    ]);
