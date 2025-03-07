"""The “plot” module offers simple shortcuts to pyGplates functionalities for reconstructing geological features,
transforming them into Shapely geometries and plotting them onto maps.

Methods in this module perform a combination of reconstructing topological features, generating and sorting through 
valid Shapely geometries, and plotting them. Some methods conduct all the steps above, while others only accept 
reconstructed features as parameters. The methods that reconstruct geometries using pyGplates before plotting include:
    * add_coastlines
    * add_continents
    * add_ridges
The features to reconstruct must be defined above where these methods are called under the variable names ‘coastlines’,
‘continents’ and ‘topology_features’ respectively. 

The methods that assume geometries are reconstructed already are:
    * another version of add_ridges
    * add_trenches
For both methods, reconstructed ridges and topologies are assumed to be defined in the specific shapefile paths:
    * "reconstructed_topologies/ridge_transform_boundaries_{reconstruction_time}Ma.shp"
    * "reconstructed_topologies/subduction_boundaries_{reconstruction_time}Ma.shp"
    * "reconstructed_topologies/subduction_boundaries_sL_{reconstruction_time}Ma.shp"
    * "reconstructed_topologies/subduction_boundaries_sR_{reconstruction_time}Ma.shp"
for a specific reconstruction_time. For example, reconstructed ridges at 40Ma should be contained in the path:
reconstructed_topologies/ridge_transform_boundaries_40Ma.shp

add_quiver calculates and plots plate motion velocity vectors, executing Plate Tectonic Tools’ velocity vector
functionalities in a single line. A rotation model and topology feature must be defined above this method as 
“rotation_model” and “topology_features” respectively (if using GPlately, these would be held in the
PlateReconstruction object).

shapelify_feature_lines and shapelify_feature_polygons turn reconstructed features into Shapely geometries for plotting. 

In the PlotTopologies class, 
    * plot_coastlines
    * plot_continents
    * Plot_continent_ocean_boundaries
are plotting methods that use shapefile strings given to the PlotTopologies object. Moreover,
    * plot_ridges
    * plot_ridges_and_transforms
    * plot_transforms
    * plot_trenches
    * plot_subduction_teeth
are plotting methods that use the PlotTopologies feature attributes: self.topologies, self.ridge_transforms,
self.ridges, self.transforms, self.trenches, self.trench_left, self.trench_right and self.other. These features
have been resolved using Plate Tectonics Tools’ ptt.resolve_topologies.resolve_topologies_into_features method. 

The following methods:
    *plot_grid
    *plot_grid_from_netCDF
plot ndarray-like and netCDF grids respectively onto maps. The latter method uses GPlately’s grids module to
extract a grid from a given netCDF file path.

The method ‘plot_plate_motion_vectors’ constructs and plots plate motion velocity vectors using Plate Tectonics Tools functionalities. 

Classes
-------
PlotTopologies
"""
import ptt
import numpy as np
import matplotlib.pyplot as plt
import pygplates

def get_valid_geometries(shape_filename):
    """Reads a shapefile of feature geometries and obtains only valid geometries.

    Parameters
    ----------
    shape_filename : str
        Path to a filename for a shape file of feature geometries

    Returns
    -------
    geometries : ndarray 
        Valid shapely polygons that define the feature geometry held in the shape file. Can be plotted directly using
        add_geometries.
    """
    import cartopy.io.shapereader as shpreader
    shp_geom = shpreader.Reader(shape_filename).geometries()
    geometries = []
    for record in shp_geom:
        geometries.append(record.buffer(0.0))
    return geometries
    
def add_coastlines(ax, reconstruction_time, **kwargs):
    """Reconstructs coastline geometries and plots them onto a standard map. 

    The coastlines for plotting must be defined in a variable "coastlines" above the method, along with a "rotation_model".
    "coastlines" should be a feature collection, or filename, or feature, or sequence of features, 
    or a list or tuple of any combination of those four types. These coastlines are reconstructed, transformed into shapely
    geometries and added onto the chosen map. Map presentation details (e.g. facecolor, edgecolor, alpha…) permitted.

    Parameters
    ----------
    ax : GeoAxis
        A standard map for lat-lon data built on a matplotlib figure. Can be for a single plot or for multiple subplots. 
        Should be set at a particular Cartopy map projection.

    reconstruction_time : float
        A particular geological time (Ma) at which to reconstruct the feature coastlines. 

    **export_wrap_to_dateline : bool, default=True
        Wrap/clip reconstructed geometries to the dateline.

    **kwargs 
        Keyword arguments that allow control over parameters such as ‘facecolor’, ‘alpha’, etc. for plotting coastline 
        geometries.

    Returns
    -------
    ax : GeoAxis
        The map with coastline features plotted onto the chosen projection. 
    """
    # write shapefile
    reconstructed_coastlines = []
    pygplates.reconstruct(coastlines, rotation_model, reconstructed_coastlines, float(reconstruction_time),
                          export_wrap_to_dateline=True)
    coastlines_geometries = shapelify_feature_polygons(reconstructed_coastlines)
    
    ax.add_geometries(coastlines_geometries, crs=ccrs.PlateCarree(), **kwargs)
    
