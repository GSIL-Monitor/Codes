var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var SettingStore = require('../../../store/user/SettingStore');
var SettingActions = require('../../../action/user/SettingActions');

var Functions = require('../../../../../react-kit/util/Functions');

const SelectSector = React.createClass({

    render(){
        var data = this.props.data;
        var sectors = data.sectors;
        var selectedSectors = data.selectedSectors;

        return (
            <div className="all-block">
                 <h2>关注领域</h2>

                <div className="sector-list all-block">
                    {sectors.map(function(result, index){
                        return <Sector key={index} data={result} selected={selectedSectors}/>
                    })}
                </div>
            </div>

        );
    }

});


const Sector = React.createClass({

    render(){
        var className='setting-sector ';
        var selected = this.props.selected;
        if(!Functions.isEmptyObject(selected)){
            var sectors = selected;
            if(sectors.length > 0){
                for(var i in sectors){
                    if(this.props.data.id == sectors[i])
                        className += 'sector-selected';
                }
            }
        }

        return(
            <div className={className}
                 onClick={this.click} >
                {this.props.data.sectorName}
            </div>
        )
    },

    click(){
        SettingActions.selectSector(this.props.data);
    }
});



module.exports = SelectSector;

