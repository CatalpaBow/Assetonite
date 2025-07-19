import cfg_loder
from message.packing_fncs import *
STATIC_TABLE = [
    ('suspensionMaxTravel','suspension_max_travel','f4',pack_f4_wheels)
]
PHYSICS_TABLE = [
    ('packetID', 'packed_id', 'i', str),
    ('gas', 'gas', 'f', str),
    ('brake', 'brake', 'f', str),
    ('fuel', 'fuel', 'f', str),
    ('gear', 'gear', 'i', str),
    ('rpm', 'rpm', 'i', str),
    ('steerAngle', 'steer_angle', 'f', str),

    ('speedKmh', 'speed_kmh', 'f', str),
    ('velocity', 'velocity', 'f3', pack_f3),
    ('accG', 'g_force', 'f3', pack_f3),

    ('wheelSlip', 'wheel_slip', 'f4', pack_f4_wheels),
    #('wheelLoad', 'wheel_load', 'f4', format_wheels),
    #('wheelsPressure', 'wheel_pressure', 'f4', format_wheels),
    ('wheelAngularSpeed', 'wheel_angular_s', 'f4', pack_f4_wheels),
    ('tyreWear', 'tyre_wear', 'f4', pack_f4_wheels),
    ('tyreDirtyLevel', 'tyre_dirty_level', 'f4', pack_f4_wheels),
    #('tyreCoreTemperature', 'tyre_core_temp', 'f4', format_wheels),
    ('camberRAD', 'camber_rad', 'f4', pack_f4_wheels),
    ('suspensionTravel', 'suspension_travel', 'f4', pack_f4_wheels),

    #('drs', 'drs', 'i', str),
    #('tc', 'tc', 'f', str),
    ('headeing', 'heading', 'f', str),
    ('pitch', 'pitch', 'f', str),
    ('roll', 'roll', 'f', str),
    ('cgHeight', 'cg_height', 'f', str),
    ('carDamage', 'car_damage', 'f4', pack_f4_car_damage),
    ('numberOfTyresOut', 'number_of_tyres_out', 'i', str),
    #('pitLimiterOn', 'pit_limiter_on', 'b', str),
    #('abs', 'abs', 'f', str),

    #('kersCharge', 'kers_charge', 'f', str),
    #('kersInput', 'kers_input', 'f', str),

    #('autoshifterOn', 'autoshifter_on', 'b', str),
    #('rideHeight', 'ride_height', 'f2', format_array_2f),
    #('turboBoost', 'turbo_boost', 'f', str),
    #('ballast', 'ballast', 'f', str),
    ('airDensity', 'air_density', 'f', str),
    ('airTemp', 'air_temp', 'f', str),
    ('roadTemp', 'road_temp', 'f', str),
    ('localAngularVel', 'local_angular_vel', 'f3', pack_f3),
    #('FinalFF', 'final_ff', 'f', str),
    #('performanceMeter', 'performance_meter', 'f', str),

    #('engineBrake', 'engine_brake', 'i', str),
    #('ersRecoveryLevel', 'ers_recovery_level', 'i', str),
    #('ersPowerLevel', 'ers_power_level', 'i', str),
    #('ersHeatCharging', 'ers_heat_charging', 'i', str),
    #('ersIsCharging', 'ers_is_charging', 'i', str),
    #('kersCurrentKJ', 'kers_current_kj', 'f', str),

    #('drsAvailable', 'drs_available', 'i', str),
    #('drsEnabled', 'drs_enabled', 'i', str),

    ('brakeTemp', 'brake_temp', 'f4', pack_f4_wheels),
    ('clutch', 'clutch', 'f', str),

    #('tyreTempI', 'tyre_temp_i', 'f4', format_wheels),
    #('tyreTempM', 'tyre_temp_m', 'f4', format_wheels),
    #('tyreTempO', 'tyre_temp_o', 'f4', format_wheels),

    #('isAIControlled', 'is_ai_controlled', 'b', str),

    #('tyreContactPoint', 'tyre_contact_point', 'f44', format_contact_point),
    #('tyreContactNormal', 'tyre_contact_normal', 'f44', format_contact_point),
    #('tyreContactHeading', 'tyre_contact_heading', 'f44', format_contact_point),

    #('brakeBias', 'brake_bias', 'f', str),

    #('localVelocity', 'local_velocity', 'f3', format_f3),
]