def add_continents(ax, reconstruction_time, **kwargs):
    """Reconstructs continental geometries and plots them onto a standard map. 

    The continents for plotting must be defined in a variable "continents" above the method, along with a "rotation_model".
    "continents" should be a feature collection, or filename, or feature, or sequence of features, or a list or tuple 
    of any combination of those four types. These coastlines are reconstructed, transformed into shapely
    geometries and added onto the chosen map. Map presentation details (e.g. facecolor, edgecolor, alpha…) permitted.

    Parameters
    ----------
    ax : GeoAxis
        A standard map for lat-lon data built on a matplotlib figure. Can be for a single plot or for multiple subplots. 
        Should be set at a particular Cartopy map projection.

    reconstruction_time : float
        A particular geological time (Ma) at which to reconstruct the feature continents. 

    **export_wrap_to_dateline : bool, default=True
        Wrap/clip reconstructed geometries to the dateline.

    **kwargs 
        Keyword arguments that allow control over parameters such as ‘facecolor’, ‘alpha’, etc. for plotting continental
        geometries.

    Returns
    -------
    ax : GeoAxis
        The map with continental features plotted onto the chosen projection. 
    """
    reconstructed_continents = []
    pygplates.reconstruct(continents, rotation_model, reconstructed_continents, float(reconstruction_time),
                          export_wrap_to_dateline=True)
    continent_geometries = shapelify_feature_polygons(reconstructed_continents)
    
    ax.add_geometries(continent_geometries, crs=ccrs.PlateCarree(), **kwargs)
    
def add_ridges(ax, reconstruction_time, **kwargs):
    """Reconstructs ridge features to a specific geological time, converts them into shapely geometries and plots them 
    onto a standard map.
    
    The ridges for plotting must be defined in a variable "topology_features" above the method, along with a "rotation_model".
    "topology_features" must be a feature collection, or filename, or feature, or sequence of features, 
    or a list or tuple of any combination of those four types. Map presentation details (e.g. facecolor, edgecolor, alpha…)
    permitted.

    Exterior coordinates are ordered anti-clockwise and only valid geometries are passed to ensure compatibility with Cartopy.

    Parameters
    ----------
    ax : GeoAxis
        A standard map for lat-lon data built on a matplotlib figure. Can be for a single plot or for multiple subplots. 
        Should be set at a particular Cartopy map projection.

    reconstruction_time : float
        A particular geological time (Ma) at which to reconstruct the feature ridges. 

    **kwargs 
        Keyword arguments that allow control over parameters such as ‘facecolor’, ‘alpha’, etc. for plotting ridge geometries.

    Returns
    -------
    ax
        The map with ridge features plotted onto the chosen projection. 

    """
    import shapely
    reconstructed_ridges = get_ridge_transforms(topology_features, rotation_model, float(reconstruction_time))
    all_geometries = []
    for feature in reconstructed_ridges:
        geometry = feature.get_all_geometries()[0].to_lat_lon_array()[::-1,::-1]
        
        # construct shapely geometry
        geom = shapely.geometry.LineString(geometry)

        # we need to make sure the exterior coordinates are ordered anti-clockwise
        # and the geometry is valid otherwise it will screw with cartopy
        if geom.is_valid:
            all_geometries.append(geom)
    
    ax.add_geometries(all_geometries, crs=ccrs.PlateCarree(), **kwargs)
    
def add_ridges(ax, reconstruction_time, **kwargs):
    """Reads a shapefile containing reconstructed ridge features. Plots them onto a standard map.

    Ridge features to be plotted must be reconstructed to a specific geological time already. These are assumed to be 
    held in the filename string
    "reconstructed_topologies/ridge_transform_boundaries_{reconstruction_time}Ma.shp" for each reconstruction time. This
    shape filename is read and its ridge geometries are extracted, turned into shapely geometries, and plotted onto the 
    given map.

    Parameters
    ----------
    ax : GeoAxis
        A standard map for lat-lon data built on a matplotlib figure. Can be for a single plot or for multiple subplots.
        Should be set at a particular Cartopy map projection.

    reconstruction_time : float
        A particular geological time (Ma) at which to reconstruct the feature ridges. 

    **kwargs 
        Keyword arguments that allow control over parameters such as ‘facecolor’, ‘alpha’, etc. for plotting ridge 
        geometries.

    Returns
    -------
    ax : GeoAxis
        The map with ridge features plotted onto the chosen projection.
    """
    shp_name = "reconstructed_topologies/ridge_transform_boundaries_{:.2f}Ma.shp".format(reconstruction_time)
    shp_continents = shpreader.Reader(shp_name).geometries()
    ft_continents  = cfeature.ShapelyFeature(shp_continents, ccrs.PlateCarree())
    ax.add_feature(ft_continents, **kwargs)

