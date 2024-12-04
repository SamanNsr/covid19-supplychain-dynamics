"""
Python model 'innovation sd.py'
Translated using PySD
"""

from pathlib import Path
import numpy as np
from scipy import stats

from pysd.py_backend.functions import integer, if_then_else
from pysd.py_backend.statefuls import Delay, Smooth, Integ
from pysd import Component

__pysd_version__ = "3.10.0"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent


component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 0,
    "final_time": lambda: 72,
    "time_step": lambda: 0.5,
    "saveper": lambda: time_step(),
}


def _init_outer_references(data):
    for key in data:
        __data[key] = data[key]


@component.add(name="Time")
def time():
    """
    Current time of the model.
    """
    return __data["time"]()


@component.add(
    name="FINAL TIME", units="week", comp_type="Constant", comp_subtype="Normal"
)
def final_time():
    """
    The final time for the simulation.
    """
    return __data["time"].final_time()


@component.add(
    name="INITIAL TIME", units="week", comp_type="Constant", comp_subtype="Normal"
)
def initial_time():
    """
    The initial time for the simulation.
    """
    return __data["time"].initial_time()


@component.add(
    name="SAVEPER",
    units="week",
    limits=(0.0, np.nan),
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_step": 1},
)
def saveper():
    """
    The frequency with which output is stored.
    """
    return __data["time"].saveper()


@component.add(
    name="TIME STEP",
    units="week",
    limits=(0.0, np.nan),
    comp_type="Constant",
    comp_subtype="Normal",
)
def time_step():
    """
    The time step for the simulation.
    """
    return __data["time"].time_step()


#######################################################################
#                           MODEL VARIABLES                           #
#######################################################################


@component.add(
    name='"%reduction in product price"', comp_type="Constant", comp_subtype="Normal"
)
def reduction_in_product_price():
    return 0.2


@component.add(
    name="coefficient of hr reduction", comp_type="Constant", comp_subtype="Normal"
)
def coefficient_of_hr_reduction():
    return 0.1


@component.add(name="initial price", comp_type="Constant", comp_subtype="Normal")
def initial_price():
    return 200


@component.add(
    name="reduction rate of hr",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "increase_of_hr_reduction_rate": 2,
        "coefficient_of_hr_reduction": 3,
        "mhr": 3,
        "desired_mhr": 3,
        "time_3": 1,
    },
)
def reduction_rate_of_hr():
    return if_then_else(
        time_1() == 1,
        lambda: (mhr() / desired_mhr())
        * (1 + increase_of_hr_reduction_rate())
        * coefficient_of_hr_reduction(),
        lambda: if_then_else(
            time_3() == 1,
            lambda: (mhr() / desired_mhr())
            * (1 + 0.5 * increase_of_hr_reduction_rate())
            * coefficient_of_hr_reduction(),
            lambda: (mhr() / desired_mhr()) * coefficient_of_hr_reduction(),
        ),
    )


@component.add(
    name="temp increase",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_step": 1, "reduction_rate_of_hr": 1},
)
def temp_increase():
    return time_step() * reduction_rate_of_hr()


@component.add(
    name="Temp MHR reduction",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_temp_mhr_reduction": 1},
    other_deps={
        "_integ_temp_mhr_reduction": {
            "initial": {},
            "step": {"temp_increase": 1, "temp_reduction": 1},
        }
    },
)
def temp_mhr_reduction():
    return _integ_temp_mhr_reduction()


_integ_temp_mhr_reduction = Integ(
    lambda: temp_increase() - temp_reduction(), lambda: 0, "_integ_temp_mhr_reduction"
)


@component.add(
    name="temp reduction",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"temp_mhr_reduction": 1},
)
def temp_reduction():
    return integer(temp_mhr_reduction())


@component.add(name="desired MHR", comp_type="Constant", comp_subtype="Normal")
def desired_mhr():
    return 400


@component.add(
    name='"%reduction of production rate"',
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "mhr": 2,
        "job_performance": 2,
        "initial_reduction_of_production_rate": 1,
        "desired_mhr": 2,
    },
)
def reduction_of_production_rate():
    return if_then_else(
        time_1() == 1,
        lambda: initial_reduction_of_production_rate()
        + ((1 - job_performance()) * (desired_mhr() / mhr())) / 5,
        lambda: ((1 - job_performance()) * (desired_mhr() / mhr())) / 5,
    )


@component.add(
    name="reduction in hr of manufaturer",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"temp_reduction": 1},
)
def reduction_in_hr_of_manufaturer():
    return temp_reduction()


@component.add(
    name="discrepancy of MHR",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"desired_mhr": 1, "mhr": 1},
)
def discrepancy_of_mhr():
    return np.maximum(desired_mhr() - mhr(), 0)


@component.add(
    name="price",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_1": 1, "reduction_in_product_price": 1, "initial_price": 2},
)
def price():
    return if_then_else(
        time_1() == 1,
        lambda: initial_price() * (1 - reduction_in_product_price()),
        lambda: initial_price(),
    )


@component.add(
    name='"%increase of hr reduction rate"', comp_type="Constant", comp_subtype="Normal"
)
def increase_of_hr_reduction_rate():
    return 1.2


@component.add(
    name="initial reduction of production rate",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_reduction_of_production_rate():
    return 0.2


@component.add(
    name='"%reduction of oc js"', comp_type="Constant", comp_subtype="Normal"
)
def reduction_of_oc_js():
    return 0.2


@component.add(name='"%reduction of oc"', comp_type="Constant", comp_subtype="Normal")
def reduction_of_oc():
    return 0.2


@component.add(name='"%reduction of wm"', comp_type="Constant", comp_subtype="Normal")
def reduction_of_wm():
    return 0.2


@component.add(
    name="oc deviation",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "initial_deviation_of_oc": 3,
        "reduction_of_oc": 2,
        "time_3": 1,
    },
)
def oc_deviation():
    return if_then_else(
        time_1() == 1,
        lambda: (1 + reduction_of_oc()) * initial_deviation_of_oc(),
        lambda: if_then_else(
            time_3() == 1,
            lambda: (1 + 0.5 * reduction_of_oc()) * initial_deviation_of_oc(),
            lambda: initial_deviation_of_oc(),
        ),
    )


@component.add(
    name="oc mean",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "initial_mean_of_oc": 3,
        "reduction_of_oc": 2,
        "time_3": 1,
    },
)
def oc_mean():
    return if_then_else(
        time_1() == 1,
        lambda: (1 - reduction_of_oc()) * initial_mean_of_oc(),
        lambda: if_then_else(
            time_3() == 1,
            lambda: (1 + 0.5 * reduction_of_oc()) * initial_mean_of_oc(),
            lambda: initial_mean_of_oc(),
        ),
    )


@component.add(
    name="initial deviation of js", comp_type="Constant", comp_subtype="Normal"
)
def initial_deviation_of_js():
    return 0.1


@component.add(
    name="adjust time of MHR",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_1": 1, "initial_adjust_time_of_mhr": 2, "increase_of_time": 1},
)
def adjust_time_of_mhr():
    return if_then_else(
        time_1() == 1,
        lambda: initial_adjust_time_of_mhr() * (1 + increase_of_time()),
        lambda: initial_adjust_time_of_mhr(),
    )


@component.add(
    name="initial deviation of wm", comp_type="Constant", comp_subtype="Normal"
)
def initial_deviation_of_wm():
    return 0.1


@component.add(name="initial mean of js", comp_type="Constant", comp_subtype="Normal")
def initial_mean_of_js():
    return 1


@component.add(name="initial mean of oc", comp_type="Constant", comp_subtype="Normal")
def initial_mean_of_oc():
    return 1


@component.add(name="initial mean of wm", comp_type="Constant", comp_subtype="Normal")
def initial_mean_of_wm():
    return 1


@component.add(name="w oc", comp_type="Constant", comp_subtype="Normal")
def w_oc():
    return 1


@component.add(
    name="js deviation",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "initial_deviation_of_js": 3,
        "reduction_of_oc_js": 2,
        "time_3": 1,
    },
)
def js_deviation():
    return if_then_else(
        time_1() == 1,
        lambda: (1 + reduction_of_oc_js()) * initial_deviation_of_js(),
        lambda: if_then_else(
            time_3() == 1,
            lambda: (1 + 0.5 * reduction_of_oc_js()) * initial_deviation_of_js(),
            lambda: initial_deviation_of_js(),
        ),
    )


@component.add(
    name="wm deviation",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "reduction_of_wm": 2,
        "initial_deviation_of_wm": 3,
        "time_3": 1,
    },
)
def wm_deviation():
    return if_then_else(
        time_1() == 1,
        lambda: (1 + reduction_of_wm()) * initial_deviation_of_wm(),
        lambda: if_then_else(
            time_3() == 1,
            lambda: (1 + 0.5 * reduction_of_wm()) * initial_deviation_of_wm(),
            lambda: initial_deviation_of_wm(),
        ),
    )


@component.add(
    name="wm mean",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "reduction_of_wm": 2,
        "initial_mean_of_wm": 3,
        "time_3": 1,
    },
)
def wm_mean():
    return if_then_else(
        time_1() == 1,
        lambda: (1 - reduction_of_wm()) * initial_mean_of_wm(),
        lambda: if_then_else(
            time_3() == 1,
            lambda: (1 + 0.5 * reduction_of_wm()) * initial_mean_of_wm(),
            lambda: initial_mean_of_wm(),
        ),
    )


@component.add(
    name="work motivation",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_work_motivation": 1},
    other_deps={
        "_smooth_work_motivation": {
            "initial": {"wm_mean": 1, "wm_deviation": 1, "time": 1},
            "step": {"wm_mean": 1, "wm_deviation": 1, "time": 1},
        }
    },
)
def work_motivation():
    return _smooth_work_motivation()


_smooth_work_motivation = Smooth(
    lambda: stats.truncnorm.rvs(0, 2, loc=wm_mean(), scale=wm_deviation(), size=()),
    lambda: 2,
    lambda: stats.truncnorm.rvs(0, 2, loc=wm_mean(), scale=wm_deviation(), size=()),
    lambda: 1,
    "_smooth_work_motivation",
)


@component.add(
    name="job satisfaction",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_job_satisfaction": 1},
    other_deps={
        "_smooth_job_satisfaction": {
            "initial": {"js_mean": 1, "js_deviation": 1, "time": 1},
            "step": {"js_mean": 1, "js_deviation": 1, "time": 1},
        }
    },
)
def job_satisfaction():
    return _smooth_job_satisfaction()


_smooth_job_satisfaction = Smooth(
    lambda: stats.truncnorm.rvs(0, 2, loc=js_mean(), scale=js_deviation(), size=()),
    lambda: 2,
    lambda: stats.truncnorm.rvs(0, 2, loc=js_mean(), scale=js_deviation(), size=()),
    lambda: 1,
    "_smooth_job_satisfaction",
)


@component.add(
    name="js mean",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "initial_mean_of_js": 3,
        "reduction_of_oc_js": 2,
        "time_3": 1,
    },
)
def js_mean():
    return if_then_else(
        time_1() == 1,
        lambda: (1 - reduction_of_oc_js()) * initial_mean_of_js(),
        lambda: if_then_else(
            time_3() == 1,
            lambda: (1 + 0.5 * reduction_of_oc_js()) * initial_mean_of_js(),
            lambda: initial_mean_of_js(),
        ),
    )


@component.add(
    name="initial adjust time of MHR", comp_type="Constant", comp_subtype="Normal"
)
def initial_adjust_time_of_mhr():
    return 2


@component.add(name="w js", comp_type="Constant", comp_subtype="Normal")
def w_js():
    return 2


