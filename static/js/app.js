angular.module('softwareRequestApp', []) 
.controller("MainCtrl", ["$scope", "softwareService", 
    function($scope, softwareService){ 
		$scope.currentPage = 0; $scope.pageSize = 10;
		$scope.allUsers = [];
		$scope.softwares = [];
		$scope.numberOfPages= 0;
        
		var currentUser = '';
		loadRemoteData();

		$scope.addSoftware = function() {
			addSoftware_imp($scope.newSoftware);
		};  

		$scope.submit = function() {
			softwareService.submit($scope.allUsers, $scope.softwares).then(
				function(data) {alert("ok");}, function(data) {alert("fail");});
				
		};
		
		$scope.exportcsv = function() {
			softwareService.exportcsv().then(
				function(data) {
					window.open(data);
				});
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
		
		function addSoftware_imp(software) {
			var result = $.grep($scope.softwares, function(item){ return item.name === software.name});
			if(result.length == 0) {
				var usage = ['x'];
				for(var i = 1; i < $scope.allUsers.length; ++i)
					usage.push(' ');
				if(software.notes)
					usage[0] = software.notes;
				$scope.softwares.push({name:software.name, usage:usage});
			}
			else
				throw "add software error";
		};
	
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

		exportcsv : function() {
            var request = $http({
				method: "get",
				url: "/software/export2",
				cache: false,
				headers: {
                    'Content-Type': 'application/json'
                }
			});
			return request.then(handleSuccess, handleError);
        },
	
        query : function() {
            var request = $http({
				method: "get",
				url: "/software/query",
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
				url: "/software/update",
				params: {action: "add"},
				data: {users: users, softwares: softwares}
			});
			
            return request.then(handleSuccess, handleError);
        }

    };
}])
.directive( 'editInPlace', function() {
    return {
        restrict: 'E',
        scope: { value: '=' },
        template: '<label ng-click="edit()" ng-bind="value"></label><input ng-model="value"></input>',
        link: function ( $scope, element, attrs ) {
            var inputElement = angular.element( element.children()[1] );
            element.addClass( 'edit-in-place' );
            $scope.editing = false;

              // ng-click handler to activate edit-in-place
            $scope.edit = function () {
                $scope.editing = true;

                // We control display through a class on the directive itself. See the CSS.
                element.addClass( 'active' );

                // And we must focus the element. 
                // `angular.element()` provides a chainable array, like jQuery so to access a native DOM function, 
                // we have to reference the first element in the array.
                inputElement[0].focus();
            };

            // When we leave the input, we're done editing.
            inputElement[0].onblur = function() {
                $scope.editing = false;
                element.removeClass( 'active' );
            };
			
			angular.element(inputElement[0]).bind("keydown keypress", function(event){
				if(event.which === 13) {
					$scope.editing = false;
					element.removeClass( 'active' );
					event.preventDefault();
				}
                
			})
        }
    };
});
