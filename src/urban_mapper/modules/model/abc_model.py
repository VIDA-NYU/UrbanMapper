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

from sklearn.base import BaseEstimator, RegressorMixin, ClassifierMixin, ClusterMixin, TransformerMixin
from sklearn import feature_selection, preprocessing 
from sklearn.cluster import KMeans
from sklearn.compose import TransformedTargetRegressor
from sklearn.exceptions import NotFittedError
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from sklearn.svm import *  #ex.: SVR
from sklearn.linear_model import * #ex.: LinearRegression
from sklearn.ensemble import *  #ex.: RandomForestRegressor

class ModelTask(IntEnum): 
  CLUSTERING = 0
  CLASSIFICATION = 1
  REGRESSION = 2
  OTHERS = 3

def _set_prediction(
      data: Union[gpd.GeoDataFrame, pd.DataFrame], 
      subset: Union[gpd.GeoDataFrame, pd.DataFrame], 
      subset_name: str, 
      mask: np.ndarray, 
      predicted_column: str, 
      predicted_value: np.ndarray):
  """
            
      Args:
          data: Original dataframe to be changed
          subset: Subset of the original dataframe
          subset_name: Subset name
          mask: mask applied over the subset data
          predicted_column: name of the predicted column
          predicted_value: value of the predicted column

      Returns:

      Examples:

  """  
  if mask is None:
    data.loc[subset.index, "subset"] = subset_name
    data.loc[subset.index, predicted_column] =  predicted_value
  else:  
    data.loc[subset[mask].index, "subset"] = subset_name
    data.loc[subset[mask].index, predicted_column] = predicted_value    

