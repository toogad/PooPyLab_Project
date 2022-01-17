from gui_utils import FlowchartInterface
from PooPyLab.utils import run

fci = FlowchartInterface()


def main():
    fn = './data/CMAS_example1.csv'
    flowchart = fci.read(fn)
    print(flowchart)
    wwtp = fci.construct_wwtp(flowchart)
    run.get_steady_state(wwtp,
                         target_SRT=10,
                         verbose=False,
                         diagnose=False,
                         mn='BDF',
                         fDO=True,
                         DOsat=10
                         )


if __name__ == '__main__':
    main()
