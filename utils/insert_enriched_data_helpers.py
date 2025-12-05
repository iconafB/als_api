
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
# Helper function to convert dict to tuple


def get_tuple(datadictlist, num):

    rows = []
    for datadict in datadictlist:
        if num == 1:
            tuple_data = (
                datadict['mobile_Number'], datadict['IDNo'], datadict['Title'], datadict['forename'],
                datadict['lastname'], datadict['birth_date'], None, datadict['Race'], datadict['gender'],
                datadict['Marital_Status'], None, None, datadict['derived_income'], 'Enriched', None
            )
        elif num == 2:
            tuple_data = (
                datadict['mobile_Number'], datadict.get('Home_number'), datadict.get('Work_number'),
                datadict.get('mobile_Number'), datadict.get('mobile_Number2'), datadict.get('mobile_Number3'),
                datadict.get('mobile_Number4'), datadict.get('mobile_Number5'), datadict.get('mobile_Number6'), None
            )
        elif num == 3:
            tuple_data = (
                datadict['mobile_Number'], datadict['cipro_reg'], datadict['Deed_office_reg'], datadict['vehicle_owner'],
                datadict['cr_score_tu'], datadict['monthly_expenditure'], datadict['owns_cr_card'], datadict['cr_card_rem_bal'],
                datadict['owns_st_card'], datadict['st_card_rem_bal'], datadict['has_loan_acc'], datadict['loan_acc_rem_bal'],
                datadict['has_st_loan'], datadict['st_loan_bal'], datadict['has_1mth_loan'], datadict['onemth_loan_bal'],
                datadict['sti_insurance'], datadict['has_sequestration'], datadict['has_admin_order'],
                datadict['under_debt_review'], datadict['has_judgements']
            )
        elif num == 4:
            tuple_data = (
                datadict['mobile_Number'], datadict.get('make'), datadict.get('model'), datadict.get('year')
            )
        elif num == 5:
            tuple_data = (datadict['mobile_Number'], None, None, None)
        elif num == 6:
            tuple_data = (
                datadict['mobile_Number'], datadict['line1'], datadict['line2'], datadict['line3'], datadict['line4'],
                datadict['PCode'], datadict['Province'], None
            )
        rows.append(tuple_data)
    return rows



# Async insert helper

async def insert_vendor_list(session: AsyncSession, sqlstmt: str, vendor_list: List[tuple]):
    try:
        async with session.begin():
            conn = await session.connection()
            await conn.exec_driver_sql(sqlstmt, vendor_list)
    except Exception as e:
        await session.rollback()
        raise e
