from sqlmodel import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from models.person_table import Person
from models.rules_table import RulesTable
from schemas.person import PersonCreate
#create the test person
async def create_person_db(person:PersonCreate,session:AsyncSession):
    db_person=Person(**person.model_dump())
    session.add(db_person)
    await session.commit()
    await session.refresh(db_person)
    return db_person

async def get_rule_by_name_db(name:str,session:AsyncSession):
    db_person_query=select(RulesTable).where(RulesTable.name==name)
    db_person=await session.execute(db_person_query)
    result=db_person.first()
    print("print the result from the database")
    print(result)
    if result==None:
        return None
    print("print the first part of the row object")
    print(result[0])
    print("print the rule json object part")
    print(result[0].rule_json)
    print("print parts of the rule json")
    print("print the pinged data")
    print(result[0].rule_json["pinged_data"])
    print("print the salary")
    print(result[0].rule_json['salary'])
    print("print derived income")
    print(result[0].rule_json["derived_income"])
    print("print the age operator")
    print(result[0].rule_json['age'])
    # print("print the second part of the row object")
    # print(result[1])
    return result
