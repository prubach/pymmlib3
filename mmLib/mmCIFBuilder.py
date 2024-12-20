## Copyright 2002-2010 by PyMMLib Development Group (see AUTHORS file)
## This code is part of the PyMMLib distribution and governed by
## its license.  Please see the LICENSE file that should have been
## included as part of this package.
"""Convert a Structure object into its mmCIFFile description.
"""
## Python
import copy

## pymmlib
from . import ConsoleOutput
from . import mmCIF
from . import StructureBuilder
from . import Structure


def setmaps_cif(smap, skey, dmap, dkey):
    """For string converisons, treat [?.] as blank.
    """
    if smap.has_key(skey):
        x = smap.getitem_lower(skey)
        if x in ('', '?', '.'):
            return False
        dmap[dkey] = str(x)
        return True
    return False


def setmapi_cif(smap, skey, dmap, dkey):
    """For integer converisons, treat [?.] as blank.
    """
    if smap.has_key_lower(skey):
        x = smap.getitem_lower(skey)
        if x in ('', '?', '.'):
            return False
        try:
            dmap[dkey] = int(x)
        except ValueError:
            return False
        return True
    return False


def setmapf_cif(smap, skey, dmap, dkey):
    """For float converisons, treat [?.] as blank.
    """
    if smap.has_key_lower(skey):
        x = smap.getitem_lower(skey)
        if x in ('', '?', '.'):
            return False
        try:
            dmap[dkey] = float(x)
        except ValueError:
            return False
        return True
    return False


