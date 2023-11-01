odoo.define('ks_dashboard_ninja_list.ks_to_do_preview', function(require) {
    "use strict";

    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');

    var QWeb = core.qweb;
    var field_utils = require('web.field_utils');

    var KsToDOViewPreview = AbstractField.extend({
        supportedFieldTypes: ['char'],

        resetOnAnyFieldChange: true,

        init: function(parent, state, params) {
            this._super.apply(this, arguments);
            this.state = {};
        },

        _render: function() {
            var self = this;
            this.$el.empty()
            var rec = self.recordData;
            var ks_rgba_font_color;
            if (rec.ks_dashboard_item_type === 'ks_to_do') {
                    self.ksRenderToDoView(rec);
                }
        },

          _ks_get_rgba_format: function(val) {
            var rgba = val.split(',')[0].match(/[A-Za-z0-9]{2}/g);
            rgba = rgba.map(function(v) {
                return parseInt(v, 16)
            }).join(",");
            return "rgba(" + rgba + "," + val.split(',')[1] + ")";
        },

        ksRenderToDoView: function(rec) {
            var self = this;
            var ks_header_color = self._ks_get_rgba_format(rec.ks_header_bg_color);
            var ks_font_color = self._ks_get_rgba_format(rec.ks_font_color);
            var ks_rgba_button_color = self._ks_get_rgba_format(rec.ks_button_color);
             var list_to_do_data = {}
                   if (rec.ks_to_do_data){
                        list_to_do_data = JSON.parse(rec.ks_to_do_data)
                   }
            var $todoViewContainer = $(QWeb.render('ks_to_do_container', {

                ks_to_do_view_name: rec.name ? rec.name : 'Name',
                to_do_view_data: list_to_do_data,
            }));
            $todoViewContainer.find('.ks_card_header').addClass('ks_bg_to_color').css({"background-color": ks_header_color });
            $todoViewContainer.find('.ks_card_header').addClass('ks_bg_to_color').css({"color": ks_font_color + ' !important' });
            $todoViewContainer.find('.ks_li_tab').addClass('ks_bg_to_color').css({"color": ks_font_color + ' !important' });
            $todoViewContainer.find('.ks_chart_heading').addClass('ks_bg_to_color').css({"color": ks_font_color + ' !important' });
            this.$el.append($todoViewContainer);
        },


    });
    registry.add('ks_dashboard_to_do_preview', KsToDOViewPreview);

    return {
        KsToDOViewPreview: KsToDOViewPreview,
    };

});