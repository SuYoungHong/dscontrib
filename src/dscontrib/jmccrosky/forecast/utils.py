# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import numpy as np
import pandas as pd
import plotly.graph_objs as go
from datetime import timedelta


# Calculate Mean Absolute Percentage Error of forecast
def calcMAPE(true, predicted):
    mask = true != 0
    return (np.fabs(true - predicted)/true)[mask].mean() * 100


# Calculate Mean Relative Error of forecast
def calcMRE(true, predicted):
    mask = true != 0
    return ((true - predicted)/true)[mask].mean() * 100


def calcLogRatio(true, predicted):
    logratio = np.mean(np.log(true) - np.log(predicted))
    return logratio


# Get most recent date in table
def getLatestDate(bqClient, project, dataset, table, product, field):
    query = '''
        SELECT
            MAX({field}) as date
        FROM
            `{project}.{dataset}.{table}`
        WHERE
            datasource="{product}"
    '''.format(
        project=project, dataset=dataset, table=table, field=field, product=product
    )
    data = bqClient.query(query).to_dataframe()
    if len(data) == 0:
        return None
    return bqClient.query(query).to_dataframe()['date'][0]


def splitData(data, firstTrainDate, firstHoldoutDate, firstTestDate, lastTestDate):
    temp = data.set_index('ds')
    split_data = {
        "training": temp[
            firstTrainDate:(firstHoldoutDate - timedelta(days=1))
        ].reset_index(),
        "holdout": temp[
            firstHoldoutDate:(firstTestDate - timedelta(days=1))
        ].reset_index(),
        "test": temp[firstTestDate:lastTestDate].reset_index(),
        "all": temp.reset_index(),
    }
    return split_data


def s2d(stringDate):
    return pd.to_datetime(stringDate).date()


def matchDates(data, forecast):
    temp = forecast.copy()
    temp['ds'] = temp.ds.dt.date
    return data.merge(temp, on="ds", how="inner")


def getLayout(title, xaxis, yaxis):
    return go.Layout(
        title=title,
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(
                text=xaxis
            )
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text=yaxis
            )
        ),
    )
