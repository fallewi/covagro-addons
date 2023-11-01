odoo.define('ks_dashboard_ninja_list.ks_image_basic_widget', function(require) {
    "use strict";

    var core = require('web.core');
    var basic_fields = require('web.basic_fields');
    var core = require('web.core');
    var registry = require('web.field_registry');

    var QWeb = core.qweb;

    var KsImageWidget = basic_fields.FieldBinaryImage.extend({

        init: function(parent, state, params) {
            this._super.apply(this, arguments);
            this.ksSelectedIcon = false;
            this.ks_icon_set = ['home', 'puzzle-piece', 'clock-o', 'comments-o', 'car', 'calendar', 'calendar-times-o', 'bar-chart', 'commenting-o', 'star-half-o', 'address-book-o', 'tachometer', 'search', 'money', 'line-chart', 'area-chart', 'pie-chart', 'check-square-o', 'users', 'shopping-cart', 'truck', 'user-circle-o', 'user-plus', 'sun-o', 'paper-plane', 'rss', 'gears', 'check', 'book'];
        },

        template: 'KsFieldBinaryImage',

        events: _.extend({}, basic_fields.FieldBinaryImage.prototype.events, {
            'click .ks_icon_container_list': 'ks_icon_container_list',
            'click .ks_image_widget_icon_container': 'ks_image_widget_icon_container',
            'click .ks_icon_container_open_button': 'ks_icon_container_open_button',
            'click .ks_fa_icon_search': 'ks_fa_icon_search',
            'keyup .ks_modal_icon_input': 'ks_modal_icon_input_enter',
        }),

        _render: function() {
            var ks_self = this;
            var url = this.placeholder;
            if (ks_self.value) {
                ks_self.$('> img').remove();
                ks_self.$('> span').remove();
                $('<span>').addClass('fa fa-' + ks_self.recordData.ks_default_icon + ' fa-5x').appendTo(ks_self.$el).css('color', 'black');
            } else {
                var $img = $(QWeb.render("FieldBinaryImage-img", {
                    widget: this,
                    url: url
                }));
                ks_self.$('> img').remove();
                ks_self.$('> span').remove();
                ks_self.$el.prepend($img);
            }

            var $ks_icon_container_modal = $(QWeb.render('ks_icon_container_modal_template', {
                ks_fa_icons_set: ks_self.ks_icon_set
            }));

            $ks_icon_container_modal.prependTo(ks_self.$el);
        },

        //This will show modal box on clicking on open icon button.
        ks_image_widget_icon_container: function(e) {
            $('#ks_icon_container_modal_id').modal({
                show: true,
            });

        },


        ks_icon_container_list: function(e) {
            var self = this;
            self.ksSelectedIcon = $(e.currentTarget).find('span').attr('id').split('.')[1]
            _.each($('.ks_icon_container_list'), function(selected_icon) {
                $(selected_icon).removeClass('ks_icon_selected');
            });

            $(e.currentTarget).addClass('ks_icon_selected')
            $('.ks_icon_container_open_button').show()
        },

        //Imp :  Hardcoded for svg file only. If different file, change this code to dynamic.
        ks_icon_container_open_button: function(e) {
            var ks_self = this;
            ks_self._setValue(ks_self.ksSelectedIcon);
        },

        ks_fa_icon_search: function(e) {
            var self = this
            self.$el.find('.ks_fa_search_icon').remove()
            var ks_fa_icon_name = self.$el.find('.ks_modal_icon_input')[0].value
            if (ks_fa_icon_name.slice(0, 3) === "fa-") {
                ks_fa_icon_name = ks_fa_icon_name.slice(3)
            }
            var ks_fa_icon_render = $('<div>').addClass('ks_icon_container_list ks_fa_search_icon')
            $('<span>').attr('id', 'ks.' + ks_fa_icon_name.toLocaleLowerCase()).addClass("fa fa-" + ks_fa_icon_name.toLocaleLowerCase() + " fa-4x").appendTo($(ks_fa_icon_render))
            $(ks_fa_icon_render).appendTo(self.$el.find('.ks_icon_container_grid_view'))
        },

        ks_modal_icon_input_enter: function(e) {
            var ks_self = this
            if (e.keyCode == 13) {
                ks_self.$el.find('.ks_fa_icon_search').click()
            }
        },
    });

    registry.add('ks_image_widget', KsImageWidget);

    return {
        KsImageWidget: KsImageWidget,
    };
});