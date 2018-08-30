var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

// view
var FormInput = require('../form/FormInput.react');
var FormTextarea = require('../form/FormTextarea.react');
var FormSelect = require('../form/FormSelect.react');
var LastInvestor = require('./LastInvestor.react');
var InvestorStore = require('../../reflux/InvestorStore');
var InvestorActions = require('../../reflux/InvestorActions');
var ActionUtil = require('../../action/ActionUtil');

var Functions = require('../../util/Functions');


const NewForm = React.createClass({
    mixins: [Reflux.connect(InvestorStore, 'data')],
    getInitialState: function () {
        return null;
    },
    componentDidMount: function () {
        //console.log("componentDidMount");
        InvestorActions.clean();
    },

    render() {
        //console.log(this.state.data);
        if(this.state.data == null){
            return (
                <div className="m-t-10"></div>
            )
        }
        else {
            current = this.state.data.current;
            return (
                <div className="m-t-10">
                    <div className="left-part">
                        <div className="sub-round">
                            <div>
                                <h3>添加新投资人</h3>
                                <FormInput label='名称*'
                                           name='name'
                                           value={current.name}
                                           className='input-short'
                                           onChange={this.handleChange}/>
                                <FormSelect label='类型'
                                            name='type'
                                            value={current.type||10020}
                                            select={Functions.investorTypeSelect()}
                                            onChange={this.handleChange}/>
                                <FormInput label='网站'
                                           name='website'
                                           value={current.website||""}
                                           className='input-short'
                                           onChange={this.handleChange}/>
                                <FormTextarea label='简介'
                                              name='description'
                                              value={current.description||""}
                                              onChange={this.handleChange}
                                              className="desc"/>
                                <FormTextarea label='投资阶段'
                                              name='stage'
                                              value={current.stage||""}
                                              onChange={this.handleChange}
                                              className="desc"/>
                                <FormTextarea label='投资领域'
                                              name='field'
                                              value={current.field||""}
                                              onChange={this.handleChange}
                                              className="desc"/>
                            </div>

                            <div className="div-operate">
                                <a className="a-red m-t-10 m-l-10 left" onClick={this.handleClean}>清除</a>
                                <button className="btn btn-navy" onClick={this.handleAdd}>添加</button>
                            </div>
                        </div>
                    </div>
                    <LastInvestor data={this.state.data.last}/>
                </div>
            )
        }
    },

    handleChange(event){
        //console.log(event.target.value);
        InvestorActions.change(event.target.name, event.target.value);
    },

    handleClean(){
        $('#modal-clean').show();
        $('.modal-content').html("");
    },

    handleAdd(){
        //console.log(this.state.data.current);
        var name = this.state.data.current.name.trim();
        if( name == ""){
            return;
        }
        var content = '<p>'+name+'</p>';
        $('#modal-add').show();
        $('.modal-content').html(content);
    },

});


module.exports = NewForm;
