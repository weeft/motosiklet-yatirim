from flask import Flask, render_template, request
from calculations import run_analysis
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    form_data = {
        "start_month": 4,
        "start_year": 2025,
        "end_month": 3,
        "end_year": 2027,
        "auto_end": False,
        "initial_investment": "",
        "monthly_contribution": "",
        "annual_return": "35",
        "annual_increase": "35",
        "option_html": "",
        "option_count": 0,
        "future_purchase": False,
        "purchase_month": 4,
        "purchase_year": 2025
    }

    if request.method == "POST":
        try:
            form_data["start_month"] = int(request.form.get("start_month"))
            form_data["start_year"] = int(request.form.get("start_year"))
            start_date = datetime(form_data["start_year"], form_data["start_month"], 1)

            form_data["auto_end"] = "auto_end" in request.form

            if form_data["auto_end"]:
                end_date = None
            else:
                form_data["end_month"] = int(request.form.get("end_month"))
                form_data["end_year"] = int(request.form.get("end_year"))
                end_date = datetime(form_data["end_year"], form_data["end_month"], 1)

            form_data["initial_investment"] = request.form.get("initial_investment")
            form_data["monthly_contribution"] = request.form.get("monthly_contribution")
            form_data["annual_return"] = request.form.get("annual_return")
            form_data["annual_increase"] = request.form.get("annual_increase")

            def parse_float(val): return float((val or "0").replace(",", "."))

            form_data["future_purchase"] = "future_purchase" in request.form

            if form_data["future_purchase"]:
                form_data["purchase_month"] = int(request.form.get("purchase_month"))
                form_data["purchase_year"] = int(request.form.get("purchase_year"))
                purchase_date = datetime(form_data["purchase_year"], form_data["purchase_month"], 1)
            else:
                purchase_date = start_date

            initial_investment = parse_float(form_data["initial_investment"])
            monthly_contribution = parse_float(form_data["monthly_contribution"])
            annual_return = parse_float(form_data["annual_return"])
            annual_increase = parse_float(form_data["annual_increase"])

            options = []
            option_html = ""
            index = 0

            for key in request.form:
                if key.startswith("label_"):
                    i = key.split("_")[1]
                    label = request.form.get(f"label_{i}") or f"Seçenek {i}"
                    pesinat_raw = request.form.get(f"pesinat_{i}")
                    pesinat = parse_float(pesinat_raw)
                    aylik = parse_float(request.form.get(f"aylik_{i}"))
                    vade = int(request.form.get(f"vade_{i}") or 0)
                    is_cash = f"cash_{i}" in request.form

                    options.append({
                        "label": label,
                        "pesinat": pesinat,
                        "aylik": aylik,
                        "vade": vade,
                        "nakit": is_cash
                    })

                    pesinat_display = pesinat

                    option_html += f'''
                    <div class="option-block">
                        <span class="remove-btn" onclick="this.parentElement.remove()">🗑️</span>
                        <div class="mb-2"><label>Seçenek Etiketi</label>
                        <input type="text" name="label_{i}" value="{label}" class="form-control" required></div>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="checkbox" id="cash_{i}" name="cash_{i}" onchange="toggleInputs({i})" {'checked' if is_cash else ''}>
                            <label class="form-check-label" for="cash_{i}">Nakit Alım</label>
                        </div>
                        <div id="installment_inputs_{i}" style="display:{'none' if is_cash else 'block'};">
                            <div class="mb-2"><label>Peşinat (₺)</label><input type="number" name="pesinat_{i}" value="{pesinat_display}" class="form-control"></div>
                            <div class="mb-2"><label>Aylık Taksit (₺)</label><input type="number" name="aylik_{i}" value="{aylik}" class="form-control"></div>
                            <div class="mb-2"><label>Vade (Ay)</label><input type="number" name="vade_{i}" value="{vade}" class="form-control"></div>
                        </div>
                        <div class="mb-2" id="cash_input_{i}" style="display:{'block' if is_cash else 'none'};">
                            <label>Nakit Fiyatı (₺)</label><input type="number" name="pesinat_{i}" value="{pesinat_display}" class="form-control">
                        </div>
                    </div>
                    '''
                    index += 1

            form_data["option_html"] = option_html
            form_data["option_count"] = index

            results = run_analysis(
                initial_investment,
                monthly_contribution,
                annual_return,
                annual_increase,
                start_date,
                end_date,
                options,
                purchase_date
            )

            results.sort(key=lambda r: r['difference'])  # Kötüden iyiye sırala

        except Exception as e:
            import traceback
            traceback.print_exc()
            results = [{"label": "HATA", "payment": 0, "remaining": 0, "combined": 0, "investment_only": 0, "difference": f"Hata: {str(e)}", "schedule": []}]

    return render_template("index.html", results=results, form_data=form_data)

if __name__ == "__main__":
    app.run(debug=True, port=5002)
