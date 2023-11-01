odoo.define('ks_dn_advance.ks_tv_dashboard', function(require){

    var KsDashboardNinja = require('ks_dashboard_ninja.ks_dashboard');
    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;
    var field_utils = require('web.field_utils');
    var config = require('web.config');
    var KsGlobalFunction = require('ks_dashboard_ninja.KsGlobalFunction');
    const session = require('web.session');

    KsDashboardNinja.include({

           jsLibs: [
            '/ks_dashboard_ninja/static/lib/js/Chart.bundle.min.js',
            '/ks_dashboard_ninja/static/lib/js/gridstack-h5.js',
            '/ks_dashboard_ninja/static/lib/js/chartjs-plugin-datalabels.js',
            '/ks_dashboard_ninja/static/lib/js/pdfmake.min.js',
            '/ks_dashboard_ninja/static/lib/js/vfs_fonts.js',
            'ks_dn_advance/static/lib/js/print.min.js',
            'ks_dn_advance/static/lib/js/pdf.min.js',

        ],

        events : _.extend(KsDashboardNinja.prototype.events, {
            'click .ks_start_tv_dashboard': 'startTvDashboard',
            'click .ks_stop_tv_dashboard': 'ksStopTvDashboard',
            'click .ks_dn_asc': '_ksSortAscOrder',
            'click .ks_dn_desc': '_ksSortDescOrder',
            'click .ks_dashboard_print_pdf' : 'ks_dash_print',
            'click .ks_dashboard_send_email' : 'ks_send_mail',

        }),

        ks_dash_print : function(id){
            var self = this;
            var ks_dashboard_name = self.ks_dashboard_data.name
            setTimeout(function () {


            window.scrollTo(0, 0);
            html2canvas(document.querySelector('.ks_dashboard_item_content'), {useCORS: true, allowTaint: false}).then(function(canvas){
            window.jsPDF = window.jspdf.jsPDF;
            var pdf = new jsPDF("p", "mm", "a4");
            var ks_img = canvas.toDataURL("image/jpeg", 0.90);
            var ks_props= pdf.getImageProperties(ks_img);
            var KspageHeight = 300;
            var KspageWidth = pdf.internal.pageSize.getWidth();
            var ksheight = (ks_props.height * KspageWidth) / ks_props.width;
            var ksheightLeft = ksheight;
            var position = 0;

            pdf.addImage(ks_img,'JPEG', 0, 0, KspageWidth, ksheight, 'FAST');
            ksheightLeft -= KspageHeight;
            while (ksheightLeft >= 0) {
                position = ksheightLeft - ksheight;
                pdf.addPage();
                pdf.addImage(ks_img, 'JPEG', 0, position,  KspageWidth, ksheight, 'FAST');
                ksheightLeft -= KspageHeight;
            };
            pdf.save(ks_dashboard_name + '.pdf');
        })
        },500);
        },

        ks_send_mail: function(ev) {
            var self = this;
            var ks_dashboard_name = self.ks_dashboard_data.name
            setTimeout(function () {
            $('.fa-envelope').addClass('d-none')
            $('.fa-spinner').removeClass('d-none');


            window.scrollTo(0, 0);
            html2canvas(document.querySelector('.ks_dashboard_item_content'), {useCORS: true, allowTaint: false}).then(function(canvas){
            window.jsPDF = window.jspdf.jsPDF;
            var pdf = new jsPDF("p", "mm", "a4");
            var ks_img = canvas.toDataURL("image/jpeg", 0.90);
            var ks_props= pdf.getImageProperties(ks_img);
            var KspageHeight = 300;
            var KspageWidth = pdf.internal.pageSize.getWidth();
            var ksheight = (ks_props.height * KspageWidth) / ks_props.width;
            var ksheightLeft = ksheight;
            var position = 0;

            pdf.addImage(ks_img,'JPEG', 0, 0, KspageWidth, ksheight, 'FAST');
            ksheightLeft -= KspageHeight;
            while (ksheightLeft >= 0) {
                position = ksheightLeft - ksheight;
                pdf.addPage();
                pdf.addImage(ks_img, 'JPEG', 0, position,  KspageWidth, ksheight, 'FAST');
                ksheightLeft -= KspageHeight;
            };
//            pdf.save(ks_dashboard_name + '.pdf');
            const file = pdf.output()
            const base64String = btoa(file)

//            localStorage.setItem(ks_dashboard_name + '.pdf',file);

            $.when(base64String).then(function(){
                self._rpc({
                    model: 'ks_dashboard_ninja.board',
                    method: 'ks_dashboard_send_mail',
                    args: [
                        [parseInt(self.ks_dashboard_id)],base64String

                    ]
                }).then(function(res){
                    $('.fa-envelope').removeClass('d-none')
                    $('.fa-spinner').addClass('d-none');
                    if (res['ks_is_send']){
                        var msg = res['ks_massage']
                            self.call('notification', 'notify', {
                                message: msg,
                                type: 'info',
                                title: "Success"
                            });
                    }else{
                        var msg = res['ks_massage']
                            self.call('notification', 'notify', {
                                message: msg,
                                type: 'info',
                                title: "Fail"
                            });
                    }
                });
             })
        })
        },500);

        },

       _ksRenderNoItemView: function() {
            $('.ks_dashboard_items_list').remove();
            var self = this;
            self.$el.find('.ks_dashboard_link').addClass("d-none");
            self.$el.find('.ks_dashboard_edit_layout').addClass("d-none");
            self.$el.find('.ks_dashboard_print_pdf').addClass("ks_hide_display");
            self.$el.find('.ks_start_tv_dashboard').addClass("ks_hide_display");
            $(QWeb.render('ksNoItemView')).appendTo(self.$el)

        },

         _ksSortAscOrder: function(e) {
            var self = this;
            var ks_value_offfset = $(e.currentTarget.parentElement.parentElement.parentElement.offsetParent).find('.ks_pager').find('.ks_counter').find('.ks_value').text();
            var offset = 0;
            var initial_count = 0;
            if (ks_value_offfset)
            {
                initial_count = parseInt(ks_value_offfset.split('-')[0])
                offset = parseInt(ks_value_offfset.split('-')[1])
            }

            var item_id = e.currentTarget.dataset.itemId;
            var field = e.currentTarget.dataset.fields;
            var context = self.getContext();
            var searchList = []
            var searchField = []
            var user_id = session.userContext.uid;
            var context = self.getContext();
            context.user_id = user_id;
            context.offset = offset;
            context.initial_count = initial_count;

            var store = e.currentTarget.dataset.store;
            context.field = field;
            context.sort_order = "ASC"
            var ks_domain = self.ksGetParamsForItemFetch(parseInt(item_id));
            if (store == "true") {
                self._rpc({
                    model: 'ks_dashboard_ninja.item',
                    method: 'ks_get_list_data_orderby_extend',
                    args: [
                        [parseInt(item_id)], ks_domain
                    ],
                    context: context,
                }).then(function(result) {
                    if (result) {
                        var list_view_data = result;
                        var $listBody = self._ksListViewBody(list_view_data, item_id);
                        $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".ks_table_body").empty();
                        $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".ks_table_body").append($listBody);
                        }
                }.bind(this));

                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".ks_sort_up[data-fields=" + field + "]").removeClass('ks_plus')
                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".ks_sort_down[data-fields=" + field + "]").addClass('ks_plus')
                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".list_header[data-fields=" + field + "]").removeClass('ks_dn_asc')
                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".list_header[data-fields=" + field + "]").addClass('ks_dn_desc')
            }
        },

        _ksSortDescOrder: function(e) {
            var self = this;
            var ks_value_offfset = $(e.currentTarget.parentElement.parentElement.parentElement.offsetParent).find('.ks_pager').find('.ks_counter').find('.ks_value').text();
            var offset = 0;
            var initial_count = 0;
            if (ks_value_offfset)
            {
                initial_count = parseInt(ks_value_offfset.split('-')[0])
                offset = parseInt(ks_value_offfset.split('-')[1])
            }
            var item_id = e.currentTarget.dataset.itemId;
            var field = e.currentTarget.dataset.fields;
            var context = self.getContext();
            var user_id = session.userContext.uid;
            var context = self.getContext();
            context.user_id = user_id;
            context.offset = offset;
            context.initial_count = initial_count;
            var store = e.currentTarget.dataset.store;
            context.field = field;
            context.sort_order = "DESC";
            var ks_domain = self.ksGetParamsForItemFetch(parseInt(item_id));
            if (store == "true") {
                self._rpc({
                    model: 'ks_dashboard_ninja.item',
                    method: 'ks_get_list_data_orderby_extend',
                    args: [
                        [parseInt(item_id)], ks_domain
                    ],
                    context: context,
                }).then(function(result) {
                    if (result){
                        var list_view_data = result;
                        var $listBody = self._ksListViewBody(list_view_data, item_id);
                        $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".ks_table_body").empty();
                        $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".ks_table_body").append($listBody);
                    }
                }.bind(this));
                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".ks_sort_down[data-fields=" + field + "]").removeClass('ks_plus')
                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".ks_sort_up[data-fields=" + field + "]").addClass('ks_plus')
                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".list_header[data-fields=" + field + "]").addClass('ks_dn_asc')
                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".list_header[data-fields=" + field + "]").removeClass('ks_dn_desc')
            }
        },
       _ksListViewBody: function(list_view_data, item_id) {
            var self = this;
            var itemid = item_id
            var  ks_data_calculation_type = self.ks_dashboard_data.ks_item_data[item_id].ks_data_calculation_type;
            var list_view_type = self.ks_dashboard_data.ks_item_data[item_id].ks_list_view_type
            if (list_view_type === "ungrouped" && list_view_data) {
                if (list_view_data.date_index) {
                    var index_data = list_view_data.date_index;
                    for (var i = 0; i < index_data.length; i++) {
                        for (var j = 0; j < list_view_data.data_rows.length; j++) {
                            var index = index_data[i]
                            var date = list_view_data.data_rows[j]["data"][index]
                            if (date){
                             if( list_view_data.fields_type[index] === 'date'){
                                    list_view_data.data_rows[j]["data"][index] = moment(new Date(date)).format(this.date_format) , {}, {timezone: false};
                             }else{
                                list_view_data.data_rows[j]["data"][index] = field_utils.format.datetime(moment(moment(date).utc(true)._d), {}, {
                                timezone: false
                            });
                            }

                             }else {
                                list_view_data.data_rows[j]["data"][index] = "";
                            }
                        }
                    }
                }
            }
            if (list_view_data) {
                for (var i = 0; i < list_view_data.data_rows.length; i++) {
                    for (var j = 0; j < list_view_data.data_rows[0]["data"].length; j++) {
                        if (typeof(list_view_data.data_rows[i].data[j]) === "number" || list_view_data.data_rows[i].data[j]) {
                            if (typeof(list_view_data.data_rows[i].data[j]) === "number") {
                                list_view_data.data_rows[i].data[j] = field_utils.format.float(list_view_data.data_rows[i].data[j], Float64Array)
                            }
                        } else {
                            list_view_data.data_rows[i].data[j] = "";
                        }
                    }
                }
            }
            var $ksitemBody = $(QWeb.render('ks_list_view_tmpl', {
                        list_view_data: list_view_data,
                        item_id: itemid,
                        calculation_type: ks_data_calculation_type,
                        isDrill: self.ks_dashboard_data.ks_item_data[item_id]['isDrill'],
                        list_type: list_view_type,
                    }));

           if (!self.ks_dashboard_data.ks_item_data[item_id].ks_show_records) {
                $ksitemBody.find('#ks_item_info').hide();
            }
            return $ksitemBody;
       },

        rendertvDashboard: function(){
            var self = this;
            this.$el.find('.ks_float_tv').remove();
            this.container_owl = $(QWeb.render('ks_owl_carssel'));

            var items = self.ksSortItems(self.ks_dashboard_data.ks_item_data);
            self.$el.find('.ks_dashboard_main_content').append(this.container_owl);
            this.container_owl = this.container_owl.find('.owl-carousel');
            self.ksRenderTvDashboardItems(items);
        },

        ksRenderTvDashboardItems: function(items){
            var self = this;
            this.ks_dashboard_manager = self.ks_dashboard_data.ks_dashboard_manager
            self.ks_dashboard_data.ks_dashboard_manager = false;
            this.tiles = [];
            this.kpi = [];
            for (var i = 0; i < items.length; i++) {
                if (items[i].ks_dashboard_item_type === 'ks_tile') {
                    this.tiles.push(items[i]);
                } else if (items[i].ks_dashboard_item_type === 'ks_list_view') {
                    var item_view = self.renderTvListView(items[i], self.grid);
                     this.container_owl.append(item_view);
                } else if (items[i].ks_dashboard_item_type === 'ks_kpi') {
                    this.kpi.push(items[i]);
                } else if (items[i].ks_dashboard_item_type === 'ks_to_do') {
                        var active_section_id = false
                    if ($(".grid-stack-item[gs-id=" + items[i].id + "]").find('.ks_card_header').find('.active').data()){
                        active_section_id = $(".grid-stack-item[gs-id=" + items[i].id + "]").find('.ks_card_header').find('.active').data().sectionId
                    }

                    var item_view = self.renderTvTodoView(items[i], active_section_id,self.grid);
                     this.container_owl.append(item_view);
                }else {
                    self._renderTvGraph(items[i], self.grid)
                }

            }
            self._renderTiles();
            self._renderKPi();
            self.ks_dashboard_data.ks_dashboard_manager = this.ks_dashboard_manager;
        },
        renderTvTodoView: function(item, active_section_id){
            var self = this;
            var item_title = item.name;
            var item_id = item.id;
            var list_to_do_data = JSON.parse(item.ks_to_do_data)
            var ks_header_color = self._ks_get_rgba_format(item.ks_header_bg_color);
            var ks_font_color = self._ks_get_rgba_format(item.ks_font_color);
            var ks_rgba_button_color = self._ks_get_rgba_format(item.ks_button_color);
            var $ksItemContainer = self.ksRenderToDoView(item, ks_tv_play=true);
            var $ks_gridstack_container = $(QWeb.render('ks_gridstack_todo_tv_view_container', {
                ks_chart_title: item_title,
                ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                item_id: item_id,
                to_do_view_data: list_to_do_data,
            })).addClass('ks_dashboarditem_id')

            $ks_gridstack_container.find('.ks_card_header').addClass('ks_bg_to_color').css({"background-color": ks_header_color });
            $ks_gridstack_container.find('.ks_card_header').addClass('ks_bg_to_color').css({"color": ks_font_color + ' !important' });
            $ks_gridstack_container.find('.ks_dna_li_tab').addClass('ks_bg_to_color').css({"color": ks_font_color + ' !important' });
            $ks_gridstack_container.find('.ks_list_view_heading').addClass('ks_bg_to_color').css({"color": ks_font_color + ' !important' });
            if (active_section_id){
                $ks_gridstack_container.find('.ks_card_header').find('.nav-link').removeClass('active')
                $ks_gridstack_container.find('.ks_card_header').find(".nav-link[data-section-id=" + active_section_id+ "]").addClass('active')
                $ksItemContainer.find('.ks_tab_section').removeClass('active');
                $ksItemContainer.find(".ks_tab_section[data-section-id=" + active_section_id+ "]").addClass('active');
                $ksItemContainer.find(".ks_tab_section[data-section-id=" + active_section_id+ "]").addClass('show');
            }
            $ks_gridstack_container.find('.ks_to_do_card_body').append($ksItemContainer)
            return $ks_gridstack_container;
        },

        _renderTiles: function(){
            var self = this;
            var count  =  Math.round(this.tiles.length/2)
            var $kscontainer = $('<div class="d-flex align-items-center justify-content-center flex-column h-100 ks_tv_item">')
            for(var i = 1; i<= count; i++){
                var ks_tiles = this.tiles.splice(0,2);
                var $container = $('<div class="d-flex align-items-center ks-tv-item">');
                for (var j = 0; j<ks_tiles.length; j++){
                    var item_data = ks_tiles[j];

                        var item_view = self._ksRenderDashboardTile(item_data);

                    $container.append(item_view);
                }
                $kscontainer.append($container)
                if (i%2 === 0){
                    this.container_owl.append($kscontainer);
                    $kscontainer = $('<div class="d-flex align-items-center justify-content-center flex-column h-100 ks_tv_item">');
                }
            }
            if($kscontainer[0].childElementCount){
                this.container_owl.append($kscontainer);
            }

        },

        _renderKPi: function(){
            var self = this;
            var count  =  Math.round(this.kpi.length/2);
            for(var i = 1; i<= count; i++){
                var $kscontainer = $('<div class="d-flex align-items-center justify-content-center h-100 ks_tv_item ks-tv-kpi">');
                var ks_tiles = this.kpi.splice(0,2)
                 for (var j = 0; j<ks_tiles.length; j++){
                    var item_data = ks_tiles[j];
                    var item_view = self.renderKpi(item_data);
                    $kscontainer.append(item_view);
                }
                this.container_owl.append($kscontainer);
            }
        },

         renderKpi: function(item, grid) {
            if (item.ks_data_calculation_type === 'custom'){
                return this._super.apply(this,arguments);
            }
            var self = this;
            var field = item;
            var kpi_data = JSON.parse(field.ks_kpi_data);
            item['ksIsDashboardManager'] = self.ks_dashboard_data.ks_dashboard_manager;
            item['ksIsUser'] = true;

            var ks_icon_url;
            if (field.ks_icon_select == "Custom") {
                if (field.ks_icon[0]) {
                    ks_icon_url = 'data:image/' + (self.file_type_magic_word[field.ks_icon[0]] || 'png') + ';base64,' + field.ks_icon;
                } else {
                    ks_icon_url = false;
                }
            }
            var count_1 = kpi_data[0].record_data ? kpi_data[0].record_data:0;
            var count_2 = kpi_data[1] ? kpi_data[1].record_data : undefined;
            var target_1 = kpi_data[0].target;
            var target_view = field.ks_target_view,
                pre_view = field.ks_prev_view;
            var ks_rgba_background_color = self._ks_get_rgba_format(field.ks_background_color);
            var ks_rgba_font_color = self._ks_get_rgba_format(field.ks_font_color);
            var ks_rgba_icon_color = self._ks_get_rgba_format(field.ks_default_icon_color);
            var ks_rgba_button_color = self._ks_get_rgba_format(field.ks_button_color);
            var acheive = false;
            var pre_acheive = false;
            var pre_deviation = false;
            if(isNaN(kpi_data[0]['record_data'])){
                var count_value = kpi_data[0]['record_data']
            }else
            {
                var count_value = KsGlobalFunction._onKsGlobalFormatter(kpi_data[0]['record_data'], field.ks_data_formatting, field.ks_precision_digits);
            }
            var item_info = {
                item: item,
                id: field.id,
                count_1: count_value,
                count_1_tooltip: kpi_data[0]['record_data'],
                count_2: kpi_data[1] ? String(kpi_data[1]['record_data']) : false,
                name: field.name ? field.name : field.ks_model_id.data.display_name,
                target_progress_deviation:false,
                icon_select: field.ks_icon_select,
                default_icon: field.ks_default_icon,
                icon_color: ks_rgba_icon_color,
                target_deviation: false,
                target_arrow: acheive ? 'up' : 'down',
                ks_enable_goal: field.ks_goal_enable,
                ks_previous_period: false,
                target: KsGlobalFunction.ksNumFormatter(target_1, 1),
                previous_period_data: false,
                pre_deviation: false,
                pre_arrow: false ? 'up' : 'down',
                target_view: field.ks_target_view,
                pre_view: field.ks_prev_view,
                ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                ks_icon_url: ks_icon_url,
                ks_rgba_button_color:ks_rgba_button_color,

            }
            var $kpi_preview;
            if (!kpi_data[1]) {
                if (field.ks_target_view === "Number" || !field.ks_goal_enable) {
                    $kpi_preview = $(QWeb.render("ks_kpi_template", item_info));
                } else if (field.ks_target_view === "Progress Bar" && field.ks_goal_enable) {
                    $kpi_preview = $(QWeb.render("ks_kpi_template_3", item_info));
                    $kpi_preview.find('#ks_progressbar').val(parseInt(item_info.target_progress_deviation));

                }

               if ($kpi_preview.find('.ks_target_previous').children().length !== 2) {
                $kpi_preview.find('.ks_target_previous').addClass('justify-content-center');
                }
            }
            $kpi_preview.find('.ks_dashboarditem_id').css({
                "background-color": ks_rgba_background_color,
                "color": ks_rgba_font_color,
            });
            return $kpi_preview
        },

        _onKsItemClick: function(e) {
            var self = this;
            //  To Handle only allow item to open when not clicking on item
            if (self.ksAllowItemClick) {

                e.preventDefault();
                if (e.target.title != "Customize Item") {
                    var item_id = parseInt(e.currentTarget.firstElementChild.id);
                    var item_data = self.ks_dashboard_data.ks_item_data[item_id];
                    if (item_data && item_data.ks_show_records && item_data.ks_data_calculation_type === 'custom') {

                        if (item_data.action) {
                            if (!item_data.ks_is_client_action){
                                var action = Object.assign({}, item_data.action);
                                if (action.view_mode.includes('tree')) action.view_mode = action.view_mode.replace('tree', 'list');
                                for (var i = 0; i < action.views.length; i++) action.views[i][1].includes('tree') ? action.views[i][1] = action.views[i][1].replace('tree', 'list') : action.views[i][1];
                                action['domain'] = item_data.ks_domain || [];
                                action['search_view_id'] = [action.search_view_id, 'search']
                            }else{
                                var action = Object.assign({}, item_data.action[0]);
                                if (action.params){
                                    action.params.default_active_id || 'mailbox_inbox';
                                    }else{
                                        action.params = {
                                        'default_active_id': 'mailbox_inbox'
                                        }
                                        action.context = {}
                                        action.context.params = {
                                        'active_model': false
                                        };
                                    }
                            }

                        } else {
                            var action = {
                                name: _t(item_data.name),
                                type: 'ir.actions.act_window',
                                res_model: item_data.ks_model_name,
                                domain: item_data.ks_domain || "[]",
                                views: [
                                    [false, 'list'],
                                    [false, 'form']
                                ],
                                view_mode: 'list',
                                target: 'current',
                            }
                        }
                        self.do_action(action, {
                            on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                        });
                    }
                }
            } else {
                self.ksAllowItemClick = true;
            }
        },

        _renderGraph: function(item){
            var self = this;
            this._super.apply(this, arguments);
            if (item.ks_data_calculation_type === 'query'){
                $(self.$el.find(".grid-stack-item[gs-id=" + item.id + "]").children()[0]).find(".ks_dashboard_item_chart_info").addClass('d-none');
            }
        },

        onChartCanvasClick: function(evt){
            var self = this;
            var item_id;
            if (evt.currentTarget.classList.value !== 'ks_list_canvas_click') {
                item_id = evt.currentTarget.dataset.chartId;
            } else {
                item_id = $(evt.target).parent().data().itemId;
            }
            var item_data = self.ks_dashboard_data.ks_item_data[item_id];

            if (item_data.ks_data_calculation_type === 'custom'){
                this._super.apply(this,arguments);
            }
        },

        startTvDashboard: function(e){
            this.rendertvDashboard();
            var self = this;
            var speed = self.ks_dashboard_data.ks_croessel_speed ? parseInt(self.ks_dashboard_data.ks_croessel_speed) : 5000
            $('.ks_float_tv').removeClass('d-none');

            $('.owl-carousel').owlCarousel({
                rtl: $('.o_rtl').length>0,
                loop:true,
                nav:true,
                dots:false,
                items : 1,
                margin:10,
                autoplay:true,
                autoplayTimeout:speed,
                responsiveClass: true,
                autoplayHoverPause: true,
                navText:['<i class="fa fa fa-angle-left"></i>','<i class="fa fa fa-angle-right"></i>'],
            });
            if (self.ks_dashboard_data.ks_dashboard_background_color != undefined){
                $('.owl-carousel').find('.ks_chart_container').each(function() {
                    var currentElement = $(this);
                    if (self.ks_dashboard_data.ks_dark_mode_enable == true){
                        currentElement.children().css({"backgroundColor": '#2a2a2a'});
                    }
                    else{
                        currentElement.children().css({"backgroundColor": self.ks_dashboard_data.ks_dashboard_background_color.split(',')[0]});
                    }
                });
            }
        },
        ksStopTvDashboard: function(e){
            $('.owl-carousel').owlCarousel('destroy');
             $('.ks_float_tv').addClass('d-none');

        },


        ksUpdateDashboardItem: function(ids) {
            var self = this;
            for (var i = 0; i < ids.length; i++) {

                var item_data = self.ks_dashboard_data.ks_item_data[ids[i]]
                if (item_data['ks_dashboard_item_type'] == 'ks_list_view') {
                    var item_view = self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]");
                    item_view.find('.card-body').empty();
                    var name = item_data.name ?item_data.name : item_data.ks_model_display_name;
                    item_view.children().find('.ks_list_view_heading').prop('title', name);
                    item_view.children().find('.ks_list_view_heading').text(name);
                    item_view.find('.ks_dashboard_item_drill_up').addClass('d-none')
                    item_view.find('.ks_dashboard_item_action_export').removeClass('d-none')
                    item_view.find('.ks_dashboard_quick_edit_action_popup ').removeClass('d-none')
                    item_view.find('.card-body').append(self.renderListViewData(item_data));
                    var rows = JSON.parse(item_data['ks_list_view_data']).data_rows;
                    var ks_length = rows ? rows.length : false;
                        if (ks_length) {
                            if (item_view.find('.ks_pager_name')) {
                                item_view.find('.ks_pager_name').empty();
                                var $ks_pager_container = QWeb.render('ks_pager_template', {
                                    item_id: ids[i],
                                    intial_count: item_data.ks_pagination_limit,
                                    offset : 1
                                })
                                item_view.find('.ks_pager_name').append($($ks_pager_container));
                            }
                            if (ks_length < item_data.ks_pagination_limit) item_view.find('.ks_load_next').addClass('ks_event_offer_list');
                                item_view.find('.ks_value').text("1-" + JSON.parse(item_data['ks_list_view_data']).data_rows.length);

                            if (item_data.ks_record_data_limit == item_data.ks_pagination_limit || item_data.ks_record_count==item_data.ks_pagination_limit) {
                                item_view.find('.ks_load_next').addClass('ks_event_offer_list');
                            }
                    }
                    else{
                        item_view.find('.ks_pager').addClass('d-none');
                    }
                } else if (item_data['ks_dashboard_item_type'] == 'ks_tile') {
                    var item_view = self._ksRenderDashboardTile(item_data);
                    self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]").find(".ks_dashboard_item_hover").replaceWith($(item_view).find('.ks_dashboarditem_id'));
                } else if (item_data['ks_dashboard_item_type'] == 'ks_kpi') {
                    var item_view = self.renderKpi(item_data);
                    self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]").find(".ks_dashboard_item_hover").replaceWith($(item_view).find('.ks_dashboarditem_id'));
                } else  if (item_data['ks_dashboard_item_type'] == 'ks_to_do'){
                    var name = item_data.name ?item_data.name : item_data.ks_model_display_name;
                    self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]").find('.ks_list_view_heading').prop('title',name)
                    self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]").find('.ks_list_view_heading').text(name);
                    self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]").find('.ks_to_do_card_body').empty();
                    self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]").find('.ks_to_do_card_body').append(self.ksRenderToDoDashboardView(item_data)[1]);
                }else{
                    self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]").find(".card-body").empty()
                    var name = item_data.name ?item_data.name : item_data.ks_model_display_name;
                    self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]").find('.ks_chart_heading').prop('title',name)
                    self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]").find('.ks_chart_heading').text(name)
                    self._renderChart(self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]"), item_data);
                }

            }
            self.grid.setStatic(true);
        },

        renderListViewData: function(item) {
            var self = this;
            var list_view_data = JSON.parse(item.ks_list_view_data);
            var item_id = item.id,
                data_rows = list_view_data.data_rows,
                item_title = item.name;
            if (item.ks_list_view_type === "ungrouped" && list_view_data) {
                if (list_view_data.date_index) {
                    var index_data = list_view_data.date_index;
                    for (var i = 0; i < index_data.length; i++) {
                        for (var j = 0; j < list_view_data.data_rows.length; j++) {
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
            if (list_view_data) {
                for (var i = 0; i < list_view_data.data_rows.length; i++) {
                    for (var j = 0; j < list_view_data.data_rows[0]["data"].length; j++) {
                        if (typeof(list_view_data.data_rows[i].data[j]) === "number" || list_view_data.data_rows[i].data[j]) {
                            if (typeof(list_view_data.data_rows[i].data[j]) === "number") {
                                list_view_data.data_rows[i].data[j] = field_utils.format.float(list_view_data.data_rows[i].data[j], Float64Array, {digits: [0, item.ks_precision_digits]})
                            }
                        } else {
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
            var $ksItemContainer = $(QWeb.render(template, {
                list_view_data: list_view_data,
                item_id: item_id,
                list_type: item.ks_list_view_type,
                calculation_type: item.ks_data_calculation_type,
                isDrill: self.ks_dashboard_data.ks_item_data[item_id]['isDrill']
            }));
            self.list_container = $ksItemContainer;
            if (list_view_data) {
                var $ksitemBody = self.ksListViewBody(list_view_data,item_id)
                self.list_container.find('.ks_table_body').append($ksitemBody)
            }

            if (item.ks_list_view_type === "ungrouped" && item.ks_data_calculation_type === 'custom') {
                $ksItemContainer.find('.ks_list_canvas_click').removeClass('ks_list_canvas_click');
            }
            if (item.ks_goal_liness){
                $ksItemContainer.find('.ks_sort_icon').addClass('d-none')
                $ksItemContainer.find('.ks_sort_down').removeClass('ks_sort_down')
                $ksItemContainer.find('.ks_sort_up').removeClass('ks_sort_up')
                $ksItemContainer.find('.list_header').removeClass('ks_dn_asc');

            }

            if (!item.ks_show_records) {
                $ksItemContainer.find('#ks_item_info').hide();
            }
            return $ksItemContainer
        },

        renderTvListView: function(item){
            var self = this;
            var list_view_data = JSON.parse(item.ks_list_view_data),
                pager =  false,
                item_id = item.id,
                data_rows = list_view_data.data_rows,
                length = data_rows ? data_rows.length : false,
                item_title = item.name;
//            var $ksItemContainer = self.renderListViewData(item)
            var $ks_gridstack_container = $(QWeb.render('ks_gridstack_list_tv_view_container', {
                ks_chart_title: item_title,
                ksIsDashboardManager: self.ks_dashboard_data.ks_dashboard_manager,
                ksIsUser: true,
                ks_pager: pager,
                calculation_type: item.ks_data_calculation_type,
            }));

            var $container = self.renderListViewData(item);
            $container.find('.list_header').removeClass('ks_dn_asc');
            if (item.ks_data_calculation_type === 'custom'){
                $container.find('.ks_list_canvas_click').removeClass('ks_list_canvas_click');
            }
            $container.find('.ks_sort_icon').addClass('d-none');
            $ks_gridstack_container.find('.card-body').append($container);

            return $ks_gridstack_container
        },

        _renderListView: function(item, grid){
           var self = this;
            var list_view_data = JSON.parse(item.ks_list_view_data),
                pager = true,
                item_id = item.id,
                data_rows = list_view_data.data_rows,
                length = data_rows ? data_rows.length : 0,
                item_title = item.name;
            var $ksItemContainer = self.renderListViewData(item)
            var $ks_gridstack_container = $(QWeb.render('ks_gridstack_list_view_container', {
                ks_chart_title: item_title,
                ksIsDashboardManager: self.ks_dashboard_data.ks_dashboard_manager,
                ksIsUser: true,
                ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                item_id: item_id,
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
//            if (pager){
//                $ks_gridstack_container.find('.ks_list_canvas_click').removeClass('ks_list_canvas_click');
//            }

            if (item.ks_data_calculation_type === 'query' || item.ks_list_view_type === "ungrouped"){
                $ks_gridstack_container.find('.ks_list_canvas_click').removeClass('ks_list_canvas_click');
            }

            item.$el = $ks_gridstack_container;
            if (item_id in self.gridstackConfig) {
                if (config.device.isMobile){
                    grid.addWidget($ks_gridstack_container[0], {x:self.gridstackConfig[item_id].x, y:self.gridstackConfig[item_id].y, w:self.gridstackConfig[item_id].w, h:self.gridstackConfig[item_id].h, autoPosition:true, minW:3, maxW:null, minH:3, maxH:null, id:item_id});
                }
                else{
                    grid.addWidget($ks_gridstack_container[0], {x:self.gridstackConfig[item_id].x, y:self.gridstackConfig[item_id].y, w:self.gridstackConfig[item_id].w, h:self.gridstackConfig[item_id].h, autoPosition:false, minW:3, maxW:null, minH:3, maxH:null, id:item_id});
                }
            } else {
                grid.addWidget($ks_gridstack_container[0], {x:0, y:0, w:5, h:4, autoPosition:true, minW:3, maxW:null, minH:3, maxH:null, id:item_id});
            }
        },

        _renderTvGraph: function(item){
            var self = this;
            var chart_data = JSON.parse(item.ks_chart_data);
            var isDrill = item.isDrill ? item.isDrill : false;
            var chart_id = item.id,
                chart_title = item.name;
            var chart_title = item.name;
            var chart_type = item.ks_dashboard_item_type.split('_')[1];
            switch (chart_type) {
                case "pie":
                case "doughnut":
                case "polarArea":
                    var chart_family = "circle";
                    break;
                case "bar":
                case "horizontalBar":
                case "line":
                case "area":
                    var chart_family = "square"
                    break;
                default:
                    var chart_family = "none";
                    break;

            }

            var $ks_gridstack_container = $(QWeb.render('ks_gridstack_tv_container', {
                ks_chart_title: chart_title,
                ksIsDashboardManager: self.ks_dashboard_data.ks_dashboard_manager,
                ksIsUser: true,
                ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                chart_id: chart_id,
                chart_family: chart_family,
                chart_type: chart_type,
                ksChartColorOptions: this.ksChartColorOptions,
            })).addClass('ks_dashboarditem_id');
            this.container_owl.append($ks_gridstack_container);
            self._rendertvChart($ks_gridstack_container, item);
        },

        _rendertvChart($ks_gridstack_container,item){
            var self = this;
            var chart_data = JSON.parse(item.ks_chart_data);
            if (item.ks_chart_cumulative_field){
                for (var i=0; i< chart_data.datasets.length; i++){
                    var ks_temp_com = 0
                    var data = []
                    var datasets = {}
                    if (chart_data.datasets[i].ks_chart_cumulative_field){
                        for (var j=0; j < chart_data.datasets[i].data.length; j++)
                            {
                                ks_temp_com = ks_temp_com + chart_data.datasets[i].data[j];
                                data.push(ks_temp_com);
                            }
                            datasets.label =  'Cumulative' + chart_data.datasets[i].label;
                            datasets.data = data;
                            if (item.ks_chart_cumulative){
                                datasets.type =  'line';
                            }
                            chart_data.datasets.push(datasets);
                    }
                }
            }
            if (item.ks_as_of_now){
                   for (var i=0; i< chart_data.datasets.length; i++){
                    var ks_temp_com = 0
                    var data = []
                    var datasets = {}
                    for (var j=0; j < chart_data.datasets[i].data.length; j++)
                        {
                            ks_temp_com = ks_temp_com + chart_data.datasets[i].data[j];
                            data.push(ks_temp_com);
                        }
                        chart_data.datasets[i].data = data.slice(-item.ks_record_data_limit)
                 }
              chart_data['labels'] = chart_data['labels'].slice(-item.ks_record_data_limit)

            }
            var isDrill = item.isDrill ? item.isDrill : false;
            var chart_id = item.id,
                chart_title = item.name;
            var chart_title = item.name;
            var chart_type = item.ks_dashboard_item_type.split('_')[1];
            switch (chart_type) {
                case "pie":
                case "doughnut":
                case "polarArea":
                    var chart_family = "circle";
                    break;
                case "bar":
                case "horizontalBar":
                case "line":
                case "area":
                    var chart_family = "square"
                    break;
                default:
                    var chart_family = "none";
                    break;

            }
            $ks_gridstack_container.find('.ks_color_pallate').data({chartType:chart_type,chartFamily:chart_family});
            var $ksChartContainer = $('<canvas id="ks_chart_canvas_id"  data-chart-id='+chart_id+' style="height:400px"/>');
            $ks_gridstack_container.find('.card-body').append($ksChartContainer);

//            item.$el = $ks_gridstack_container;
            if(chart_family === "circle"){
                if (chart_data && chart_data['labels'].length > 30){
                    $ks_gridstack_container.find(".ks_dashboard_color_option").remove();
                    $ks_gridstack_container.find(".card-body").empty().append($("<div style='font-size:20px;'>Too many records for selected Chart Type. Consider using <strong>Domain</strong> to filter records or <strong>Record Limit</strong> to limit the no of records under <strong>30.</strong>"));
                    return ;
                }
            }

            if(chart_data["ks_show_second_y_scale"] && item.ks_dashboard_item_type === 'ks_bar_chart'){
                var scales  = {}
                scales.yAxes = [
                    {
                        type: "linear",
                        display: true,
                        position: "left",
                        id: "y-axis-0",
                        gridLines:{
                            display: true
                        },
                        labels: {
                            show:true,
                        }
                    },
                    {
                        type: "linear",
                        display: true,
                        position: "right",
                        id: "y-axis-1",
                        labels: {
                            show:true,
                        },
                        ticks: {
                            beginAtZero: true,
                            callback : function(value, index, values){
                                var ks_selection = chart_data.ks_selection;
                                if (ks_selection === 'monetary'){
                                    var ks_currency_id = chart_data.ks_currency;
                                    var ks_data = KsGlobalFunction.ksNumFormatter(value,1);
                                    var ks_data = KsGlobalFunction._onKsGlobalFormatter(value, item.ks_data_formatting, item.ks_precision_digits);
                                    ks_data = KsGlobalFunction.ks_monetary(ks_data, ks_currency_id);
                                    return ks_data;
                                }
                                else if (ks_selection === 'custom'){
                                    var ks_field = chart_data.ks_field;
                                    return KsGlobalFunction._onKsGlobalFormatter(value, item.ks_data_formatting, item.ks_precision_digits) +' '+ ks_field;
                                }
                                else {
                                    return KsGlobalFunction._onKsGlobalFormatter(value, item.ks_data_formatting, item.ks_precision_digits);
                                }
                            },
                        }
                    }
                ]

            }
            var chart_plugin = [];
            if (item.ks_show_data_value) {
                chart_plugin.push(ChartDataLabels);
            }
            var ksMyChart = new Chart($ksChartContainer[0].getContext('2d'), {
                type: chart_type === "area" ? "line" : chart_type,
                plugins: chart_plugin,
                data: {
                    labels: chart_data['labels'],
                    groupByIds:chart_data['groupByIds'],
                    domains:chart_data['domains'],
                    datasets: chart_data.datasets,
                },
                options: {
                    maintainAspectRatio: false,
                    responsiveAnimationDuration: 1000,
                    animation: {
                        easing: 'easeInQuad',
                    },
                    legend: {
                            display: item.ks_hide_legend
                        },
                    scales: scales,
                    layout: {
                        padding: {
                            bottom: 0,
                        }
                    },
                    plugins: {
                        datalabels: {
                            backgroundColor: function(context) {
                                return context.dataset.backgroundColor;
                            },
                            borderRadius: 4,
                            color: 'white',
                            font: {
                                weight: 'bold'
                            },
                            anchor: 'center',
                            display: 'auto',
                            clamp: true,
                            formatter : function(value, ctx) {
                                let sum = 0;
                                let dataArr = ctx.dataset.data;
                                dataArr.map(data => {
                                    sum += data;
                                });
                                let percentage = sum === 0 ? 0 + "%" : (value*100 / sum).toFixed(2)+"%";
                                return percentage;
                            },
                        },
                    },
                }
            });

//            this.chart_container[chart_id] = ksMyChart;
            if(chart_data && chart_data["datasets"].length>0) self.ksChartColors(item.ks_chart_item_color, ksMyChart, chart_type, chart_family,item.ks_bar_chart_stacked,item.ks_semi_circle_chart,item.ks_show_data_value,chart_data,item);

        },
    })
    return KsDashboardNinja;
})
