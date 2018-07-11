# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################
import os
import sys
import uuid
import time
import pytz
import hashlib
import slugify
import platform
import datetime
import dateutil.parser

import ConfigParser

from jinja2 import Environment, FileSystemLoader
from osgeo import ogr
from cswconfig.output import BaseOutput

_m = hashlib.md5()

config = ConfigParser.ConfigParser()


def is_valid_file(parser, arg):
    """
    Check if arg is a valid file that already exists on the file system.

    Parameters
    ----------
    parser : argparse object
    arg : str

    Returns
    -------
    arg
    """
    try:
        arg = os.path.abspath(arg)
        if not os.path.exists(arg):
            parser.error("The file %s does not exist!" % arg)
        else:
            return arg
    except:
        parser.error("Invalid arguments")


def get_parser():
    """Get parser object for script xy.py."""
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(description=__doc__,
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument("--settings",
                        dest="settings",
                        help="Settings")

    parser.add_argument("-f", "--file",
                        dest="filename",
                        type=lambda x: is_valid_file(parser, x),
                        help="input FILE; must be a valid and readable ESRI Shapefile",
                        metavar="FILE")

    parser.add_argument("-t", "--template",
                        dest="template",
                        default="stengl_template",
                        help="XML template name to use [default: stengl_template]")

    parser.add_argument("--abstract",
                        dest="abstract",
                        help="Abstract")

    parser.add_argument("--topic-category",
                        dest="topicCategory",
                        help="ISO Topic Category")

    parser.add_argument("--constraints",
                        dest="constraints",
                        help="ISO Constraints")

    parser.add_argument("--data-poc-position",
                        dest="dataPOCPosition",
                        help="POC Position")

    parser.add_argument("--resource-url",
                        dest="resourceURL",
                        help="Resource URL")

    parser.add_argument("--resource-name",
                        dest="resourceName",
                        help="Resource Name")

    parser.add_argument("--lineage-statement",
                        dest="lineageStatement",
                        help="Lineage Statement")

    parser.add_argument("--keyword",
                        dest="keyword",
                        help="Keyword")

    parser.add_argument("--inspire-keyword",
                        dest="inspireKeyword",
                        help="INSPIRE Keyword")

    parser.add_argument("--timezone",
                        dest="timezone",
                        default="America/Los_Angeles",
                        help="Local TimeZone")

    parser.add_argument("--datestamp",
                        dest="datestamp",
                        help="Date Stamp")

    parser.add_argument("--datadate",
                        dest="datadate",
                        help="Data Date")

    parser.add_argument("--temporalstart",
                        dest="temporalstart",
                        help="Temporal Extent Start")

    parser.add_argument("--temporalend",
                        dest="temporalend",
                        help="Temporal Extent End")

    parser.add_argument("--output",
                        dest="output",
                        choices=['FILE', 'CSW'],
                        help="Strem Output to a destination")

    parser.add_argument("-q", "--quiet",
                        action="store_false",
                        dest="quiet",
                        default=False,
                        help="don't print status messages to stdout")
    return parser


def uuid2slug(uuidstring):
    return uuid.UUID(uuidstring).bytes.encode('base64').rstrip('=\n').replace('/', '-')


def slug2uuid(slug):
    return str(uuid.UUID(bytes=(slug + '==').replace('-', '/').decode('base64')))


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


if __name__ == "__main__":
    args = get_parser().parse_args()

    if not args.filename:
        print("Please specify a valid input file.")
        sys.exit(-1)

    if not args.quiet:
        print("Will open file %s now." % args.filename)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    if not os.path.isfile(os.path.join(dir_path, "templates", "%s.xml" % args.template)):
        print("No %s.xml template could be found under folder %s." % (args.template, os.path.join(dir_path, "templates")))
        sys.exit(-1)

    # Create the jinja2 environment.
    # Notice the use of trim_blocks, which greatly helps control whitespace.
    _m.update("tamplate [%s] / base_file [%s]" % (args.template, args.filename))

    if not args.settings:
        config.read(os.path.join(dir_path, 'settings', 'settings.ini'))
    else:
        config.read(args.settings)

    j2_env = Environment(loader=FileSystemLoader(os.path.join(dir_path, "templates")),
                         trim_blocks=True)
    template = j2_env.get_template("%s.xml" % args.template)

    ds = ogr.Open(args.filename)
    for lyr in ds:
        if not args.quiet:
            print("Layer : %s" % lyr.GetName())
            print("Feature count : %d" % lyr.GetFeatureCount())

        (xmin, xmax, ymin, ymax) = lyr.GetExtent() # not in same order as ogrinfo

        if not args.quiet:
            print("Extent : (%f, %f) - (%f %f)" % (xmin, ymin, xmax, ymax))
            print("Geometry type: %s" % ogr.GeometryTypeToName(lyr.GetGeomType()))

        srs = lyr.GetSpatialRef()
        if srs is not None:
            if not args.quiet:
                print("SRS: %s"% srs.ExportToWkt())

        lyr_defn = lyr.GetLayerDefn()
        for i in range(lyr_defn.GetFieldCount()):
            field_defn = lyr_defn.GetFieldDefn(i)
            name = field_defn.GetName()
            type = ogr.GetFieldTypeName(field_defn.GetType())
            width = field_defn.GetWidth()
            prec = field_defn.GetPrecision()
            if not args.quiet:
                print('Field %s, type %s (%d.%d)' % (name, type, width, prec))

    local = pytz.timezone(args.timezone)

    datestamp = None
    if args.datestamp:
        datestamp = dateutil.parser.parse(args.datestamp)
    iso_datestamp =  datestamp or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    if not args.quiet:
        print("ISO Date Stamp: %s" % iso_datestamp)

    datadate = datetime.datetime.now()
    if args.datadate:
        datadate = dateutil.parser.parse(args.datadate)
    else:
        datadate = datetime.datetime.utcfromtimestamp(creation_date(args.filename))
    local_dt = local.localize(datadate, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    iso_datadate = utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    if not args.quiet:
        print("ISO Data Date: %s" % iso_datadate)

    iso_temporalstart = None
    if args.temporalstart:
        temporalstart = dateutil.parser.parse(args.temporalstart)
        local_dt = local.localize(temporalstart, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        iso_temporalstart = utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    if iso_temporalstart and not args.quiet:
        print("ISO Temporal Start Extent: %s" % iso_temporalstart)

    iso_temporalend = None
    if args.temporalend:
        temporalend = dateutil.parser.parse(args.temporalend)
        local_dt = local.localize(temporalend, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        iso_temporalend = utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    if iso_temporalend and not args.quiet:
        print("ISO Temporal End Extent: %s" % iso_temporalend)

    record_identifier = slug2uuid(uuid2slug(_m.hexdigest()))
    ctx = {
        "FILEIDENTIFIER": record_identifier,
        "TITLE": slugify.slugify(os.path.splitext(os.path.basename(args.filename))[0],
                                 separator=' ',
                                 capitalize=True),
        "WEST": xmin,
        "EAST": xmax,
        "SOUTH": ymin,
        "NORTH": ymax,
        "CRS": srs.GetAuthorityCode(None),
        "ABSTRACT": args.abstract,
        "TOPIC": args.topicCategory,
        "DATAPOCPOS": args.dataPOCPosition,
        "RESOURCEURL": args.resourceURL,
        "RESOURCENAME": args.resourceName,
        "CONSTRAINTS": args.constraints,
        "LINEAGESTATEMENT": args.lineageStatement,
        "KEYWORD": args.keyword,
        "INSPIREKEYWORD": args.inspireKeyword,
        "DATADATE": iso_datadate,
        "DATESTAMP": iso_datestamp,
        "TEMPORALSTART": iso_temporalstart,
        "TEMPORALEND": iso_temporalend
    }

    if not args.quiet:
        print(ctx)

    final_xml_record = template.render(ctx)

    if not args.output:
        print(final_xml_record)
    else:
        _output = BaseOutput._get_output(args.output, config)
        if _output:
            if args.output == 'FILE':
                if not args.quiet:
                    print("Streaming to the destination throguh %s" % _output)
            elif args.output == 'CSW':
                if not args.quiet:
                    print("Streaming to CSW Server throguh %s" % _output)

            _output.stream(final_xml_record, record_id=record_identifier)
        else:
            if not args.quiet:
                print("Could not find a suitable Output Stream!")
            sys.exit(-1)
