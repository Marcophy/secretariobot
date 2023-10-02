# SECRETARIOBOT
*Author: **Marco A. Villena**&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;Email: [mavillenas@proton.me](mailto:mavillenas@proton.me)*


This tool uses a **GMAIL** account to communicate with a remote machine. The general idea is that the script periodically check the inbox of an specific gmail account. The subject of the emails are considered as commands for this script.

This tool was developed as an alternative communication method with a remote machine. In this way, this script can be used for remotelly tracking other scripts by their log files and/or any other actions.

## Configuration options
You can find the configuration options in the file **config.json**. From there, you can setup the response of the script.

| Option              |   Type   | Description                                                                                                  |
|:--------------------|:--------:|:-------------------------------------------------------------------------------------------------------------|
| loop_time           | Integer  | Define the checking time of the email account. **The time is defined in minutes and must be higher than 1.** |
| whitelist           |   Bool   | Enable\disable the filter by white-list.                                                                     |
| report_unidentified |   Bool   | Determine if the script provide information to the sender about errors or security filters.                  |
| manual              |  String  | It's the website link where the user guide can be visited.                                                   |

### IMPORTANT
The master email address and its password are saved as enviroment variables. It's necessary to create a new file called **.env** in the main folder and save the information as:

**EMAIL = "*master gmail address*"**

**PASSWORD = "*master gmail account password*"**

## Subject keywords
There're several keywords avaiable designed for testing only.

| Subject keyword | Function                                                                                                                    |
|:----------------|:----------------------------------------------------------------------------------------------------------------------------|
| myip            | Return the public IP iof the machine.                                                                                       |
| looptime=       | Update the email checking time. Add an **integer number (>1)** after the equal. This munber is the refresh time in minutes. |
| melon           | Return an internal joke.                                                                                                    |
| help            | Send by email the link to this manual.                                                                                      |

