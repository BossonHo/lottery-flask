from flask import Flask, render_template, request

from lottery import (
    big_draws,
    big_top10,
    big_recent10,
    big_range,
    analyze,

    power_draws,
    power_second,
    power_top10,
    power_recent10,
    power_range,
    analyze_second
)


app = Flask(__name__)

@app.route("/")
def home():

    return render_template(
        "home.html"
    )


@app.route("/lotto", methods=["GET","POST"])
def lotto():

    result = []
    recommend = []
    count = 0
    avg_gap = None


    if request.method == "POST":

        selected = request.form.getlist("number")

        if selected:

            selected = list(map(int,selected))

            result,recommend,count,avg_gap = analyze(
                big_draws,
                selected
            )


    return render_template(
        "index.html",
        numbers=big_range,
        result=result,
        recommend=recommend,
        count=count,
        avg_gap=avg_gap,
        selected=selected if 'selected' in locals() else [],
        top10=big_top10,
        recent10=big_recent10
    )
# ======================
# 大樂透
# ======================
@app.route("/", methods=["GET", "POST"])
def index():

    result = []
    recommend = []
    count = 0
    avg_gap = None

    if request.method == "POST":

        selected = request.form.getlist("number")

        if selected:
            selected = list(map(int, selected))

            result, recommend, count, avg_gap = analyze(
                big_draws,
                selected
            )


    return render_template(
        "index.html",

        numbers=big_range,

        result=result,
        recommend=recommend,

        count=count,
        avg_gap=avg_gap,

        top10=big_top10,
        recent10=big_recent10
    )


# ======================
# 威力彩
# ======================
@app.route("/power", methods=["GET", "POST"])
def power():

    result=[]
    recommend=[]
    second=[]
    selected = []
    count=0
    avg_gap=None


    if request.method=="POST":

        selected=request.form.getlist("number")

        if selected:

            selected=list(map(int,selected))


            result,recommend,count,avg_gap = analyze(
                power_draws,
                selected
            )


            second=analyze_second(
                selected
            )


    return render_template(
        "power.html",

        numbers=power_range,
        selected=selected,
        result=result,
        recommend=recommend,

        second_probability=second,

        count=count,
        avg_gap=avg_gap,

        top10=power_top10,
        recent10=power_recent10
    )


if __name__=="__main__":

    app.run(
        host="0.0.0.0",
        port=10000,
        debug=True
    )