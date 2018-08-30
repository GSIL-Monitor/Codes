var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

// view
var FormInput = require('../form/FormInput.react');
var FormTextarea = require('../form/FormTextarea.react');
var FormSelect = require('../form/FormSelect.react');
var Functions = require('../../util/Functions');

var InvestorStore = require('../../reflux/InvestorStore');
var InvestorActions = require('../../reflux/InvestorActions');
var SourceInvestor = require('./SourceInvestor.react');

const UpdateForm = React.createClass({
    mixins: [Reflux.connect(InvestorStore, 'data')],
    getInitialState: function () {
        return null;
    },
    componentDidMount: function () {
        InvestorActions.get(this.props.id);
    },

    render() {
        //console.log(current);
        if(this.state.data == null || this.state.data.current == null) {
            return (<div>无数据</div>);
        }
        else {
            var current = this.state.data.current;
            var img = "";
            if (current.logo != null && current.logo != "") {
                img = <img src={"/file/" + current.logo} width="100"/>
            }

            return (
                <div className="m-t-10">
                    <div className="left-part">
                        <div className="sub-round">
                            <div>
                                <h3>更新投资人信息</h3>
                                <div className="form-part">
                                    <label>Logo</label>
                                    {img}
                                </div>
                                <FormInput label='姓名*'
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
                                <a className="a-red m-t-10 m-l-10 left" onClick={this.handleDelete}>删除</a>
                                <button className="btn btn-navy" onClick={this.handleUpdate}>更新</button>
                            </div>
                        </div>
                    </div>
                    <SourceInvestor investors={this.state.data.sources}/>
                </div>
            )
        }
    },

    handleChange(event){
        //console.log("handleChange");
        InvestorActions.change(event.target.name, event.target.value);
    },

    handleUpdate() {
        var name = this.state.data.current.name.trim();
        if( name == ""){
            return;
        }
        var content = '<p>'+name+'</p>';
        $('#modal-update').show();
        $('.modal-content').html(content);
    },

    handleDelete(){
        var name = this.state.data.current.name.trim();
        var content = '<p>'+name+'</p>';
        $('#modal-delete').show();
        $('.modal-content').html(content);
    },
});


module.exports = UpdateForm;
