import dask
from dask.distributed import LocalCluster
from dask.distributed import as_completed
import traceback
from radar_line_processing import process_radar_line


if __name__ == "__main__":

    client = LocalCluster().get_client()

    flight_line_urls = [
        [f'https://data.cresis.ku.edu/data/rds/2016_Antarctica_DC8/CSARP_standard/20161026_05/Data_20161026_05_{i:03d}.mat' for i in range(1, 43)], #range(1, 43)
        [f'https://data.cresis.ku.edu/data/rds/2016_Antarctica_DC8/CSARP_standard/20161028_04/Data_20161028_04_{i:03d}.mat' for i in range(1, 35)], #range(1, 35)
        [f'https://data.cresis.ku.edu/data/rds/2016_Antarctica_DC8/CSARP_standard/20161028_05/Data_20161028_05_{i:03d}.mat' for i in range(1, 11)], #range(1, 11)
    ]

    output_storage_location = "tmp"

    kwargs = {
        'output_storage_location': output_storage_location,
        'parameters': {
            'layer_selection_margin_m': 30,  # meters
            'ice_relative_permittivity': 3.17,  # Relative permittivity of ice
            'downsample_interval_s': 1,  # Rolling window for downsampling, in seconds
        },
    }

    futures = client.map(
        process_radar_line,
        flight_line_urls,
        **kwargs)

    # Process results as they complete, capturing exceptions
    results = []
    for future in as_completed(futures):
        try:
            result = future.result()
            results.append(('success', result))
        except Exception as e:
            results.append(('error', e, traceback.format_exc()))
