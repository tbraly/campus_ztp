# Campus ZTP Integration Pack

This integration pack works with Brocade Workflow Composer (BWC) to enhance Zero Touch Provisioning (ZTP) to reliably setup ICX campus access Ethernet switches.

BWC is a platform for integration and automation across services and tools. It ties together your existing infrastructure and application environment so you can more easily automate that environment. It has a particular focus on taking actions in response to events.

## Getting Started

Follow these steps to get started with this integration pack.

1. You will need to have BWC already installed. Follow these steps here: https://bwc-docs.brocade.com/install/bwc.html
2. BWC architecture can be an all in one on a single box or with separate nodes for work and sensor nodes. Either way these nodes will need network connectivity to the management network with the switches being provisioned.
3. ZTP relies on a TFTP and DHCP server which will also need to have network connectivity to the switches.


## Configuration

* `templates` - directory where templates are stored
* `excel` - location of excel spreadsheet of configuration data

## Actions

```
+----------------------------------------+------------+----------------------------------------------------------+
| ref                                    | pack       | description                                              |
+----------------------------------------+------------+----------------------------------------------------------+
| campus_ztp.delay                       | campus_ztp | creates a delay                                          |
| campus_ztp.generate_ssh_key            | campus_ztp | generates the nessessary keys to ssh into the box        |
| campus_ztp.get_configuration           | campus_ztp | builds the switch configuration                          |
| campus_ztp.get_flash                   | campus_ztp | gets the current flash information as a json record      |
| campus_ztp.get_modules                 | campus_ztp | gets the modules by unit as a json record                |
| campus_ztp.initial_configuration_chain | campus_ztp | Campus ZTP Workflow                                      |
| campus_ztp.is_boot_code_current        | campus_ztp | checks to see if boot code is current                    |
| campus_ztp.is_image_current            | campus_ztp | checks to see if image is current                        |
| campus_ztp.secure_copy                 | campus_ztp | secure copies with interactive login                     |
| campus_ztp.send_cli_command            | campus_ztp | sends cli command(s) to the device(s)                    |
| campus_ztp.transfer_ztp_configuration  | campus_ztp | builds startup configuration, telnets to device,         |
|                                        |            | transfers config via SCP from server, and reloads switch |
| campus_ztp.upgrade_boot_code           | campus_ztp | upgrades the boot code via tftp                          |
| campus_ztp.upgrade_image               | campus_ztp | upgrades the image via tftp                              |
+----------------------------------------+------------+----------------------------------------------------------+
```

## License

Campus_ZTP is released under the APACHE 2.0 license. See ./LICENSE for more information.
