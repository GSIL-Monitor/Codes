var React = require('react');
var $ = require('jquery');


// view
var FormInput = require('../form/FormInput.react');
var FormTextarea = require('../form/FormTextarea.react');
var FormSelect = require('../form/FormSelect.react');

var ActionUtil = require('../../action/ActionUtil');

var Functions = require('../../util/Functions');



const MemberForm = React.createClass({

    getInitialState() {
        return {};
    },

    render() {
        var detail = this.props.data;
        //console.log(detail);

        if (detail == null){
            return(
                <div>无</div>
            )
        }else{

            return(
                <div className="sub-round">
                    <div>
                        <h3>成员详情</h3>
                        <div className="form-part">
                            <label>照片</label>
                            <img src={"/file/" + detail.member.photo} width="100"/>
                        </div>
                        <FormSelect label='成员类型'
                                    name='type'
                                    value={detail.rel.type}
                                    select = {Functions.memberTypeSelect()}
                                    onChange={this.handleChange} />
                        <FormInput label='职位'
                                   name='position'
                                   value={detail.rel.position||""}
                                   className='input-short'
                                   onChange={this.handleChange} />
                        <FormInput label='姓名'
                                   name='name'
                                   value={detail.member.name||""}
                                   className='input-short'
                                   onChange={this.handleChange} />
                        <FormTextarea label='教育'
                                      name='education'
                                      value={detail.member.education||""}
                                      onChange={this.handleChange}
                                      className="desc"/>
                        <FormTextarea label='工作'
                                      name='work'
                                      value={detail.member.work||""}
                                      onChange={this.handleChange}
                                      className="desc"/>
                        <FormTextarea label='工作重点'
                                      name='workEmphasis'
                                      value={detail.member.workEmphasis||""}
                                      onChange={this.handleChange}
                                      className="desc"/>
                    </div>

                    <div className="div-operate">
                        <a className="a-red m-t-10 m-l-10 left" onClick={this.handleDelete}>删除</a>
                        <button className="btn btn-navy" onClick={this.handleUpdate}>更新</button>
                    </div>
                </div>
            )
        }

    },

    handleChange(event){
        this.props.onChange(event);
    },

    handleUpdate(){
        var info = this.props.data.member.name;
        var content = '<p>'+info+'</p>';
        $('#modal-update').show();
        $('.modal-content').html(content);
    },

    handleDelete(){
        var info = this.props.data.member.name;
        //console.log(info);
        ActionUtil.delete(info);
    },

});


module.exports = MemberForm;
