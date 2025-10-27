from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.authentication import auth_router
from routers.campaigns import campaigns_router
from routers.dnc_routes import dnc_router
from routers.dedupes import dedupe_routes
from routers.campaign_rules import campaign_rule_router
from routers.black_list import black_router
from routers.pings import ping_router
from routers.leads_route import leads_router
from database.database import create_db_and_tables
from routers.leads_route import leads_router
#from database.database import create_db_and_tables


app=FastAPI(title="ALS BACKEND API",
            description="The ALS API receives the request from frontend to load a list for a specific campaign and ALS checks the data spec that needs to be used for a campaign",
            version="0.2.0"
            )

#Not best practice you need to filter the correct domain


origins=["http://localhost:5173","http://127.0.0.1:8000/auth/login","http://127.0.0.1:8000/auth/register"]

app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

#add cors middleware chief

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
#this should go baba loading should be automatic
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
