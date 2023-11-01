odoo.define("ks_dashboard_ninja.ks_ylabels", function(require){

    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var field_utils = require('web.field_utils');
    var session = require('web.session');
    var utils = require('web.utils');
    var QWeb = core.qweb;
    var KsYLabels = AbstractField.extend({
        resetOnAnyFieldChange: true,
        supportedFieldTypes: ['char'],
        events: _.extend({}, AbstractField.prototype.events, {
            'change select': 'ks_toggle_icon_input_click',
            'blur .ks_stack_group': 'ks_group_input_click',
        }),
        init: function(){
            this.ks_columns = {};
            this.ks_rows_keys = [];
            this.ks_rows_chart_type = {}
            this._super.apply(this, arguments);
        },

        _render: function () {
            var self = this;
            self.$el.empty();
            var field = self.recordData;
            if(field.ks_query_result && field.ks_dashboard_item_type !== 'ks_kpi'){
                var ks_query_result = JSON.parse(field.ks_query_result);
                if (field.ks_dashboard_item_type !== 'ks_kpi' && ks_query_result.header.length){
                    if (field.ks_dashboard_item_type !== 'ks_list_view' && field.ks_dashboard_item_type !=='ks_kpi' && field.ks_dashboard_item_type !== 'ks_tile'){
                        self.ks_check_for_labels();
                        var $view = $(QWeb.render('ks_y_label_table',{
                            label_rows: self.ks_columns,
                            chart_type: self.ks_rows_chart_type,
                            mode: self.mode,
                            ks_is_group_column: ks_query_result.ks_is_group_column
                        }));

                        self.ks_rows_keys.forEach(function(key){
                            $view.find('#' + key).val(self.ks_rows_chart_type[key]);
                        })

                        self.$el.append($view);
                        if (this.mode == 'edit') self.ks_toggle_icon_input_click();
                    }
                } else {
                    this.$el.append("No Data Available");
                }
            } else {
                this.$el.append("Please Enter the Appropriate Query for this");
            }
            if (this.mode === 'readonly') {
                this.$el.find('select').addClass('ks_not_click');
                this.$el.find('td.ks_stack_group').addClass('ks_not_click');
            }
        },
        ks_check_for_labels: function(){
            var self = this;
            self.ks_columns = {};
            if(self.value){
                var ks_columns = JSON.parse(self.value);
                Object.keys(ks_columns).forEach(function(key){
                    var chart_type = ks_columns[key]['chart_type'];
                    self.ks_rows_chart_type[key] = chart_type;
                    ks_columns[key]['chart_type'] = {}
                    if(self.recordData.ks_dashboard_item_type === 'ks_bar_chart'){
                        var chart_type_temp = self.recordData.ks_dashboard_item_type.split("_")[1];
                        if (chart_type_temp !== chart_type) {
                            chart_type = chart_type_temp;
                        }
                        ks_columns[key]['chart_type'][chart_type] = self.ks_title(chart_type);
                        if (chart_type === "bar"){
                            ks_columns[key]['chart_type']["line"] = "Line";
                        } else {
                            ks_columns[key]['chart_type']["bar"] = "Bar"
                        }
                    } else {
                        var chart_type = self.recordData.ks_dashboard_item_type.split("_")[1];
                        ks_columns[key]['chart_type'][chart_type] = self.ks_title(chart_type);
                        if (chart_type === "bar") ks_columns[key]['chart_type']["line"] = "Line";
                    }
                    self.ks_rows_keys.push(key);
                });
                self.ks_columns = ks_columns;
            } else {
                var query_result = JSON.parse(self.recordData.ks_query_result);

                query_result.header.forEach(function(key){
                    for(var i =0;i< query_result.header.length; i++){
                        if(query_result.type_code[query_result.header.indexOf(key)] !== 'numeric'){
                            continue;
                        }
                        if(query_result.type_code[query_result.header.indexOf(key)] == 'numeric') {
                            var ks_row = {}
                            ks_row['measure'] = self.ks_title(key.replace("_", " "));
                            ks_row['chart_type'] = {}
                            var chart_type = self.recordData.ks_dashboard_item_type.split("_")[1];
                            ks_row['chart_type'][chart_type] = self.ks_title(chart_type);
                            if (chart_type === "bar") ks_row['chart_type']["line"] = "Line";
                            ks_row['group'] = " ";
                            self.ks_columns[key] = ks_row;
                        }
                        break;
                    }
                });
            }
        },

        ks_toggle_icon_input_click: function(e){
            var self = this;

            var ks_tbody = this.$el.find('tbody.ks_y_axis');
            ks_tbody.find('select').each(function(){
                self.ks_columns[this.id]['chart_type'] = this.value;
            });
            var value = JSON.stringify(self.ks_columns);
            self._setValue(value);
        },

        ks_title: function(str) {
            var split_str = str.toLowerCase().split(' ');
            for (var i = 0; i < split_str.length; i++) {
                split_str[i] = split_str[i].charAt(0).toUpperCase() + split_str[i].substring(1);
                str = split_str.join(' ');
            }
            return str;
        },

        ks_group_input_click: function(e){
            var self = this;
            var ks_tbody = this.$el.find('tbody.ks_y_axis');
            ks_tbody.find('select').each(function(){
                self.ks_columns[this.id]['chart_type'] = this.value;
            });
            self.ks_columns[e.currentTarget.id]['group'] = e.currentTarget.textContent.trim();
            var value = JSON.stringify(self.ks_columns);
            self._setValue(value);
        }
    });

    registry.add('ks_y_labels', KsYLabels);

    return KsYLabels;
});