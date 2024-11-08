from mmLib import FileIO
from mmLib.CIFBuilder import CIFStructureBuilder

if __name__ == "__main__":
    def builder_test(test_file):
        structure_cif = FileIO.LoadStructure(file=test_file, format='CIF')
        print(structure_cif.unit_cell.space_group.short_name)
        print(structure_cif.unit_cell.space_group.number)
        #csb = CIFStructureBuilder(fil=test_file)
        #s = csb.struct
        #print(s)
    builder_test("data/1eas.cif")