class mmCIFStructureBuilder(StructureBuilder.StructureBuilder):
    """Builds a new Structure object by loading an mmCIF file.
    """

    def read_start(self, filobj):
        ## parse the mmCIF file
        self.cif_file = mmCIF.mmCIFFile()
        self.cif_file.load_file(filobj)

        ## for an mmCIF file for a structure, assume the first data item
        ## contains the structure; if there is no data in the mmCIF
        ## file, halt
        try:
            self.cif_data = self.cif_file[0]
        except IndexError:
            self.halt = True
            return

        self.set_atom_site_data_columns()

        ## maintain a map of atom_site.id -> atm
        self.atom_site_id_map = {}

    def set_atom_site_auth(self):
        """Read atom_site.auth_ labels for atom definitions.
        """
        self.atom_id       = "auth_atom_id"
        self.alt_id        = "auth_alt_id"
        self.comp_id       = "auth_comp_id"
        self.seq_id        = "auth_seq_id"
        self.asym_id       = "auth_asym_id"
        self.ptnr1_atom_id = "ptnr1_auth_atom_id"
        self.ptnr1_comp_id = "ptnr1_auth_comp_id"
        self.ptnr1_asym_id = "ptnr1_auth_asym_id"
        self.ptnr1_seq_id  = "ptnr1_auth_seq_id"
        self.ptnr2_atom_id = "ptnr2_auth_atom_id"
        self.ptnr2_comp_id = "ptnr2_auth_comp_id"
        self.ptnr2_asym_id = "ptnr2_auth_asym_id"
        self.ptnr2_seq_id  = "ptnr2_auth_seq_id"
        
    def set_atom_site_label(self):
        """Read atom_site.label_ items for atom definitions.
        """
        self.atom_id       = "label_atom_id"
        self.alt_id        = "label_alt_id"
        self.comp_id       = "label_comp_id"
        self.seq_id        = "label_seq_id"
        self.asym_id       = "label_asym_id"
        self.ptnr1_atom_id = "ptnr1_label_atom_id"
        self.ptnr1_comp_id = "ptnr1_label_comp_id"
        self.ptnr1_asym_id = "ptnr1_label_asym_id"
        self.ptnr1_seq_id  = "ptnr1_label_seq_id"
        self.ptnr2_atom_id = "ptnr2_label_atom_id"
        self.ptnr2_comp_id = "ptnr2_label_comp_id"
        self.ptnr2_asym_id = "ptnr2_label_asym_id"
        self.ptnr2_seq_id  = "ptnr2_label_seq_id"

    def set_atom_site_data_columns(self):
        """Choose to use atom_site.auth_ labels, or atom_site.label_
        """
        try:
            atom_site_table = self.cif_data["atom_site"]
        except KeyError:
            return

        ## count the number of columns which exist for the auth_ style
        ## columns and label_ style columns
        auth_cols  = ["auth_atom_id", "auth_comp_id", "auth_seq_id", "auth_asym_id"]
        label_cols = ["label_atom_id", "label_comp_id", "label_seq_id", "label_asym_id"]
        
        auth_count = 0
        for col in auth_cols:
            if col in atom_site_table.columns:
                auth_count += 1
        
        label_count = 0
        for col in label_cols:
            if col in atom_site_table.columns:
                label_count += 1
        
        if auth_count >= label_count:
            self.set_atom_site_auth()
        else:
            self.set_atom_site_label()

    def read_atoms(self):
        try:
            atom_site_table = self.cif_data["atom_site"]
        except KeyError:
            ConsoleOutput.warning("read_atoms: atom_site table not found")
            return

        try:
            aniso_table = self.cif_data["atom_site_anisotrop"]
        except KeyError:
            aniso_table = None
        else:
            aniso_dict  = aniso_table.row_index_dict("id")
        
        for atom_site in atom_site_table:
            try:
                atom_site_id = atom_site["id"]
            except KeyError:
                ConsoleOutput.warning("unable to find id for atom_site row")
                continue

            atm_map = {}

            setmaps_cif(atom_site, self.atom_id, atm_map, "name")
            setmaps_cif(atom_site, self.alt_id,  atm_map, "alt_loc")
            setmaps_cif(atom_site, self.comp_id, atm_map, "res_name")
            setmaps_cif(atom_site, self.seq_id,  atm_map, "fragment_id")
            setmaps_cif(atom_site, self.asym_id, atm_map, "chain_id")

            setmaps_cif(atom_site, "label_entity_id", atm_map, "label_entity_id")
            setmaps_cif(atom_site, "label_asym_id", atm_map, "label_asym_id")
            setmaps_cif(atom_site, "label_seq_id", atm_map, "label_seq_id")
            setmaps_cif(atom_site, "type_symbol", atm_map, "element")
            setmapf_cif(atom_site, "cartn_x", atm_map, "x")
            setmapf_cif(atom_site, "cartn_y", atm_map, "y")
            setmapf_cif(atom_site, "cartn_z", atm_map, "z")
            setmapf_cif(atom_site, "occupancy", atm_map, "occupancy")
            setmapf_cif(atom_site, "b_iso_or_equiv", atm_map, "temp_factor")
            setmapf_cif(atom_site, "cartn_x_esd", atm_map, "sig_x")
            setmapf_cif(atom_site, "cartn_y_esd", atm_map, "sig_y")
            setmapf_cif(atom_site, "cartn_z_esd", atm_map, "sig_z")
            setmapf_cif(atom_site, "occupancy_esd", atm_map, "sig_occupancy")

            setmapf_cif(atom_site, "b_iso_or_equiv_esd",
                        atm_map,   "sig_temp_factor")

            setmapi_cif(atom_site, "pdbx_pdb_model_num",
                        atm_map,   "model_id")

            if aniso_table is not None:
                if atom_site_id in aniso_dict.keys():
                    aniso = aniso_dict[atom_site_id]
                    setmapf_cif(aniso, "u[1][1]", atm_map, "u11")
                    setmapf_cif(aniso, "u[2][2]", atm_map, "u22")
                    setmapf_cif(aniso, "u[3][3]", atm_map, "u33")
                    setmapf_cif(aniso, "u[1][2]", atm_map, "u12")
                    setmapf_cif(aniso, "u[1][3]", atm_map, "u13")
                    setmapf_cif(aniso, "u[2][3]", atm_map, "u23")

                    setmapf_cif(aniso, "u[1][1]_esd", atm_map, "sig_u12")
                    setmapf_cif(aniso, "u[2][2]_esd", atm_map, "sig_u22")
                    setmapf_cif(aniso, "u[3][3]_esd", atm_map, "sig_u33")
                    setmapf_cif(aniso, "u[1][2]_esd", atm_map, "sig_u12")
                    setmapf_cif(aniso, "u[1][3]_esd", atm_map, "sig_u13")
                    setmapf_cif(aniso, "u[2][3]_esd", atm_map, "sig_u23")
                else:
                    ConsoleOutput.warning("unable to find aniso row for atom")

            atm = self.load_atom(atm_map)
            self.atom_site_id_map[atom_site_id] = atm

    def read_metadata(self):
        self.read_structure_id()
        
        ## copy selected mmCIF tables to the structure's mmCIF database
        skip_tables = ["atom_site",
                       "atom_site_anisotrop",
                       "atom_sites_alt"]
        
        for table in self.cif_data:
            #print("DEBUG: %s" % table)
            if table.name not in skip_tables:
                self.struct.cifdb.add_table(table)

        self.read_sequence()

        ## read unit cell table
        self.read_unit_cell()

        ## read bond information
        self.read_struct_conn()

    def read_sequence(self):
        """Read the sequence. 
        """

    def read_structure_id(self):
        """Read the PDB ID.
        """
        entry_id = None
        try:
            entry_id = self.cif_data["entry"]["id"]
        except KeyError:
            pass
        if entry_id:
            self.load_structure_id(entry_id)

    def read_unit_cell(self):
        """Load unit cell and symmetry tables.
        """
        ucell_map = {}
        
        try:
            entry_id = self.cif_data["entry"]["id"]
            cell_table = self.cif_data["cell"]
            symmetry_table = self.cif_data["symmetry"]
        except KeyError:
            return

        if not entry_id or not cell_table or not symmetry_table:
            return

        cell = cell_table.get_row1("entry_id", entry_id)
        if cell is not None:
            setmapf_cif(cell, "length_a", ucell_map, "a")
            setmapf_cif(cell, "length_b", ucell_map, "b")
            setmapf_cif(cell, "length_c", ucell_map, "c")
            setmapf_cif(cell, "angle_alpha", ucell_map, "alpha")
            setmapf_cif(cell, "angle_beta", ucell_map, "beta")
            setmapf_cif(cell, "angle_gamma", ucell_map, "gamma")
            setmapi_cif(cell, "z_pdb", ucell_map, "z")
            
        symm = symmetry_table.get_row1("entry_id", entry_id)
        if symm is not None:
            setmaps_cif(symm, "space_group_name_H-M", ucell_map, "space_group")
        
        self.load_unit_cell(ucell_map)

    def read_struct_conn(self):
        """Read bond information form the struct_conn and struct_conn_type
        sections.
        """
        ## only read these types of bonds for now
        bond_type_list = [
            "covale",           # covalent bond
            "metalc",           # metal coordination
            "disulf",           # disulfide bridge
            "saltbr",           # ionic interaction
            "covale_base",      # covalent modification of a nucleotide base
            "covale_sugar",     # covalent modification of a nucleotide sugar
            "covale_phosphate", # covalent modification of a nucleotide phosphate
            ]

        try:
            atom_site = self.cif_data["atom_site"]
        except KeyError:
            ConsoleOutput.warning("read_struct_conn: atom_site table not found")
            return

        try:
            struct_conn_table = self.cif_data["struct_conn"]
        except KeyError:
            ConsoleOutput.warning("read_struct_conn: struct_conn table not found")
            return

        bond_map = {}

        for row in struct_conn_table:
            conn_type = row.get("conn_type_id")
            if conn_type not in bond_type_list:
                continue
            
            # Always use label_ values since they are mandatory
            asym_id1 = row.get("ptnr1_label_asym_id")
            seq_id1  = row.get("ptnr1_label_seq_id")
            comp_id1 = row.get("ptnr1_label_comp_id")
            atom_id1 = row.get("ptnr1_label_atom_id")
            auth_asym_id1 = row.get("ptnr1_auth_asym_id")
            auth_seq_id1  = row.get("ptnr1_auth_seq_id")
            auth_comp_id1 = row.get("ptnr1_auth_comp_id")
            symm1    = row.get("ptnr1_symmetry")

            asym_id2 = row.get("ptnr2_label_asym_id")
            seq_id2  = row.get("ptnr2_label_seq_id")
            comp_id2 = row.get("ptnr2_label_comp_id")
            atom_id2 = row.get("ptnr2_label_atom_id")
            auth_asym_id2 = row.get("ptnr2_auth_asym_id")
            auth_seq_id2  = row.get("ptnr2_auth_seq_id")
            auth_comp_id2 = row.get("ptnr2_auth_comp_id")
            symm2    = row.get("ptnr2_symmetry")

            ## check for these special mmCIF tokens
            if conn_type == "disulf":
                atom_id1 = atom_id2 = "SG"

            as1 = atom_site.get_row(
                ("label_asym_id", asym_id1),
                ("label_seq_id",  seq_id1),
                ("label_comp_id", comp_id1),
                ("auth_asym_id", auth_asym_id1),
                ("auth_seq_id",  auth_seq_id1),
                ("auth_comp_id", auth_comp_id1),
                ("label_atom_id", atom_id1))

            as2 = atom_site.get_row(
                ("label_asym_id", asym_id2),
                ("label_seq_id",  seq_id2),
                ("label_comp_id", comp_id2),
                ("auth_asym_id", auth_asym_id2),
                ("auth_seq_id",  auth_seq_id2),
                ("auth_comp_id", auth_comp_id2),
                ("label_atom_id", atom_id2))

            if not as1 or not as2:
                ConsoleOutput.warning("read_struct_conn: atom not found id: " + \
                        row.get("id","[No ID]"))
                
                ConsoleOutput.warning("atm1: asym=%s seq=%s comp=%s atom=%s symm=%s" % (
                    asym_id1, seq_id1, comp_id1, atom_id1, symm1))
                
                ConsoleOutput.warning("atm2: asym=%s seq=%s comp=%s atom=%s symm=%s" % (
                    asym_id2, seq_id2, comp_id2, atom_id2, symm2))

                continue

            try:
                atm1 = self.atom_site_id_map[as1["id"]]
                atm2 = self.atom_site_id_map[as2["id"]]
            except KeyError:
                ConsoleOutput.warning("read_struct_conn: atom_site_id_map incorrect id: " + \
                        row.get("id", "[No ID]"))

                ConsoleOutput.warning("atm1: asym=%s seq=%s comp=%s atom=%s symm=%s" % (
                    asym_id1, seq_id1, comp_id1, atom_id1, symm1))
                
                ConsoleOutput.warning("atm2: asym=%s seq=%s comp=%s atom=%s symm=%s" % (
                    asym_id2, seq_id2, comp_id2, atom_id2, symm2))

                continue

            if id(atm1) < id(atm2):
                bnd = (atm1, atm2)
            else:
                bnd = (atm2, atm1)

            try:
                bond_map[bnd]["bond_type"] = conn_type
            except KeyError:
                bond_map[bnd] = {"bond_type": conn_type}

            if symm1:
                bond_map[bnd]["symop1"] = symm1
            if symm2:
                bond_map[bnd]["symop2"] = symm2

        ## load the bonds
        self.load_bonds(bond_map)

    def read_struct_conf(self):
        """Reads the struct_conf table getting information on alpha
        helicies and turns in the structure.
        """
        try:
            struct_conf = self.cif_data["struct_conf"]
        except KeyError:
            return

        ## iterate over struct_conf and create the helix_list
        helix_list = []
        
        for row in struct_conf:
            ## check for required fields
            try:
                row["id"]
                row["conf_type_id"]
            except KeyError:
                continue

            ## if this is a alpha helix
            if row["conf_type_id"].startswith("HELIX"):
                helix = {"helix_id":    row["id"],
                         "helix_class": row["conf_type_id"]}


