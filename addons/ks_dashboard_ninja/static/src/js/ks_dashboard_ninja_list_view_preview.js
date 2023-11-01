odoo.define('ks_dashboard_ninja_list.ks_dashboard_ninja_list_view_preview', function(require) {
    "use strict";

    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');

    var QWeb = core.qweb;
    var field_utils = require('web.field_utils');
    var time = require('web.time');
    var _t = core._t;

    var KsListViewPreview = AbstractField.extend({
        supportedFieldTypes: ['char'],

        resetOnAnyFieldChange: true,

        init: function(parent, state, params) {
            this._super.apply(this, arguments);
            var l10n = _t.database.parameters;
            this.date_format = time.strftime_to_moment_format(_t.database.parameters.date_format)
            this.date_format = this.date_format.replace(/\bYY\b/g, "YYYY");
            this.datetime_format = time.strftime_to_moment_format((_t.database.parameters.date_format + ' ' + l10n.time_format))
            this.state = {};
        },

        _render: function() {
            this.$el.empty()
            var rec = this.recordData;
            if (rec.ks_dashboard_item_type === 'ks_list_view') {
                if (rec.ks_list_view_type == "ungrouped") {
                    if (rec.ks_list_view_fields.count !== 0) {
                        this.ksRenderListView();
                    } else {
                        this.$el.append($('<div>').text("Select Fields to show in list view."));
                    }
                } else if (rec.ks_list_view_type == "grouped") {
                    if (rec.ks_list_view_group_fields.count !== 0 && rec.ks_chart_relation_groupby) {
                        if (rec.ks_chart_groupby_type === 'relational_type' || rec.ks_chart_groupby_type === 'selection' || rec.ks_chart_groupby_type === 'other' || rec.ks_chart_groupby_type === 'date_type' && rec.ks_chart_date_groupby) {
                            this.ksRenderListView();
                        } else {
                            this.$el.append($('<div>').text("Select Group by Date to show list data."));
                        }

                    } else {
                        this.$el.append($('<div>').text("Select Fields and Group By to show in list view."));

                    }
                }
            }
        },

        ksRenderListView: function() {
            var self = this;
            var field = this.recordData;
            var ks_list_view_name;
            var list_view_data = JSON.parse(field.ks_list_view_data);
            var count = field.ks_record_count;
            if (field.name) ks_list_view_name = field.name;
            else if (field.ks_model_name) ks_list_view_name = field.ks_model_id.data.display_name;
            else ks_list_view_name = "Name";
            if (field.ks_list_view_type === "ungrouped" && list_view_data) {
                var index_data = list_view_data.date_index;
                if (index_data){
                    for (var i = 0; i < index_data.length; i++) {
                        for (var j = 0; j < list_view_data.data_rows.length; j++) {
                            var index = index_data[i]
                            var date = list_view_data.data_rows[j]["data"][index]
                            if (date){
                             if( list_view_data.fields_type[index] === 'date'){
                                    list_view_data.data_rows[j]["data"][index] = moment(new Date(date)).format(this.date_format) , {}, {timezone: false};
                             } else{
                                list_view_data.data_rows[j]["data"][index] = field_utils.format.datetime(moment(moment(date).utc(true)._d), {}, {
                                timezone: false
                            });
                            }

                            }else {list_view_data.data_rows[j]["data"][index] = "";}
                        }
                    }
                }
            }

            if (field.ks_list_view_data) {
                var data_rows = list_view_data.data_rows;
                if (data_rows){
                    for (var i = 0; i < list_view_data.data_rows.length; i++) {
                    for (var j = 0; j < list_view_data.data_rows[0]["data"].length; j++) {
                        if (typeof(list_view_data.data_rows[i].data[j]) === "number" || list_view_data.data_rows[i].data[j]) {
                            if (typeof(list_view_data.data_rows[i].data[j]) === "number") {
                                list_view_data.data_rows[i].data[j] = field_utils.format.float(list_view_data.data_rows[i].data[j], Float64Array, {digits: [0, field.ks_precision_digits]})
                            }
                        } else {
                            list_view_data.data_rows[i].data[j] = "";
                        }
                    }
                }
                }
            } else list_view_data = false;
            count = list_view_data && field.ks_list_view_type === "ungrouped" ? count - list_view_data.data_rows.length : false;
            count = count ? count <=0 ? false : count : false;
            var $listViewContainer = $(QWeb.render('ks_list_view_container', {
                ks_list_view_name: ks_list_view_name,
                list_view_data: list_view_data,
                count: count,
                layout: self.recordData.ks_list_view_layout,
            }));
            if (!this.recordData.ks_show_records === true) {
                $listViewContainer.find('#ks_item_info').hide();
            }
            this.$el.append($listViewContainer);
        },


    });
    registry.add('ks_dashboard_list_view_preview', KsListViewPreview);

    return {
        KsListViewPreview: KsListViewPreview,
    };

});