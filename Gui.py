
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget,QVBoxLayout,QLabel,QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import QtCore, QtWidgets

import plotly.offline as po
import plotly.graph_objs as go
import pandas as pd
import numpy as np    
import pyodbc as db
import dateutil.parser
 
class App(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.title = 'Performance Report'
        self.left = 300
        self.top = 100
        self.width = 1400
        self.height = 850
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
 
        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)
 
        self.show()
 
class MyTableWidget(QWidget):        
     
    @pyqtSlot()
    def clickMethod(self):
        import AccountReport
        from AccountReport import account_report
        aa = self.line.text()
        self.nameLabel1.setText(account_report(aa))
        
    def clickMethodb(self):
        import TEST
        from TEST import placement_report
        aaaa = self.lineb.text()
        self.nameLabel1b.setText(placement_report(aaaa))
        try:
        
            beam = db.connect(driver='{SQL Server Native Client 11.0}',
                               server='20.36.19.132',
                               database = "Beam00320",
                               uid= 'xugao',
                               pwd='xxxxxxxxxxxxxxxxxxxx')
            pla = """''"""+aaaa+"""''"""
            df = pd.read_sql("""
            
                     DECLARE @cols AS NVARCHAR(MAX),
                     @query  AS NVARCHAR(MAX)
                     select @cols = STUFF((SELECT ',' + QUOTENAME(pl.Mon)
                    from (
					SELECT ph.*
					from
					(
					SELECT ad.AccountID, ad.Mon, sum(ad.Amount) AS MonCollection
					FROM
					(SELECT sd.AccountID, CONVERT(VARCHAR(7), phh.Date, 126 ) AS Mon, phh.Amount 
					FROM PaymentHistory phh
					LEFT JOIN ServicerData sd
					on phh.ServicerDataID = sd.ServicerDataID
					WHERE  phh.IsPayment = 1 and phh.Date <> '2008-12-31' and phh.Date <> '2018-08-31'
					) ad
					group by  ad.AccountID, ad.Mon
					) ph
					) pl
                    group by pl.Mon
                    order by pl.Mon
            FOR XML PATH(''), TYPE
            ).value('.', 'NVARCHAR(MAX)') 
            ,1,1,'')
            set @query = '
            select vv.AccountID, vv.ccPlacementInBeam, vv.AcqBalance, op.*
            from Account vv
            left join ( SELECT AccountID as AcctID,' + @cols + ' from 
                       (
                               select pl.AccountID, pl.Mon, pl.MonCollection
				 FROM( 
	               SELECT ph.*
					from
					(
					SELECT ad.AccountID, ad.Mon, sum(ad.Amount) AS MonCollection
					FROM
					(SELECT sd.AccountID, CONVERT(VARCHAR(7), phh.Date, 126 ) AS Mon, phh.Amount 
					FROM PaymentHistory phh
					LEFT JOIN ServicerData sd
					on phh.ServicerDataID = sd.ServicerDataID
					WHERE phh.IsPayment = 1 and phh.Date <> ''2008-12-31'' and phh.Date <> ''2018-08-31''
					) ad
					group by  ad.AccountID, ad.Mon
					) ph
				)pl
            ) x
            pivot 
            (
                MAX(MonCollection)
                for Mon in (' + @cols + ')
            ) p 
			) op
            on vv.AccountID = op.AcctID
            where ccPlacementInBeam IN ("""+pla + """)' execute(@query)""", beam)
            