def add_trenches(ax, reconstruction_time, color='k', linewidth=2, **kwargs):
    """Reads 3 shapefile containing reconstructed subduction boundaries, left subduction trenches and right subduction
    trenches. Generates subduction teeth along these boundaries and plots both subduction zones and teeth onto a standard map.

    The subduction boundary features to be plotted should be reconstructed to a specific geological time already. They are
    assumed to be held in the filename string "reconstructed_topologies/subduction_boundaries_{reconstruction_time}Ma.shp"
    for a specific reconstruction time. 
    
    The left subduction features are assumed to be held in the filename string: 
    "reconstructed_topologies/subduction_boundaries_sL_{reconstruction_time}Ma.shp", while the right subduction features are
    assumed to be held in the filename string: "reconstructed_topologies/subduction_boundaries_sR_{reconstruction_time}Ma.shp".
    These left and right features are tessellated into subduction teeth. 

    Parameters
    ----------
    ax : GeoAxis
        A standard map for lat-lon data built on a matplotlib figure. Can be for a single plot or for multiple subplots.
        Should be set at a particular Cartopy map projection.

    reconstruction_time : float
        A particular geological time (Ma) at which to reconstruct the feature ridges.

    color : str, default='k'
        Sets the subduction boundaries to a specific edge color.

    linewidth : float, default=2
        Defines the thickness of the subduction boundaries 

    **kwargs 
        Keyword arguments that allow control over map features like ‘alpha’, etc. for plotting trench geometries.

    Returns
    -------
    ax : GeoAxis
        The map with subduction boundary features & subduction teeth plotted onto the chosen projection.
    """
    shp_name = "reconstructed_topologies/subduction_boundaries_{:.2f}Ma.shp".format(reconstruction_time)
    shp_subd = shpreader.Reader(shp_name).geometries()
    ft_subd  = cfeature.ShapelyFeature(shp_subd, ccrs.PlateCarree())
    ax.add_feature(ft_subd, facecolor='none', edgecolor=color, linewidth=linewidth, zorder=5)
    # add Subduction Teeth
    subd_xL, subd_yL = tesselate_triangles(
        "reconstructed_topologies/subduction_boundaries_sL_{:.2f}Ma.shp".format(reconstruction_time),
        tesselation_radians=0.1, triangle_base_length=2.0, triangle_aspect=-1.0)
    subd_xR, subd_yR = tesselate_triangles(
        "reconstructed_topologies/subduction_boundaries_sR_{:.2f}Ma.shp".format(reconstruction_time),
        tesselation_radians=0.1, triangle_base_length=2.0, triangle_aspect=1.0)
    
    for tX, tY in zip(subd_xL, subd_yL):
        triangle_xy_points = np.c_[tX, tY]
        patch = plt.Polygon(triangle_xy_points, color=color, transform=ccrs.PlateCarree(), zorder=6)
        ax.add_patch(patch)
    for tX, tY in zip(subd_xR, subd_yR):
        triangle_xy_points = np.c_[tX, tY]
        patch = plt.Polygon(triangle_xy_points, color=color, transform=ccrs.PlateCarree(), zorder=6)
        ax.add_patch(patch)
    
    
def add_quiver(ax, reconstruction_time, **kwargs):
    """Calculates velocity data for a specific reconstruction time and plots velocity vectors onto a map. 

    A rotation model and topology feature must be defined above this method as “rotation_model” and “topology_features”
    respectively. These are used to generate velocity domain feature points. Velocities at each domain point are calculated
    for a specific geological time. X and Y nodes (coordinates of domain points) and u and v components of velocity are
    generated to plot velocity vectors onto the given map. Velocity magnitudes are not normalised. 

    Parameters
    -----------
    ax : GeoAxis
        A standard map for lat-lon data built on a matplotlib figure. Can be for a single plot or for multiple subplots.
        Should be set at a particular Cartopy map projection.

    reconstruction_time : float
        A particular geological time (Ma) at which to reconstruct the feature ridges.

    **kwargs 
        Keyword arguments that allow control over quiver features like ‘alpha’, etc. for velocity vectors.

    Returns
    -------
    ax : GeoAxis
        The map with velocity vectors plotted onto the chosen projection.
    """
    Xnodes, Ynodes, U, V = ptt.velocity_tools.get_velocity_x_y_u_v(reconstruction_time, rotation_model,
                                                                   topology_features)
    mag = np.hypot(U, V)
#     mag = np.clip(mag, 1.0, 1e99)
#     mag[mag==0] = 1 #to avoid 0 divisor
#     U = U/mag
#     V = V/mag
    
    if mag.any():
        ax.quiver(Xnodes, Ynodes, U, V, transform=ccrs.PlateCarree(), **kwargs)



# subduction teeth
def tesselate_triangles(shapefilename, tesselation_radians, triangle_base_length, triangle_aspect=1.0):
    """Places subduction teeth along subduction boundary line segments within a MultiLineString shapefile. 

    Parameters
    ----------
    shapefilename  : str  
       Path to shapefile containing the reconstructed subduction boundary features.

    tesselation_radians : float
        Parametrises subduction teeth density. Triangles are generated only along line segments with distances that 
        exceed the given threshold tessellation_radians.

    triangle_base_length : float  
        Length of teeth triangle base
        
    triangle_aspect : float, default=1.0  
        Aspect ratio of teeth triangles. Ratio is 1.0 by default.

    Returns
    -------
    X_points : (n,3) array
        X points that define the teeth triangles
    Y_points : (n,3) array 
        Y points that define the teeth triangles
    """

    import shapefile
    shp = shapefile.Reader(shapefilename)

    tesselation_degrees = np.degrees(tesselation_radians)
    triangle_pointsX = []
    triangle_pointsY = []

    for i in range(len(shp)):
        pts = np.array(shp.shape(i).points)

        cum_distance = 0.0
        for p in range(len(pts) - 1):

            A = pts[p]
            B = pts[p+1]

            AB_dist = B - A
            AB_norm = AB_dist / np.hypot(*AB_dist)
            cum_distance += np.hypot(*AB_dist)

            # create a new triangle if cumulative distance is exceeded.
            if cum_distance >= tesselation_degrees:

                C = A + triangle_base_length*AB_norm

                # find normal vector
                AD_dist = np.array([AB_norm[1], -AB_norm[0]])
                AD_norm = AD_dist / np.linalg.norm(AD_dist)

                C0 = A + 0.5*triangle_base_length*AB_norm

                # project point along normal vector
                D = C0 + triangle_base_length*triangle_aspect*AD_norm

                triangle_pointsX.append( [A[0], C[0], D[0]] )
                triangle_pointsY.append( [A[1], C[1], D[1]] )

                cum_distance = 0.0

    shp.close()
    return np.array(triangle_pointsX), np.array(triangle_pointsY)

