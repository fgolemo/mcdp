from mocdp.dp_report.report import report_dp1, report_ndp1
from mocdp.unittests.generation import for_all_dps_dyn, for_all_nameddps_dyn

@for_all_dps_dyn
def dp1_report(context, _id_dp, dp):
    r = context.comp(report_dp1, dp)
    context.add_report(r, 'dp1')


@for_all_nameddps_dyn
def ndp1_report(context, _id_dp, ndp):
    r = context.comp(report_ndp1, ndp)
    context.add_report(r, 'ndp1')

