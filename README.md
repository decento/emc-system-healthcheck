# Emc system healthcheck using SMI-S
Healthchecks for EMC SMI-S systems like VNX and VMAX


The idea comes from Openstack documentation on adding SMI-S systems [here](https://docs.openstack.org/icehouse/config-reference/content/emc-smis-driver.html)

The EMC SMI-S provider is a part of the “Solutions Enabler with SMI” package which you can download from Powerlink (requires registration); search for “SMI-S Provider” once you log in. There are provider versions available for Windows and Linux, and either can be used. 

## Install
### Setup the EMC SMI-S provider

Setup SMI-S on the physical server/ESX VM with access to VNX or VMAX management network.


SMI-S is usually installed at /opt/emc/ECIM/ECOM/bin on Linux and C:\Program Files\EMC\ECIM\ECOM\bin on Windows. 
Run `TestSmiProvider` or `TestSmiProvider` & specify credentials for external systems to connect to this provider.
Run `addsys` to add VNX or VMAX systems.
Run `dv` to display added systems.

### On your workstation
Install the python-pywbem package on your local workstation from PyPi

``` pip install pywbem ```

Then use this package
```
decento@decento-MBP-2 emc-system-healthcheck % python3 ./emc_healthcheck.py
usage: emc_healthcheck.py -s SERVER [-h] [-u USER] [-p PWD] [-t TYPE]

```