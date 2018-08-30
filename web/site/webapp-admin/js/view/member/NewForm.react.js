var React = require('react');
var $ = require('jquery');

// view
var FormInput = require('../form/FormInput.react');
var FormTextarea = require('../form/FormTextarea.react');
var FormSelect = require('../form/FormSelect.react');
var LastMember = require('./LastMember.react');
var NewMemberStore = require('../../store/member/NewMemberStore');
var NewAction = require('../../action/member/NewAction');
var ActionUtil = require('../../action/ActionUtil');

var Functions = require('../../util/Functions');



const NewForm = React.createClass({

    getInitialState() {
        return {data:NewMemberStore.get()};
    },

    componentDidMount() {
        NewMemberStore.addChangeListener(this._onChange);
    },
    componentWillUnmount(){
        NewMemberStore.removeChangeListener(this._onChange);
    },

    render() {
        current = this.state.data.current;
        return(
        <div className="m-t-10">
            <div className="left-part">
                <div className="sub-round">
                    <div>
                        <h3>添加新成员</h3>
                        <div className="form-part">
                            <label>照片</label>
                        </div>
                        <FormInput label='姓名*'
                                   name='name'
                                   value={current.name}
                                   className='input-short'
                                   onChange={this.handleChange} />
                        <FormTextarea label='教育'
                                      name='education'
                                      value={current.education}
                                      onChange={this.handleChange}
                                      className="desc"/>
                        <FormTextarea label='工作'
                                      name='work'
                                      value={current.work}
                                      onChange={this.handleChange}
                                      className="desc"/>
                        <FormTextarea label='工作重点'
                                      name='workEmphasis'
                                      value={current.workEmphasis}
                                      onChange={this.handleChange}
                                      className="desc"/>
                    </div>

                    <div className="div-operate">
                        <a className="a-red m-t-10 m-l-10 left" onClick={this.handleClean}>清除</a>
                        <button className="btn btn-navy" onClick={this.handleAdd}>添加</button>
                    </div>
                </div>
            </div>
            <LastMember />
        </div>
        )

    },

    handleChange(event){
        console.log(event);
        NewAction.change(event.target.name, event.target.value);
    },

    _onChange() {
        console.log(NewMemberStore.get());
        this.setState({data:NewMemberStore.get()});
    },

    handleClean(){
        $('#modal-clean').show();
        $('.modal-content').html("");
    },

    handleAdd(){
        //console.log("handleAdd");
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
