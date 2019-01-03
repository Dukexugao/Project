
import pandas as pd
import numpy as np
import pyodbc as db


def import_beam():
    beam = db.connect(driver='{SQL Server Native Client 11.0}',
                               server='20.36.19.132',
                               database = "Beam00320",
                               uid= 'xugao',
                               pwd='h7zLeFdQNhApp166')
    return beam


beam = import_beam()

def placement_report(placement):
    try:
        pd.options.mode.chained_assignment = None 
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
on ee.AccountID = op.AccountID"""
        pla = """''"""+placement+"""''"""
        query =  sqlQuery+ """  where ccPlacementInBeam IN ("""+pla + """)' execute(@query)"""
        df = pd.read_sql(query, beam)
        cols = pd.io.parsers.ParserBase({'names':df.columns})._maybe_dedup_names(df.columns)
        df.columns=cols
        df = df.drop_duplicates(subset=['AccountID'])
        df['Payer'] = np.where(df['TotCollection']>0,1,0)
        df1 = df.dropna(axis = 1, how = 'all')
        if df1.shape[0] == 0:
            abcd = "Warning: Placement Does Not Exist"
        elif df1.shape[0] > 0:
            import dateutil.parser
            abcd = "I. Placement Summary\n "+\
            "\nPlacement Name:{}{}".format("    ", df1.bfill(axis=0).loc[:, 'ccPlacementInBeam'][0])+\
            "\nPlacement Owner:{}{}".format("  ", df1.bfill(axis=0).loc[:, 'PortfolioOwner'][0])+\
            "\nPlacement Type:{}{}".format("     ", df1.bfill(axis=0).loc[:, 'Description'][0])+\
            "\nTotal Balance: {}{:.2f}".format("       $", df1['AcqBalance'].agg('sum'))+\
            "\nTotal Accounts: {}{}".format("     ", df1['AcqBalance'].agg('count'))+\
            "\nAvg Balance: {}{:.2f}".format("         $", df1['AcqBalance'].agg('sum')/df1['AcqBalance'].agg('count'))+\
            "\nFirst Assigned:{}{}".format("       ", dateutil.parser.parse(df1[['1MoveIn']].sort_values(by=['1MoveIn']).iloc[1,:].values[0].astype(str)).strftime('%Y-%m-%d'))+\
            "\nLast Assigned:{}{}".format("       ",  dateutil.parser.parse(df1[['1MoveIn']].sort_values(by=['1MoveIn'],ascending=False).iloc[1,:].values[0].astype(str)).strftime('%Y-%m-%d'))+\
            "\n\nII. Collection Summary \n"+\
            "\nTotal Payers: {}{}".format("         ", df1['Payer'].agg('sum'))+\
            "\nPayer Rate: {}{:.2f}{}".format("           ", 100*df1['Payer'].agg('sum')/df1['Payer'].agg('count'),"%")+\
            "\nTotal Collection: {}{:.2f}".format("     $", df1['TotCollection'].agg('sum'))+\
            "\nGross Liquidation: {}{:.2f}{}".format("  ", 100*df1['TotCollection'].agg('sum')/df1['AcqBalance'].agg('sum'),"%")+\
            "\nAvg Pay(Per Payer): {}{:.2f}{}".format("$", df1['TotCollection'].agg('sum')/df1['Payer'].agg('sum'),"\n\n\n")
    except:
        abcd = "Warning: Input Error"
    return abcd

