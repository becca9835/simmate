# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.db.models import F
from django.contrib.auth.decorators import login_required

from simmate.website.third_parties.forms import ChemicalSystemForm

from simmate.database.third_parties.all import (
    MaterialsProjectStructure,
    CodStructure,
    JarvisStructure,
    AflowStructure,
    OqmdStructure,
)


@login_required
def home(request):

    # The home page is also an html "form" because users submit queries from
    # here. So we need to handle form submissions properly.

    # first check if the webpage is accessed via a POST method
    if request.method == "POST":
        # if it is, that means a user is trying to submit a query
        # let's grab the data and validate it before running the query
        form = ChemicalSystemForm(request.POST)
        # see if all of the data is valid
        if form.is_valid():

            # grab the cleaned data from the form
            cleaned_data = form.cleaned_data

            # check which databases the user wants to search and collect the
            # proper models into a list that we query with below
            databases_to_search = []
            for database, database_model in (
                ("aflow", AflowStructure),
                ("cod", CodStructure),
                ("jarvis", JarvisStructure),
                ("materials_project", MaterialsProjectStructure),
                ("oqmd", OqmdStructure),
            ):
                # if the user requested this database, the value will be true
                if cleaned_data[database]:
                    databases_to_search.append(database_model)
            # Note, this value is converted to a list of systems once cleaned.
            chemical_systems = cleaned_data["chemical_system"]

            # now go through each database, search for the requested system
            # and then pool them all together. We limit each database to 50
            # results. Note the += below means we compile into a single list
            structures = []
            nstructures_possible = 0
            for database_model in databases_to_search:
                # Now we can make the query! We also dont want to load the
                # structure json -- so that everything runs faster.
                search_results = database_model.objects.filter(
                    chemical_system__in=chemical_systems
                ).defer("structure_string")

                # if the database provides the hull energy, we want to sort
                # the structures by that (putting highest priority on stable ones)
                if hasattr(database_model, "energy_above_hull"):
                    # if there isn't a hull energy value, place these last
                    search_results = search_results.order_by(
                        F("energy_above_hull").asc(nulls_last=True)
                    )
                # now add the search results to the output
                # for performance, we limit each database to 50 structures
                structures += search_results.all()[:50]

                # We also tell the user how many results are possible if there
                # wasn't any limit on the structures returned
                nstructures_possible += database_model.objects.filter(
                    chemical_system__in=chemical_systems,
                ).count()
    # if the page is grabbed via a 'GET' method, send an empty form
    else:
        # otherwise we are giving an empty form and no result structures
        form = ChemicalSystemForm()
        structures = None
        nstructures_possible = None
    # now let's put the data and template together to send the user
    context = {
        "active_tab_id": "home",
        "chemical_system_form": form,
        "structures": structures,
        "nstructures_possible": nstructures_possible,
    }
    template = "core/home.html"
    return render(request, template, context)


@login_required
def extras(request):

    # now let's put the data and template together to send the user
    context = {"active_tab_id": "extras"}
    template = "core/extras.html"
    return render(request, template, context)


def testing(request):

    # now let's put the data and template together to send the user
    context = {"active_tab_id": "home"}
    template = "core/testing.html"
    return render(request, template, context)
