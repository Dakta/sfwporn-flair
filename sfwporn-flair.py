import sqlite3
import reddit
import time
from datetime import datetime
import sys, os
import re


WAIT_TIME = 60*60*24 # seconds before assigning flair, one day


def get_current_utc_timestamp():
    dt = datetime.utcnow()
    dt_tuple = dt.timetuple()
    dt_tuple = dt_tuple[0:8] + (0,)
    return int(time.mktime(dt_tuple) - time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0)))



def main():
    print 'Logging in as PornOverlord'
    r = reddit.Reddit(user_agent='PornOverlord - SFWPorn Network bot operated by /u/dakta')
    r.login('PornOverlord', '305g37YXq2Sby6120W495h8F4tYY11')

    start_time = get_current_utc_timestamp() - WAIT_TIME
    mod_sr = r.get_subreddit('mod')

    path_to_db = os.path.abspath(os.path.dirname(sys.argv[0]))
    path_to_db = os.path.join(path_to_db, 'sfwporn-flair.db')
    con = sqlite3.connect(path_to_db)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute('SELECT * FROM flair')
    rows = cur.fetchall()
    for row in rows:
        print row
        
#         results = mod_sr.search('(and title:\''+row['query']+'\' timestamp:'+str(row['last_check'])+'..'+str(start_time)+')', sort='new', limit=1000)
        results = mod_sr.search('[oc] [os]', sort='new', limit=1000)
        
        for result in results:
            print result
            
            if result.subreddit.display_name.lower() == 'moderationporn':
                continue

            if datetime.utcfromtimestamp(result.created_utc) <= datetime.utcfromtimestamp(row['last_check']):
                break

            if not re.search('.*((\(|\[)oc(\)|\])|(\(|\[)os(\)|\]))+.*', result.title.lower(), re.IGNORECASE|re.DOTALL|re.UNICODE):
                continue

            print '  Setting flair for '+result.author.name+' in /r/'+result.subreddit.display_name+' to '+row['flair_class']
            if result.author_flair_css_class is None:
                result.subreddit.set_flair(result.author, flair_css_class=row['flair_class'])
            else:
                if row['flair_class'] not in result.author_flair_css_class:
                    result.subreddit.set_flair(result.author, flair_css_class=row['flair_class'])
                else:
                    print '    User already has flair'

        cur.execute('UPDATE flair '
                    'SET last_check = '+str(start_time)+' '
                    'WHERE flair_class = \''+row['flair_class']+'\'')
        con.commit()


if __name__ == '__main__':
    main()
#     print get_current_utc_timestamp()