from fastapi import FastAPI
from routers.authentication import auth_router
from routers.campaigns import campaigns_router
from routers.dnc_routes import dnc_router
from routers.dedupes import dedupe_routes
from routers.campaign_rules import campaign_rule_router
from routers.load_als_routes import load_als_router
from routers.black_list import black_router
from routers.pings import ping_router
from routers.leads_route import leads_router
from database.database import create_db_and_tables

#from database.database import create_db_and_tables

app=FastAPI(title="ALS BACKEND API",
            description="The ALS API receives the request from frontend to load a list for a specific campaign and ALS checks the data spec that needs to be used for a campaign",
            version="0.2.0"
            )

""" @app.on_event("startup")
def on_start():
    create_db_and_tables() """


@app.get("/")
async def health_check():

    return {"main":"test the als endpoints"}

app.include_router(auth_router)
app.include_router(campaigns_router)
app.include_router(dnc_router)

app.include_router(dedupe_routes)
app.include_router(campaign_rule_router)
app.include_router(load_als_router)
app.include_router(black_router)
app.include_router(ping_router)
app.include_router(leads_router)

create_db_and_tables()

""" 
@app.on_event("startup")
    def on_start():
        create_db_and_tables()
        print("Table Created")

if __name__=="__main__":
    @app.on_event("startup")
    def on_start():
        create_db_and_tables()
        print("Table Created")

        
 """