## df = df[df['AcqBalance']>0]      
        

            
            df['Gross'] =  df.iloc[:, 4:].sum(axis = 1)
            df['Payer'] = np.where(df['Gross'] > 0, 1 ,0)
            df = df.drop('AcctID', axis = 1)
            df = df.drop('AccountID', axis = 1)
            df['Act'] = 1
            dfsum = df.groupby('ccPlacementInBeam').sum()
    

            aa = pd.DataFrame(dfsum.loc[aaaa])
            aa = aa.drop(['AcqBalance', 'Gross', 'Payer', 'Act'], axis = 0)
            m = aa.ne(0).idxmax()[0]


            bb = aa == aa.apply(lambda x: x.iloc[x.nonzero()].iloc[-1], axis=0)
            cc = bb[bb.iloc[:,0]>0].index[0]

            a = aa.loc[m:cc]
    
            trace = []
            place = go.Scatter(x=list(a.index),
                        y=list(a.iloc[:,0]),
                        name= aaaa)
            place_avg = go.Scatter(x=list(a.index),
                        y=[a.iloc[:,0].mean()]*len(a.index),
                        name=' Average',
                        line=dict(dash='dash'))
            trace.append(place)
            trace.append(place_avg)    
            data = trace

            if len(a.index)<4:
                layout = go.Layout(
                        title="Beam Monthly Gross Collection ("+aaaa+")", yaxis=dict(
                        title='Collection ($)'), xaxis=dict(title='Time'),
                        annotations=[dict(x=a.index[0],
                                          y=a.iloc[:,0].mean(),
                                          xref='x', yref='y',
                                          text=' Average:<br> $'+str(round(a.iloc[:,0].mean(),2)),
                                          ax=0, ay=-40),
                                     dict(x=a.index[0],
                                          y=0,
                                          xref='x', yref='y',
                                          text=' First Payment: '+str(a.index[0]),
                                          ax=0, ay=-40),
                                    dict(x=a.index[-1],
                                         y=0,
                                         xref='x', yref='y',
                                         text=' Last Payment: '+str(a.index[-1]),
                                         ax=0, ay=-40),
                                    dict(x=a.iloc[:,0].idxmax(),
                                         y=a.iloc[:,0].max(),
                                         xref='x', yref='y',
                                         text= ' Max:<br> $'+str(round(a.iloc[:,0].max(),2)),
                                         ax=0, ay=-40)]
                                    )

            else:
                layout = go.Layout(
                        title="Beam Monthly Gross Collection ("+aaaa+")", yaxis=dict(
                        title='Collection ($)'), xaxis=dict(title='Time'),
                        annotations=[dict(x=a.index[2],
                                          y=a.iloc[:,0].mean(),
                                          xref='x', yref='y',
                                          text=' Average:<br> $'+str(round(a.iloc[:,0].mean(),2)),
                                          ax=0, ay=-40),
                                     dict(x=a.index[0],
                                          y=0,
                                          xref='x', yref='y',
                                          text=' First Payment: '+str(a.index[0]),
                                          ax=0, ay=-40),
                                    dict(x=a.index[-1],
                                         y=0,
                                         xref='x', yref='y',
                                         text=' Last Payment: '+str(a.index[-1]),
                                         ax=0, ay=-40),
                                    dict(x=a.iloc[:,0].idxmax(),
                                         y=a.iloc[:,0].max(),
                                         xref='x', yref='y',
                                         text= ' Max:<br> $'+str(round(a.iloc[:,0].max(),2)),
                                         ax=0, ay=-40)]
                                    )

            fig = go.Figure(data=data,layout = layout)



            raw_html = '<html><head><meta charset="utf-8" />'
            raw_html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
            raw_html += '<body>'
            raw_html += po.plot(fig, include_plotlyjs=False, output_type='div')
            raw_html += '</body></html>'

        
    # setHtml has a 2MB size limit, need to switch to setUrl on tmp file
    # for large figures.
            self.tab4.setHtml(raw_html)
        except:
            beam = db.connect(driver='{SQL Server Native Client 11.0}',
                               server='20.36.19.132',
                               database = "Beam00320",
                               uid= 'xugao',
                               pwd='xxxxxxxxxxxxxxxxxxxx')

            df = pd.read_sql("""
            
                     DECLARE @cols AS NVARCHAR(MAX),
                     @query  AS NVARCHAR(MAX)
                     select @cols = STUFF((SELECT ',' + QUOTENAME(pl.Mon)
                    from (
					SELECT ph.*
					from
					(
					SELECT ad.AccountID, ad.Mon, sum(ad.Amount) AS MonCollection
					FROM
					(SELECT sd.AccountID, CONVERT(VARCHAR(7), phh.Date, 126 ) AS Mon, phh.Amount 
					FROM PaymentHistory phh
					LEFT JOIN ServicerData sd
					on phh.ServicerDataID = sd.ServicerDataID
					WHERE  phh.IsPayment = 1 and phh.Date <> '2008-12-31' and phh.Date <> '2018-08-31'
					) ad
					group by  ad.AccountID, ad.Mon
					) ph
					) pl
                    group by pl.Mon
                    order by pl.Mon
            FOR XML PATH(''), TYPE
            ).value('.', 'NVARCHAR(MAX)') 
            ,1,1,'')
            set @query = '
            select  op.*
            from  ( SELECT AccountID as AcctID,' + @cols + ' from 
                       (
                               select pl.AccountID, pl.Mon, pl.MonCollection
				 FROM( 
	               SELECT ph.*
					from
					(
					SELECT ad.AccountID, ad.Mon, sum(ad.Amount) AS MonCollection
					FROM
					(SELECT sd.AccountID, CONVERT(VARCHAR(7), phh.Date, 126 ) AS Mon, phh.Amount 
					FROM PaymentHistory phh
					LEFT JOIN ServicerData sd
					on phh.ServicerDataID = sd.ServicerDataID
					WHERE phh.IsPayment = 1 and phh.Date <> ''2008-12-31'' and phh.Date <> ''2018-08-31''
					) ad
					group by  ad.AccountID, ad.Mon
					) ph
				)pl
            ) x
            pivot 
            (
                MAX(MonCollection)
                for Mon in (' + @cols + ')
            ) p 
			) op
            ' execute(@query)""", beam)
            
