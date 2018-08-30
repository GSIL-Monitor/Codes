var React = require('react');

var Span = React.createClass({

    render: function() {
        return (
            <div className="form-part">
                <label>
                    {this.props.name}
                </label>

              <span>
                  {this.props.value}
              </span>
            </div>
        );
    }
});

module.exports = Span;
