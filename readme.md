# IVR-Security-assessment-tool
Built with Python & XML as a database.

Screenshots and description: http://payatu.com/automating-ivr-pentesting/

This tool’s main objective is to reduce the time required during an IVR security assessment. This isn’t a full-fledged tool that we planned for but it’s built enough where anybody can extend it further.

For now this tool has only two major functionalities.

>Record a call flow

>Replay a call flow

![ScreenShot](https://raw.github.com/payatu/ivr-pentest/master/banner_menu.png)

For the first time the user needs to record a call flow by manually sending the DTMF tones using the tool. Then, the tool can automatically dial that number and reach to that point by automatically sending the pre-recorded DTMF values. Now the user can easily send different payloads at that point from the tool.

![ScreenShot](https://raw.github.com/payatu/ivr-pentest/master/saved_calls.png)

![ScreenShot](https://raw.github.com/payatu/ivr-pentest/master/replay_call.png)

# Features to be added in the future version of this tool 

>Custom Bruteforce attack at any defined point.

>SQL Injection payloads

>Buffer overflow payloads

>Input validation payloads

# NOTE

This is not the full fledged tool that we intended for. The full fledged tool will have all the features listed above. I coded this a year back but could not release it because it was not finished completely and I realised that for a full fledged tool, it’s better to make a GUI or Web version of this tool rather than a command line one. With the command line tool, we cannot have a good control when it comes to combining different attack vectors. We will probably make a full version of this tool with an easy to use graphical interface. Meanwhile, the code could prove helpful for a pentester to reduce the time needed for IVR pentest and it could also prove helpful to those who want to automate the IVR interaction process.
