# -*- coding: utf-8 -*-
import time

class Friend:
    @classmethod
    def add_friend_request(cls, db, uid, friend_uid):
        now = int(time.time())
        sql = "INSERT INTO friend_request(uid, friend_uid, timestamp) VALUES(%s, %s, %s)"
        r = db.execute(sql, (uid, friend_uid, now))
        req_id = r.lastrowid
        return req_id
    
    @classmethod
    def get_friend_request(cls, db, req_id):
        sql = "SELECT uid, friend_uid, timestamp FROM friend_request WHERE id=%s"
        r = db.execute(sql, (req_id,))
        return r.fetchone()


    @classmethod
    def add_friend_relation(cls, db, uid, friend_uid):
        db.begin()
        sql = "INSERT INTO friend(uid, friend_uid) VALUES(%s, %s)"
        db.execute(sql, (uid, friend_uid))
        db.execute(sql, (friend_uid, uid))
        db.commit()

    @classmethod
    def delete_friend_relation(cls, db, uid, friend_uid):
        db.begin()
        sql = "DELETE FROM friend WHERE uid=%s AND friend_uid=%s"
        db.execute(sql, (uid, friend_uid))
        db.execute(sql, (friend_uid, uid))
        db.commit()
        
