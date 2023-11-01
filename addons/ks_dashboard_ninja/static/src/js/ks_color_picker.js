odoo.define('ks_dashboard_ninja_list.ks_color_picker', function(require) {
    "use strict";

    require('web.dom_ready');

    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');

    var QWeb = core.qweb;

    //Widget for color picker being used in dashboard item create view.
    //TODO : This color picker functionality can be improved a lot.
    var KsColorPicker = AbstractField.extend({

        supportedFieldTypes: ['char'],

        events: _.extend({}, AbstractField.prototype.events, {
            'change.spectrum .ks_color_picker': '_ksOnColorChange',
            'change .ks_color_opacity': '_ksOnOpacityChange',
            'input .ks_color_opacity': '_ksOnOpacityInput'
        }),

        jsLibs: [
            '/ks_dashboard_ninja/static/lib/js/spectrum.js'
        ],
        cssLibs: [
            '/ks_dashboard_ninja/static/lib/css/spectrum.css',
        ],

        _render: function() {
            this.$el.empty();
            var ks_color_value = '#376CAE';
            var ks_color_opacity = '0.99';
            if (this.value) {
                ks_color_value = this.value.split(',')[0];
                ks_color_opacity = this.value.split(',')[1];
            };
            var $view = $(QWeb.render('ks_color_picker_opacity_view', {
                ks_color_value: ks_color_value,
                ks_color_opacity: ks_color_opacity
            }));

            this.$el.append($view)

            this.$el.find(".ks_color_picker").spectrum({
                color: ks_color_value,
                showInput: true,
                hideAfterPaletteSelect: true,

                clickoutFiresChange: true,
                showInitial: true,
                preferredFormat: "rgb",
            });

            if (this.mode === 'readonly') {
                this.$el.find('.ks_color_picker').addClass('ks_not_click');
                this.$el.find('.ks_color_opacity').addClass('ks_not_click');
                this.$el.find('.ks_color_picker').spectrum("disable");
            } else {
                this.$el.find('.ks_color_picker').spectrum("enable");
            }
        },



        _ksOnColorChange: function(e, tinycolor) {
            this._setValue(tinycolor.toHexString().concat("," + this.value.split(',')[1]));
        },

        _ksOnOpacityChange: function(event) {
            this._setValue(this.value.split(',')[0].concat("," + event.currentTarget.value));
        },

        _ksOnOpacityInput: function(event) {
            var self = this;
            var color;
            if (self.name == "ks_background_color") {
                color = $('.ks_db_item_preview_color_picker').css("background-color")
                $('.ks_db_item_preview_color_picker').css("background-color", self.get_color_opacity_value(color, event.currentTarget.value))

                color = $('.ks_db_item_preview_l2').css("background-color")
                $('.ks_db_item_preview_l2').css("background-color", self.get_color_opacity_value(color, event.currentTarget.value))

            } else if (self.name == "ks_default_icon_color") {
                color = $('.ks_dashboard_icon_color_picker > span').css('color')
                $('.ks_dashboard_icon_color_picker > span').css('color', self.get_color_opacity_value(color, event.currentTarget.value))
            } else if (self.name == "ks_font_color") {
                color = $('.ks_db_item_preview').css("color")
                color = $('.ks_db_item_preview').css("color", self.get_color_opacity_value(color, event.currentTarget.value))
            }
        },

        get_color_opacity_value: function(color, val) {
            if (color) {
                return color.replace(color.split(',')[3], val + ")");
            } else {
                return false;
            }
        },


    });
    registry.add('ks_color_dashboard_picker', KsColorPicker);

    return {
        KsColorPicker: KsColorPicker
    };

});