@component.add(
    name="initial deviation of oc", comp_type="Constant", comp_subtype="Normal"
)
def initial_deviation_of_oc():
    return 0.1


@component.add(
    name="increase in hr of manufaturer",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"discrepancy_of_mhr": 1, "adjust_time_of_mhr": 1},
)
def increase_in_hr_of_manufaturer():
    return integer(np.maximum(discrepancy_of_mhr() / adjust_time_of_mhr(), 0))


@component.add(
    name="organizational commitment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_organizational_commitment": 1},
    other_deps={
        "_smooth_organizational_commitment": {
            "initial": {"oc_mean": 1, "oc_deviation": 1, "time": 1},
            "step": {"oc_mean": 1, "oc_deviation": 1, "time": 1},
        }
    },
)
def organizational_commitment():
    return _smooth_organizational_commitment()


_smooth_organizational_commitment = Smooth(
    lambda: stats.truncnorm.rvs(0, 2, loc=oc_mean(), scale=oc_deviation(), size=()),
    lambda: 2,
    lambda: stats.truncnorm.rvs(0, 2, loc=oc_mean(), scale=oc_deviation(), size=()),
    lambda: 1,
    "_smooth_organizational_commitment",
)


@component.add(name="w wm", comp_type="Constant", comp_subtype="Normal")
def w_wm():
    return 3


@component.add(
    name="job performance",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "job_satisfaction": 1,
        "w_js": 2,
        "organizational_commitment": 1,
        "w_oc": 2,
        "work_motivation": 1,
        "w_wm": 2,
    },
)
def job_performance():
    return np.power(
        np.power(job_satisfaction(), w_js())
        * np.power(organizational_commitment(), w_oc())
        * np.power(work_motivation(), w_wm()),
        1 / (w_js() + w_oc() + w_wm()),
    )


@component.add(
    name="desired of RMSI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"cover_time_of_rmsi": 1, "expected_purchase_rate_of_new_material": 1},
)
def desired_of_rmsi():
    return cover_time_of_rmsi() * expected_purchase_rate_of_new_material()


@component.add(
    name="MHR",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_mhr": 1},
    other_deps={
        "_integ_mhr": {
            "initial": {},
            "step": {
                "increase_in_hr_of_manufaturer": 1,
                "reduction_in_hr_of_manufaturer": 1,
            },
        }
    },
)
def mhr():
    return _integ_mhr()


_integ_mhr = Integ(
    lambda: increase_in_hr_of_manufaturer() - reduction_in_hr_of_manufaturer(),
    lambda: 400,
    "_integ_mhr",
)


@component.add(name="Krmsi", comp_type="Constant", comp_subtype="Normal")
def krmsi():
    return 1


@component.add(name="Krpi", comp_type="Constant", comp_subtype="Normal")
def krpi():
    return 0


@component.add(name="L units", comp_type="Constant", comp_subtype="Normal")
def l_units():
    return 4


@component.add(
    name="discrepancy of RI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"desired_of_ri": 1, "ri": 1},
)
def discrepancy_of_ri():
    return np.maximum(desired_of_ri() - ri(), 0)


@component.add(
    name="M cost",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "total_pr": 1,
        "production_cost": 1,
        "mi": 1,
        "t1": 1,
        "mi_holding_cost": 1,
        "shipment_to_wholesaler": 1,
        "m_transportation_cost": 1,
        "shipment_offered_by_contracted_manufacturer": 1,
        "unit_cost_by_contract": 1,
    },
)
def m_cost():
    return (
        total_pr() * production_cost()
        + mi() * mi_holding_cost() / t1()
        + shipment_to_wholesaler() * m_transportation_cost()
        + shipment_offered_by_contracted_manufacturer() * unit_cost_by_contract()
    )


@component.add(
    name="M transportation cost", comp_type="Constant", comp_subtype="Normal"
)
def m_transportation_cost():
    return 1.2


@component.add(name="M units", comp_type="Constant", comp_subtype="Normal")
def m_units():
    return 20


@component.add(
    name="adjust time of RI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_1": 1, "initial_adjust_time_of_ri": 2, "increase_of_time": 1},
)
def adjust_time_of_ri():
    return if_then_else(
        time_1() == 1,
        lambda: initial_adjust_time_of_ri() * (1 + increase_of_time()),
        lambda: initial_adjust_time_of_ri(),
    )


@component.add(
    name="adjust time of RMSI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_1": 1, "initial_adjust_time_of_rmsi": 2, "increase_of_time": 1},
)
def adjust_time_of_rmsi():
    return if_then_else(
        time_1() == 1,
        lambda: initial_adjust_time_of_rmsi() * (1 + increase_of_time()),
        lambda: initial_adjust_time_of_rmsi(),
    )


@component.add(
    name="D transportation cost of recycled material",
    comp_type="Constant",
    comp_subtype="Normal",
)
def d_transportation_cost_of_recycled_material():
    return 0.04


@component.add(
    name="discrepancy of WI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"desired_of_wi": 1, "wi": 1},
)
def discrepancy_of_wi():
    return np.maximum(desired_of_wi() - wi(), 0)


@component.add(name="MI capacity", comp_type="Constant", comp_subtype="Normal")
def mi_capacity():
    return 10000


@component.add(name="MI holding cost", comp_type="Constant", comp_subtype="Normal")
def mi_holding_cost():
    return 0.8


@component.add(name="MO units", comp_type="Constant", comp_subtype="Normal")
def mo_units():
    return 12


@component.add(
    name="adjust time of WI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_1": 1, "initial_adjust_time_of_wi": 2, "increase_of_time": 1},
)
def adjust_time_of_wi():
    return if_then_else(
        time_1() == 1,
        lambda: initial_adjust_time_of_wi() * (1 + increase_of_time()),
        lambda: initial_adjust_time_of_wi(),
    )


@component.add(
    name="expected purchase rate of new material",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delay_expected_purchase_rate_of_new_material": 1},
    other_deps={
        "_delay_expected_purchase_rate_of_new_material": {
            "initial": {
                "total_amount_of_material": 1,
                "rmi": 1,
                "time_step": 1,
                "t1": 1,
            },
            "step": {"purchase_rate_of_new_material": 1, "t1": 1},
        }
    },
)
def expected_purchase_rate_of_new_material():
    return _delay_expected_purchase_rate_of_new_material()


_delay_expected_purchase_rate_of_new_material = Delay(
    lambda: purchase_rate_of_new_material(),
    lambda: t1(),
    lambda: (total_amount_of_material() - rmi()) / time_step(),
    lambda: 1,
    time_step,
    "_delay_expected_purchase_rate_of_new_material",
)


@component.add(name="N5 units", comp_type="Constant", comp_subtype="Normal")
def n5_units():
    return 5


@component.add(name="NO units", comp_type="Constant", comp_subtype="Normal")
def no_units():
    return 1


@component.add(
    name='"expected used-product demand rate"',
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delay_expected_usedproduct_demand_rate": 1},
    other_deps={
        "_delay_expected_usedproduct_demand_rate": {
            "initial": {"expected_pr_for_rpi": 1, "n1_units": 1, "tu": 1},
            "step": {"expected_pr_for_rpi": 1, "n1_units": 1, "tu": 1},
        }
    },
)
def expected_usedproduct_demand_rate():
    return _delay_expected_usedproduct_demand_rate()


_delay_expected_usedproduct_demand_rate = Delay(
    lambda: expected_pr_for_rpi() / n1_units(),
    lambda: tu(),
    lambda: expected_pr_for_rpi() / n1_units(),
    lambda: 1,
    time_step,
    "_delay_expected_usedproduct_demand_rate",
)


@component.add(
    name="C cost",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "expected_collection_rate": 1,
        "collection_cost": 1,
        "ci_holding_cost": 1,
        "temporary_ci": 1,
        "t1": 1,
        "ci": 1,
        "purchase_rate": 1,
        "c_transportation_cost": 1,
    },
)
def c_cost():
    return (
        expected_collection_rate() * collection_cost()
        + (ci() + temporary_ci()) * ci_holding_cost() / t1()
        + purchase_rate() * c_transportation_cost()
    )


@component.add(
    name="C transportation cost", comp_type="Constant", comp_subtype="Normal"
)
def c_transportation_cost():
    return 1


@component.add(name="part production cost", comp_type="Constant", comp_subtype="Normal")
def part_production_cost():
    return 4.8


@component.add(name="CI holding cost", comp_type="Constant", comp_subtype="Normal")
def ci_holding_cost():
    return 0.4


@component.add(name="R delivery cost", comp_type="Constant", comp_subtype="Normal")
def r_delivery_cost():
    return 1


@component.add(name="hd", comp_type="Constant", comp_subtype="Normal")
def hd():
    return 6


@component.add(
    name="recycling rate",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"rmi": 1, "total_amount_of_material": 1, "recycling_time": 1},
)
def recycling_rate():
    return np.minimum(rmi(), total_amount_of_material()) / recycling_time()


@component.add(name="hrec", comp_type="Constant", comp_subtype="Normal")
def hrec():
    return 4


@component.add(name="collection cost", comp_type="Constant", comp_subtype="Normal")
def collection_cost():
    return 8


@component.add(name="disassembly cost", comp_type="Constant", comp_subtype="Normal")
def disassembly_cost():
    return 0.7


@component.add(name="T1", comp_type="Constant", comp_subtype="Normal")
def t1():
    return 1


@component.add(name="T2", comp_type="Constant", comp_subtype="Normal")
def t2():
    return 4


@component.add(name="T3", comp_type="Constant", comp_subtype="Normal")
def t3():
    return 4


@component.add(
    name="coming rate 1",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delay_coming_rate_1": 1},
    other_deps={
        "_delay_coming_rate_1": {
            "initial": {"sales_1": 1, "usage_period": 1},
            "step": {"sales": 1, "usage_period": 1},
        }
    },
)
def coming_rate_1():
    return _delay_coming_rate_1()


_delay_coming_rate_1 = Delay(
    lambda: sales(),
    lambda: usage_period(),
    lambda: sales_1(),
    lambda: 3,
    time_step,
    "_delay_coming_rate_1",
)


@component.add(
    name="coming rate of raw material",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "krmsi": 1,
        "expected_purchase_rate_of_new_material": 2,
        "time_1": 1,
        "discrepancy_of_rmsi": 2,
        "adjust_time_of_rmsi": 2,
    },
)
def coming_rate_of_raw_material():
    return if_then_else(
        krmsi() == 1,
        lambda: if_then_else(
            time_1() == 1,
            lambda: 0,
            lambda: np.maximum(
                expected_purchase_rate_of_new_material()
                + discrepancy_of_rmsi() / adjust_time_of_rmsi(),
                0,
            ),
        ),
        lambda: np.maximum(
            expected_purchase_rate_of_new_material()
            + discrepancy_of_rmsi() / adjust_time_of_rmsi(),
            0,
        ),
    )


@component.add(
    name="PP cost",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "total_ppr": 1,
        "part_production_cost": 1,
        "ppi_holding_cost": 2,
        "t1": 2,
        "ppi": 1,
        "temporary_ppi": 1,
        "pp_transportation_cost": 1,
        "purchase_rate_of_new_part": 1,
    },
)
def pp_cost():
    return (
        total_ppr() * part_production_cost()
        + ppi() * ppi_holding_cost() / t1()
        + temporary_ppi() * ppi_holding_cost() / t1()
        + purchase_rate_of_new_part() * pp_transportation_cost()
    )


@component.add(
    name="pp transportation cost", comp_type="Constant", comp_subtype="Normal"
)
def pp_transportation_cost():
    return 0.4


@component.add(name="RI holding cost", comp_type="Constant", comp_subtype="Normal")
def ri_holding_cost():
    return 0.7


