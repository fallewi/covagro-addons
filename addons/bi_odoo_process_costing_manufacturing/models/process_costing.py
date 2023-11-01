# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_round


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def _compute_total_cost(self):
        material_total = 0.0
        labour_total = 0.0
        overhead_total = 0.0
        for line in self.bom_material_cost_ids:
            material_total += line.total_cost

        for line in self.bom_labour_cost_ids:
            labour_total += line.total_cost

        for line in self.bom_overhead_cost_ids:
            overhead_total += line.total_cost

        self.bom_total_material_cost = material_total
        self.bom_total_labour_cost = labour_total
        self.bom_total_overhead_cost = overhead_total

    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = res_user_id.company_id.currency_id

    @api.model
    def create(self, vals):
        res = super(MrpBom, self).create(vals)

        for material in res.bom_line_ids:
            vals = {
                'product_id': material.product_id.product_tmpl_id.id,
                'planned_qty': material.product_qty,
                'uom_id': material.product_uom_id.id,
                'cost': material.product_uom_id._compute_price(material.product_id.standard_price, material.product_uom_id),
                'mrp_bom_material_id': res.id,
            }

            res.write({'bom_material_cost_ids': [(0, 0, vals)]})
        config = self.env['res.config.settings'].search([], order="id desc", limit=1)
        if res.operation_ids and config.process_costing == 'workcenter':
            for line in res.bom_labour_cost_ids:
                line.unlink()
            for line in res.bom_overhead_cost_ids:
                line.unlink()
            for operation in res.operation_ids:
                value = {
                    'operation_id': operation.id,
                    'workcenter_id': operation.workcenter_id.id,
                    'cost': operation.workcenter_id.labour_costs_hour or False,
                    'mrp_bom_labour_id': res.id,

                }
                if operation.time_cycle > 0:
                    value.update({'planned_qty': operation.time_cycle / 60})
                res.write({'bom_labour_cost_ids': [(0, 0, value)]})

            for operation in res.operation_ids:
                value = {
                    'operation_id': operation.id,
                    'workcenter_id': operation.workcenter_id.id,
                    'cost': operation.workcenter_id.overhead_cost_hour or False,
                    'mrp_bom_overhead_id': res.id,

                }
                if operation.time_cycle > 0:
                    value.update({'planned_qty': operation.time_cycle / 60})
                res.write({'bom_overhead_cost_ids': [(0, 0, value)]})
        return res

    def write(self, vals):
        res = super(MrpBom, self).write(vals)
        config = self.env['res.config.settings'].search([], order="id desc", limit=1)

        if vals.get('bom_line_ids'):
            for line in self.bom_material_cost_ids:
                line.unlink()
            for material in self.bom_line_ids:
                vals = {
                    'product_id': material.product_id.product_tmpl_id.id,
                    'planned_qty': material.product_qty,
                    'uom_id': material.product_uom_id.id,
                    'cost': material.product_uom_id._compute_price(material.product_id.standard_price, material.product_uom_id),
                    'mrp_bom_material_id': self.id,
                }
                material_obj = self.env['mrp.bom.material.cost'].create(vals)
        if vals.get('operation_ids') and config.process_costing == 'workcenter':
            for line in self.bom_labour_cost_ids:
                line.unlink()
            for line in self.bom_overhead_cost_ids:
                line.unlink()
            for operation in self.operation_ids:
                value = {
                    'operation_id': operation.id,
                    'workcenter_id': operation.workcenter_id.id,
                    'cost': operation.workcenter_id.labour_costs_hour or False,
                    'mrp_bom_labour_id': self.id,
                }
                if operation.time_cycle > 0:
                    value.update({'planned_qty': operation.time_cycle / 60})
                self.write({'bom_labour_cost_ids': [(0, 0, value)]})

            for operation in self.operation_ids:
                value = {
                    'operation_id': operation.id,
                    'workcenter_id': operation.workcenter_id.id,
                    'cost': operation.workcenter_id.overhead_cost_hour or False,
                    'mrp_bom_overhead_id': self.id,

                }
                if operation.time_cycle > 0:
                    value.update({'planned_qty': operation.time_cycle / 60})
                self.write({'bom_overhead_cost_ids': [(0, 0, value)]})

        return res

    bom_material_cost_ids = fields.One2many("mrp.bom.material.cost", "mrp_bom_material_id", "Coût matériel")
    bom_labour_cost_ids = fields.One2many("mrp.bom.labour.cost", "mrp_bom_labour_id", "Coût du travail")
    bom_overhead_cost_ids = fields.One2many("mrp.bom.overhead.cost", "mrp_bom_overhead_id", "Frais généraux")
    # single page total cost
    bom_total_material_cost = fields.Float(compute='_compute_total_cost', string="Coût total du matériel", default=0.0)
    bom_total_labour_cost = fields.Float(compute='_compute_total_cost', string="Coût total de la main-d'œuvre", default=0.0)
    bom_total_overhead_cost = fields.Float(compute='_compute_total_cost', string="Frais généraux totaux", default=0.0)
    currency_id = fields.Many2one("res.currency", compute='get_currency_id', string="Monnaie")


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    def write(self, vals):
        if vals.get('product_id'):
            product = self.env['product.product'].browse(vals.get('product_id'))
            old_product = self.product_id.product_tmpl_id
            product_id = product.product_tmpl_id
            material_product_id = self.env['mrp.bom.material.cost'].search(
                [('product_id', '=', old_product.id), ('mrp_bom_material_id', '=', self.bom_id.id)])
            material_vals = {
                'product_id': product_id.id,
                'uom_id': product_id.uom_id.id,
                'cost': product_id.uom_id._compute_price(product_id.standard_price, product_id.uom_id),
                'planned_qty': self.product_qty or vals.get('product_qty'),
            }
            material_product_id.write(material_vals)
        if vals.get('product_qty'):
            product = self.env['product.product'].browse(self.product_id)
            product_id = self.product_id.product_tmpl_id
            material_product_id = self.env['mrp.bom.material.cost'].search(
                [('product_id', '=', product_id.id), ('mrp_bom_material_id', '=', self.bom_id.id)])
            material_product_id.write({'planned_qty': vals.get('product_qty')})

        res = super(MrpBomLine, self).write(vals)
        return res


