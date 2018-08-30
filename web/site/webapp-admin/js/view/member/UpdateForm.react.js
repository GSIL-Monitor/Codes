var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

// view
var FormInput = require('../form/FormInput.react');
var FormTextarea = require('../form/FormTextarea.react');
var FormSelect = require('../form/FormSelect.react');
var LastMember = require('./LastMember.react');
var MemberStore = require('../../reflux/MemberStore');
var MemberActions = require('../../reflux/MemberActions');
var SourceMember = require('./source/SourceMember.react');

const UpdateForm = React.createClass({
    mixins: [Reflux.connect(MemberStore, 'current')],
    getInitialState: function () {
        return {current: null};
    },
    componentDidMount: function () {
        MemberActions.get(this.props.id);
    },

    render() {
        current = this.state.current;
        //console.log(current);
        if(current == null || current == "") {
            return (<div>无数据</div>);
        }
        var img = "";
        if(current.photo!=null && current.photo!=""){
            img = <img src={"/file/" + current.photo} width="100"/>
        }
        return(
        <div className="m-t-10">
            <div className="left-part">
                <div className="sub-round">
                    <div>
                        <h3>更新成员信息</h3>
                        <div className="form-part">
                            <label>照片</label>
                            {img}
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
                        <a className="a-red m-t-10 m-l-10 left" onClick={this.handleDelete}>删除</a>
                        <button className="btn btn-navy" onClick={this.handleAdd}>更新</button>
                    </div>
                </div>
            </div>
            <SourceMember id={current.id} />
        </div>
        )

    },

    handleChange(event){
        //console.log("handleChange");
        MemberActions.change(event.target.name, event.target.value);
    },

    handleAdd() {
        var name = this.state.current.name.trim();
        if( name == ""){
            return;
        }
        var content = '<p>'+name+'</p>';
        $('#modal-update').show();
        $('.modal-content').html(content);
    },

    handleDelete(){
        var name = this.state.current.name.trim();
        var content = '<p>'+name+'</p>';
        $('#modal-delete').show();
        $('.modal-content').html(content);
    },
});


module.exports = UpdateForm;