@component.add(name="cover time of RI", comp_type="Constant", comp_subtype="Normal")
def cover_time_of_ri():
    return 2


@component.add(name="cover time of RMSI", comp_type="Constant", comp_subtype="Normal")
def cover_time_of_rmsi():
    return 2


@component.add(
    name="process rate",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"rt": 1, "process_time": 1},
)
def process_rate():
    return rt() / process_time()


@component.add(
    name="process time",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_1": 1, "initial_process_time": 2, "increase_of_time": 1},
)
def process_time():
    return if_then_else(
        time_1() == 1,
        lambda: initial_process_time() * (1 + increase_of_time()),
        lambda: initial_process_time(),
    )


@component.add(
    name="D cost",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "disassembly_rate": 1,
        "disassembly_cost": 1,
        "remanufacturing_rate": 2,
        "remanufacturing_cost": 1,
        "recycling_cost": 1,
        "recycling_rate": 2,
        "upi": 1,
        "t1": 5,
        "upi_holding_cost": 1,
        "parts_to_remanufacture": 1,
        "rpi_holding_cost": 2,
        "temporary_rpi": 1,
        "rmi": 1,
        "rmi_holding_cost": 1,
        "rt_holding_cost": 1,
        "rt": 1,
        "d_transportation_cost_of_remanufactured_part": 1,
        "d_transportation_cost_of_recycled_material": 1,
    },
)
def d_cost():
    return (
        disassembly_rate() * disassembly_cost()
        + remanufacturing_rate() * remanufacturing_cost()
        + recycling_rate() * recycling_cost()
        + upi() * upi_holding_cost() / t1()
        + parts_to_remanufacture() * rpi_holding_cost() / t1()
        + temporary_rpi() * rpi_holding_cost() / t1()
        + rmi() * rmi_holding_cost() / t1()
        + rt() * rt_holding_cost() / t1()
        + remanufacturing_rate() * d_transportation_cost_of_remanufactured_part()
        + recycling_rate() * d_transportation_cost_of_recycled_material()
    )


@component.add(
    name="discrepancy of Temporary RPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"planned_temporary_rpi": 1, "temporary_rpi": 1},
)
def discrepancy_of_temporary_rpi():
    return np.maximum(planned_temporary_rpi() - temporary_rpi(), 0)


@component.add(
    name="D transportation cost of remanufactured part",
    comp_type="Constant",
    comp_subtype="Normal",
)
def d_transportation_cost_of_remanufactured_part():
    return 0.4


@component.add(
    name="total pr",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"production_rate": 1, "production_rate_1": 1},
)
def total_pr():
    return production_rate() + production_rate_1()


@component.add(
    name="purchase rate of new material",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "rmsi": 2,
        "purchase_time_of_new_material": 1,
        "total_amount_of_material": 1,
        "rmi": 1,
    },
)
def purchase_rate_of_new_material():
    return if_then_else(
        rmsi() > 0,
        lambda: np.minimum(np.maximum(total_amount_of_material() - rmi(), 0), rmsi())
        / purchase_time_of_new_material(),
        lambda: 0,
    )


@component.add(name="Tu", comp_type="Constant", comp_subtype="Normal")
def tu():
    return 4


@component.add(
    name="purchase rate of new part to end product",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "discrepancy_of_parts_to_end_product": 1,
        "adjust_time_of_parts": 1,
        "purchase_rate_of_rpi_to_end_product": 1,
        "n5_units": 1,
        "purchase_rate_of_new_part": 1,
    },
)
def purchase_rate_of_new_part_to_end_product():
    return np.minimum(
        np.maximum(
            discrepancy_of_parts_to_end_product() / adjust_time_of_parts()
            - purchase_rate_of_rpi_to_end_product(),
            0,
        ),
        purchase_rate_of_new_part() / n5_units(),
    )


@component.add(
    name="expected purchase rate of new part",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delay_expected_purchase_rate_of_new_part": 1},
    other_deps={
        "_delay_expected_purchase_rate_of_new_part": {
            "initial": {
                "desired_needs_of_parts_for_production": 1,
                "purchase_rate_of_rpi": 1,
                "t2": 1,
            },
            "step": {"purchase_rate_of_new_part": 1, "t2": 1},
        }
    },
)
def expected_purchase_rate_of_new_part():
    return _delay_expected_purchase_rate_of_new_part()


_delay_expected_purchase_rate_of_new_part = Delay(
    lambda: purchase_rate_of_new_part(),
    lambda: t2(),
    lambda: np.maximum(
        desired_needs_of_parts_for_production() - purchase_rate_of_rpi(), 0
    ),
    lambda: 1,
    time_step,
    "_delay_expected_purchase_rate_of_new_part",
)


@component.add(
    name="purchase rate of RPI to end product",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "discrepancy_of_parts_to_end_product": 1,
        "adjust_time_of_parts": 1,
        "purchase_rate_of_rpi": 1,
        "n5_units": 1,
    },
)
def purchase_rate_of_rpi_to_end_product():
    return np.minimum(
        discrepancy_of_parts_to_end_product() / adjust_time_of_parts(),
        purchase_rate_of_rpi() / n5_units(),
    )


@component.add(
    name="desired needs of parts for production",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "expected_wholesaler_orders": 1,
        "adjust_time_for_mi": 1,
        "discrepancy_of_mi": 1,
        "no_units": 1,
    },
)
def desired_needs_of_parts_for_production():
    return (
        expected_wholesaler_orders() + discrepancy_of_mi() / adjust_time_for_mi()
    ) * no_units()


@component.add(
    name="purchase time of new material", comp_type="Constant", comp_subtype="Normal"
)
def purchase_time_of_new_material():
    return 1


@component.add(
    name="desired of RI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"expected_demand": 1, "cover_time_of_ri": 1},
)
def desired_of_ri():
    return expected_demand() * cover_time_of_ri()


@component.add(name="k", comp_type="Constant", comp_subtype="Normal")
def k():
    return 1


@component.add(
    name="desired of WI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"initial_cover_time_of_wi": 1, "expected_retailer_orders": 1},
)
def desired_of_wi():
    return initial_cover_time_of_wi() * expected_retailer_orders()


@component.add(name="Kci", comp_type="Constant", comp_subtype="Normal")
def kci():
    return 1


@component.add(
    name="desired RPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"cover_time_of_rpi": 1, "expected_pr_for_rpi": 1},
)
def desired_rpi():
    return cover_time_of_rpi() * expected_pr_for_rpi()


@component.add(
    name="remanent trash will be disposed",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"l_units": 1, "upi_disassembly_rate": 1},
)
def remanent_trash_will_be_disposed():
    return l_units() * upi_disassembly_rate()


@component.add(name="Km2", comp_type="Constant", comp_subtype="Normal")
def km2():
    return 0


@component.add(
    name="disassembly rate",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "upi": 1,
        "rpn": 1,
        "disassembly_time": 1,
        "disassembly_rate1": 1,
        "expected_pr_for_rpi": 1,
        "discrepancy_of_rpi": 1,
        "adjust_time_of_rpi": 1,
    },
)
def disassembly_rate():
    return np.maximum(
        np.minimum(
            upi() * rpn() / disassembly_time(),
            expected_pr_for_rpi()
            + discrepancy_of_rpi() / adjust_time_of_rpi()
            + disassembly_rate1(),
        ),
        0,
    )


@component.add(name="Km5", comp_type="Constant", comp_subtype="Normal")
def km5():
    return 0


@component.add(name="Kp", comp_type="Constant", comp_subtype="Normal")
def kp():
    return 1


@component.add(
    name="retailer orders",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"expected_demand": 1, "discrepancy_of_ri": 1, "adjust_time_of_ri": 1},
)
def retailer_orders():
    return expected_demand() + discrepancy_of_ri() / adjust_time_of_ri()


@component.add(
    name="initial adjust time of RI", comp_type="Constant", comp_subtype="Normal"
)
def initial_adjust_time_of_ri():
    return 4


@component.add(
    name="initial adjust time of RMSI", comp_type="Constant", comp_subtype="Normal"
)
def initial_adjust_time_of_rmsi():
    return 4


@component.add(name='"Kused-prod"', comp_type="Constant", comp_subtype="Normal")
def kusedprod():
    return 1


@component.add(name="T5", comp_type="Constant", comp_subtype="Normal")
def t5():
    return 4


@component.add(
    name="expected wholesaler orders",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delay_expected_wholesaler_orders": 1},
    other_deps={
        "_delay_expected_wholesaler_orders": {
            "initial": {"wholesaler_orders": 1, "tm": 1},
            "step": {"wholesaler_orders": 1, "tm": 1},
        }
    },
)
def expected_wholesaler_orders():
    return _delay_expected_wholesaler_orders()


_delay_expected_wholesaler_orders = Delay(
    lambda: wholesaler_orders(),
    lambda: tm(),
    lambda: wholesaler_orders(),
    lambda: 1,
    time_step,
    "_delay_expected_wholesaler_orders",
)


@component.add(
    name="discrepancy of RMSI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"desired_of_rmsi": 1, "rmsi": 1},
)
def discrepancy_of_rmsi():
    return np.maximum(desired_of_rmsi() - rmsi(), 0)


@component.add(
    name="discrepancy of RPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"desired_rpi": 1, "parts_to_remanufacture": 1},
)
def discrepancy_of_rpi():
    return np.maximum(desired_rpi() - parts_to_remanufacture(), 0)


@component.add(
    name="RMS transportation cost", comp_type="Constant", comp_subtype="Normal"
)
def rms_transportation_cost():
    return 0.04


@component.add(name="making cost", comp_type="Constant", comp_subtype="Normal")
def making_cost():
    return 0.5


@component.add(
    name="initial cover time of WI", comp_type="Constant", comp_subtype="Normal"
)
def initial_cover_time_of_wi():
    return 1


@component.add(
    name="total amount of material",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"total_ppr": 1, "time_step": 1, "mo_units": 1},
)
def total_amount_of_material():
    return total_ppr() * time_step() * mo_units()


@component.add(name="RPI holding cost", comp_type="Constant", comp_subtype="Normal")
def rpi_holding_cost():
    return 0.07


@component.add(
    name="expected collection rate",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "kc": 1,
        "expected_purchase_rate": 2,
        "adjust_time_of_ci": 2,
        "discrepancy_of_ci": 2,
        "used_product_amount": 4,
        "collection_time": 2,
        "collection_rate1": 1,
    },
)
def expected_collection_rate():
    return if_then_else(
        kc() == 1,
        lambda: if_then_else(
            used_product_amount() > 0,
            lambda: np.minimum(
                used_product_amount() / collection_time(),
                np.maximum(
                    expected_purchase_rate()
                    + discrepancy_of_ci() / adjust_time_of_ci(),
                    0,
                ),
            ),
            lambda: 0,
        ),
        lambda: if_then_else(
            used_product_amount() > 0,
            lambda: np.minimum(
                used_product_amount() / collection_time(),
                np.maximum(
                    expected_purchase_rate()
                    + discrepancy_of_ci() / adjust_time_of_ci()
                    + collection_rate1(),
                    0,
                ),
            ),
            lambda: 0,
        ),
    )


@component.add(
    name="expected demand",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delay_expected_demand": 1},
    other_deps={
        "_delay_expected_demand": {
            "initial": {"mean_value": 1, "t4": 1},
            "step": {"demand": 1, "t4": 1},
        }
    },
)
def expected_demand():
    return _delay_expected_demand()


_delay_expected_demand = Delay(
    lambda: demand(),
    lambda: t4(),
    lambda: mean_value(),
    lambda: 1,
    time_step,
    "_delay_expected_demand",
)


