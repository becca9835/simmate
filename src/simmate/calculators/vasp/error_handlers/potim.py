# -*- coding: utf-8 -*-

import os

from pymatgen.core.structure import Structure

from simmate.workflow_engine.tasks.error_handler import ErrorHandler
from simmate.calculators.vasp.inputs.incar import Incar
from simmate.calculators.vasp.outputs.oszicar import Oszicar


class PotimErrorHandler(ErrorHandler):
    """
    This hanlder checks if a run has excessively large positive energy changes,
    where it's typically caused by too large of a POTIM. Runs will end up crashing
    with some other error (e.g. BRMIX) as the geometry gets progressively worse.
    """

    # run this while the VASP calculation is still going
    is_monitor = True

    def __init__(self, dE_per_atom_threshold=1):
        self.dE_per_atom_threshold = dE_per_atom_threshold

    def check(self, directory):

        # We check for this error in the OSZICAR because it's the smallest file
        # that will tell us energies -- and therefore the fastest to read.
        oszicar_filename = os.path.join(directory, "OSZICAR")

        # check to see that the file is there first
        if os.path.exists(oszicar_filename):

            # then load the file's data
            oszicar = Oszicar(oszicar_filename)

            # also load the structure so we know how many sites there are
            poscar_filename = os.path.join(directory, "POSCAR")
            structure = Structure.from_file(poscar_filename)
            nsites = structure.num_sites

            # iterate through all of the ionic steps and look at the changes
            # in energy. If any is greater than our threshold, then we have
            # an error!
            for ionic_step in oszicar.ionic_steps:
                energy_change_per_atom = ionic_step["energy_change"] / nsites
                if energy_change_per_atom > self.dE_per_atom_threshold:
                    return True

        # if the file doesn't exist OR the threshold is never hit, the we are
        # not seeing any error.
        return False

    def correct(self, directory):

        # load the INCAR file to view the current settings
        incar_filename = os.path.join(directory, "INCAR")
        incar = Incar.from_file(incar_filename)

        current_potim = incar.get("POTIM", 0.5)
        current_ibrion = incar.get("IBRION", 0)

        # if we have a small potim and an ibrion that isn't damped molecular
        # dynamics, then then we switch the damped MD
        if current_potim < 0.2 and current_ibrion != 3:
            incar["IBRION"] = 3
            incar["SMASS"] = 0.75
            correction = "switched IBRION to 3 and SMASS to 0.75"

        # If we already have a small POTIM, then we try setting a low SYMPREC
        elif current_potim < 0.1:
            incar["SYMPREC"] = 1e-8
            correction = "switched SYMPREC to 1e-8"

        # Otherwise we trying halving the potim
        else:
            new_potim = current_potim * 0.5
            incar["POTIM"] = new_potim
            correction = f"halved the POTIM from {current_potim} to {new_potim}"

        # rewrite the INCAR with new settings
        incar.to_file(incar_filename)

        return correction
