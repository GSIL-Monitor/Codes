var React = require('react');
var $ = require('jquery');

var Functions = require('../util/Functions');


const SectorList = React.createClass({
    render(){
        var sectors = this.props.data;
        var parentSector = '';
        var subSector = '';
        if(sectors != null){
            if(sectors.length == 1){
                parentSector = sectors[0].sectorName;
            }else if(sectors.length == 2){
                for(var i in sectors){
                    if(sectors[i].level == 1){
                        parentSector = sectors[i].sectorName;
                    }
                    if(sectors[i].level == 2){
                        subSector = ' > '+sectors[i].sectorName;
                    }
                }
            }
        }

        var sectorList= parentSector + subSector;

        return(
            <span className="item-field">{sectorList}</span>
        )
    }
});



module.exports = SectorList;