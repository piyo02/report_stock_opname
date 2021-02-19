from odoo import api, fields, models
from datetime import datetime, timedelta

import logging

_logger = logging.getLogger(__name__)

class ReportStockOpname(models.TransientModel):
    _name = 'report.stock.opname'

    location_ids = fields.Many2many('stock.location', string='Lokasi', required=False)
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)

    @api.multi
    def print_report_stock_opname(self):
        final_dict = {}

        locations = self.location_ids
        if not len(locations):
            locations = self.env['stock.location'].search([
                ('name', '=', 'Stock')
            ])
        
        for location in locations:
            opnames = self.env['stock.inventory'].search([
                ('date', '<=', self.end_date),
                ('date', '>=', self.start_date),
                ('location_id', '=', location.id),
            ],
            order="date asc")
            
            for opname in opnames:
            
                date = (datetime.strptime(opname.date, '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).date()
                date = date.strftime("%Y-%m-%d")
                loc = '{}/{}'.format(location.location_id.name, location.name)

                if date in final_dict:
                    if loc not in final_dict[date]: 
                        final_dict[date][loc] = []
                else:
                    final_dict[date] = {}
                    final_dict[date][loc] = []
                
                curr_dict = final_dict[date][loc]

                for line in opname.line_ids:
                    quants = self.env['stock.quant'].search([
                        ('product_id.id', '=', line.product_id.id),
                        ('location_id.id', '=', location.id)
                    ])

                    row = 0
                    inv_val = 0
                    for quant in quants:
                        row =+ 1
                        total_inv_val =+ quant.inventory_value

                    if row:
                        avr_inv_val = total_inv_val/row
                    else:
                        purchase = self.env['purchase.order.line'].search([
                            ('product_id.id', '=', line.product_id.id),
                        ],
                        order="date_planned asc", limit=1)
                        avr_inv_val = purchase.price_unit
                    
                    diff = line.product_qty - line.theoretical_qty

                    curr_dict.append([
                        line.product_id.name,                       #0
                        line.product_uom_id.name,                   #1
                        line.product_qty,                           #2
                        line.theoretical_qty,                       #3
                        diff,                                       #4
                        avr_inv_val*diff                            #5
                    ])

        datas = {
            'ids': self.ids,
            'model': 'report.stock.opname',
            'form': final_dict,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        return self.env['report'].get_action(self,'report_stock_opname.temp_report_stock_opname', data=datas)
