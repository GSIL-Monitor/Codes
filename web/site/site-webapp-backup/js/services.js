/* Services */

function gridService() {
	  var gridData = [];
	  
	  var newData = function(newObj){
		  gridData = newObj;
	  }
	  
	  var addData = function(newObj) {
		  newObj.concat(gridData);
	  };

	  var getData = function(){
	      return gridData;
	  };

	  return {
		  newData: newData,
		  addData: addData,
		  getData: getData
	  };
}

function listGridService() {
	  var gridData = [];
	  
	  var newData = function(newObj){
		  gridData = newObj;
	  }

	  var getData = function(){
	      return gridData;
	  };

	  return {
		  newData: newData,
		  getData: getData
	  };
}

function compsGridService() {
	var gridData = [];

	var newData = function(newObj){
		gridData = newObj;
	}

	var getData = function(){
		return gridData;
	};

	return {
		newData: newData,
		getData: getData
	};
}

function listService() {
	  var gridData = [];
	  
	  var newData = function(newObj){
		  gridData = newObj;
	  }

	  var getData = function(){
	      return gridData;
	  };

	  return {
		  newData: newData,
		  getData: getData
	  };
}

function langService() {
	  var data = {};
	  
	  var newData = function(newObj){
		  data = newObj;
	  }

	  var getData = function(){
	      return data;
	  };

	  return {
		  newData: newData,
		  getData: getData
	  };
}

function crowdfundingService() {
	var gridData = [];

	var newData = function(newObj){
		gridData = newObj;
	}

	var getData = function(){
		return gridData;
	};

	return {
		newData: newData,
		getData: getData
	};
}


function cfTotalService() {
	var gridData = [];

	var newData = function(newObj){
		gridData = newObj;
	}

	var getData = function(){
		return gridData;
	};

	return {
		newData: newData,
		getData: getData
	};
}



angular.module('gobi')
	.service('gridService', gridService)
	.service('listGridService', listGridService)
	.service('compsGridService', compsGridService)
	.service('listService', listService)
	.service('langService', langService)
	.service('crowdfundingService', crowdfundingService)
	.service('cfTotalService', cfTotalService)






