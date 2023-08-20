from datetime import datetime
import json, csv
try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO ## for Python 3

import argparse
import pywbem

class EmcHealthReport(object):
    def __init__(self, ip, user="admin",pwd="#1Password"):
        self.ip = ip
        self.url = "https://%s:5989" % ip
        self.user = user
        self.pwd = pwd
        self.connection = pywbem.WBEMConnection(
                            self.url, 
                            (self.user, self.pwd),
                            default_namespace="/root/emc",
                            no_verification=True)
    
    
    def getAllArrays(self):
        registered_arrays = self.connection.EnumerateInstanceNames("Clar_StorageSystem")
        return registered_arrays
        
    def getArray(self, array_serial):
        registered_arrays = self.getAllArrays()
        array = next(iter(i for i in registered_arrays if i['Name'] == "CLARiiON+{0}".format(array_serial)) , None )
        return array
            
    def healthcheck(self):
        # Generate our time stamp
        timestamp = datetime.now().strftime("%s")
        array_list = self.getAllArrays()
        
        # Devices we're  getting status on
        health_classes = ["EMC_LinkControlDevice", "EMC_PowerDevice",
                          "EMC_BatteryDevice", "EMC_StorageProcessorSystem",
                          "EMC_DiskDrive"]
        healthcheck_records = []
        healthcheck_records.append(['array','device_type','device_id','timestamp','status'])
        
        for array in array_list:
            for device in health_classes:
                dev_instance = self.connection.Associators(array, ResultClass=device)
                for inst in dev_instance:
                    if "DiskDrive" in device:
                        device_id = inst["SystemName"] + "+" + inst["Name"]
                    elif "StorageProcessor" in device:
                        device_id = inst["EMCBSPInstanceID"]
                    else:
                        device_id = inst["DeviceID"]
                    
                    healthcheck_records.append([
                        array['Name'].split('+')[1],
                        "emc.vnx.health.Status.{0}".format(device),
                        device_id,
                        timestamp,
                        " ".join(inst["StatusDescriptions"])
                    ])
                
        # For enclosures we need to locate the ArrayChassis
        chassis_list = self.connection.EnumerateInstanceNames("EMC_ArrayChassis")
        for array_chassis in chassis_list:
            # Now we can locate enclosures
            enclosures = self.connection.Associators(array_chassis,
                                               ResultClass="EMC_EnclosureChassis")
            for inst in enclosures:
                healthcheck_records.append([
                    inst["Tag"].split('+')[1],
                    "emc.vnx.health.Status.{0}".format(device),
                    inst["Tag"],
                    timestamp,
                    " ".join(inst["StatusDescriptions"])
                ])
    
        return healthcheck_records
    
    def to_csv(self, delimiter=','):
        table = self.healthcheck()
        si = StringIO.StringIO()
        writer = csv.writer(si, delimiter=delimiter)
        writer.writerows(table)
        output=si.getvalue()
        si.close()
        return output
    
    def to_dict(self):
        table = self.healthcheck()
        headers = table[0]
        dict_table = [ { headers[i] : row[i] for i in range(len(row)) } for row in table[1:] ]
        return dict_table
    
    def to_json(self):
        return json.dumps(self.to_dict())

def main():
    #Parse the arguments
    parser = argparse.ArgumentParser(add_help=False)
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    
    #required arguments
    required.add_argument('-s','--server',help='EMC SMI-S Server IP', required=True)
    
    #optional arguments
    optional.add_argument('-h', '--help', action='help', help='show this help message and exit')
    optional.add_argument('-u','--user',help='SMI-S Username (default=admin)', default='admin')
    optional.add_argument('-p','--pwd',help='SMI-S Password (default=#1Password)', default='#1Password')
    optional.add_argument('-t','--type',help='Report Type (csv|tsv|json) (default=csv)', default='csv')
    args = parser.parse_args()

    healthcheck = EmcHealthReport(
        smis_ip=args.server,
        smis_user=args.user,
        smis_pass=args.pwd
    )

    if args.type.lower() == "json":
        report = healthcheck.to_json()
    elif args.type.lower() == "csv":
        report = healthcheck.to_csv()
    elif args.type.lower() == "tsv":
        report = healthcheck.to_csv(delimiter="\t")
    print(report)

if __name__ == '__main__':
    main()
