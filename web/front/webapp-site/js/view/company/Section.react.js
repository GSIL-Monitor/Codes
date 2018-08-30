var React = require('react');
var $ = require('jquery');

const Section = React.createClass({
    render(){
        var section = this.props.data;
        var id = 0;
        return(
            <div className="section">
                <span className="section-header">
                    {section.header}
                </span>
                { section.data.map(function (result) {
                    id++;
                    return <SectionBody key={id} data={result}/>;
                }.bind(this))}
            </div>
        )
    }
});

const SectionBody = React.createClass({
    render(){
        return(
            <section className="section-body">
                <div className="section-left">
                    <div className="section-left-name name2">
                        {this.props.data.name}
                    </div>
                </div>
                <div className="section-right">
                    {this.props.data.content}
                </div>
            </section>
        )
    }
});

module.exports = Section;