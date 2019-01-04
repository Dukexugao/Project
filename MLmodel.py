

#-------------------------------------------------------------------------------------#
###### After obtaining data from SQL Server, preprocessing and feature engineering #####
#-------------------------------------------------------------------------------------#

import sklearn
import scipy.io as scio
from sklearn.preprocessing import Imputer
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size=0.2, 
                                                    random_state=1234)
#-----------------------------------------------------------------------------#
############### deal with imbalanced data ###################################
#-----------------------------------------------------------------------------#

import imblearn
from imblearn.over_sampling import SMOTE
sm = SMOTE(random_state=12, ratio = 1.0)
x_train_res, y_train_res = sm.fit_sample(x_train, y_train)

#-----------------------------------------------------------------------------#
############### make model pipelines #########################################
#-----------------------------------------------------------------------------#
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import ElasticNet, Ridge, Lasso
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier

# Create pipelines dictionary
pipelines = {'rf' : make_pipeline(StandardScaler(), RandomForestClassifier(random_state=123)),
            'gb':  make_pipeline(StandardScaler(), GradientBoostingClassifier(random_state=123))
            }

# Check algorithms, and that they are all pipelines
for key, value in pipelines.items():
    print( key, type(value) )
#  Random forest hyperparameters
rf_hyperparameters = { 
    'randomforestclassifier__n_estimators' : [100, 200],
    'randomforestclassifier__max_features': ['auto', 'sqrt', 5, 15]
}
# Boosted tree hyperparameters
gb_hyperparameters = { 
    'gradientboostingclassifier__n_estimators': [100, 200],
    'gradientboostingclassifier__learning_rate' : [0.05, 0.1, 0.2],
    'gradientboostingclassifier__max_depth': [1, 3, 5]
}

# Create hyperparameters dictionary
hyperparameters = {
    'rf' : rf_hyperparameters,
    'gb' : gb_hyperparameters
}

###
for key in ['gb','rf']:
    if key in hyperparameters:
        if type(hyperparameters[key]) is dict:
            print( key, 'was found in hyperparameters, and it is a grid.' )
        else:
            print( key, 'was found in hyperparameters, but it is not a grid.' )
    else:
        print( key, 'was not found in hyperparameters')

#-----------------------------------------------------------------------------#
######################## cross-validaton ######################################
#-----------------------------------------------------------------------------#

from sklearn.model_selection import GridSearchCV        
fitted_models = {}
for name, pipeline in pipelines.items():
    # Create cross-validation object from pipeline and hyperparameters
    model = GridSearchCV(pipeline, hyperparameters[name], cv=10, n_jobs=-1)
    model.fit(x_train_res, y_train_res)
    fitted_models[name] = model
    print(name, 'has been fitted.')
    
#check error
from sklearn.exceptions import NotFittedError
for name, model in fitted_models.items():
    try:
        pred = model.predict(X_test)
        print(name, 'has been fitted.')
    except NotFittedError as e:
        print(repr(e))
        
# Display best_score_ for each fitted model
for name, model in fitted_models.items():
    print( name, model.best_score_ )
    
    
###
def report(results, n_top=3):
    for i in range(1, n_top+1):
        candidates = np.flatnonzero(results['rank_test_score'] == i)
        for candidate in candidates:
            print("Model wiht rank: {0}".format(i))
            print("Mean Validation Score: {0:.3f} (std: {1:.3f})".format(
                    results['mean_test_score'][candidate],
                    results['std_test_score'][candidate]))
            print("Parameters: {0}".format(results['params'][candidate]))
            print("")

#-----------------------------------------------------------------------------#
############### confusion matrix and f1 score report ##########################
#-----------------------------------------------------------------------------#
def my_confusion_matrix(y_true, y_pred):
    from sklearn.metrics import confusion_matrix
    labels = list(set(y_true))
    conf_mat = confusion_matrix(y_true, y_pred, labels=labels)
    print("confusion_matrix(left labels: y_true, up labels: y_pred):\n",conf_mat)
    
    
def my_classification_report(y_true, y_pred):
    from sklearn.metrics import classification_report
    print("classification_report(left: labels):")
    print(classification_report(y_true, y_pred))


#%%
    
print("Training:\n")
y_pred = fitted_models['rf'].predict(X_train)
my_confusion_matrix(y_train, y_pred)
my_classification_report(y_train, y_pred)
print("Testing:\n")
y_pred2 = fitted_models['rf'].predict(X_test)
my_confusion_matrix(y_test, y_pred2)
my_classification_report(y_test, y_pred2)

#-----------------------------------------------------------------------------#
############### save model for later use ######################################
#-----------------------------------------------------------------------------#
from sklearn.externals import joblib

joblib.dump(fitted_models['rf'], "rf_model.m")
joblib.dump(fitted_models['gb'], "gb_model.m")
