import csv
from typing import List
from PooPyLab.unit_procs.streams import splitter, pipe, WAS
from PooPyLab.unit_procs.streams import influent, effluent
from PooPyLab.unit_procs.bio import asm_reactor
from PooPyLab.unit_procs.physchem import final_clarifier
from PooPyLab.utils import pfd


def instantiate_one_component(component: dict):
    component_type = component.get('Type', '')
    if component_type == 'influent':
        return_obj = influent()
    elif component_type == 'asm_reactor':
        return_obj = asm_reactor()
    elif component_type in ['pipe', 'ras']:
        return_obj = pipe()
    elif component_type == 'splitter':
        return_obj = splitter()
    elif component_type == 'effluent':
        return_obj = effluent()
    elif component_type == 'waste':
        return_obj = WAS()
    elif component_type == 'final_clarifier':
        return_obj = final_clarifier()
    else:
        print(f"Object type not found: {component_type}")
        return_obj = None

    component.update(
        {'object': return_obj}
    )
    return component


def get_component_by_id(wwtp: List[dict], id_value: int) -> dict:
    return next(item for item in wwtp if item['Id'] == id_value)


class FlowchartInterface(object):
    """

    """
    @staticmethod
    def read(filename: str) -> List[dict]:
        flowchart_list = []
        with open(filename, newline='') as fh:
            reader = csv.reader(fh)
            header_row = next(reader)

            for row in reader:
                flowchart_list.append(
                    dict(zip(header_row, row))
                )

        return flowchart_list

    @staticmethod
    def construct_wwtp(flowchart: List[dict]):
        """

        """
        wwtp = []
        for i in range(0, len(flowchart)):
            component = instantiate_one_component(flowchart[i])
            wwtp.append(component)

        for i in range(0, len(flowchart)):
            if flowchart[i]['Pipe_Dest_Main']:
                tmp_obj = get_component_by_id(wwtp, flowchart[i]['Id'])['object']
                tmp_obj.set_downstream_main(
                    get_component_by_id(wwtp, flowchart[i]['Pipe_Dest_Main'])['object']
                )

            if flowchart[i]['Pipe_Dest_Side']:
                tmp_obj = get_component_by_id(wwtp, flowchart[i]['Id'])['object']
                tmp_obj.set_downstream_side(
                    get_component_by_id(wwtp, flowchart[i]['Pipe_Dest_Side'])['object']
                )

        # set splitter sidestream
        # TODO: This is a temparary solution. Needs update later.
        for component in wwtp:
            if component['Type'] == 'splitter':
                component['object'].set_as_SRT_controller(True)
                component['object'].set_mainstream_flow(37800)

        wwtp_objects = [i['object'] for i in wwtp]

        pfd.check(wwtp_objects)

        return wwtp_objects