class MrpBomMaterialCost(models.Model):
    _name = "mrp.bom.material.cost"

    operation_id = fields.Many2one('mrp.routing.workcenter', string="Opération")
    product_id = fields.Many2one('product.template', string="Produit")
    planned_qty = fields.Float(string="Quantité prévue", default=0.0)
    actual_qty = fields.Float(string="Quantité réelle", default=0.0)
    uom_id = fields.Many2one('uom.uom', string="Unité")
    cost = fields.Float(string="Coût/Unité")
    total_cost = fields.Float(compute='onchange_planned_qty', string="Coût total")
    total_actual_cost = fields.Float(compute='onchange_planned_qty', string="Coût réel total")
    mrp_bom_material_id = fields.Many2one("mrp.bom", "Matériau de la nomenclature Mrp")
    mrp_pro_material_id = fields.Many2one("mrp.production", "Matériel de production MRP")
    mrp_wo_material_id = fields.Many2one("mrp.workorder", "Matériel de bon de travail Mrp")
    currency_id = fields.Many2one("res.currency", compute='get_currency_id', string="Dévise")

    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = res_user_id.company_id.currency_id

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = {}
        if not self.product_id:
            return res
        self.uom_id = self.product_id.uom_id.id
        if self.uom_id:
            self.cost = self.product_id.uom_id._compute_price(self.product_id.standard_price, self.uom_id)
        else:
            self.cost = self.product_id.uom_id._compute_price(self.product_id.standard_price, self.product_id.uom_id)

    @api.onchange('planned_qty', 'cost','uom_id')
    def onchange_planned_qty(self):
        for line in self:
            if line.product_id:
                if line.uom_id:
                    line.cost = line.product_id.uom_id._compute_price(line.product_id.standard_price, line.uom_id)
                else:
                    line.cost = line.product_id.uom_id._compute_price(line.product_id.standard_price, line.product_id.uom_id)

            price = line.planned_qty * line.cost
            actual_price = line.actual_qty * line.cost
            line.total_cost = price
            line.total_actual_cost = actual_price


