from datetime import datetime, timedelta
from math import pow

def run_analysis(initial_investment, monthly_contribution, annual_return, annual_increase, start_date, end_date, options, purchase_date):
    monthly_return = pow(1 + annual_return / 100, 1 / 12) - 1

    if end_date is None:
        taksitli_ops = [opt["vade"] for opt in options if not opt["nakit"]]
        max_vade = max(taksitli_ops) if taksitli_ops else 0
        end_date = start_date + timedelta(days=30 * max_vade + 90)

    def monthly_by_year(year):
        delta = year - start_date.year
        return monthly_contribution * pow(1 + annual_increase / 100, delta)

    def simulate_only_investment():
        value = initial_investment
        date = start_date
        while date <= end_date:
            monthly = monthly_by_year(date.year)
            value = (value + monthly) * (1 + monthly_return)
            date += timedelta(days=30)
        return value

    pure_investment_value = simulate_only_investment()

    results = []
    for opt in options:
        label = opt["label"]
        pesinat = opt["pesinat"]
        aylik = opt["aylik"]
        vade = opt["vade"]
        is_cash = opt["nakit"]

        value = initial_investment
        total_invested = initial_investment
        total_payment = 0
        date = start_date
        schedule = []

        if is_cash:
            if pesinat <= 0:
                total_payment = 0
                schedule.append("⚠️ Nakit fiyatı girilmediği için ödeme yapılmadı.")
            else:
                # Alım tarihine kadar yatırım yapılır
                while date < purchase_date and date <= end_date:
                    monthly = monthly_by_year(date.year)
                    value = (value + monthly) * (1 + monthly_return)
                    total_invested += monthly
                    date += timedelta(days=30)

                value -= pesinat
                total_payment = pesinat
                schedule.append(f"{date.strftime('%Y-%m')} tarihinde nakit ödeme ile alındı: {int(pesinat)} ₺")
                date += timedelta(days=30)

            while date <= end_date:
                monthly = monthly_by_year(date.year)
                value = (value + monthly) * (1 + monthly_return)
                total_invested += monthly
                date += timedelta(days=30)

        else:
            # Alım tarihine kadar yatırım yapılır
            while date < purchase_date and date <= end_date:
                monthly = monthly_by_year(date.year)
                value = (value + monthly) * (1 + monthly_return)
                total_invested += monthly
                date += timedelta(days=30)

            value -= pesinat
            total_payment = pesinat
            schedule.append(f"{date.strftime('%Y-%m')}: Peşinat ödendi: {int(pesinat)} ₺")
            date += timedelta(days=30)

            for i in range(1, vade + 1):
                monthly = monthly_by_year(date.year)
                value = (value + monthly - aylik) * (1 + monthly_return)
                total_invested += monthly
                total_payment += aylik
                schedule.append(f"{date.strftime('%Y-%m')}: {i}. taksit ödendi: {int(aylik)} ₺")
                date += timedelta(days=30)

            while date <= end_date:
                monthly = monthly_by_year(date.year)
                value = (value + monthly) * (1 + monthly_return)
                total_invested += monthly
                date += timedelta(days=30)

        results.append({
            "label": label,
            "payment": round(total_payment),
            "remaining": round(value),
            "combined": round(value + total_payment),
            "investment_only": round(pure_investment_value),
            "difference": round((value + total_payment) - pure_investment_value),
            "schedule": schedule
        })

    return results
