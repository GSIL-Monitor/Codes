var React = require('react');

var MobileFooter = React.createClass({

    render() {
        var year = new Date().getFullYear();

        return (
            <footer>
                <div className="footer right">
                    &copy; {year}
                </div>
            </footer>
        );
    }

});

module.exports = MobileFooter;
