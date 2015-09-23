
    
#
#
# codp chassis = primitive:
#
#
# codp battery = primitive:
#     f voltage (intervals of V) "Supplied voltage"
#     f amps    (A)              "Supplied amps"
#
#     r weight  (g)              "Battery weight"
#     r cost    ($)
#
#     solve with [python comp.pokde.pok]
#
#
# dp chassis_plus_motor = compose:
#     dp motor = ...
#     dp chassis = ...
#
#     f extra_payload
#     f velocity = chassis.velocity
#
#     r voltage = motor.voltage
#     r current = motor.current
#
#     # constraints
#     extra_payload + motor.weight <= chassis.payload
#     chassis.req_speed <= motor.speed
#     chassis.req_torque <= motor.torque
#
# dp MCB_plus_PSU = compose:
#     dp MCB = MCB
#     dp PSU = battery
#
#     f mission_duration (s) "Mission duration"
#     f req_voltage = MCB.voltage
#     f req_amps    = MCB.amps
#
#     r weight = MCB.weight + PSU.weight
#     r cost   = MCB.cost   + PSU.cost
#
#     power = MCB.req_V + MCB.req_A
#     PSU.capacity >= power * mission_duration
#
# dp mobility_plus_power = compose:
#     dp MCB_plus_PSU
#     dp chassis_plus_motor
#
#     F velocity = chassis_plus_motor.velocity
#     F extra_payload (g)   "Extra payload"
#     F extra_power   (P)   "Extra power"
#     F mission_time = MCB_plus_PSU.mission_time
#
#     R control_strategy = chassis_plus_motor.control_strategy
#     R weight = chassis_plus_motor.weight + MCB_plus_PSU.weight
#     R cost = chassis_plus_motor.cost + MCB_plus_PSU.cost
#
#     extra_payload + MCB_plus_PSU.weight <= chassis_plus_motor.payload
#     chassis_plus_motor.voltage <= MCB_plus_PSU.voltage
#     chassis_plus_motor.amps <= MCB_plus_PSU.amps
#
#     chassis_plus_motor.req_amps  <= MCB_plus_PSU.provided_amps


