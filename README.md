# SFWPN [OC] Flair script

## Introduction

This is a fairly hacked-together reddit moderation script, roughly based on code from
github/Deimos (/u/Deimorz) which crawls every subreddit the account connected moderate
and looks for approved submissions with [OC] in the title, and grants the user fancy
flair.

## Configuration

Example config file is included, just update, remove ".example" and you're set.
For regular usage, suggest cron. To work with virtualenv, use `/path/to/virtualenv
/bin/python sfwporn-flair.py`.

## Depends

Python 2.7 with latest PRAW. Best create a virtual environment for this.