## df = df[df['AcqBalance']>0]      
        
            df = df.drop('AcctID', axis = 1)
            dfsum = df.sum()

            aa = pd.DataFrame(dfsum)
            m = aa.ne(0).idxmax()[0]

            bb = aa == aa.apply(lambda x: x.iloc[x.nonzero()].iloc[-1], axis=0)
            cc = bb[bb.iloc[:,0]>0].index[0]

            a = aa.loc[m:cc]
        
            trace = []
            place = go.Scatter(x=list(a.index),
                           y=list(a.iloc[:,0]),
                        name= 'LCS')
            place_avg = go.Scatter(x=list(a.index),
                        y=[a.iloc[:,0].mean()]*len(a.index),
                        name=' Average',
                            line=dict(dash='dash'))
            trace.append(place)
            trace.append(place_avg)    
            data = trace

            layout = go.Layout(
                    title="Beam Monthly Gross Collection (LCS Total)", yaxis=dict(
                        title='Collection ($)'), xaxis=dict(title='Time'),
                        annotations=[dict(x=a.index[-50],
                                          y=a.iloc[:,0].mean(),
                                          xref='x', yref='y',
                                          text=' Average:<br> $'+str(round(a.iloc[:,0].mean(),2)),
                                          ax=0, ay=-40),
                                     dict(x=a.index[0],
                                          y=0,
                                          xref='x', yref='y',
                                          text=' Payment History Start: '+str(a.index[0]),
                                          ax=0, ay=-40),
                                    dict(x=a.index[-1],
                                         y=0,
                                         xref='x', yref='y',
                                         text=' Current Month: '+str(a.index[-1]),
                                         ax=0, ay=-40),
                                    dict(x=a.iloc[:,0].idxmax(),
                                         y=a.iloc[:,0].max(),
                                         xref='x', yref='y',
                                         text= ' Max:<br> $'+str(round(a.iloc[:,0].max(),2)),
                                         ax=0, ay=-40)]
                                    )


            fig = go.Figure(data=data,layout = layout)
        
            raw_html1 = '<html><head><meta charset="utf-8" />'
            raw_html1 += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
            raw_html1 += '<body>'
            raw_html1 += po.plot(fig, include_plotlyjs=False, output_type='div')
            raw_html1 += '</body></html>'

            self.tab4.setHtml(raw_html1)
            

 
    def __init__(self, parent):   
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
 
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()	
        self.tab2 = QWidget()
        self.tab3 = QWebEngineView()
        self.tab4 = QWebEngineView()
        
        beam = db.connect(driver='{SQL Server Native Client 11.0}',
                               server='20.36.19.132',
                               database = "Beam00320",
                               uid= 'xugao',
                               pwd='xxxxxxxxxxxxxxxxxxxxx')

        df = pd.read_sql("""
            
                     DECLARE @cols AS NVARCHAR(MAX),
                     @query  AS NVARCHAR(MAX)
                     select @cols = STUFF((SELECT ',' + QUOTENAME(pl.Mon)
                    from (
					SELECT ph.*
					from
					(
					SELECT ad.AccountID, ad.Mon, sum(ad.Amount) AS MonCollection
					FROM
					(SELECT sd.AccountID, CONVERT(VARCHAR(7), phh.Date, 126 ) AS Mon, phh.Amount 
					FROM PaymentHistory phh
					LEFT JOIN ServicerData sd
					on phh.ServicerDataID = sd.ServicerDataID
					WHERE  phh.IsPayment = 1 and phh.Date <> '2008-12-31' and phh.Date <> '2018-08-31'
					) ad
					group by  ad.AccountID, ad.Mon
					) ph
					) pl
                    group by pl.Mon
                    order by pl.Mon
            FOR XML PATH(''), TYPE
            ).value('.', 'NVARCHAR(MAX)') 
            ,1,1,'')
            set @query = '
            select  op.*
            from  ( SELECT AccountID as AcctID,' + @cols + ' from 
                       (
                               select pl.AccountID, pl.Mon, pl.MonCollection
				 FROM( 
	               SELECT ph.*
					from
					(
					SELECT ad.AccountID, ad.Mon, sum(ad.Amount) AS MonCollection
					FROM
					(SELECT sd.AccountID, CONVERT(VARCHAR(7), phh.Date, 126 ) AS Mon, phh.Amount 
					FROM PaymentHistory phh
					LEFT JOIN ServicerData sd
					on phh.ServicerDataID = sd.ServicerDataID
					WHERE phh.IsPayment = 1 and phh.Date <> ''2008-12-31'' and phh.Date <> ''2018-08-31''
					) ad
					group by  ad.AccountID, ad.Mon
					) ph
				)pl
            ) x
            pivot 
            (
                MAX(MonCollection)
                for Mon in (' + @cols + ')
            ) p 
			) op
            ' execute(@query)""", beam)
            
