# Campus ZTP Integration Pack

This integration pack allows you ZTP provision campus access switches

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
