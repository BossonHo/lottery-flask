import requests
import pandas as pd

from io import StringIO
from collections import Counter



# ==========================
# 抓資料
# ==========================

def fetch_lottery(url, pages):

    data=[]


    for i in range(1,pages+1):

        full=f"{url}?indexpage={i}&orderby=new"


        r=requests.get(
            full,
            timeout=20
        )

        r.encoding="big5"


        tables=pd.read_html(
            StringIO(r.text)
        )


        df=tables[1]

        df=df[df[0]!="期數"]

        data.append(df)



    df=pd.concat(
        data,
        ignore_index=True
    )


    df.columns=[
        "期數",
        "日期",
        "第一區",
        "第二區",
        "備註"
    ]


    first=df["第一區"].str.split(
        ",",
        expand=True
    )


    first.columns=[
        "A",
        "B",
        "C",
        "D",
        "E",
        "F"
    ]


    first=first.astype(int)


    second=df["第二區"].astype(int)


    return (
        first.values.tolist(),
        second.tolist()
    )



# ==========================
# 大樂透
# ==========================

big_draws,big_second = fetch_lottery(
    "https://www.pilio.idv.tw/ltobig/listbbk.asp",
    72
)


# ==========================
# 威力彩
# ==========================

power_draws,power_second = fetch_lottery(
    "https://www.pilio.idv.tw/lto/listbbk.asp",
    60
)



# ==========================
# 統計
# ==========================

def flat(draws):

    return [
        n
        for d in draws
        for n in d
    ]



def top10(draws):

    return Counter(
        flat(draws)
    ).most_common(10)



def recent(draws,n=50):

    return top10(
        draws[:n]
    )



big_top10=top10(big_draws)
big_recent10=recent(big_draws)


power_top10=top10(power_draws)
power_recent10=recent(power_draws)



big_range=range(1,50)
power_range=range(1,39)



# ==========================
# 共現分析
# ==========================

def analyze(draws,selected):


    match=[

        d for d in draws

        if all(
            x in d
            for x in selected
        )
    ]


    count=len(match)


    if count==0:

        return [],[],0,None



    counter=Counter()


    for d in match:

        counter.update(d)



    result=[]


    recommend=[]


    for n,c in counter.most_common():

        percent=round(
            c/count*100,
            1
        )


        result.append(
            (
                n,
                c,
                percent
            )
        )


        if n not in selected:

            recommend.append(
                (
                    n,
                    c,
                    percent
                )
            )



    avg=round(
        len(draws)/count,
        2
    )


    return (
        result[:8],
        recommend[:8],
        count,
        avg
    )



# ==========================
# 威力彩第二區
# ==========================

def analyze_second(selected):


    index=[]


    for i,d in enumerate(power_draws):

        if all(
            x in d
            for x in selected
        ):

            index.append(i)



    if not index:

        return []



    nums=[

        power_second[i]

        for i in index

    ]


    counter=Counter(nums)


    total=len(nums)


    result=[]


    for n,c in counter.most_common():


        p=round(
            c/total*100,
            1
        )


        bias=round(
            p/12.5,
            2
        )


        result.append(
            (
                n,
                c,
                p,
                bias
            )
        )

    #print(result)
    return result
