#!/usr/bin/env python
from quickapp import QuickApp
from conf_tools.global_config import GlobalConfig
from quickapp.quick_app import quickapp_main
from mcdp_library.library import MCDPLibrary
from mocdp.dp_report.report import report_ndp1

class ExampleDrone1(QuickApp):

    """ Runs the sequence of examples with the drone / battery / payload """

    def define_options(self, params):
        pass

    def define_jobs_context(self, context):
        GlobalConfig.global_load_dir("mocdp")

        a = MCDPLibrary()

        dirs_models = [
            {'id': 'drone1', 'dir': 'models/drone1', 'model': 'drone'},
            {'id': 'drone2', 'dir': 'models/drone2', 'model': 'drone2_cost'},
            {'id': 'drone3', 'dir': 'models/drone3', 'model': 'drone3'},
        ]

        for x in dirs_models:
            dir = x['dir']
            id = x['id']
            model = x['model']

            a = a.add_search_dir(dir)
            _, ndp = a.load_ndp(model)
            r = context.comp(report_ndp1, ndp)
            context.add_report(r, 'report_ndp1', id_ndp=id)

def job_done():

    pass

if __name__ == '__main__':
    quickapp_main(ExampleDrone1)

