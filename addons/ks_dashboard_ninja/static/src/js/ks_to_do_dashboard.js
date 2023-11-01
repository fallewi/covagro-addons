odoo.define('ks_dashboard_ninja.ks_to_do_dashboard_filter', function (require) {
"use strict";

var KsDashboard = require('ks_dashboard_ninja.ks_dashboard');
var core = require('web.core');
var _t = core._t;
var QWeb = core.qweb;
var Dialog = require('web.Dialog');
var config = require('web.config');

return KsDashboard.include({
         events: _.extend({}, KsDashboard.prototype.events, {
        'click .ks_edit_content': '_onKsEditTask',
        'click .ks_delete_content': '_onKsDeleteContent',
        'click .header_add_btn': '_onKsAddTask',
//        'click .ks_add_section': '_onKsAddSection',
        'click .ks_li_tab': '_onKsUpdateAddButtonAttribute',
        'click .ks_do_item_active_handler': '_onKsActiveHandler',
    }),

        ksRenderDashboardItems: function(items) {
            var self = this;
            self.$el.find('.print-dashboard-btn').addClass("ks_pro_print_hide");
            if (self.ks_dashboard_data.ks_gridstack_config) {
                self.gridstackConfig = JSON.parse(self.ks_dashboard_data.ks_gridstack_config);
            }
            var item_view;
            var ks_container_class = 'grid-stack-item',
                ks_inner_container_class = 'grid-stack-item-content';
                for (var i = 0; i < items.length; i++) {
                if (self.grid) {

                    if (items[i].ks_dashboard_item_type === 'ks_tile') {
                        var item_view = self._ksRenderDashboardTile(items[i])
                        if (items[i].id in self.gridstackConfig) {
//                            self.grid.addWidget($(item_view), self.gridstackConfig[items[i].id].x, self.gridstackConfig[items[i].id].y, self.gridstackConfig[items[i].id].width, self.gridstackConfig[items[i].id].height, false, 6, null, 2, 2, items[i].id);
                             if (config.device.isMobile){
                                self.grid.addWidget($(item_view)[0], {x:self.gridstackConfig[items[i].id].x, y:self.gridstackConfig[items[i].id].y, w:self.gridstackConfig[items[i].id].w, h:self.gridstackConfig[items[i].id].h,autoPosition:true,minW:2,maxW:null,minH:2,maxH:2,id:items[i].id,});
                             }
                             else{
                                self.grid.addWidget($(item_view)[0], {x:self.gridstackConfig[items[i].id].x, y:self.gridstackConfig[items[i].id].y, w:self.gridstackConfig[items[i].id].w, h:self.gridstackConfig[items[i].id].h,autoPosition:false,minW:2,maxW:null,minH:2,maxH:2,id:items[i].id,});
                             }
                        } else {
                             self.grid.addWidget($(item_view)[0], {x:0, y:0, w:3, h:2,autoPosition:true,minW:2,maxW:null,minH:2,maxH:2,id:items[i].id});
                        }
                    } else if (items[i].ks_dashboard_item_type === 'ks_list_view') {
                        self._renderListView(items[i], self.grid)
                    } else if (items[i].ks_dashboard_item_type === 'ks_kpi') {
                        var $kpi_preview = self.renderKpi(items[i], self.grid)
                        if (items[i].id in self.gridstackConfig) {
                            if (config.device.isMobile){
                                self.grid.addWidget($kpi_preview[0], {x:self.gridstackConfig[items[i].id].x, y:self.gridstackConfig[items[i].id].y, w:self.gridstackConfig[items[i].id].w, h:self.gridstackConfig[items[i].id].h,autoPosition:true,minW:2,maxW:null,minH:2,maxH:3,id:items[i].id});
                             }
                             else{
                                self.grid.addWidget($kpi_preview[0], {x:self.gridstackConfig[items[i].id].x, y:self.gridstackConfig[items[i].id].y, w:self.gridstackConfig[items[i].id].w, h:self.gridstackConfig[items[i].id].h,autoPosition:false,minW:2,maxW:null,minH:2,maxH:3,id:items[i].id});
                             }
                        } else {
                             self.grid.addWidget($kpi_preview[0], {x:0, y:0, w:3, h:2,autoPosition:true,minW:2,maxW:null,minH:2,maxH:3,id:items[i].id});
                        }

                    }  else if (items[i].ks_dashboard_item_type === 'ks_to_do'){
                        var $to_do_preview = self.ksRenderToDoDashboardView(items[i])[0];
                        if (items[i].id in self.gridstackConfig) {
                            if (config.device.isMobile){
                                self.grid.addWidget($to_do_preview[0], {x:self.gridstackConfig[items[i].id].x, y:self.gridstackConfig[items[i].id].y, w:self.gridstackConfig[items[i].id].w, h:self.gridstackConfig[items[i].id].h, autoPosition:true, minW:3, maxW:null, minH:2, maxH:null, id:items[i].id});
                             }
                             else{
                                self.grid.addWidget($to_do_preview[0], {x:self.gridstackConfig[items[i].id].x, y:self.gridstackConfig[items[i].id].y, w:self.gridstackConfig[items[i].id].w, h:self.gridstackConfig[items[i].id].h, autoPosition:false, minW:3, maxW:null, minH:2, maxH:null, id:items[i].id});
                             }
                        } else {
                            self.grid.addWidget($to_do_preview[0], {x:0, y:0, w:6, h:4, autoPosition:true, minW:3, maxW:null, minH:2, maxH:null, id:items[i].id})
                        }
                    } else {
                        self._renderGraph(items[i], self.grid)
                    }
                }
            }
        },

        ksRenderToDoDashboardView: function(item){
            var self = this;
            var item_title = item.name;
            var item_id = item.id;
            var list_to_do_data = JSON.parse(item.ks_to_do_data)
            var ks_header_color = self._ks_get_rgba_format(item.ks_header_bg_color);
            var ks_font_color = self._ks_get_rgba_format(item.ks_font_color);
            var ks_rgba_button_color = self._ks_get_rgba_format(item.ks_button_color);
            var $ksItemContainer = self.ksRenderToDoView(item);
            var $ks_gridstack_container = $(QWeb.render('ks_to_do_dashboard_container', {
                ks_chart_title: item_title,
                ksIsDashboardManager: self.ks_dashboard_data.ks_dashboard_manager,
                ksIsUser: true,
                ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                item_id: item_id,
                to_do_view_data: list_to_do_data,
                 ks_rgba_button_color:ks_rgba_button_color,
            })).addClass('ks_dashboarditem_id')
            $ks_gridstack_container.find('.ks_card_header').addClass('ks_bg_to_color').css({"background-color": ks_header_color });
            $ks_gridstack_container.find('.ks_card_header').addClass('ks_bg_to_color').css({"color": ks_font_color + ' !important' });
            $ks_gridstack_container.find('.ks_li_tab').addClass('ks_bg_to_color').css({"color": ks_font_color + ' !important' });
            $ks_gridstack_container.find('.ks_list_view_heading').addClass('ks_bg_to_color').css({"color": ks_font_color + ' !important' });
            $ks_gridstack_container.find('.ks_to_do_card_body').append($ksItemContainer)
            return [$ks_gridstack_container, $ksItemContainer];
        },

        ksRenderToDoView: function(item, ks_tv_play=false) {
            var self = this;
            var  item_id = item.id;
            var list_to_do_data = JSON.parse(item.ks_to_do_data);
            var $todoViewContainer = $(QWeb.render('ks_to_do_dashboard_inner_container', {
                ks_to_do_view_name: "Test",
                to_do_view_data: list_to_do_data,
                item_id: item_id,
                ks_tv_play: ks_tv_play
            }));

            return $todoViewContainer
        },

        _onKsEditTask: function(e){
            var self = this;
            var ks_description_id = e.currentTarget.dataset.contentId;
            var ks_item_id = e.currentTarget.dataset.itemId;
            var ks_section_id = e.currentTarget.dataset.sectionId;
            var ks_description = $(e.currentTarget.parentElement.parentElement).find('.ks_description').attr('value');

            var $content = "<div><input type='text' class='ks_description' value='"+ ks_description +"' placeholder='Task'></input></div>"
            var dialog = new Dialog(this, {
            title: _t('Edit Task'),
            size: 'medium',
            $content: $content,
            buttons: [
                {
                text: 'Save',
                classes: 'btn-primary',
                click: function(e){
                    var content = $(e.currentTarget.parentElement.parentElement).find('.ks_description').val();
                    if (content.length === 0){
                        content = ks_description;
                    }
                    self.onSaveTask(content, parseInt(ks_description_id), parseInt(ks_item_id), parseInt(ks_section_id));
                },
                close: true,
            },
            {
                    text: _t('Close'),
                    classes: 'btn-secondary o_form_button_cancel',
                    close: true,
                }
            ],
        });
            dialog.open();
        },

        onSaveTask: function(content, ks_description_id, ks_item_id, ks_section_id){
            var self = this;
            this._rpc({
                    model: 'ks_to.do.description',
                    method: 'write',
                    args: [ks_description_id, {
                        "ks_description": content
                    }],
                }).then(function() {
                    self.ksFetchUpdateItem(ks_item_id).then(function(){
                        $(".ks_li_tab[data-item-id=" + ks_item_id + "]").removeClass('active');
                        $(".ks_li_tab[data-section-id=" + ks_section_id + "]").addClass('active');
                        $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('active');
                        $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('show');
                        $(".ks_tab_section[data-section-id=" + ks_section_id + "]").addClass('active');
                        $(".ks_tab_section[data-section-id=" + ks_section_id + "]").addClass('show');
                        $(".header_add_btn[data-item-id=" + ks_item_id + "]").attr('data-section-id', ks_section_id);
                    });
                });
        },

        _onKsDeleteContent: function(e){
            var self = this;
            var ks_description_id = e.currentTarget.dataset.contentId;
            var ks_item_id = e.currentTarget.dataset.itemId;
            var ks_section_id = e.currentTarget.dataset.sectionId;

            Dialog.confirm(this, (_t("Are you sure you want to remove this task?")), {
                confirm_callback: function() {

                    self._rpc({
                    model: 'ks_to.do.description',
                    method: 'unlink',
                    args: [parseInt(ks_description_id)],
                }).then(function() {
                        self.ksFetchUpdateItem(ks_item_id).then(function(){
                            $(".ks_li_tab[data-item-id=" + ks_item_id + "]").removeClass('active');
                            $(".ks_li_tab[data-section-id=" + ks_section_id + "]").addClass('active');
                            $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('active');
                            $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('show');
                            $(".ks_tab_section[data-section-id=" + ks_section_id + "]").addClass('active');
                            $(".ks_tab_section[data-section-id=" + ks_section_id + "]").addClass('show');
                            $(".header_add_btn[data-item-id=" + ks_item_id + "]").attr('data-section-id', ks_section_id);
                        });
                    });
                },
            });
        },

        _onKsAddTask: function(e){
            var self = this;
            var ks_section_id = e.currentTarget.dataset.sectionId;
            var ks_item_id = e.currentTarget.dataset.itemId;
            var $content = "<div><input type='text' class='ks_section' placeholder='Task' required></input></div>"
            var dialog = new Dialog(this, {
            title: _t('New Task'),
            $content: $content,
            size: 'medium',
            buttons: [
                {
                text: 'Save',
                classes: 'btn-primary',
                click: function(e){
                    var content = $(e.currentTarget.parentElement.parentElement).find('.ks_section').val();
                    if (content.length === 0){
//                        this.do_notify(false, _t('Successfully sent to printer!'));
                    }
                    else{
                        self._onCreateTask(content, parseInt(ks_section_id), parseInt(ks_item_id));
                    }
                },
                close: true,
            },
            {
                    text: _t('Close'),
                    classes: 'btn-secondary o_form_button_cancel',
                    close: true,
                }
            ],
        });
            dialog.open();
        },

        _onCreateTask: function(content, ks_section_id, ks_item_id){
            var self = this;
            this._rpc({
                    model: 'ks_to.do.description',
                    method: 'create',
                    args: [{
                        ks_to_do_header_id: ks_section_id,
                        ks_description: content,
                    }],
                }).then(function() {
                    self.ksFetchUpdateItem(ks_item_id).then(function(){
                        $(".ks_li_tab[data-item-id=" + ks_item_id + "]").removeClass('active');
                        $(".ks_li_tab[data-section-id=" + ks_section_id + "]").addClass('active');
                        $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('active');
                        $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('show');
                        $(".ks_tab_section[data-section-id=" + ks_section_id + "]").addClass('active');
                        $(".ks_tab_section[data-section-id=" + ks_section_id + "]").addClass('show');
                        $(".header_add_btn[data-item-id=" + ks_item_id + "]").attr('data-section-id', ks_section_id);
                    });

                });
        },


        _onKsUpdateAddButtonAttribute: function(e){
            var item_id = e.currentTarget.dataset.itemId;
            var sectionId = e.currentTarget.dataset.sectionId;
            $(".header_add_btn[data-item-id=" + item_id + "]").attr('data-section-id', sectionId);
        },

        _onKsActiveHandler: function(e){
            var self = this;
            var ks_item_id = e.currentTarget.dataset.itemId;
            var content_id = e.currentTarget.dataset.contentId;
            var ks_task_id = e.currentTarget.dataset.contentId;
            var ks_section_id = e.currentTarget.dataset.sectionId;
            var ks_value = e.currentTarget.dataset.valueId;
            if (ks_value== 'True'){
                ks_value = false
            }else{
                ks_value = true
            }
            self.content_id = content_id;
            this._rpc({
                    model: 'ks_to.do.description',
                    method: 'write',
                    args: [content_id, {
                        "ks_active": ks_value
                    }],
                }).then(function() {
                    self.ksFetchUpdateItem(ks_item_id).then(function(){
                        $(".ks_li_tab[data-item-id=" + ks_item_id + "]").removeClass('active');
                        $(".ks_li_tab[data-section-id=" + ks_section_id + "]").addClass('active');
                        $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('active');
                        $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('show');
                        $(".ks_tab_section[data-section-id=" + ks_section_id + "]").addClass('active');
                        $(".ks_tab_section[data-section-id=" + ks_section_id + "]").addClass('show');
                        $(".header_add_btn[data-item-id=" + ks_item_id + "]").attr('data-section-id', ks_section_id);
                    });
                });
        }
})

});