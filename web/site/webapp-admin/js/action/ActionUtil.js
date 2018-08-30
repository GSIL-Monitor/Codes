var $ = require('jquery');
var ActionUtil = {

    checkUpdate: function(old, update){
        var updates = [];

        for(var k in old){
            if(old[k]!= update[k]){
                var p =  '<p>'+k+': <span>'+old[k]+ '</span> --> <strong>' + update[k]+'</strong></p>';
                updates.push(p)
            }
        }

        if (updates.length > 0){
            var content = '';
            updates.forEach(function(data){
                content += data;
            });

            $('#modal-update').show();
            $('#modal-update > .modal-body > .modal-content').html(content);

        }
    },

    reset: function(old, update){
        var updates = [];

        for(var k in old){
            if(old[k]!= update[k]){
                var p =  '<p>'+k+': <span>'+update[k]+ '</span> --> <strong>' + old[k]+'</strong></p>';
                updates.push(p)
            }
        }

        if (updates.length > 0){
            var content = '';
            updates.forEach(function(data){
                content += data;
            });

            $('#modal-reset').show();
            $('#modal-reset > .modal-body > .modal-content').html(content);

        }
    },

    delete(data){
        var content = '<p>'+data+'</p>';
        $('#modal-delete').show();
        $('#modal-delete > .modal-body > .modal-content').html(content);
    }

};

module.exports = ActionUtil;


