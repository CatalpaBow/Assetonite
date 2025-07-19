
// XXXXXXXXXXXX Assetto Corsa Telemetry Interface v1.1.2 written by Latch Dimitrov - Dec 2017 XXXXXXXXXXXXXXXXX

// Changelog:
        v0.1: (released during AC Steam Early Access 0.9.11)
                - initial Release
        v0.2: (released during AC Steam Early Access 0.22.9)
                - fixed wchar issue in handshakerResponse
        v0.3: (released during AC Steam Early Access 0.22.9)
                - fixed potential ACTI dialog window corruption
        v0.3.1: (released during AC Steam Early Access 0.22.9)
                - fixed ACTI dialog window corruption under non-aero themes
        v0.4: (released during AC Steam Early Access 0.22.9)
                - ACTI Trigger Control (in-game control, auto-launch, auto-connect)
                - further minor tweaks
        v0.4.1: (released during AC Steam Early Access 0.22.9)
                - various bug fixes
        v0.5: (released during AC Steam Early Access 0.22.9)
                - new mini in-game ACTI Trigger Control window (separated from settings window)
                - new data channels added (wheelAngularSpeed, tyreRadius and tyreLoadedRadius)
                - updated sample Motec i2 project to display the new data channels
        v0.6: (released during AC Steam Early Access 0.22.9)
                - now supports the latest Motec i2 version (mi2_pro_1.0.21.0030)
                - replaced the i2 installer with the latest one (mi2_pro_1.0.21.0030)
                - new data channels added (Car Coord [X,Y,Z])
                - updated sample Motec i2 project to display the new data channels (racing line
                    generated using local GPS maths and car coordinates)
                - fixed potential crash and data loss issues
        v0.7: (released during AC Steam Early Access 1.0.3 RC)
                - new Live Telemetry Viewer (using configurable xml-specified workspaces)
                - able to manually override the system text encoding (in-game ACTI Trigger Control)
        v1.0.0: (released during AC Steam Early Access 1.0.4 RC)
                - many new channels added (go to Help->See Channel List in acti to get the complete
                    list)
                - updated sample Motec i2 project to display the new data channels
                - fixed incorrect "Gear" channel data
                - fixed occasional issue with the "Tire Slip Angle" and "Tire Slip Ratio" channels
                - fixed in-game acti trigger control load/save settings issue
                - in-game acti trigger control can now trigger up to 3 remote hosts
                - generated motec logs now include "Event" and "Session" info ("Event" is used to
                    show if the data was generated from a live AC session or a replay and "Session"
                    is used to show what type of session i.e. practise/quali/race etc)
                - acti now has a configurable setting that allows it to launch as a "topmost" window
                    if desired
                - minor tweaks
        v1.0.1: (released during AC Steam Early Access 1.0.9 RC)
                - live telem reference lap bug fix
                - motec log session info tweak
                - total number of channels displayed when "Help->See Channel List" is clicked
        v1.0.2: (released during Assetto Corsa v1.0)
                - auto trigger connect ignored when viewing replays
        v1.0.3: (released during Assetto Corsa v1.3.1)
                - Fix for AC v1.3
        v1.1.0: (released during Assetto Corsa v1.3.2)
                - Added configurable recording rate settings. All of the available channels are now
                    divided into two groups - 'Base-Rate' and 'High-Rate' channels. The respective
                    recording rates for the two groups can be specified through the acti.exe
                    settings menu. Note that the recording rates should not exceed the average video
                    frame rate.
                - added a few new data channels (i.e. KERS Level, Flags, Position etc)
                - updated sample Motec i2 project to display the new data channels
                - added the name of the tire compound used during the recorded stint to the motec
                    log
                - added the current version of AC to the motec log
                - acti.exe layout changes
        v1.1.1: (released during Assetto Corsa v1.6.3)
                - added new data channels (i.e. Track Conditions, KERS & AIDs)
                - updated sample Motec i2 project to display the new data channels
                - updated sample ACTI Live Telem workspace to display the new data channels
        v1.1.2: (released during Assetto Corsa v1.16.1)
                - added new data channels (i.e. extra KERS settings / parameters, brake & tire tread
                    temps and a few other misc channels)
                - updated sample Motec i2 project to display the new data channels
                - updated sample ACTI Live Telem workspace to display the new data channels

// Notes:
        - ACTI records telemetry data at a rate of 20 Hz (by default) and displays it live at a rate of 2 Hz

// Known Issues:
        - If acti.exe is launched from in-game and you fully exit Assetto Corsa with acti.exe DISCONNECTED,
            you will need to manually close acti.exe before you can start Assetto Corsa again (Steam will
            report that "the app is still running"
        - In hotlap / race sessions, the FIRST timed lap recorded by ACTI (as viewed in Motec's i2) may
            show a slightly different laptime compared to what Assetto Corsa officially recorded. The
            difference should be less than the ACTI sampling period (i.e. <50ms).
        - If the in-game ACTI Trigger Control is unable to launch ACTI due to a "Unicode Decode Error",
            you need to manually specify the system text encoding. You can do this by opening a command
            prompt, typing in "chcp" [Enter] and writing the provided value in the ACTI Trigger Control
            config.ini next to "text_encoding_override" (the number value should be preceded by "cp").

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

