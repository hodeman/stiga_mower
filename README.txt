- last opp mappa under custom_components, eller som custom resporotie i HACS
- finn UUID under attributter i integrasjonen
- rediger scripts.yaml i HA. Se egen fil:  Forandre til din UUID. Skriptet er som følger:
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

videre ønsker: mer automatisert installasjon, navn i scriptet, ikke uuid og ikke minst å få status til å funke
