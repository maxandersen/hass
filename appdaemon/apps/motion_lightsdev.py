import appdaemon.plugins.hass.hassapi as hass
#############################################################################################
# Args:
#
# sensor: binary sensor to use as trigger. several motion detectors are seperated with ,
# entity_on : entity to turn on when detecting motion, can be a light, script, scene or anything else that can be turned on. more lights are sepetated with ,
# entity_off : entity to turn off when detecting motion, can be a light, script or anything else that can be turned off. Can also be a scene which will be turned on. more lights are sepetated with ,
# delay: amount of time after turning on to turn off again. If not specified defaults to 60 seconds.
#  
#
# Release Notes
#
# Version 1.2:
#   Updated to work with AppDaemon 3 (max)
# Version 1.1: https://community.home-assistant.io/t/appdaemon-motion-detectionlights-version-1-1/6632
#   Added option for several lights, scripts, scenes (Rene Tode)
#   Added option for several motiondetectors (Rene Tode)
#   Added option to just turn out light after timer ended (Rene Tode)
#   Added controle if timer from motionsensor is longer then the delay (Rene Tode)
#   Changed handlenaming bug (Rene Tode)
#   Changed reset flow (Rene Tode)
# Version 1.0:
#   Initial Version (aimc)

import itertools

class MotionLights(hass.Hass):

  def initialize(self):
     
    self.handle = None 

    if "sensor" in self.args:
      self.sensors = self.args.get("sensor","").split(",")
      self.log("Listen to {}".format(self.sensors))
      for sensor in self.sensors:
        self.listen_state(self.motion, sensor)
    else:
      self.log("No sensor specified, doing nothing")
    
    self.timer = self.args.get("countdown")
    self.on_entities = [x.strip() for x in self.args.get("entity_on", "").split(",")]
    self.off_entities = [x.strip() for x in self.args.get("entity_off", self.args.get("entity_on", "")).split(",")]

    self.delay = self.args.get("delay", 300)

    self.states = self.args.get("states", [ 
                              { 'name': 'initial',   'data': { 'brightness_pct': 100 }}, 
                              { 'name': 'dimmed',    'data': { 'brightness_pct': 50  }},
                              { 'name': 'very dimm', 'data': { 'brightness_pct': 1   }},
                              { 'name': 'turnedoff', 'data': { 'brightness_pct': 0   }}
                              ])
     
  def reset_on_motion(self):
    self.currentstate = iter(self.states)
    
    self.log("Calling start timer on {}".format(self.timer))
    if (self.handle):
        self.cancel_listen_event(self.handle)
    
    self.call_service("timer/cancel", entity_id = self.timer)
    self.call_service("timer/start", entity_id = self.timer, duration = self.delay)
    
    self.handle = self.listen_event(self.timed_out, "timer/finished", entity_id = self.timer)

    
  def motion(self, entity, attribute, old, new, kwargs):
    self.log("{} changed on {} from {} to {}".format(attribute, entity, old, new))
    self.reset_on_motion()
    if new == "on":
      ## todo only fire turn on if timer started ?
      self._turn_on()
    
  def motion_detected(self):
    for sensor in self.sensors:
      self.log("sensor " + sensor + " is " + self.get_state(sensor))

      if self.get_state(sensor) == "on":
        return True
    return False
    
  def timed_out(self, kwargs):
    
    self.log("Timed out")
    if not self.motion_detected():
      self._turn_off()
    else:
      self.log("Timer has Ended, but a motion detector is still on. Restarting timer")
      self.reset_on_motion()
      

  def _turn_on(self):
    self.log("Turning on...")
    if self.on_entities: 
          for on_entity in self.on_entities:
            data = next(self.currentstate)['data']
            self.log("calling turn on " + on_entity + " with " + str(data))
            self.turn_on(on_entity,**data)
           
          self.log("I turned {} on.".format(self.args["entity_on"]))
    else:
          self.log("Asked to turn but there was nothing to turn on.")          
        

  def _turn_off(self):
    for off_entity in self.off_entities:
      # If it's a scene we need to turn it on not off
      device, entity = self.split_entity(off_entity)
      if device == "scene":
        self.log("I activated {}".format(off_entity))
        self.turn_on(off_entity)
      else:
        self.log("I turned {} off".format(off_entity))
        self.turn_off(off_entity)