import pandas as pd
import urban_mapper as um
import numpy as np
import pytest

from sklearn.cluster import DBSCAN
from sklearn.svm import SVR
from sklearn.preprocessing import  MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import TransformedTargetRegressor, ColumnTransformer, make_column_selector
from sklearn.base import BaseEstimator, TransformerMixin, RegressorMixin
from sklearn.feature_selection import SelectorMixin

from urban_mapper.modules.model import ModelFactory, CustomModel_Adapter, ZScoreOutlierDetector

class MyRegressor(RegressorMixin, CustomModel_Adapter):
  def __init__(self):
    pass

  def fit(self, X, y, **kwargs):
    return self

  def predict(self, X, **kwargs):
    return np.zeros(X.shape[0])
  
class GeneralModel(CustomModel_Adapter):
  def __init__(self):
    pass

  def fit(self, X, y, **kwargs):
    return self

  def predict(self, X, **kwargs):
    return X
 
class MyFeatureMapping(TransformerMixin, BaseEstimator):
   def __init__(self, map_payment = True):
      pass

   def fit(self, X, y=None):
     return self
   
   def transform(self, X):
      if "payment_type" in X:
        X = pd.get_dummies(X, columns=['payment_type',], dtype = int)

      return X

   def __sklearn_tags__(self):
      tags = super().__sklearn_tags__()
      tags.input_tags.allow_nan = True

      return tags  

class MyFeatureSelection(SelectorMixin, BaseEstimator):
   def __init__(self):
      self.__mask = None

   def fit(self, X, y=None):
      self.feature_names_in_ = X.columns.tolist() if isinstance(X, pd.DataFrame) else [f"x{i}" for i in range(X.shape[1])]
      self.__mask = np.zeros(X.shape[1], dtype=bool) #True: keep feature, False: remove feature
      columns = list(X.columns)

      for cl in X.select_dtypes(include='number').columns:
        self.__mask[columns.index(cl)] = True
        
      return self

   def __sklearn_tags__(self):
      tags = super().__sklearn_tags__()
      tags.input_tags.allow_nan = True

      return tags
   
   def _get_support_mask(self):
      return self.__mask

# @pytest.mark.skip()
class TestModelBase:
  loader = um.UrbanMapper().loader
  model = um.UrbanMapper().model

  file_path = "test/data_files/small_2010_Yellow_Taxi_Trip_Data.csv"
  data = (
      loader
      .from_file(file_path)
      .with_columns(geometry_column="pickup_location")
      .with_map({"pickup_location": "geometry"})
      .load()
  )

  scikit_pipeline = Pipeline([
    ("feature_scaler", ColumnTransformer([
      ("selector", MinMaxScaler(), make_column_selector(dtype_include="number"))
    ])),
    ("model", TransformedTargetRegressor(regressor=SVR(), transformer=MinMaxScaler()))
  ])  

  def test_build(self):
    """
    Default K-Means clustering
    """    
    assert self.model.build() is not None 

    """
    Default SVR regression
    """
    (
      self
      .model
      .with_columns(target_column="total_amount")
    ) 
    assert self.model.build() is not None

    """
    Default Kringing regression
    """
    (
      self
      .model
      .with_columns(longitude_column="pickup_longitude", latitude_column="pickup_latitude", target_column="total_amount")
    )
    assert self.model.build() is not None    

    """
    Default ML_Lag regression
    """
    (
      self
      .model
      .with_columns(geometry_column="geometry", target_column="total_amount")
    )
    assert self.model.build() is not None      

    """
    Default SVM classifier
    """
    (
      self
      .model
      .with_columns(target_column="payment_type")
    )
    assert self.model.build() is not None          

    """
    Passing a model string name     
    """
    (
      self
      .model
      .with_model(model="RandomForestRegressor")
      .with_columns(target_column="total_amount")
    )
    assert self.model.build() is not None              

    """
    Passing an object as model
    """
    (
      self
      .model
      .with_model(model=DBSCAN())
      .with_columns(target_column="total_amount")
    )
    assert self.model.build() is not None                  

    """
    Passing a scikit-learn pipeline
    """
    (
      self
      .model
      .with_model(model=self.scikit_pipeline)
      .with_columns(target_column="total_amount")
    )
    assert self.model.build() is not None                      

    """
    Passing a Custom Regressor/Classifier/Clusterer
    """
    (
      self
      .model
      .with_model(model=MyRegressor())
      .with_columns(target_column="total_amount")
    )
    assert self.model.build() is not None                      

    """
    Passing a Custom Model
    """
    (
      self
      .model
      .with_model(model=GeneralModel())
      .with_columns(target_column="total_amount")
    ) 
    assert self.model.build() is not None

    """
    Using `with_data` to change the basic split train:validation:test 
    """
    (
      self
      .model
      .with_model(model=GeneralModel())
      .with_columns(target_column="total_amount")
      .with_data(train_size=0.70, validation_size=0.15, test_size=0.15)
    ) 
    assert self.model.build() is not None   

    """
    Using `with_transform` to customize the basic data transformations
    """
    (
      self
      .model
      .with_columns(target_column="total_amount")
      .with_transform(
        feature_mapper=MyFeatureMapping(),
        feature_selector=MyFeatureSelection(),
        feature_scaler=MinMaxScaler(),

        target_filter=ZScoreOutlierDetector(), 
        target_scaler=MinMaxScaler(),
        # target_encoder=self.target_encoder,   
        
        ignore_feature_on_scaler=["payment_type_CRD", "payment_type_CSH"],        
      )
    )
    assert self.model.build() is not None

    """
    Using `with_transform` to disable data transformations
    """
    (
      self
      .model
      .with_columns(target_column="total_amount")
      .with_transform(
        feature_mapper=None, 
        feature_selector=MyFeatureSelection(), 
        feature_scaler=False, 

        target_filter=False,  
        target_scaler=False,  
        # target_encoder=target_encoder, 
        
        # ignore_feature_on_scaler=ignore_feature_on_scaler,       
      )
    )
    assert self.model.build() is not None                                 
