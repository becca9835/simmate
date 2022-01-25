# -*- coding: utf-8 -*-

"""

> :warning: This file is only for use by the Simmate team. Users should instead
access data via the load_remote_archive method.

This file is for pulling OQMD data into the Simmate database. 

There are many ways to pull from this database, but it looks like the easiest
is the qmpy_rester python package. This officially supported and maintained
at https://github.com/mohanliu/qmpy_rester. For now the package is only available
via a pip install.

For other options such as the REST API, check out http://oqmd.org/static/docs/restful.html

"""

from django.db import transaction

from tqdm import tqdm
from simmate.toolkit import Structure

from simmate.database.third_parties import OqmdStructure

# Jarvis is not a dependency of simmate, so make sure you install it before using
# this module
try:
    import qmpy_rester
except:
    raise ModuleNotFoundError(
        "You must install qmpy-rester with `pip install qmpy_rester`"
    )


@transaction.atomic
def load_all_structures():
    """
    Only use this function if you are part of the Simmate dev team!

    Loads all structures directly for the OQMD database into the local
    Simmate database.
    """

    # The documentation indicates that we handle a query via a context manager
    # for qmpy_rester. Each query is returned as a page of data, where we need
    # to iterate through all of the pages. To do this, we constantly make a query
    # and check the "next" field, which tells us if its the last page or not.

    # as we download all the data, we store it in a main list
    data = []

    # starting from the first page, assume we aren't on the last page until told
    # otherwise. And loop until we know its the last page.
    current_page = 0
    is_last_page = False
    results_per_page = 100  # based on OQMD recommendations
    while not is_last_page:

        with qmpy_rester.QMPYRester() as query:

            # make the query
            result = query.get_oqmd_phases(
                verbose=False,
                limit=results_per_page,
                offset=current_page * results_per_page,
                #
                # Note delta_e is the formation energy and then stability is the
                # energy above hull.
                fields="entry_id,unit_cell,sites,delta_e",
                element_set="Al,C",  # Useful for testing
            )
            # grab the data for the next slice of structures
            query_slice = result["data"]
            # And check to see if this is the last page. The logic here is if
            # there is data for "next", then it isn't the last page
            is_last_page = not bool(result["links"]["next"])

            # store the slice of entrys in our main list
            for entry in query_slice:
                data.append(entry)

            # on the very first page, let's also check the total number of pages
            if current_page == 0:
                total_pages = result["meta"]["data_available"] // results_per_page

            # move on to the next page
            print(f"Successfully downloaded page {current_page} of {total_pages}")
            current_page += 1

    # Now iterate through all the data -- which is a list of dictionaries.
    # We convert the data into a pymatgen object and sanitize it before saving
    # to the Simmate database
    for entry in tqdm(data):

        # Parse the data into a pymatgen object
        # Also before converting into a pymatgen object, we need to parse the sites,
        # which are given as a list of "Element @ X Y Z" (ex: "Na @ 0.5 0.5 0.5")
        # Changing this format is why we have this complex lists below
        structure = Structure(
            lattice=entry["unit_cell"],
            species=[site.split(" @ ")[0] for site in entry["sites"]],
            coords=[
                [float(n) for n in site.split(" @ ")[1].split()]
                for site in entry["sites"]
            ],
            coords_are_cartesian=False,
        )

        # now convert the entry to a database object
        structure_db = OqmdStructure.from_toolkit(
            id="oqmd-" + str(entry["entry_id"]),
            structure=structure,
            energy=entry["delta_e"],
        )

        # and save it to our database!
        structure_db.save()
