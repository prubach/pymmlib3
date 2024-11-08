import argparse
import os
import tempfile
import urllib.request, urllib.parse, urllib.error
import mmLib.mmCIF

def build_library(cif_file, zip=False):
    SITE_PACKAGES = os.path.dirname(os.path.dirname(__file__))
    LIB_FILE = os.path.join(SITE_PACKAGES, "mmLib", "Data", "Monomers.zip")
    LIB_PATH = os.path.join(SITE_PACKAGES, "mmLib", "Data", "Monomers")
    print('Will create mmLib Monomer library at: {}'.format(LIB_FILE if zip else LIB_PATH))
    TMP_PATH = cif_file
    if not cif_file or not os.path.exists(cif_file):
        TMP_FILE = tempfile.NamedTemporaryFile()
        TMP_PATH = TMP_FILE.name
        # "components.cif"
        URL = "https://ftp.ebi.ac.uk/pub/databases/pdb/data/monomers/components.cif"
        print("[BUILDLIB] downloading %s to temp file: %s" % (URL, TMP_PATH))

        fil = open(TMP_PATH, "wb")

        opener = urllib.request.FancyURLopener()
        con = opener.open(URL)
        for ln in con.readlines():
            fil.write(ln)
        con.close()
        fil.close()

    print("[BUILDLIB] constructing library from %s" % (TMP_PATH))

    if zip:
        import zipfile
        import io
        zf = zipfile.ZipFile(LIB_FILE, "w")

    cif_file = mmLib.mmCIF.mmCIFFile()
    cif_file.load_file(TMP_PATH)

    if not os.path.isdir(LIB_PATH):
        os.mkdir(LIB_PATH)

    while len(cif_file) > 0:
        cif_data = cif_file[0]
        cif_file.remove(cif_data)
        cf = mmLib.mmCIF.mmCIFFile()
        cf.append(cif_data)

        if zip:
            print("[BUILDLIB] writing %s" % (cif_data.name))
            sf = io.StringIO()
            cf.save_file(sf)
            zf.writestr(cif_data.name, sf.getvalue())
            sf.close()
        else:
            mkdir_path = os.path.join(LIB_PATH, cif_data.name[0])
            if not os.path.isdir(mkdir_path):
                os.mkdir(mkdir_path)
            save_path = os.path.join(mkdir_path, "%s.cif" % (cif_data.name))
            print("[BUILDLIB] writing %s" % (save_path))
            cf.save_file(save_path)

    if zip:
        zf.close()


def run():
    parser = argparse.ArgumentParser(prog="build_library", formatter_class=argparse.RawDescriptionHelpFormatter,
                                         description="build_library agent")
    parser.add_argument('--cif-file', nargs='?', default=None, help="Path to components.cif file. If not given it will be downloaded from PDBe")
    parser.add_argument('--zip', nargs='?', default=False, type=bool, help="Should the monomer library be zipped? Default: NO")
    args = vars(parser.parse_args())
    build_library(args['cif_file'], args['zip'])

