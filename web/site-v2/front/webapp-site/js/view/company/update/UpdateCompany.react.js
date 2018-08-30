var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyStore = require('../../../store/CompanyStore');
var CompanyActions = require('../../../action/CompanyActions');
var CompanyUtil = require('../../../util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');
var ButtonAdd = require('../../../../../react-kit/basic/ButtonAdd.react');

var UpdateInput = require('./UpdateInput.react');
var Select  = require('../../../../../react-kit/form/Select.react');
var AddTagList = require('../modal/tag/AddTagList.react');

var UpdateFundingStatus = require('./UpdateFundingStatus.react');
var UpdateFundings = require('./UpdateFundings.react.js');
var UpdateFootprints = require('./UpdateFootprints.react.js');
var UpdateFiles = require('./UpdateDocuments.react.js');
var UpdateSelect  = require('./UpdateSelect.react');

var Recommendation = require('../../demoDay/add/Recommendation.react');


const UpdateCompany = React.createClass({

    render(){

        if(Functions.isEmptyObject(this.props.data))
            return null;

        var data = this.props.data;
        var company = data.updateCompany;
        var desc = company.description;
        var old_company = data.company;

        //<UpdateFundings  data={data.updateFundings}
        //                 newFundings={data.newFundings}
        //                 old={data.fundings} />
        //<UpdateFootprints data={data.updateFootprints}
        //                newFootprints={data.newFootprints}
        //                old={data.footprints} />


        var from = data.from;
        var recommendation;
        if(from == 'demodayAdd'){
            recommendation = <Recommendation />;
        }


        return (
            <div className="section first-section">
                <span className="section-header">
                    公司信息
                </span>

                <UpdateDesc data={data}/>

                {recommendation}

                <UpdateBasic data={data} />

                <UpdateFundingStatus data={data}/>

                <UpdateFiles data={data} />


            </div>
        )
    }
});


const UpdateDesc = React.createClass({
    render(){

        var className= 'textarea-update-full ';

        var data = this.props.data;
        var update_desc = data.updateCompany.description;
        var old_desc = data.company.description;

        if(CompanyUtil.checkCompanyDiff(update_desc, old_desc)){
            className += 'update';
        }

        var updateClass = "section-round ";
        if(data.from == 'demodayAdd'){
            if(Functions.isNull(update_desc))
                updateClass += 'section-must-update'
        }

        return(
            <section className="section-body">
                <div className={updateClass}>
                    <div className="section-name name2">
                        简介
                    </div>
                </div>
                <div className="section-content">
                    <textarea  className={className}
                               name="description"
                               value={update_desc}
                               onChange={this.change}
                               onMouseOver={this.onMouseOver}
                               onMouseOut={this.onMouseOut}
                               placeholder="公司简介"
                        />
                </div>
            </section>
        )
    },

    change(e){
        CompanyActions.changeCompany(e.target.name, e.target.value);
    },

    onMouseOver(){
        //document.body.style.overflow = 'hidden';
    },

    onMouseOut(){
        //document.body.style.overflow = 'auto';
    }
});


const UpdateBasic = React.createClass({
    render(){

        var data= this.props.data;
        var company = data.updateCompany;
        var old_company = data.company;

        var from = data.from;

        return(
            <section className="section-body">
                <div className="section-round">
                    <div className="section-name name4">
                        基本<br/>信息
                    </div>
                </div>
                <div className="section-content">

                    <UpdateFullName data={company.fullName}
                                    old={old_company.fullName}/>

                    <UpdateHeadCount data={company.headCountMin}
                                    old={old_company.headCountMin}/>

                    <UpdateSectors parentSectors={data.parentSectors}
                                   subSectors = {data.subSectors}
                                   parentSector={data.updateParentSector}
                                   oldParent = {data.parentSector}
                                   subSector = {data.updateSubSector}
                                   oldSub = {data.subSector}
                                   from = {from}
                        />

                    <UpdateTag data={data.updateTags} newTags={data.newTags}/>

                </div>
            </section>
        )
    }

});


