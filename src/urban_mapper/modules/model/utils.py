import numpy as np
import pdb
from sklearn.base import OutlierMixin, ClassifierMixin, BaseEstimator
from sklearn.preprocessing import LabelEncoder

class IQROutlierDetector(OutlierMixin):
  def __init__(self):
    self.__q1 = None
    self.__q3 = None

  def fit(self, X, y=None):
    self.__q1 = np.quantile(X, 0.25)
    self.__q3 = np.quantile(X, 0.75)

    return self

  def predict(self, X):
    iqr = self.__q3 - self.__q1

    labels = np.ones(len(X))
    outliers = (X < (self.__q1 - 1.5 * iqr)) | (X > (self.__q3 + 1.5 * iqr))
    labels[outliers] = -1

    ## 1 for inliers, -1 for outliers.
    return labels

class ThresholdOutlierDetector(OutlierMixin):
  def __init__(self, lower = None, upper = None):
    if lower is None and upper is None:
      raise Exception("ThresholdOutlierDetector needs at least one bound [lower or upper]")
    
    self.__lower_bound = lower
    self.__upper_bound = upper 

  def fit(self, X, y=None):
    return self

  def predict(self, X):
    labels = np.ones(len(X))

    if self.__lower_bound is not None:
      labels[X < self.__lower_bound] = -1
    if self.__upper_bound is not None:
      labels[X > self.__upper_bound] = -1      

    ## 1 for inliers, -1 for outliers.
    return labels
  
class TransformedTargetClassifier(ClassifierMixin, BaseEstimator):
  def __init__(
      self,
      classifier,
      transformer=LabelEncoder(),
  ):
      self.classifier = classifier
      self.transformer = transformer

  def fit(self, X, y, **fit_params):
    y_encoded = self.transformer.fit_transform(y)

    return self.classifier.fit(X, y_encoded, **fit_params)

  def predict(self, X, **predict_params):
    y_pred = self.classifier.predict(X, **predict_params)

    return self.transformer.inverse_transform(y_pred)

