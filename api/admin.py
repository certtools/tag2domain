# --------------------------------------
# admin stuff




@app.post('/api/v1/admin/register_user',
          summary="Add a user/API-key combination",
          tags=["Admin"])
def admin_register_user(
        email: EmailStr,
        days_valid: int = default_expiry,
        credentials: HTTPBasicCredentials = Depends(check_if_admin)):
    """
    Adds a user (given by email address) to the api_keys database. Generates a new API key for them and mails it.
    """

    new_api_key = secrets.token_hex(API_KEYLEN)

    SQL = """ INSERT into api_keys (email, expires, api_key) VALUES (%s, now() + '%s days'::interval, %s) """

    cur = db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    logging.debug(cur.mogrify(SQL, (email, days_valid, new_api_key)))
    try:
        cur.execute(SQL, (email, days_valid, new_api_key))
        if 1 != cur.rowcount:  # did not update anything at all actually
            logging.warning("register_user(): did not create user in api_keys table: %s" % email)
        else:
            db_conn.commit()
            cur.close()
            send_email_api_key(email, new_api_key, days_valid)
    except Exception as ex:
        logging.error("Exception while creating user %s: %s" % (email, str(ex)))
        db_conn.rollback()
        cur.close()
        raise HTTPException(status_code=400, detail="Could not create user %s. reason: %s" % (email, str(ex)))

    return JSONResponse(status_code=HTTP_201_CREATED, content=new_api_key)


@app.get('/api/v1/admin/reset_api_key', summary="Reset the API-key", tags=["Admin"])
def admin_reset_api_key(email: EmailStr, credentials: HTTPBasicCredentials = Depends(check_if_admin)):
    """
    Reset a users' api_key.
    """
    new_api_key = secrets.token_hex(API_KEYLEN)

    SQL = """ UPDATE api_keys set api_key = %s WHERE email= %s """

    cur = db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    logging.debug(cur.mogrify(SQL, (new_api_key, email)))
    try:
        cur.execute(SQL, (new_api_key, email))
        if 0 == cur.rowcount:  # did not update anything at all actually
            logging.warning("UPDATE api_key: did not find email %s" % email)
        else:
            db_conn.commit()
            cur.close()
            send_email_api_key(email, new_api_key)
            logging.info("UPDATE api_key: updated api_key for email %s" % email)
    except Exception as ex:
        logging.error("Exception while resetting API key for user %s: %s" % (email, str(ex)))
        db_conn.rollback()
        cur.close()
        raise HTTPException(status_code=400,
                            detail="Could not reset API key for user %s. reason: %s" % (email, str(ex)))

    return JSONResponse(status_code=HTTP_200_OK, content=new_api_key)


@app.get('/api/v1/admin/remove_user',
         summary="Delete the user and the corresponding API key from the database.",
         tags=["Admin"]
         )
def admin_remove_user(email: EmailStr, credentials: HTTPBasicCredentials = Depends(check_if_admin)):
    """
    Delete a user / api_key combination
    """
    SQL = """ DELETE FROM api_keys WHERE email=%s """

    cur = db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    logging.debug(cur.mogrify(SQL, (email,)))
    try:
        cur.execute(SQL, (email,))
        if 0 == cur.rowcount:  # did not update anything at all actually
            logging.warning("remove_user(): did not find email %s" % email)
        else:
            db_conn.commit()
            cur.close()
    except Exception as ex:
        logging.error("Exception while removing user %s: %s" % (email, str(ex)))
        db_conn.rollback()
        cur.close()
        raise HTTPException(status_code=400, detail="Could not remove user %s. reason: %s" % (email, str(ex)))

    return JSONResponse(status_code=200)
