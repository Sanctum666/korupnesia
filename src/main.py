import dispatcher
from pathlib import Path


def main():
    datapath = Path(f"{Path(__file__).parent.parent}/data")
    datachunk = dispatcher.get_data_chunk(datapath)
    if not datachunk:
        return
    dispatcher.batch_process(datachunk)


main()
