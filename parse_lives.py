#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2011 Popov Igor
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import sqlite3
import random
import GeoIP
import re
import os

def db_init():
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()

    sql = """CREATE TABLE "lives" (
             "uid" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE ,
             "name" VARCHAR NOT NULL ,
             "lives" INTEGER NOT NULL DEFAULT 3,
             "ip" VARCHAR NOT NULL,
             "real_name" VARCHAR NOT NULL,
             "max_lives" INTEGER NOT NULL DEFAULT 3
             )
    """
    cur.execute(sql)
    conn.commit()
    cur.close()

if not os.path.exists('db.sqlite'):
    db_init()

conn = sqlite3.connect('db.sqlite')
cur = conn.cursor()

global max_lives_amount
max_lives_amount = 3

sql = """SELECT max_lives FROM "lives"
        ORDER BY max_lives LIMIT 1
"""
cur.execute(sql)
conn.commit()
row = []
for row in cur:
    pass
if row != []:
    max_lives_amount = row[0]


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
            (name,ip,real_name,lives,max_lives)
            VALUES
            (
            '"""+name.replace("'","''")+"','"+ip+"','"+realname.replace("'","''")+"""','"""+str(max_lives_amount)+"""','"""+str(max_lives_amount)+"""'
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
            SET lives = """+str(max_lives_amount)+"""
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
            if lives == 2:
                lives_msg = '1 life left'
            elif lives == 1:
                lives_msg = 'last life'
            else:
                lives_msg = str(int(lives - 1))+' lives left'
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
        if row == []:
            lives = row[0]
        else:
            lives = 0
        if lives > 0:
            random_coords = ['10 10 50 50','10 170 50 -50','170 10 50 50','170 170 50 -50']
            coords = random.choice(random_coords)
            data = "RESPAWN_PLAYER "+dead+" "+coords+"\n"
            to_file(data)
            if lives == 2:
                lives_msg = '1 life left'
            elif lives == 1:
                lives_msg = 'last life'
            else:
                lives_msg = str(int(lives - 1))+' lives left'
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
        if lst[1] == '/max_lives':
            if int(lst[4]) <= 2 :
                name = lst[2]
                if len(lst[5:]) == 1:
                    max_lives = ''
                    try:
                        max_lives = int(lst[5])
                    except:
                        data = 'PLAYER_MESSAGE "'+name+'" "0xff0000Amount error"\n'
                        to_file(data)
                    if type(max_lives) == int:
                        sql = """UPDATE lives
                                SET max_lives = '"""+str(max_lives)+"""'
                        """
                        cur.execute(sql)
                        conn.commit()
                        data = 'PLAYER_MESSAGE "'+name+'" "Changes are applied!"\n'
                        to_file(data)
                elif len(lst[5:]) > 1:  #request amount of lives for player
                    max_lives = ''
                    try:
                        max_lives = int(lst[5])
                    except:
                        data = 'PLAYER_MESSAGE "'+name+'" "0xff0000Amount error"\n'
                        to_file(data)
                    if type(max_lives) == int:
                        to_whom = " ".join(lst[6:])
                        sql = """SELECT max_lives,lives FROM lives
                                WHERE upper(name) LIKE upper('%"""+to_whom.replace("'","''")+"""%')
                        """
                        cur.execute(sql)
                        conn.commit()
                        row = []
                        for row in cur:
                            pass
                        if row != []:
                            if ( len(row) == 1):
                                current_max_lives = row[0]
                                current_lives = row[1]
                                add_lives = str(int(current_lives) + (int(max_lives) - int(current_max_lives)))
                                if add_lives < current_lives:
                                    data = 'PLAYER_MESSAGE "'+name+'" "You can set up less lives then player has!"\n'
                                    to_file(data)
                                else:
                                    sql = """UPDATE lives
                                            SET max_lives = '"""+str(max_lives)+"""'
                                            WHERE upper(name) LIKE upper('%"""+to_whom.replace("'","''")+"""%')
                                    """
                                    cur.execute(sql)
                                    conn.commit()
                                    sql = """UPDATE lives
                                            SET lives = '"""+add_lives+"""'
                                            WHERE upper(name) LIKE upper('%"""+to_whom.replace("'","''")+"""%')
                                    """
                                    cur.execute(sql)
                                    conn.commit()
                                    data = 'PLAYER_MESSAGE "'+name+'" "Changes are applied!"\n'
                                    to_file(data)
                            else:
                                data = 'PLAYER_MESSAGE "'+name+'" "Too many matches!"\n'
                                to_file(data)
                        else:
                            data = 'PLAYER_MESSAGE "'+name+'" "No such a player online!"\n'
                            to_file(data)
                else:
                    data = 'PLAYER_MESSAGE "'+name+'" "0xff0000Error!"\n'
                    to_file(data)
                
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
