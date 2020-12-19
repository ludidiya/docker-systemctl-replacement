#! /usr/bin/python3
import re
import logging

DONE = (logging.ERROR + logging.WARNING) // 2

logg = logging.getLogger("FORMAT")
logging.addLevelName(DONE, "DONE")

WRITEBACK=False
COMPAT=False
DBG=False
NEWS=False

def run(filename):
    changes = 0
    lines = []
    srctext = open(filename).read()
    for line0 in srctext.splitlines():
        line = line0
        if re.match("^\\s*#", line):
            lines.append(line)
            continue
        m = re.match(r'^(\s*)(\w+[.]\w+[(])(["][^"]*["]),\s*(\w+)\s*([)].*)$', line)
        if m:
            prefix, loggfu, fmt, a, suffix = m.groups()
            if loggfu in ("logg.debug(", "logg.info(", "logg.warning(", "logg.error("):
                if (not a.startswith("_") and a[0].lower() == a[0]):
                    fmt2 = fmt.replace("%s", "{"+a+"}", 1)
                    if fmt != fmt2 and "%" not in fmt2:
                        line = prefix+loggfu+fmt2+".format(**locals())"+suffix
        m = re.match(r'^(\s*)(\w+[.]\w+[(])(["][^"]*["]),\s*(\w+)\s*,\s*(\w+)\s*([)].*)$', line)
        if m:
            prefix, loggfu, fmt, a, b, suffix = m.groups()
            if loggfu in ("logg.debug(", "logg.info(", "logg.warning(", "logg.error("):
                if (not a.startswith("_") and a[0].lower() == a[0] and
                    not b.startswith("_") and b[0].lower() == b[0]):
                    fmt2 = fmt.replace("%s", "{"+a+"}", 1)
                    fmt3 = fmt2.replace("%s", "{"+b+"}", 1)
                    if fmt != fmt3 and "%" not in fmt3:
                        line = prefix+loggfu+fmt3+".format(**locals())"+suffix
        m = re.match(r'^(\s*)(\w+[.]\w+[(])(["][^"]*["]),\s*(\w+)\s*,\s*(\w+),\s*(\w+)\s*([)].*)$', line)
        if m:
            prefix, loggfu, fmt, a, b, c, suffix = m.groups()
            if loggfu in ("logg.debug(", "logg.info(", "logg.warning(", "logg.error("):
                if (not a.startswith("_") and a[0].lower() == a[0] and
                    not b.startswith("_") and b[0].lower() == b[0] and
                    not c.startswith("_") and c[0].lower() == c[0]):
                    fmt2 = fmt.replace("%s", "{"+a+"}", 1)
                    fmt3 = fmt2.replace("%s", "{"+b+"}", 1)
                    fmt4 = fmt3.replace("%s", "{"+c+"}", 1)
                    if fmt != fmt4 and "%" not in fmt4:
                        line = prefix+loggfu+fmt4+".format(**locals())"+suffix
        m = re.match(r'^(\s*)(\w+[.]\w+[(])(["][^"]*["]),\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+),\s*(\w+)\s*([)].*)$', line)
        if m:
            prefix, loggfu, fmt, a, b, c, d, suffix = m.groups()
            if loggfu in ("logg.debug(", "logg.info(", "logg.warning(", "logg.error("):
                if (not a.startswith("_") and a[0].lower() == a[0] and
                    not b.startswith("_") and b[0].lower() == b[0] and
                    not c.startswith("_") and c[0].lower() == c[0] and
                    not c.startswith("_") and d[0].lower() == d[0]):
                    fmt2 = fmt.replace("%s", "{"+a+"}", 1)
                    fmt3 = fmt2.replace("%s", "{"+b+"}", 1)
                    fmt4 = fmt3.replace("%s", "{"+c+"}", 1)
                    fmt5 = fmt4.replace("%s", "{"+d+"}", 1)
                    if fmt != fmt5 and "%" not in fmt5:
                        line = prefix+loggfu+fmt5+".format(**locals())"+suffix
        m = re.match('(^[^"]*)(["][^"]*["])([^"]*)$', line)
        if m:
            prefix, string, suffix = m.groups()
            flocals = ".format(**locals())"
            if suffix.startswith(flocals) and not COMPAT:
                if not prefix.strip().endswith("+"):
                    line = prefix+"f"+string+suffix[len(flocals):]
        m = re.match(r'^(\s*)(\w+[.]\w+)([(]["][^"]*["])(.*)([)].*)$', line)
        if m:
            prefix, command, string, formats, suffix = m.groups()
            if command in ["logg.debug"] and formats.strip() in [".format(**locals())", ""]:
                line = prefix+"dbg_"+string+formats+suffix
            if command in ["logg.info"] and formats.strip() in [".format(**locals())", ""]:
                line = prefix+"info_"+string+formats+suffix
            if command in ["logg.warning"] and formats.strip() in [".format(**locals())", ""]:
                line = prefix+"warn_"+string+formats+suffix
            if command in ["logg.error"] and formats.strip() in [".format(**locals())", ""]:
                line = prefix+"error_"+string+formats+suffix
        m = re.match(r'^(.*:\s*)(\w+[.]\w+)([(]["][^"]*["])(.*)([)].*)$', line)
        if m:
            prefix, command, string, formats, suffix = m.groups()
            if command in ["logg.debug"] and formats.strip() in [".format(**locals())", ""]:
                line = prefix+"dbg_"+string+formats+suffix
            if command in ["logg.info"] and formats.strip() in [".format(**locals())", ""]:
                line = prefix+"info_"+string+formats+suffix
            if command in ["logg.warning"] and formats.strip() in [".format(**locals())", ""]:
                line = prefix+"warn_"+string+formats+suffix
            if command in ["logg.error"] and formats.strip() in [".format(**locals())", ""]:
                line = prefix+"error_"+string+formats+suffix
        if line != line0:
            if not NEWS:
                logg.info(" -%s", line0)
            if True:
                logg.info(" +%s", line)
            changes += 1
        lines.append(line)
    logg.debug("found %s lines in %s", len(lines), filename)
    if changes:
        logg.log(DONE, "found %s changes for %s", changes, filename)
    if WRITEBACK:
       with open(filename, "w") as f:
          for line in lines:
              print(line, file=f)

if __name__ == "__main__":
    from argparse import ArgumentParser
    o = ArgumentParser()
    o.add_argument("-v", "--verbose", action="count", default=0,
                   help="increase logging level [%(default)s]")
    o.add_argument("-i", "--in-place", dest="writeback", action="store_true", default=WRITEBACK,
                   help="write the changes back to the file [%(default)s]")
    o.add_argument("-2", "--compat", action="store_true", default=COMPAT,
                   help="update only with python2 compatible parts [%(default)s]")
    o.add_argument("-d", "--dbg", action="store_true", default=DBG,
                   help="implant dbg_ wrapper calls [%(default)s]")
    o.add_argument("-n", "--news", action="store_true", default=NEWS,
                   help="show only the new lines in diff [%(default)s]")
    o.add_argument("filename", 
                   help="the file to show the changes")
    opt = o.parse_args()
    logging.basicConfig(level = max(0, DONE - 10 * opt.verbose))
    WRITEBACK = opt.writeback
    COMPAT = opt.compat
    DBG = opt.dbg
    NEWS = opt.news
    run(opt.filename)
    
    
       