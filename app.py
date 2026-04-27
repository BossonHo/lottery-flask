from flask import Flask, render_template_string, request
import requests
import pandas as pd
from io import StringIO
from collections import Counter

app = Flask(__name__)

# =========================
# 1️⃣ 抓資料
# =========================
def fetch_lottery_data():
    url = "https://www.pilio.idv.tw/ltobig/listbbk.asp?indexpage={}&orderby=new"
    df_list = []

    for i in range(1, 72):
        r = requests.get(url.format(i))
        r.encoding = "big5"
        dfs = pd.read_html(StringIO(r.text))
        df_list.append(dfs[1])

    df = pd.concat(df_list, ignore_index=True)
    df = df[df[0] != "期數"]
    df.columns = ["期數", "日期", "第一區", "第二區", "備註"]

    df_1 = df["第一區"].str.split(",", expand=True)
    df_1.columns = ["第一", "第二", "第三", "第四", "第五", "第六"]
    df_1 = df_1.astype(int)

    return df_1

df_1 = fetch_lottery_data()
cols = ["第一", "第二", "第三", "第四", "第五", "第六"]
draws = df_1[cols].values.tolist()

# =========================
# 📊 Top 10 全局統計
# =========================
flat_all = sum(draws, [])
global_counter = Counter(flat_all)
top10_global = global_counter.most_common(10)

first_range = sorted(set(flat_all))

# =========================
# 2️⃣ AND + 共現分析（已修改）
# =========================
def calculate_prob(selected_numbers=None):
    if not selected_numbers:
        return [], 0, None

    # 找出「包含輸入數字」的期數
    filtered = [d for d in draws if all(n in d for n in selected_numbers)]
    count = len(filtered)

    if not filtered:
        return [], 0, None

    avg_gap = round(len(draws) / count, 2)

    # =========================
    # 🔥 共現統計（重點修改）
    # =========================
    counter = Counter()

    for d in filtered:
        for n in d:
            counter[n] += 1   # ✅ 不排除 selected_numbers（核心改動）

    # Top 5 ranking
    result = counter.most_common(5)

    return result, count, avg_gap

# =========================
# 3️⃣ HTML
# =========================
HTML = """
<html>
<head>
<style>
body {
    font-family: Arial;
    background: #f5f7fb;
    margin: 0;
}

.container {
    display: flex;
    padding: 20px;
    gap: 20px;
}

.left, .right {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.left { flex: 3; }
.right { flex: 1; }

.num-grid {
    display: grid;
    grid-template-columns: repeat(10, 1fr);
    gap: 5px;
}

button {
    margin-top: 10px;
    padding: 10px;
    width: 100%;
    background: #4CAF50;
    color: white;
    border: none;
    border-radius: 8px;
}

.card {
    padding: 8px;
    margin: 5px 0;
    background: #f1f3f8;
    border-radius: 6px;
}
</style>
</head>

<body>

<div class="container">

<!-- 左邊 -->
<div class="left">
<h2>大樂透分析（共現版）</h2>

<form method="post">
<div class="num-grid">
{% for n in first_range %}
<label><input type="checkbox" name="first" value="{{n}}"> {{n}}</label>
{% endfor %}
</div>

<button type="submit">計算</button>
</form>

{% if result %}
<hr>
<h3>📌 符合期數：{{match_count}}</h3>
<h3>📌 平均 {{avg_gap}} 期出現一次</h3>

<h3>🔥 共現 Top 5</h3>
{% for n,p in result %}
<div class="card">{{n}} → {{p}} 次</div>
{% endfor %}
{% endif %}

</div>

<!-- 右邊 -->
<div class="right">
<h3>🔥 最常出現 Top 10</h3>

{% for n,c in top10 %}
<div class="card">{{n}} ： {{c}} 次</div>
{% endfor %}

</div>

</div>

</body>
</html>
"""

# =========================
# 4️⃣ Route
# =========================
@app.route('/', methods=['GET','POST'])
def index():
    result=None
    match_count=0
    avg_gap=None

    if request.method=='POST':
        selected = request.form.getlist('first')
        selected = list(map(int, selected)) if selected else None
        result, match_count, avg_gap = calculate_prob(selected)

    return render_template_string(
        HTML,
        result=result,
        match_count=match_count,
        avg_gap=avg_gap,
        first_range=first_range,
        top10=top10_global
    )

# =========================
# 5️⃣ Run
# =========================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)