## df = df[df['AcqBalance']>0]      
        
        df = df.drop('AcctID', axis = 1)
        dfsum = df.sum()

        aa = pd.DataFrame(dfsum)
        m = aa.ne(0).idxmax()[0]

        bb = aa == aa.apply(lambda x: x.iloc[x.nonzero()].iloc[-1], axis=0)
        cc = bb[bb.iloc[:,0]>0].index[0]

        a = aa.loc[m:cc]
        
        trace = []
        place = go.Scatter(x=list(a.index),
                        y=list(a.iloc[:,0]),
                        name= 'LCS')
        place_avg = go.Scatter(x=list(a.index),
                        y=[a.iloc[:,0].mean()]*len(a.index),
                        name=' Average',
                        line=dict(dash='dash'))
        trace.append(place)
        trace.append(place_avg)    
        data = trace

        layout = go.Layout(
                    title="Beam Monthly Gross Collection (LCS Total)", yaxis=dict(
                        title='Collection ($)'), xaxis=dict(title='Time'),
                        annotations=[dict(x=a.index[-50],
                                          y=a.iloc[:,0].mean(),
                                          xref='x', yref='y',
                                          text=' Average:<br> $'+str(round(a.iloc[:,0].mean(),2)),
                                          ax=0, ay=-40),
                                     dict(x=a.index[0],
                                          y=0,
                                          xref='x', yref='y',
                                          text=' Payment History Start: '+str(a.index[0]),
                                          ax=0, ay=-40),
                                    dict(x=a.index[-1],
                                         y=0,
                                         xref='x', yref='y',
                                         text=' Current Month: '+str(a.index[-1]),
                                         ax=0, ay=-40),
                                    dict(x=a.iloc[:,0].idxmax(),
                                         y=a.iloc[:,0].max(),
                                         xref='x', yref='y',
                                         text= ' Max:<br> $'+str(round(a.iloc[:,0].max(),2)),
                                         ax=0, ay=-40)]
                                    )


        fig = go.Figure(data=data,layout = layout)

        raw_html1 = '<html><head><meta charset="utf-8" />'
        raw_html1 += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
        raw_html1 += '<body>'
        raw_html1 += po.plot(fig, include_plotlyjs=False, output_type='div')
        raw_html1 += '</body></html>'

        
    # setHtml has a 2MB size limit, need to switch to setUrl on tmp file
    # for large figures.
        self.tab4.setHtml(raw_html1)
        
