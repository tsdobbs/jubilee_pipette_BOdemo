                
import numpy as np
from ax.service.ax_client import AxClient, ObjectiveProperties


import pandas as pd

obj1_name = "diff_from_fluo_objective"

# Define total for compositional constraint, where x1 + x2 + x3 == total
total = 1.0 #volume fraction must sum to 1.0

WORKING_VOLUME = 200 #in ul

#SETUP LABWARE POSITIONS

def make_formulation(well, c1, c2, c3, jubilee, P300, reagent_stocks):
   v1, v2, v3 = [c * WORKING_VOLUME for c in [c1, c2, c3]]
   #get pipette tool
   #pipette each
   pass

def read_fluo(well):
    #get flurourescence probe
    #read
    #zip freqnecy and amplitude file
    #make dataframe, remove areas away from region of interest
    amplitude = max(0) #take the max value of the series instead of 0

    return amplitude


def get_fluo_diff(c1, c2, c3, objective_amplitude, get_well, jubilee, P300, FProbe, reagent_stocks, DUMMY=False):

    well = next(get_well())

    if not DUMMY:
        make_formulation(well, c1, c2, c3, jubilee, P300, reagent_stocks)
        y = abs(objective_amplitude - read_fluo(well, jubilee, FProbe))
    else:
        y = objective_amplitude - (((c1 - c2)**2 + c2**2) + c3*.1) #arbitrary function for testing

    return y


def run_campaign(objective_amplitude, n_iterations, threshold, jubilee, P300, FProbe, reagent_stocks, starting_well = 0 , save =True, DUMMY = False):

    def well_getter():
        for i in range(starting_well, 95):
            yield i
    get_well = well_getter

    ax_client = AxClient()
    # note how lower bound of x1 is now 0.0 instead of -5.0, which is for the sake of illustrating a composition, where negative values wouldn't make sense
    ax_client.create_experiment(
        parameters=[
            {"name": "c1", "type": "range", "bounds": [0.0, total]},
            {"name": "c2", "type": "range", "bounds": [0.0, total]},
        ],
        objectives={
            obj1_name: ObjectiveProperties(minimize=True),
        },
        parameter_constraints=[
            f"c1 + c2 <= {total}",  # reparameterized compositional constraint, which is a type of sum constraint
        ],
    )

    results = np.inf
    cnt = 0
    while results > threshold and cnt < n_iterations:
        cnt += 1

        parameterization, trial_index = ax_client.get_next_trial()

        # extract parameters
        c1 = parameterization["c1"]
        c2 = parameterization["c2"]
        c3 = total - (c1 + c2)  # composition constraint: c1 + c2 + c3 == total

        results = get_fluo_diff(c1,c2,c3, objective_amplitude, get_well, jubilee, P300, FProbe, reagent_stocks, DUMMY)
        ax_client.complete_trial(trial_index=trial_index, raw_data=results)

        if save: ax_client.save_to_json_file() #in case you want to restart the experiment later


    best_parameters, metrics = ax_client.get_best_parameters()

                