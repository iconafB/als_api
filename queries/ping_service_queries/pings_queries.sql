

sql =
            UPDATE origin.pinged_output_status 
            SET model_output = 'HIGH'
            WHERE 
            (DATE(pinged_date) = '{today_date}') 
            AND
            ((status = 'ANSWER' AND duration::INTEGER > 4)
            OR (status = 'BUSY' AND duration::INTEGER <= 4)
            OR (status = 'POS'));
        