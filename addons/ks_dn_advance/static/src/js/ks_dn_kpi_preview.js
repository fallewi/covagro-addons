odoo.define('ks_dashboard_tv_ninja.ks_kpi_view_preview', function(require){

    var KsKpiPreview = require('ks_dashboard_ninja_list.ks_dashboard_kpi_preview');
    var viewRegistry = require('web.view_registry');
    var field_utils = require('web.field_utils');
    var session = require('web.session');
    var utils = require('web.utils');
    var KsGlobalFunction = require('ks_dashboard_ninja.KsGlobalFunction');
    var core = require('web.core');
    var Qweb = core.qweb;

    KsKpiPreview.KsKpiPreview.include({

        _render: function(){
            this.$el.empty();
            var rec =  this.recordData;
            if (rec.ks_dashboard_item_type === 'ks_kpi') {
                if(rec.ks_data_calculation_type === "custom"){
                    this._super.apply(this, arguments);
                } else {
                    var kpi_data = JSON.parse(rec.ks_kpi_data)
                    if (kpi_data){
                        this.KsRenderKpi();
                    }else{
                        this.$el.append($('<div>').text("Please run the appropriate Query"));
                    }
                }
            }
        },

        KsRenderKpi: function(){
            var self = this;
            var field = this.recordData;
            var kpi_data = JSON.parse(field.ks_kpi_data);
            var count_1 = kpi_data[0].record_data ? kpi_data[0].record_data:0;
            var count_2 = kpi_data[1] ? kpi_data[1].record_data : undefined;
            var target_1 = kpi_data[0].target;
            var target_view = field.ks_target_view,
                pre_view = field.ks_prev_view;
            var ks_rgba_background_color = self._get_rgba_format(field.ks_background_color);
            var ks_rgba_font_color = self._get_rgba_format(field.ks_font_color);
            var ks_rgba_icon_color = self._get_rgba_format(field.ks_default_icon_color);
            var acheive = false;
            var pre_acheive = false;
            var pre_deviation = false;
            if(isNaN(kpi_data[0]['record_data'])){
                var count_value = kpi_data[0]['record_data']
            }else
            {
                var count_value = KsGlobalFunction._onKsGlobalFormatter(kpi_data[0]['record_data'], field.ks_data_format, field.ks_precision_digits);
            }
            var item_info = {
                count_1: count_value,
                count_1_tooltip: kpi_data[0]['record_data'],
                count_2: kpi_data[1] ? String(kpi_data[1]['record_data']) : false,
                name: field.name ? field.name : "Name",
                target_progress_deviation:false,
                icon_select: field.ks_icon_select,
                default_icon: field.ks_default_icon,
                icon_color: ks_rgba_icon_color,
                target_deviation: false,
                target_arrow: acheive ? 'up' : 'down',
                ks_enable_goal: field.ks_goal_enable,
                ks_previous_period: false,
                target: self.ksNumFormatter(target_1, 1),
                previous_period_data: false,
                pre_deviation: pre_deviation,
                pre_arrow: pre_acheive ? 'up' : 'down',
                target_view: field.ks_target_view,
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

            var $kpi_preview;
            if (!kpi_data[1]) {
                if (target_view === "Number" || !field.ks_goal_enable) {
                    $kpi_preview = $(Qweb.render("ks_kpi_preview_template", item_info));
                } else if (target_view === "Progress Bar" && field.ks_goal_enable) {
                    $kpi_preview = $(Qweb.render("ks_kpi_preview_template_3", item_info));
                    $kpi_preview.find('#ks_progressbar').val(parseInt(item_info.target_progress_deviation));
                }


                if ($kpi_preview.find('.row').children().length !== 2) {
                    $kpi_preview.find('.row').children().addClass('text-center');
                }
            }
            $kpi_preview.css({
                "background-color": ks_rgba_background_color,
                "color": ks_rgba_font_color,
            });
            this.$el.append($kpi_preview);
        },

    });

    return KsKpiPreview;
});