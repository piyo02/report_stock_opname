from odoo import api, models


class ReportStockOpnameTemp(models.AbstractModel):
    _name = 'report.report_stock_opname.temp_report_stock_opname'

    @api.model
    def render_html(self, docids, data=None):
        docargs =  {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'data': data['form'],
            'start_date': data['start_date'],
            'end_date': data['end_date'],
        }
        print "===================docargs",docargs
        return self.env['report'].render('report_stock_opname.temp_report_stock_opname', docargs)