class MrpBomLabourCost(models.Model):
    _name = "mrp.bom.labour.cost"

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = {}
        if not self.product_id:
            return res
        self.uom_id = self.product_id.uom_id.id

    @api.onchange('planned_qty', 'cost')
    def onchange_labour_planned_qty(self):
        for line in self:
            price = line.planned_qty * line.cost
            actual_price = line.actual_qty * line.cost
            line.total_cost = price
            line.total_actual_cost = actual_price

    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = res_user_id.company_id.currency_id

    operation_id = fields.Many2one('mrp.routing.workcenter', string="Opération")
    product_id = fields.Many2one('product.template', string="Produit")
    planned_qty = fields.Float(string="Heure prévue", default=0.0)
    actual_qty = fields.Float(string="Heure réelle", default=0.0)
    uom_id = fields.Many2one('uom.uom', string="Unité")
    workcenter_id = fields.Many2one('mrp.workcenter', string="Centre de travail")
    cost = fields.Float(string="Cost/Hour")
    total_cost = fields.Float(compute='onchange_labour_planned_qty', string="Coût total")
    total_actual_cost = fields.Float(compute='onchange_labour_planned_qty', string="Coût réel total")
    mrp_bom_labour_id = fields.Many2one("mrp.bom", "Travail sur le BOM")
    mrp_pro_labour_id = fields.Many2one("mrp.production", "Travail sur la production de BOM")
    mrp_wo_labour_id = fields.Many2one("mrp.workorder", "Main-d'oeuvre")
    currency_id = fields.Many2one("res.currency", compute='get_currency_id', string="Dévise")


