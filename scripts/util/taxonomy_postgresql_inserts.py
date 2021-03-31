import sys
import traceback
from argparse import ArgumentParser
import yaml
from pprint import PrettyPrinter
from collections import OrderedDict
import json

pprinter = PrettyPrinter()
pprint = pprinter.pprint


def error(s):
    sys.stderr.write(s)
    sys.exit(1)


class InvalidSpec(Exception):
    pass


def value_escape(value):
    if isinstance(value, str):
        s = value.replace("'", "''")
        return "'" + s + "'"
    elif value is None:
        return "NULL"
    else:
        return str(value)


def check_extra_keys(d, path=None):
    if len(d) > 0:
        if path is not None:
            s = "extra keys in %s: %s" % (path, ', '.join(d.keys()))
        else:
            s = "extra keys: %s" % (', '.join(d.keys()))
        raise InvalidSpec(s)


def gen_taxonomy_stmts(taxonomy, args):
    namespace = args.namespace

    # Fetch the parameters
    taxonomy_pars = OrderedDict()

    # Description
    taxonomy_pars["name"] = get_value(taxonomy, "name", type_=str)
    taxonomy_pars["description"] = \
        get_value(taxonomy, "description", type_=str)
    taxonomy_pars["url"] = get_value(taxonomy, "url", type_=str)
    taxonomy_pars["is_actionable"] = \
        get_value(taxonomy, "is_actionable", type_=float)

    # Flags
    flags = get_value(taxonomy, "flags", optional=True, default={})
    taxonomy_pars["allows_auto_tags"] = get_value(
        flags,
        "allows_auto_tags",
        optional=True,
        default=False,
        type_=bool
    )

    taxonomy_pars["allows_auto_values"] = get_value(
        flags,
        "allows_auto_values",
        optional=True,
        default=False,
        type_=bool
    )

    taxonomy_pars["for_numbers"] = get_value(
        flags,
        "for_numbers",
        optional=True,
        default=True,
        type_=bool
    )

    taxonomy_pars["for_domains"] = get_value(
        flags,
        "for_domains",
        optional=True,
        default=True,
        type_=bool
    )

    taxonomy_pars["is_automatically_classifiable"] = get_value(
        flags,
        "is_automatically_classifiable",
        optional=True,
        default=True,
        type_=bool
    )

    taxonomy_pars["is_stable"] = get_value(
        flags,
        "is_stable",
        optional=True,
        default=False,
        type_=bool
    )

    check_extra_keys(flags, "taxonomy.flags")

    if len(flags) > 0:
        raise InvalidSpec(
            "unknown key(s) in flags: %s" % ', '.join(flags.keys())
        )

    stmts = """
    DO $$
        DECLARE taxonomy_id integer;
        DECLARE last_tag_id integer;
    BEGIN""".replace("\n    ", "\n").split("\n")
    stmts.append(
        "INSERT INTO %(namespace)s.taxonomy (%(keys)s) VALUES(%(values)s) RETURNING id INTO taxonomy_id;" % (
            {
                "namespace": namespace,
                "keys": ','.join(taxonomy_pars.keys()),
                "values": ','.join(map(value_escape, taxonomy_pars.values()))
            }
        )
    )

    # tags
    tags = get_value(taxonomy, "tags", optional=True, default=[])

    check_extra_keys(taxonomy, "taxonomy")

    for i, _tag in enumerate(tags):
        stmts += gen_tag_stmts(_tag, args, "taxonomy.tags[%i]" % i)

    stmts.append("END $$")

    return stmts


def gen_tag_stmts(tag, args, path):
    namespace = args.namespace

    # Fetch the parameters
    tag_pars = OrderedDict()

    # Description
    tag_pars["tag_name"] = get_value(tag, "name", type_=str)
    tag_pars["tag_description"] = get_value(tag, "description", type_=str)
    tag_pars["extras"] = \
        get_value(tag, "extras", optional=True, default={}, type_=json.dumps)

    stmts = []
    stmts.append("-- tag %s" % tag_pars["tag_name"])
    stmts.append("INSERT INTO %(namespace)s.tags (%(keys)s) VALUES (%(values)s) RETURNING tag_id INTO last_tag_id;" % (
        {
            "namespace": namespace,
            "keys": ','.join(["taxonomy_id", ] + list(tag_pars.keys())),
            "values": ','.join(
                ["taxonomy_id", ] + list(map(value_escape, tag_pars.values()))
            )
        }
    ))

    values = get_value(tag, "values", default=[], optional=True)

    check_extra_keys(tag, "%s" % path)

    for i, _value in enumerate(values):
        stmts += gen_value_stmts(_value, args, "%s.values[%i]" % (path, i))

    return stmts


def gen_value_stmts(value, args, path):
    namespace = args.namespace

    if not isinstance(value, str):
        raise InvalidSpec(
            "invalid value in %s: expected string got %s" % (
                path,
                type(value).__name__
            )
        )

    # Fetch the parameters
    value_pars = OrderedDict()
    value_pars["value"] = value

    stmts = []
    stmts.append("INSERT INTO %(namespace)s.taxonomy_tag_val (%(keys)s) VALUES (%(values)s);" % (
        {
            "namespace": namespace,
            "keys": ','.join(["tag_id", ] + list(value_pars.keys())),
            "values": ','.join(
                ["last_tag_id", ] + list(map(value_escape, value_pars.values()))
            )
        }
    ))

    return stmts


def get_value(
    d, key,
    optional=False,
    default=None,
    parent=None,
    type_=None,
    consume=True
):
    try:
        value = d[key]
        if consume:
            del(d[key])
    except KeyError:
        if optional:
            value = default
        else:
            if parent:
                s = "could not find required key %s.%s" % (parent, key)
            else:
                s = "could not find required key %s" % key
            raise InvalidSpec(s)

    if type_ is not None:
        try:
            cast_value = type_(value)
            value = cast_value
        except ValueError as e:
            raise InvalidSpec(
                "could not convert value '%s' to type %s - %s" % (
                    value,
                    type(type_),
                    str(e)
                )
            )

    return value


def parse_taxonomy(specfile):
    try:
        data = yaml.safe_load(specfile)
    except Exception as e:
        sys.stderr.write("could not parse yaml: %s" % str(e))
        sys.exit(1)

    taxonomy = get_value(data, "taxonomy")

    return taxonomy


def run(args):

    taxonomy = parse_taxonomy(args.specfile)

    stmts = gen_taxonomy_stmts(taxonomy, args)

    for _stmt in stmts:
        print(_stmt)


if __name__ == '__main__':
    parser = ArgumentParser(
        description="Create the PostgreSQL statements that create a "
                    "tag2domain taxonomy"
    )

    parser.add_argument(
        "specfile",
        help="path of specification file",
        type=open
    )

    parser.add_argument(
        "-n",
        "--namespace",
        help="namespace the tag2domain tables live in",
        type=str,
        default="tag2domain"
    )

    args = parser.parse_args()

    try:
        run(args)
    except InvalidSpec as e:
        error("error in spec file - %s" % str(e))
    except Exception as e:
        traceback.print_exc()
        error("fatal error: %s" % str(e))
