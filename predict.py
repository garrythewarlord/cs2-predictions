

# import dependancies
import pandas as pd
from sklearn.metrics import precision_score, accuracy_score
from sklearn.ensemble import RandomForestClassifier



def Predict(dist, save):

    # init rf object
    rf = RandomForestClassifier(max_depth=5, max_features=7, min_samples_leaf=3, min_samples_split=2, n_estimators=100)

    # import data
    data = pd.read_csv('data.csv', encoding='unicode_escape')

    # create predictor columnn; init predictors
    data['venue_code'] = data['event'].astype('category').cat.codes
    data['ranking_opponent_code'] = data['opponent-ranking']
    predictors = ['venue_code', 'ranking_opponent_code']

    # create target column
    data['target'] = (data['result'] == 'W').astype('int')


    # split the data into train and test sets
    train = data[data['index'] > dist]
    test = data[data['index'] < dist]

    # train the model / predict test set
    rf.fit(train[predictors].values, train['target'].values)
    predictions = rf.predict(test[predictors].values)

    # calculate accuracy and precisiaon scores
    accuracy = accuracy_score(test['target'], predictions)
    precision = precision_score(test['target'], predictions)


    # create new dataframe to display results
    results = {
        'date': test['date'],
        'team': test['team'],
        'opponent': test['opponent'],
        'result': test['result'],
        'predicted': ['W' if pred == 1 else 'L' for pred in predictions],
    }
    final_data = pd.DataFrame(results)

    # check if results need to be saved to .csv
    if save:
        final_data.to_csv('predictions.csv', index=True)

    # return results
    return {
        'results': final_data,
        'accuracy': accuracy,
        'precision': precision,
        'predictors': predictors,
        'rf': rf
    }


def Single_Predict(rf, row, predictors):
    predictions = rf.predict(row[predictors].values.reshape(1, -1))
    res = 'W' if predictions == 1 else 'L'
    return [row['date'], row['team'], row['opponent'], res]

dist = 203
Predict(dist, False)

