import xarray as xr
import numpy as np
import scipy.spatial

def interpolate_nearest_from_grid(ds_source, ds_target, field_names, x_name='x', y_name='y', source_crs=None, target_crs=None, target_gridded=False):
    """
    Interpolate a gridded field from ds_source to ungridded points in ds_target using nearest neighbor.

    Parameters:
        ds_source (xr.Dataset): Gridded source dataset
        ds_target (xr.Dataset): Ungridded target dataset with x/y coordinates
        field_names (str or list of str): Name of the variable(s) to interpolate from ds_source
        x_name (str): Name of x-coordinate in source datasets
        y_name (str): Name of y-coordinate in source datasets
        source_crs (pyproj.CRS): Coordinate reference system of the source dataset
        target_crs (pyproj.CRS): Coordinate reference system of the target dataset
        target_gridded (bool): If True, treat the x and y coordiantes of ds_target as axes and return a gridded dataset

    Returns:
        xr.DataArray: Interpolated field with same coords/dims as ds_target or a list of the same length as field_names
    """

    # Check if field_names is a list or a single string
    if isinstance(field_names, str):
        field_names = [field_names]

    # Extract gridded source coordinates and field
    X_src, Y_src = np.meshgrid(ds_source[x_name].values, ds_source[y_name].values)
    X_src, Y_src = X_src.ravel(), Y_src.ravel()
    if source_crs is not None:
        # Transform source coordinates to target CRS if needed
        coords_src = target_crs.transform_points(source_crs, X_src, Y_src) # TODO: Swapping Y and X here. Check to see if this is correct in general.
        X_src, Y_src = coords_src[:, 0], coords_src[:, 1]
        #print((np.min(X_src), np.max(X_src), np.min(Y_src), np.max(Y_src)))
    Z_src = [ds_source[fn].values for fn in field_names]

    # Flatten for KDTree
    source_points = np.column_stack((X_src, Y_src))
    source_values = [z.ravel() for z in Z_src]

    # Extract scattered target coordinates
    x_tgt = ds_target['x'].values
    y_tgt = ds_target['y'].values

    if target_gridded:
        x_mesh, y_mesh = np.meshgrid(x_tgt, y_tgt)
        
        x_tgt = x_mesh.ravel()
        y_tgt = y_mesh.ravel()
    
    target_points = np.column_stack((x_tgt, y_tgt))

    # Build KDTree and query nearest neighbors
    tree = scipy.spatial.KDTree(source_points)
    interpolated_values = []

    dists, idx = tree.query(target_points, k=1)
    for sv in source_values:
        # For each source variable, take the value at the nearest neighbor
        tmp = np.array(sv[idx])

        # If target is gridded, reshape to the original grid shape
        if target_gridded:
            tmp = tmp.reshape(x_mesh.shape)
        
        interpolated_values.append(tmp)

    # Convert to DataArray
    if target_gridded:
        interpolated_values_xr = [xr.DataArray(
                values,
                dims=['y', 'x'],
                coords={'x': ds_target.x, 'y': ds_target.y},
                name=fn
            ) for values, fn in zip(interpolated_values, field_names)
        ]
    else:
        interpolated_values_xr = [xr.DataArray(
                    values,
                    dims=['index'],
                    coords={'index': ds_target.index},
                    name=fn
                ) for values, fn in zip(interpolated_values, field_names)
            ]
    
    if len(interpolated_values_xr) == 1:
        return interpolated_values_xr[0]
    else:
        return interpolated_values_xr