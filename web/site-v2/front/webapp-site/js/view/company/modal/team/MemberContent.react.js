var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../../../../react-kit/util/Functions');

const MemberContent = React.createClass({

    render(){
        var data = this.props.data;
        if(Functions.isEmptyObject(data))
            return null;

        //console.log(data)

        var education = '暂无记录';
        var work = '暂无记录';
        if (!Functions.isNull(data.member.education)) {
            education = data.member.education;
        }

        if (!Functions.isNull(data.member.work)) {
            work = data.member.work;
        }

        return(
            <div>
                <h3>{data.member.name}</h3>
                <p>{data.companyMemberRel.position}</p>
                <p>教育：{education}</p>
                <p>工作：{work}</p>
            </div>
        )
    }

});


module.exports = MemberContent;