@component.add(
    name="expected pr for RPI",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delay_expected_pr_for_rpi": 1},
    other_deps={
        "_delay_expected_pr_for_rpi": {
            "initial": {
                "total_amount_of_the_part": 1,
                "remanufacturing_time": 1,
                "t5": 1,
            },
            "step": {"total_amount_of_the_part": 1, "remanufacturing_time": 1, "t5": 1},
        }
    },
)
def expected_pr_for_rpi():
    return _delay_expected_pr_for_rpi()


_delay_expected_pr_for_rpi = Delay(
    lambda: total_amount_of_the_part() / remanufacturing_time(),
    lambda: t5(),
    lambda: total_amount_of_the_part() / remanufacturing_time(),
    lambda: 1,
    time_step,
    "_delay_expected_pr_for_rpi",
)


@component.add(
    name="expected purchase rate",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delay_expected_purchase_rate": 1},
    other_deps={
        "_delay_expected_purchase_rate": {
            "initial": {"should_satisfy_rate_of_usedproducts": 1, "tu": 1},
            "step": {"should_satisfy_rate_of_usedproducts": 1, "tu": 1},
        }
    },
)
def expected_purchase_rate():
    return _delay_expected_purchase_rate()


_delay_expected_purchase_rate = Delay(
    lambda: should_satisfy_rate_of_usedproducts(),
    lambda: tu(),
    lambda: should_satisfy_rate_of_usedproducts(),
    lambda: 1,
    time_step,
    "_delay_expected_purchase_rate",
)


@component.add(
    name='"sales-"',
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"sales_1": 1, "n4": 1},
)
def sales():
    return sales_1() * n4()


@component.add(
    name="unit cost by contract", comp_type="Constant", comp_subtype="Normal"
)
def unit_cost_by_contract():
    return 48


@component.add(
    name="expected retailer orders",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delay_expected_retailer_orders": 1},
    other_deps={
        "_delay_expected_retailer_orders": {
            "initial": {"retailer_orders": 1, "t3": 1},
            "step": {"retailer_orders": 1, "t3": 1},
        }
    },
)
def expected_retailer_orders():
    return _delay_expected_retailer_orders()


_delay_expected_retailer_orders = Delay(
    lambda: retailer_orders(),
    lambda: t3(),
    lambda: retailer_orders(),
    lambda: 1,
    time_step,
    "_delay_expected_retailer_orders",
)


@component.add(name="td", comp_type="Constant", comp_subtype="Normal")
def td():
    return 10


@component.add(
    name="planned Temporary RPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"average_rpi": 1, "percentage_of_average_rpi": 1},
)
def planned_temporary_rpi():
    return average_rpi() * percentage_of_average_rpi()


@component.add(name="usage period", comp_type="Constant", comp_subtype="Normal")
def usage_period():
    return 50


@component.add(name="PPI holding cost", comp_type="Constant", comp_subtype="Normal")
def ppi_holding_cost():
    return 0.07


@component.add(
    name="time 1",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 2, "td": 2, "initial_time": 2, "hd": 1},
)
def time_1():
    return if_then_else(
        np.logical_and(
            time() >= initial_time() + td(), time() <= initial_time() + hd() + td()
        ),
        lambda: 1,
        lambda: 0,
    )


@component.add(name="Kc", comp_type="Constant", comp_subtype="Normal")
def kc():
    return 1


@component.add(
    name="W cost",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "wi": 1,
        "wi_holding_cost": 1,
        "t1": 1,
        "shipment_to_retailer": 1,
        "w_transportation_cost": 1,
    },
)
def w_cost():
    return (
        wi() * wi_holding_cost() / t1()
        + shipment_to_retailer() * w_transportation_cost()
    )


@component.add(name="Kd", comp_type="Constant", comp_subtype="Normal")
def kd():
    return 1


@component.add(name="Km1", comp_type="Constant", comp_subtype="Normal")
def km1():
    return 0


@component.add(
    name="recycling time",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_1": 1, "initial_recycling_time": 2, "increase_of_time": 1},
)
def recycling_time():
    return if_then_else(
        time_1() == 1,
        lambda: initial_recycling_time() * (1 + increase_of_time()),
        lambda: initial_recycling_time(),
    )


@component.add(name="Km3", comp_type="Constant", comp_subtype="Normal")
def km3():
    return 1


@component.add(name="Km4", comp_type="Constant", comp_subtype="Normal")
def km4():
    return 0


@component.add(
    name="wholesaler orders",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "expected_retailer_orders": 1,
        "adjust_time_of_wi": 1,
        "discrepancy_of_wi": 1,
    },
)
def wholesaler_orders():
    return expected_retailer_orders() + discrepancy_of_wi() / adjust_time_of_wi()


@component.add(
    name="initial recycling time", comp_type="Constant", comp_subtype="Normal"
)
def initial_recycling_time():
    return 1


@component.add(name="Kppi", comp_type="Constant", comp_subtype="Normal")
def kppi():
    return 0


@component.add(name="WI holding cost", comp_type="Constant", comp_subtype="Normal")
def wi_holding_cost():
    return 0.6


@component.add(
    name="material can be recycled",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"m_units": 1, "upi_disassembly_rate": 1},
)
def material_can_be_recycled():
    return m_units() * upi_disassembly_rate()


@component.add(name="RMSI holding cost", comp_type="Constant", comp_subtype="Normal")
def rmsi_holding_cost():
    return 0.01


@component.add(name="UPI holding cost", comp_type="Constant", comp_subtype="Normal")
def upi_holding_cost():
    return 0.8


@component.add(name="initial process time", comp_type="Constant", comp_subtype="Normal")
def initial_process_time():
    return 1


@component.add(
    name="Profit per week",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "profit": 1,
        "c_cost": 1,
        "d_cost": 1,
        "m_cost": 1,
        "pp_cost": 1,
        "r_cost": 1,
        "rms_cost": 1,
        "w_cost": 1,
    },
)
def profit_per_week():
    return (
        profit()
        - c_cost()
        - d_cost()
        - m_cost()
        - pp_cost()
        - r_cost()
        - rms_cost()
        - w_cost()
    )


@component.add(
    name="initial adjust time of WI", comp_type="Constant", comp_subtype="Normal"
)
def initial_adjust_time_of_wi():
    return 3


@component.add(
    name="time 3",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 2, "td": 2, "initial_time": 2, "hd": 2, "hrec": 1},
)
def time_3():
    return if_then_else(
        np.logical_and(
            time() >= initial_time() + td() + hd(),
            time() <= initial_time() + hd() + td() + hrec(),
        ),
        lambda: 1,
        lambda: 0,
    )


@component.add(
    name="time 2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "td": 1, "initial_time": 1, "hd": 1},
)
def time_2():
    return if_then_else(time() <= initial_time() + hd() + td(), lambda: 1, lambda: 0)


@component.add(name="recycling cost", comp_type="Constant", comp_subtype="Normal")
def recycling_cost():
    return 0.1


@component.add(
    name="W transportation cost", comp_type="Constant", comp_subtype="Normal"
)
def w_transportation_cost():
    return 1


@component.add(
    name="total amount of the part",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"no_units": 1, "time_step": 1, "total_pr": 1},
)
def total_amount_of_the_part():
    return no_units() * time_step() * total_pr()


@component.add(
    name="w5",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "adjust_time_for_mi": 2,
        "expected_wholesaler_orders": 2,
        "discrepancy_of_mi": 2,
        "reduction_of_production_rate": 1,
        "wholesaler_orders_backlogs": 1,
        "high_percentage_offered_by_contracted_manufacturer": 1,
        "mi": 1,
        "time_3": 1,
        "shipment_time_to_wholesaler": 1,
    },
)
def w5():
    return if_then_else(
        time_1() == 1,
        lambda: (1 - reduction_of_production_rate())
        * (expected_wholesaler_orders() + discrepancy_of_mi() / adjust_time_for_mi()),
        lambda: if_then_else(
            time_3() == 1,
            lambda: (1 - high_percentage_offered_by_contracted_manufacturer())
            * expected_wholesaler_orders()
            + discrepancy_of_mi() / adjust_time_for_mi(),
            lambda: np.maximum(
                np.minimum(mi(), wholesaler_orders_backlogs())
                / shipment_time_to_wholesaler(),
                0,
            ),
        ),
    )


@component.add(name="remanufacturing cost", comp_type="Constant", comp_subtype="Normal")
def remanufacturing_cost():
    return 2.2


@component.add(name="RMI holding cost", comp_type="Constant", comp_subtype="Normal")
def rmi_holding_cost():
    return 0.005


@component.add(name="N1 units", comp_type="Constant", comp_subtype="Normal")
def n1_units():
    return 1


@component.add(
    name="total profit",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_total_profit": 1},
    other_deps={
        "_integ_total_profit": {
            "initial": {},
            "step": {
                "profit": 1,
                "c_cost": 1,
                "d_cost": 1,
                "m_cost": 1,
                "pp_cost": 1,
                "r_cost": 1,
                "rms_cost": 1,
                "w_cost": 1,
            },
        }
    },
)
def total_profit():
    return _integ_total_profit()


_integ_total_profit = Integ(
    lambda: profit()
    - c_cost()
    - d_cost()
    - m_cost()
    - pp_cost()
    - r_cost()
    - rms_cost()
    - w_cost(),
    lambda: 0,
    "_integ_total_profit",
)


@component.add(
    name="profit",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"price": 1, "sales_1": 1},
)
def profit():
    return price() * sales_1()


@component.add(name="production cost", comp_type="Constant", comp_subtype="Normal")
def production_cost():
    return 32


@component.add(name="Tm", comp_type="Constant", comp_subtype="Normal")
def tm():
    return 4


@component.add(
    name="R cost",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ri": 1,
        "ri_holding_cost": 1,
        "t1": 1,
        "sales_1": 1,
        "r_delivery_cost": 1,
    },
)
def r_cost():
    return ri() * ri_holding_cost() / t1() + sales_1() * r_delivery_cost()


@component.add(
    name="total ppr",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"part_production_rate": 1, "part_production_rate1": 1},
)
def total_ppr():
    return part_production_rate() + part_production_rate1()


@component.add(name="RT holding cost", comp_type="Constant", comp_subtype="Normal")
def rt_holding_cost():
    return 0.005


@component.add(
    name="RMS cost",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "coming_rate_of_raw_material": 1,
        "making_cost": 1,
        "rmsi": 1,
        "rmsi_holding_cost": 1,
        "t1": 1,
        "purchase_rate_of_new_material": 1,
        "rms_transportation_cost": 1,
    },
)
def rms_cost():
    return (
        coming_rate_of_raw_material() * making_cost()
        + rmsi() * rmsi_holding_cost() / t1()
        + purchase_rate_of_new_material() * rms_transportation_cost()
    )


@component.add(name='"%increase of time"', comp_type="Constant", comp_subtype="Normal")
def increase_of_time():
    return 0.3


@component.add(
    name="discrepancy of MI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"desired_mi": 1, "mi": 1},
)
def discrepancy_of_mi():
    return np.maximum(desired_mi() - mi(), 0)


@component.add(
    name="adjust time for MI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_1": 1, "initial_adjust_time_for_mi": 2, "increase_of_time": 1},
)
def adjust_time_for_mi():
    return if_then_else(
        time_1() == 1,
        lambda: initial_adjust_time_for_mi() * (1 + increase_of_time()),
        lambda: initial_adjust_time_for_mi(),
    )


@component.add(
    name="adjust time for remote MI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "initial_adjust_time_for_remote_mi": 2,
        "increase_of_time": 1,
    },
)
def adjust_time_for_remote_mi():
    return if_then_else(
        time_1() == 1,
        lambda: initial_adjust_time_for_remote_mi() * (1 + increase_of_time()),
        lambda: initial_adjust_time_for_remote_mi(),
    )


