odoo.define('ks_dn_advance.ks_tv_website_dashboard', function(require){

    var KsDashboardNinjaWebsite =  require('ks_website_dashboard_ninja.ks_website_dashboard');
    var core = require('web.core');
    var QWeb = core.qweb;
    var ajax = require('web.ajax');
    var _t = core._t;
    var config = require('web.config');

    ajax.loadXML('/ks_dn_advance/static/src/xml/ks_dashboard_tv_ninja.xml', QWeb);
    ajax.loadXML('/ks_dn_advance/static/src/xml/ks_query_templates.xml', QWeb);
    if (KsDashboardNinjaWebsite){
        KsDashboardNinjaWebsite.include({

         _renderListView: function (item, grid) {
            var ks_self = this;
            var list_view_data = JSON.parse(item.ks_list_view_data);
            var item_id = item.id,
                pager = true,
                data_rows = list_view_data.data_rows,
                length  = data_rows ? data_rows.length : 0,
                item_title = item.name;
            if(item.ks_data_calculation_type && item.ks_data_calculation_type === 'query'){
                pager = true;
            }
            var $ksItemContainer = ks_self._renderListViewData(item)

            var $ks_gridstack_container = $(QWeb.render('ks_gridstack_list_view_container', {
                ks_chart_title: item_title,
                ksIsDashboardManager: ks_self.config.ks_dashboard_manager,
                ks_dashboard_list: ks_self.config.ks_dashboard_list,
                item_id : item_id,
                count: '1-' + length,
                offset: 1,
                intial_count: length,
                ks_pager: pager,
                calculation_type: item.ks_data_calculation_type,
            })).addClass('ks_dashboarditem_id');
             if (item.ks_pagination_limit < length  ) {
                $ks_gridstack_container.find('.ks_load_next').addClass('ks_event_offer_list');
            }
            if (length < item.ks_pagination_limit ) {
                $ks_gridstack_container.find('.ks_load_next').addClass('ks_event_offer_list');
            }
            if (item.ks_record_data_limit === item.ks_pagination_limit){
                   $ks_gridstack_container.find('.ks_load_next').addClass('ks_event_offer_list');
            }
            if (length == 0){
                $ks_gridstack_container.find('.ks_pager').addClass('d-none');
            }
           if (item.ks_pagination_limit == 0){
                $ks_gridstack_container.find('.ks_pager_name').addClass('d-none');
           }
            $ks_gridstack_container.find('.card-body').append($ksItemContainer);
            item.$el = $ks_gridstack_container;
            if (item_id in ks_self.gridstackConfig) {
                if (config.device.isMobile){
                    grid.addWidget($ks_gridstack_container[0], {x:ks_self.gridstackConfig[item_id].x, y:ks_self.gridstackConfig[item_id].y, w:ks_self.gridstackConfig[item_id].w, h:ks_self.gridstackConfig[item_id].h, autoPosition:true, minW:3, maxW:null, minH:3, maxH:null, id:item_id});
                }
                else{
                    grid.addWidget($ks_gridstack_container[0], {x:ks_self.gridstackConfig[item_id].x, y:ks_self.gridstackConfig[item_id].y, w:ks_self.gridstackConfig[item_id].w, h:ks_self.gridstackConfig[item_id].h, autoPosition:false, minW:3, maxW:null, minH:3, maxH:null, id:item_id});
                }
            } else {
                grid.addWidget($ks_gridstack_container[0], {x:0, y:0, w:5, h:4, autoPosition:true, minW:3, maxW:null, minH:3, maxH:null, id:item_id});
            }
        },

        _renderListViewData: function(item){
            var ks_self = this;
            var list_view_data = JSON.parse(item.ks_list_view_data);
            var item_id = item.id,
                data_rows = list_view_data.data_rows,
                item_title = item.name;
            if(item.ks_list_view_type === "ungrouped" && list_view_data){
                if(list_view_data.date_index){
                    var index_data = list_view_data.date_index;
                    for (var i = 0; i < index_data.length; i++){
                        for (var j = 0; j < list_view_data.data_rows.length; j++){
                            var index = index_data[i]
                            var date = list_view_data.data_rows[j]["data"][index]
                             if (date) {
                                if (list_view_data.fields_type[index] === 'date'){
                                    list_view_data.data_rows[j]["data"][index] = moment(new Date(date)).format(this.date_format) , {}, {timezone: false};
                                }else{
                                    list_view_data.data_rows[j]["data"][index] = moment(new Date(date+" UTC")).format(this.datetime_format), {}, {timezone: false};
                                }
                            }else{
                                list_view_data.data_rows[j]["data"][index] = "";
                            }
                        }
                    }
                }
            }
            if(list_view_data){
                for (var i = 0; i < list_view_data.data_rows.length; i++){
                    for (var j = 0; j < list_view_data.data_rows[0]["data"].length; j++){
                        if(typeof(data_rows[i].data[j]) === "number" || list_view_data.data_rows[i].data[j]){
                            if (typeof(list_view_data.data_rows[i].data[j]) === "number"){
                                list_view_data.data_rows[i].data[j]  = ks_self.ksFormatValue(data_rows[i].data[j], 'float',item.ks_precision_digits);
                        }
                        }else {
                            list_view_data.data_rows[i].data[j] = "";
                        }
                    }
                }
            }
            var template;
            switch(item.ks_list_view_layout){
                case 'layout_1':
                    template = 'ks_list_view_table';
                    break;
                case 'layout_2':
                    template = 'ks_list_view_layout_2';
                    break;
                case 'layout_3':
                    template = 'ks_list_view_layout_3';
                    break;
                case 'layout_4':
                    template = 'ks_list_view_layout_4';
                    break;
                default :
                    template = 'ks_list_view_table';
                    break;
            }

            ks_data_calculation_type = ks_self.config.ks_item_data[item_id].ks_data_calculation_type
          var $ksItemContainer = $(QWeb.render(template, {
                list_view_data: list_view_data,
                item_id: item_id,
                list_type: item.ks_list_view_type,
                calculation_type: ks_data_calculation_type,
                isDrill: ks_self.config.ks_item_data[item_id]['isDrill']
            }));
            $ksItemContainer.find('.ks_sort_icon').addClass('d-none')
            if (list_view_data){
                var $ksitemBody = this.ksListViewBody(list_view_data,item_id)
                $ksItemContainer.find('.ks_table_body').append($ksitemBody)
            }
           if (item.ks_list_view_type === "ungrouped" && item.ks_data_calculation_type === 'custom') {
                $ksItemContainer.find('.ks_list_canvas_click').removeClass('ks_list_canvas_click');
            }


           $ksItemContainer.find('#ks_item_info').hide();

            return $ksItemContainer
        },

    });
    }
    return KsDashboardNinjaWebsite
});
