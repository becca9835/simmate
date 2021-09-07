# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------

class Trigger:
    def __init__(
        self,
    ):
        # add any unchanging variables or settings here
        pass

    def check(self, search):
        # This method should take in one argument:
        # search = this is the main Search object seen in search.py
        # The Trigger can run any analysis on the Search object WITHOUT
        # making any changes to it. Then you should return True if the
        # trigger condition(s) has been met and False if the calculation should
        # continue without setting off the trigger
        pass

    def action(self, search):
        # This method should take in one argument:
        # search = this is the main Search object seen in search.py
        # This is where to apply some change to the search. It can be whatever you'd like!
        # The most common actions (such as search.new_sample) will be accessed via
        # the search class and not custom code here.
        pass


#!!! In the future, should I reduce triggers down to lower order objects?
#!!! One example of this would be reducing a Trigger to a Check/Validation and an Action

# -----------------------------------------------------------------------------


class InitStructures:

    # Super simple check that passes True if no structures have been created yet.
    # If that is the case, then it creates new structures using the input probilities for each generator.
    # This is used to start the entire search.

    def __init__(self, n_initial_structures):

        # Number of initial structures to create
        self.n_initial_structures = n_initial_structures

    def check(self, search):  #!!! can I move 'search' to the init?

        if not search.structures:  # same as len(structures) == 0
            return True
        else:
            return False

    def action(self, search):

        print("Making new structures...")

        # we want n total structures so we are going to loop this number of times
        for n in range(self.n_initial_structures):
            # make a new sample
            search.new_sample(creators_only=True)


# -----------------------------------------------------------------------------


class AddStructures:
    def __init__(self, n_pending_limit, n_add_structures):

        self.n_pending_limit = n_pending_limit

        # Number of structures to create if the pending_limit is hit
        self.n_add_structures = n_add_structures

    def check(self, search):  #!!! can I move 'search' to the init?

        # if no structures have completed yet, we don't want to add any new structure with this trigger
        if search.njobs_completed == 0:
            return False

        # See if the number of jobs pending has dropped below the limit
        if search.njobs_pending <= self.n_pending_limit:
            return True
        else:
            return False

    def action(self, search):

        print("Making new structures...")

        # we want n total structures so we are going to loop this number of times
        for n in range(self.n_add_structures):
            # make a new sample
            search.new_sample()


# -----------------------------------------------------------------------------