class MrpBomOverheadCost(models.Model):
    _name = "mrp.bom.overhead.cost"

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = {}
        if not self.product_id:
            return res
        self.uom_id = self.product_id.uom_id.id

    @api.onchange('planned_qty', 'cost')
    def onchange_overhead_planned_qty(self):
        for line in self:
            price = line.planned_qty * line.cost
            actual_price = line.actual_qty * line.cost
            line.total_cost = price
            line.total_actual_cost = actual_price

    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = res_user_id.company_id.currency_id

    operation_id = fields.Many2one('mrp.routing.workcenter', string="Opération")
    product_id = fields.Many2one('product.template', string="Produit")
    planned_qty = fields.Float(string="Heure prévue", default=0.0)
    actual_qty = fields.Float(string="Heure réelle", default=0.0)
    uom_id = fields.Many2one('uom.uom', string="Unité")
    workcenter_id = fields.Many2one('mrp.workcenter', string="Centre de travail")
    cost = fields.Float(string="Cost/Hour")
    total_cost = fields.Float(compute='onchange_overhead_planned_qty', string="Coût total")
    total_actual_cost = fields.Float(compute='onchange_overhead_planned_qty', string="Coût réel total")
    mrp_bom_overhead_id = fields.Many2one("mrp.bom", "Frais généraux de nomenclature")
    mrp_pro_overhead_id = fields.Many2one("mrp.production", "Frais généraux de production Mrp")
    mrp_wo_overhead_id = fields.Many2one("mrp.workorder", "Frais généraux d'ordre de travail Mrp")
    currency_id = fields.Many2one("res.currency", compute='get_currency_id', string="Dévise")


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def copy(self, default=None):
        res = super().copy(default)

        for line in res.pro_labour_cost_ids:
            line.unlink()
        for line in res.pro_overhead_cost_ids:
            line.unlink()
        for line in res.pro_material_cost_ids:
            line.unlink()
        for labour in self.pro_labour_cost_ids:
            new_line = labour.copy()
            new_line.write({'mrp_pro_labour_id': res.id})
        for overhead in self.pro_overhead_cost_ids:
            new_line = overhead.copy()
            new_line.write({'mrp_pro_overhead_id': res.id})
        for material in self.pro_material_cost_ids:
            new_line = material.copy()
            new_line.write({'mrp_pro_material_id': res.id})

        return res

    @api.model
    def create(self, vals):
        list_of_material = []
        list_of_labour = []
        list_of_overhead = []

        mrp_bom_obj = self.env['mrp.bom'].browse(vals['bom_id'])
        res = super(MrpProduction, self).create(vals)
        for labour in res.bom_id.bom_labour_cost_ids:
            vals = {'operation_id': labour.operation_id.id,
                    'product_id': labour.product_id.id,
                    'planned_qty': labour.planned_qty,
                    'uom_id': labour.uom_id.id,
                    'cost': labour.cost or False,
                    'mrp_pro_labour_id': res.id,

                    }
            labour_res = self.env["mrp.bom.labour.cost"].create(vals)

        for overhead in res.bom_id.bom_overhead_cost_ids:
            vals = {'operation_id': overhead.operation_id.id,
                    'product_id': overhead.product_id.id,
                    'planned_qty': overhead.planned_qty,
                    'uom_id': overhead.uom_id.id,
                    'cost': overhead.cost or False,
                    'mrp_pro_overhead_id': res.id,

                    }

            overhead_res = self.env["mrp.bom.overhead.cost"].create(vals)

        for material in res.move_raw_ids:
            product_id = self.env['product.template'].search([('id', '=', material.product_id.product_tmpl_id.id)])

            bom_material = self.env['mrp.bom.material.cost'].search(
                [('product_id', '=', product_id.id), ('mrp_bom_material_id', '=', res.bom_id.id)], limit=1)

            if bom_material:
                vals = {
                    'product_id': product_id.id,
                    'planned_qty': material.product_uom_qty,
                    'uom_id': bom_material.uom_id.id,
                    'cost': bom_material.cost,
                    'operation_id': bom_material.operation_id.id,
                    'mrp_pro_material_id': res.id,
                }
                if res.product_qty <= 1:
                    material_obj = self.env['mrp.bom.material.cost'].create(vals)

        return res

    @api.onchange('product_qty')
    def _onchange_qty(self):
        list1 = []
        for material in self.move_raw_ids:
            product_id = self.env['product.template'].search([('id', '=', material.product_id.product_tmpl_id.id)])

            bom_material = self.env['mrp.bom.material.cost'].search(
                [('product_id', '=', product_id.id), ('mrp_bom_material_id', '=', self.bom_id.id)], limit=1)
            if bom_material:
                list1.append([0, 0, {'product_id': product_id.id,
                                     'planned_qty': material.product_uom_qty,
                                     'uom_id': bom_material.uom_id.id,
                                     'cost': bom_material.cost,
                                     'operation_id': bom_material.operation_id.id,
                                     'mrp_pro_material_id': self.id,
                                     }])
        self.pro_material_cost_ids = [(6, 0, [])]
        self.write({'pro_material_cost_ids': list1})

    def _compute_total_cost(self):
        material_total = 0.0
        material_actual_total = 0.0

        labour_total = 0.0
        labour_actual_total = 0.0

        overhead_total = 0.0
        overhead_actual_total = 0.0

        for line in self.pro_material_cost_ids:
            material_total += line.total_cost
            material_actual_total += line.total_actual_cost

        for line in self.pro_labour_cost_ids:
            labour_total += line.total_cost
            labour_actual_total += line.total_actual_cost

        for line in self.pro_overhead_cost_ids:
            overhead_total += line.total_cost
            overhead_actual_total += line.total_actual_cost

        self.total_material_cost = material_total
        self.total_actual_material_cost = material_actual_total

        self.total_labour_cost = labour_total
        self.total_actual_labour_cost = labour_actual_total

        self.total_overhead_cost = overhead_total
        self.total_actual_overhead_cost = overhead_actual_total

    def _compute_total_all_cost(self):
        total = 0.0
        actual_total = 0.0
        total = self.total_material_cost + self.total_labour_cost + self.total_overhead_cost
        actual_total = self.total_actual_material_cost + self.total_actual_labour_cost + self.total_actual_overhead_cost
        self.total_all_cost = total
        self.total_actual_all_cost = actual_total

    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = res_user_id.company_id.currency_id

    def _compute_total_product_cost(self):
        total = 0.0
        for line in self.finished_move_line_ids:
            if line.qty_done != 0.0:
                total = self.total_actual_all_cost / line.qty_done
        self.product_unit_cost = total

    def button_mark_done(self):
        if  not self.workorder_ids:
            for line in self.move_raw_ids:

                for mo in self.pro_material_cost_ids:
                    if line.product_id.product_tmpl_id.id == mo.product_id.id:
                        if mo.actual_qty == 0.00:
                            mo.write({'actual_qty': line.quantity_done})  
                        
                for mo in self.pro_labour_cost_ids:
                    if mo.actual_qty == 0.00:
                        mo.write({'actual_qty': line.quantity_done})  

                for mo in self.pro_overhead_cost_ids:
                    if mo.actual_qty == 0.00:
                        mo.write({'actual_qty': line.quantity_done})          
        res = super(MrpProduction, self).button_mark_done()
        return res

    currency_id = fields.Many2one("res.currency", compute='get_currency_id', string="Currency")

    pro_material_cost_ids = fields.One2many("mrp.bom.material.cost", "mrp_pro_material_id", "Coût matériel")
    pro_labour_cost_ids = fields.One2many("mrp.bom.labour.cost", "mrp_pro_labour_id", "Coût du travail")
    pro_overhead_cost_ids = fields.One2many("mrp.bom.overhead.cost", "mrp_pro_overhead_id", "Frais généraux")
    pro_total_material_cost = fields.Float(string="Coût total du matériel", default=0.0)

    # Costing Tab
    total_material_cost = fields.Float(compute='_compute_total_cost', string="Coût total du matériel", default=0.0)
    total_labour_cost = fields.Float(compute='_compute_total_cost', string="Coût total de la main-d'œuvre", default=0.0)
    total_overhead_cost = fields.Float(compute='_compute_total_cost', string="Frais généraux totaux", default=0.0)
    total_all_cost = fields.Float(compute='_compute_total_all_cost', string="Coût total", default=0.0)

    # Costing Tab
    total_actual_material_cost = fields.Float(compute='_compute_total_cost', string="Total Actual Material Cost",
                                              default=0.0)
    total_actual_labour_cost = fields.Float(compute='_compute_total_cost', string="Coût réel total de la main-d'œuvre",
                                            default=0.0)
    total_actual_overhead_cost = fields.Float(compute='_compute_total_cost', string="Frais généraux réels totaux",
                                              default=0.0)
    total_actual_all_cost = fields.Float(compute='_compute_total_all_cost', string="Coût réel total", default=0.0)

    product_unit_cost = fields.Float(compute='_compute_total_product_cost', string="Coût unitaire du produit", default=0.0)


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def button_finish(self):
        for line in self:
            actual_hour = line.duration / 60
            labout = self.env['mrp.bom.labour.cost'].search(
                [('mrp_pro_labour_id', '=', line.production_id.id), ('operation_id', '=', line.operation_id.id)])
            overhead = self.env['mrp.bom.overhead.cost'].search(
                [('mrp_pro_overhead_id', '=', line.production_id.id), ('operation_id', '=', line.operation_id.id)])

            if labout:
                labout.write({'actual_qty': actual_hour})

            else:
                for lo in line.production_id.pro_labour_cost_ids:
                    lo.write({'actual_qty': actual_hour})

            if overhead:
                overhead.write({'actual_qty': actual_hour})
            else:
                for lo in line.production_id.pro_overhead_cost_ids:
                    lo.write({'actual_qty': actual_hour})

            if not line.next_work_order_id:
                for line in self.production_id.move_raw_ids:

                    for mo in self.production_id.pro_material_cost_ids:
                        if line.product_id.product_tmpl_id.id == mo.product_id.id:
                            mo.write({'actual_qty': actual_hour})

              
        res = super(MrpWorkorder, self).button_finish()
        return res



    def _compute_total_cost(self):
        material_total = 0.0
        material_actual_total = 0.0

        labour_total = 0.0
        labour_actual_total = 0.0

        overhead_total = 0.0
        overhead_actual_total = 0.0

        for order in self:
            for line in order.wo_material_cost_ids:
                material_total += line.total_cost
                material_actual_total += line.total_actual_cost
            order.total_material_cost = material_total
            order.total_actual_material_cost = material_actual_total

            for line in order.wo_labour_cost_ids:
                labour_total += line.total_cost
                labour_actual_total += line.total_actual_cost
            order.total_labour_cost = labour_total
            order.total_actual_labour_cost = labour_actual_total

            for line in order.wo_overhead_cost_ids:
                overhead_total += line.total_cost
                overhead_actual_total += line.total_actual_cost
            order.total_overhead_cost = overhead_total
            order.total_actual_overhead_cost = overhead_actual_total

    def _compute_total_all_cost(self):
        total = 0.0
        actual_total = 0.0
        for line in self:
            total = line.total_material_cost + line.total_labour_cost + line.total_overhead_cost
            actual_total = line.total_actual_material_cost + line.total_actual_labour_cost + line.total_actual_overhead_cost
            line.total_all_cost = total
            line.total_actual_all_cost = actual_total

    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = res_user_id.company_id.currency_id

    currency_id = fields.Many2one("res.currency", compute='get_currency_id', string="Currency")

    wo_material_cost_ids = fields.One2many("mrp.bom.material.cost", "mrp_wo_material_id", "Coût matériel")
    wo_labour_cost_ids = fields.One2many("mrp.bom.labour.cost", "mrp_wo_labour_id", "Coût du travail")
    wo_overhead_cost_ids = fields.One2many("mrp.bom.overhead.cost", "mrp_wo_overhead_id", "Frais généraux")
    actual_hour_wo = fields.Float(string="Heure réelle")
    # Costing Tab
    total_material_cost = fields.Float(compute='_compute_total_cost', string="Coût total du matériel", default=0.0)
    total_labour_cost = fields.Float(compute='_compute_total_cost', string="Coût total de la main-d'œuvre", default=0.0)
    total_overhead_cost = fields.Float(compute='_compute_total_cost', string="Frais généraux totaux", default=0.0)
    total_all_cost = fields.Float(compute='_compute_total_all_cost', string="Coût total", default=0.0)

    # Costing Tab
    total_actual_material_cost = fields.Float(compute='_compute_total_cost', string="Total Actual Material Cost",
                                              default=0.0)
    total_actual_labour_cost = fields.Float(compute='_compute_total_cost', string="Coût réel total de la main-d'œuvre",
                                            default=0.0)
    total_actual_overhead_cost = fields.Float(compute='_compute_total_cost', string="Frais généraux réels totaux",
                                              default=0.0)
    total_actual_all_cost = fields.Float(compute='_compute_total_all_cost', string="Coût réel total", default=0.0)

    product_unit_cost = fields.Float(string="Coût unitaire du produit", default=0.0)

    def record_production(self):

        for line in self.production_id.pro_labour_cost_ids:
            if line.operation_id.id == self.operation_id.id:
                line.write({'actual_qty': self.actual_hour_wo})
        for line in self.production_id.pro_overhead_cost_ids:
            if line.operation_id.id == self.operation_id.id:
                line.write({'actual_qty': self.actual_hour_wo})

        res = super(MrpWorkorder, self).record_production()

        return res


