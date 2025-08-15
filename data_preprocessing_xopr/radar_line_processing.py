import xarray as xr
import numpy as np
import matplotlib
matplotlib.use('svg')
import matplotlib.pyplot as plt
# Configure matplotlib for better SVG editability
plt.rcParams['svg.fonttype'] = 'none'  # Embed fonts as text, not paths
import xopr.opr_access
import pandas as pd # For time types
import scipy.constants
import os
import zarr
import fsspec

def get_output_locations(flight_id : str, season_name : str, output_storage_location : str):
    """
    Build the output paths for processed radar line data
    Parameters:
    - flight_id: The ID of the flight being processed.
    - season_name: Name of the season (e.g., '2016_Antarctica_DC8').
    - output_storage_location: Path to store the processed radar line data, parsed by fsspec
    Returns:
    - A dictionary containing the output paths for the processed radar line data.
    """
    
    return {
        'zarr': os.path.join(output_storage_location, f"reflectivity_{season_name}_{flight_id}.zarr"),
        'summary_image': os.path.join(output_storage_location, f"reflectivity_{season_name}_{flight_id}.svg"),
    }

def cache_exists(flight_id : str, season_name : str,
                    output_storage_location : str, cache_revision_id : int = None):
    """
    Check if the processed radar line data already exists in the cache.
    
    Parameters:
    - flight_id: The ID of the flight being processed.
    - season_name: Name of the season (e.g., '2016_Antarctica_DC8').
    - output_storage_location: Path to store the processed radar line data, parsed by fsspec
    - cache_revision_id: Revision ID to check against existing cache files.
       If None, it will check for the existence of the file without considering the revision ID.

    Returns:
    - True if the processed data exists, False otherwise.
    """
    
    output_paths = get_output_locations(flight_id, season_name, output_storage_location)
    fs = fsspec.filesystem(fsspec.utils.infer_storage_options(output_paths['zarr'])['protocol'])
    file_exists = fs.exists(output_paths['zarr'])

    if cache_revision_id is not None:
        # Check if the file exists and has the correct revision ID
        if file_exists:
            zarr_store = zarr.open(output_paths['zarr'], mode='r')
            return zarr_store.attrs.get('revision_id', None) == cache_revision_id
        else:
            return False
    else:
        # Just check if the file exists
        return file_exists

