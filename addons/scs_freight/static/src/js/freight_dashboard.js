odoo.define('freightDashboard.freightDashboard', function (require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var web_client = require('web.web_client');
    var _t = core._t;
    var QWeb = core.qweb;
    var self = this;
    var currency;
    var ActionMenu = AbstractAction.extend({

        contentTemplate: 'freightDashboard',

        renderElement: function (ev) {
            var self = this;
            $.when(this._super())
                .then(function (ev) {

                    // //loading Net Profit Total
                    // rpc.query({
                    //
                    //     model: "account.move",
                    //     method: 'search_read',
                    //     args: [[], []],
                    // }).then(function (result) {
                    //     var sale_count = 0;
                    //     var service_count = 0;
                    //     var sale_ser_total = 0;
                    //     var salePercentage = 0;
                    //     var servicePercentage = 0;
                    //     let total_profit = 0
                    //     result.map(t => {
                    //         if (t.move_type == 'out_invoice') {
                    //             total_profit += t.amount_total
                    //         }
                    //
                    //         if (!t.operation_id) {
                    //             sale_count += 1
                    //         } else {
                    //             service_count += 1
                    //         }
                    //
                    //         sale_ser_total = service_count + sale_count
                    //
                    //     })
                    //     salePercentage = (sale_count / sale_ser_total) * 100;
                    //     servicePercentage = (service_count / sale_ser_total) * 100;
                    //     $('#net_profit_value').empty().append(`${total_profit} ${result.length ? result[0].currency_id[1] : ''}`);
                    //     var chartProgressProfit = document.getElementById("net_profit_progress");
                    //     if (chartProgressProfit) {
                    //         var myChartCircle = new Chart(chartProgressProfit, {
                    //             type: 'doughnut',
                    //             data: {
                    //                 labels: ["From sales", "From services"],
                    //                 datasets: [{
                    //                     label: "Population (millions)",
                    //                     backgroundColor: ["#5283ff"],
                    //                     data: [salePercentage, servicePercentage]
                    //                 }]
                    //             },
                    //             plugins: [{
                    //                 beforeDraw: function (chart) {
                    //                     var width = chart.chart.width,
                    //                         height = chart.chart.height,
                    //                         ctx = chart.chart.ctx;
                    //
                    //                     ctx.restore();
                    //                     var text = salePercentage.toFixed(2) + "%",
                    //                         textX = Math.round((width - ctx.measureText(text).width) / 2),
                    //                         textY = height / 1.8;
                    //                     ctx.fillText(text, textX, textY);
                    //                     ctx.save();
                    //                 }
                    //             }],
                    //             options: {
                    //                 legend: {
                    //                     display: true,
                    //                 },
                    //                 responsive: false,
                    //                 maintainAspectRatio: true,
                    //                 cutoutPercentage: 60
                    //             }
                    //
                    //         });
                    //     }
                    // })
                    //
                    // //Loading Expense Total
                    // rpc.query({
                    //
                    //     model: "account.move",
                    //     method: 'search_read',
                    //     args: [[], []],
                    // }).then(function (result) {
                    //
                    //     let total_expense = 0
                    //     result.map(t => {
                    //         if (t.move_type == 'in_invoice') {
                    //             total_expense += t.amount_total
                    //         }
                    //     })
                    //
                    //
                    //     $('#cash_flow_value').empty().append(`${total_expense} ${result.length ? result[0].currency_id[1] : ''}`);
                    //
                    //     var chartProgressCash = document.getElementById("cash_flow_progress");
                    //     if (chartProgressCash) {
                    //         var myChartCircle = new Chart(chartProgressCash, {
                    //             type: 'doughnut',
                    //             data: {
                    //                 labels: ["Cash Flow"],
                    //                 datasets: [{
                    //                     label: "Population (millions)",
                    //                     backgroundColor: ["#5283ff"],
                    //                     data: [0, 100]
                    //                 }]
                    //             },
                    //             plugins: [{
                    //                 beforeDraw: function (chart) {
                    //                     var width = chart.chart.width,
                    //                         height = chart.chart.height,
                    //                         ctx = chart.chart.ctx;
                    //
                    //                     ctx.restore();
                    //                     var text = "0%",
                    //                         textX = Math.round((width - ctx.measureText(text).width) / 2),
                    //                         textY = height / 1.8;
                    //                     ctx.fillText(text, textX, textY);
                    //                     ctx.save();
                    //                 }
                    //             }],
                    //             options: {
                    //                 legend: {
                    //                     display: true,
                    //                 },
                    //                 responsive: false,
                    //                 maintainAspectRatio: true,
                    //                 cutoutPercentage: 60
                    //             }
                    //
                    //         });
                    //     }
                    // })
                    //
                    // //Loading Gross Margin
                    // rpc.query({
                    //
                    //     model: "account.move",
                    //     method: 'search_read',
                    //     args: [[], []],
                    // }).then(function (result) {
                    //
                    //     let total_expense = 0
                    //     let total_profit = 0
                    //     result.map(t => {
                    //         if (t.move_type == 'in_invoice') {
                    //             total_expense += t.amount_total
                    //         } else  if (t.move_type == 'out_invoice') {
                    //             total_profit += t.amount_total
                    //         }
                    //     })
                    //
                    //
                    //     $('#gross_margin_value').empty().append(`${(total_profit - total_expense).toFixed(2)} ${result.length ? result[0].currency_id[1] : ''}`);
                    //
                    //
                    // })

                    //loading total customers
                    rpc.query({

                        model: "res.partner",
                        method: 'search_read',
                        args: [[], []],
                    }).then(function (result) {

                        let total_customer = 0
                        let new_customer = 0
                        const current_date = new Date()
                        current_date.setMonth(current_date.getMonth() - 1)
                        let customers = result.filter(r => r.customer_rank > 0)
                        let newCustomers = customers.map(r => {
                                if (new Date(r.create_date.slice(0, 10)) < new Date(current_date.toISOString().slice(0, 10))) {
                                    return r
                                }
                            }
                        )


                        total_customer = customers.length
                        new_customer = newCustomers.length

                        let percentageNewCustomers = (new_customer * 100) / total_customer

                        $('#total_customers_value').empty().append(total_customer);
                        $('#new_customers_value').empty().append(new_customer);
                        $('#percentage_newCustomers').empty().append(`    
                                               <div class="progress-bar bg-success" role="progressbar" style="width: ${percentageNewCustomers}%"
                                               aria-valuenow="${percentageNewCustomers}" aria-valuemin="0"
                                               aria-valuemax="100">

                                          </div>`);


                    })

                    //loading TOTAL OPERATIONS
                    rpc.query({

                        model: "freight.operation",
                        method: 'search_read',
                        args: [[], []],
                    }).then(function (result) {
                        let total_opertions = result.length;

                        let not_invoiced = result.filter(r => r.invoicing_state != 'invoiced')
                        let not_invoiced_percentage = (not_invoiced.length * 100) / total_opertions

                        let data_template = `
                        <div class="progress-bar bg-warning" role="progressbar" style="width: ${not_invoiced_percentage}%"
                                               aria-valuenow="${not_invoiced_percentage}" aria-valuemin="0"
                                               aria-valuemax="100"></div>
                        
                        `
                        $('#operations_value').empty().append(total_opertions)
                        $('#not_invoiced_operations_value').empty().append(not_invoiced.length)
                        $('#not_invoiced_operations').empty().append(data_template)
                    })

                    //loading TOTAL Records
                    rpc.query({

                        model: "freight.folder",
                        method: 'search_read',
                        args: [[], []],
                    }).then(function (result) {
                        let total_folders = result.length;

                        let is_opened = result.filter(r => r.state == 'open')
                        let is_opened_percentage = (is_opened.length * 100) / total_folders

                        let data_template = `
                        <div class="progress-bar bg-primary" role="progressbar" style="width: ${is_opened_percentage}%"
                                               aria-valuenow="${is_opened_percentage}" aria-valuemin="0"
                                               aria-valuemax="100"></div>
                        
                        `
                        $('#folders_value').empty().append(total_folders)
                        $('#is_opened_folders').empty().append(data_template)
                        $('#is_opened_value').empty().append(is_opened.length)
                    })

                    //loading TOTAL offers
                    rpc.query({
                        model: "freight.offer",
                        method: 'search_read',
                        args: [[], []],
                    }).then(function (result) {
                        let total_offers = result.length;

                        let declined_offers = result.filter(r => r.state == 'cancel')
                        let declined_offers_percentage = (declined_offers.length * 100) / total_offers

                        let data_template = `
                         <div class="progress-bar bg-danger" role="progressbar" style="width: ${declined_offers_percentage}%"
                                               aria-valuenow="${declined_offers_percentage}" aria-valuemin="0"
                                               aria-valuemax="100">
                                          </div>
                        
                        `
                        $('#total_offers').empty().append(total_offers)
                        $('#declined_percentage').empty().append(data_template)
                        $('#declined_offers').empty().append(declined_offers.length)
                    })

                    //loading Top 10 services
                    rpc.query({
                        model: "product.product",
                        method: "search_read",
                        args: [[], []]
                    })
                        .then(function (result) {


                            result.sort((a, b) => (a.sales_count < b.sales_count) ? 1 : ((b.sales_count < a.sales_count) ? -1 : 0))

                            $('#top_10_customers_row').empty()
                            result.slice(0, 5).map(c => {
                                $('#top_10_services_row').append(
                                    `
                                        <tr>
                                        <td>${c.name}</td>
                                        <td>${c.sales_count} time${c.sales_count > 1 ? 's' : ''}</td>
                                        </tr>
                                   `
                                )
                            })
                            console.log(result)


                        })

                    //loading Top 10 customers
                    rpc.query({
                        model: "res.partner",
                        method: "search_read",
                        args: [[], []]
                    })
                        .then(function (result) {
                            let customers = result.filter(r => r.customer_rank > 0)

                            customers.sort((a, b) => (a.customer_rank < b.customer_rank) ? 1 : ((b.customer_rank < a.customer_rank) ? -1 : 0))

                            $('#top_10_customers_row').empty()
                            customers.slice(0, 5).map(c => {
                                $('#top_10_customers_row').append(
                                    `
                                        <tr>
                                        <td>${c.name}</td>
                                        <td>${c.credit} ${c.currency_id[1]}</td>
                                        </tr>
                                   `
                                )
                            })
                            console.log(customers)


                        })


                    // var chartProgressOverdue = document.getElementById("overdue_ratio_progress");
                    // if (chartProgressOverdue) {
                    //     var myChartCircle = new Chart(chartProgressOverdue, {
                    //         type: 'doughnut',
                    //         data: {
                    //             datasets: [{
                    //                 label: "Population (millions)",
                    //                 backgroundColor: ["#5283ff"],
                    //                 data: [100, 0]
                    //             }]
                    //         },
                    //         plugins: [{
                    //             beforeDraw: function (chart) {
                    //                 var width = chart.chart.width,
                    //                     height = chart.chart.height,
                    //                     ctx = chart.chart.ctx;
                    //
                    //                 ctx.restore();
                    //                 var text = "100%",
                    //                     textX = Math.round((width - ctx.measureText(text).width) / 2),
                    //                     textY = height / 1.8;
                    //                 ctx.fillText(text, textX, textY);
                    //                 ctx.save();
                    //             }
                    //         }],
                    //         options: {
                    //             legend: {
                    //                 display: true,
                    //             },
                    //             responsive: false,
                    //             maintainAspectRatio: true,
                    //             cutoutPercentage: 60
                    //         }
                    //
                    //     });
                    // }

                    // var chartBarPurchases = document.getElementById("purchase_bar_chart");
                    // if (chartBarPurchases) {
                    //     var myChartCircle = new Chart(chartBarPurchases, {
                    //         type: 'bar',
                    //         data: {
                    //             labels: ["1900", "1950", "1999", "2050"],
                    //             datasets: [
                    //
                    //                 {
                    //                     backgroundColor: "#ff6384",
                    //                     data: [133, 221, 783, 2478],
                    //                 },
                    //                 {
                    //                     backgroundColor: "#ff6384",
                    //                     data: [133, 221, 783, 2478],
                    //                 },
                    //                 {
                    //
                    //                     backgroundColor: "#ff6384",
                    //                     data: [408, 547, 675, 734],
                    //                 },
                    //                 {
                    //                     backgroundColor: "#ff6384",
                    //                     data: [408, 547, 675, 734],
                    //                 }
                    //
                    //             ]
                    //         },
                    //         options: {
                    //             title: {
                    //                 display: false,
                    //                 text: 'Population growth (millions): Europe & Africa'
                    //             },
                    //             legend: {display: false}
                    //         }
                    //     });
                    //
                    // }
                    //
                    // var chartBarSales = document.getElementById("sales_bar_chart");
                    // if (chartBarSales) {
                    //     var myChartCircle = new Chart(chartBarSales, {
                    //         type: 'bar',
                    //         data: {
                    //             labels: ["1900", "1950", "1999", "2050"],
                    //             datasets: [
                    //                 {
                    //                     backgroundColor: "#ff6384",
                    //                     data: [408, 547, 675, 734],
                    //                 },
                    //                 {
                    //                     backgroundColor: "#ff6384",
                    //                     data: [133, 221, 783, 2478],
                    //                 },
                    //                 {
                    //                     backgroundColor: "#ff6384",
                    //                     data: [408, 547, 675, 734],
                    //                 },
                    //                 {
                    //                     backgroundColor: "#ff6384",
                    //                     data: [133, 221, 783, 2478],
                    //                 }
                    //             ]
                    //         },
                    //         options: {
                    //             title: {
                    //                 display: false,
                    //                 text: 'Population growth (millions): Europe & Africa'
                    //             },
                    //             legend: {display: false}
                    //         }
                    //     });
                    //
                    // }

                });
        },

    });

    core.action_registry.add('freight_dashboard', ActionMenu);

});