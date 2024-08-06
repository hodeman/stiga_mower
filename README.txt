I wanted to see if AI could make me an integration for Home Assistant to control Stiga Autonomous robotic lawn mower (A-series)

- upload folder under custom_components, or use HACS
- edit stiga_api.py and enter the API. (Studio Code Servcer is a great tool for this). Restart HA.
- find UUID under attributes in the integration
- edit scripts.yaml in HA. Use your own UUID in the script. This is the script:
start_mower:
  alias: Start Mower
  sequence:
    - service: stiga_mower.start_mowing
      data_template:
        uuid: >
          {{ states('input_select.stiga_mower') }}

stop_mower:
  alias: Stop Mower
  sequence:
    - service: stiga_mower.stop_mowing
      data_template:
        uuid: >
          {{ states('input_select.stiga_mower') }}

- edit configuration.yaml.:
input_select:
  stiga_mower:
    name: Select Mower
    options:
      - "uuid-of-mower-1"
      - "uuid-of-mower-2"
      - "uuid-of-mower-3"
    initial: "uuid-of-mower-1"
    icon: mdi:robot-mower

- make buttons in Lovelace, for example:
type: vertical-stack
cards:
  - type: entities
    title: Select Mower
    entities:
      - input_select.stiga_mower
  - type: horizontal-stack
    cards:
      - type: button
        name: Start Mower
        icon: mdi:play
        tap_action:
          action: call-service
          service: script.start_mower
      - type: button
        name: Stop Mower
        icon: mdi:stop
        tap_action:
          action: call-service
          service: script.stop_mower

To fix:
- Status of mower is not working
- Ability to stop it while going to start point. 
- Note: stop buttin is actually "return to base"
- It seems that the stop button only works if mower is actually mowing, not when calculation route or driving towars starting points (for now)
- Names instead of UUID in inpout selector
- More functionalities

