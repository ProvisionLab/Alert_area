function Component()
{
    // default constructor
}

Component.prototype.createOperations = function()
{
    component.createOperations();

    if (systemInfo.productType === "windows") 
    {
        component.addOperation("CreateShortcut", "@TargetDir@\\BvcClient.exe", "@StartMenuDir@\\BvcClient.lnk", 
            "workingDirectory=@TargetDir@", "iconPath=@TargetDir@/bvc.ico", "iconId=0", "description=BvcClient");

        component.addOperation("CreateShortcut", "@TargetDir@\\BvcClient.exe", "@DesktopDir@\\BvcClient.lnk", 
            "workingDirectory=@TargetDir@", "iconPath=@TargetDir@\\bvc.ico", "iconId=0", "description=BvcClient");

        component.addElevatedOperation("Execute", "{0,1638}", "@TargetDir@\\vcredist_x64.exe", "/norestart", "/quiet");
    }

    if (installer.value("os") === "x11")
    {
        component.addOperation("CreateDesktopEntry", "/usr/share/applications/BvcClient.desktop", 
            "Version=1.0\nType=Application\nTerminal=false\nExec=@TargetDir@/BvcClient.sh\nName=Bvc Client\nIcon=@TargetDir@bvc.png\nName[en_US]=Bvc Client");
        component.addElevatedOperation("Copy", "/usr/share/applications/BvcClient.desktop", "@HomeDir@/Desktop/BvcClient.desktop");
    }
}
