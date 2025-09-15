import gurobipy as gp
import os


def create_gurobi_model(name="", own_env=False):
    if not own_env:
        # Use the default environment if not creating a new one
        return gp.Model(name=name)

    env = gp.Env(empty=True)
    env.setParam("WLSAccessID", os.getenv("GRB_WLSACCESSID"))
    env.setParam("WLSSecret", os.getenv("GRB_WLSSECRET"))
    env.setParam("LicenseID", int(os.getenv("GRB_LICENSEID")))
    env.start()

    return gp.Model(name=name, env=env)
