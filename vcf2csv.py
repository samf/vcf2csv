#! /usr/bin/env python3

import sys
import argparse
import csv

import vobject


class Recipient:
    def __init__(self, vcard):
        self.vcard = vcard
        try:
            self.name = vcard.org.value[0]
        except (AttributeError, KeyError) as err:
            pretty = vcard.prettyPrint()
            print(f'{pretty} is missing "{err}"')
            raise
        try:
            self.address = vcard.adr.value
        except (AttributeError, KeyError) as err:
            print(f'{self.name} is missing "{err}"')
            self.street = self.box

        try:
            self.street = self.address.street
            self.extended = self.address.extended
            self.city = self.address.city
            self.region = self.address.region
            self.code = self.address.code
            self.country = self.address.country
        except (AttributeError, KeyError) as err:
            print(f'{self.name} is missing "{err}"')

        self.addr1 = self.street
        self.addr2 = ""
        if "\n" in self.street:
            self.addr1, self.addr2 = self.street.split("\n")

    def __str__(self):
        return self.name

    def writerow(self, dictwriter):
        "given a dictwriter, write a csv row"
        dictwriter.writerow(self.__dict__)

    def skip_country(self, country):
        "empty out the country if it equals the passed-in country"
        if self.country == country:
            self.country = ""

    @classmethod
    def all(cls, f):
        stuff = list()
        for c in vobject.readComponents(f):
            try:
                r = cls(c)
                stuff.append(r)
            except:
                pass
        return stuff


def cli():
    p = argparse.ArgumentParser(
        description="convert apple VCF into CSV"
    )
    p.add_argument("contacts", type=argparse.FileType(mode="r"))
    p.add_argument(
        "--fields",
        nargs="*",
        choices=[
            "name",
            "address",
            "street",
            "city",
            "region",
            "code",
            "country",
        ],
        default=["name", "addr1", "addr2", "city", "region", "code", "country"],
    )
    p.add_argument("--skip-country", default="United States")
    return p


def main(args):
    p = cli()
    args = p.parse_args(args)
    peeps = Recipient.all(args.contacts)
    writer = csv.DictWriter(
        sys.stdout, fieldnames=args.fields, extrasaction="ignore"
    )
    writer.writerow(dict([(f, f) for f in args.fields]))
    for p in peeps:
        p.skip_country(args.skip_country)
        p.writerow(writer)


if __name__ == "__main__":
    main(sys.argv[1:])
