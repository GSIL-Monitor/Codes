var React = require('react');
var $ = require('jquery');


// view
var FormInput = require('../form/FormInput.react');
var FormTextarea = require('../form/FormTextarea.react');
var FormDatePicker = require('../form/FormDatePicker.react');

var ActionUtil = require('../../action/ActionUtil');
var CompanyAction = require('../../action/CompanyAction');
var CompanyStore = require('../../store/CompanyStore');
var Functions = require('../../util/Functions');

function get(){
    return CompanyStore.get();
};

function getOld(){
    return CompanyStore.getOld();
};


const Company = React.createClass({


    getInitialState() {
        return get();
    },
    componentDidMount() {
        var store = get();
        if(store == null){
            CompanyAction.get(this.props.id);
        }else if(store.id != this.props.id) {
            CompanyAction.get(this.props.id);
        }else{
            this.setState(store);
        }

        CompanyStore.addChangeListener(this._onChange);
    },

    componentWillUnmount(){
        CompanyStore.removeChangeListener(this._onChange);
    },


    render() {
        $('.nav-c > ul > li:eq(0) > a').css('color', '#1c84c6');

        var state = this.state;
        if(state == null){
            return (<div></div>);
        }else{

        return (
            <div className= "left-part">
                <div>
                    <h3>基本信息</h3>

                    <FormInput label='名称'
                                name='name'
                                value={this.state.name}
                                onChange={this.handleChange} />

                    <FormInput label='公司全称'
                               name='fullName'
                               value={this.state.fullName}
                               onChange={this.handleChange} />

                    <FormTextarea label='描述'
                                  name='description'
                                  value={this.state.description}
                                  onChange={this.handleChange}
                                  className="desc"/>


                    <FormTextarea label='简介'
                               name='brief'
                               value={this.state.brief}
                               onChange={this.handleChange} />

                    <FormDatePicker label='成立时间'
                               name='establishDate'
                               value={this.state.establishDate}
                               onChange={this.datePick}
                               className="input-short" />

                    <FormInput label='最小人数'
                               name='headCountMin'
                               value={this.state.headCountMin}
                               onChange={this.handleChange}
                               className="input-short" />

                    <FormInput label='最大人数'
                               name='headCountMax'
                               value={this.state.headCountMax}
                               onChange={this.handleChange}
                               className="input-short" />

                    <div className="form-part">
                        <label>地址</label>
                        <input type="text"
                               className="input-short"
                               name="locationId"
                               value={this.state.locationId}
                               placeholder="地址ID"
                               onChange={this.handleChange}
                               onClick={this.handleClickLocation} />

                        <Location locationUpdate={this.locationChange} onClick={this.handleClickLocation}/>
                    </div>


                    <FormInput label='详细地址'
                               name='address'
                               value={this.state.address}
                               onChange={this.handleChange} />

                    <FormInput label='联系电话'
                               name='phone'
                               value={this.state.phone}
                               onChange={this.handleChange}
                               className="input-short" />


                </div>

                <div className="div-operate">
                    <button className="btn btn-navy" onClick={this.update}>更新</button>
                    <button className="btn btn-white" onClick={this.reset}>还原</button>
                </div>

            </div>

        );
        }
    },

    handleChange(event) {
        CompanyAction.change(event.target.name, event.target.value);
    },

    //datePick(date){
    //    console.log(date)
    //    CompanyAction.change('establishDate', date);
    //},

    update(){
        ActionUtil.checkUpdate(getOld(), get());
    },

    reset(){
        ActionUtil.reset(getOld(), get());
    },

    handleClickLocation(event){
        $('#pop-location ').show();
        event.stopPropagation();
    },

    locationChange(val){
        CompanyAction.change('locationId', val);
    },

    _onChange() {
        var store = get();

        if (store != null)
            this.setState(store);
    }

});




/***********  location ***********/

const Location = React.createClass({

    getInitialState: function() {
        return {data: Functions.locationUseful()};
    },

    render(){
        return(
            <div id="pop-location" className="pop-inner pop-right hide" onClick={this.handleClick}>
                <div>
                    <input type="text"
                           id="input-location-name"
                           placeholder="输入地名"
                           className="m-r-10"
                           onKeyDown={this.handleKeyDown}/>

                    <input type="text"
                           id="input-location-id"
                           className="m-r-10"
                           placeholder="地址ID"  />

                    <button className="btn btn-navy" onClick={this.handleComfirm}>确认</button>
                </div>
                <LocationList data={this.state.data} />
            </div>
        );
    },

    handleClick(){
        this.props.onClick();
    },


    handleKeyDown(event){
        if(event.keyCode === 13){
            var name = $('#input-location-name').val();
            var url = "http://localhost/web-admin/api/admin/company/get/location?name="+name;
            $.ajax({
                url: url,
                cache: false,
                success: function(data) {
                    $('#input-location-id').val(data)
                }
            });
        }
    },

    handleComfirm(event){
        var locationId = $('#input-location-id').val();
        if (locationId !=""){
            this.props.locationUpdate(locationId);
            $('#pop-location').hide();
            event.stopPropagation();
        }
    }

});

const LocationList =  React.createClass({
    render(){
        return(
            <div className="div-useful m-t-10">
                <h4>常用地址</h4>
                <ul>
                    { this.props.data.map(function(result){
                        return <LocationUseful key={result.value} name={result.name} value={result.value} />;
                    })}

                </ul>
            </div>
        )
    }

});

const LocationUseful = React.createClass({
    render(){
        return(
            <li onClick={this.handleClick}>
                <span>{this.props.name}</span>
                <strong>{this.props.value}</strong>
            </li>
        )
    },
    handleClick(event){
        $('#input-location-name').val(this.props.name);
        $('#input-location-id').val(this.props.value);
    }
});



module.exports = Company;

