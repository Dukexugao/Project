
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
        beam = db.connect(driver='{SQL Server Native Client 11.0}',
                               server='20.36.19.132',
                               database = "Beam00320",
                               uid= 'xugao',
                               pwd='h7zLeFdQNhApp166') 
  
        AcctID = self.line.text()
        try:
                sqlQuery = """
                
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
select ee.*, op.*
from(
select a3.*,a4.AccountExceptionSourceID, a4.Description as EDescription, a4.AccountExceptionStatusID, a4.Status, a4.AccountExceptionTypeID, a4.Exception,
a4.Details, a4.Recorded, a4.Assets, a4.CaseNumber, a4.CaseStatus, a4.Chapter, a4.FileDate, a4.DateDischarged, a4.DateDismissed, a4.StatusChangeDate, a4.DateClosed, 
a4.CourtState, abc.FirstPay, abc.TotCollection, abc.Times
from
(
SELECT a1.*, a2.[1ResApplied], a2.[1Description], a2.[1ResEnd],
       a2.[2ResApplied], a2.[2Description], a2.[2ResEnd],
	   a2.[3ResApplied], a2.[3Description], a2.[3ResEnd],
	   a2.[4ResApplied], a2.[4Description], a2.[4ResEnd],
	   a2.[5ResApplied], a2.[5Description], a2.[5ResEnd]
from
(
SELECT a.AccountID, a.ConvertedAccountID,  a.AccountTypeID, att.Description,  a.ccStateProvince , a.ccPlacementInBeam, a.PortfolioOwner, a.ccPlacementPortfolio, 
		a.ccMoreThan1Debtor, a.AcqBalance, a.COAmount, a.ccBalance, a.OpenAmount, a.AccountOpenDate, a.CODate,a.ccSOLDate, a.ccStatus, 
        num.TransferTimes, num.Collectors, num.UniCollectors, num.Dif, convert(char(7), movein.[1MoveIn], 120) as AssignMon, 
		movein.[1MoveIn], que.[1Collector], moveout.[1MoveOut],
		movein.[2MoveIn], que.[2Collector], moveout.[2MoveOut],
		movein.[3MoveIn], que.[3Collector], moveout.[3MoveOut],
		movein.[4MoveIn], que.[4Collector], moveout.[4MoveOut],
		movein.[5MoveIn], que.[5Collector], moveout.[5MoveOut],
		movein.[6MoveIn], que.[6Collector], moveout.[6MoveOut],
		movein.[7MoveIn], que.[7Collector], moveout.[7MoveOut],
		movein.[8MoveIn], que.[8Collector], moveout.[8MoveOut]
FROM Account a

LEFT JOIN AccountType att
on a.AccountTypeID = att.AccountTypeID

left join
(
 select pl.AccountID, pl.TransferTimes,  pl.Collectors, pl.UniCollectors, ( pl.Collectors - pl.UniCollectors) AS Dif
  FROM 
	(SELECT ph.AccountID,  count(ph.AccountID) as TransferTimes, count(ph.QueueID) as Collectors,  count(distinct(ph.QueueID)) as UniCollectors
	from PlacementHistory ph
	group by ph.AccountID
	)pl

) num

on a.AccountID = num.AccountID

left join

(
select *
from 
(
  select pl.AccountID,  pl.MoveInDate, CONCAT(pl.TransferID,  ''MoveIn'') As TransferIDN 
  From(
					SELECT ph.*,  row_number() over (partition by ph.AccountID Order by ph.AccountID, ph.MoveInDate) as TransferID
					from(
					select *,  DATEDIFF( day, MoveInDate, MoveOutDate ) AS Days
					from PlacementHistory
					) ph
					WHERE (ph.Days <> 0) OR (ph.Days is null)
					) pl
) src
pivot
(
  max(src.MoveInDate)
  for src.TransferIDN in ([1MoveIn], [2MoveIn], [3MoveIn], [4MoveIn], [5MoveIn], [6MoveIn], [7MoveIn], [8MoveIn])
) piv
) movein
 on a.AccountID = movein.AccountID


left join
(

select *
from 
(
  select pl.AccountID,  pl.QueueID, CONCAT(pl.TransferID,  ''Collector'') As TransferIDN 
  From(
					SELECT ph.*,  row_number() over (partition by ph.AccountID Order by ph.AccountID, ph.MoveInDate) as TransferID
					from(
					select *,  DATEDIFF( day, MoveInDate, MoveOutDate ) AS Days
					from PlacementHistory
					) ph
					WHERE (ph.Days <> 0) OR (ph.Days is null)
					) pl
) src
pivot
(
  max(src.QueueID)
  for src.TransferIDN in ([1Collector], [2Collector], [3Collector], [4Collector], [5Collector], [6Collector], [7Collector], [8Collector])
) piv
) que
on a.AccountID = que.AccountID

left join
(

select *
from 
(
  select pl.AccountID,  pl.MoveOutDate, CONCAT(pl.TransferID,  ''MoveOut'') As TransferIDN 
  From(
					SELECT ph.*,  row_number() over (partition by ph.AccountID Order by ph.AccountID, ph.MoveInDate) as TransferID
					from(
					select *,  DATEDIFF( day, MoveInDate, MoveOutDate ) AS Days
					from PlacementHistory
					) ph
					WHERE (ph.Days <> 0) OR (ph.Days is null)
					) pl
) src
pivot
(
  max(src.MoveOutDate)
  for src.TransferIDN in ([1MoveOut], [2MoveOut], [3MoveOut], [4MoveOut], [5MoveOut], [6MoveOut], [7MoveOut], [8MoveOut])
) piv
) moveout
on a.AccountID = moveout.AccountID
) a1

join
(
SELECT a.AccountID, app.[1ResApplied], dess.[1Description], en.[1ResEnd],
       app.[2ResApplied], dess.[2Description], en.[2ResEnd],
	   app.[3ResApplied], dess.[3Description], en.[3ResEnd],
	   app.[4ResApplied], dess.[4Description], en.[4ResEnd],
	   app.[5ResApplied], dess.[5Description], en.[5ResEnd]
FROM Account a
left join
(

select *
from 
(
  select pl.AccountID,  pl.AppliedDate, CONCAT(pl.RestrictionID,  ''ResApplied'') As RestrictionIDN
  From(
					select fo.*, row_number() over(partition by fo.AccountID Order by fo.AccountID, fo.AppliedDate) as RestrictionID
					from 
					(
				SELECT fi.AccountID,
				fi.AppliedDate,
				fi.EndDate,
				fi.RestrictionDaysDiff,
				fi.AccountRestrictionTypeID  AS RestrictionTypeID,
				CONCAT (fi.Description,'' '', fi.AccountRestrictionSubType) As Describe
				from
				(
				SELECT re.*,
				  AccountRestrictionType.Description
				FROM
				(
				sELECT T1.AccountID,
				 T1.Applied as AppliedDate, 
				 MIN(T2.Applied) AS EndDate, 
				DATEDIFF(day, T1.Applied, MIN(T2.Applied)) AS   RestrictionDaysDiff,
				t1.AccountRestrictionTypeID,
				t1.AccountRestrictionSubType
				FROM    AccountRestriction	T1
				 LEFT JOIN AccountRestriction T2
				 ON T1.AccountID = T2.AccountID
					AND T2.Applied > T1.Applied
				GROUP BY  T1.AccountID,t1.AccountRestrictionTypeID, t1.AccountRestrictionSubType,  T1.Applied
				) re
				left join AccountRestrictionType
				on re.AccountRestrictionTypeID  = AccountRestrictionType.RestrictionTypeID
				) fi
				) fo
				) pl

) src
pivot
(
  max(src.AppliedDate)
  for src.RestrictionIDN in ([1ResApplied], [2ResApplied], [3ResApplied], [4ResApplied], [5ResApplied])
) piv
) app
on a.AccountID = app.AccountID

left join
(



select *
from 
(
  select pl.AccountID,  pl.EndDate, CONCAT(pl.RestrictionID,  ''ResEnd'') As RestrictionIDN
  From(
					select fo.*, row_number() over(partition by fo.AccountID Order by fo.AccountID, fo.AppliedDate) as RestrictionID
					from 
					(
				SELECT fi.AccountID,
				fi.AppliedDate,
				fi.EndDate,
				fi.RestrictionDaysDiff,
				fi.AccountRestrictionTypeID  AS RestrictionTypeID,
				CONCAT (fi.Description,'' '', fi.AccountRestrictionSubType) As Describe
				from
				(
				SELECT re.*,
				  AccountRestrictionType.Description
				FROM
				(
				sELECT T1.AccountID,
				 T1.Applied as AppliedDate, 
				 MIN(T2.Applied) AS EndDate, 
				DATEDIFF(day, T1.Applied, MIN(T2.Applied)) AS   RestrictionDaysDiff,
				t1.AccountRestrictionTypeID,
				t1.AccountRestrictionSubType
				FROM    AccountRestriction	T1
				 LEFT JOIN AccountRestriction T2
				 ON T1.AccountID = T2.AccountID
					AND T2.Applied > T1.Applied
				GROUP BY  T1.AccountID,t1.AccountRestrictionTypeID, t1.AccountRestrictionSubType,  T1.Applied
				) re
				left join AccountRestrictionType
				on re.AccountRestrictionTypeID  = AccountRestrictionType.RestrictionTypeID
				) fi
				) fo
				) pl

) src
pivot
(
  max(src.EndDate)
  for src.RestrictionIDN in ([1ResEnd], [2ResEnd], [3ResEnd], [4ResEnd], [5ResEnd])
) piv
) en
on  a.AccountID = en.AccountID
left join
(

select *
from 
(
  select pl.AccountID,  pl.Describe, CONCAT(pl.RestrictionID,  ''Description'') As RestrictionIDN
  From(
					select fo.*, row_number() over(partition by fo.AccountID Order by fo.AccountID, fo.AppliedDate) as RestrictionID
					from 
					(
				SELECT fi.AccountID,
				fi.AppliedDate,
				fi.EndDate,
				fi.RestrictionDaysDiff,
				fi.AccountRestrictionTypeID  AS RestrictionTypeID,
				CONCAT (fi.Description,'' '', fi.AccountRestrictionSubType) As Describe
				from
				(
				SELECT re.*,
				  AccountRestrictionType.Description
				FROM
				(
				sELECT T1.AccountID,
				 T1.Applied as AppliedDate, 
				 MIN(T2.Applied) AS EndDate, 
				DATEDIFF(day, T1.Applied, MIN(T2.Applied)) AS   RestrictionDaysDiff,
				t1.AccountRestrictionTypeID,
				t1.AccountRestrictionSubType
				FROM    AccountRestriction	T1
				 LEFT JOIN AccountRestriction T2
				 ON T1.AccountID = T2.AccountID
					AND T2.Applied > T1.Applied
				GROUP BY  T1.AccountID,t1.AccountRestrictionTypeID, t1.AccountRestrictionSubType,  T1.Applied
				) re
				left join AccountRestrictionType
				on re.AccountRestrictionTypeID  = AccountRestrictionType.RestrictionTypeID
				) fi
				) fo
				) pl

) src
pivot
(
  max(src.Describe)
  for src.RestrictionIDN in ([1Description], [2Description], [3Description], [4Description], [5Description])
) piv
) dess

on a.AccountID = dess.AccountID
)a2

on a1.AccountID = a2.AccountID
) a3
left join
(
select ae.AccountID, ae.AccountExceptionSourceID, ass.Description , ae.AccountExceptionStatusID, aes.Description as Status, ae.AccountExceptionTypeID, ayp.Description as Exception,
ae.Details, ae.Recorded, bk.Assets, bk.CaseNumber, bk.CaseStatus, bk.Chapter, bk.FileDate, bk.DateDischarged, bk.DateDismissed, bk.StatusChangeDate, bk.DateClosed, 
bk.CourtState

from AccountException ae
left join AccountExceptionSource ass
on ae.AccountExceptionSourceID = ass.AccountExceptionSourceID
left join AccountExceptionStatus aes
on ae.AccountExceptionStatusID = aes.AccountExceptionStatusID
left join AccountExceptionType ayp
on ae.AccountExceptionTypeID = ayp.AccountExceptionTypeID
left join BankruptcyDetail bk
on ae.AccountExceptionID = bk.ExceptionID
) a4
on a3.AccountID = a4.AccountID

left join 
(
/* firstpay+total*/
select cc.*,convert(char(7), bb.FirstPay, 120) as FirstPay
from
(
SELECT ac.AccountID, ac.Date as FirstPay
from
(
SELECT sd.AccountID , aa.Date, aa.PaymentHistoryTypeID, row_number() over(partition by sd.AccountID Order by sd.AccountID, aa.Date) as TransID,
	   SUM(aa.Amount) over(partition by sd.AccountID Order by sd.AccountID, aa.Date) as Payment
FROM  PaymentHistory aa
LEFT JOIN ServicerData sd
on aa.ServicerDataID = sd.ServicerDataID
WHERE aa.IsPayment = 1 and aa.Date <> ''2008-12-31'' and aa.Date <> ''2018-08-31'') ac

where ac.TransID = 1
) bb

join
(
SELECT sd.AccountID , SUM(aa.Amount) as TotCollection, COUNT(aa.Amount) as Times
FROM  PaymentHistory aa
LEFT JOIN ServicerData sd
on aa.ServicerDataID = sd.ServicerDataID
WHERE aa.IsPayment = 1 and aa.Date <> ''2008-12-31'' and aa.Date <> ''2018-08-31''
group by AccountID
) cc
on bb.AccountID = cc.AccountID
) abc
on a3.AccountID = abc.AccountID
) ee
left join
(

SELECT AccountID,' + @cols + ' from 
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
					WHERE  phh.IsPayment = 1 and phh.Date <> ''2008-12-31'' and phh.Date <> ''2018-08-31''
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
on ee.AccountID = op.AccountID
 
"""
                query =  sqlQuery+ """  where ee.AccountID = """+ str(AcctID) + """' execute(@query)"""
                df = pd.read_sql(query, beam)
                cols = pd.io.parsers.ParserBase({'names':df.columns})._maybe_dedup_names(df.columns)
                df.columns=cols
                AcctID = str(AcctID)
                df.AccountID = df.AccountID.astype(str)
                if df.shape[0] == 0:
                    a = "Warning: Account Does Not Exist"
                elif df.shape[0] > 0:
                    if df[df['AccountID'] == AcctID]['AccountOpenDate'].values[0] is None:
                        b = "No Info"
                    else:
                        b = (df[df['AccountID'] == AcctID]['AccountOpenDate'].values[0]).astype(str)[:10]
                    if df[df['AccountID'] == AcctID]['CODate'].values[0] is None:
                        c = "No Info"
                    else:
                        c = (df[df['AccountID'] == AcctID]['CODate'].values[0]).astype(str)[:10]
                    if df[df['AccountID'] == AcctID]['ccSOLDate'].values[0] is None:
                        d = "No Info"
                    else:
                        d = (df[df['AccountID'] == AcctID]['ccSOLDate'].values[0]).astype(str)[:10]
                
                a = " I. Account Information\n" +  "\nAccountID:{}  {}".format("        ",str(AcctID))\
                +"\nLoan Type: {}  {}".format("        ", df[df['AccountID'] == AcctID]['Description'].values[0])\
                +"\nPlacement: {}  {}".format("        ", df[df['AccountID'] == AcctID]['ccPlacementInBeam'].values[0])\
                +"\nDebtor State: {}{}".format("      ", df[df['AccountID'] == AcctID]['ccStateProvince'].values[0])\
                +"\nCurrent Status:{} {}".format("   ",  df[df['AccountID'] == AcctID]['ccStatus'].values[0])\
                +"\nAssigned Date: {} {}".format( "  ", dateutil.parser.parse((df[df['AccountID'] == AcctID]['1MoveIn'].values[0]).astype(str)).strftime('%Y-%m-%d'))\
                +"\nAcq Balance: {}{}".format("       $", df[df['AccountID'] == AcctID]['AcqBalance'].values[0])\
                +"\nOpen Date: {} {}".format( "        ",  b)\
                +"\nCO Date: {} {}".format( "            ", c)\
                +"\nCO Amount: {}{}".format( "        $", np.where(df[df['AccountID'] == AcctID]['COAmount'].values[0] is None, "0", df[df['AccountID'] == AcctID]['COAmount'].values[0]))\
                +"\nSOL Date: {} {}{}".format( "           ", d,"\n")\
                +"\nII. Collection Information\n "\
                +"\nIS Bankruptcy: {}{}".format( "      ", np.where((df[df['AccountID'] == AcctID]['AccountExceptionTypeID'].values[0] == 1)&(df[df['AccountID'] == AcctID]['AccountExceptionStatusID'].values[0] == 5), "YES", "NO"))\
                +"\nCurrent Balance: {}{}".format( "   $", df[df['AccountID'] == AcctID]['ccBalance'].values[0])\
                +"\nTotal Collection: {}{}".format( "    $", np.where(df[df['AccountID'] == AcctID]['TotCollection'].values[0] is None, "0",df[df['AccountID'] == AcctID]['TotCollection'].values[0]))\
                +"\nFirst Payment: {} {}".format("      ", np.where(df[df['AccountID'] == AcctID]['FirstPay'].values[0] is None, "No Info",df[df['AccountID'] == AcctID]['FirstPay'].values[0]))\
                +"\nPayment Times: {}{}".format("     ",np.where(df[df['AccountID'] == AcctID]['Times'].values[0] is None, "No Info",df[df['AccountID'] == AcctID]['Times'].values[0]))\
                +"\nTotal Collectors: {}{}{}".format( "     ", df[df['AccountID'] == AcctID]['UniCollectors'].values[0],"\n")
        except:
                a = "Warning: Account Does Not Exist"
       
        self.nameLabel1.setText(a)
        
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
                               pwd='h7zLeFdQNhApp166')
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
                               pwd='h7zLeFdQNhApp166')

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
                               pwd='h7zLeFdQNhApp166')

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
        df4 = df4[df4.CreditUser != 'PamelaDotson']
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
                                                  ) bbc
                                          where bbc.CreditUser <> 'Pamela Dotson'""", beam)


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
