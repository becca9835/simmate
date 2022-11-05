from simmate.calculators.vasp.inputs.potcar_mappings import PBE_ELEMENT_MAPPINGS
from simmate.calculators.vasp.workflows.base import VaspWorkflow


class Relaxation__Vasp__ClusterHighQ(VaspWorkflow):

    functional = "PBE"
    potcar_mappings = PBE_ELEMENT_MAPPINGS

    incar = dict(
        IBRION=2,
        KSPACING=0.4,
        EDIFFG=-0.02,
        IVDW=11,
        PREC="Accurate",
        ISMEAR=-5,
        ALGO="Fast",
        EDIFF=1e-06,
        ENCUT=500,
        NELM=100,
        NSW=99,
        SIGMA=0.05,
        LASPH=True,
        LORBIT=11,
        multiple_keywords__smart_ldau=dict(
            LDAU__auto=True,
            LDAUTYPE=2,
            LDAUPRINT=2,
            LDAUJ={"C": {"Sc": 0}},
            LDAUL={"C": {"Sc": 2}},
            LDAUU={"C": {"Sc": 3.0}},
        ),
    )