GRAPHICS_TABLE = [
    ('packed_id','packed_id', 'i', str),
    ('status', 'status','str', pack_str_enum),
    ('session_type','session_type', 'str', pack_str_enum),
    ('current_time_str','current_time_str', 'str', str),
    ('last_time_str','last_time_str', 'str', str),
    ('best_time_str','best_time_str','str', str),
    ('last_sector_time_str','last_sector_time_str', 'str', str),
    ('completed_lap','completed_lap', 'i', str),
    ('position','position', 'i', str),
    ('current_time', 'current_time','i', str),
    ('last_time', 'last_time','i',str),
    ('best_time','best_time', 'i', str),
    ('session_time_left','session_time_left', 'f', str),
    ('distance_traveled','distance_traveled', 'f', str),
    ('is_in_pit','is_in_pit',  'b', str),
    ('current_sector_index', 'current_sector_index','i', str),
    ('last_sector_time','last_sector_time', 'i', str),
    ('number_of_laps', 'number_of_laps','i', str),
    ('tyre_compound','tyre_compound', 'str', str),
    ('normalized_car_position','normalized_car_position', 'f', str),
    ('active_cars','active_cars', 'i',str),
    ('car_coordinates', 'car_coordinates','f3', pack_f3),
    ('penalty_time','penalty_time', 'f', str),
    ('flag','flag', 'str', str),
    ('ideal_line_on','ideal_line_on', 'b', str),
    ('is_in_pit_lane','is_in_pit_lane', 'b', str),
    ('surface_grip','surface_grip','f',str),
    ('mandatory_pit_done','mandatory_pit_done','i',str)
]
TYRE_TABLE = [
    ('tyreRotation','tyre_rotation','f44',pack_f44_quaternion)
    #('carRotation','car_rotation','q',pack_quaternion_temp),
]
ANALOG_INSTRUMENTS_TABLE = [
    ('rpmRot','rpm_rot','f',str),
    ('speedRot','speed_rot','f',str),
    ('fuelRot','fuel_rot','f',str),
    ('turboRot','turbo_rot','f',str),
    ('waterTempRot','water_temp_rot','f',str)
]
CAR_CFG_TABLE = {
    'car':{
        'BASIC':{
            'GRAPHICS_OFFSET' : ('carPosOffset','f3',pack_f3_cfg),
            'GRAPHICS_PITCH_ROTATION':('carPitchOffset','f',str)
        },
        'CONTROLS':{
            'STEER_LOCK' : ('steerLock','f',str),
            'STEER_RATIO': ('steerRatio','f',str)
        }
    },
    'suspensions':{
        'GRAPHICS_OFFSETS':{
            ('WHEEL_LF','WHEEL_RF','WHEEL_LR','WHEEL_RR') : ('offSetWheels','f4',pack_f4_list),
            ('SUSP_LF','SUSP_RF','SUSP_LR','SUSP_RR')     : ('offSetSuspension','f4',str),
        }
    }
}


def pack(data_container,table) -> list[str]:
    packed_list : list[str] = [] 
    if(isinstance(data_container,cfg_loder.ConfigData)):
        for ini,ini_val in table.items():
            for section, sec_val in ini_val.items():
                for key_def, (msg_key,msg_type,msg_packing) in sec_val.items():
                    if isinstance(key_def, tuple):
                        value = [data_container[ini][section][key_t] for key_t in key_def]
                    else:
                        value = data_container[ini][section][key_def]
                    packed_msg = pack_message(msg_key,msg_type,msg_packing(value))
                    packed_list.append(packed_msg)

    #フィールド読み取り
    else:
        for message_key, attr_name, mes_type, pack in table:
            value = getattr(data_container, attr_name)
            packed_list.append(pack_message(message_key, mes_type, pack(value)))
    return packed_list

if __name__ == "__main__":
    cfg = cfg_loder.load_cfg('bmw_1m')
    rslt = pack(cfg,CAR_CFG_TABLE)
    print(rslt)