class AutoConfig():
  """Class that runs a basic model configuration based on data information

  """

  def __init__(self):
    self.__task_type = ModelTask.OTHERS

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
      random_state: Optional[Union[int, np.random.RandomState]] = None,
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
        kwargs.setdefault("random_state", random_state)
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

    if isinstance(model, ClusterMixin) or (isinstance(model, Pipeline) and np.any([ isinstance(stp, ClusterMixin) for stp in model.steps ])):
      self.__task_type = ModelTask.CLUSTERING
    elif  isinstance(model, ClassifierMixin) or (isinstance(model, Pipeline) and np.any([ isinstance(stp, ClassifierMixin) for stp in model.steps ])):
      self.__task_type = ModelTask.CLASSIFICATION  
    elif  isinstance(model, RegressorMixin) or (isinstance(model, Pipeline) and np.any([ isinstance(stp, RegressorMixin) for stp in model.steps ])):
      self.__task_type = ModelTask.REGRESSION

    if weight_path is not None:
      if isinstance(model, (ClusterMixin, ClassifierMixin, RegressorMixin, Pipeline)):
        model = joblib.load(weight_path)
      else:  
        model.load(weight_path)

    print("Autoconfig model:", model.regressor.__class__.__name__ if isinstance(model, TransformedTargetRegressor) else model.__class__.__name__)

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
      target_column: The name of the column containing target values to predict. 
      latitude_column: The name of the column containing latitude values.
      longitude_column: The name of the column containing longitude values.
      geometry_column: The name of column containing data geometry. If None, __auto_config uses the `active_geometry_name` from the geodataframe.   
      model_args: Specific arguments of non-custom model.
      feature_mapper: An object that inherits scikit-learn TransformerMixin used to map features. 
                      If None, no mapping is done
      feature_selector: An object that inherits scikit-learn SelectorMixin used to select features. 
                        If None or True, it uses a feature_selection.VarianceThreshold as default
      feature_scaler:  An object that inherits scikit-learn TransformerMixin used to scale features. 
                       If None or True, it uses a preprocessing.StandardScaler as default
      target_filter:  An object that inherits scikit-learn BaseEstimator used to filter regression target outliers. 
                      If None or True, it uses a utils.IQROutlierDetector defined 
      target_scaler:  An object that inherits scikit-learn TransformerMixin used to scale regression targets. 
                      If None or True, it uses a preprocessing.StandardScaler as default
      target_encoder:  An object that inherits scikit-learn TransformerMixin used to encode classification targets. 
                      If None or Nonte, it uses a preprocessing.LabelEncoder as default
      ignore_feature_on_scaler: A string or a list of strings with column names to be ignored during `feature_scaler` transformation
      train_size: Size of the training subset. 
      validation_size: Size of the validation subset. 
      test_size: Size of the test subset.
      random_state:  

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
    test_size: Optional[Union[bool, int, float]] = None,
    target_column: Optional[str] = None,
    longitude_column: Optional[str] = None,
    latitude_column: Optional[str] = None,
    geometry_column: Optional[str] = None,
    feature_mapper: Optional[TransformerMixin] = None,
    feature_selector: Optional[Union[bool, feature_selection.SelectorMixin]] = None,
    feature_scaler: Optional[Union[bool, TransformerMixin]] = None,
    target_filter: Optional[Union[bool, OutlierMixin]] = None,
    target_scaler: Optional[Union[bool, TransformerMixin]] = None,
    target_encoder: Optional[Union[bool, TransformerMixin]] = None,
    ignore_feature_on_scaler: Optional[Union[str, List]] = None,
    random_state: Optional[Union[int, np.random.RandomState]] = None,
  ):
    self.__auto_config = AutoConfig()
    self.__fitted = False
    self.__in_fit_predict = False

    self.model = model
    self.weight_path = weight_path

    self.feature_mapper = feature_mapper
    self.feature_selector = feature_selector
    self.feature_scaler = preprocessing.StandardScaler() if feature_scaler in (None, True) else feature_scaler
    self.ignore_feature_on_scaler = ignore_feature_on_scaler

    ## Default transformers are defined inside self.fit bacause they depend on the created model
    self.target_filter = target_filter
    self.target_scaler = target_scaler
    self.target_encoder = target_encoder
    self.mask_outlier = None

    self.train_size = train_size
    self.validation_size = validation_size
    self.test_size = 0.1 if test_size in (None, True) else test_size

    self.target_column = target_column
    self.longitude_column = longitude_column
    self.latitude_column = latitude_column
    self.geometry_column = geometry_column

    self.random_state = random_state or 42

  @property
  def fitted(self):
    return self.__fitted

  def __extract_target(self, input_geodataframe: Union[gpd.GeoDataFrame, pd.DataFrame]) -> Tuple[Optional[Union[gpd.GeoDataFrame, pd.DataFrame]], Optional[pd.Series]]:  
    """
        It extracts the target column if self.target_column is defined

        Args:
            input_geodataframe: Original (geo)dataframe

        Returns:
            Union[gpd.GeoDataFrame, pd.DataFrame]: Original input_geodataframe without the target
            pd.Series: Target column from the input_geodataframe 

        Examples:

    """      
    target = None

    if self.target_column is not None:
      target = input_geodataframe.loc[:, self.target_column]
      input_geodataframe = input_geodataframe.drop(self.target_column, axis = 1)

    return input_geodataframe, target

  def __extract_spatial_features(self, input_geodataframe: Union[gpd.GeoDataFrame, pd.DataFrame]) -> Tuple[Optional[Union[gpd.GeoDataFrame, pd.DataFrame]], Optional[np.ndarray], Optional[gpd.GeoSeries]]:
    """
        It extracts the lat/long or geometry columns if they are defined

        Args:
            input_geodataframe: Original (geo)dataframe

        Returns:
            Union[gpd.GeoDataFrame, pd.DataFrame]: Original input_geodataframe without spatial columns
            np.ndarray: information of longitude-latitude
            gpd.GeoSeries: geometry information

        Examples:

    """       
    longitude, latitude, long_lat, geometry = None, None, None, None

    if self.longitude_column is not None:
      longitude = input_geodataframe.loc[:, self.longitude_column]
      input_geodataframe = input_geodataframe.drop(self.longitude_column, axis = 1)
    if self.latitude_column is not None:
      latitude = input_geodataframe.loc[:, self.latitude_column]
      input_geodataframe = input_geodataframe.drop(self.latitude_column, axis = 1)
    if self.longitude_column is not None and self.latitude_column is not None:
      long_lat = np.array([ [x, y] for x, y in  zip(longitude, latitude)])
    if self.geometry_column is not None:
      geometry = input_geodataframe.pop(self.geometry_column)
    elif hasattr(input_geodataframe, "active_geometry_name") and input_geodataframe.active_geometry_name is not None:
      geometry = input_geodataframe.pop(input_geodataframe.active_geometry_name)

    has_geometry = geometry is not None
    # has_lat_or_long = latitude is not None or longitude is not None
    has_lat_and_long = latitude is not None and longitude is not None

    # if isinstance(input_geodataframe, gpd.GeoDataFrame) and ((has_geometry and has_lat_or_long) or (not has_geometry and not has_lat_and_long)):
    if isinstance(input_geodataframe, gpd.GeoDataFrame) and not has_geometry and not has_lat_and_long:      
      raise ValueError("ModelBase requires latitude and longitude columns or only geometry column")      

    return input_geodataframe, long_lat, geometry

  def __remove_target_outliers(self, input_geodataframe: Union[gpd.GeoDataFrame, pd.DataFrame], long_lat: Optional[np.ndarray], geometry: Optional[gpd.GeoSeries], target: Optional[pd.Series], fit: Optional[bool] = True) -> Tuple[Union[gpd.GeoDataFrame, pd.DataFrame], Optional[np.ndarray], Optional[gpd.GeoSeries], Optional[pd.Series]]:
    """
        Only for regression, it filters input based on outliers of the target column

        Args:
            input_geodataframe: Original (geo)dataframe
            long_lat: information of longitude-latitude
            geometry: geometry information
            target: target information
            fit: if True, it fits the transformer. if False, only applies the transformation
            
        Returns:
            Union[gpd.GeoDataFrame, pd.DataFrame]: Filtered input_geodataframe
            np.ndarray: Filtered longitude-latitude
            gpd.GeoSeries: Filtered geometry column
            gpd.GeoSeries: Filtered target column

        Examples:

    """       
    if self.__auto_config.task_type == ModelTask.REGRESSION and self.target_filter is not None and target is not None:
      ## 1 for inliers, -1 for outliers.
      self.mask_outlier = self.target_filter.fit_predict(target) == 1 if fit else self.target_filter.predict(target) == 1
      
      target = target.loc[self.mask_outlier]
      input_geodataframe = input_geodataframe.loc[self.mask_outlier]

      if long_lat is not None:
        long_lat = long_lat[self.mask_outlier]
      if geometry is not None:
        geometry = geometry[self.mask_outlier]

    return input_geodataframe, long_lat, geometry, target

  def __map_features(self, input_geodataframe: Union[gpd.GeoDataFrame, pd.DataFrame], fit: Optional[bool] = True) -> Union[gpd.GeoDataFrame, pd.DataFrame]:
    """
        Used to map features from one to another domain. For example, categorical features that should be one-hot-encoded

        Note: `fit_predict` applies it before any other method to avoid missing values.

        Args:
            input_geodataframe: Original (geo)dataframe features
            fit: if True, it fits the transformer. if False, only applies the transformation
            
        Returns:
            Union[gpd.GeoDataFrame, pd.DataFrame]: 

        Examples:

    """       
    if self.feature_mapper and not self.__in_fit_predict:
      input_geodataframe = self.feature_mapper.fit_transform(input_geodataframe) if fit else self.feature_mapper.transform(input_geodataframe)  

    return input_geodataframe  
  
  def __select_features(self, input_geodataframe: Union[gpd.GeoDataFrame, pd.DataFrame], fit: Optional[bool] = True) -> Union[gpd.GeoDataFrame, pd.DataFrame]:
    """
        Used to select features based on same criterion. If no external selection is defined, it will select only the numeric features

        Args:
            input_geodataframe: Original (geo)dataframe features
            fit: if True, it fits the transformer. if False, only applies the transformation
            
        Returns:
            Union[gpd.GeoDataFrame, pd.DataFrame]: A (geo)dataframe only with the selected features

        Examples:

    """        
    if self.feature_selector in (None, True):
      input_geodataframe = input_geodataframe.select_dtypes(include='number')  
    elif self.feature_selector is not None:
      if fit:
        self.feature_selector.fit_transform(input_geodataframe)
      else:
        self.feature_selector.transform(input_geodataframe)  

      column_filter = self.feature_selector.get_support()
      input_geodataframe = input_geodataframe.loc[:, column_filter]

    return input_geodataframe    
    
  def __scale_features(self, input_geodataframe: Union[gpd.GeoDataFrame, pd.DataFrame], fit: Optional[bool] = True) -> Union[gpd.GeoDataFrame, pd.DataFrame]:
    """
        Used to scale features that are not listed on self.ignore_feature_on_scaler. For example, one-hot-encoded features should not be rescaled.

        Args:
            input_geodataframe: Original (geo)dataframe features
            fit: if True, it fits the transformer. if False, only applies the transformation
            
        Returns:
            Union[gpd.GeoDataFrame, pd.DataFrame]: A (geo)dataframe with rescaled features

        Examples:

    """      
    if self.feature_scaler:
      columns = input_geodataframe.columns if self.ignore_feature_on_scaler is None else [col for col in input_geodataframe.columns if col not in self.ignore_feature_on_scaler]
      input_geodataframe.loc[:, columns] = self.feature_scaler.fit_transform(input_geodataframe.loc[:, columns]) if fit else self.feature_scaler.transform(input_geodataframe.loc[:, columns])

    return input_geodataframe

  def __set_target_transform(self):
    """
        Used to initialize target filter used in __remove_target_outliers, and target_scaler (Regression) or target_encoder (Classification).

        Args:
            
        Returns:

        Examples:

    """      
    if not isinstance(self.model, Pipeline):
      if self.__auto_config.task_type == ModelTask.REGRESSION:
        self.target_filter = IQROutlierDetector() if self.target_filter in (None, True) else self.target_filter
        self.target_scaler = preprocessing.StandardScaler() if self.target_scaler in (None, True) else self.target_scaler
        self.target_encoder = None
      else:  
        self.target_filter = self.target_scaler = None

        if self.__auto_config.task_type == ModelTask.CLASSIFICATION:
          self.target_encoder = preprocessing.LabelEncoder() if self.target_encoder in (None, True) else self.target_encoder
        else:
          self.target_encoder = None

  def __create_model_wrapper(self):
    """
        Used to wrap model and target_scaler in the same TransformedTargetRegressor or model and self.target_encoder in the same TransformedTargetClassifier helper

        Args:
            
        Returns:

        Examples:

    """     
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

  def __train_val_test_split(self, input_geodataframe: Union[gpd.GeoDataFrame, pd.DataFrame]) -> Tuple[Optional[Union[gpd.GeoDataFrame, pd.DataFrame]], Optional[Union[gpd.GeoDataFrame, pd.DataFrame]], Optional[Union[gpd.GeoDataFrame, pd.DataFrame]]]:
    """
        Used to split a dataframe in train, validation, and test subsets if there are specifica configurations: train_size, validation_size, test_size
        By default, only test_size = 0.1, and consequently train-size = 0.9

        Args:
            input_geodataframe: Original (geo)dataframe
            
        Returns:
            Union[gpd.GeoDataFrame, pd.DataFrame]: A train subset (Default 90% of the input_geodataframe)
            Union[gpd.GeoDataFrame, pd.DataFrame]: A validation subset
            Union[gpd.GeoDataFrame, pd.DataFrame]: A test subset (Default 10% of the input_geodataframe)

        Examples:

    """      
    train = validation = test = None
    split_kwargs = {}  

    if self.train_size:
      split_kwargs["train_size"] = self.train_size
    if self.test_size:
      split_kwargs["test_size"] = self.test_size
    if self.random_state:
      split_kwargs["random_state"] = self.random_state

    if self.train_size or self.test_size:
      train, test = train_test_split(input_geodataframe, **split_kwargs)

    if self.validation_size:
      split_kwargs["train_size"] = None
      split_kwargs["test_size"] = len(input_geodataframe) / len(train) * self.validation_size if isinstance(self.validation_size, float) else self.validation_size
      train, validation = train_test_split(train, **split_kwargs)

    return train, validation, test          

  def transform(self, input_geodataframe: Union[gpd.GeoDataFrame, pd.DataFrame], fit = True) -> Tuple[Optional[Union[gpd.GeoDataFrame, pd.DataFrame, np.ndarray]], Optional[np.ndarray], Optional[gpd.GeoSeries], Optional[Union[pd.Series, np.ndarray]]]:
    """
      In the following order:
      1. Extract target from the dataframe (Only for classification and regression)
      2. Extract longitude-latitude or geometry from the dataframe. If no column configuration exists, it will return the active_geometry_name of the GeoDataFrame
      3. Remove data rows based on target outliers (Only for regression)
      4. Map features to different domains. For example, from categorical to one-hot-encoding or from integer to float (No default action)
      5. Select features. If False, no selection is applied (select only the numeric columns by default)
      6. Scale features (`scikit-learn` StandardScaler() by default)

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
    input_geodataframe = input_geodataframe.copy()
    target, long_lat, geometry = None, None, None

    input_geodataframe, target = self.__extract_target(input_geodataframe)

    if isinstance(self.model, Pipeline) or self.__auto_config.task_type == ModelTask.OTHERS:
      return input_geodataframe, long_lat, geometry, target
    
    input_geodataframe, long_lat, geometry = self.__extract_spatial_features(input_geodataframe)

    input_geodataframe, long_lat, geometry, target = self.__remove_target_outliers(input_geodataframe, long_lat, geometry, target, fit)

    input_geodataframe = self.__map_features(input_geodataframe, fit)

    input_geodataframe = self.__select_features(input_geodataframe, fit)

    input_geodataframe = self.__scale_features(input_geodataframe, fit)    

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
    
    self.model = self.__auto_config.config_model(
      input_geodataframe=input_geodataframe, 
      model=self.model, 
      weight_path=self.weight_path, 
      target_column=self.target_column, 
      longitude_column=self.longitude_column, 
      latitude_column=self.latitude_column, 
      geometry_column=self.geometry_column, 
      random_state=self.random_state, 
      **kwargs)

    self.__set_target_transform()

    input_geodataframe, long_lat, geometry, target = self.transform(input_geodataframe)

    if isinstance(self.model, Pipeline) or self.__auto_config.task_type == ModelTask.OTHERS:
      return self.model.fit(input_geodataframe, target) if self.weight_path is None else self.model   

    self.__create_model_wrapper()

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
  ) -> Union[gpd.GeoDataFrame, pd.DataFrame, np.ndarray]:
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
    
    if isinstance(self.model, Pipeline) or self.__auto_config.task_type == ModelTask.OTHERS:
      return self.model.predict(input_geodataframe)

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
        Finally, add to the original dataframe, predictions for train, validaiton, and test subsets.
        
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

    if (self.model is not None) and (isinstance(self.model, Pipeline) or not isinstance(self.model, (RegressorMixin, ClassifierMixin, ClusterMixin, str))):
      self.fit(input_geodataframe, **kwargs)

      return self.predict(input_geodataframe)
    elif self.target_column is None:
      self.fit(input_geodataframe, **kwargs)

      input_geodataframe.loc[:, "subset"] = "train"
      input_geodataframe.loc[:, "cluster_predicted"] = self.model.labels_

      return input_geodataframe
    else: 
      mapped_geodataframe = self.__map_features(input_geodataframe, True)
      train, validation, test = self.__train_val_test_split(mapped_geodataframe)
      self.__in_fit_predict = True

      try:
        predicted_column = self.target_column + "_predicted"
        self.fit(mapped_geodataframe if train is None else train, validation=validation, **kwargs)
        predicted_value = self.predict(mapped_geodataframe if train is None else train, **kwargs)

        is_custom_model = isinstance(self.model.regressor if isinstance(self.model, TransformedTargetRegressor) else self.model, CustomModel_Adapter)

        if train is None and is_custom_model:
          model = self.model.regressor_ if isinstance(self.model, TransformedTargetRegressor) else self.model
          model.set_prediction(X=input_geodataframe, mask_outlier=self.mask_outlier, y_predicted_column=predicted_column, y_predicted=predicted_value) 
        else:
          _set_prediction(data=input_geodataframe, subset=train, subset_name="train", mask=self.mask_outlier, predicted_column=predicted_column, predicted_value=predicted_value)

        if validation is not None:
          predicted_value = self.predict(validation, **kwargs)   
          _set_prediction(data=input_geodataframe, subset=validation, subset_name="validation", mask=self.mask_outlier, predicted_column=predicted_column, predicted_value=predicted_value)

        if test is not None:
          predicted_value = self.predict(test, **kwargs)   
          _set_prediction(data=input_geodataframe, subset=test, subset_name="test", mask=self.mask_outlier, predicted_column=predicted_column, predicted_value=predicted_value)
      finally:
        self.__in_fit_predict = False

      if not input_geodataframe[predicted_column].all():
        input_geodataframe[predicted_column] = input_geodataframe[predicted_column].astype(input_geodataframe[self.target_column].dtype)

      return input_geodataframe
