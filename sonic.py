#!/usr/bin/env python

import re
import argparse
from sys import argv, stderr


parser = argparse.ArgumentParser(
    description="Convert your SonicWall configuration dump to a csv file"
)
parser.add_argument("--format", choices=["csv", "dhcp"], default="dhcp")
parser.add_argument("input", type=str, help="The SonicWall conifguration file")
parser.add_argument("output", type=str, help="The output file name")

args = parser.parse_args()

output_file = open(args.output, "w")

if args.format == "csv":
    output_file.write("ScopeID,IPAddress,ClientID,Name\n")

print(args.format)
with open(args.input, "rb") as handle:
    data = (handle.read()).decode("utf-8", errors="ignore")
    matches = re.findall("^Pool Entry \d+(.*?)\n\n", data, re.MULTILINE | re.DOTALL)

    for match in matches:
        ip = None
        mac = None
        entry = None
        for line in match.split("\n"):
            ip_match = re.compile("IP = (\d+\.\d+\.\d+\.\d+)").search(line)
            if ip_match:
                ip = ip_match.group(1)
            mac_match = re.compile("MAC = ([0-9AaBbCcDdEeFf\ ]*)").search(line)
            if mac_match:
                mac = mac_match.group(1).lower().replace(" ", "")
            entry_match = re.compile("Entry Name = (.*)").search(line)
            if entry_match:
                entry = entry_match.group(1).lower().replace(" ", "-")

        if ip or mac or entry:
            if args.format == "csv":
                output_file.write(",{},{},{}\n".format(ip, mac, entry))
            else:
                output_file.write(
                    "host {} {{ hardware ethernet {}; fixed-address {}; }}\n".format(
                        entry, mac, ip
                    )
                )

output_file.close()