@component.add(
    name="adjust time of CI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_1": 1, "initial_adjust_time_of_ci": 2, "increase_of_time": 1},
)
def adjust_time_of_ci():
    return if_then_else(
        time_1() == 1,
        lambda: initial_adjust_time_of_ci() * (1 + increase_of_time()),
        lambda: initial_adjust_time_of_ci(),
    )


@component.add(
    name="adjust time of parts",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_1": 1, "initial_adjust_time_of_parts": 2, "increase_of_time": 1},
)
def adjust_time_of_parts():
    return if_then_else(
        time_1() == 1,
        lambda: initial_adjust_time_of_parts() * (1 + increase_of_time()),
        lambda: initial_adjust_time_of_parts(),
    )


@component.add(
    name="adjust time of PPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_1": 1, "initial_adjust_time_of_ppi": 2, "increase_of_time": 1},
)
def adjust_time_of_ppi():
    return if_then_else(
        time_1() == 1,
        lambda: initial_adjust_time_of_ppi() * (1 + increase_of_time()),
        lambda: initial_adjust_time_of_ppi(),
    )


@component.add(
    name="retailer orders reduction rate",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"shipment_to_retailer": 1},
)
def retailer_orders_reduction_rate():
    return shipment_to_retailer()


@component.add(
    name="adjust time of Temporary PPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "initial_adjust_time_of_temporary_ppi": 2,
        "increase_of_time": 1,
    },
)
def adjust_time_of_temporary_ppi():
    return if_then_else(
        time_1() == 1,
        lambda: initial_adjust_time_of_temporary_ppi() * (1 + increase_of_time()),
        lambda: initial_adjust_time_of_temporary_ppi(),
    )


@component.add(
    name="RPI",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_rpi": 1},
    other_deps={
        "_integ_rpi": {
            "initial": {},
            "step": {"remanufacturing_rate": 1, "purchase_rate_of_rpi": 1},
        }
    },
)
def rpi():
    return _integ_rpi()


_integ_rpi = Integ(
    lambda: remanufacturing_rate() - purchase_rate_of_rpi(), lambda: 0, "_integ_rpi"
)


@component.add(
    name="adjust time of UPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_1": 1, "initial_adjust_time_of_upi": 2, "increase_of_time": 1},
)
def adjust_time_of_upi():
    return if_then_else(
        time_1() == 1,
        lambda: initial_adjust_time_of_upi() * (1 + increase_of_time()),
        lambda: initial_adjust_time_of_upi(),
    )


@component.add(
    name="MI",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_mi": 1},
    other_deps={
        "_integ_mi": {
            "initial": {},
            "step": {
                "fill_rate_for_mi": 1,
                "production_rate": 1,
                "shipment_to_wholesaler": 1,
            },
        }
    },
)
def mi():
    return _integ_mi()


_integ_mi = Integ(
    lambda: fill_rate_for_mi() + production_rate() - shipment_to_wholesaler(),
    lambda: 0,
    "_integ_mi",
)


@component.add(
    name="desired CI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"expected_purchase_rate": 1, "cover_time_of_ci": 1},
)
def desired_ci():
    return expected_purchase_rate() * cover_time_of_ci()


@component.add(name="average PPI", comp_type="Constant", comp_subtype="Normal")
def average_ppi():
    return 24734


@component.add(name="average RPI", comp_type="Constant", comp_subtype="Normal")
def average_rpi():
    return 19044


@component.add(
    name="number of shifts for hrec", comp_type="Constant", comp_subtype="Normal"
)
def number_of_shifts_for_hrec():
    return 2


@component.add(
    name="CM1 CM2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "adjust_time_for_mi": 2,
        "expected_wholesaler_orders": 2,
        "discrepancy_of_mi": 2,
        "reduction_of_production_rate": 1,
    },
)
def cm1_cm2():
    return if_then_else(
        time_1() == 1,
        lambda: (1 - reduction_of_production_rate())
        * (expected_wholesaler_orders() + discrepancy_of_mi() / adjust_time_for_mi()),
        lambda: expected_wholesaler_orders()
        + discrepancy_of_mi() / adjust_time_for_mi(),
    )


@component.add(
    name="CM3",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "reduction_of_production_rate": 1,
        "adjust_time_for_mi": 2,
        "expected_wholesaler_orders": 2,
        "discrepancy_of_mi": 2,
        "percentage_offered_by_contracted_manufacturer": 2,
    },
)
def cm3():
    return if_then_else(
        time_1() == 1,
        lambda: (1 - reduction_of_production_rate())
        * (
            (1 - percentage_offered_by_contracted_manufacturer())
            * expected_wholesaler_orders()
            + discrepancy_of_mi() / adjust_time_for_mi()
        ),
        lambda: (1 - percentage_offered_by_contracted_manufacturer())
        * expected_wholesaler_orders()
        + discrepancy_of_mi() / adjust_time_for_mi(),
    )


@component.add(
    name="CM4",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "adjust_time_for_mi": 2,
        "expected_wholesaler_orders": 2,
        "discrepancy_of_mi": 2,
        "reduction_of_production_rate": 1,
        "percentage_offered_by_contracted_manufacturer": 1,
    },
)
def cm4():
    return if_then_else(
        time_1() == 1,
        lambda: (1 - reduction_of_production_rate())
        * (expected_wholesaler_orders() + discrepancy_of_mi() / adjust_time_for_mi()),
        lambda: (1 - percentage_offered_by_contracted_manufacturer())
        * expected_wholesaler_orders()
        + discrepancy_of_mi() / adjust_time_for_mi(),
    )


@component.add(
    name="CM5",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "adjust_time_for_mi": 2,
        "expected_wholesaler_orders": 2,
        "discrepancy_of_mi": 2,
        "reduction_of_production_rate": 1,
        "mi_capacity": 1,
        "time_3": 1,
        "number_of_shifts_for_hrec": 1,
    },
)
def cm5():
    return if_then_else(
        time_1() == 1,
        lambda: (1 - reduction_of_production_rate())
        * (expected_wholesaler_orders() + discrepancy_of_mi() / adjust_time_for_mi()),
        lambda: if_then_else(
            time_3() == 1,
            lambda: mi_capacity() * number_of_shifts_for_hrec(),
            lambda: expected_wholesaler_orders()
            + discrepancy_of_mi() / adjust_time_for_mi(),
        ),
    )


@component.add(
    name="Parts to remanufacture",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_parts_to_remanufacture": 1},
    other_deps={
        "_integ_parts_to_remanufacture": {
            "initial": {},
            "step": {
                "fill_rate_of_rpi": 1,
                "part_can_be_remanufatured": 1,
                "remanufacturing_rate": 1,
            },
        }
    },
)
def parts_to_remanufacture():
    return _integ_parts_to_remanufacture()


_integ_parts_to_remanufacture = Integ(
    lambda: fill_rate_of_rpi() + part_can_be_remanufatured() - remanufacturing_rate(),
    lambda: 0,
    "_integ_parts_to_remanufacture",
)


@component.add(
    name="initial adjust time for MI", comp_type="Constant", comp_subtype="Normal"
)
def initial_adjust_time_for_mi():
    return 4


@component.add(
    name="initial adjust time for remote MI",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_adjust_time_for_remote_mi():
    return 4


@component.add(
    name="collection time",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_1": 1, "initial_collection_time": 2, "increase_of_time": 1},
)
def collection_time():
    return if_then_else(
        time_1() == 1,
        lambda: initial_collection_time() * (1 + increase_of_time()),
        lambda: initial_collection_time(),
    )


@component.add(
    name="percentage of average RPI", comp_type="Constant", comp_subtype="Normal"
)
def percentage_of_average_rpi():
    return 1


@component.add(
    name="percentage offered by contracted manufacturer",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "km3": 1,
        "low_percentage_offered_by_contracted_manufacturer": 2,
        "high_percentage_offered_by_contracted_manufacturer": 2,
        "time_1": 1,
        "km4": 1,
        "time_3": 1,
    },
)
def percentage_offered_by_contracted_manufacturer():
    return if_then_else(
        km3() == 1,
        lambda: if_then_else(
            time_1() == 0,
            lambda: low_percentage_offered_by_contracted_manufacturer(),
            lambda: high_percentage_offered_by_contracted_manufacturer(),
        ),
        lambda: if_then_else(
            km4() == 1,
            lambda: if_then_else(
                time_3() == 0,
                lambda: low_percentage_offered_by_contracted_manufacturer(),
                lambda: high_percentage_offered_by_contracted_manufacturer(),
            ),
            lambda: 0,
        ),
    )


@component.add(name="cover time of CI", comp_type="Constant", comp_subtype="Normal")
def cover_time_of_ci():
    return 2


@component.add(name="cover time of MI", comp_type="Constant", comp_subtype="Normal")
def cover_time_of_mi():
    return 4


@component.add(name="cover time of PPI", comp_type="Constant", comp_subtype="Normal")
def cover_time_of_ppi():
    return 2


@component.add(name="cover time of RPI", comp_type="Constant", comp_subtype="Normal")
def cover_time_of_rpi():
    return 2


@component.add(name="cover time of UPI", comp_type="Constant", comp_subtype="Normal")
def cover_time_of_upi():
    return 2


@component.add(
    name="initial collection time", comp_type="Constant", comp_subtype="Normal"
)
def initial_collection_time():
    return 1


@component.add(
    name="PPI",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_ppi": 1},
    other_deps={
        "_integ_ppi": {
            "initial": {},
            "step": {
                "fill_rate_for_ppi": 1,
                "part_production_rate": 1,
                "purchase_rate_of_new_part": 1,
            },
        }
    },
)
def ppi():
    return _integ_ppi()


_integ_ppi = Integ(
    lambda: fill_rate_for_ppi() + part_production_rate() - purchase_rate_of_new_part(),
    lambda: 0,
    "_integ_ppi",
)


