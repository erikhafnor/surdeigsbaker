"""ESPHome external component: the Surdeigsbaker v1 bake program.

The C++ core (planner, doser, sequence, bake) is plain C++ with host tests in
firmware/v1/test/. This file only wires it into ESPHome: sensor inputs, callbacks for
the actuators (handled in YAML so the hardware stays visible in the config) and actions.
"""

from esphome import automation
import esphome.codegen as cg
from esphome.components import binary_sensor, sensor
import esphome.config_validation as cv
from esphome.const import CONF_ID

CODEOWNERS = []
AUTO_LOAD = ["sensor", "binary_sensor"]

bakeplan_ns = cg.esphome_ns.namespace("bakeplan")
BakeplanComponent = bakeplan_ns.class_("BakeplanComponent", cg.Component)
StartAction = bakeplan_ns.class_("StartAction", automation.Action)
AbortAction = bakeplan_ns.class_("AbortAction", automation.Action)
ConfirmAction = bakeplan_ns.class_("ConfirmAction", automation.Action)
ShapedAction = bakeplan_ns.class_("ShapedAction", automation.Action)
StoreEmptyPanAction = bakeplan_ns.class_("StoreEmptyPanAction", automation.Action)

CONF_WEIGHT = "weight"
CONF_DISTANCE = "distance"
CONF_DOUGH_TEMPERATURE = "dough_temperature"
CONF_ROOM_TEMPERATURE = "room_temperature"
CONF_DOOR = "door"
CONF_EMERGENCY_STOP = "emergency_stop"
CONF_TOF_TO_BOTTOM = "tof_to_bottom"
CONF_TOTAL_FLOUR = "total_flour"
CONF_HYDRATION = "hydration"
CONF_SALT = "salt"
CONF_SIMULATE = "simulate"
CONF_TIME_SCALE = "time_scale"
CONF_ACTIVITY = "activity"
CONF_HOURS = "hours"
CONF_COLD_STARTER = "cold_starter"

CONF_ON_KNEAD = "on_knead"
CONF_ON_DOSE = "on_dose"
CONF_ON_FLAP = "on_flap"
CONF_ON_SETPOINT = "on_setpoint"
CONF_ON_QUIET = "on_quiet"
CONF_ON_MESSAGE = "on_message"
CONF_ON_STATUS = "on_status"
CONF_ON_READY = "on_ready"

SIMULATE_SCHEMA = cv.Schema(
    {
        cv.Optional(CONF_TIME_SCALE, default=1.0): cv.float_range(min=1.0, max=10000.0),
        cv.Optional(CONF_ACTIVITY, default=1.0): cv.float_range(min=0.3, max=3.0),
    }
)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(BakeplanComponent),
        cv.Optional(CONF_WEIGHT): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_DISTANCE): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_DOUGH_TEMPERATURE): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_ROOM_TEMPERATURE): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_DOOR): cv.use_id(binary_sensor.BinarySensor),
        cv.Optional(CONF_EMERGENCY_STOP): cv.use_id(binary_sensor.BinarySensor),
        cv.Optional(CONF_TOF_TO_BOTTOM, default=186.0): cv.float_range(min=50.0, max=400.0),
        cv.Optional(CONF_TOTAL_FLOUR, default=560.0): cv.float_range(min=200.0, max=600.0),
        cv.Optional(CONF_HYDRATION, default=0.77): cv.float_range(min=0.55, max=0.9),
        cv.Optional(CONF_SALT, default=0.02): cv.float_range(min=0.0, max=0.03),
        cv.Optional(CONF_SIMULATE): SIMULATE_SCHEMA,
        cv.Optional(CONF_ON_KNEAD): automation.validate_automation({}),
        cv.Optional(CONF_ON_DOSE): automation.validate_automation({}),
        cv.Optional(CONF_ON_FLAP): automation.validate_automation({}),
        cv.Optional(CONF_ON_SETPOINT): automation.validate_automation({}),
        cv.Optional(CONF_ON_QUIET): automation.validate_automation({}),
        cv.Optional(CONF_ON_MESSAGE): automation.validate_automation({}),
        cv.Optional(CONF_ON_STATUS): automation.validate_automation({}),
        cv.Optional(CONF_ON_READY): automation.validate_automation({}),
    }
).extend(cv.COMPONENT_SCHEMA)

