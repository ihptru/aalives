#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import sqlite3
import random
import GeoIP
import re

conn = sqlite3.connect('df.sqlite')
cur = conn.cursor()

#sql = """CREATE TABLE "lives" (
#         "uid" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE ,
#         "name" VARCHAR NOT NULL ,
#         "lives" INTEGER NOT NULL DEFAULT 3,
#         "ip" VARCHAR NOT NULL,
#         "real_name" VARCHAR NOT NULL
#         )
#"""
#cur.execute(sql)
#conn.commit()

def to_file(data):
    filename = '/var/svr/df/cmds.txt'
    file = open(filename, 'a')
    file.write(data)
    file.close()
while True:
    line=sys.stdin.readline()
    line=line.rstrip()      #remove \n and space from right side
    lst=line.split(' ')     #got list of args
    if lst[0] == 'PLAYER_ENTERED':
        name = lst[1]
        ip = lst[2]
        realname = " ".join(lst[3:])
        sql = """INSERT INTO lives
            (name,ip,real_name)
            VALUES
            (
            '"""+name.replace("'","''")+"','"+ip+"','"+realname.replace("'","''")+"""'
            )
        """
        cur.execute(sql)
        conn.commit()
        random_coords = ['10 10 50 50','10 170 50 -50','170 10 50 50','170 170 50 -50']
        coords = random.choice(random_coords)
        data = "RESPAWN_PLAYER "+name+" "+coords+"\n"
        to_file(data)
    if lst[0] == 'PLAYER_LEFT':
        name = lst[1]
        sql = """DELETE FROM lives
                WHERE name = '"""+name.replace("'","''")+"'"+"""
        """
        cur.execute(sql)
        conn.commit()
    if lst[0] == 'PLAYER_RENAMED':
        old_name = lst[1]
        new_name = lst[2]
        realname = " ".join(lst[5:])
        sql = """UPDATE lives
                SET name = '"""+new_name.replace("'","''")+"'"+""", real_name = '"""+realname.replace("'","''")+"""'
                WHERE name = '"""+old_name.replace("'","''")+"'"+"""
        """
        cur.execute(sql)
        conn.commit()
    if lst[0] == 'NEW_ROUND':
        sql = """UPDATE lives
            SET lives = 3
        """
        cur.execute(sql)
        conn.commit()
    if lst[0] == 'DEATH_FRAG':
        dead = lst[1]
        sql = """SELECT lives FROM lives
                WHERE name = '"""+dead.replace("'","''")+"'"+"""
        """
        cur.execute(sql)
        conn.commit()
        row = []
        for row in cur:
            pass
        lives = row[0]
        if lives > 0:
            random_coords = ['10 10 50 50','10 170 50 -50','170 10 50 50','170 170 50 -50']
            coords = random.choice(random_coords)
            data = "RESPAWN_PLAYER "+dead+" "+coords+"\n"
            to_file(data)
            if lives == 3:
                lives_msg = '2 lives left'
            elif lives == 2:
                lives_msg = '1 life left'
            else:
                lives_msg = 'last life'
            data = "CONSOLE_MESSAGE 0xcccccc"+dead+" is respawned, "+lives_msg+"\n"
            to_file(data)
            sql = """UPDATE lives
                    SET lives = """+str(int(lives)-1)+"""
                    WHERE name = '"""+dead.replace("'","''")+"'"+"""
            """
            cur.execute(sql)
            conn.commit()
        else:
            data = "CONSOLE_MESSAGE 0xcccccc"+dead+" is dead\n"
            to_file(data)
    if lst[0] == 'DEATH_SUICIDE':
        dead = lst[1]
        sql = """SELECT lives FROM lives
                WHERE name = '"""+dead.replace("'","''")+"'"+"""
        """
        cur.execute(sql)
        conn.commit()
        row = []
        for row in cur:
            pass
        lives = row[0]
        if lives > 0:
            random_coords = ['10 10 50 50','10 170 50 -50','170 10 50 50','170 170 50 -50']
            coords = random.choice(random_coords)
            data = "RESPAWN_PLAYER "+dead+" "+coords+"\n"
            to_file(data)
            if lives == 3:
                lives_msg = '2 lives left'
            elif lives == 2:
                lives_msg = '1 life left'
            else:
                lives_msg = 'last life'
            data = "CONSOLE_MESSAGE 0xcccccc"+dead+" is respawned, "+lives_msg+"\n"
            to_file(data)
            sql = """UPDATE lives
                    SET lives = """+str(int(lives)-1)+"""
                    WHERE name = '"""+dead.replace("'","''")+"'"+"""
            """
            cur.execute(sql)
            conn.commit()
        else:
            data = "CONSOLE_MESSAGE 0xcccccc"+dead+" is dead\n"
            to_file(data)
    if lst[0] == 'GAME_END':
        sql = """DELETE FROM lives
        """
        cur.execute(sql)
        conn.commit()
    if lst[0] == 'INVALID_COMMAND':
        if lst[1] == '/location':
            name = lst[2]
            ip = lst[3]
            length=len(lst)
            if ( length == 5 ):
                gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
                country = gi.country_name_by_addr(ip)
                data = 'PLAYER_MESSAGE "'+name+'" "0xff1100You are in 0xffc000'+country+'"\n'
                to_file(data)
            else:
                gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
                request_name = "_".join(lst[5:])
                sql = """SELECT name,ip,real_name FROM lives
                """
                cur.execute(sql)
                conn.commit()
                row = []
                db_name = []
                db_ip = []
                db_realname = []
                for row in cur:
                    db_name.append(row[0])
                    db_ip.append(row[1])
                    db_realname.append(row[2])
                p = re.compile(request_name, re.IGNORECASE)
                player_data = []
                for i in range(int(len(db_name))):
                    if p.search(db_name[i]) or p.search(db_realname[i]):
                        player_data.append(db_name[i])
                        player_data.append(db_ip[i])
                        player_data.append(db_realname[i])
                if len(player_data) == 0:
                    data = 'PLAYER_MESSAGE "'+name+'" "0xff1100No matches"\n' 
                    to_file(data)
                elif len(player_data) > 3:
                    data = 'PLAYER_MESSAGE "'+name+'" "0xff1100Too many matches, be more specific"\n'
                    to_file(data)
                else:
                    if re.search("@",player_data[0]):
                        country = gi.country_name_by_addr(player_data[1])
                        data = 'PLAYER_MESSAGE "'+name+'" "0xff1100'+player_data[2]+' 0xffffff(0xff1100'+player_data[0]+'0xffffff) is in 0xffc000'+country+'"\n'
                        to_file(data)
                    else:
                        country = gi.country_name_by_addr(player_data[1])
                        data = 'PLAYER_MESSAGE "'+name+'" "0xff1100'+player_data[2]+' 0xffffffis in 0xffc000'+country+'"\n'
                        to_file(data)
        else:
            data = 'PLAYER_MESSAGE "'+lst[2]+'" "0xffffffUnknown chat command \''+lst[1]+'\'"\n'
            to_file(data)
cur.close()
