from project import app, db, models, cron
from project.functions import usd_sell_rate

if __name__ == "__main__":
    cron.add_job(id ='usd_sell_rate', func = usd_sell_rate, trigger = 'interval', seconds = 10)
    cron.start()
    app.run(host = "0.0.0.0", port = 80, debug = True)