@component.add(
    name="production rate",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "total_amount_of_parts_to_end_products": 2,
        "cm5": 1,
        "time_step": 1,
        "km5": 1,
        "km3": 1,
        "km4": 1,
        "cm3": 1,
        "km1": 1,
        "expected_wholesaler_orders": 3,
        "km2": 1,
        "mi_capacity": 1,
        "cm4": 1,
        "time": 1,
        "k": 1,
        "adjust_time_for_mi": 3,
        "discrepancy_of_mi": 3,
        "initial_time": 1,
        "cm1_cm2": 2,
    },
)
def production_rate():
    return if_then_else(
        total_amount_of_parts_to_end_products() > 0,
        lambda: if_then_else(
            time() == initial_time(),
            lambda: expected_wholesaler_orders()
            + discrepancy_of_mi() / adjust_time_for_mi(),
            lambda: np.minimum(
                total_amount_of_parts_to_end_products() / time_step(),
                np.minimum(
                    mi_capacity(),
                    if_then_else(
                        k() == 0,
                        lambda: expected_wholesaler_orders()
                        + discrepancy_of_mi() / adjust_time_for_mi(),
                        lambda: if_then_else(
                            km1() == 1,
                            lambda: cm1_cm2(),
                            lambda: if_then_else(
                                km2() == 1,
                                lambda: cm1_cm2(),
                                lambda: if_then_else(
                                    km3() == 1,
                                    lambda: cm3(),
                                    lambda: if_then_else(
                                        km4() == 1,
                                        lambda: cm4(),
                                        lambda: if_then_else(
                                            km5() == 1,
                                            lambda: cm5(),
                                            lambda: expected_wholesaler_orders()
                                            + discrepancy_of_mi()
                                            / adjust_time_for_mi(),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
        lambda: 0,
    )


@component.add(
    name="demand backlog reduction rate",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"sales_1": 1},
)
def demand_backlog_reduction_rate():
    return sales_1()


@component.add(
    name="total amount of parts to end products",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_total_amount_of_parts_to_end_products": 1},
    other_deps={
        "_integ_total_amount_of_parts_to_end_products": {
            "initial": {},
            "step": {
                "purchase_rate_of_new_part_to_end_product": 1,
                "purchase_rate_of_rpi_to_end_product": 1,
                "production_rate": 1,
            },
        }
    },
)
def total_amount_of_parts_to_end_products():
    return _integ_total_amount_of_parts_to_end_products()


_integ_total_amount_of_parts_to_end_products = Integ(
    lambda: purchase_rate_of_new_part_to_end_product()
    + purchase_rate_of_rpi_to_end_product()
    - production_rate(),
    lambda: 0,
    "_integ_total_amount_of_parts_to_end_products",
)


@component.add(
    name="desired MI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"cover_time_of_mi": 1, "expected_wholesaler_orders": 1},
)
def desired_mi():
    return cover_time_of_mi() * expected_wholesaler_orders()


@component.add(
    name="desired new parts to end product",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"desired_mi": 1},
)
def desired_new_parts_to_end_product():
    return desired_mi()


@component.add(
    name="desired of UPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"expected_usedproduct_demand_rate": 1, "cover_time_of_upi": 1},
)
def desired_of_upi():
    return expected_usedproduct_demand_rate() * cover_time_of_upi()


@component.add(
    name="desired PPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"cover_time_of_ppi": 1, "expected_purchase_rate_of_new_part": 1},
)
def desired_ppi():
    return cover_time_of_ppi() * expected_purchase_rate_of_new_part()


@component.add(
    name="purchase time",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_1": 1, "initial_purchase_time": 2, "increase_of_time": 1},
)
def purchase_time():
    return if_then_else(
        time_1() == 1,
        lambda: initial_purchase_time() * (1 + increase_of_time()),
        lambda: initial_purchase_time(),
    )


@component.add(
    name="purchase time of new part", comp_type="Constant", comp_subtype="Normal"
)
def purchase_time_of_new_part():
    return 1


@component.add(
    name="wholesaler orders reduction rate",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"shipment_to_wholesaler": 1},
)
def wholesaler_orders_reduction_rate():
    return shipment_to_wholesaler()


@component.add(
    name="discrepancy of CI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"desired_ci": 1, "ci": 1},
)
def discrepancy_of_ci():
    return np.maximum(desired_ci() - ci(), 0)


@component.add(
    name="discrepancy of parts to end product",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "desired_new_parts_to_end_product": 1,
        "total_amount_of_parts_to_end_products": 1,
    },
)
def discrepancy_of_parts_to_end_product():
    return np.maximum(
        desired_new_parts_to_end_product() - total_amount_of_parts_to_end_products(), 0
    )


@component.add(
    name="discrepancy of PPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"desired_ppi": 1, "ppi": 1},
)
def discrepancy_of_ppi():
    return np.maximum(desired_ppi() - ppi(), 0)


@component.add(
    name="remanufacturing time",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_1": 1, "initial_remanufacturing_time": 2, "increase_of_time": 1},
)
def remanufacturing_time():
    return if_then_else(
        time_1() == 1,
        lambda: initial_remanufacturing_time() * (1 + increase_of_time()),
        lambda: initial_remanufacturing_time(),
    )


@component.add(
    name='"should satisfy rate of used-products"',
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "kusedprod": 1,
        "discrepancy_of_upi": 2,
        "time_1": 1,
        "expected_usedproduct_demand_rate": 2,
        "adjust_time_of_upi": 2,
    },
)
def should_satisfy_rate_of_usedproducts():
    return if_then_else(
        kusedprod() == 1,
        lambda: if_then_else(
            time_1() == 1,
            lambda: 0,
            lambda: np.maximum(
                expected_usedproduct_demand_rate()
                + discrepancy_of_upi() / adjust_time_of_upi(),
                0,
            ),
        ),
        lambda: np.maximum(
            expected_usedproduct_demand_rate()
            + discrepancy_of_upi() / adjust_time_of_upi(),
            0,
        ),
    )


@component.add(
    name="discrepancy of Temporary PPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"planned_temporary_ppi": 2, "temporary_ppi": 2},
)
def discrepancy_of_temporary_ppi():
    return if_then_else(
        planned_temporary_ppi() - temporary_ppi() >= 0,
        lambda: planned_temporary_ppi() - temporary_ppi(),
        lambda: 0,
    )


@component.add(
    name="Temporary RPI",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_temporary_rpi": 1},
    other_deps={
        "_integ_temporary_rpi": {
            "initial": {},
            "step": {"part_can_be_remanufatured1": 1, "fill_rate_of_rpi": 1},
        }
    },
)
def temporary_rpi():
    return _integ_temporary_rpi()


_integ_temporary_rpi = Integ(
    lambda: part_can_be_remanufatured1() - fill_rate_of_rpi(),
    lambda: 0,
    "_integ_temporary_rpi",
)


@component.add(
    name="discrepancy of UPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"desired_of_upi": 1, "upi_disassembly_rate": 1},
)
def discrepancy_of_upi():
    return np.maximum(desired_of_upi() - upi_disassembly_rate(), 0)


@component.add(
    name="Temporary PPI",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_temporary_ppi": 1},
    other_deps={
        "_integ_temporary_ppi": {
            "initial": {},
            "step": {"part_production_rate1": 1, "fill_rate_for_ppi": 1},
        }
    },
)
def temporary_ppi():
    return _integ_temporary_ppi()


_integ_temporary_ppi = Integ(
    lambda: part_production_rate1() - fill_rate_for_ppi(),
    lambda: 0,
    "_integ_temporary_ppi",
)


@component.add(
    name="low percentage offered by contracted manufacturer",
    comp_type="Constant",
    comp_subtype="Normal",
)
def low_percentage_offered_by_contracted_manufacturer():
    return 0.5


@component.add(
    name="part production rate1",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "kp": 1,
        "time_1": 1,
        "discrepancy_of_temporary_ppi": 1,
        "adjust_time_of_temporary_ppi": 1,
    },
)
def part_production_rate1():
    return if_then_else(
        kp() == 0,
        lambda: 0,
        lambda: if_then_else(
            time_1() == 1,
            lambda: np.maximum(discrepancy_of_temporary_ppi(), 0)
            / adjust_time_of_temporary_ppi(),
            lambda: 0,
        ),
    )


@component.add(
    name="shipment time to wholesaler",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "initial_shipment_time_to_wholesaler": 2,
        "increase_of_time": 1,
    },
)
def shipment_time_to_wholesaler():
    return if_then_else(
        time_1() == 1,
        lambda: initial_shipment_time_to_wholesaler() * (1 + increase_of_time()),
        lambda: initial_shipment_time_to_wholesaler(),
    )


@component.add(
    name="initial purchase time", comp_type="Constant", comp_subtype="Normal"
)
def initial_purchase_time():
    return 1


@component.add(
    name="initial remanufacturing time", comp_type="Constant", comp_subtype="Normal"
)
def initial_remanufacturing_time():
    return 2


@component.add(
    name="used product amount",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_used_product_amount": 1},
    other_deps={
        "_integ_used_product_amount": {
            "initial": {},
            "step": {"coming_rate_1": 1, "expected_collection_rate": 1},
        }
    },
)
def used_product_amount():
    return _integ_used_product_amount()


_integ_used_product_amount = Integ(
    lambda: coming_rate_1() - expected_collection_rate(),
    lambda: 0,
    "_integ_used_product_amount",
)


@component.add(
    name="shipment to wholesaler by contracted manufacturer",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "km3": 1,
        "shipment_offered_by_contracted_manufacturer": 1,
        "km4": 1,
        "expected_wholesaler_orders": 2,
        "high_percentage_offered_by_contracted_manufacturer": 1,
        "time_1": 1,
        "low_percentage_offered_by_contracted_manufacturer": 1,
        "time_3": 1,
    },
)
def shipment_to_wholesaler_by_contracted_manufacturer():
    return if_then_else(
        km3() == 1,
        lambda: shipment_offered_by_contracted_manufacturer(),
        lambda: if_then_else(
            km4() == 1,
            lambda: if_then_else(
                time_1() == 1,
                lambda: 0,
                lambda: if_then_else(
                    time_3() == 1,
                    lambda: expected_wholesaler_orders()
                    * high_percentage_offered_by_contracted_manufacturer(),
                    lambda: expected_wholesaler_orders()
                    * low_percentage_offered_by_contracted_manufacturer(),
                ),
            ),
            lambda: 0,
        ),
    )


@component.add(
    name="initial service period of temporary PPI",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_service_period_of_temporary_ppi():
    return 2


@component.add(
    name="service periods of Temporary PPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "initial_service_period_of_temporary_ppi": 2,
        "increase_of_time": 1,
    },
)
def service_periods_of_temporary_ppi():
    return if_then_else(
        time_1() == 1,
        lambda: initial_service_period_of_temporary_ppi() * (1 + increase_of_time()),
        lambda: initial_service_period_of_temporary_ppi(),
    )


@component.add(
    name="fill rate for PPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "kp": 1,
        "time_2": 1,
        "service_periods_of_temporary_ppi": 1,
        "temporary_ppi": 1,
    },
)
def fill_rate_for_ppi():
    return if_then_else(
        kp() == 0,
        lambda: 0,
        lambda: if_then_else(
            time_2() == 1,
            lambda: 0,
            lambda: np.maximum(temporary_ppi() / service_periods_of_temporary_ppi(), 0),
        ),
    )


@component.add(
    name="fill rate of RPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "kd": 1,
        "time_2": 1,
        "temporary_rpi": 1,
        "service_periods_of_temporary_rpi": 1,
    },
)
def fill_rate_of_rpi():
    return if_then_else(
        kd() == 0,
        lambda: 0,
        lambda: if_then_else(
            time_2() == 1,
            lambda: 0,
            lambda: np.maximum(temporary_rpi() / service_periods_of_temporary_rpi(), 0),
        ),
    )


@component.add(
    name="high percentage offered by contracted manufacturer",
    comp_type="Constant",
    comp_subtype="Normal",
)
def high_percentage_offered_by_contracted_manufacturer():
    return 0.1


@component.add(
    name="part production rate",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "kppi": 1,
        "time_1": 1,
        "adjust_time_of_ppi": 2,
        "expected_purchase_rate_of_new_part": 2,
        "discrepancy_of_ppi": 2,
    },
)
def part_production_rate():
    return if_then_else(
        kppi() == 1,
        lambda: if_then_else(
            time_1() == 1,
            lambda: 0,
            lambda: np.maximum(
                expected_purchase_rate_of_new_part()
                + discrepancy_of_ppi() / adjust_time_of_ppi(),
                0,
            ),
        ),
        lambda: np.maximum(
            expected_purchase_rate_of_new_part()
            + discrepancy_of_ppi() / adjust_time_of_ppi(),
            0,
        ),
    )


@component.add(
    name="service periods of temporary RPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "initial_service_period_of_temporary_rpi": 2,
        "increase_of_time": 1,
    },
)
def service_periods_of_temporary_rpi():
    return if_then_else(
        time_1() == 1,
        lambda: initial_service_period_of_temporary_rpi() * (1 + increase_of_time()),
        lambda: initial_service_period_of_temporary_rpi(),
    )


@component.add(
    name="initial adjust time of CI", comp_type="Constant", comp_subtype="Normal"
)
def initial_adjust_time_of_ci():
    return 2


