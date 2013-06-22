#!~/reddit-tools/bin/python

import praw
import sys, os
import re
import logging
from ConfigParser import SafeConfigParser
from datetime import datetime, timedelta
import time



def get_current_utc_timestamp():
    dt = datetime.utcnow()
    dt_tuple = dt.timetuple()
    dt_tuple = dt_tuple[0:8] + (0,)
    return int(time.mktime(dt_tuple) - time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0)))


# Iiiit's showtime!
def main():
    # set up the config parser
    cfg_file = SafeConfigParser()
    path_to_cfg = os.path.abspath(os.path.dirname(sys.argv[0]))
    path_to_cfg = os.path.join(path_to_cfg, 'sfwporn-flair.cfg')
    cfg_file.read(path_to_cfg)
    
    # configure logging
    logging.basicConfig(level=getattr(logging, cfg_file.get('logging', 'level')))
    
    flair_class = cfg_file.get('flair', 'css_class')
    # no need to read this value
    # last_check = float(cfg_file.get('subreddit', 'last_check'))
    ignore_subreddit = cfg_file.get('subreddit', 'ignore_subreddit')
    
    reddit_username = cfg_file.get('reddit', 'username')
    reddit_password = cfg_file.get('reddit', 'password')
    reddit_useragent = cfg_file.get('reddit', 'user_agent')
    
    SUBMISSION_BACKLOG_LIMIT = timedelta(days=2)
    stop_time = datetime.utcnow() - SUBMISSION_BACKLOG_LIMIT

    start_time = get_current_utc_timestamp()

    logging.info('Logging in as /u/'+reddit_username)

    r = praw.Reddit(user_agent=reddit_useragent)
    r.login(reddit_username, reddit_password)
    
    # unfortunately, due to the need for approved-oinly submissions, we can't use `place_holder=thing_id` here
    results = r.search('[oc] [os]', subreddit='mod', sort='new', limit=1000)


    new_flair_count = 0

    for result in results:            
        # ignore this subreddit
        if result.subreddit.display_name.lower() == ignore_subreddit:
            continue

        # hit the end of the checks
        # if datetime.utcfromtimestamp(result.created_utc) <= datetime.utcfromtimestamp(last_check):
        #     break
        
        # always check through to the backlog limit
        submission_time = datetime.utcfromtimestamp(result.created_utc)                
        if submission_time <= stop_time:
            logging.debug('Reached backlog limit')
            break

        # gotta match [OC] or [OS] in the title
        if not re.search('.*((\(|\[)oc(\)|\])|(\(|\[)os(\)|\]))+.*', result.title.lower(), re.IGNORECASE|re.DOTALL|re.UNICODE):
            continue

        # only flair human-approved posts
        if (not result.approved_by) or (result.approved_by == None) or (result.approved_by == "None"):
            continue

        logging.debug(result.title+" submitted by "+result.author.name+" on "+datetime.fromtimestamp(result.created).strftime('%Y-%m-%d %H:%M:%S'))

        logging.debug('  Setting flair for '+result.author.name+' in /r/'+result.subreddit.display_name+' to '+flair_class)

        if result.author_flair_css_class is None:
            result.subreddit.set_flair(result.author, flair_css_class=flair_class)
            logging.debug('    Success!')
        else:
            if flair_class not in result.author_flair_css_class:
                result.subreddit.set_flair(result.author, flair_css_class=flair_class)
                new_flair_count = new_flair_count + 1
                logging.debug('    Success!')
            else:
                logging.debug('    User already has flair')
        
    try:
      cfg_file.set('subreddit', 'last_check', datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'))
      cfg_file.write(open(path_to_cfg, 'w'))
    except:
      logging.warn("Something bad happened...")
    
    if new_flair_count == 0:
        logging.info("No new OC flair this run.")
    else:
        logging.info("Flaired "+str(new_flair_count)+" new users!")
    
    logging.info("Done!")

if __name__ == '__main__':
    main()