def shapelify_feature_polygons(features):
    """Generates shapely MultiPolygon geometries from reconstructed feature polygons. 
    
    Wraps geometries to the dateline by splitting a polygon into multiple polygons at the dateline. This is to avoid 
    horizontal lines being formed between polygons at longitudes of -180 and 180 degrees. Exterior coordinates are 
    ordered anti-clockwise and only valid geometries are passed to ensure compatibility with Cartopy. 

    Parameters
    ----------
    features : list
        Contains reconstructed polygon features.

    Returns
    -------
    all_geometries : list
        Shapely multi-polygon geometries generated from the given reconstructed features.
    """
    import shapely

    date_line_wrapper = pygplates.DateLineWrapper()

    all_geometries = []
    for feature in features:

        rings = []
        wrapped_polygons = date_line_wrapper.wrap(feature.get_reconstructed_geometry())
        for poly in wrapped_polygons:
            ring = np.array([(p.get_longitude(), p.get_latitude()) for p in poly.get_exterior_points()])
            ring[:,1] = np.clip(ring[:,1], -89, 89) # anything approaching the poles creates artefacts
            ring_polygon = shapely.geometry.Polygon(ring)

            # we need to make sure the exterior coordinates are ordered anti-clockwise
            # and the geometry is valid otherwise it will screw with cartopy
            if not ring_polygon.exterior.is_ccw:
                ring_polygon.exterior.coords = list(ring[::-1])

            rings.append(ring_polygon)

        geom = shapely.geometry.MultiPolygon(rings)

        # we need to make sure the exterior coordinates are ordered anti-clockwise
        # and the geometry is valid otherwise it will screw with cartopy
        all_geometries.append(geom.buffer(0.0)) # add 0.0 buffer to deal with artefacts

    return all_geometries

def shapelify_feature_lines(features):
    """Generates shapely MultiLineString geometries from reconstructed linestring features. 

    Wraps geometries to the dateline by splitting a polyline into multiple polylines at the dateline. This is to avoid
    horizontal lines being formed between polylines at longitudes of -180 and 180 degrees. 

    Parameters
    ----------
    features : list
        Contains reconstructed linestring features.

    Returns
    -------
    all_geometries : list
        Shapely MultiLineString geometries generated from the given reconstructed features.
    """
    import shapely

    date_line_wrapper = pygplates.DateLineWrapper()

    all_geometries = []
    for feature in features:

        rings = []
        wrapped_lines = date_line_wrapper.wrap(feature.get_reconstructed_geometry())
        for line in wrapped_lines:
            ring = np.array([(p.get_longitude(), p.get_latitude()) for p in line.get_points()])
            ring[:,1] = np.clip(ring[:,1], -89, 89) # anything approaching the poles creates artefacts
            ring_linestring = shapely.geometry.LineString(ring)

            rings.append(ring_linestring)

        # construct shapely geometry
        geom = shapely.geometry.MultiLineString(rings)

        if geom.is_valid:
            all_geometries.append(geom)

    return all_geometries