const UpdateFullName= React.createClass({
    render(){
        var className= 'input-update-full ';
        if(CompanyUtil.checkCompanyDiff(this.props.data, this.props.old)){
            className += 'update';
        }

        return(
            <div className="section-sub-item">
                <div className="section-sub-item-name  update-field-name">公司名称：</div>
                <div className="section-sub-item-content">
                    <UpdateInput className={className}
                                 name="fullName"
                                 data={this.props.data}
                                 placeholder="公司全称"
                        />
                </div>
            </div>
        )
    }
});

const UpdateHeadCount = React.createClass({
    render(){
        var headCountMin = this.props.data;
        var old_headCountMin = this.props.old;
        var headCount = CompanyUtil.getHeadCount(headCountMin);
        var headCountSelect = CompanyUtil.headCountSelect();

        var headCountClass = 'input-update-small ';
        if(CompanyUtil.checkCompanyDiff(headCountMin, old_headCountMin)){
            headCountClass += 'update';
        }

        return(
            <div className="section-sub-item select-part">
                <div className="section-sub-item-name  update-field-name">团队规模：</div>
                <div className="section-sub-item-content">
                    <UpdateSelect   className={headCountClass}
                                    name= 'headCount'
                                    value= {headCount}
                                    select={headCountSelect}
                        />
                </div>
            </div>
        )

    }
});


const UpdateSectors= React.createClass({
    render(){
        var parentSectors = this.props.parentSectors;
        var subSectors = this.props.subSectors;
        var parentSector = this.props.parentSector;
        var subSector = this.props.subSector;

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
        }
        for(var i in subSectors){
            var sub = {};
            sub.name = subSectors[i].sectorName;
            sub.value = subSectors[i].id;
            subs.push(sub)
        }


        var sectorId;
        var subSectorId;
        if(parentSector!=null) sectorId = parentSector.id;
        if(subSector != null) subSectorId = subSector.id;

        var oldParent = this.props.oldParent;
        var subParent = this.props.oldSub;

        var parentClass = 'input-update-small ';
        if(CompanyUtil.checkSectorDiff(parentSector, oldParent)){
            parentClass += 'update'
        }

        var subClass = 'input-update-small ';
        if(CompanyUtil.checkSectorDiff(subSector, subParent)){
            subClass += 'update'
        }

        var from = this.props.from;
        var updateClass = 'section-sub-item-name  update-field-name ';
        if(from == 'demodayAdd'){
            if( Functions.isEmptyObject(parentSector)||
                Functions.isEmptyObject(subSector)){
                updateClass += 'field-must-update';
            }
        }



        return(
            <div className="section-sub-item select-part">
                <div className={updateClass}>
                    行业：</div>
                <div className="section-sub-item-content">

                    <UpdateSelect   className={parentClass}
                                    name= 'parentSector'
                                    value= {sectorId}
                                    select={sectors}
                        />

                    <UpdateSelect   className={subClass}
                                    name= 'subSector'
                                    value= {subSectorId}
                                    select={subs}
                        />


                </div>
            </div>
        )
    },

    changeSector(e){
        CompanyActions.changeSector(e.target.value);
    },

    changeSubSector(e){
        CompanyActions.changeSubSector(e.target.value);
    }
});

const UpdateTag= React.createClass({
    render(){
        var tagList;

        if(this.props.data != null){
            if(this.props.data.length > 0){
                tagList = this.props.data.map(function (result) {
                    return <UpdateTagItem key={result.id} data={result}/>;
                });
            }
        }

        return(
            <div className="section-sub-item">
                <div className="section-sub-item-name">标签：</div>
                <div className="section-sub-item-content">
                    {tagList}

                    <AddTagList data={this.props.newTags}/>

                    <ButtonAdd onClick={this.add}/>
                </div>
            </div>
        )
    },

    add(){
        $('#add-tag-modal').show();
    }
});



const UpdateTagItem = React.createClass({
    render(){
        return(
            <div className="label tag">
                {this.props.data.name}
                <i className="fa fa-times m-l-10 label-close" onClick={this.delete}></i>
            </div>
        )
    },

    delete(){
        CompanyActions.deleteTag(this.props.data.id);
    }
});



module.exports = UpdateCompany;