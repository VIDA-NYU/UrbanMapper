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
  if mask is None:
    data.loc[subset.index, "subset"] = subset_name
    data.loc[subset.index, predicted_column] =  predicted_value
  else:  
    data.loc[subset[mask].index, "subset"] = subset_name
    data.loc[subset[mask].index, predicted_column] = predicted_value    

class AutoConfig():
  """Class that runs a basic model configuration based on data infomrations

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
      feature_mapper: A custom object that inherits scikit-learn TransformerMixin used to map features. 
                      If None, no mapping is done
      feature_selector: The name class name from scikit-learn or a custom object that inherits scikit-learn SelectorMixin used to select features. 
                        If None, it uses a feature_selection.VarianceThreshold as default
      feature_scaler:  The name class name from scikit-learn or a custom object that inherits scikit-learn TransformerMixin used to scale features. 
                       If None, it uses a preprocessing.StandardScaler as default
      target_filter:  The name class name from scikit-learn or a custom object that inherits scikit-learn BaseEstimator used to filter regression target outliers. 
                      If None, it uses a utils.IQROutlierDetector defined 
      target_scaler:  The name class name from scikit-learn or a custom object that inherits scikit-learn TransformerMixin used to scale regression targets. 
                      If None, it uses a preprocessing.StandardScaler as default
      target_encoder:  The name class name from scikit-learn or a custom object that inherits scikit-learn TransformerMixin used to encode classification targets. 
                      If None, it uses a preprocessing.LabelEncoder as default
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
    test_size: Optional[Union[int, float]] = None,
    target_column: Optional[str] = None,
    longitude_column: Optional[str] = None,
    latitude_column: Optional[str] = None,
    geometry_column: Optional[str] = None,
    feature_mapper: Optional[TransformerMixin] = None,
    feature_selector: Optional[Union[str, feature_selection.SelectorMixin]] = None,
    feature_scaler: Optional[Union[str, TransformerMixin]] = None,
    target_filter: Optional[Union[str, OutlierMixin]] = None,
    target_scaler: Optional[Union[str, TransformerMixin]] = None,
    target_encoder: Optional[Union[str, TransformerMixin]] = None,
    ignore_feature_on_scaler: Optional[Union[str, List]] = None,
    random_state: Optional[Union[int, np.random.RandomState]] = None,
  ):
    self.__auto_config = AutoConfig()
    self.__fitted = False

    self.model = model
    self.mask_outlier = None

    self.feature_mapper = feature_mapper
    self.feature_selector = feature_selector or feature_selection.VarianceThreshold(0.01)
    self.feature_scaler = feature_scaler or preprocessing.StandardScaler()
    self.ignore_feature_on_scaler = ignore_feature_on_scaler

    self.target_filter = target_filter
    self.target_scaler = target_scaler
    self.target_encoder = target_encoder

    self.weight_path = weight_path
    self.train_size = train_size
    self.validation_size = validation_size
    self.test_size = test_size or 0.1
    self.target_column = target_column
    self.longitude_column = longitude_column
    self.latitude_column = latitude_column
    self.geometry_column = geometry_column
    self.random_state = random_state or 42

  @property
  def fitted(self):
    return self.__fitted

  def transform(self, input_geodataframe: Union[gpd.GeoDataFrame, pd.DataFrame], fit = True) -> Tuple[Optional[Union[gpd.GeoDataFrame, pd.DataFrame, np.ndarray]], Optional[np.ndarray], Optional[gpd.GeoSeries], Optional[Union[pd.Series, np.ndarray]]]:
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

    #Extracting from input_geodataframe: target column
    if self.target_column is not None:
      target = input_geodataframe.loc[:, self.target_column]
      input_geodataframe = input_geodataframe.drop(self.target_column, axis = 1)

    if isinstance(self.model, Pipeline) or self.__auto_config.task_type == ModelTask.OTHERS:
      return input_geodataframe, long_lat, geometry, target

    #Extracting from input_geodataframe: longitude/latitude, geometry columns
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
    elif long_lat is None and hasattr(input_geodataframe, "active_geometry_name") and input_geodataframe.active_geometry_name is not None:
      geometry = input_geodataframe.pop(input_geodataframe.active_geometry_name)

    has_geometry = geometry is not None
    has_lat_or_long = latitude is not None or longitude is not None
    has_lat_and_long = latitude is not None and longitude is not None

    if isinstance(input_geodataframe, gpd.GeoDataFrame) and ((has_geometry and has_lat_or_long) or (not has_geometry and not has_lat_and_long)):
      raise ValueError("ModelBase requires latitude and longitude columns or only geometry column")

    #Removing outliers from the target column
    if self.__auto_config.task_type == ModelTask.REGRESSION and self.target_filter is not None and target is not None:
      ## 1 for inliers, -1 for outliers.
      self.mask_outlier = self.target_filter.fit_predict(target) == 1 if fit else self.target_filter.predict(target) == 1
      
      target = target.loc[self.mask_outlier]
      input_geodataframe = input_geodataframe.loc[self.mask_outlier]

      if long_lat is not None:
        long_lat = long_lat[self.mask_outlier]
      if geometry is not None:
        geometry = geometry[self.mask_outlier]  

    #Maps feature from one domain to another. For example, from categorical to one-hot-encod
    if self.feature_mapper:
      input_geodataframe = self.feature_mapper.fit_transform(input_geodataframe) if fit else self.feature_mapper.transform(input_geodataframe)  

    #Feature selection
    if self.feature_selector:
      if fit:
        self.feature_selector.fit_transform(input_geodataframe)
      else:
        self.feature_selector.transform(input_geodataframe)  

      column_filter = self.feature_selector.get_support()
      input_geodataframe = input_geodataframe.loc[:, column_filter]
    else:
      #Select only the numeric columns if no feature_selector is configured       
      input_geodataframe = input_geodataframe.select_dtypes(include='number')  

    #Feature scaling/normalization
    if self.feature_scaler:
      columns = input_geodataframe.columns if self.ignore_feature_on_scaler is None else [col for col in input_geodataframe.columns if col not in self.ignore_feature_on_scaler]
      input_geodataframe.loc[:, columns] = self.feature_scaler.fit_transform(input_geodataframe.loc[:, columns]) if fit else self.feature_scaler.transform(input_geodataframe.loc[:, columns])

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

    if not isinstance(self.model, Pipeline):
      self.target_filter = self.target_filter or IQROutlierDetector() if self.__auto_config.task_type == ModelTask.REGRESSION else None
      self.target_scaler = self.target_scaler or preprocessing.StandardScaler() if self.__auto_config.task_type == ModelTask.REGRESSION else None
      self.target_encoder = self.target_encoder or preprocessing.LabelEncoder() if self.__auto_config.task_type == ModelTask.CLASSIFICATION else None

    input_geodataframe, long_lat, geometry, target = self.transform(input_geodataframe)

    if isinstance(self.model, Pipeline) or self.__auto_config.task_type == ModelTask.OTHERS:
      return self.model.fit(input_geodataframe, target) if self.weight_path is None else self.model   

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
  ) -> Union[gpd.GeoDataFrame, pd.DataFrame, np.ndarray]:
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

    if (self.model is not None) and (isinstance(self.model, Pipeline) or not isinstance(self.model, (RegressorMixin, ClassifierMixin, ClusterMixin, str))):
      self.fit(input_geodataframe, **kwargs)

      return self.predict(input_geodataframe)
    elif self.target_column is None:
      self.fit(input_geodataframe, **kwargs)

      input_geodataframe.loc[:, "subset"] = "train"
      input_geodataframe.loc[:, "cluster_predicted"] = self.model.labels_

      return input_geodataframe
    else: 
      validation = None
      split_kwargs = {}  

      if self.train_size is not None:
        split_kwargs["train_size"] = self.train_size
      if self.test_size is not None:
        split_kwargs["test_size"] = self.test_size
      if self.random_state is not None:
        split_kwargs["random_state"] = self.random_state

      train, test = train_test_split(input_geodataframe, **split_kwargs)

      if self.validation_size is not None:
        split_kwargs["train_size"] = None
        split_kwargs["test_size"] = len(input_geodataframe) / len(train) * self.validation_size if isinstance(self.validation_size, float) else self.validation_size
        train, validation = train_test_split(train, **split_kwargs)

      predicted_column = self.target_column + "_predicted"

      self.fit(train, validation=validation, **kwargs)
      predicted_value = self.predict(train, **kwargs)
      _set_prediction(data=input_geodataframe, subset=train, subset_name="train", mask=self.mask_outlier, predicted_column=predicted_column, predicted_value=predicted_value)

      if validation is not None:
        predicted_value = self.predict(validation, **kwargs)   
        _set_prediction(data=input_geodataframe, subset=validation, subset_name="validation", mask=self.mask_outlier, predicted_column=predicted_column, predicted_value=predicted_value)

      predicted_value = self.predict(test, **kwargs)   
      _set_prediction(data=input_geodataframe, subset=test, subset_name="test", mask=self.mask_outlier, predicted_column=predicted_column, predicted_value=predicted_value)

      if not input_geodataframe[predicted_column].all():
        input_geodataframe[predicted_column] = input_geodataframe[predicted_column].astype(input_geodataframe[self.target_column].dtype)

      return input_geodataframe
