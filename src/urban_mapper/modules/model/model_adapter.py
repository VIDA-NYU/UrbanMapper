# pip install pykrige pysal spreg

import numpy as np
import pandas as pd, geopandas as gpd
import libpysal

from sklearn.base import BaseEstimator, RegressorMixin

from spreg import ML_Lag
from pykrige.rk import * #ex.: RegressionKriging

# https://geostat-framework.readthedocs.io/en/latest/#pykrige
class Kriging_Adapter(RegressorMixin, BaseEstimator):
  """Class that adapts pykrige.rk.RegressionKriging to scikit-learn environment.

  Attributes:
      __kriging_obj: The proper `RegressionKriging` object
      __kwargs: Additional model arguments

  Examples:
      >>> from .model_adapter import *
      ...
      >>> model = Kriging_Adapter()
  """
  
  def __init__(self, **kwargs):
    self.__kriging_obj = RegressionKriging(**kwargs)

  @property
  def kriging_obj(self):
    return self.__kriging_obj

  def __getattr__(self, attr):
    return getattr(self.__kriging_obj, attr)

  def fit(self, X, y, long_lat):
    """
        Args:
            X: The dataset used to fit the model
            y: Target values used to fit the model
            long_lat: longitude-latitude information used to fit the model

        Returns:
            RegressionKriging: 

        Examples:
            >>> from .model_adapter import *
            >>> model = Kriging_Adapter()
            >>> ...
            >>> model.fit(data_features, target, long_lat)
    """       

    return self.__kriging_obj.fit(p=X, x=long_lat, y=y)
  
  def predict(self, X, long_lat):
    """
        Args:
            X: The dataset used for predictions
            long_lat: longitude-latitude information used for predictions

        Returns:
            predictions: `np.array` with predictions

        Examples:
            >>> from .model_adapter import *
            >>> model = Kriging_Adapter()
            >>> ...
            >>> model.fit(data_features, target, long_lat)
            >>> ...
            >>> model.predict(test_features, test_long_lat)
    """         
    return self.__kriging_obj.predict(p=X, x=long_lat)

#ML_Lag from https://pysal.org/spreg/        
#Spatial Lag Model (SLM)
class ML_Lag_Adapter(RegressorMixin, BaseEstimator):
  """Class that adapts spreg.ML_Lag (from PySAL project) to scikit-learn environment.

  Attributes:
      __slm_obj: The proper `ML_Lag` object
      __train_geometry: Geometry information used to fit the model and predict new values
      __train_y: Target values used to fit the model and predict new values
      __kwargs: Additional model arguments 

  Examples:
      >>> from .model_adapter import *
      ...
      >>> model = ML_Lag_Adapter()
  """  
  def __init__(self, **kwargs):
    self.__slm_obj = None
    self.__train_geometry = None
    self.__train_y = None
    self.__kwargs = kwargs

  def __getattr__(self, attr):
    return getattr(self.__slm_obj, attr)

  def fit(self, X, y, geometry):
    """
        Args:
            X: The dataset used to fit the model
            y: Target values used to fit the model
            geometry: Geometry information used to fit the model

        Returns:
            ML_Lag: 

        Examples:
            >>> from .model_adapter import *
            >>> model = ML_Lag_Adapter()
            >>> ...
            >>> model.fit(data_features, target, geometry)
    """        
    self.__train_geometry = geometry
    self.__train_y = y

    # Spatial weights with Queen contiguity (neighbors that share a border or vertex)
    W = libpysal.weights.Queen.from_dataframe(gpd.GeoDataFrame(geometry), use_index = True)
    # W = libpysal.weights.Rook.from_dataframe(data, use_index = True)
    W.transform = "r"   # Row-standardize weights

    # slm = ML_Lag(x=X, w=W, y=y, name_ds="input_geodataframe", name_x=["medianinco", "medianagem"], name_w="Queen", name_y="gini")
    self.__slm_obj = ML_Lag(x=X, w=W, y=y, **self.__kwargs)

    return self.__slm_obj

  def predict(self, X, geometry):
    """
        Args:
            X: The dataset used for predictions
            geometry: Geometry information used for predictions    

        Returns:
            predictions: `np.array` with predictions

        Examples:
            >>> from .model_adapter import *
            >>> model = ML_Lag_Adapter()
            >>> ...
            >>> model.fit(data_features, target, geometry)
            >>> ...
            >>> model.predict(test_features, test_geometry)
    """       
    train_test_geometry = gpd.GeoDataFrame(pd.concat([self.__train_geometry, geometry], ignore_index=True))

    # Spatial weights with Queen contiguity (neighbors that share a border or vertex)
    W_train_test = libpysal.weights.Queen.from_dataframe(train_test_geometry, use_index = True)
    W_train_test.transform = "r"
    W_train_test = W_train_test.full()[0]

    # Model parameters
    intercept = self.__slm_obj.betas.flatten()[0]
    beta = self.__slm_obj.betas.flatten()[1:-1]   #
    # rho = self.__slm_obj.rho[0][0]
    rho = self.__slm_obj.rho

    y_pred = []
    n_train = len(self.__train_geometry)
    n_total = len(train_test_geometry)    

    #TODO: is it the only or the best way to do it?
    for i in range(n_train, n_total):
      # Spatial lag part: neighbors' target values (observed or predicted if available)
      neighbors = np.where(W_train_test[i, :] != 0)[0]
      spatial_effect = 0

      for j in neighbors:
        # Use observed target for training polygons
        if j < n_train:
          spatial_effect += W_train_test[i, j] * self.__train_y[j]
        # For neighbors that are also new polygons, use predicted value (recursive)
        elif (j - n_train) < len(y_pred):
           spatial_effect += W_train_test[i, j] * y_pred[j - n_train]

      # Final prediction
      y_pred.append(intercept + np.dot(X[i - n_train], beta) + rho * spatial_effect)

    return np.array(y_pred)
  
class CustomModel_Adapter(BaseEstimator):
  """Abstract base class to adapt customized models

    Children classes should implement this interface and a specific scikit-learn mixin (RegressorMixin, ClassifierMixin, or ClusterMixin)

    Note: UrbanMapper model structure depends on this classes types.

  Attributes:

  Examples:
    # Define a regressor class
    >>> class MyRegressor(RegressorMixin, CustomModel_Adapter):
    >>>   def fit(self, X, y, **kwargs):
    >>>     ...
    >>> 
    >>>   def predict(self, X, **kwargs):
    >>>     ...
    >>> 
    >>>   def load(self, path):
    >>>     ...
    ...
    # Define a classifier class
    >>> class MyClassifier(ClassifierMixin, CustomModel_Adapter):
    >>>   def fit(self, X, y, **kwargs):
    >>>     ...
    >>> 
    >>>   def predict(self, X, **kwargs):
    >>>     ...
    >>> 
    >>>   def load(self, path):
    >>>     ...
    ...
    # Define a clusterer class
    >>> class MyCluster(ClusterMixin, CustomModel_Adapter):
    >>>   def fit(self, X, y, **kwargs):
    >>>     ...
    >>> 
    >>>   def predict(self, X, **kwargs):
    >>>     ...
    >>> 
    >>>   def load(self, path):
    >>>     ...
  """  
  def fit(self, X, y, **kwargs):
    return self

  def predict(self, X, **kwargs):
    return None

  def load(self, path):
    pass