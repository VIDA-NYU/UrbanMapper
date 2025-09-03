import geopandas as gpd
import numpy as np
import pdb
import joblib

from typing import Optional, List, Union, Tuple
from abc import ABC
from beartype import beartype
from enum import IntEnum
from .utils import *
from .model_adapter import *

from sklearn.base import BaseEstimator, RegressorMixin, ClassifierMixin, ClusterMixin
from sklearn import feature_selection, preprocessing 
from sklearn.cluster import KMeans
from sklearn.compose import TransformedTargetRegressor
from sklearn.exceptions import NotFittedError
from sklearn.model_selection import train_test_split

from sklearn.svm import *  #ex.: SVR
from sklearn.linear_model import * #ex.: LinearRegression
from sklearn.ensemble import *  #ex.: RandomForestRegressor

class ModelTask(IntEnum): 
  CLUSTERING = 0
  CLASSIFICATION = 1
  REGRESSION = 2

class AutoConfig():
  """Class that runs a basic model configuration based on data infomrations

  """

  def __init__(self):
    self.__task_type = None

  @property
  def task_type(self):
    return self.__task_type

  def config_model(
      self,
      input_geodataframe: Union[gpd.GeoDataFrame, pd.DataFrame], 
      model: Optional[Union[str, BaseEstimator]] = None, 
      weight_path: Optional[str] = None, 
      target_column: Optional[str] = None, 
      longitude_column: Optional[str] = None, 
      latitude_column: Optional[str] = None, 
      geometry_column: Optional[str] = None,
      **kwargs
  ) -> BaseEstimator:
    """
        Args:
            input_geodataframe: dataset used to configure the model
            model: if None, the functions tests the columns to define the model type.
                   if str, it tries to instatiate the related class from sklearn.svm, sklearn.linear_model, sklearn.ensemble, or one adapted class in utils.py 
            weight_path: The path to load saved model weights.
            target_column: The name of the target column values to predict.
                           If None, the function assumes the task as `clustering` and returns a `KMeans` object.
                           If it is the name of an `integer`column, it assumes the task as `classification` and returns a `SVC` object.
                           If it is the name of an `float`column, it assumes the task as `regression` and evaluate the coordinates type to define a default model
            latitude_column: The name of the column containing latitude values.
            longitude_column: The name of the column containing longitude values.
                Note: If latitude_column/longitude_column are not None, it returns an adapter class for pykrige.rk.RegressionKriging
            geometry_column: The name of column containing data geometry. 
                             If None, it considers the input_geodataframe.active_geometry_name and returns an adapter class for libpysal.ML_Lag object.
                             Otherwise, it consider the input_geodataframe column and also returns an adapter class for libpysal.ML_Lag object.
            **kwargs: Additional model arguments

        Returns:
            BaseEstimator: 

        Examples:
            >>> from urban_mapper.modules.model import ModelBase
            # Creates with all default attributes
            >>> model = ModelBase()
            ...
            >>> data_transformed, long_lat, geometry, target = model.transform(data)
    """          
    if model is None:
      #Clustering
      if target_column is None:
        #Sturge's rule
        n_clusters = int(1.0 + 3.322 * np.log10(input_geodataframe.shape[0]))
        kwargs.setdefault("n_clusters", n_clusters)
        model = KMeans(**kwargs)

      #Classification  
      elif isinstance(input_geodataframe[target_column].iloc[0], np.integer):
        kwargs.setdefault("random_state", 42)
        kwargs.setdefault("max_iter", 1000)
        kwargs.setdefault("probability", False)
        kwargs.setdefault("verbose", False)
        model = SVC(**kwargs)

      #Regression  
      elif longitude_column is not None and latitude_column is not None:
        model = Kriging_Adapter(**kwargs)
      elif geometry_column is not None or (hasattr(input_geodataframe, "active_geometry_name") and input_geodataframe.active_geometry_name is not None):
        model = ML_Lag_Adapter(**kwargs)
      else:
        model = SVR(**kwargs)     

    elif isinstance(model, str):
      model = eval(model)(**kwargs)

    if isinstance(model, ClusterMixin):
      self.__task_type = ModelTask.CLUSTERING
    elif  isinstance(model, ClassifierMixin):
      self.__task_type = ModelTask.CLASSIFICATION  
    elif  isinstance(model, RegressorMixin):
      self.__task_type = ModelTask.REGRESSION

    if weight_path is not None:
      if isinstance(model, (ClusterMixin, ClassifierMixin, RegressorMixin)):
        model = joblib.load(weight_path)
      else:  
        model.load(weight_path)

    return model

