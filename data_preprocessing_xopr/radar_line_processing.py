import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import xopr.opr_access
import pandas as pd # For time types
import scipy.constants
import os
import zarr

def process_radar_line(urls : list, output_storage_location : str, parameters : dict = {},
                       save_summary_image: bool = True, return_dataset: bool = True,
                       opr_connection : xopr.opr_access.OPRConnection = None):
    """
    Load and process a radar line from a list of URLs representing radar frame data files.
    
    Parameters:
    - urls: List of URLs pointing to radar frame data files.
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

    if opr_connection:
        # Use the provided OPRConnection instance
        opr = opr_connection
    else:
        # Create a new OPRConnection instance with no caching
        opr = xopr.opr_access.OPRConnection()
    
    # Load the radar frames from the provided URLs
    frames = [opr.load_frame(url) for url in urls]
    flight_line = xr.concat(frames, dim='slow_time', combine_attrs='drop_conflicts')

    # Downsample by stacking to 1 second intervals
    flight_line = flight_line.resample(slow_time=f"{parameters['downsample_interval_s']}s").mean()

    # Fetch layer data from OPS
    layers = xopr.opr_access.get_layers(flight_line)
    
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

    attributes_to_copy = ['season', 'segment', 'doi', 'ror', 'funder_text']
    reflectivity_dataset.attrs = {attr: flight_line.attrs[attr] for attr in attributes_to_copy if attr in flight_line.attrs}

    reflectivity_dataset.attrs['source_urls'] = urls

    output_path = os.path.join(output_storage_location, f"reflectivity_{reflectivity_dataset.attrs['season']}_{reflectivity_dataset.attrs['segment']}.zarr.zip")
    with zarr.storage.ZipStore(output_path, mode='w') as store:
        reflectivity_dataset.to_zarr(store)

    if save_summary_image:
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
        plot_layer_line(ax_radar, flight_line, surface_repicked_twtt, c='C0', linestyle='--', alpha=0.5, linewidth=0.5, label='Repicked Surface')
        plot_layer_line(ax_radar, flight_line, layers[2].twtt, c='C1', linestyle=':', alpha=0.5, linewidth=0.2, label='Bed')
        plot_layer_line(ax_radar, flight_line, bed_repicked_twtt, c='C1', linestyle='--', alpha=0.5, linewidth=0.5, label='Repicked Bed')

        # Find good y limits
        y_min = min(surface_repicked_twtt.min(), bed_repicked_twtt.min()) * 0.9
        y_max = max(surface_repicked_twtt.max(), bed_repicked_twtt.max()) * 1.1

        ax_radar.set_ylim(y_max, y_min)
        ax_radar.legend()

        surface_power.plot.scatter(ax=ax_pwr, x='slow_time', label='Surface Power', s=5, edgecolors='none')
        bed_power.plot.scatter(ax=ax_pwr, x='slow_time', label='Bed Power', s=5, edgecolors='none')

        ax_pwr.legend()
        ax_pwr.grid()

        # Save figure
        summary_image_path = os.path.join(output_storage_location, f"reflectivity_{reflectivity_dataset.attrs['season']}_{reflectivity_dataset.attrs['segment']}.png")
        fig.savefig(summary_image_path, dpi=500)
        plt.close(fig)
    
    if return_dataset:
        return reflectivity_dataset
    else:
        return output_path


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