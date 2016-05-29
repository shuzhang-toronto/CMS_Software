angular.module('softwareRequestApp', []) 
.controller("MainCtrl", ["$scope", "userService", "softwareService", 
    function($scope, userService, softwareService){ 
		$scope.currentPage = 0; $scope.pageSize = 3;

		$scope.allUsers = softwareService.getAllUsers();
		$scope.currentUser = userService.getCurrentUser();
		$scope.softwares = softwareService.query();
		$scope.numberOfPages=
        Math.ceil(($scope.softwares.length - 1)/($scope.pageSize -1));                

    $scope.addSoftware = function() {
        softwareService.addSoftware($scope.newSoftware);
    };  

    $scope.submit = function() {
        softwareService.submit();
    };
}])
.filter('startFrom', function() {
    return function(input, start) {
        start = +start; //parse to int
        return input.slice(start);
    }
})
.factory("userService", ["$http", function($http){
    var users = [
        {   id:"alex", name:"alex zhang", isadmin:false, email:"zhangalex@fake.com"},
        {   id:"carol", name:"carol peng", isadmin:false, email:"pengcarol@fake.com"},
        {   id:"juliana", name:"juliana peng", isadmin:true, email:"pengjuli@fake.com"},
        {   id:"shu", name:"shu zhang", isadmin:false, email:"zhangshu@fake.com"},
    ];
    var currentUser = null;
    return {
        getCurrentUser : function() {
            return currentUser;
        },
        getAllUsers : function() {
            return users;
        },
        login : function(name, password) {
            var result = $.grep(users, function(item){ return item.id === name; });
            if(result.length == 1)
                currentUser = result[0];
            else
                throw "login software error";
        },
        logout : function() {
            currentUser = null;
        },
        isLogin : function()
        {
            return (currentUser == null);
        }
    };
}])
.factory("softwareService", ["$http", "userService", function($http, userService){
    var softwares = [
        {name: "git", usage: [true, "2.0", false, true ]},
        {name: "svn", usage: [true, "2.0", false, true ]},
        {name: "php", usage: [false, false, "5.0", true ]},
        {name: "python", usage: [false, "3.3", false, "3.3" ]},
        {name: "jquery", usage: ["1.2", "2.0", false, true ]}
    ];

    return {

        query : function() {
            return softwares;
        },

        submit : function()
        {
            var data = {users: userService.getAllUsers(), softwares: softwares};
            alert(angular.toJson(data) );
        },

        getAllUsers : function() {
            return userService.getAllUsers();
        },

        addSoftware : function(software) {
            var result = $.grep(softwares, function(item){ return item.name === software.name});
            if(result.length == 0) {
                var usage = [true, false, false, false];
                if(software.notes)
                    usage[0] = software.notes;
                s = {};
                s.name = software.name;
                s.usage = usage;
                softwares.push(s);
            }
            else
                throw "add software error";
        }
    };
}])
.directive( 'editInPlace', function() {
    return {
        restrict: 'E',
        scope: { value: '=' },
        template: '<span ng-click="edit()" ng-bind="value"></span><input ng-model="value"></input>',
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
            inputElement.prop( 'onblur', function() {
                $scope.editing = false;
                element.removeClass( 'active' );
            });
        }
    };
});