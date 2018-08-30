var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var FormSelect = require('../../../../../../react-kit/form/FormSelect.react');
var FormInput = require('../../../../../../react-kit/form/FormInput.react');
var FormTextarea = require('../../../../../../react-kit/form/FormTextarea.react');

var CompanyActions = require('../../../../action/CompanyActions');
var Functions = require('../../../../../../react-kit/util/Functions');

const FootprintContent = React.createClass({

    render(){
        var data = this.props.data;
        if(Functions.isEmptyObject(data))
            return null;

        var date = data.footDate;
        //if(date == null){
        //    date = new Date().format("yyyy-MM-dd");
        //    CompanyActions.changeNewFootprint('footDate', date);
        //}
        var desc = data.description;

        return(
            <div className="modal-info">

                <FormInput label='时间'
                           name='footDate'
                           className='input-short'
                           placeholder="例: 2016-01-01"
                           value={date}
                           onChange={this.handleChange} />

                <FormTextarea label='描述'
                              name='description'
                              className='input-short'
                              value={desc}
                              onChange={this.handleChange} />

                <div className="modal-comfirm">
                    <button className="btn btn-navy m-r-20 right" onClick={this.add}>
                        {this.props.name}
                    </button>
                </div>

            </div>

        )
    },

    handleChange(e){
        if(this.props.type == 'addFootprint')
            CompanyActions.changeNewFootprint(e.target.name, e.target.value);
        else
            CompanyActions.changeSelectedFootprint(e.target.name, e.target.value);
    },

    add(){
        if(this.props.type == 'addFootprint')
            CompanyActions.addFootprint();
        else
            CompanyActions.updateSelectedFootprint();

        $('.modal').hide();
    }
});

module.exports = FootprintContent;