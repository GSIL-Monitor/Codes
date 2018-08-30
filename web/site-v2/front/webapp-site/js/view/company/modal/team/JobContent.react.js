var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../../../../react-kit/util/Functions');


const JobContent = React.createClass({


    render(){
        var data = this.props.data;
        if(Functions.isEmptyObject(data))
            return null;

        var job = data.job
        var domain = Functions.getJobFieldName(job.domain);
        var education = Functions.getEducationName(job.educationType);

        return(
            <div>
                <h3>{job.position}</h3>
                <p>{job.startDate}</p>
                <p>地点：{data.location}</p>
                <p>领域：{domain}</p>
                <p>教育：{education}</p>


            </div>
        )
    }

});


module.exports = JobContent;