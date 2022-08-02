#!/usr/bin/env python3
#
# Copyright (C) 2020 Red Hat, Inc.
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import glob
import os
import shutil
import subprocess
import tempfile


def signcode(path):
    if cmd := os.environ.get("SIGNCODE"):
        subprocess.run([cmd, path])
    else:
        return


def main():
    parser = argparse.ArgumentParser(description="QEMU NSIS build helper.")
    parser.add_argument("outfile")
    parser.add_argument("prefix")
    parser.add_argument("srcdir")
    parser.add_argument("cpu")
    parser.add_argument("nsisargs", nargs="*")
    args = parser.parse_args()

    destdir = tempfile.mkdtemp()
    try:
        subprocess.run(["make", "install", f"DESTDIR={destdir}{os.path.sep}"])
        with open(
            os.path.join(destdir + args.prefix, "system-emulations.nsh"), "w"
        ) as nsh:
            for exe in glob.glob(
                os.path.join(destdir + args.prefix, "qemu-system-*.exe")
            ):
                exe = os.path.basename(exe)
                arch = exe[12:-4]
                nsh.write(
                    """
                Section "{0}" Section_{0}
                SetOutPath "$INSTDIR"
                File "${{BINDIR}}\\{1}"
                SectionEnd
                """.format(
                        arch, exe
                    )
                )

        for exe in glob.glob(os.path.join(destdir + args.prefix, "*.exe")):
            signcode(exe)

        makensis = [
            "makensis",
            "-V2",
            "-NOCD",
            f"-DSRCDIR={args.srcdir}",
            f"-DBINDIR={destdir}{args.prefix}",
        ]

        dlldir = "w32"
        if args.cpu == "x86_64":
            dlldir = "w64"
            makensis += ["-DW64"]
        if os.path.exists(os.path.join(args.srcdir, "dll")):
            makensis += ["-DDLLDIR={0}/dll/{1}".format(args.srcdir, dlldir)]

        makensis += [f"-DOUTFILE={args.outfile}"] + args.nsisargs
        subprocess.run(makensis)
        signcode(args.outfile)
    finally:
        shutil.rmtree(destdir)


if __name__ == "__main__":
    main()
