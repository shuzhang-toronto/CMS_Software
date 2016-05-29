angular.module('softwareRequestApp', ['ui.bootstrap']) 
.controller("MainCtrl", ["$scope", "$uibModal", "softwareService", "modalService",
    function($scope, $uibModal, softwareService, modalService){ 
		$scope.currentPage = 0; $scope.pageSize = 3;
		$scope.allUsers = [];
		$scope.softwares = [];
		$scope.numberOfPages= 0;
        $scope.alert = null;
		$scope.admin = false;
		
		var currentUser = 'carol';
		loadRemoteData();

		$scope.addSoftware = function() {
			var modalOptions = {
				closeButtonText: 'Cancel',
				actionButtonText: 'Add',
				headerText: 'Add software?',
				bodyText: 'Are you sure you want to add "' + $scope.newSoftware.name +'"?'
			};
			
			modalService.showModal({}, modalOptions).then(function (result) {
				try{
					$scope.alert = null;
					addSoftware_imp($scope.newSoftware);
				}
				catch(err) {
					$scope.alert = {type: 'danger', msg: err};
				}
			});
		};  

		$scope.closeAlert = function(index) {
			$scope.alert = null;
		};
		
		$scope.toggleUsage = function(software, index){
			index = $scope.currentPage*($scope.pageSize-1) + index;
			if(index != 0 && !$scope.admin)
				return;
			if(software.usage[index])
				software.usage[index] = "";
			else
				software.usage[index] = "x";
		};
		
		function addSoftware_imp(software) {
			
			var result = $.grep($scope.softwares, function(item){ return item.name === software.name});
			if(result.length == 0) {
				var usage = ['x'];
				for(var i = 1; i < $scope.allUsers.length; ++i)
					usage.push('');
				if(software.notes)
					usage[0] = software.notes;
				$scope.softwares.push({name:software.name, usage:usage});
			}
			else
				throw "[add software error]software '" + software.name + "' is already there";
		};
		
		$scope.submit = function() {
			softwareService.submit($scope.allUsers, $scope.softwares).then(
				function(data) {alert("ok");}, function(data) {alert("fail");});
		};
		
		function loadRemoteData() {
			$scope.isLoading = true;
			softwareService.query().then( 
				function(data) {
					applyRemoteData(data);
				});
		}
		
		function applyRemoteData( data ) {
			$scope.allUsers = data['users'];
			$scope.softwares = data['softwares'];
			// for(var i = 0; i < data['users'].length; ++i)
			// {
				// if(data['users'][i].id === currentUser)
					// $scope.allUsers.unshift(data['users'][i]);
				// else
					// $scope.allUsers.push(data['users'][i]);
			// }
			// $scope.softwares = [];
			// for(var i = 0; i < data['softwares'].length; ++i){
				// var s = data['softwares'][i];
				// var usage = [];
				// for(var j = 0; j < $scope.allUsers.length; ++j) {
					// if($scope.allUsers[j].id in s.usage) {
						// usage[j] = s.usage[$scope.allUsers[j].id];
					// }
					// else {
						// usage[j] = false;
					// }
				// }
				// $scope.softwares.push({name:s.name, usage:usage});
			// }
			$scope.numberOfPages = Math.ceil(($scope.allUsers.length - 1)/($scope.pageSize -1)); 
			$scope.isLoading = false;
		}
		
		
	
	}])
.filter('startFrom', function() {
	return function(input, start) {
		start = +start; //parse to int
		return input.slice(start);
	}
})
.filter('replaceEmpty', function() {
	return function(input, replace) {
		if(input) 
			return input
		else
			return replace;
	}
})
.service('modalService', ['$uibModal',
	function ($uibModal) {

		var modalDefaults = {
			backdrop: true,
			keyboard: true,
			modalFade: true,
			templateUrl: '/static/partials/modal.html'
		};

		var modalOptions = {
			closeButtonText: 'Close',
			actionButtonText: 'OK',
			headerText: 'Proceed?',
			bodyText: 'Perform this action?'
		};

		this.showModal = function (customModalDefaults, customModalOptions) {
			if (!customModalDefaults) customModalDefaults = {};
			customModalDefaults.backdrop = 'static';
			return this.show(customModalDefaults, customModalOptions);
		};

		this.show = function (customModalDefaults, customModalOptions) {
			//Create temp objects to work with since we're in a singleton service
			var tempModalDefaults = {};
			var tempModalOptions = {};

			//Map angular-ui modal custom defaults to modal defaults defined in service
			angular.extend(tempModalDefaults, modalDefaults, customModalDefaults);

			//Map modal.html $scope custom properties to defaults defined in service
			angular.extend(tempModalOptions, modalOptions, customModalOptions);

			if (!tempModalDefaults.controller) {
				tempModalDefaults.controller = function ($scope, $uibModalInstance) {
					$scope.modalOptions = tempModalOptions;
					$scope.modalOptions.ok = function (result) {
						$uibModalInstance.close(result);
					};
					$scope.modalOptions.close = function (result) {
						$uibModalInstance.dismiss('cancel');
					};
				}
			}

			return $uibModal.open(tempModalDefaults).result;
		};
	}
])
.factory("softwareService", ["$http", "$q", function($http, $q){
    var handleError = function( response ) {
		if (! angular.isObject( response.data ) ||
			! response.data.message) {
			return( $q.reject( "An unknown error occurred." ) );
		}
		
		return( $q.reject( response.data.message ) );
	}
	var handleSuccess = function( response ) {
		return( response.data );
	}
	
	
    return {

        query : function() {
            var request = $http({
				method: "get",
				url: "/query",
				cache: false,
				headers: {
                    'Content-Type': 'application/json'
                }
			});
			return request.then(handleSuccess, handleError);
        },

        submit : function(users, softwares)
        {
            var data = {users: users, softwares: softwares};
			var request = $http({
				method: "post",
				url: "/update",
				params: {action: "add"},
				data: {users: users, softwares: softwares}
			});
			
            return request.then(handleSuccess, handleError);
        }

    };
}])
.directive( "mwConfirmClick", [
	function( ) {
		return {
			priority: -1,
			restrict: 'A',
			scope: { confirmFunction: "&mwConfirmClick" },
			link: function( scope, element, attrs ){
				element.bind( 'click', function( e ){
					var message = attrs.mwConfirmClickMessage ? attrs.mwConfirmClickMessage : "Are you sure?";
					if( confirm( message ) ) {
						scope.confirmFunction();
					}
				});
			}
		}
	}
]);