################################################################################
        df1 = pd.read_sql("""select REPLACE(ccStatus, ' ', '') AS ccStatus,
		count(*) as Accounts,
		FORMAT(sum(AcqBalance), 'C', 'en-us') as TotalBalance
        from Account 
        where ccPlacementInBeam = 'Loan Depot - NL'
        group by REPLACE(ccStatus, ' ', '')""",beam)

    
        df2 = pd.read_sql("""
                          select convert(varchar(7),PostingDate, 126) as MON, sum(aa.Amount) as AMT
                          from account ss
                          
                          inner join Reports_PostedAndFuturePayments aa
                          on ss.AccountID = aa.AccountID
                          where ss.ccPlacementInBeam = 'Loan Depot - NL' 
                          group by convert(varchar(7),PostingDate, 126)
                          ORDER BY convert(varchar(7),PostingDate, 126)""", beam)
        df2 = df2.head(60)
        df3 = {'Pred': [6668.07,10290.23,14708.26,19795.32,23500.81,29216.33,26245.85,29332.04,29503.68,32174.61,28661.89,24185.25,26520.90,22828.38,22828.38,
                    31877.03,22828.38,22828.38,22828.38,22828.38,22521.80,22521.80,22236.00,21320.62,20394.76,19545.03,19545.03,19240.13,19240.13,
                    19240.13,18480.93,17685.09,17137.64,16609.51,16609.51,16609.51,15860.36,15593.10,14543.61,13246.61,12266.85,12266.85,12266.85,
                    12266.85,12266.85,12266.85,12266.85,12266.85,12266.85,11817.09,11603.68,10909.24,10027.99,9809.920,8901.37,8901.37,8901.37,8901.370,8901.37,8901.37]}
        df3 = pd.DataFrame(data=df3)
        df2['Pred']=df3
    
    
    
        df4 = pd.read_sql("""

            select aa.AccountID, convert(varchar(10),aa.PaymentDate, 126) as PaymentDate, FORMAT(aa.Amount, 'N2') AS Amount, REPLACE(aa.CreditUser, ' ', '') AS CreditUser
            from account ss
            
            inner join Reports_PostedAndFuturePayments aa
            on ss.AccountID = aa.AccountID
            where ss.ccPlacementInBeam = 'Loan Depot - NL' and aa.IsPosted = 1
            order by PaymentDate""", beam)
        df4['Amount'] = df4[['Amount']].replace('[\$,]', '', regex=True).astype(float)
        df4.loc['Total'] = df4.sum()
        df4.loc['Total', 'AccountID'] = 'Total'
        df4.loc['Total', 'PaymentDate'] = ' '
        df4.loc['Total', 'CreditUser'] = ' '
        df4['Amount'] = df4[['Amount']].applymap("${0:.2f}".format)
        
        df5 = pd.read_sql("""
                          select REPLACE(bbc.CreditUser, ' ', '') as CreditUser, bbc.PostedPayment, bbc.[6MonPayment], bbc.TotalPayment
                          from(
                          select aaa.CreditUser, FORMAT(bbb.PostedCollection,'C', 'en-us') as PostedPayment, 
                          FORMAT(ccc.SixCollection,'C', 'en-us') as [6MonPayment], FORMAT(aaa.PendingCollection,'C', 'en-us') as TotalPayment
                          from
                          (
                                  select aa.CreditUser, sum(aa.Amount) as PendingCollection 
                                  from account ss
                                  inner join Reports_PostedAndFuturePayments aa
                                  on ss.AccountID = aa.AccountID
                                  where ss.ccPlacementInBeam = 'Loan Depot - NL' 
                                  group by aa.CreditUser
                                  ) aaa
                                  left join
                                  (
                                          
                                          select aa.CreditUser, sum(aa.Amount) as PostedCollection 
                                          from account ss
                                          inner join Reports_PostedAndFuturePayments aa
                                          on ss.AccountID = aa.AccountID
                                          where ss.ccPlacementInBeam = 'Loan Depot - NL' and aa.IsPosted = 1
                                          group by aa.CreditUser
                                          ) bbb
                                          on aaa.CreditUser = bbb.CreditUser
                                          join
                                          (
                                                  select aa.CreditUser, sum(aa.Amount) as SixCollection 
                                                  from account ss
                                                  inner join Reports_PostedAndFuturePayments aa
                                                  on ss.AccountID = aa.AccountID
                                                  where ss.ccPlacementInBeam = 'Loan Depot - NL' and aa.PostingDate < '2019-06-01'
                                                  group by aa.CreditUser
                                                  ) ccc
                                                  on aaa.CreditUser = ccc.CreditUser
                                                  ) bbc""", beam)


        df5['6MonPrediction'] = '${:,.2f}'.format(df3.head(6).sum()[0]/df5.shape[0])
        df5['TotalPrediction'] = '${:,.2f}'.format(df3.sum()[0]/df5.shape[0])
    
    
        df6 = df5[['CreditUser']]

        df6[['PostedPayment', '6MonPayment', 'TotalPayment','6MonPrediction', 'TotalPrediction']]= df5[df5.columns[1:]].replace('[\$,]', '', regex=True).astype(float)
    
        df6.loc['Total'] = df6.sum()
        df6[df6.columns[1:]] = df6[df6.columns[1:]].applymap("${0:.2f}".format)
        df6.loc['Total', 'CreditUser'] = 'Total'
        