CIF_BUILD_TABLES = {
    "entry": ["id"],

    "entity": [
        "id", "type", "ndb_description"],

    "cell": [
        "entry_id", "length_a", "length_b", "length_c",
        "angle_alpha", "angle_beta", "angle_gamma", "PDB_Z"],

    "symmetry": [
        "entry_id", "space_group_name_H-M", "cell_setting",
        "Int_Tables_number"],

    "entity_poly": [
        "entity_id", "ndb_chain_id", "ndb_seq_one_letter_code"],

    "audit_author": ["name"],

    "atom_site": [
        "group_PDB", "id", "type_symbol", "label_entity_id", "label_asym_id",
        "label_seq_id", "label_comp_id", "label_alt_id", "label_atom_id",
        "Cartn_x", "Cartn_y", "Cartn_z", "occupancy", "B_iso_or_equiv",
        "Cartn_x_esd", "Cartn_y_esd", "Cartn_z_esd", "occupancy_esd",
        "B_iso_or_equiv_esd", "auth_asym_id", "auth_seq_id", "auth_comp_id",
        "auth_alt_id", "auth_atom_id", "pdbx_PDB_model_num"],

    "atom_site_anisotrop": [
        "id", "type_symbol", "label_entity_id", "U[1][1]", "U[1][2]",
        "U[1][3]", "U[2][2]", "U[2][3]", "U[3][3]", "U[1][1]_esd",
        "U[1][2]_esd", "U[1][3]_esd", "U[2][2]_esd", "U[2][3]_esd",
        "U[3][3]_esd", "pdbx_auth_seq_id", "pdbx_auth_comp_id",
        "pdbx_auth_asym_id", "pdbx_auth_atom_id"]
    }



