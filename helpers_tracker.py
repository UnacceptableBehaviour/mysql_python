#! /usr/bin/env python

# tracker helpers
#from helpers_tracker import nix_time_ms, day_from_nix_time, time24h_from_nix_time

from datetime import datetime


def nix_time_ms(dt=datetime.now()):
    epoch = datetime.utcfromtimestamp(0)
    return int( (dt - epoch).total_seconds() * 1000.0 )

def day_from_nix_time(nix_time_ms):
    return datetime.utcfromtimestamp(nix_time_ms / 1000.0).strftime("%a").lower()

def time24h_from_nix_time(nix_time_ms):
    return datetime.utcfromtimestamp(nix_time_ms / 1000.0).strftime("%H%M")



# testing         
if __name__ == '__main__':
    
    # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
    day = datetime.now().strftime("%d") # day number
    day = datetime.now().strftime("%a").lower() # day 3 letter
    time = datetime.now().strftime("%H%M").lower() # 4 digit 24hr clock
    #time_since_epoch = nix_time_ms(datetime.now())
    time_since_epoch = nix_time_ms()
    day_from_nx = day_from_nix_time(time_since_epoch)
    time24_from_nx = time24h_from_nix_time(time_since_epoch)
    
    print(day, time, time_since_epoch, day_from_nx)
    print(type(datetime.now()))

    
    
    