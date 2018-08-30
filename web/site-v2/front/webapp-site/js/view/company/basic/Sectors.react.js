var React = require('react');
var Functions = require('../../../../../react-kit/util/Functions');
var UpdateSelect = require('../update/UpdateSelect.react');

const Sectors = React.createClass({
    render(){
        var data = this.props.data;
        //if(!Functions.isEmptyObject(sector)){
        //    sector = sector.sectorName;
        //}else{
        //    sector = null;
        //}
        //var arrow = <strong className="sector-arrow"> {'>'} </strong>
        //if(!Functions.isEmptyObject(subSector) && subSector != undefined) {
        //    subSector = <span>
        //                    {arrow}
        //        {subSector.sectorName}
        //                </span>;
        //}else{
        //    subSector = null;
        //}
        //
        //if(sector == null && subSector == null){
        //    sector = 'N/A';
        //}


        var parentSectors = data.parentSectors;
        var subSectors = data.subSectors;
        var parentSector = data.parentSector;
        var subSector = data.subSector;

        var sectors = [];
        if(Functions.isEmptyObject(parentSector)){
            var sector = {value: 0, name:'请选择行业'}
            sectors.push(sector)
        }

        for(var i in parentSectors){
            var sector = {};
            sector.name = parentSectors[i].sectorName;
            sector.value = parentSectors[i].id;
            sectors.push(sector)
        }

        var subs = [];
        if(Functions.isEmptyObject(subSector)){
            var sector = {value: 0, name:'请选择子行业'}
            subs.push(sector)
        }else{
            var subFlag = false;
            for(var i in subSectors){
                if(subSectors[i].id == subSector.id){
                    subFlag = true;
                }
            }
            if(!subFlag){
                var sector = {value: 0, name:'请选择子行业'}
                subs.push(sector)
            }
        }
        for(var i in subSectors){
            var sub = {};
            sub.name = subSectors[i].sectorName;
            sub.value = subSectors[i].id;
            subs.push(sub);
        }

        var sectorId;
        var subSectorId;
        if(parentSector!=null) sectorId = parentSector.id;
        if(subSector != null) subSectorId = subSector.id;

        if(Functions.isNull(sectorId)) sectorId = 0;
        if(Functions.isNull(subSectorId)) subSectorId = 0;


        return (
            <div className="section-sub-item sector-part">
                <div className="section-sub-item-name">行业：</div>
                <div className="section-sub-item-content">
                    <UpdateSelect   className='select-update-small'
                                    name= 'companySector'
                                    value= {sectorId}
                                    select={sectors}
                        />

                    <UpdateSelect   className='select-update-small'
                                    name= 'companySubSector'
                                    value= {subSectorId}
                                    select={subs}
                        />
                </div>
            </div>
        )
    }
});

module.exports = Sectors;