class PlotTopologies(object):
    """Provides methods to read, reconstruct and plot geological topology features.

    Accesses PyGplates and Shapely functionalities to reconstruct feature shapefiles to specific geological times. A
    variety of geological features can be plotted on GeoAxes maps as Shapely MultiLineString or MultiPolygon geometries,
    including subduction trenches & subduction teeth, mid-ocean ridge boundaries, transform boundaries, coastlines,
    continents and COBs. Moreover, netCDF4 and ndarray grids can be plotted onto GeoAxes maps. Plate motion velocity
    vectors can be generated and plotted using this object.

    The rotation models and topology features are used with pyGplates to extract resolved topology features, ridge and
    transform boundary sections, ridge boundary sections, transform boundary sections, subduction boundary sections,
    left subduction boundary sections, right subduction boundary sections and other boundary sections that are not
    subduction zones or mid-ocean ridges (ridge/transform). The continents, coastlines and COBs are read from file
    names given to this class.


    Attributes
    ----------
    self.PlateReconstruction_object
    self.base_projection
    self.coastline_filename
    self.continent_filename
    self.COB_filename
    self.time
    self.topologies
    self.ridge_transforms
    self.ridges
    self.transforms
    self.trenches
    self.trench_left
    self.trench_right
    self.other

    Methods
    ---------
    __init__(self, PlateReconstruction_object, time, coastline_filename=None, continent_filename=None, COB_filename=None)
        Constructs all necessary attributes for the PlotTopologies object. 
        
    update_time(self, time)
    
    _get_feature_lines(self, features)
        Generates shapely MultiLineString geometries from reconstructed linestring features.
        
    _tesselate_triangles(self, features, tesselation_radians, triangle_base_length, triangle_aspect=1.0)
        Places subduction teeth along subduction boundary line segments within a MultiLineString shapefile.
        
    plot_coastlines(self, ax, **kwargs)
    plot_continents(self, ax, **kwargs)
    plot_continent_ocean_boundaries(self, ax, **kwargs)
    plot_ridges(self, ax, color='black', **kwargs)
    plot_ridges_and_transforms(self, ax, color='black', **kwargs)
    plot_transforms(self, ax, color='black', **kwargs)
    plot_trenches(self, ax, color='black', **kwargs)
    plot_subduction_teeth(self, ax, spacing=0.1, size=2.0, aspect=1, color='black', **kwargs)
    plot_grid(self, ax, grid, extent=[-180,180,-90,90], **kwargs)
    plot_grid_from_netCDF(self, ax, filename, **kwargs)
    plot_plate_motion_vectors(self, ax, spacingX=10, spacingY=10, normalise=False, **kwargs)
    """
    def __init__(self, PlateReconstruction_object, time, coastline_filename=None, continent_filename=None, COB_filename=None):
        """Constructs all necessary attributes for the PlateTopologies object.
        """
        import ptt
        import cartopy.crs as ccrs

        self.PlateReconstruction_object = PlateReconstruction_object
        self.base_projection = ccrs.PlateCarree()

        self.coastline_filename = coastline_filename
        self.continent_filename = continent_filename
        self.COB_filename = COB_filename

        # store topologies for easy access
        # setting time runs the update_time routine
        self.time = time

    @property
    def time(self):
        """ Reconstruction time """
        return self._time

    @time.setter
    def time(self, var):
        """Allows the time attribute to be changed. Updates all instances of the time attribute in the object (e.g.
        reconstructions and resolving topologies will use this new time).

        Raises
        ------
        ValueError
            If the chosen reconstruction time is <0 Ma.
        """
        if var >= 0:
            self.update_time(var)
        else:
            raise ValueError("Enter a valid time >= 0")


    def update_time(self, time):
        """Reconstructs features and resolves important topologies at the set reconstruction time. Updates all
        reconstructions/resolutions accordingly whenever the time attribute is changed.

        Returns
        -------
        The following class attributes are generated and updated whenever a reconstruction time attribute is set:
        topologies, ridge_transforms, ridges, transforms, trenches, trench_left, trench_right, or other : lists 
            Common topology features resolved to the set geological time. Specifically, these are lists of:
                - resolved topology features (topological plates and networks)
                - ridge and transform boundary sections (resolved features)
                - ridge boundary sections (resolved features)
                - transform boundary sections (resolved features)
                - subduction boundary sections (resolved features)
                - left subduction boundary sections (resolved features)
                - right subduction boundary sections (resolved features)
                - other boundary sections (resolved features) that are not subduction zones or mid-ocean ridges 
                (ridge/transform)

        coastlines, continents, COBs : lists
            Reconstructed features appended to a Python list. 
        """
        self._time = float(time)
        resolved_topologies = ptt.resolve_topologies.resolve_topologies_into_features(
            self.PlateReconstruction_object.rotation_model,
            self.PlateReconstruction_object.topology_features,
            self.time)

        self.topologies, self.ridge_transforms, self.ridges, self.transforms, self.trenches, self.trench_left, self.trench_right, self.other = resolved_topologies

        # reconstruct other important polygons and lines
        if self.coastline_filename:
            self.coastlines = self.PlateReconstruction_object.reconstruct(
                self.coastline_filename, self.time, from_time=0, anchor_plate_id=0)

        if self.continent_filename:
            self.continents = self.PlateReconstruction_object.reconstruct(
                self.continent_filename, self.time, from_time=0, anchor_plate_id=0)

        if self.COB_filename:
            self.COBs = self.PlateReconstruction_object.reconstruct(
                self.COB_filename, self.time, from_time=0, anchor_plate_id=0)

    def _get_feature_lines(self, features):
        """Generates shapely MultiLineString geometries from reconstructed linestring features. 

        Wraps geometries to the dateline by splitting a polyline into multiple polylines at the dateline. This is to 
        avoid horizontal lines being formed between polylines at longitudes of -180 and 180 degrees. Note: Lat-lon feature
        points near the poles (-89 & 89 latitude) are clipped to ensure compatibility with Cartopy. 

        Parameters
        ----------
        features : list
            Contains reconstructed linestring features.

        Returns
        -------
        all_geometries : list
            Shapely MultiLineString geometries generated from the given reconstructed features.
        """
        import shapely
        
        date_line_wrapper = pygplates.DateLineWrapper()

        all_geometries = []
        for feature in features:

            # get geometry in lon lat order
            rings = []
            for geometry in feature.get_geometries():
                wrapped_lines = date_line_wrapper.wrap(geometry)
                for line in wrapped_lines:
                    ring = np.array([(p.get_longitude(), p.get_latitude()) for p in line.get_points()])
                    ring[:,1] = np.clip(ring[:,1], -89, 89) # anything approaching the poles creates artefacts
                    ring_linestring = shapely.geometry.LineString(ring)
                    
                    rings.append(ring_linestring)
                
            # construct shapely geometry
            geom = shapely.geometry.MultiLineString(rings)

            if geom.is_valid:
                all_geometries.append(geom)

        return all_geometries

    # subduction teeth
    def _tesselate_triangles(self, features, tesselation_radians, triangle_base_length, triangle_aspect=1.0):
        """Places subduction teeth along subduction boundary line segments within a MultiLineString shapefile. 

        Parameters
        ----------
        shapefilename  : str  
            Path to shapefile containing the subduction boundary features

        tesselation_radians : float
            Parametrises subduction teeth density. Triangles are generated only along line segments with distances
            that exceed the given threshold tessellation_radians.

        triangle_base_length : float  
            Length of teeth triangle base
        
        triangle_aspect : float, default=1.0  
            Aspect ratio of teeth triangles. Ratio is 1.0 by default.

        Returns
        -------
        X_points : (n,3) array 
            X points that define the teeth triangles
        Y_points : (n,3) array 
            Y points that define the teeth triangles
        """

        tesselation_degrees = np.degrees(tesselation_radians)
        triangle_pointsX = []
        triangle_pointsY = []

        date_line_wrapper = pygplates.DateLineWrapper()


        for feature in features:

            cum_distance = 0.0

            for geometry in feature.get_geometries():
                wrapped_lines = date_line_wrapper.wrap(geometry)
                for line in wrapped_lines:
                    pts = np.array([(p.get_longitude(), p.get_latitude()) for p in line.get_points()])

                    for p in range(0, len(pts) - 1):
                        A = pts[p]
                        B = pts[p+1]

                        AB_dist = B - A
                        AB_norm = AB_dist / np.hypot(*AB_dist)
                        cum_distance += np.hypot(*AB_dist)

                        # create a new triangle if cumulative distance is exceeded.
                        if cum_distance >= tesselation_degrees:

                            C = A + triangle_base_length*AB_norm

                            # find normal vector
                            AD_dist = np.array([AB_norm[1], -AB_norm[0]])
                            AD_norm = AD_dist / np.linalg.norm(AD_dist)

                            C0 = A + 0.5*triangle_base_length*AB_norm

                            # project point along normal vector
                            D = C0 + triangle_base_length*triangle_aspect*AD_norm

                            triangle_pointsX.append( [A[0], C[0], D[0]] )
                            triangle_pointsY.append( [A[1], C[1], D[1]] )

                            cum_distance = 0.0

        return np.array(triangle_pointsX), np.array(triangle_pointsY)

    def plot_coastlines(self, ax, **kwargs):
        """Plots reconstructed coastline polygons onto a standard map. 

        The reconstructed coastlines for plotting must be contained in a shape filename. These coastlines are transformed
        into shapely geometries and added onto the chosen map for a specific geological time (supplied to the PlotTopologies
        object). Map presentation details (e.g. facecolor, edgecolor, alpha…) are permitted.

        Parameters
        ----------
        ax : GeoAxis
            A standard map for lat-lon data built on a matplotlib figure. Can be for a single plot or for multiple subplots.
            Should be set at a particular Cartopy map projection.

        **kwargs 
            Keyword arguments that allow control over parameters such as ‘facecolor’, ‘alpha’, etc. for plotting 
            coastline geometries.

        Returns
        -------
        ax : GeoAxis
            The map with coastline features plotted onto the chosen projection (transformed using PlateCarree). 
        """
        if self.coastline_filename is None:
            raise ValueError("Supply coastline_filename to PlotTopologies object")

        coastline_polygons = shapelify_feature_polygons(self.coastlines)
        return ax.add_geometries(coastline_polygons, crs=self.base_projection, **kwargs)

    def plot_continents(self, ax, **kwargs):
        """Plots reconstructed continental polygons onto a standard map. 

        The reconstructed continents for plotting must be contained in a shape filename. These continents are transformed
        into shapely geometries and added onto the chosen map for a specific geological time (supplied to the PlotTopologies
        object). Map presentation details (e.g. facecolor, edgecolor, alpha…) are permitted.

        Parameters
        ----------
        ax : GeoAxis
            A standard map for lat-lon data built on a matplotlib figure. Can be for a single plot or for multiple subplots.
            Should be set at a particular Cartopy map projection.

        **kwargs 
            Keyword arguments that allow control over parameters such as ‘facecolor’, ‘alpha’, etc. for plotting continental
            geometries.

        Returns
        -------
        ax : GeoAxis
            The map with continental features plotted onto the chosen projection (transformed using PlateCarree). 
        """
        if self.continent_filename is None:
            raise ValueError("Supply continent_filename to PlotTopologies object")

        continent_polygons = shapelify_feature_polygons(self.continents)
        return ax.add_geometries(continent_polygons, crs=self.base_projection, **kwargs)

    def plot_continent_ocean_boundaries(self, ax, **kwargs):
        """Plots reconstructed continent-ocean boundary (COB) polygons onto a standard map. 

        The reconstructed COBs for plotting must be contained in a shape filename. These COBs are transformed into shapely
        geometries and added onto the chosen map for a specific geological time (supplied to the PlotTopologies object). Map
        presentation details (e.g. facecolor, edgecolor, alpha…) are permitted.

        Parameters
        ----------
        ax : GeoAxis
            A standard map for lat-lon data built on a matplotlib figure. Can be for a single plot or for multiple subplots.
            Should be set at a particular Cartopy map projection.

        **kwargs 
            Keyword arguments that allow control over parameters such as ‘facecolor’, ‘alpha’, etc. for plotting COBs.

        Returns
        -------
        ax : GeoAxis
            The map with coastline features plotted onto the chosen projection (transformed using PlateCarree). 
        """
        if self.COB_filename is None:
            raise ValueError("Supply COB_filename to PlotTopologies object")

        COB_lines = shapelify_feature_lines(self.COBs)
        return ax.add_geometries(COB_lines, crs=self.base_projection, facecolor='none', **kwargs)

    def plot_ridges(self, ax, color='black', **kwargs):
        """Plots reconstructed ridge polylines onto a standard map. 

        The reconstructed ridges for plotting must be a list held in the ‘ridges’ attribute. These ridges are transformed 
        into shapely geometries and added onto the chosen map for a specific geological time (supplied to the PlotTopologies
        object). Map presentation details (e.g. color, alpha…) are permitted.

        Note: Ridge geometries are wrapped to the dateline by splitting a polyline into multiple polylines at the dateline.
        This is to avoid horizontal lines being formed between polylines at longitudes of -180 and 180 degrees. Lat-lon 
        feature points near the poles (-89 & 89 latitude) are clipped to ensure compatibility with Cartopy. 

        Parameters
        ----------
        ax : GeoAxis
            A standard map for lat-lon data built on a matplotlib figure. Can be for a single plot or for multiple subplots.
            Should be set at a particular Cartopy map projection.

        color : str, default=’black’
            The colour of the ridge lines. By default, it is set to black.

        **kwargs 
            Keyword arguments that allow control over parameters such as ‘alpha’, etc. for plotting ridge geometries.

        Returns
        -------
        ax : GeoAxis
            The map with ridge features plotted onto the chosen projection (transformed using PlateCarree). 
        """
        ridge_lines = self._get_feature_lines(self.ridges)
        return ax.add_geometries(ridge_lines, crs=self.base_projection, facecolor='none', edgecolor=color, **kwargs)

    def plot_ridges_and_transforms(self, ax, color='black', **kwargs):
        """Plots reconstructed ridge & transform boundary polylines onto a standard map. 

        The reconstructed ridge & transform sections for plotting must be a list held in the ‘ridge_transforms’ attribute. 
        These sections are transformed into shapely geometries and added onto the chosen map for a specific geological time
        (supplied to the PlotTopologies object). Map presentation details (e.g. color, alpha…) are permitted.

        Note: Ridge & transform geometries are wrapped to the dateline by splitting a polyline into multiple polylines at 
        the dateline. This is to avoid horizontal lines being formed between polylines at longitudes of -180 and 180 degrees.
        Lat-lon feature points near the poles (-89 & 89 latitude) are clipped to ensure compatibility with Cartopy. 

        Parameters
        ----------
        ax : GeoAxis
            A standard map for lat-lon data built on a matplotlib figure. Can be for a single plot or for multiple subplots.
            Should be set at a particular Cartopy map projection.

        color : str, default=’black’
            The colour of the ridge & transform lines. By default, it is set to black.

        **kwargs 
            Keyword arguments that allow control over parameters such as ‘alpha’, etc. for plotting ridge & transform geometries.

        Returns
        -------
        ax : GeoAxis
            The map with ridge & transform features plotted onto the chosen projection (transformed using PlateCarree).
        """
        ridge_transform_lines = self._get_feature_lines(self.ridge_transforms)
        return ax.add_geometries(ridge_transform_lines, crs=self.base_projection, facecolor='none', edgecolor=color, **kwargs)

    def plot_transforms(self, ax, color='black', **kwargs):
        """Plots reconstructed transform boundary polylines onto a standard map. 

        The reconstructed transform sections for plotting must be a list held in the ‘transforms’ attribute. These sections
        are transformed into shapely geometries and added onto the chosen map for a specific geological time (supplied to
        the PlotTopologies object). Map presentation details (e.g. color, alpha…) are permitted.

        Note: Transform geometries are wrapped to the dateline by splitting a polyline into multiple polylines at the dateline.
        This is to avoid horizontal lines being formed between polylines at longitudes of -180 and 180 degrees. Lat-lon feature
        points near the poles (-89 & 89 latitude) are clipped to ensure compatibility with Cartopy. 

        Parameters
        ----------
        ax : GeoAxis
            A standard map for lat-lon data built on a matplotlib figure. Can be for a single plot or for multiple subplots.
            Should be set at a particular Cartopy map projection.

        color = str, default=’black’
            The colour of the transform lines. By default, it is set to black.

        **kwargs 
            Keyword arguments that allow control over parameters such as ‘alpha’, etc. for plotting transform geometries.

        Returns
        -------
        ax : GeoAxis
            The map with transform features plotted onto the chosen projection (transformed using PlateCarree).
        """
        transform_lines = self._get_feature_lines(self.transforms)
        return ax.add_geometries(transform_lines, crs=self.base_projection, facecolor='none', edgecolor=color, **kwargs)

    def plot_trenches(self, ax, color='black', **kwargs):
        """Plots reconstructed subduction trench polylines onto a standard map. 

        The reconstructed trenches for plotting must be a list held in the ‘trenches’ attribute. These sections are 
        transformed into shapely geometries and added onto the chosen map for a specific geological time (supplied to the
        PlotTopologies object). Map presentation details (e.g. color, alpha…) are permitted.

        Note: Trench geometries are wrapped to the dateline by splitting a polyline into multiple polylines at the dateline.
        This is to avoid horizontal lines being formed between polylines at longitudes of -180 and 180 degrees. Lat-lon 
        feature points near the poles (-89 & 89 latitude) are clipped to ensure compatibility with Cartopy. 

        Parameters
        ----------
        ax : GeoAxis
            A standard map for lat-lon data built on a matplotlib figure. Can be for a single plot or for multiple subplots.
            Should be set at a particular Cartopy map projection.

        color = str, default=’black’
            The colour of the trench lines. By default, it is set to black.

        **kwargs 
            Keyword arguments that allow control over parameters such as ‘alpha’, etc. for plotting trench geometries.

        Returns
        -------
        ax : GeoAxis
            The map with subduction trench features plotted onto the chosen projection (transformed using PlateCarree).
        """
        trench_lines = self._get_feature_lines(self.trenches)
        return ax.add_geometries(trench_lines, crs=self.base_projection, facecolor='none', edgecolor=color, **kwargs)

    def plot_subduction_teeth(self, ax, spacing=0.1, size=2.0, aspect=1, color='black', **kwargs):
        """Plots subduction teeth onto a standard map. 

        To plot subduction teeth, the left and right sides of resolved subduction boundary sections must be accessible
        from the “left_trench” and “right_trench” attributes. Teeth are created and transformed into Shapely polygons for
        plotting. 

        Parameters
        ----------
        ax : GeoAxis
            A standard map for lat-lon data built on a matplotlib figure. Can be for a single plot or for multiple subplots.
            Should be set at a particular Cartopy map projection.

        spacing : float, default=0.1 
            The tessellation threshold (in radians). Parametrises subduction tooth density. Triangles are generated only
            along line segments with distances that exceed the given threshold ‘spacing’.

        size : float, default=2.0
            Length of teeth triangle base.

        aspect : float, default=1
            Aspect ratio of teeth triangles. Ratio is 1.0 by default. 

        color = str, default=’black’
            The colour of the teeth. By default, it is set to black.

        **kwargs 
            Keyword arguments that allow control over parameters such as ‘alpha’, etc. for plotting subduction tooth polygons.

        Returns
        -------
        ax : GeoAxis
            The map with subduction teeth plotted onto the chosen projection (transformed using PlateCarree).
        """
        import shapely

        # add Subduction Teeth
        subd_xL, subd_yL = self._tesselate_triangles(
            self.trench_left,
            tesselation_radians=spacing,
            triangle_base_length=size,
            triangle_aspect=-aspect)
        subd_xR, subd_yR = self._tesselate_triangles(
            self.trench_right,
            tesselation_radians=spacing,
            triangle_base_length=size,
            triangle_aspect=aspect)
        
        teeth = []
        for tX, tY in zip(subd_xL, subd_yL):
            triangle_xy_points = np.c_[tX, tY]
            shp = shapely.geometry.Polygon(triangle_xy_points)
            teeth.append(shp)

        for tX, tY in zip(subd_xR, subd_yR):
            triangle_xy_points = np.c_[tX, tY]
            shp = shapely.geometry.Polygon(triangle_xy_points)
            teeth.append(shp)

        ax.add_geometries(teeth, crs=self.base_projection, color=color, **kwargs)

    def plot_grid(self, ax, grid, extent=[-180,180,-90,90], **kwargs):
        """Plots an ndarray of gridded data onto a standard map. 

        Parameters
        ----------
        ax : GeoAxis
            A standard map for lat-lon data built on a matplotlib figure. Can be for a single plot or for multiple subplots.
            Should be set at a particular Cartopy map projection.

        grid : ndarray
            An array with elements that define a grid. The number of rows corresponds to the number of latitudinal points, 
            while the number of columns corresponds to the number of longitudinal points.

        extent : 1d array, default=[-180,180,-90,90]
            A four-element array to specify the [min lon, max lon, min lat, max lat] with which to constrain the grid image.
            If no extents are supplied, full global extent is assumed. 

        **kwargs
            Keyword arguments that allow control over map presentation parameters such as ‘alpha’, etc. for plotting the grid.

        Returns
        -------
        ax : GeoAxis
            The map with the grid plotted onto the chosen projection (transformed using PlateCarree).
        """
        return ax.imshow(grid, origin='lower', extent=extent, transform=self.base_projection, **kwargs)


    def plot_grid_from_netCDF(self, ax, filename, **kwargs):
        """Reads in a netCDF file, extracts a raster grid and its associated latitude and longitude arrays and plots the
        raster grid onto a standard map. 

        The lat-lon arrays are used to define the extent of the grid image.

        Parameters
        ----------
        ax : GeoAxis
            A standard map for lat-lon data built on a matplotlib figure. Can be for a single plot or for multiple subplots.
            Should be set at a particular Cartopy map projection.

        filename : str
            Path to a netCDF filename.

        **kwargs
            Keyword arguments that allow control over map presentation parameters such as ‘alpha’, etc. for plotting the grid.

        Returns
        -------
        ax : GeoAxis
            The map with the extracted grid plotted onto the chosen projection (transformed using PlateCarree).
        """
        from .grids import read_netcdf_grid

        raster, lon_coords, lat_coords = read_netcdf_grid(filename, return_grids=True)
        extent = [lon_coords.min(), lon_coords.max(), lat_coords.min(), lat_coords.max()]
        return self.plot_grid(ax, raster, extent=extent, **kwargs)


    def plot_plate_motion_vectors(self, ax, spacingX=10, spacingY=10, normalise=False, **kwargs):
        """Calculates plate motion velocity vector fields at a particular geological time and plots them onto a 
        standard map. 
        
        Generates velocity domain feature collections (MeshNode-type features) from given spacing in the X and Y 
        directions. Domain points are extracted from these features and assigned plate IDs, which are used to obtain
        equivalent stage rotations of identified tectonic plates over a 5 Ma time interval. Each point and its stage 
        rotation are used to calculate plate velocities at a particular geological time. Obtained velocities for each
        domain point are represented in the north-east-down coordinate system.
        
        Vector fields can be optionally normalised to have uniform arrow lengths. 

        Parameters
        ----------
        ax : GeoAxis
            A standard map for lat-lon data built on a matplotlib figure. Can be for a single plot or for multiple subplots.
            Should be set at a particular Cartopy map projection.

        spacingX : int, default=10
            The spacing in the X direction used to make the latitude-longitude velocity domain feature mesh. 

        spacingY : int, default=10
            The spacing in the Y direction used to make the latitude-longitude velocity domain feature mesh. 

        normalise : bool, default=False
            Choose whether to normalise the velocity magnitudes so that vector lengths are all equal. 

        **kwargs
            Keyword arguments that allow control over quiver presentation parameters such as ‘alpha’, etc. for plotting
            the vector field.

        Returns
        -------
        ax : GeoAxis
            The map with the plate velocity vector field plotted onto the chosen projection (transformed using PlateCarree).
        """
        
        lons = np.arange(-180, 180+spacingX, spacingX)
        lats = np.arange(-90, 90+spacingY, spacingY)
        lonq, latq = np.meshgrid(lons, lats)

        # create a feature from all the points
        velocity_domain_features = ptt.velocity_tools.make_GPML_velocity_feature(lonq.ravel(), latq.ravel())

        rotation_model = self.PlateReconstruction_object.rotation_model
        topology_features = self.PlateReconstruction_object.topology_features

        delta_time = 5.0
        all_velocities = ptt.velocity_tools.get_plate_velocities(
            velocity_domain_features,
            topology_features,
            rotation_model,
            self.time,
            delta_time,
            'vector_comp')

        X, Y, U, V = ptt.velocity_tools.get_x_y_u_v(lons, lats, all_velocities)

        if normalise:
            mag = np.hypot(U, V)
            mag[mag == 0] = 1
            U /= mag
            V /= mag

        return ax.quiver(X, Y, U, V, transform=self.base_projection, **kwargs)