_CALLBACK_AUTOMATIONS = (
    automation.CallbackAutomation(CONF_ON_KNEAD, "add_on_knead_callback", [(cg.float_, "speed")]),
    automation.CallbackAutomation(
        CONF_ON_DOSE,
        "add_on_dose_callback",
        [(cg.std_string, "ingredient"), (cg.bool_, "run"), (cg.bool_, "reverse")],
    ),
    automation.CallbackAutomation(
        CONF_ON_FLAP, "add_on_flap_callback", [(cg.std_string, "ingredient"), (cg.bool_, "open")]
    ),
    automation.CallbackAutomation(CONF_ON_SETPOINT, "add_on_setpoint_callback", [(cg.float_, "temperature")]),
    automation.CallbackAutomation(CONF_ON_QUIET, "add_on_quiet_callback", [(cg.bool_, "quiet")]),
    automation.CallbackAutomation(CONF_ON_MESSAGE, "add_on_message_callback", [(cg.std_string, "message")]),
    automation.CallbackAutomation(CONF_ON_STATUS, "add_on_status_callback", [(cg.std_string, "status")]),
    automation.CallbackAutomation(CONF_ON_READY, "add_on_ready_callback"),
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    for key, setter in (
        (CONF_WEIGHT, "set_weight_sensor"),
        (CONF_DISTANCE, "set_distance_sensor"),
        (CONF_DOUGH_TEMPERATURE, "set_dough_temperature_sensor"),
        (CONF_ROOM_TEMPERATURE, "set_room_temperature_sensor"),
    ):
        if key in config:
            cg.add(getattr(var, setter)(await cg.get_variable(config[key])))
    if CONF_DOOR in config:
        cg.add(var.set_door_sensor(await cg.get_variable(config[CONF_DOOR])))
    if CONF_EMERGENCY_STOP in config:
        cg.add(var.set_emergency_stop_sensor(await cg.get_variable(config[CONF_EMERGENCY_STOP])))
    cg.add(var.set_tof_to_bottom(config[CONF_TOF_TO_BOTTOM]))
    cg.add(var.set_recipe(config[CONF_TOTAL_FLOUR], config[CONF_HYDRATION], config[CONF_SALT]))
    if CONF_SIMULATE in config:
        sim = config[CONF_SIMULATE]
        cg.add(var.set_simulation(sim[CONF_TIME_SCALE], sim[CONF_ACTIVITY]))
    await automation.build_callback_automations(var, config, _CALLBACK_AUTOMATIONS)


PARENT_SCHEMA = cv.Schema({cv.GenerateID(): cv.use_id(BakeplanComponent)})
SIMPLE_SCHEMA = automation.maybe_simple_id({cv.GenerateID(): cv.use_id(BakeplanComponent)})

START_SCHEMA = PARENT_SCHEMA.extend(
    {
        cv.Required(CONF_HOURS): cv.templatable(cv.float_range(min=0.5, max=48.0)),
        cv.Optional(CONF_COLD_STARTER, default=True): cv.templatable(cv.boolean),
    }
)


@automation.register_action("bakeplan.start", StartAction, START_SCHEMA, synchronous=True)
async def start_to_code(config, action_id, template_arg, args):
    paren = await cg.get_variable(config[CONF_ID])
    var = cg.new_Pvariable(action_id, template_arg, paren)
    cg.add(var.set_hours(await cg.templatable(config[CONF_HOURS], args, cg.float_)))
    cg.add(var.set_cold_starter(await cg.templatable(config[CONF_COLD_STARTER], args, cg.bool_)))
    return var


async def _simple_to_code(config, action_id, template_arg, args):
    paren = await cg.get_variable(config[CONF_ID])
    return cg.new_Pvariable(action_id, template_arg, paren)


for _name, _cls in (
    ("bakeplan.abort", AbortAction),
    ("bakeplan.confirm", ConfirmAction),
    ("bakeplan.shaped", ShapedAction),
    ("bakeplan.store_empty_pan", StoreEmptyPanAction),
):
    automation.register_action(_name, _cls, SIMPLE_SCHEMA, synchronous=True)(_simple_to_code)
