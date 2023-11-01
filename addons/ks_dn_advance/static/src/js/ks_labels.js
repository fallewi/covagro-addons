odoo.define('ks_dashboard_ninja_list.ks_labels', function (require) {
    "use strict";

    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var field_utils = require('web.field_utils');
    var session = require('web.session');
    var utils = require('web.utils');

    var QWeb = core.qweb;

    var KsLabels = AbstractField.extend({
        resetOnAnyFieldChange: true,
        supportedFieldTypes: ['char'],

        events: _.extend({}, AbstractField.prototype.events, {
            'change select': 'ks_toggle_icon_input_click',
        }),
        init: function(){
            this.ks_columns = {};
            this._super.apply(this, arguments);
        },

        _renderEdit : function(){
            var self = this;
            self.$el.empty();
            var field = self.recordData;

            if(field.ks_query_result && field.ks_dashboard_item_type !== 'ks_kpi'){
                var ks_query_result = JSON.parse(field.ks_query_result);
                if (ks_query_result.header.length){
                    self.ks_check_for_labels();
                    var $view = $(QWeb.render('ks_select_labels',{
                        ks_columns_list: self.ks_columns,
                        mode: self.mode,
                    }));

                    if (self.value) {
                        $view.val(self.value);
                    }
                    this.$el.append($view)

                    if (this.mode === 'readonly') {
                        this.$el.find('.ks_label_select').addClass('ks_not_click');
                    }
                } else {
                    this.$el.append("No Data Available");
                }
            } else {
               this.$el.append("Please Enter the Appropriate Query for this");
            }
        },
        _renderReadonly : function(){
            var self = this;
            self.$el.empty();
            var field = self.recordData;

            if(field.ks_query_result){
                var ks_query_result = JSON.parse(field.ks_query_result);
                if (field.ks_dashboard_item_type !== 'ks_kpi' && ks_query_result.records.length){
                    self.ks_check_for_labels();
                    var $view = $(QWeb.render('ks_select_labels',{
                        ks_columns_list: self.ks_columns,
                        value: self.ks_columns[self.value],
                        mode: self.mode,
                    }));
                    self.$el.append($view);
                } else {
                    this.$el.append("No Data Available");
                }
            } else {
               this.$el.append("Please Enter the Appropriate Query for this")
            }
        },

        ks_toggle_icon_input_click: function(e){
            var self = this;
            self._setValue(e.currentTarget.value);
        },

        ks_check_for_labels: function(){
            var self = this;
            self.ks_columns = {false:false};
            var query_result = JSON.parse(self.recordData.ks_query_result);
            if (self.name === "ks_ylabels"){
                query_result.header.forEach(function(key){
                    if(typeof(query_result[0][key]) === "number") {
                        self.ks_columns[key] = self.ks_title(key.replace("_", " "));
                    }
                });
            } else {
                query_result.header.forEach(function(key){
                    self.ks_columns[key] = self.ks_title(key.replace("_", " "));
                });
            }
        },

        ks_title: function(str) {
            var split_str = str.toLowerCase().split(' ');
            for (var i = 0; i < split_str.length; i++) {
                split_str[i] = split_str[i].charAt(0).toUpperCase() + split_str[i].substring(1);
                str = split_str.join(' ');
            }
            return str;
        }
    });
    registry.add('ks_labels', KsLabels);

    return KsLabels

});