class mmCIFFileBuilder(object):
    """Builds a mmCIF file from a Structure object.
    """
    def __init__(self, struct, cif_file):
        self.struct   = struct
        self.entry_id = self.struct.structure_id        
        self.cif_data = cif_file.new_data(self.entry_id)

        ## entity handling
        ## entity_desc list
        self.entity_list          = []
        ## Fragment -> entity_desc
        self.entity_frag_dict     = {}
        ## res_name -> entity_desc
        self.entity_res_name_dict = {}

        ## these tables need to be formed from the atom structure
        self.add__entry()
        self.add__entity()
        self.add__entity_poly()
        self.add__cell()
        self.add__symmetry()
        self.add__atom_site()

    def get_table(self, name):
        """Returns the self.cif_data[name] mmCIFTable, or it creates
        it and adds it to self.cif_data if it does not exist.
        """
        table = self.cif_data.get_table(name)
        if table is not None:
            return table

        columns = copy.deepcopy(CIF_BUILD_TABLES[name])
        table  = self.cif_data.new_table(name, columns)
        return table

    def get_entity_desc_from_id(self, entity_id):
        for entity_desc in self.entity_list:
            if entity_desc["id"]==entity_id:
                return entity_desc
        return None

    def get_entity_desc_from_sequence(self, sequence):
        for entity_desc in self.entity_list:
            if "sequence" in entity_desc and entity_desc["sequence"] == sequence:
                return entity_desc
        return None

    def add__entry(self):
        """Add the _entry table.
        """
        entry = self.get_table("entry")
        row = entry.new_row()
        row["id"] = self.entry_id

    def add__entity(self):
        """Adds the entity table. The entity names are faked here, since
        it is really not clear to us how the names are chosen by the PDB.
        """
        ## maps fragment -> entity_id
        entity = self.get_table("entity")

        ## ADD BIO-POLYMERS
        ## list of polymer entities (entity_id, sequence1)

        cur_entity_id = 1

        for chain in self.struct.iter_all_chains():

            ## if the chain is a bio-polymer, it is one entity; come up
            ## with a name from its sequence and add it to the
            ## entity map
            if chain.count_standard_residues() < 3:
                continue
            
            ## calculate sequence and compare the sequence to chains
            ## already added so we can re-use the entity ID
            sequence = chain.sequence.one_letter_code()
            
            entity_desc = self.get_entity_desc_from_sequence(sequence)

            ## ADD POLYMER TO CURRENT ENTITY
            if entity_desc is not None:
                entity_desc["chains"].append(chain)
                entity_desc["chain_ids"].append(chain.chain_id)
                    
            ## NEW ENTITY
            else:
                ## figure out what type of biopolymer this is
                if (chain.count_amino_acids() / len(chain)) > 0.5:
                    details   = "%d residue polypeptide" % (chain.count_amino_acids())
                    poly_type = "polypeptide(L)"

                elif (chain.count_nucleic_acids() / len(chain)) > 0.5:
                    details   = "%d residue DNA/RNA" % (chain.count_nucleic_acids())
                    poly_type = "polydeoxyribonucleotide"
                    
                else:
                    details   = "unknown polymer"
                    poly_type = "other"

                ## new entity description
                entity_desc = {
                    "id":        cur_entity_id,
                    "chains":    [chain],
                    "chain_ids": [chain.chain_id],
                    "polymer":   True,
                    "poly_type": poly_type,
                    "sequence":  sequence,
                    "details":   details }
                self.entity_list.append(entity_desc)
                
                row  = entity.new_row()
                row["id"] = entity_desc["id"]
                row["type"] = "polymer"
                row["ndb_description"] = details

                ## incriment entity_id
                cur_entity_id = cur_entity_id + 1

            ## loop over all residues and map the frag->entity_desc
            for frag in chain.iter_standard_residues():
                self.entity_frag_dict[frag] = entity_desc


        ## ADD HET ATOMS (Water, metal)
        for chain in self.struct.iter_all_chains():
            for frag in chain.iter_fragments():

                ## any fragments already assigned to a entity by the
                ## polymer section above should be skipped
                if frag in self.entity_frag_dict:
                    continue

                ## already assigned a entity_id for this fragment_id
                if frag.res_name in self.entity_res_name_dict:
                    self.entity_frag_dict[frag] = self.entity_res_name_dict[frag.res_name]
                    continue
                    
                ## we need to assign a entity_id for this fragment_id
                ## and add a row for it in the entity table
                if frag.is_water():
                    type = "water"
                    details = ""
                else:
                    type = "non-polymer"
                    details = frag.res_name

                row = entity.new_row()
                row["id"]              = cur_entity_id
                row["type"]            = "non-polymer"
                row["ndb_description"] = frag.res_name

                entity_desc = {
                    "id":       cur_entity_id,
                    "polymer":  False,
                    "res_name": frag.res_name }
                
                self.entity_res_name_dict[frag.res_name] = entity_desc
                self.entity_frag_dict[frag] = entity_desc

                ## incriment entity_id
                cur_entity_id = cur_entity_id + 1

    def add__entity_poly(self):
        """Adds the _entity_poly table.
        """
        entity_poly = self.get_table("entity_poly")

        for entity_desc in self.entity_list:
            if entity_desc["polymer"]==False:
                continue

            row = entity_poly.new_row()
            
            row["entity_id"] = entity_desc["id"]
            row["ndb_chain_id"] = ",".join(entity_desc["chain_ids"])
            row["ndb_seq_one_letter_code"] = entity_desc["sequence"]
        
    def add__cell(self):
        """Adds the _cell table.
        """
        try:
            unit_cell = self.struct.unit_cell
        except AttributeError:
            return
        
        cell = self.get_table("cell")
        row = cell.new_row()

        row["entry_id"]    = self.entry_id
        row["length_a"]    = unit_cell.a
        row["length_b"]    = unit_cell.b
        row["length_c"]    = unit_cell.c
        row["angle_alpha"] = unit_cell.calc_alpha_deg()
        row["angle_beta"]  = unit_cell.calc_beta_deg()
        row["angle_gamma"] = unit_cell.calc_gamma_deg()

    def add__symmetry(self):
        """Adds the _symmetry table.
        """
        try: 
            space_group = self.struct.unit_cell.space_group
        except AttributeError:
            return

        symmetry = self.get_table("symmetry")
        row = symmetry.new_row()

        row["entry_id"]             = self.entry_id
        row["space_group_name_H-M"] = space_group.pdb_name
        row["Int_Tables_number"]    = space_group.number

    def add__atom_site(self):
        """Adds the _atom_site table.
        """
        atom_site = self.get_table("atom_site")
        atom_id = 0

        for chain in self.struct.iter_all_chains():
            label_seq_id = 0

            for frag in chain.iter_fragments():
                label_seq_id += 1
                entity_desc = self.entity_frag_dict[frag]

                for atm in frag.iter_all_atoms():
                    atom_id += 1

                    row = atom_site.new_row()
                    row["id"] = atom_id
                    
                    self.set_atom_site_row(row, atm, entity_desc, label_seq_id)

    def set_atom_site_row(self, asrow, atm, entity_desc, label_seq_id):
        """Add atom_site coordinate row.
        """
        if entity_desc["polymer"]==True:
            asrow["group_PDB"]     = "ATOM"
            asrow["label_asym_id"] = atm.chain_id

        else:
            asrow["group_PDB"] = "HETATM"

        asrow["label_entity_id"]    = entity_desc["id"]
        asrow["label_atom_id"]      = atm.name
        asrow["label_alt_id"]       = atm.alt_loc
        asrow["label_comp_id"]      = atm.res_name
        asrow["label_seq_id"]       = label_seq_id

        asrow["auth_atom_id"]       = atm.name
        asrow["auth_alt_id"]        = atm.alt_loc
        asrow["auth_comp_id"]       = atm.res_name
        asrow["auth_seq_id"]        = atm.fragment_id
        asrow["auth_asym_id"]       = atm.chain_id

        asrow["type_symbol"]        = atm.element
        asrow["pdbx_PDB_model_num"] = atm.model_id
        
        if atm.occupancy is not None:
            asrow["occupancy"] = atm.occupancy

        if atm.temp_factor is not None:
            asrow["B_iso_or_equiv"] = atm.temp_factor

        if atm.position is not None:
            if atm.position[0] is not None:
                asrow["Cartn_x"] = atm.position[0]
            if atm.position[1] is not None:
                asrow["Cartn_y"] = atm.position[1]
            if atm.position[2] is not None:
                asrow["Cartn_z"] = atm.position[2]
        
        if atm.sig_position is not None:
            if atm.sig_position[0] is not None:
                asrow["Cartn_x_esd"] = atm.sig_position[0]
            if atm.sig_position[1] is not None:
                asrow["Cartn_y_esd"] = atm.sig_position[1]
            if atm.sig_position[2] is not None:
                asrow["Cartn_z_esd"] = atm.sig_position[2]

        if atm.sig_occupancy is not None:
            asrow["occupancy_esd"] = atm.sig_occupancy

        if atm.sig_temp_factor is not None:
            asrow["B_iso_or_equiv_esd"] = atm.sig_temp_factor

        if atm.U is not None:
            aniso = self.get_table("atom_site_anisotrop")
            anrow = aniso.new_row()

            anrow["id"]                = asrow["id"]
            anrow["type_symbol"]       = asrow["type_symbol"]
            anrow["label_entity_id"]   = asrow["label_entity_id"]
            anrow["pdbx_auth_seq_id"]  = asrow["auth_seq_id"]
            anrow["pdbx_auth_comp_id"] = asrow["auth_comp_id"]
            anrow["pdbx_auth_asym_id"] = asrow["auth_asym_id"]
            anrow["pdbx_auth_atom_id"] = asrow["auth_atom_id"]
            anrow["pdbx_auth_alt_id"]  = asrow["auth_alt_id"]

            if atm.U[0,0] is not None:
                anrow["U[1][1]"] = atm.U[0,0]
            if atm.U[1,1] is not None:
                anrow["U[2][2]"] = atm.U[1,1]
            if atm.U[2,2] is not None:
                anrow["U[3][3]"] = atm.U[2,2]
            if atm.U[0,1] is not None:
                anrow["U[1][2]"] = atm.U[0,1]
            if atm.U[0,2] is not None:
                anrow["U[1][3]"] = atm.U[0,2]
            if atm.U[1,2] is not None:
                anrow["U[2][3]"] = atm.U[1,2]

            if atm.sig_U is not None:
                if atm.sig_U[0,0] is not None:
                    anrow["U[1][1]_esd"] = atm.sig_U[0,0]
                if atm.sig_U[1,1] is not None:
                    anrow["U[2][2]_esd"] = atm.sig_U[1,1]
                if atm.sig_U[2,2] is not None:
                    anrow["U[3][3]_esd"] = atm.sig_U[2,2]
                if atm.sig_U[0,1] is not None:
                    anrow["U[1][2]_esd"] = atm.sig_U[0,1]
                if atm.sig_U[0,2] is not None:
                    anrow["U[1][3]_esd"] = atm.sig_U[0,2]
                if atm.sig_U[1,2] is not None:
                    anrow["U[2][3]_esd"] = atm.sig_U[1,2]

