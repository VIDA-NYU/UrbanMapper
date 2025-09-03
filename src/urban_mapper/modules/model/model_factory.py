
import geopandas as gpd
import pdb

from beartype import beartype
from typing import Union, Optional, Dict, List
from sklearn.base import BaseEstimator, OutlierMixin
from .abc_model import ModelBase

@beartype
class ModelFactory:
  """Factory Class For Creating and Configuring `Models`.

  This class offers a fluent, chaining-methods interface for crafting and setting up
  `models` in the `UrbanMapper` workflow. `Models` can be any machine learning approach
  that coulde used to predict geospatial-data information.

  The factory handles the nitty-gritty of `model` instantiation, ensuring a uniform 
  workflow no matter the model type.

  Attributes:
      _instance: The actual model object
      model: The name class name from scikit-learn or a custom object that inherits scikit-learn BaseEstimator. 
      weight_path: The path to load saved model weights.
      data_columns: List of column names containing values used to train a model.
      target_column: The name of the column containing target values to predict.
      latitude_column: The name of the column containing latitude values.
      longitude_column: The name of the column containing longitude values.
      geometry_column: The name of column containing data geometry. 
      model_args: Specific arguments of non-custom model.
      feature_selector: The name class name from scikit-learn or a custom object that inherits scikit-learn BaseEstimator used to select features. 
      feature_scaler:  The name class name from scikit-learn or a custom object that inherits scikit-learn BaseEstimator used to scale features. 
      target_filter:  The name class name from scikit-learn or a custom object that inherits scikit-learn BaseEstimator used to filter target outliers. 
      target_scaler:  The name class name from scikit-learn or a custom object that inherits scikit-learn BaseEstimator used to scale regression targets. 
      train_size: Size of the training subset. 
      validation_size: Size of the validation subset. 
      test_size: Size of the test subset. 

  Examples:
      >>> import urban_mapper as um
      >>> data = mapper.loader.from_file("taxisvis1M.csv").with_columns(longitude_column="pickup_longitude", latitude_column="pickup_latitude").load()
      >>> mapper = um.UrbanMapper()
      >>> model = mapper.model\
      ...     .with_model("SVR")\
      ...     .with_columns(target_column="total_amount")
      >>> model_out = model.fit_predict(data)
  """

  def __init__(self):
    self._instance: BaseEstimator = None
    self.model: Optional[Union[str, BaseEstimator]] = None
    self.weight_path: Optional[str] = None
    self.data_columns: Optional[List[str]] = None
    self.target_column: Optional[str] = None
    self.longitude_column: Optional[str] = None
    self.latitude_column: Optional[str] = None
    self.geometry_column: Optional[str] = None
    self._instance_args: Optional[Dict] = {}
    self.feature_selector: Optional[Union[str, BaseEstimator]] = None
    self.feature_scaler: Optional[Union[str, BaseEstimator]] = None
    self.target_filter: Optional[Union[str, OutlierMixin]] = None
    self.target_scaler: Optional[Union[str, BaseEstimator]] = None    
    self.target_encoder: Optional[Union[str, BaseEstimator]] = None
    self.train_size: Optional[Union[int, float]] = None    
    self.validation_size: Optional[Union[int, float]] = None    
    self.test_size: Optional[Union[int, float]] = None  

  def _reset(self):
    self._instance = None
    self.model = None
    self.weight_path = None
    self.data_columns = None
    self.target_column = None
    self.longitude_column = None
    self.latitude_column = None
    self.geometry_column = None
    self._instance_args = {}
    self.feature_selector = None
    self.feature_scaler = None
    self.target_filter = None
    self.target_scaler = None
    self.target_encoder = None
    self.train_size = None
    self.validation_size = None
    self.test_size = None

  def with_transform(self, 
                     feature_selector: Optional[Union[str, BaseEstimator]] = None, 
                     feature_scaler: Optional[Union[str, BaseEstimator]] = None, 
                     target_filter: Optional[Union[str, OutlierMixin]] = None, 
                     target_scaler: Optional[Union[str, BaseEstimator]] = None,
                     target_encoder: Optional[Union[str, BaseEstimator]] = None,):
    """
        Args:
            feature_selector: if not None, it selects the bests features based on a criterion. VarianceThreshold(0.01) (default)
            feature_scaler: if not None, it rescales all the numeric features. StandardScaler (default)
            target_filter: if not None, it filters outliers in the target column of regression tasks. utils.IQROutlierDetector (default)
            target_scaler if not None, it rescales the target column of regression tasks. StandardScaler (default)
            target_encoder if not None, it rescales the target column of classification tasks. LabelEncoder (default)

        Returns:
            The ModelFactory instance for chaining.

        Examples:
            >>> import urban_mapper as um
            >>> mapper = um.UrbanMapper()
            >>> model = mapper.model.with_transform(target_scaler=MinMaxScaler())    
            >>> 
    """    
    self.feature_selector = feature_selector
    self.feature_scaler = feature_scaler
    self.target_filter = target_filter
    self.target_scaler = target_scaler
    self.target_encoder = target_encoder

    return self

  def with_model(self, model: Optional[Union[str, BaseEstimator]] = None, weight_path: Optional[str] = None, **kwargs) -> "ModelFactory":
    """
        Args:
            model: if a string, it is a class name in sklearn modules svm, linear_model, ensamble, or in pykrige modules
                   if an objection, it is an object decendent from sklearn BaseEstimator
                   otherwise, the factory will use a standard model
            ***kwargs: arguments to be passed to the model constructor

        Returns:
            The ModelFactory instance for chaining.

        Examples:
            >>> import urban_mapper as um
            >>> mapper = um.UrbanMapper()
            >>> model = mapper.model.with_model(model="SVR")    
            >>> 
            >>> model = mapper.model.with_model(model="RandomForestRegressor")    
            >>> 
            >>> model = mapper.model.with_model(model="LinearRegression")   
            >>> 
            >>> model = mapper.model.with_model(model="RegressionKriging")
            >>>
            >>> model = mapper.model.with_model(model=MyEstimator())
    """
    self._reset()
    self.model = model
    self.weight_path = weight_path
    self._instance_args = kwargs

    return self
  
  def with_columns(self, data_columns: Optional[List[str]] = None, target_column: Optional[str] = None, longitude_column: Optional[str] = None, latitude_column: Optional[str] = None, geometry_column: Optional[str] = None) -> "ModelFactory":
    """
        Args:
          data_columns: List of column names containing values used to train a model.
          target_column: The name of the column containing target values to predict.
          latitude_column: The name of the column containing latitude values.
          longitude_column: The name of the column containing longitude values.
          geometry_column: The name of column containing data geometry. 

        Returns:
            The ModelFactory instance for chaining.

        Examples:
            >>> import urban_mapper as um
            >>> mapper = um.UrbanMapper()
            >>> model = mapper.model.with_columns(data_columns=["passenger_count", "trip_distance"])
            >>>
            >>> model = mapper.model.with_columns(target_column="total_amount")    
            >>> 
            >>> model = mapper.model.with_columns(latitude_column="x", longitude_column="y")    
            >>> 
            >>> model = mapper.model.with_columns(geometry_column="the_geom")    
    """    
    self.data_columns = data_columns
    self.target_column = target_column
    self.longitude_column = longitude_column
    self.latitude_column = latitude_column
    self.geometry_column = geometry_column

    return self

  def with_data(self, train_size: Optional[Union[int, float]] = None, validation_size: Optional[Union[int, float]] = None, test_size: Optional[Union[int, float]] = None) -> "ModelFactory":
    """
        Args:
          train_size: Number that defines the number (int) or percentage (float) of samples of the data, used for model training
          validation_size: Number that defines the number (int) or percentage (float) of samples of the data, used for model validation
          test_size:  Number that defines the number (int) or percentage (float) of samples of the data, used for model testing

        Returns:
            The ModelFactory instance for chaining.

        Examples:
            >>> import urban_mapper as um
            >>> mapper = um.UrbanMapper()
            >>> model = mapper.model.with_data(train_size=0.8, validation_size=0.1, test_size=0.1)
            >>>
            >>> model = mapper.model.with_data(train_size=950, test_size=50)
    """        
    self.train_size = train_size
    self.validation_size = validation_size
    self.test_size = test_size

    return self

  def build(self) -> ModelBase:
    """Build and return a `model` instance without fitting the data.
    
    This method creates and returns a model instance without immediately fitting
    the data. It is primarily intended for use in the `UrbanPipeline`, where the
    actual fitting is deferred until pipeline execution.
    
    Returns:
        A ModelBase instance configured to fit the data when needed.
        
    Examples:
        >>> # Creating a pipeline component
        >>> model = mapper
        ...     .model\
        ...     .build()
    """    
    self._instance = ModelBase(
      #model
      model=self.model,
      weight_path=self.weight_path,

      #data config
      train_size=self.train_size,
      validation_size=self.validation_size,
      test_size=self.test_size,

      #dataset columns
      data_columns=self.data_columns, 
      target_column=self.target_column,
      longitude_column=self.longitude_column,
      latitude_column=self.latitude_column,
      geometry_column=self.geometry_column,
      
      #transform/preprocessing steps
      feature_selector=self.feature_selector,
      feature_scaler=self.feature_scaler,
      target_filter=self.target_filter, 
      target_scaler=self.target_scaler,
      target_encoder=self.target_encoder,    
    )

    return self._instance
