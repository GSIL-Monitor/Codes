var React = require('react');
var ReactDom = require('react-dom');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyStore = require('../../../store/CompanyStore');
var CompanyActions = require('../../../action/CompanyActions');
var CompanyUtil = require('../../../util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');

var ValidateCompanyStore = require('../../../store/validation/ValidateCompanyStore');
var ValidateCompanyActions = require('../../../action/validation/ValidateCompanyActions');

var UpdateInput = require('./UpdateInput.react');
var UpdateSelect = require('./UpdateSelect.react');
//var ChangeLocation = require('ChangeLocation.react.js');
var LocationInput = require('../../../../../react-kit/basic/search/LocationInput.react');

const UpdateHeader = React.createClass({

    mixins: [Reflux.connect(ValidateCompanyStore, 'validate')],

    render(){
        var data = this.props.data;
        var old = data.company;
        var logo;
        if(old.logo != null){
            logo = "/file/"+old.logo+"/product.png";
        }

        var nameClass = 'input-update-short ';
        var briefClass = 'input-update-full ';
        var dateClass = 'input-update-short ';
        var locationClass = 'search-location-input ';


        var update = data.updateCompany;
        var company =update;

        if(CompanyUtil.checkCompanyDiff(update.name, old.name)){
            nameClass += 'update ';
        }

        if(CompanyUtil.checkCompanyDiff(update.brief, old.brief)){
            briefClass += 'update';
        }

        if(CompanyUtil.checkCompanyDiff(update.establishDate, old.establishDate)){
            dateClass += 'update';
        }

        if(CompanyUtil.checkCompanyDiff(update.locationId, old.locationId)){
            locationClass += 'update';
        }

        if(!Functions.isEmptyObject(this.state)){
            var validate = this.state.validate;
            //if(validate.validateDate){
            //    dateClass += ' error';
            //}
            if(validate.validateLocation){
                locationClass += ' error';
            }
        }

        if(data.from == 'demodayAdd'){
            if(Functions.isNull(update.name))
                nameClass += ' error';

            if(Functions.isNull(update.brief))
                briefClass += ' error';

            if(Functions.isNull(update.locationId) || Functions.isNull(update.location)){
                locationClass += ' error';
            }

            //if(Functions.isNull(update.establishDate))
            //    dateClass += ' error';
        }

        //<a className="update-company">
        //    <span className="text-red" onClick={this.deleteCompany}>删除</span>
        //</a>

        var comfirmSpan = <span>
                                <a className="comfirm-company update-company" onClick={this.comfirm}>
                                    确定
                                </a>

                                <a className="update-company" onClick={this.update}>
                                    取消
                                </a>
                            </span>;

        if(data.from == 'demodayAdd'){
            comfirmSpan = <span>
                                <a className="comfirm-company update-company" onClick={this.comfirm}>
                                    提交项目
                                </a>
                            </span>;
        }

        //<UpdateInput className={dateClass}
        //             name="establishDate"
        //             data={company.establishDate}
        //             placeholder="创立时间(2016-01-01)"
        //             onBlur={this.handleDateBlur}
        //             ref="date" />


        return (
            <div className="company-header">
                <img className="company-logo" src={logo} />
                <div>
                    <div className="company-basic">
                        <p className="company-name">
                             <UpdateInput className={nameClass}
                                          name="name"
                                          data={company.name}
                                          placeholder="产品名称/公司简称"
                                 />
                             {comfirmSpan}
                        </p>

                        <UpdateInput className={briefClass}
                                     name="brief"
                                     data={company.brief}
                                     placeholder="一句话介绍" />


                        <UpdateEstablishDate data={data} />

                        <LocationInput  className = {locationClass}
                                        value={company.location}
                                        id={company.locationId}
                                        from="updateCompany"
                                        ref="location" />

                    </div>

                </div>

            </div>

        )
    },

    update(){
        CompanyActions.update();
    },

    comfirm(){
        ValidateCompanyActions.submit(CompanyActions);
    },

    locationComfirm(e){
        var locationName  = $('#input-location-name').val();
        if (locationName !=""){
            CompanyActions.changeCompany('location', locationName);
            $('#pop-location').hide();
            e.stopPropagation();
        }
    },

    handleDateBlur(value){
        ValidateCompanyActions.validateDate(value);
    },

    deleteCompany(){
        $('#delete-company-warn').show();
    }
});


const UpdateEstablishDate = React.createClass({
    render(){
        var data = this.props.data;
        var year = data.updateDateYear;
        var month = data.updateDateMonth;

        var yearSelect = CompanyUtil.yearSelect();
        var monthSelect = CompanyUtil.monthSelect();

        var yearClass = 'input-update-small ';
        var monthClass = 'input-update-small ';

        return(
            <div className="all-block m-b-10">
                <UpdateSelect   className={yearClass}
                                name= 'year'
                                value= {year}
                                select={yearSelect}
                    />

                <UpdateSelect   className={monthClass}
                                name= 'month'
                                value= {month}
                                select={monthSelect}
                    />
            </div>
        )
    }
});




module.exports = UpdateHeader;