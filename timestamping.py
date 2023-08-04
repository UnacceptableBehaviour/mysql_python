#! /usr/bin/env python

from datetime import datetime
# from timestamping import nix_time_ms, day_from_nix_time, time24h_from_nix_time, hr_readable_from_nix
# from timestamping import hr_readable_date_from_nix, roll_over_from_nix_time


# time helper function for time since epoch, day, 24hr clock
# https://www.techatbloomberg.com/blog/work-dates-time-python/ < overview timezones
#def nix_time_ms(dt=datetime.now()):  < this assign the time the def statement is execute as the default! # https://effbot.org/zone/default-values.htm
def nix_time_ms(dt=None):                           # > 1691156542107
    if dt == None: dt = datetime.now()
    # ms 1572029735987
    epoch = datetime.utcfromtimestamp(0) 
    # print(f"nix_time_ms: {int( (dt - epoch).total_seconds() * 1000.0 )}")

    return int( (dt - epoch).total_seconds() * 1000.0 )     

def day_from_nix_time(nix_time_ms):                 # > 'fri'
    return datetime.utcfromtimestamp(nix_time_ms / 1000.0).strftime("%a").lower()

def time24h_from_nix_time(nix_time_ms):             # > '1342'
    return datetime.utcfromtimestamp(nix_time_ms / 1000.0).strftime("%H%M")

def hr_readable_from_nix(nix_time_ms):              # > '2023 08 04 1342'
    return datetime.utcfromtimestamp(nix_time_ms / 1000.0).strftime("%Y %m %d %H%M")

def hr_readable_date_from_nix(nix_time_ms):         # > '2023 08 04'
    return datetime.utcfromtimestamp(nix_time_ms / 1000.0).strftime("%Y %m %d")

# good for HR backup directory naming - ms on the END
def hr_readable_w_nix_ms_from_nix(nix_time_ms):     # > '2023_08_04_134222_107'
    ms = nix_time_ms % 1000
    return datetime.utcfromtimestamp(nix_time_ms / 1000.0).strftime("%Y_%m_%d_%H%M%S") + "_" + str(ms)

# Unecessarily complicated refactor!
#
# %Y 2049 year
# %m month
# %d 05 day 0pad
# %H 09 hours 24h 0pad
# %m 05 minutes 0pad
# get rollover 5AM time as nix time
# https://docs.python.org/3.5/library/datetime.html#datetime.datetime.replace
#
# time_in_the_AM_to_rollover 24h 4 digit string 5am = '0500'
def roll_over_from_nix_time(nix_ts, time_in_the_AM_to_rollover='0500'):
    rollover_nix_time_ms = 0

    ONE_DAY_IN_MS = 24*60*60*1000
    HRS_IN_DAY = 24
    MIN_IN_HOUR = 60

    if len(time_in_the_AM_to_rollover) == 4:
        h = int(time_in_the_AM_to_rollover[0:2])
        herr = int(h / HRS_IN_DAY)      # check for out of range
        h = h % HRS_IN_DAY

        m = int(time_in_the_AM_to_rollover[2:4])
        merr = int(m / MIN_IN_HOUR)     # check for out of range
        m = m % MIN_IN_HOUR

        if (herr or merr):
            raise(ArgsOutOfBounds(f"roll_over_from_nix_time - arguments out of range; H{herr}-M{merr} >=1 => ERROR"))

    else:       # set to 5am - 0500
        h=5
        m=0

    # convert to datetime to overwrite hrs/mins then back to nixtime
    # ts1_date:0500
    nixtime_opt1 = nix_time_ms( datetime.utcfromtimestamp(nix_ts / 1000.0).replace(hour=h, minute=m) )

    # debug
    nix_ts_hr = hr_readable_from_nix(nix_ts)

    if nixtime_opt1 > nix_ts:
        rollover_nix_time_ms = nixtime_opt1
        #print(f"<{nix_ts}|{nix_ts_hr}> - {nix_ts} - <{rollover_nix_time_ms}|{hr_readable_from_nix(rollover_nix_time_ms)}> -  {time_in_the_AM_to_rollover} - {h}:{m} - ERR:{herr} or {merr} = {herr or merr}")
    else:
        nix_ts_plus_1_day = nix_ts + ONE_DAY_IN_MS   # this takes care of rollover, last day of month / year etc
                                                            # set hours minute to the rollover time >--------\
        dt_rollover = datetime.utcfromtimestamp(nix_ts_plus_1_day / 1000.0).replace(hour=h, minute=m)  # <---/

        rollover_nix_time_ms = nix_time_ms(dt_rollover)
        #print(f"<{nix_ts}|{nix_ts_hr}> - {nix_ts_plus_1_day} - <{rollover_nix_time_ms}|{dt_rollover}> -  {time_in_the_AM_to_rollover} - {h}:{m} - ERR:{herr} or {merr} = {herr or merr}")

    return rollover_nix_time_ms

# What are we trying to do with this function?
# Create a rollover timestamp (R) for a passed in timestamp
# Compare a posted timestamp to the users daily tracker timestamp.
# if the posted timestamp has gone past the roll over
# R the rollover point R is, for example 5AM
#
# ts1        *                            < initial ts
# ts2                           *         < not rolled over yet
# ts3                                 *   < rolled over
#     ----R-------------------|----R-------------------|----R-------------------| < timeline
#     |         day 1         |         day 2          |
#         |         set 1          |         set 2          |
#
# if    ts1_date:0500 > ts1     roll over = ts1_date:0500
# else                          roll over = (ts1_date +1day):0500




if __name__ == '__main__':

    time_now = nix_time_ms()
    roll_over = roll_over_from_nix_time(time_now)

    print(f"TEST")
    print(f"nix_time: {time_now}")
    print(f"day: {day_from_nix_time(time_now)}")
    print(f"time24h_from_nix_time: {time24h_from_nix_time(time_now)}")
    print(f"hr_readable_from_nix: {hr_readable_from_nix(time_now)}")
    print(f"hr_readable_date_from_nix: {hr_readable_date_from_nix(time_now)}")
    
    print(f"\nROLL OVER - 0500")
    print(f"day: {day_from_nix_time(roll_over)}")
    print(f"time24h_from_nix_time: {time24h_from_nix_time(roll_over)}")
    print(f"hr_readable_from_nix: {hr_readable_from_nix(roll_over)}")
    print(f"hr_readable_date_from_nix: {hr_readable_date_from_nix(roll_over)}")
    print(f"day: {day_from_nix_time(roll_over)}")