@component.add(
    name="initial adjust time of parts", comp_type="Constant", comp_subtype="Normal"
)
def initial_adjust_time_of_parts():
    return 1


@component.add(
    name="initial adjust time of PPI", comp_type="Constant", comp_subtype="Normal"
)
def initial_adjust_time_of_ppi():
    return 4


@component.add(
    name="remanufacturing rate",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"parts_to_remanufacture": 1, "remanufacturing_time": 1},
)
def remanufacturing_rate():
    return parts_to_remanufacture() / remanufacturing_time()


@component.add(
    name="purchase rate of new part",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ppi": 2,
        "no_units": 1,
        "purchase_time_of_new_part": 1,
        "adjust_time_of_parts": 1,
        "discrepancy_of_parts_to_end_product": 1,
        "purchase_rate_of_rpi": 1,
    },
)
def purchase_rate_of_new_part():
    return if_then_else(
        ppi() > 0,
        lambda: np.minimum(
            ppi() / purchase_time_of_new_part(),
            np.maximum(
                discrepancy_of_parts_to_end_product() / adjust_time_of_parts()
                - purchase_rate_of_rpi(),
                0,
            )
            * no_units(),
        ),
        lambda: 0,
    )


@component.add(
    name="initial adjust time of Temporary PPI",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_adjust_time_of_temporary_ppi():
    return 4


@component.add(
    name="initial service period of temporary RPI",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_service_period_of_temporary_rpi():
    return 1


@component.add(
    name="initial adjust time of UPI", comp_type="Constant", comp_subtype="Normal"
)
def initial_adjust_time_of_upi():
    return 4


@component.add(
    name="initial shipment time to wholesaler",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_shipment_time_to_wholesaler():
    return 1


@component.add(
    name="part can be remanufatured1",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"kd": 1, "disassembly_rate1": 1, "time_1": 1, "disassembly_rate": 1},
)
def part_can_be_remanufatured1():
    return if_then_else(
        kd() == 0,
        lambda: 0,
        lambda: if_then_else(
            time_1() == 1,
            lambda: np.minimum(disassembly_rate1(), disassembly_rate()),
            lambda: 0,
        ),
    )


@component.add(
    name="w4",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "reduction_of_production_rate": 1,
        "adjust_time_for_mi": 1,
        "expected_wholesaler_orders": 1,
        "discrepancy_of_mi": 1,
        "percentage_offered_by_contracted_manufacturer": 1,
        "wholesaler_orders_backlogs": 1,
        "shipment_time_to_wholesaler": 1,
        "mi": 1,
    },
)
def w4():
    return if_then_else(
        time_1() == 1,
        lambda: (1 - reduction_of_production_rate())
        * (
            (1 - percentage_offered_by_contracted_manufacturer())
            * expected_wholesaler_orders()
            + discrepancy_of_mi() / adjust_time_for_mi()
        ),
        lambda: np.maximum(
            np.minimum(mi(), wholesaler_orders_backlogs())
            / shipment_time_to_wholesaler(),
            0,
        ),
    )


@component.add(
    name="WI",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_wi": 1},
    other_deps={
        "_integ_wi": {
            "initial": {},
            "step": {
                "shipment_to_wholesaler": 1,
                "shipment_to_wholesaler_by_contracted_manufacturer": 1,
                "shipment_to_retailer": 1,
            },
        }
    },
)
def wi():
    return _integ_wi()


_integ_wi = Integ(
    lambda: shipment_to_wholesaler()
    + shipment_to_wholesaler_by_contracted_manufacturer()
    - shipment_to_retailer(),
    lambda: 0,
    "_integ_wi",
)


@component.add(
    name="shipment offered by contracted manufacturer",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "expected_wholesaler_orders": 1,
        "percentage_offered_by_contracted_manufacturer": 1,
    },
)
def shipment_offered_by_contracted_manufacturer():
    return (
        expected_wholesaler_orders() * percentage_offered_by_contracted_manufacturer()
    )


@component.add(
    name="production rate 1",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "km2": 1,
        "time_step": 1,
        "discrepancy_of_remote_mi": 1,
        "time_1": 1,
        "total_amount_of_parts_to_end_products": 1,
        "production_rate": 1,
        "adjust_time_for_remote_mi": 1,
    },
)
def production_rate_1():
    return if_then_else(
        km2() == 1,
        lambda: if_then_else(
            time_1() == 1,
            lambda: 0,
            lambda: np.minimum(
                total_amount_of_parts_to_end_products() / time_step()
                - production_rate(),
                np.maximum(discrepancy_of_remote_mi(), 0) / adjust_time_for_remote_mi(),
            ),
        ),
        lambda: 0,
    )


@component.add(
    name="planned Temporary PPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"average_ppi": 1, "percentage_of_average_ppi": 1},
)
def planned_temporary_ppi():
    return average_ppi() * percentage_of_average_ppi()


@component.add(
    name="shipment to wholesaler",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "k": 1,
        "wholesaler_orders_backlogs": 1,
        "shipment_time_to_wholesaler": 1,
        "mi": 1,
        "km5": 1,
        "w4": 1,
        "km3": 1,
        "w1_2_3": 1,
        "km4": 1,
        "w5": 1,
        "km2": 1,
        "km1": 1,
    },
)
def shipment_to_wholesaler():
    return if_then_else(
        k() == 0,
        lambda: np.maximum(
            np.minimum(mi(), wholesaler_orders_backlogs())
            / shipment_time_to_wholesaler(),
            0,
        ),
        lambda: if_then_else(
            np.logical_or(km1() == 1, np.logical_or(km2() == 1, km3() == 1)),
            lambda: w1_2_3(),
            lambda: if_then_else(
                km4() == 1,
                lambda: w4(),
                lambda: if_then_else(km5() == 1, lambda: w5(), lambda: 0),
            ),
        ),
    )


@component.add(
    name="w1 2 3",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "mi": 1,
        "wholesaler_orders_backlogs": 1,
        "shipment_time_to_wholesaler": 1,
    },
)
def w1_2_3():
    return np.maximum(
        np.minimum(mi(), wholesaler_orders_backlogs()) / shipment_time_to_wholesaler(),
        0,
    )


@component.add(
    name="purchase rate of RPI",
    units="part/week",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "no_units": 1,
        "discrepancy_of_parts_to_end_product": 1,
        "rpi": 1,
        "adjust_time_of_parts": 1,
    },
)
def purchase_rate_of_rpi():
    return (
        np.minimum(no_units() * discrepancy_of_parts_to_end_product(), rpi())
        / adjust_time_of_parts()
    )


@component.add(
    name="percentage of average PPI", comp_type="Constant", comp_subtype="Normal"
)
def percentage_of_average_ppi():
    return 1


@component.add(
    name="part can be remanufatured",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "krpi": 1,
        "time_1": 1,
        "disassembly_rate": 1,
        "part_can_be_remanufatured1": 1,
    },
)
def part_can_be_remanufatured():
    return if_then_else(
        krpi() == 1,
        lambda: if_then_else(
            time_1() == 1,
            lambda: 0,
            lambda: disassembly_rate() - part_can_be_remanufatured1(),
        ),
        lambda: 0,
    )


@component.add(
    name="discrepancy of remote MI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"planned_remote_mi": 1, "remote_mi": 1},
)
def discrepancy_of_remote_mi():
    return np.maximum(0, planned_remote_mi() - remote_mi())


@component.add(
    name='"%reduction of demand"', comp_type="Constant", comp_subtype="Normal"
)
def reduction_of_demand():
    return 0.5


@component.add(
    name="discrepancy of Temporary CI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"planned_temporary_ci": 1, "temporary_ci": 1},
)
def discrepancy_of_temporary_ci():
    return planned_temporary_ci() - temporary_ci()


@component.add(
    name="mean value",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "reduction_of_demand": 2,
        "initial_mean_value": 3,
        "time_3": 1,
    },
)
def mean_value():
    return if_then_else(
        time_1() == 1,
        lambda: (1 - reduction_of_demand()) * initial_mean_value(),
        lambda: if_then_else(
            time_3() == 1,
            lambda: (1 - 0.5 * reduction_of_demand()) * initial_mean_value(),
            lambda: initial_mean_value(),
        ),
    )


@component.add(name="N4", comp_type="Constant", comp_subtype="Normal")
def n4():
    return 1


@component.add(
    name="adjust time of RPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_1": 1, "initial_adjust_time_of_rpi": 2, "increase_of_time": 1},
)
def adjust_time_of_rpi():
    return if_then_else(
        time_1() == 1,
        lambda: initial_adjust_time_of_rpi() * (1 + increase_of_time()),
        lambda: initial_adjust_time_of_rpi(),
    )


@component.add(
    name="adjust time of Temporary CI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "initial_adjust_time_of_temporary_ci": 2,
        "increase_of_time": 1,
    },
)
def adjust_time_of_temporary_ci():
    return if_then_else(
        time_1() == 1,
        lambda: initial_adjust_time_of_temporary_ci() * (1 + increase_of_time()),
        lambda: initial_adjust_time_of_temporary_ci(),
    )


@component.add(name="RPn", comp_type="Constant", comp_subtype="Normal")
def rpn():
    return 1


@component.add(
    name="adjust time of Temporary RPI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "initial_adjust_time_of_temporary_rpi": 2,
        "increase_of_time": 1,
    },
)
def adjust_time_of_temporary_rpi():
    return if_then_else(
        time_1() == 1,
        lambda: initial_adjust_time_of_temporary_rpi() * (1 + increase_of_time()),
        lambda: initial_adjust_time_of_temporary_rpi(),
    )


@component.add(name="average CI", comp_type="Constant", comp_subtype="Normal")
def average_ci():
    return 12941


@component.add(name="average MI", comp_type="Constant", comp_subtype="Normal")
def average_mi():
    return 21596


@component.add(name="seed", comp_type="Constant", comp_subtype="Normal")
def seed():
    return 0.5


@component.add(
    name="CI",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_ci": 1},
    other_deps={
        "_integ_ci": {
            "initial": {},
            "step": {"collection_rate": 1, "fill_rate_for_ci": 1, "purchase_rate": 1},
        }
    },
)
def ci():
    return _integ_ci()


_integ_ci = Integ(
    lambda: collection_rate() + fill_rate_for_ci() - purchase_rate(),
    lambda: 0,
    "_integ_ci",
)


@component.add(
    name="collection rate",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "kci": 1,
        "time_1": 1,
        "expected_collection_rate": 2,
        "collection_rate_for_temporary_ci": 2,
    },
)
def collection_rate():
    return if_then_else(
        kci() == 1,
        lambda: if_then_else(
            time_1() == 1,
            lambda: 0,
            lambda: np.maximum(
                expected_collection_rate() - collection_rate_for_temporary_ci(), 0
            ),
        ),
        lambda: np.maximum(
            expected_collection_rate() - collection_rate_for_temporary_ci(), 0
        ),
    )


@component.add(
    name="collection rate for Temporary CI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"collection_rate1": 1, "expected_collection_rate": 1},
)
def collection_rate_for_temporary_ci():
    return np.minimum(collection_rate1(), expected_collection_rate())


@component.add(
    name="collection rate1",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "kc": 1,
        "discrepancy_of_temporary_ci": 1,
        "time_1": 1,
        "adjust_time_of_temporary_ci": 1,
    },
)
def collection_rate1():
    return if_then_else(
        kc() == 0,
        lambda: 0,
        lambda: if_then_else(
            time_1() == 1,
            lambda: np.maximum(discrepancy_of_temporary_ci(), 0)
            / adjust_time_of_temporary_ci(),
            lambda: 0,
        ),
    )