class ChangeProductionQty(models.TransientModel):
    _inherit = 'change.production.qty'

    def change_prod_qty(self):
        precision = self.env['decimal.precision'].precision_get('Unité de mesure du produit')
        for wizard in self:
            production = wizard.mo_id
            produced = sum(
                production.move_finished_ids.filtered(lambda m: m.product_id == production.product_id).mapped(
                    'quantity_done'))
            if wizard.product_qty < produced:
                format_qty = '%.{precision}f'.format(precision=precision)
                raise UserError(_(
                    "Vous avez déjà traité %(quantity)s. Veuillez saisir une quantité supérieure à %(minimum)s ",
                    quantity=format_qty % produced,
                    minimum=format_qty % produced
                ))

            # Change Material,Labour and Overhead quantity
            for material in production.pro_material_cost_ids:
                for bom in production.bom_id.bom_line_ids:
                    if material.product_id.id == bom.product_id.id:
                        material.write({'planned_qty': wizard.product_qty * bom.product_qty,
                                        'actual_qty': wizard.product_qty * bom.product_qty})

            for labour in production.pro_labour_cost_ids:
                for bom in production.bom_id.bom_labour_cost_ids:
                    if labour.product_id.id == bom.product_id.id:
                        labour.write({'planned_qty': wizard.product_qty * bom.planned_qty,
                                      'actual_qty': wizard.product_qty * bom.planned_qty})

            for overhead in production.pro_overhead_cost_ids:
                for bom in production.bom_id.bom_overhead_cost_ids:
                    if overhead.product_id.id == bom.product_id.id:
                        overhead.write({'planned_qty': wizard.product_qty * bom.planned_qty,
                                        'actual_qty': wizard.product_qty * bom.planned_qty})

            old_production_qty = production.product_qty
            new_production_qty = wizard.product_qty
            done_moves = production.move_finished_ids.filtered(lambda x: x.state == 'done' and x.product_id == production.product_id)
            qty_produced = production.product_id.uom_id._compute_quantity(sum(done_moves.mapped('product_qty')), production.product_uom_id)

            factor = (new_production_qty - qty_produced) / (old_production_qty - qty_produced)
            update_info = production._update_raw_moves(factor)
            documents = {}
            for move, old_qty, new_qty in update_info:
                iterate_key = production._get_document_iterate_key(move)
                if iterate_key:
                    document = self.env['stock.picking']._log_activity_get_documents({move: (new_qty, old_qty)}, iterate_key, 'UP')
                    for key, value in document.items():
                        if documents.get(key):
                            documents[key] += [value]
                        else:
                            documents[key] = [value]
            production._log_manufacture_exception(documents)
            finished_moves_modification = self._update_finished_moves(production, new_production_qty - qty_produced, old_production_qty - qty_produced)
            if finished_moves_modification:
                production._log_downside_manufactured_quantity(finished_moves_modification)
            production.write({'product_qty': new_production_qty})

            for wo in production.workorder_ids:
                operation = wo.operation_id
                wo.duration_expected = wo._get_duration_expected(ratio=new_production_qty / old_production_qty)
                quantity = wo.qty_production - wo.qty_produced
                if production.product_id.tracking == 'serial':
                    quantity = 1.0 if not float_is_zero(quantity, precision_digits=precision) else 0.0
                else:
                    quantity = quantity if (quantity > 0 and not float_is_zero(quantity, precision_digits=precision)) else 0
                wo._update_qty_producing(quantity)
                if wo.qty_produced < wo.qty_production and wo.state == 'done':
                    wo.state = 'progress'
                if wo.qty_produced == wo.qty_production and wo.state == 'progress':
                    wo.state = 'done'
                    if wo.next_work_order_id.state == 'pending':
                        wo.next_work_order_id.state = 'ready'
                # assign moves; last operation receive all unassigned moves
                # TODO: following could be put in a function as it is similar as code in _workorders_create
                # TODO: only needed when creating new moves
                moves_raw = production.move_raw_ids.filtered(lambda move: move.operation_id == operation and move.state not in ('done', 'cancel'))
                if wo == production.workorder_ids[-1]:
                    moves_raw |= production.move_raw_ids.filtered(lambda move: not move.operation_id)
                moves_finished = production.move_finished_ids.filtered(lambda move: move.operation_id == operation) #TODO: code does nothing, unless maybe by_products?
                moves_raw.mapped('move_line_ids').write({'workorder_id': wo.id})
                (moves_finished + moves_raw).write({'workorder_id': wo.id})

        # run scheduler for moves forecasted to not have enough in stock
        self.mo_id.filtered(lambda mo: mo.state in ['confirmed', 'progress']).move_raw_ids._trigger_scheduler()
        return {}
