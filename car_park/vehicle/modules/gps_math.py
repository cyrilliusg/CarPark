
def get_period_key(dt, period):
    if period == 'day':
        return str(dt.date())
    elif period == 'month':
        return dt.strftime("%Y-%m")
    elif period == 'year':
        return str(dt.year)
    else:
        return str(dt.date())