@beartype
class ModelBase(ABC, BaseEstimator):
  """Abstract base class for models

  This class defines the interface that model implementations
  must follow. Urban layers represent spatial layers (dataset as `GeoDataframe`) used for geographical
  analysis and mapping within `UrbanMapper`, such as `streets`, `regions`, or custom layers.

  Attributes:
      model: The name class name from scikit-learn or a custom object that inherits scikit-learn BaseEstimator. If None, __auto_config will create one.
      weight_path: The path to load saved model weights.
      data_columns: List of column names containing values used to train a model. If None, __auto_config selects them.
      target_column: The name of the column containing target values to predict. 
      latitude_column: The name of the column containing latitude values.
      longitude_column: The name of the column containing longitude values.
      geometry_column: The name of column containing data geometry. If None, __auto_config uses the `active_geometry_name` from the geodataframe.   
      model_args: Specific arguments of non-custom model.
      feature_selector: The name class name from scikit-learn or a custom object that inherits scikit-learn BaseEstimator used to select features. 
                        If None, it uses a feature_selection.VarianceThreshold as default
      feature_scaler:  The name class name from scikit-learn or a custom object that inherits scikit-learn BaseEstimator used to scale features. 
                       If None, it uses a preprocessing.StandardScaler as default
      target_filter:  The name class name from scikit-learn or a custom object that inherits scikit-learn BaseEstimator used to filter regression target outliers. 
                      If None, it uses a utils.IQROutlierDetector defined 
      target_scaler:  The name class name from scikit-learn or a custom object that inherits scikit-learn BaseEstimator used to scale regression targets. 
                      If None, it uses a preprocessing.StandardScaler as default
      train_size: Size of the training subset. 
      validation_size: Size of the validation subset. 
      test_size: Size of the test subset. 

  Examples:
      >>> from urban_mapper.modules.model import ModelBase
      # Creates with all default attributes
      >>> model = ModelBase()
      ...
      >>> model = ModelBase(model="SVR")
      ...
      >>> model = ModelBase(weight_path="/home/user/model.joblib")
  """

  def __init__(
    self,
    model: Optional[Union[str, BaseEstimator]] = None,
    weight_path: Optional[str] = None,
    train_size: Optional[Union[int, float]] = None,
    validation_size: Optional[Union[int, float]] = None,
    test_size: Optional[Union[int, float]] = None,
    data_columns: Optional[List[str]] = None,
    target_column: Optional[str] = None,
    longitude_column: Optional[str] = None,
    latitude_column: Optional[str] = None,
    geometry_column: Optional[str] = None,
    feature_selector: Optional[Union[str, BaseEstimator]] = None,
    feature_scaler: Optional[Union[str, BaseEstimator]] = None,
    target_filter: Optional[Union[str, OutlierMixin]] = None,
    target_scaler: Optional[Union[str, BaseEstimator]] = None,
    target_encoder: Optional[Union[str, BaseEstimator]] = None,
  ):
    self.__auto_config = AutoConfig()
    self.__fitted = False

    self.model = model
    self.mask_fit = None

    self.feature_selector = feature_selector or feature_selection.VarianceThreshold(0.01)
    self.feature_scaler = feature_scaler or preprocessing.StandardScaler()

    self.target_filter = target_filter
    self.target_scaler = target_scaler
    self.target_encoder = target_encoder

    self.weight_path = weight_path
    self.train_size = train_size
    self.validation_size = validation_size
    self.test_size = test_size or 0.1
    self.data_columns = data_columns
    self.target_column = target_column
    self.longitude_column = longitude_column
    self.latitude_column = latitude_column
    self.geometry_column = geometry_column

  @property
  def fitted(self):
    return self.__fitted

  def transform(self, input_geodataframe: Union[gpd.GeoDataFrame, pd.DataFrame], fit = True) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[gpd.GeoSeries], Optional[np.ndarray]]:
    """
        Args:
            input_geodataframe: GeoDataFrame to be transformed
            fit: if True, fits the transformations. Otherwise, only transforms data

        Returns:
            np.ndarray: Matrix (n', f) transformed data features. If the task is regression, (n') is the number of rows from `input_geodataframe`, filtered by the target_filter.
            np.ndarray: The longitude-latitude coordinates extracted from the original `input_geodataframe`, filtered by the target_filter.
            gpd.GeoSeries: The geometry column extracted from the original `input_geodataframe`, filtered by the target_filter.
            np.ndarray: Target column from the original `input_geodataframe`, filtered by the target_filter.

        Examples:
            >>> from urban_mapper.modules.model import ModelBase
            # Creates with all default attributes
            >>> model = ModelBase()
            ...
            >>> data_transformed, long_lat, geometry, target = model.transform(data)
    """      
    target, longitude, latitude, long_lat, geometry = None, None, None, None, None

    #Extracting from input_geodataframe: target, longitude/latitude, geometry columns, and keeping data_columns
    if self.target_column:
      target = input_geodataframe.loc[:, self.target_column]
      input_geodataframe = input_geodataframe.drop(self.target_column, axis = 1)
    if self.longitude_column:
      longitude = input_geodataframe.loc[:, self.longitude_column]
      input_geodataframe = input_geodataframe.drop(self.longitude_column, axis = 1)
    if self.latitude_column:
      latitude = input_geodataframe.loc[:, self.latitude_column]
      input_geodataframe = input_geodataframe.drop(self.latitude_column, axis = 1)
    if self.longitude_column and self.latitude_column:
      long_lat = np.array([ [x, y] for x, y in  zip(longitude, latitude)])
    if self.geometry_column:
      geometry = input_geodataframe.loc[:, self.geometry_column]
      input_geodataframe = input_geodataframe.drop(self.geometry_column, axis = 1)
    if long_lat is None and geometry is None and (hasattr(input_geodataframe, "active_geometry_name") and input_geodataframe.active_geometry_name is not None):
      geometry = input_geodataframe.geometry
      input_geodataframe = input_geodataframe.drop(input_geodataframe.active_geometry_name, axis = 1)

    has_geometry = geometry is not None
    has_lat_or_long = latitude is not None or longitude is not None
    has_lat_and_long = latitude is not None and longitude is not None

    if isinstance(input_geodataframe, gpd.GeoDataFrame) and ((has_geometry and has_lat_or_long) or (not has_geometry and not has_lat_and_long)):
      raise ValueError("ModelBase requires latitude and longitude columns or only geometry column")

    #Select only the numeric columns if no data_columns is configured 
    input_geodataframe = input_geodataframe.loc[:, self.data_columns] if self.data_columns else input_geodataframe.select_dtypes(include='number')

    #Removing outliers from the target column
    if fit and self.__auto_config.task_type == ModelTask.REGRESSION and self.target_filter is not None and target is not None:
      ## 1 for inliers, -1 for outliers.
      self.mask_fit = self.target_filter.fit_predict(target) == 1
      
      target = target.loc[self.mask_fit]
      input_geodataframe = input_geodataframe.loc[self.mask_fit]

      if long_lat is not None:
        long_lat = long_lat[self.mask_fit]
      if geometry is not None:
        geometry = geometry[self.mask_fit]  

    #Feature selection
    if self.feature_selector:
      if fit:
        self.feature_selector.fit_transform(input_geodataframe)
      else:
        self.feature_selector.transform(input_geodataframe)  

      column_filter = self.feature_selector.get_support()
      input_geodataframe = input_geodataframe.loc[:, column_filter]

    #Feature scaling/normalization
    if self.feature_scaler:
      input_geodataframe = self.feature_scaler.fit_transform(input_geodataframe) if fit else self.feature_scaler.transform(input_geodataframe)

    return input_geodataframe, long_lat, geometry, None if target is None else target.to_numpy()

  def fit(
      self,
      input_geodataframe: Union[gpd.GeoDataFrame, pd.DataFrame],
      validation: Optional[Union[gpd.GeoDataFrame, pd.DataFrame]] = None,
      **kwargs,
  ) -> BaseEstimator:
    """
        It transforms data features and fit the model

        Args:
            input_geodataframe: The train dataset to fit the model
            validation: A validation dataset used to evaluate the training process, e.g., in a neural network training process.

        Returns:
            BaseEstimator: The final fitted model. 

        Examples:
            >>> from urban_mapper.modules.model import ModelBase
            # Creates with all default attributes
            >>> model = ModelBase()
            ...
            >>> model.fit(data)
    """  
    self.__fitted = True
    self.model = self.__auto_config.config_model(input_geodataframe, self.model, self.weight_path, self.target_column, self.longitude_column, self.latitude_column, self.geometry_column, **kwargs)

    self.target_filter = self.target_filter or IQROutlierDetector() if self.__auto_config.task_type == ModelTask.REGRESSION else None
    self.target_scaler = self.target_scaler or preprocessing.StandardScaler() if self.__auto_config.task_type == ModelTask.REGRESSION else None
    self.target_encoder = self.target_encoder or preprocessing.LabelEncoder() if self.__auto_config.task_type == ModelTask.CLASSIFICATION else None

    input_geodataframe, long_lat, geometry, target = self.transform(input_geodataframe)

    if self.__auto_config.task_type == ModelTask.REGRESSION:
      if self.weight_path is None and self.target_scaler is not None:
        self.model = TransformedTargetRegressor(regressor=self.model, transformer=self.target_scaler)        
      if self.weight_path is not None and isinstance(self.model, TransformedTargetRegressor):
        self.target_scaler = self.model.transformer

    if self.__auto_config.task_type == ModelTask.CLASSIFICATION:
      if self.weight_path is None and self.target_encoder is not None:
        self.model = TransformedTargetClassifier(classifier=self.model, transformer=self.target_encoder)        
      if self.weight_path is not None and isinstance(self.model, TransformedTargetClassifier):
        self.target_encoder = self.model.transformer

    send_coord = isinstance(self.model.regressor if isinstance(self.model, TransformedTargetRegressor) else self.model, (Kriging_Adapter, CustomModel_Adapter))
    send_geom  = isinstance(self.model.regressor if isinstance(self.model, TransformedTargetRegressor) else self.model, (ML_Lag_Adapter, CustomModel_Adapter))

    if send_coord:
      kwargs["long_lat"] = long_lat
    if send_geom:  
      kwargs["geometry"] = geometry

    if validation is not None:
      validation, val_long_lat, val_geometry, val_target = self.transform(validation, fit = False)

      kwargs["validation"] = validation
      kwargs["validation_target"] = val_target

      if send_coord:
        kwargs["validation_long_lat"] = val_long_lat
      if send_geom:  
        kwargs["validation_geometry"] = val_geometry

    return self.model.fit(input_geodataframe, target, **kwargs) if self.weight_path is None else self.model 
  
  def predict(
      self,
      input_geodataframe: Union[gpd.GeoDataFrame, pd.DataFrame],
      **kwargs,
  ) -> np.ndarray:
    """
        It transforms data features and returns the model prediction
        
        Args:
            input_geodataframe: The dataset in which the model runs predictions
            kwargs: Aditional arguments passed to the model

        Returns:
            np.ndarray: Model predictions 

        Examples:
            >>> from urban_mapper.modules.model import ModelBase
            # Creates with all default attributes
            >>> model = ModelBase()
            ...
            >>> model.fit(data)
    """             
    if not self.__fitted:
      msg = (
          "This %(name)s instance is not fitted yet. Call 'fit' with "
          "appropriate arguments before using this estimator."
      )
      raise NotFittedError(msg % {"name": type(self).__name__})
    
    input_geodataframe, long_lat, geometry, _ = self.transform(input_geodataframe, fit = False)
    send_coord = isinstance(self.model.regressor if isinstance(self.model, TransformedTargetRegressor) else self.model, Kriging_Adapter)
    send_geom  = isinstance(self.model.regressor if isinstance(self.model, TransformedTargetRegressor) else self.model, ML_Lag_Adapter)

    if send_coord:
      kwargs["long_lat"] = long_lat
    if send_geom:  
      kwargs["geometry"] = geometry

    return self.model.predict(input_geodataframe, **kwargs)
    
  def fit_predict(
      self,
      input_geodataframe: Union[gpd.GeoDataFrame, pd.DataFrame],
      **kwargs,
  ) -> Union[gpd.GeoDataFrame, pd.DataFrame]:
    """
        It splits the data into train, validation (if necessary), and test subset.
        Fits the model with the train/validation subsets and returns the pedictions for the input dataset 
        
        Args:
            input_geodataframe: The dataset to fit the model and in which the model runs predictions
            kwargs: Aditional arguments passed to the model

        Returns:
            GeoDataFrame: The input dataset with additonal columns indicating: the subset (train, validation, test)
                          and the predicted values for each data item.

        Examples:
            >>> from urban_mapper.modules.model import ModelBase
            # Creates with all default attributes
            >>> model = ModelBase()
            ...
            >>> model.fit_predict(data)
    """
    input_geodataframe = input_geodataframe.copy()

    if self.target_column is None:
      self.fit(input_geodataframe)

      input_geodataframe.loc[:, "subset"] = "train"
      input_geodataframe.loc[:, "cluster_predicted"] = self.model.labels_

      return input_geodataframe
    else:  
      kwargs.setdefault("train_size", self.train_size)
      kwargs.setdefault("test_size", self.test_size)
      kwargs.setdefault("random_state", 42)
      validation = None

      train, test = train_test_split(input_geodataframe, **kwargs)

      if self.validation_size is not None:
        kwargs["train_size"] = None
        kwargs["test_size"] = self.validation_size
        train, validation = train_test_split(train, **kwargs)

      self.fit(train, validation=validation)

      predicted_column = self.target_column + "_predicted"
      
      input_geodataframe.loc[test.index, "subset"] = "test"
      input_geodataframe.loc[test.index, predicted_column] = self.predict(test)

      if self.mask_fit is None:
        input_geodataframe.loc[train.index, "subset"] = "train"
        input_geodataframe.loc[train.index, predicted_column] =  self.predict(train)        
      else:  
        input_geodataframe.loc[train[self.mask_fit].index, "subset"] = "train"
        input_geodataframe.loc[train[self.mask_fit].index, predicted_column] =  self.predict(train[self.mask_fit])

      if validation is not None:
        input_geodataframe.loc[validation.index, "subset"] = "validation"
        input_geodataframe.loc[validation.index, predicted_column] = self.predict(validation)

      if not input_geodataframe[predicted_column].all():
        input_geodataframe[predicted_column] = input_geodataframe[predicted_column].astype(input_geodataframe[self.target_column].dtype)

      return input_geodataframe
