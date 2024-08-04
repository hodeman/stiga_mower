- last opp mappa under custom_components
- finn UUID under attributter i integrasjonen
- rediger scripts.yaml i HA. Se egen fil: skriptet.txt. Forandre til din UUID. 
- rediger configuration.yaml. skriv følgende:
input_select:
  stiga_mower:
    name: Select Mower
    options:
      - "uuid-of-mower-1"
      - "uuid-of-mower-2"
      - "uuid-of-mower-3"
    initial: "uuid-of-mower-1"
    icon: mdi:robot-mower