@component.add(
    name="shipment time to retailer",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "initial_shipment_time_to_retailer": 2,
        "increase_of_time": 1,
    },
)
def shipment_time_to_retailer():
    return if_then_else(
        time_1() == 1,
        lambda: initial_shipment_time_to_retailer() * (1 + increase_of_time()),
        lambda: initial_shipment_time_to_retailer(),
    )


@component.add(
    name="planned remote MI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"average_mi": 1, "percentage_of_average_mi": 1},
)
def planned_remote_mi():
    return average_mi() * percentage_of_average_mi()


@component.add(
    name="Planned Temporary CI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"average_ci": 1, "percentage_of_average_ci": 1},
)
def planned_temporary_ci():
    return average_ci() * percentage_of_average_ci()


@component.add(
    name="initial adjust time of RPI", comp_type="Constant", comp_subtype="Normal"
)
def initial_adjust_time_of_rpi():
    return 4


@component.add(
    name="delivery time",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_1": 1, "initial_delivery_time": 2, "increase_of_time": 1},
)
def delivery_time():
    return if_then_else(
        time_1() == 1,
        lambda: initial_delivery_time() * (1 + increase_of_time()),
        lambda: initial_delivery_time(),
    )


@component.add(
    name="demand",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"mean_value": 1, "deviation": 1, "seed": 1, "time": 1},
)
def demand():
    return stats.truncnorm.rvs(0, 50000, loc=mean_value(), scale=deviation(), size=())


@component.add(
    name="demand backlog",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_demand_backlog": 1},
    other_deps={
        "_integ_demand_backlog": {
            "initial": {},
            "step": {"demand": 1, "demand_backlog_reduction_rate": 1, "sales_1": 1},
        }
    },
)
def demand_backlog():
    return _integ_demand_backlog()


_integ_demand_backlog = Integ(
    lambda: demand() - demand_backlog_reduction_rate() - sales_1(),
    lambda: 0,
    "_integ_demand_backlog",
)


@component.add(
    name="initial service period of remote MI",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_service_period_of_remote_mi():
    return 2


@component.add(
    name="deviation",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "reduction_of_demand": 2,
        "initial_deviation": 3,
        "time_3": 1,
    },
)
def deviation():
    return if_then_else(
        time_1() == 1,
        lambda: (1 - reduction_of_demand()) * initial_deviation(),
        lambda: if_then_else(
            time_3() == 1,
            lambda: (1 - 0.5 * reduction_of_demand()) * initial_deviation(),
            lambda: initial_deviation(),
        ),
    )


@component.add(
    name="disassembly rate1",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "discrepancy_of_temporary_rpi": 1,
        "adjust_time_of_temporary_rpi": 1,
    },
)
def disassembly_rate1():
    return if_then_else(
        time_1() == 1,
        lambda: np.maximum(discrepancy_of_temporary_rpi(), 0)
        / adjust_time_of_temporary_rpi(),
        lambda: 0,
    )


@component.add(name="disassembly time", comp_type="Constant", comp_subtype="Normal")
def disassembly_time():
    return 1


@component.add(
    name='"used-product should satisfy"',
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_usedproduct_should_satisfy": 1},
    other_deps={
        "_integ_usedproduct_should_satisfy": {
            "initial": {},
            "step": {
                "should_satisfy_rate_of_usedproducts": 1,
                "satisfied_rate_of_used": 1,
            },
        }
    },
)
def usedproduct_should_satisfy():
    return _integ_usedproduct_should_satisfy()


_integ_usedproduct_should_satisfy = Integ(
    lambda: should_satisfy_rate_of_usedproducts() - satisfied_rate_of_used(),
    lambda: 0,
    "_integ_usedproduct_should_satisfy",
)


@component.add(
    name="retailer orders backlog",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_retailer_orders_backlog": 1},
    other_deps={
        "_integ_retailer_orders_backlog": {
            "initial": {},
            "step": {"retailer_orders": 1, "retailer_orders_reduction_rate": 1},
        }
    },
)
def retailer_orders_backlog():
    return _integ_retailer_orders_backlog()


_integ_retailer_orders_backlog = Integ(
    lambda: retailer_orders() - retailer_orders_reduction_rate(),
    lambda: 0,
    "_integ_retailer_orders_backlog",
)


@component.add(
    name="RMI",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_rmi": 1},
    other_deps={
        "_integ_rmi": {
            "initial": {},
            "step": {"material_can_be_recycled": 1, "recycling_rate": 1},
        }
    },
)
def rmi():
    return _integ_rmi()


_integ_rmi = Integ(
    lambda: material_can_be_recycled() - recycling_rate(), lambda: 0, "_integ_rmi"
)


@component.add(name="initial mean value", comp_type="Constant", comp_subtype="Normal")
def initial_mean_value():
    return 10000


@component.add(
    name="RT",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_rt": 1},
    other_deps={
        "_integ_rt": {
            "initial": {},
            "step": {"remanent_trash_will_be_disposed": 1, "process_rate": 1},
        }
    },
)
def rt():
    return _integ_rt()


_integ_rt = Integ(
    lambda: remanent_trash_will_be_disposed() - process_rate(), lambda: 0, "_integ_rt"
)


@component.add(
    name="sales",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ri": 1, "demand_backlog": 1, "delivery_time": 1},
)
def sales_1():
    return np.minimum(ri(), demand_backlog()) / delivery_time()


@component.add(
    name="satisfied rate of used",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"purchase_rate": 1},
)
def satisfied_rate_of_used():
    return purchase_rate()


@component.add(
    name="fill rate for CI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "kc": 1,
        "time_2": 1,
        "temporary_ci": 1,
        "service_periods_for_temporary_ci": 1,
    },
)
def fill_rate_for_ci():
    return if_then_else(
        kc() == 0,
        lambda: 0,
        lambda: if_then_else(
            time_2() == 1,
            lambda: 0,
            lambda: np.maximum(temporary_ci() / service_periods_for_temporary_ci(), 0),
        ),
    )


@component.add(
    name="fill rate for MI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "km2": 1,
        "service_periods_of_remote_mi": 1,
        "time_1": 1,
        "remote_mi": 1,
    },
)
def fill_rate_for_mi():
    return if_then_else(
        km2() == 1,
        lambda: if_then_else(
            time_1() == 1,
            lambda: np.maximum(remote_mi() / service_periods_of_remote_mi(), 0),
            lambda: 0,
        ),
        lambda: 0,
    )


@component.add(
    name="percentage of average CI", comp_type="Constant", comp_subtype="Normal"
)
def percentage_of_average_ci():
    return 1


@component.add(
    name="initial adjust time of Temporary CI",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_adjust_time_of_temporary_ci():
    return 4


@component.add(
    name="Temporary CI",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_temporary_ci": 1},
    other_deps={
        "_integ_temporary_ci": {
            "initial": {},
            "step": {"collection_rate_for_temporary_ci": 1, "fill_rate_for_ci": 1},
        }
    },
)
def temporary_ci():
    return _integ_temporary_ci()


_integ_temporary_ci = Integ(
    lambda: collection_rate_for_temporary_ci() - fill_rate_for_ci(),
    lambda: 0,
    "_integ_temporary_ci",
)


@component.add(
    name="initial adjust time of Temporary RPI",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_adjust_time_of_temporary_rpi():
    return 4


@component.add(
    name="initial delivery time", comp_type="Constant", comp_subtype="Normal"
)
def initial_delivery_time():
    return 1


@component.add(name="initial deviation", comp_type="Constant", comp_subtype="Normal")
def initial_deviation():
    return 1000


@component.add(
    name="purchase rate",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ci": 2, "usedproduct_should_satisfy": 1, "purchase_time": 1},
)
def purchase_rate():
    return if_then_else(
        ci() > 0,
        lambda: np.minimum(usedproduct_should_satisfy(), ci()) / purchase_time(),
        lambda: 0,
    )


@component.add(
    name="initial service period of temporary CI",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_service_period_of_temporary_ci():
    return 15


@component.add(
    name="initial shipment time to retailer",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_shipment_time_to_retailer():
    return 1


@component.add(
    name="Remote MI",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_remote_mi": 1},
    other_deps={
        "_integ_remote_mi": {
            "initial": {},
            "step": {"production_rate_1": 1, "fill_rate_for_mi": 1},
        }
    },
)
def remote_mi():
    return _integ_remote_mi()


_integ_remote_mi = Integ(
    lambda: production_rate_1() - fill_rate_for_mi(), lambda: 0, "_integ_remote_mi"
)


@component.add(
    name="UPI disassembly rate",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"disassembly_rate": 1, "rpn": 1},
)
def upi_disassembly_rate():
    return disassembly_rate() / rpn()


@component.add(
    name="wholesaler orders backlogs",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_wholesaler_orders_backlogs": 1},
    other_deps={
        "_integ_wholesaler_orders_backlogs": {
            "initial": {},
            "step": {"wholesaler_orders": 1, "wholesaler_orders_reduction_rate": 1},
        }
    },
)
def wholesaler_orders_backlogs():
    return _integ_wholesaler_orders_backlogs()


_integ_wholesaler_orders_backlogs = Integ(
    lambda: wholesaler_orders() - wholesaler_orders_reduction_rate(),
    lambda: 0,
    "_integ_wholesaler_orders_backlogs",
)


@component.add(
    name="RI",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_ri": 1},
    other_deps={
        "_integ_ri": {"initial": {}, "step": {"shipment_to_retailer": 1, "sales_1": 1}}
    },
)
def ri():
    return _integ_ri()


_integ_ri = Integ(lambda: shipment_to_retailer() - sales_1(), lambda: 0, "_integ_ri")


@component.add(
    name="shipment to retailer",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"wi": 1, "retailer_orders_backlog": 1, "shipment_time_to_retailer": 1},
)
def shipment_to_retailer():
    return np.minimum(wi(), retailer_orders_backlog()) / shipment_time_to_retailer()


@component.add(
    name="service periods of remote MI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "initial_service_period_of_remote_mi": 2,
        "increase_of_time": 1,
    },
)
def service_periods_of_remote_mi():
    return if_then_else(
        time_1() == 1,
        lambda: initial_service_period_of_remote_mi() * (1 + increase_of_time()),
        lambda: initial_service_period_of_remote_mi(),
    )


@component.add(
    name="percentage of average MI", comp_type="Constant", comp_subtype="Normal"
)
def percentage_of_average_mi():
    return 1


@component.add(
    name="UPI",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_upi": 1},
    other_deps={
        "_integ_upi": {
            "initial": {},
            "step": {"purchase_rate": 1, "upi_disassembly_rate": 1},
        }
    },
)
def upi():
    return _integ_upi()


_integ_upi = Integ(
    lambda: purchase_rate() - upi_disassembly_rate(), lambda: 0, "_integ_upi"
)


@component.add(name="T4", comp_type="Constant", comp_subtype="Normal")
def t4():
    return 4


@component.add(
    name="service periods for Temporary CI",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time_1": 1,
        "initial_service_period_of_temporary_ci": 2,
        "increase_of_time": 1,
    },
)
def service_periods_for_temporary_ci():
    return if_then_else(
        time_1() == 1,
        lambda: initial_service_period_of_temporary_ci() * (1 + increase_of_time()),
        lambda: initial_service_period_of_temporary_ci(),
    )


@component.add(
    name="RMSI",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_rmsi": 1},
    other_deps={
        "_integ_rmsi": {
            "initial": {},
            "step": {
                "coming_rate_of_raw_material": 1,
                "purchase_rate_of_new_material": 1,
            },
        }
    },
)
def rmsi():
    return _integ_rmsi()


_integ_rmsi = Integ(
    lambda: coming_rate_of_raw_material() - purchase_rate_of_new_material(),
    lambda: 0,
    "_integ_rmsi",
)
