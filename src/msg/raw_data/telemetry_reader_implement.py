from msg.raw_data.pyaccsharedmemory import accSharedMemory,ACC_STATUS,ACC_map
from msg.message_source.message_source_provider import MessageSourceImplement
from msg.message_source.i_telemtry_reader import BaseTelemtryData,Graphics,Physics,Static
class TelemetryDataImplement(BaseTelemtryData):
    def __init__(self,acc_map : ACC_map,on_launch : bool):
        self.Graphics = Graphics()
        self.Physics = Physics()
        self.Static = Static()
        self._on_launch = on_launch
        for name,val in vars(acc_map.Graphics).items():
            if(name in white_list["Graphics"]):
                setattr(self.Graphics,name,val)
                
        for name,val in vars(acc_map.Physics).items():
            if(name in white_list["Physics"]):
                setattr(self.Physics,name,val)

        for name,val in vars(acc_map.Static).items():
                setattr(self.Static,name,val)
                
    def on_launch(self):
        return self._on_launch
    
white_list = {
    "Physics": (
        'gas', 'brake', 'fuel', 'gear', 'rpm', 'steer_angle',
        'speed_kmh', 'velocity', 'g_force', 'wheel_slip', 'wheel_load', 'wheel_pressure', 'wheel_angular_s',
        'tyre_wear', 'tyre_dirty_level', 'tyre_core_temp', 'camber_rad', 'suspension_travel', 'drs', 'tc',
        'heading', 'pitch', 'roll', 'cg_height', 'car_damage', 'number_of_tyres_out', 'pit_limiter_on',
        'abs', 'kers_charge', 'kers_input', 'autoshifter_on', 'ride_height', 'turbo_boost', 'ballast',
        'air_density', 'air_temp', 'road_temp', 'local_angular_vel', 'final_ff', 'performance_meter',
        'engine_brake', 'ers_recovery_level', 'ers_power_level', 'ers_heat_charging', 'ers_is_charging',
        'kers_current_kj', 'drs_available', 'drs_enabled', 'brake_temp', 'clutch', 'tyre_temp_i', 'tyre_temp_m',
        'tyre_temp_o', 'is_ai_controlled', 
        'brake_bias', 'local_velocity',
    ),
    "Graphics": (
        'status', 'session_type', 'current_time_str', 'last_time_str', 'best_time_str',
        'last_sector_time_str', 'completed_lap', 'position', 'current_time', 'last_time', 'best_time',
        'session_time_left', 'distance_traveled', 'is_in_pit', 'current_sector_index', 'last_sector_time',
        'number_of_laps', 'tyre_compound', 'normalized_car_position', 'active_cars', 'car_coordinates',
        'penalty_time', 'flag', 'ideal_line_on', 'is_in_pit_lane', 'surface_grip', 'mandatory_pit_done'
    )
}

class TelemetryReaderImplement:
    def __init__(self, asm = accSharedMemory()):
        self._asm = asm
        self._ac_status_previous = ACC_STATUS.ACC_OFF

    def read(self) -> BaseTelemtryData:
        sm = self._asm.read_shared_memory()
        if(sm == None):
            return None
        on_launch = False
        if(self._ac_status_previous == ACC_STATUS.ACC_OFF and sm.Graphics.status == ACC_STATUS.ACC_LIVE):
            on_launch = True

        on_close = False
        if(self._ac_status_previous == ACC_STATUS.ACC_LIVE and sm.Graphics.status == ACC_STATUS.ACC_OFF) :
            self.ac_on_close = True

        self._ac_status_previous = sm.Graphics.status
        data = TelemetryDataImplement(sm,on_launch)
        return data