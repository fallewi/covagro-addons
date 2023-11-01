odoo.define('ks_dashboard_ninja_list.ks_dashboard_item_preview', function(require) {
    "use strict";

    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var field_utils = require('web.field_utils');
    var session = require('web.session');
    var utils = require('web.utils');

    var QWeb = core.qweb;

    var KsItemPreview = AbstractField.extend({

        supportedFieldTypes: ['integer'],
        resetOnAnyFieldChange: true,

        file_type_magic_word: {
            '/': 'jpg',
            'R': 'gif',
            'i': 'png',
            'P': 'svg+xml',
        },

        //        Number Formatter into shorthand function
        ksNumFormatter: function(num, digits) {
            var negative;
            var si = [{
                    value: 1,
                    symbol: ""
                },
                {
                    value: 1E3,
                    symbol: "k"
                },
                {
                    value: 1E6,
                    symbol: "M"
                },
                {
                    value: 1E9,
                    symbol: "G"
                },
                {
                    value: 1E12,
                    symbol: "T"
                },
                {
                    value: 1E15,
                    symbol: "P"
                },
                {
                    value: 1E18,
                    symbol: "E"
                }
            ];
            if (num < 0) {
                num = Math.abs(num)
                negative = true
            }
            var rx = /\.0+$|(\.[0-9]*[1-9])0+$/;
            var i;
            for (i = si.length-1; i > 0; i--) {
                if (num >= si[i].value) {
                    break;
                }
            }
            if (negative) {
                return "-" + (num / si[i].value).toFixed(digits).replace(rx, "$1") + si[i].symbol;
            } else {
                return (num / si[i].value).toFixed(digits).replace(rx, "$1") + si[i].symbol;
            }
        },

        ksNumColombianFormatter: function(num, digits, ks_precision_digits) {
            var negative;
            var si = [{
                    value: 1,
                    symbol: ""
                },
                {
                    value: 1E3,
                    symbol: ""
                },
                {
                    value: 1E6,
                    symbol: "M"
                },
                {
                    value: 1E9,
                    symbol: "M"
                },
                {
                    value: 1E12,
                    symbol: "M"
                },
                {
                    value: 1E15,
                    symbol: "M"
                },
                {
                    value: 1E18,
                    symbol: "M"
                }
            ];
            if (num < 0) {
                num = Math.abs(num)
                negative = true
            }
            var rx = /\.0+$|(\.[0-9]*[1-9])0+$/;
            var i;
            for (i = si.length-1; i > 0; i--) {
                if (num >= si[i].value) {
                    break;
                }
            }

            if (si[i].symbol === 'M'){
//                si[i].value = 1000000;
                num = parseInt(num) / 1000000
                num = field_utils.format.integer(num, Float64Array)
                if (negative) {
                    return "-" + num + si[i].symbol;
                } else {
                    return num + si[i].symbol;
                }
                }else{
                    if (num % 1===0){
                    num = field_utils.format.integer(num, Float64Array)
                    }else{
                        num = field_utils.format.float(num, Float64Array, {digits: [0,ks_precision_digits]});
                    }
                    if (negative) {
                        return "-" + num;
                    } else {
                        return num;
                    }
                }

        },

//        Indian format shorthand function
        ksNumIndianFormatter: function(num, digits) {
            var negative;
            var si = [{
                value: 1,
                symbol: ""
            },
            {
                value: 1E3,
                symbol: "Th"
            },
            {
                value: 1E5,
                symbol: "Lakh"
            },
            {
                value: 1E7,
                symbol: "Cr"
            },
            {
                value: 1E9,
                symbol: 'Arab'
            }
            ];
            if (num < 0) {
                num = Math.abs(num)
                negative = true
            }
            var rx = /\.0+$|(\.[0-9]*[1-9])0+$/;
            var i;
            for (i = si.length-1; i > 0; i--) {
                if (num >= si[i].value) {
                    break;
                }
            }
            if (negative) {
                return "-" + (num / si[i].value).toFixed(digits).replace(rx, "$1") + si[i].symbol;
            } else {
                return (num / si[i].value).toFixed(digits).replace(rx, "$1") + si[i].symbol;
            }

        },

        ks_get_dark_color: function(color, opacity, percent) { // deprecated. See below.
            var num = parseInt(color.slice(1), 16),
                amt = Math.round(2.55 * percent),
                R = (num >> 16) + amt,
                G = (num >> 8 & 0x00FF) + amt,
                B = (num & 0x0000FF) + amt;
            return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 + (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 + (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1) + "," + opacity;
        },

        _render: function() {
            var self = this;
            var field = self.recordData;
            var $val;
            var item_info;
            var ks_rgba_background_color, ks_rgba_font_color, ks_rgba_icon_color;
            self.$el.empty();
            ks_rgba_background_color = self._get_rgba_format(field.ks_background_color)
            ks_rgba_font_color = self._get_rgba_format(field.ks_font_color)
            ks_rgba_icon_color = self._get_rgba_format(field.ks_default_icon_color)
            item_info = {
                name: field.name,
                //                    count: self.record.specialData.ks_domain.nbRecords.toLocaleString('en', {useGrouping:true}),
                count: self.ksNumFormatter(field.ks_record_count, 1),
                icon_select: field.ks_icon_select,
                default_icon: field.ks_default_icon,
                icon_color: ks_rgba_icon_color,
                count_tooltip: field_utils.format.float(field.ks_record_count, Float64Array, {digits: [0, field.ks_precision_digits]}),
            }

            if (field.ks_icon) {

                if (!utils.is_bin_size(field.ks_icon)) {
                    // Use magic-word technique for detecting image type
                    item_info['img_src'] = 'data:image/' + (self.file_type_magic_word[field.ks_icon[0]] || 'png') + ';base64,' + field.ks_icon;
                } else {
                    item_info['img_src'] = session.url('/web/image', {
                        model: self.model,
                        id: JSON.stringify(self.res_id),
                        field: "ks_icon",
                        // unique forces a reload of the image when the record has been updated
                        unique: field_utils.format.datetime(self.recordData.__last_update).replace(/[^0-9]/g, ''),
                    });
                }

            }
            if (!field.name) {
                if (field.ks_model_name) {
                    item_info['name'] = field.ks_model_id.data.display_name;
                } else {
                    item_info['name'] = "Name";
                }
            }

            if (field.ks_multiplier_active){
                var ks_record_count = field.ks_record_count * field.ks_multiplier
                item_info['count'] = self._onKsGlobalFormatter(ks_record_count, field.ks_data_format, field.ks_precision_digits);
                item_info['count_tooltip'] = ks_record_count;
            }else{
                item_info['count'] = self._onKsGlobalFormatter(field.ks_record_count, field.ks_data_format, field.ks_precision_digits);
            }

//            count_tooltip

            switch (field.ks_layout) {
                case 'layout1':
                    $val = $(QWeb.render('ks_db_list_preview_layout1', item_info));
                    $val.css({
                        "background-color": ks_rgba_background_color,
                        "color": ks_rgba_font_color
                    });
                    break;

                case 'layout2':
                    $val = $(QWeb.render('ks_db_list_preview_layout2', item_info));
                    var ks_rgba_dark_background_color_l2 = self._get_rgba_format(self.ks_get_dark_color(field.ks_background_color.split(',')[0], field.ks_background_color.split(',')[1], -10));
                    $val.find('.ks_dashboard_icon_l2').css({
                        "background-color": ks_rgba_dark_background_color_l2,
                    });
                    $val.css({
                        "background-color": ks_rgba_background_color,
                        "color": ks_rgba_font_color
                    });
                    break;

                case 'layout3':
                    $val = $(QWeb.render('ks_db_list_preview_layout3', item_info));
                    $val.css({
                        "background-color": ks_rgba_background_color,
                        "color": ks_rgba_font_color
                    });
                    break;

                case 'layout4':
                    $val = $(QWeb.render('ks_db_list_preview_layout4', item_info));
                    $val.find('.ks_dashboard_icon_l4').css({
                        "background-color": ks_rgba_background_color,
                    });
                    $val.find('.ks_dashboard_item_preview_customize').css({
                        "color": ks_rgba_background_color,
                    });
                    $val.find('.ks_dashboard_item_preview_delete').css({
                        "color": ks_rgba_background_color,
                    });
                    $val.css({
                        "border-color": ks_rgba_background_color,
                        "color": ks_rgba_font_color
                    });
                    break;

                case 'layout5':
                    $val = $(QWeb.render('ks_db_list_preview_layout5', item_info));
                    $val.css({
                        "background-color": ks_rgba_background_color,
                        "color": ks_rgba_font_color
                    });
                    break;

                case 'layout6':
                    //                        item_info['icon_color'] = self._get_rgba_format(self.ks_get_dark_color(field.ks_background_color.split(',')[0],field.ks_background_color.split(',')[1],-10));
                    $val = $(QWeb.render('ks_db_list_preview_layout6', item_info));
                    $val.css({
                        "background-color": ks_rgba_background_color,
                        "color": ks_rgba_font_color
                    });

                    break;

                default:
                    $val = $(QWeb.render('ks_db_list_preview'));
                    break;

            }

            self.$el.append($val);
            self.$el.append(QWeb.render('ks_db_item_preview_footer_note'));
        },

        _onKsGlobalFormatter: function(ks_record_count, ks_data_format, ks_precision_digits){
            var self = this;
            if (ks_data_format == 'exact'){
//                return ks_record_count;
                return field_utils.format.float(ks_record_count, Float64Array, {digits: [0, ks_precision_digits]});
            }else{
                if (ks_data_format == 'indian'){
                    return self.ksNumIndianFormatter( ks_record_count, 1);
                }else if (ks_data_format == 'colombian'){
                    return self.ksNumColombianFormatter( ks_record_count, 1, ks_precision_digits);
                }else{
                    return self.ksNumFormatter(ks_record_count, 1);
                }
            }
        },

        _renderReadonly: function($val) {
            var self = this;
            var ks_icon_url;
            this._rpc({
                model: 'ks_dashboard_ninja.item',
                method: 'ks_set_preview_image',
                args: [self.res_id],
            }).then(function(data) {
                ks_icon_url = 'data:image/' + (self.file_type_magic_word[data[0]] || 'png') + ';base64,' + data;
                $val.find('.ks_db_list_image').attr('src', ks_icon_url)
                self.$el.append($val)
            });
        },


        _get_rgba_format: function(val) {
            var rgba = val.split(',')[0].match(/[A-Za-z0-9]{2}/g);
            rgba = rgba.map(function(v) {
                return parseInt(v, 16)
            }).join(",");
            return "rgba(" + rgba + "," + val.split(',')[1] + ")";
        }


    });
    registry.add('ks_dashboard_item_preview', KsItemPreview);

    return {
        KsItemPreview: KsItemPreview
    };

});