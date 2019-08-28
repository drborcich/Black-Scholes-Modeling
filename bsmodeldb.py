#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 18:55:10 2019

@author: drb
"""
 
 # Black Scholes Options Pricing Tool
 # Takes 4 inputs for model, assumes 2% risk free interest rate

 # Given market price of security, will provide implied volatility,
 # theoretical price, implied vol, and Greeks




import numpy as np
import math
from scipy.stats import norm as norm
#import scipy.integrate as integrate
#import matplotlib.pyplot as plt

rate = .02   ### risk free rate of interest


 # FOR BOTH funcs below:
  # find respective d value
  # later used in cdf to create array of d values 
def d_func1(S, K, vol, YTE):       
    d1 = (np.log(S/K) + ((rate+(vol**2)/2)*YTE))/(vol*(YTE**(.5)))
    #d1 = (d1**2)/-2
    d1 = round(d1, 4)
    return(d1)

def d_func2(S, K, vol, YTE): 
    d1 = (np.log(S/K) + ((rate+(vol**2)/2)*YTE))/(vol*(YTE**(.5)))
    d2 = d1 - vol*math.sqrt(YTE)     # here is that d2 adjustment
    #print('sig ' + str(d1-d2))
    #d2 = (d2**2)/-2
    d2 = round(d2, 4)        # round to 4 places 
    return(d2)


def find_vol(S, K, vol_var, YTE, option_mp, parity):
    option_up = option_mp + .05      # if call is in +/- 10% range
    option_down = option_mp - .05    # this range is fixed to mkt price
    end = False
    if parity == 1:  # for CALLS
        option_incr = get_call(S, K, vol_var, YTE, parity) # var for call price vol test
    else: 
        option_incr = get_put(S, K, vol_var, YTE, parity)
    #print("mkt " + str(call_mp))
    #print("up " + str(call_up))
    #print("down " + str(call_down))
    
            # loop: adjust vol up and down until within 10% range of call mkt
    #counter = 0
    while end == False:   #w/ acc +/- 10%
        if (option_incr < option_up) and (option_incr > option_down):
            #print(vol_var)
            #print(type(vol_var))
            end = True    
        elif (option_incr > option_mp) and end == False:    
            vol_var = vol_var*0.9
        elif (option_incr < option_mp) and end == False:    ### mkt price is too cheap
            vol_var = vol_var*1.10
            
        if end == False and parity == 1:     # for CALLS
            option_incr = get_call(S, K, vol_var, YTE, parity)
        if end == False and parity == 2:
            option_incr = get_put(S, K, vol_var, YTE, parity)
            
    # print theoretical price of option        
    print("\nTheoretical price = " + str(round(option_incr)))        
    return(vol_var)
    
def get_call(S, K, vol_var, YTE, parity):
    d_one = d_func1(S, K, vol_var, YTE)
    #print('d_one ' + str(d_one))  ###   test
    d_two = d_func2(S, K, vol_var, YTE)   ### implement second func, relative 
    #print('d_two ' + str(d_two))
    
    cdf_call1 = norm.cdf(d_one)     # get N(d1)
    cdf_call2 = norm.cdf(d_two)     # get N(d2)
    
    c_stock_comp = S * cdf_call1
    #print('stock comp ' + str(stock_comp))
    c_strike_comp = K *(np.exp(-rate*YTE))*cdf_call2
    #print('strike comp ' + str(strike_comp))
    call = c_stock_comp - c_strike_comp    # S*N(d1) - Kexp(-rDTE)*N(d2)
    #print("Call_incr " + str(call_incr))      # most recent guess at call price  
    return(call)
  
    
def get_put(S, K, vol_var, YTE, parity):
    d_one = d_func1(S, K, vol_var, YTE)
    #print('d_one ' + str(d_one))
    d_two = d_func2(S, K, vol_var, YTE)   ### implement second func, relative 
    #print('d_two ' + str(d_two))
    
    cdf_put1 = norm.cdf(-1.0*d_one)     # get N(-d1)
    cdf_put2 = norm.cdf(-1.0*d_two)     # get N(-d2)

    p_stock_comp = S * cdf_put1
    #print('stock comp ' + str(stock_comp))
    p_strike_comp = K *(np.exp(-rate*YTE))*cdf_put2
    #print('strike comp ' + str(strike_comp))
    put = p_strike_comp - p_stock_comp    # S*N(d1) - Kexp(-rDTE)*N(d2)
    #print("Call_incr " + str(call_incr))      # most recent guess at PUT price
    return(put)
    
    # Get Greeks using observed volatility
def greeks(S, K, vol_var, YTE, parity):
    d_one = d_func1(S, K, vol_var, YTE)
    d_two = d_func2(S, K, vol_var, YTE)
    
    Nd1 = round(norm.cdf(d_one),4)
    # normal probability density function
    Nprime = math.exp(((-1.0*d_one)**2)/2.0) * 1.0/((2.0*math.pi)**(.5))
    if parity == 1:
        print("Delta = " + str(Nd1))
        Nd2 = round(norm.cdf(d_two),4)
        theta = -1*S*Nprime*vol_var/(2*(YTE**(.5)))
        theta = theta - rate*K*math.exp(-1.0*rate*YTE)*Nd2
        theta = theta/365.0   ### put in daily terms
        print("Theta = " + str(round(theta, 3)))
    else:    # for puts
        print("Delta = " + str(Nd1-1))
        Nd2 = round(norm.cdf(-1.0*d_two),4)
        theta = -1*S*Nprime*vol_var/(2*(YTE**(.5)))
        theta = theta + rate*K*math.exp(-1*rate*YTE)*Nd2  ### add K, negative d2
        theta = theta/365.0   ### put in daily terms
        print("Theta = " + str(round(theta, 3)))
    
    gamma = Nprime/(S*vol_var*(YTE**(.5)))
    print("Gamma = " + str(round(gamma,3)))
    vega = S*(YTE**(.5))* Nprime
    vega = vega/100.0 ### put in percentage point terms
    print("Vega = " + str(round(vega,3)))
 
    return
  
   
def main():     
    print("Please enter necessary inputs to model the price of an option.")
    S =  input('Stock price: ') 
    K = input('Strike price: ')
    vol_obs = input('Annualized volatility, as decimal: ')   # need obs vol for IV comps
    YTE = input('Time to expiry, in years: ')
    #risk_free = input('Enter risk-free rate: ')
    option_mp = input('Market price of option: ') 
    parity = input('Parity (1 for Call, 2 for Put): ')
    
    S = float(S)
    K = float(K)
    vol_obs = float(vol_obs)
    YTE = float(YTE)
    
    IV = find_vol(S, K, vol_obs, YTE, option_mp, parity)  
    IV = round(IV * 100.0, 2)
    print("IV = " + str(IV) + "%")
    greeks(S, K, vol_obs, YTE, parity)  

    return

main()