def save_radar_summary_image(flight_line, reflectivity_dataset, layers, output_path):
    """
    Save a summary image of the processed radar line data.
    
    Parameters:
    - flight_line: xarray Dataset containing the original radar data.
    - reflectivity_dataset: xarray Dataset containing the processed reflectivity data.
    - layers: List of layer data from OPR.
    - output_path: Path where the summary image should be saved.
    """
    def plot_layer_line(ax, flight_line, layer, **kwargs):
        """
        Plot a layer line on the given axis.
        """
        layer_reindex = layer.reindex(slow_time=flight_line.slow_time, method='nearest', tolerance=pd.Timedelta(seconds=1), fill_value=np.nan)
        layer_reindex.plot(ax=ax, x='slow_time', **kwargs)
        

    # Get total time range in hours
    time_delta = pd.to_timedelta((reflectivity_dataset.slow_time.max() - reflectivity_dataset.slow_time.min()).item())
    total_time_range_hours = time_delta.total_seconds() / 3600
    # Create figure
    fig, (ax_radar, ax_pwr) = plt.subplots(2,1, figsize=(np.maximum(10, total_time_range_hours*10), 8), sharex=True, constrained_layout=True, dpi=500)

    pwr_dB = 10*np.log10(np.abs(flight_line.Data))
    pwr_dB.plot.imshow(x='slow_time', cmap='gray', ax=ax_radar)
    ax_radar.invert_yaxis()

    # Plot the layers
    plot_layer_line(ax_radar, flight_line, layers[1].twtt, c='C0', linestyle=':', alpha=0.5, linewidth=0.2, label='Surface')
    plot_layer_line(ax_radar, flight_line, reflectivity_dataset.surface_twtt, c='C0', linestyle='--', alpha=0.5, linewidth=0.5, label='Repicked Surface')
    plot_layer_line(ax_radar, flight_line, layers[2].twtt, c='C1', linestyle=':', alpha=0.5, linewidth=0.2, label='Bed')
    plot_layer_line(ax_radar, flight_line, reflectivity_dataset.bed_twtt, c='C1', linestyle='--', alpha=0.5, linewidth=0.5, label='Repicked Bed')

    # Find good y limits
    y_min = min(reflectivity_dataset.surface_twtt.min(), reflectivity_dataset.bed_twtt.min()) * 0.9
    y_max = max(reflectivity_dataset.surface_twtt.max(), reflectivity_dataset.bed_twtt.max()) * 1.1

    ax_radar.set_ylim(y_max, y_min)
    ax_radar.legend()

    reflectivity_dataset.surface_power_dB.plot.scatter(ax=ax_pwr, x='slow_time', label='Surface Power', s=5, edgecolors='none')
    reflectivity_dataset.bed_power_dB.plot.scatter(ax=ax_pwr, x='slow_time', label='Bed Power', s=5, edgecolors='none')

    ax_pwr.legend()
    ax_pwr.grid()

    # Save figure with SVG-optimized settings for editability
    fig.savefig(output_path, 
                format='svg',
                dpi=100,  # Lower DPI for SVG since it's vector-based
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none')
    plt.close(fig)


def grid_dataarray(dataarray, grid_size=1000, aggregation_funcs=None):
    """
    Grid unstructured DataArray onto a regular grid using specified aggregation functions.
    Memory-efficient implementation that processes one grid cell at a time.
    
    Parameters:
    - dataarray: xarray DataArray with 'x' and 'y' coordinates and values to grid
    - grid_size: Size of grid cells in meters (default: 1000m)
    - aggregation_funcs: List of aggregation functions to apply (default: [np.mean])
                        Can include functions like np.mean, np.std, np.count_nonzero, etc.
    
    Returns:
    - gridded_data: xarray Dataset with variables for each aggregation function applied
    """
    if aggregation_funcs is None:
        aggregation_funcs = [np.mean]
    
    # Define grid bounds using xarray operations
    x_min = np.floor(dataarray.x.min().item() / grid_size) * grid_size
    x_max = np.ceil(dataarray.x.max().item() / grid_size) * grid_size
    y_min = np.floor(dataarray.y.min().item() / grid_size) * grid_size
    y_max = np.ceil(dataarray.y.max().item() / grid_size) * grid_size
    
    # Create grid arrays
    x_grid = np.arange(x_min, x_max + grid_size, grid_size)
    y_grid = np.arange(y_min, y_max + grid_size, grid_size)
    
    # Create grid center coordinates
    x_centers = x_grid[:-1] + grid_size / 2
    y_centers = y_grid[:-1] + grid_size / 2
    
    # Initialize output arrays for each aggregation function
    gridded_results = {}
    for func in aggregation_funcs:
        func_name = func.__name__ if hasattr(func, '__name__') else str(func)
        gridded_results[func_name] = np.full((len(y_centers), len(x_centers)), np.nan)
    
    # Process each grid cell
    for i, x_center in enumerate(x_centers):
        for j, y_center in enumerate(y_centers):
            # Define cell boundaries
            x_left = x_center - grid_size / 2
            x_right = x_center + grid_size / 2
            y_bottom = y_center - grid_size / 2
            y_top = y_center + grid_size / 2
            
            # Query data within this grid cell using xarray
            cell_data = dataarray.where(
                (dataarray.x >= x_left) & (dataarray.x < x_right) &
                (dataarray.y >= y_bottom) & (dataarray.y < y_top),
                drop=True
            )
            
            # Skip if no data in this cell
            if cell_data.size == 0:
                continue
                
            # Apply aggregation functions
            for func in aggregation_funcs:
                func_name = func.__name__ if hasattr(func, '__name__') else str(func)
                try:
                    if func_name == 'count_nonzero':
                        result = np.count_nonzero(~np.isnan(cell_data.values))
                    else:
                        result = func(cell_data.values[~np.isnan(cell_data.values)])
                    gridded_results[func_name][j, i] = result
                except:
                    gridded_results[func_name][j, i] = np.nan
    
    # Create Dataset with results from each aggregation function
    data_vars = {}
    for func in aggregation_funcs:
        func_name = func.__name__ if hasattr(func, '__name__') else str(func)
        var_name = f"{dataarray.name}_{func_name}" if dataarray.name else func_name
        data_vars[var_name] = (('y', 'x'), gridded_results[func_name])
    
    gridded_dataset = xr.Dataset(
        data_vars,
        coords={'y': y_centers, 'x': x_centers},
        attrs=dataarray.attrs
    )
    
    return gridded_dataset


def process_radar_line(flight_id : list, season_name : str, output_storage_location : str, parameters : dict = {},
                       save_summary_image: bool = True, return_dataset: bool = True,
                       opr_connection : xopr.opr_access.OPRConnection = None):
    """
    Load and process a radar line from a list of URLs representing radar frame data files.
    
    Parameters:
    - flight_ids: List of flight IDs corresponding to the radar frames.
    - season_name: Name of the season (e.g., '2016_Antarctica_DC8').
    - output_storage_location: Path to store the processed radar line data, parsed by fsspec
    - parameters: Dictionary of (optional) processing parameters.
       Defaults are:
         {
            'layer_selection_margin_m': 30,  # meters
            'ice_relative_permittivity': 3.17,  # Relative permittivity of ice
            'downsample_interval_s': 1,  # Rolling window for downsampling, in seconds
         }
    - save_summary_image: Boolean indicating whether to save a summary image of the processed radar line.
    - return_dataset: Boolean indicating whether to return the processed dataset.
    - opr_connection: An instance of OPRConnection to manage OPR sessions and data access. 
       If None, a new OPRConnection will be created with no caching.
    Returns:
    - If return_dataset is True, returns an xarray Dataset containing the processed radar line data.
    - If return_dataset is False, returns the path to the output storage location where the processed data is saved.

    """

    default_parameters = {
        'layer_selection_margin_m': 30,  # meters
        'ice_relative_permittivity': 3.17,  # Relative permittivity of ice
        'downsample_interval_s': 1,  # Rolling window for downsampling, in seconds
    }

    # Update default parameters with any user-provided parameters
    parameters = {**default_parameters, **parameters}

    output_paths = get_output_locations(flight_id, season_name, output_storage_location)

    if opr_connection:
        # Use the provided OPRConnection instance
        opr = opr_connection
    else:
        # Create a new OPRConnection instance with no caching
        opr = xopr.opr_access.OPRConnection()

    print(f"Processing flight line: {flight_id} for season: {season_name}")
    
    # Load the radar frames from the provided URLs
    frames = opr.load_flight(season_name, flight_id=flight_id)
    flight_line = xr.concat(frames, dim='slow_time', combine_attrs='drop_conflicts')

    # Downsample by stacking to 1 second intervals
    flight_line = flight_line.resample(slow_time=f"{parameters['downsample_interval_s']}s").mean()

    # Fetch layer data from OPS
    layers = None
    try:
        layers = opr.get_layers_db(flight_line)  # Fetch layers from the database
        layers[1] # Display the surface layer as an example
    except Exception as e:
        print(f"Error fetching layers: {e}")
        print("Trying to load layers from file instead...")

        layers = opr.get_layers_files(flight_line)
    
    # Re-pick surface and bed layers to ensure we're getting the peaks
    speed_of_light_in_ice = scipy.constants.c / np.sqrt(parameters['ice_relative_permittivity'])  # Speed of light in ice (m/s)
    layer_selection_margin_twtt = parameters['layer_selection_margin_m'] / speed_of_light_in_ice # approx 50 m margin in ice
    surface_repicked_twtt, surface_power = extract_layer_peak_power(flight_line, layers[1]['twtt'], layer_selection_margin_twtt)
    bed_repicked_twtt, bed_power = extract_layer_peak_power(flight_line, layers[2]['twtt'], layer_selection_margin_twtt)

    # Create a dataset from surface_repicked_twtt, bed_repicked_twtt, surface_power, and bed_power

    reflectivity_dataset = xr.merge([
        surface_repicked_twtt.rename('surface_twtt'),
        bed_repicked_twtt.rename('bed_twtt'),
        surface_power.rename('surface_power_dB'),
        bed_power.rename('bed_power_dB'),
        ])

    flight_line_metadata = flight_line.drop_vars(['Data', 'Surface', 'Bottom'])
    reflectivity_dataset = xr.merge([reflectivity_dataset, flight_line_metadata])

    reflectivity_dataset = reflectivity_dataset.drop_dims(['twtt'])  # Remove the twtt dimension since everything has been flattened

    attributes_to_copy = ['season', 'segment', 'doi', 'ror', 'funder_text']
    reflectivity_dataset.attrs = {attr: flight_line.attrs[attr] for attr in attributes_to_copy if attr in flight_line.attrs}

    reflectivity_dataset.attrs['source_urls'] = [frame.attrs.get('source_url', '') for frame in frames]

    # Add cache revision ID to the dataset attributes
    if 'cache_revision_id' in parameters:
        reflectivity_dataset.attrs['revision_id'] = parameters['cache_revision_id']

    reflectivity_dataset.to_zarr(output_paths['zarr'], mode='w')

    if save_summary_image:
        save_radar_summary_image(flight_line, reflectivity_dataset, layers, output_paths['summary_image'])
    
    if return_dataset:
        return reflectivity_dataset
    else:
        return output_paths['zarr']


def extract_layer_peak_power(radar_ds, layer_twtt, margin_twtt):
    """
    Extract the peak power of a radar layer within a specified margin around the layer's two-way travel time (TWTT).

    Parameters:
    - radar_ds: xarray Dataset containing radar data.
    - layer_twtt: The two-way travel time of the layer to extract.
    - margin_twtt: The margin around the layer's TWTT to consider for peak power extraction.

    Returns:
    - A DataArray containing the peak power values for the specified layer.
    """
    
    # Ensure that layer_twtt.slow_time matches the radar_ds slow_time
    t_start = np.minimum(radar_ds.slow_time.min(), layer_twtt.slow_time.min())
    t_end = np.maximum(radar_ds.slow_time.max(), layer_twtt.slow_time.max())
    layer_twtt = layer_twtt.sel(slow_time=slice(t_start, t_end))
    radar_ds = radar_ds.sel(slow_time=slice(t_start, t_end))
    #layer_twtt = layer_twtt.interp(slow_time=radar_ds.slow_time, method='nearest')
    layer_twtt = layer_twtt.reindex(slow_time=radar_ds.slow_time, method='nearest', tolerance=pd.Timedelta(seconds=1), fill_value=np.nan)
    
    # Calculate the start and end TWTT for the margin
    start_twtt = layer_twtt - margin_twtt
    end_twtt = layer_twtt + margin_twtt
    
    # Extract the data within the specified TWTT range
    data_within_margin = radar_ds.where((radar_ds.twtt >= start_twtt) & (radar_ds.twtt <= end_twtt), drop=True)

    power_dB = 10 * np.log10(np.abs(data_within_margin.Data))

    # Find the twtt index corresponding to the peak power
    peak_twtt_index = power_dB.argmax(dim='twtt')
    # Convert the index to the actual TWTT value
    peak_twtt = power_dB.twtt[peak_twtt_index]

    # Calculate the peak power in dB
    peak_power = power_dB.isel(twtt=peak_twtt_index)

    # Remove unnecessary dimensions
    peak_twtt = peak_twtt.drop_vars('twtt')
    peak_power = peak_power.drop_vars('twtt')
    
    return peak_twtt, peak_power