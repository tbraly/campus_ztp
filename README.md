# Campus ZTP Integration Pack

This integration pack works with Brocade Workflow Composer (BWC) to enhance Zero Touch Provisioning (ZTP) to reliably setup ICX campus access Ethernet switches.

BWC is a platform for integration and automation across services and tools. It ties together your existing infrastructure and application environment so you can more easily automate that environment. It has a particular focus on taking actions in response to events.

This implementation of ZTP utilizes a Excel spreadsheet as the source of the variables to replace in a JINJA template that builds the final device-specific configuration that is pushed securily to the device.

## Getting Started

Follow these steps to get started with this integration pack.

1. You will need to have BWC already installed. Follow these steps here: https://bwc-docs.brocade.com/install/bwc.html
2. BWC architecture can be an all in one on a single box or with separate nodes for work and sensor nodes. Either way these nodes will need network connectivity to the management network with the switches being provisioned.
3. ZTP relies on a TFTP and DHCP server which will also need to have network connectivity to the switches.

## Installation of Campus ZTP Pack

1. Fork or download the pack into the /opt/stackstorm/packs/ directory
2. Run: st2 run packs.setup_virtualenv packs=campus_ztp
3. Run: st2ctl reload
4. Run: st2 rule create rules/dhcpcommit.yaml
5. Run: st2 rule create rules/running_config_changed.yaml

## Additional Setup

To trigger off of DHCP and option-82 information for true ZTP provisioning, add the following lines to your isc-dhcp-server dhcpd.conf file (in addition to creating a pool for the provisioning network):

```
#
# BUILD A JSON RECORD OF THE INFORMATION
#

option agent.subscriber-id code 6 = text;
option hostname code 12 = text;

on commit {
	set ClientIP = binary-to-ascii(10,8,".",leased-address);
	set ClientMac = binary-to-ascii(16,8,":",substring(hardware,1,6));
	set Name = option hostname;
	set RemoteId = "";
	set CircuitId = "";
	set SubscriberId = "";
	if exists agent.circuit-id
	{
		set RemoteId = binary-to-ascii(16,8,":",option agent.remote-id);

		# For NetIron as relay:
		set CircuitId = binary-to-ascii(10,8,"/",substring(option agent.circuit-id,2,4));

		# For ICX as relay:
		# set CircuitId = binary-to-ascii(10,8,"/",substring(option agent.circuit-id,4,4));
	}
	if exists agent.subscriber-id
	{
		set SubscriberId = option agent.subscriber-id;
	}
	set Json = concat("{",
				"\"client_ip\":\"",ClientIP,"\",",
				"\"client_mac\":\"",ClientMac,"\",",
				"\"hostname\":\"",Name,"\",",
				"\"remote_id\":\"",RemoteId,"\",",
				"\"circuit_id\":\"",CircuitId,"\",",
				"\"subscriber_id\":\"",SubscriberId,"\"",
			  "}");
	log(Json);
	execute ("/etc/dhcp/st2_dhcp_webhook",Json);
}
```

Turn on Option-82 (DHCP Snooping) on the MLXe or ICX distribution/core devices:

MLX:
```
device(config)# ip dhcp-snooping vlan 10 insert-relay-information
```
ICX:
```
!!! Prerequist for DHCP Snooping:
device(config)#enable ACL-per-port-per-vlan
device(config)#write memory
device(config)#exit
device#reload

!!! Turn on DHCP Snooping
device(config)#ip dhcp snooping vlan 10

!!! Allow the DHCP server to work where it's attached
device(config)#interface ethernet 1/1/1
device(config-if-e10000-1/1/1)#dhcp snooping trust
device(config-if-e10000-1/1/1)#exit

!!! Take advantage of Subscriber-id field to key off of in the excel spreadsheet
device(config)#interface ethernet 1/1/3
device(config-if-e1000-1/1/3)#dhcp snooping relay information subscriber-id stackmaster
```

Then copy over st2_dhcp_webhook to the /etc/dhcp directory and odify the API key in the file with the key you generate with:

```
st2 apikey create -k -m '{"used_by":"DHCP server"}'
```

In order to let the DHCP server run the WebHook, you'll need to modify apparmor:

```
sudo vi /etc/apparmor.d/usr.sbin.dhcpd

Add at the end of the file:

# Campus ZTP
/etc/dhcp/st2_dhcp_webhook cux,

Save and Restart:

sudo service apparmor restart
```

Create 'brocade.cfg' to your TFTP directory with the following contents. It will be loaded by the switch and provide for the initial configuration to allow for the SCP copy of the final configuration. 

```
user admin password brocade
aaa authentication login default local
```

Add all the neccessary boot and image files to your TFTP server directory

## Configuration 

Edit the config.yaml for your environment

* `templates` - directory where templates are stored
* `excel` - location of excel spreadsheet of configuration data
* `config_backup_dir` - location of switches backup files
* `tmp_dir` - location where configuration file will be temporary stored before SCP


## Actions

```
+-------------------------------------------------+-------------------------------------------------+
| ref                                             | description                                     |
+-------------------------------------------------+-------------------------------------------------+
| campus_ztp.backup_configuration                 | backups the configuration via SCP               |
| campus_ztp.delay                                | creates a delay                                 |
| campus_ztp.generate_ssh_key                     | generates the nessessary keys to ssh into the   |
|                                                 | box                                             |
| campus_ztp.get_configuration                    | builds the switch configuration                 |
| campus_ztp.get_flash                            | gets the current flash information as a json    |
|                                                 | record                                          |
| campus_ztp.get_modules                          | gets the modules by unit as a json record       |
| campus_ztp.get_version                          | gets the version information as a json record   |
| campus_ztp.initial_configuration_chain          | Campus ZTP Workflow                             |
| campus_ztp.is_boot_code_current                 | checks to see if boot code is current           |
| campus_ztp.is_image_current                     | checks to see if image is current               |
| campus_ztp.secure_copy                          | secure copies with interactive login            |
| campus_ztp.send_cli_command                     | send cli command(s) to the device(s)            |
| campus_ztp.send_cli_template                    | send cli template to the device(s)              |
| campus_ztp.set_hostname                         | sets the hostname on a box                      |
| campus_ztp.transfer_ztp_configuration           | builds startup configuration, telnets to        |
|                                                 | device, transfers config via SCP from server,   |
|                                                 | and reloads switch                              |
| campus_ztp.update_spreadsheet                   | adds/updates variables to a spreadsheet         |
| campus_ztp.upgrade_boot_code                    | upgrades the boot code via tftp                 |
| campus_ztp.upgrade_image                        | upgrades the image via tftp                     |
+-------------------------------------------------+-------------------------------------------------+
```

## License

Campus_ZTP is released under the APACHE 2.0 license. See ./LICENSE for more information.