################################################################################
        
        fig = go.Figure(data=data,layout = layout)

        raw_html1 = '<html><head><meta charset="utf-8" />'
        raw_html1 += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
        raw_html1 += '<body>'
        raw_html1 += po.plot(fig, include_plotlyjs=False, output_type='div')
        raw_html1 += '</body></html>'        
        
        
        
        trace1 = go.Table(
                header=dict(values=list(df1.columns),
                line = dict(color = '#20B2AA'),
                fill = dict(color='#20B2AA'),
                align = 'center',
                height = 32,
                font = dict(color = 'black', size = 14)),
                cells=dict(values=[df1.ccStatus, df1.Accounts, df1.TotalBalance],
               line = dict(color = ['#20B2AA']),
               fill = dict(color = ['white','lightgrey','white']),
               align = 'center',
               height = 28,
               font = dict(color = '#2F4F4F', size = 12)),
               domain = {'x': [0.0, 0.4], 'y': [0.0, 0.9]})

        trace2 = go.Pie(labels = df1['ccStatus'],
                   values = df1['Accounts'],
                   domain = {'x': [0.45, 1.0], 'y': [0.4, 1.0]},
                   marker=dict(colors=['#20B2AA', '#00CED1', '#FFD700', '#FF4500','#2F4F4F']),
                   hole = 0.5,
                   text = df1.ccStatus)
        traces = []
        traces.append(trace1)
        traces.append(trace2)
        layout1 = go.Layout(height = 650,
                   width = 1350,
                   autosize = True,
                   title = 'Loan Depot Overview')
        fig1 = go.Figure(data = traces, layout = layout1)
        raw_htmlone = '<html><head><meta charset="utf-8" />'
        raw_htmlone += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
        raw_htmlone += '<body>'
        raw_htmlone += po.plot(fig1, include_plotlyjs=False, output_type='div')
        raw_htmlone += '</body></html>'        
        
    #####################



        trace3 = go.Scatter(
                y=df2.AMT,
                x=df2.MON,
                name = 'Actual(Posted+Promise)', # Style name/legend entry with html tags
                line = dict(
                        color = ('rgb(22, 96, 167)'),
                        width = 4)
                )
        trace4 = go.Scatter(
                y=df2.Pred,
                x=df2.MON,
                name = 'Predicted',
                line = dict(
                        color = ('rgb(205, 12, 24)'), width = 4,dash = 'dash')
                )

        data2 = [trace3, trace4]
        layout2 = go.Layout(height = 650,
                   width = 1500, title = 'Loan Depot Liquidation (60-Month Period)')

        fig2 = dict(data=data2, layout=layout2)
        raw_htmltwo = '<html><head><meta charset="utf-8" />'
        raw_htmltwo += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
        raw_htmltwo += '<body>'
        raw_htmltwo += po.plot(fig2, include_plotlyjs=False, output_type='div')
        raw_htmltwo += '</body></html>'        

    ######################

        trace5 = go.Table(
                header=dict(values=['CreditUser', 'PostedPayment', '6MonPayment','6MonPrediction', 'TotalPayment',
                                    'TotalPrediction'],
                line = dict(color = '#20B2AA'),
                fill = dict(color='#20B2AA'),
                align = 'center',
                height = 32,
                font = dict(color = 'black', size = 14)),
                cells=dict(values=[df6.CreditUser, df6.PostedPayment, df6['6MonPayment'], df6['6MonPrediction'], df6.TotalPayment, df6.TotalPrediction],
               line = dict(color = ['#20B2AA']),
               fill = dict(color = ['white','lightgrey','white','#F0E68C', 'white', '#F0E68C','white']),
               align = 'center',
               height = 28,
               font = dict(color = '#2F4F4F', size = 12)),
               domain = {'x': [0.0, 0.55], 'y': [0.0, 1.0]})

        trace6 = go.Table(
                header=dict(values=['AccountID', 'PaymentDate', 'CreditUser', 'Amount'],
                line = dict(color = '#20B2AA'),
                fill = dict(color='#20B2AA'),
                height = 32,
                font = dict(color = 'black', size = 14)),
               cells=dict(values=[df4.AccountID, df4.PaymentDate, df4.CreditUser, df4.Amount],
               line = dict(color = ['#20B2AA']),
               fill = dict(color = ['white','lightgrey','white','lightgrey']),
               align = 'center',
               height = 28,
               font = dict(color = '#2F4F4F', size = 12)),
               domain = {'x': [0.6, 1.0], 'y': [0.0, 1.0]})
               
        traces2 = []
        traces2.append(trace5)
        traces2.append(trace6)
        layout2 = go.Layout(height = 650,
                   width = 1400,
                   autosize = True,
                   title = 'Loan Depot Collection')
        fig3 = go.Figure(data = traces2, layout = layout2)
        raw_htmlthree = '<html><head><meta charset="utf-8" />'
        raw_htmlthree += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
        raw_htmlthree += '<body>'
        raw_htmlthree += po.plot(fig3, include_plotlyjs=False, output_type='div')
        raw_htmlthree += '</body></html>'        
        
        finalcode = """
        <!DOCTYPE html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
        body {font-family: Arial;}
        
        /* Style the tab */
        .tab {
                overflow: hidden;
                border: 1px solid #ccc;
                background-color: #f1f1f1;
                    }

        /* Style the buttons inside the tab */
        .tab button {
                background-color: inherit;
                float: left;
                border: none;
                outline: none;
                cursor: pointer;
                padding: 14px 16px;
                transition: 0.3s;
                font-size: 17px;
                }

        /* Change background color of buttons on hover */
        .tab button:hover {
                background-color: #ddd;
                    }
            
        /* Create an active/current tablink class */
        .tab button.active {
                background-color: #ccc;
                    }

        /* Style the tab content */
        .tabcontent {
                display: none;
                padding: 6px 12px;
                border: 1px solid #ccc;
                border-top: none;
                }
        </style>
        </head>
        <body>

        <p>This is Summary of Loan Depot Portfolio.</p>

        <div class="tab">
            <button class="tablinks" onclick="openCity(event, 'Status')" id="defaultOpen">Status</button>
            <button class="tablinks" onclick="openCity(event, 'Liquidation')">Liquidation</button>
            <button class="tablinks" onclick="openCity(event, 'Details')">Details</button>
        </div>
        <div id="Status" class="tabcontent">"""+raw_htmlone +"""</div> <div id="Liquidation" class="tabcontent">"""+raw_htmltwo +"""</div> <div id="Details" class="tabcontent">"""+raw_htmlthree+"""</div>
        <script>
        function openCity(evt, cityName) {
                var i, tabcontent, tablinks;
                tabcontent = document.getElementsByClassName("tabcontent");
                for (i = 0; i < tabcontent.length; i++) {
                        tabcontent[i].style.display = "none";
                        }
        tablinks = document.getElementsByClassName("tablinks");
        for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
                }
        document.getElementById(cityName).style.display = "block";
        evt.currentTarget.className += " active";
        }

        // Get the element with id="defaultOpen" and click on it
        document.getElementById("defaultOpen").click();
        </script>
   
        </body>
        </html> 

"""
        self.tab3.setHtml(finalcode)
