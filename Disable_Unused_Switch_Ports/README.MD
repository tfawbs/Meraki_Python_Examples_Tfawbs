# Disable Unused Switch Ports

This script is designed to check switch ports for usage (identifed from usageInKb > total) and if no usage is found for the last 31 days disable that port.

For example, consider this as a use case, you have switch ports in public access spaces, in order to reduce surface area of attack you have a policy to keep unused ports disabled, over potentially 100s of switches this can take many hours even days of human hours to review and address manually, with a script the Python and Meraki can poll through all your switches in a few minutes.

The in this folder uses a source file where you can enter the serial numbers of multiple switches you want to target, there is a sub folder called ["Single_Switch_Version"](/Disable_Unused_Switch_Ports/Single_Switch_Version/) containing a version of this script that targets a single serial as a variable in the script, this would be good for testing purposes.

The script works by doing the following steps:
1. Imports a list of Serial Numbers to target from [switch_serials.txt](/Disable_Unused_Switch_Ports/switch_serials.txt).
2. Gets the switch port usage for the switch serial, accesses the port usage and marks a port as unused if it has no usageInKb for the last 31 days.
3. Prints to the console a list of the ports it will target.
4. Sets the targeted switch ports it found with no usage to a "Disabled" state.
5. Moves on to the next serial number from [switch_serials.txt](/Disable_Unused_Switch_Ports/switch_serials.txt). 

## Screenshots

![This is an example of before.](/Disable_Unused_Switch_Ports/Before.png)
Before running the script
![This is an example of the script running.](/Disable_Unused_Switch_Ports/Running.png)
Running the script
![This is an example of after.](/Disable_Unused_Switch_Ports/After.png)
After running the script

## Requirements 

* python
* meraki

To install run the command:
```
pip install meraki 
```

To run the script:
1. Update with your API key on line 6
2. Update [switch_serials.txt](/Disable_Unused_Switch_Ports/switch_serials.txt) with the switches you want to run this against.
3. Run python3 disable_unused_switch_ports.py

I recommend you run this in a Python Virtual Environment, if you're unfamiliar how to do that check out this [video](https://www.youtube.com/watch?v=Y21OR1OPC9A)

For any troubleshooting issues I would suggest Search Engines as the first point of call and using AI tools to assist work through and build out the script as they are excellent at troubleshooting and adding onto the existing script.

## Disclaimer

This script was built with AI assistance (GPT-4o), for the prompt I used see the [ai_prompt.txt](/Disable_Unused_Switch_Ports/ai_prompt.txt) file. This script is provided with no warranty or support it is provided with the intent to be learnt from and built on. Please always follow best practices when engaging with the Meraki API, Python and any other coding tools.