################################################################################
        
        # Add tabs
        self.tabs.addTab(self.tab3,"Loan Depot")        
        self.tabs.addTab(self.tab2,"Placement Overview")
        self.tabs.addTab(self.tab4,"Placement Liquidation Curve")
        self.tabs.addTab(self.tab1,"Account Information")
        
        
        # Add tabs to widget        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        # Create first tab
        self.tab1.layout = QVBoxLayout(self)       
    
        self.nameLabel = QLabel(self)
        self.nameLabel.setText('Account ID:')
        # input (path)
        self.line = QLineEdit(self)
  
        self.nameLabel1 = QLabel(self)  
        self.nameLabelo = QLabel(self)  

        # button_Save
        pybutton = QPushButton('Show Result', self)
        pybutton.clicked.connect(self.clickMethod) # what happend after click see clickMethod below  
  

        self.tab1.layout.addWidget(self.nameLabel)        
        self.tab1.layout.addWidget(self.line)
        self.tab1.layout.addWidget(pybutton)
        self.tab1.layout.addWidget(self.nameLabel1)
        self.tab1.layout.addWidget(self.nameLabelo)


        self.tab1.setLayout(self.tab1.layout)
        


        
        # Create 2 tab
        self.tab2.layout = QVBoxLayout(self)
    
        self.nameLabelb = QLabel(self)
        self.nameLabelb.setText('Placement Code:\n(Please wait 5-10s after click)')
        # input (path)
        self.lineb = QLineEdit(self)
  
        self.nameLabel1b = QLabel(self)   
        self.nameLabel1q = QLabel(self)   

        # button_Save
        pybuttonb = QPushButton('Show Result', self)
        pybuttonb.clicked.connect(self.clickMethodb) # what happend after click see clickMethod below  
  

        self.tab2.layout.addWidget(self.nameLabelb)        
        self.tab2.layout.addWidget(self.lineb)
        self.tab2.layout.addWidget(pybuttonb)
        self.tab2.layout.addWidget(self.nameLabel1b)
        self.tab2.layout.addWidget(self.nameLabel1q)

        self.tab2.setLayout(self.tab2.layout)
        
        ###


class HtmlView(QWebEngineView):
    def __init__(self, *args, **kwargs):
        QWebEngineView.__init__(self, *args, **kwargs)
        self.tab = self.parent()
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
